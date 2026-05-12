#!/usr/bin/env python3
"""
heartbeat_smoketest.py — validate a HelmKit firmware target is alive.

Two modes:

  --port /dev/cu.usbserial-XXXX   read live serial from a flashed Nano
  --fixture path/to/file.txt      read canned frames from a text file
                                  (used by CI; no hardware required)

Exit codes:
   0   all assertions passed
   1   one or more assertions failed
   2   usage / setup error (port not found, etc.)

Validates (sprint 0.3 acceptance, see firmware/PROTOCOL.md):
  - Boot banner present (at least one '# ' comment line) — live mode only
  - At least N=10 well-formed HKMK0 frames captured
  - Every frame has exactly 7 fields
  - Every frame's CRC-8 matches
  - tick is monotonically increasing across frames
  - mcusr is 2 hex chars (decodable)
  - freeram >= MIN_FREE_RAM_BYTES (default 1024)
  - buildid is non-empty
  - No frame has BORF (0x04) or WDRF (0x08) set (these are
    legitimate states but they fail the *clean boot* smoketest;
    use --allow-fault-bits to ignore)
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional

PROTOCOL_VERSION = "HKMK0"
MIN_FRAMES = 10
MIN_FREE_RAM_BYTES = 1024
LIVE_READ_TIMEOUT_S = 20.0  # 10 frames @ 1 Hz + slack


def crc8(data: bytes) -> int:
    """Dallas/Maxim CRC-8, poly 0x31, init 0x00. Matches the AVR firmware."""
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x31) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


@dataclass
class Frame:
    version: str
    ms: int
    tick: int
    mcusr: int
    freeram: int
    buildid: str
    crc: int
    raw: str

    @classmethod
    def parse(cls, line: str) -> "Frame":
        line = line.rstrip("\r\n")
        parts = line.split("|")
        if len(parts) != 7:
            raise ValueError(f"expected 7 fields, got {len(parts)}: {line!r}")
        version, ms, tick, mcusr, freeram, buildid, crc = parts
        if version != PROTOCOL_VERSION:
            raise ValueError(f"protocol mismatch: {version!r} != {PROTOCOL_VERSION!r}")
        return cls(
            version=version,
            ms=int(ms),
            tick=int(tick),
            mcusr=int(mcusr, 16),
            freeram=int(freeram),
            buildid=buildid,
            crc=int(crc, 16),
            raw=line,
        )

    def verify_crc(self) -> bool:
        body, _, _ = self.raw.rpartition("|")
        return crc8(body.encode("ascii")) == self.crc


def read_live(port: str, baud: int, timeout_s: float) -> Iterator[str]:
    try:
        import serial  # type: ignore
    except ImportError:
        print("ERROR: pyserial not installed. Run: pip install pyserial", file=sys.stderr)
        sys.exit(2)
    try:
        ser = serial.Serial(port, baud, timeout=1.0)
    except Exception as e:
        print(f"ERROR: cannot open {port}: {e}", file=sys.stderr)
        sys.exit(2)

    deadline = time.monotonic() + timeout_s
    with ser:
        while time.monotonic() < deadline:
            line = ser.readline().decode("ascii", errors="replace")
            if line:
                yield line


def read_fixture(path: str) -> Iterator[str]:
    with open(path, "r", encoding="ascii") as f:
        for line in f:
            yield line


def validate(lines: Iterable[str], *, allow_fault_bits: bool, require_banner: bool) -> int:
    failures: list[str] = []
    banner_seen = False
    frames: list[Frame] = []

    for raw in lines:
        s = raw.rstrip("\r\n")
        if not s:
            continue
        if s.startswith("# "):
            banner_seen = True
            continue
        if not s.startswith(PROTOCOL_VERSION + "|"):
            # Ignore anything that isn't our version tag — per PROTOCOL.md §5.
            continue
        try:
            fr = Frame.parse(s)
        except ValueError as e:
            failures.append(f"parse: {e}")
            continue
        if not fr.verify_crc():
            failures.append(f"crc mismatch in frame: {fr.raw!r}")
            continue
        frames.append(fr)
        if len(frames) >= MIN_FRAMES:
            break

    if require_banner and not banner_seen:
        failures.append("no boot banner ('# ...' line) observed")
    if len(frames) < MIN_FRAMES:
        failures.append(f"only captured {len(frames)} frames, need >= {MIN_FRAMES}")

    last_tick: Optional[int] = None
    last_buildid: Optional[str] = None
    for fr in frames:
        if last_tick is not None and last_buildid == fr.buildid and fr.tick <= last_tick:
            failures.append(
                f"non-monotonic tick within same build: {last_tick} -> {fr.tick} "
                f"(buildid={fr.buildid!r})"
            )
        last_tick = fr.tick
        last_buildid = fr.buildid

        if fr.freeram < MIN_FREE_RAM_BYTES:
            failures.append(
                f"freeram {fr.freeram} B < min {MIN_FREE_RAM_BYTES} B "
                f"(frame: {fr.raw!r})"
            )
        if not fr.buildid:
            failures.append(f"empty buildid in frame: {fr.raw!r}")
        if not allow_fault_bits and (fr.mcusr & 0x0C):
            bits = []
            if fr.mcusr & 0x04:
                bits.append("BORF")
            if fr.mcusr & 0x08:
                bits.append("WDRF")
            failures.append(
                f"mcusr fault bits set ({'+'.join(bits)}) in frame: {fr.raw!r}"
            )

    if failures:
        print(f"FAIL: {len(failures)} assertion(s) failed:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print(f"OK: {len(frames)} frames validated, "
          f"min freeram={min(f.freeram for f in frames)} B, "
          f"buildid={frames[-1].buildid}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--port", help="serial port (e.g. /dev/cu.usbserial-XXXX)")
    src.add_argument("--fixture", help="canned text file of serial output")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--timeout", type=float, default=LIVE_READ_TIMEOUT_S,
                    help="seconds to wait for MIN_FRAMES in live mode")
    ap.add_argument("--allow-fault-bits", action="store_true",
                    help="don't fail on BORF/WDRF in MCUSR")
    args = ap.parse_args()

    if args.port:
        lines = read_live(args.port, args.baud, args.timeout)
        return validate(lines, allow_fault_bits=args.allow_fault_bits, require_banner=True)
    else:
        lines = read_fixture(args.fixture)
        return validate(lines, allow_fault_bits=args.allow_fault_bits, require_banner=False)


if __name__ == "__main__":
    sys.exit(main())
