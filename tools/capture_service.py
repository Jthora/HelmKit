#!/usr/bin/env python3
"""
capture_service.py — the HelmKit log sink (Track N, N-H1 / N-L3).

Spec: docs/plans/2026-tier1-launch/track-N-capability-robustness.md §4 (N-H1, N-L3) and
firmware/mk0.5/docs/SCHEMA.md §2.4. Runs on a laptop today and as a systemd unit on the belt-pack Pi later.

What it does, per line from the helm:
  - parses NDJSON; malformed lines go to `<out>/rejects.ndjson` (host-stamped) and are counted, never fatal;
  - opens one capture file per boot (`<utc>_<boot-id>.ndjson`, from the `hello` / `boot` line);
  - enriches every sample line with `t_wallclock` (host time at the boot line plus the helm's `t`,
    SCHEMA §3), leaving `t` untouched: the firmware-emitted fields are the immutable record;
  - answers every `hb` heartbeat with the byte '~' so the helm knows the link is drained
    (after 10 s without one it buffers events to flash and replays them on return);
  - counts lost lines from gaps in `n` per boot, and keeps a `sessions.json` index;
  - refuses to start under `--min-free-mb` of free disk (default 200).

Usage:
    tools/capture_service.py                       # auto-detect the port, write under captures/
    tools/capture_service.py --port /dev/cu.usbmodem1101 --out captures --label gym-2026-09-14
    tools/capture_service.py --replay-fixture tests/fixtures/ppg_60s_good.ndjson   # offline pipeline test

pyserial is only needed for a live port; the offline path and the tests run without it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import math
import os
import shutil
import signal
import sys
import time
from pathlib import Path

try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover
    serial = None

PORT_GLOBS = ("/dev/cu.usbmodem*", "/dev/cu.SLAB_USBtoUART*", "/dev/ttyACM*", "/dev/ttyUSB*")
ACK_BYTE = b"~"


def utc_stamp(now: float | None = None) -> str:
    t = dt.datetime.fromtimestamp(now if now is not None else time.time(), tz=dt.timezone.utc)
    return t.strftime("%Y%m%dT%H%M%SZ")


def free_mb(path: str | Path) -> float:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(p).free / (1024 * 1024)


def find_port() -> str | None:
    for pat in PORT_GLOBS:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[0]
    return None


def _finite(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


class Sink:
    """Pure line handler: files, enrichment, acks, integrity. No serial inside (testable)."""

    def __init__(self, out_dir: str | Path, label: str = "", now=time.time) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.label = label
        self._now = now
        self._fh = None
        self._rej = None
        self.file: Path | None = None
        self.boot: str = ""
        self.offset: float | None = None      # host seconds - helm t, set at the boot line
        self.seqs: set[int] = set()
        self.lines = 0
        self.rejects = 0                      # running total for this run
        self._rejects_at_open = 0
        self.index_path = self.out_dir / "sessions.json"
        self.index: list[dict] = self._load_index()

    # ---- files ---------------------------------------------------------------
    def _load_index(self) -> list[dict]:
        try:
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []

    def _save_index(self) -> None:
        self.index_path.write_text(json.dumps(self.index, indent=2), encoding="utf-8")

    def _open_boot(self, boot: str, host_now: float) -> None:
        self.close()
        self.boot = boot or "noboot"
        name = f"{utc_stamp(host_now)}_{self.boot}" + (f"_{self.label}" if self.label else "") + ".ndjson"
        self.file = self.out_dir / name
        self._fh = open(self.file, "a", encoding="utf-8")
        self.offset = None
        self.seqs = set()
        self.lines = 0
        self._rejects_at_open = self.rejects
        self.index.append({"file": self.file.name, "boot": self.boot, "started": utc_stamp(host_now), "label": self.label,
                           "lines": 0, "lost": 0, "rejects": 0})
        self._save_index()

    def _reject(self, raw: str) -> None:
        """Malformed lines are kept verbatim in one rejects file per output directory, stamped with host time."""
        self.rejects += 1
        if self._rej is None:
            self._rej = open(self.out_dir / "rejects.ndjson", "a", encoding="utf-8")
        self._rej.write(f"{utc_stamp(self._now())} {self.boot or '-'} " + raw.rstrip("\n") + "\n")
        self._rej.flush()

    def close(self) -> None:
        if self._fh is not None:
            self._update_index()
            self._fh.close()
            self._fh = None
        if self._rej is not None:
            self._rej.close()
            self._rej = None

    def _update_index(self) -> None:
        if not self.index:
            return
        self.index[-1].update({"lines": self.lines, "lost": self.lost(), "rejects": self.rejects - self._rejects_at_open})
        self._save_index()

    # ---- integrity -----------------------------------------------------------
    def lost(self) -> int:
        return (max(self.seqs) - min(self.seqs) + 1) - len(self.seqs) if self.seqs else 0

    # ---- lines ---------------------------------------------------------------
    def handle_line(self, raw: str, host_now: float | None = None) -> dict:
        """Process one line. Returns {"ack": bool, "kind": str}."""
        host_now = self._now() if host_now is None else host_now
        raw = raw.strip()
        if not raw:
            return {"ack": False, "kind": "empty"}
        try:
            rec = json.loads(raw)
        except ValueError:
            self._reject(raw)
            return {"ack": False, "kind": "reject"}
        if not isinstance(rec, dict):
            self._reject(raw)
            return {"ack": False, "kind": "reject"}
        boot = rec.get("boot") if isinstance(rec.get("boot"), str) else ""
        kind = rec.get("kind") if isinstance(rec.get("kind"), str) else ""
        t = rec.get("t") if _finite(rec.get("t")) else None
        # a new file when the boot id changes (or nothing is open yet); hello / boot lines re-anchor the clock offset
        if self.file is None or (boot and boot != self.boot):
            self._open_boot(boot, host_now)
        if kind in ("hello", "boot") or self.offset is None:
            if t is not None:
                self.offset = host_now - t
        n = rec.get("n")
        if isinstance(n, int) and not isinstance(n, bool):
            self.seqs.add(n)
        if "ch" in rec and t is not None and self.offset is not None and not _finite(rec.get("t_wallclock")):
            rec["t_wallclock"] = round(self.offset + t, 3)
        assert self._fh is not None
        self._fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
        self.lines += 1
        if self.lines % 200 == 0:
            self._fh.flush()
            self._update_index()
        ack = rec.get("ch") == "hb"
        return {"ack": ack, "kind": kind or str(rec.get("ch", ""))}


def run_live(port: str, baud: int, sink: Sink, stop, log=print) -> int:
    """Reconnecting serial loop. `stop` is a callable returning True to exit."""
    if serial is None:
        log("error: pyserial is not installed (pip install pyserial)")
        return 2
    ser = None
    while not stop():
        if ser is None:
            try:
                ser = serial.Serial(port, baud, timeout=1.0)
                log(f"[capture] connected {port}")
            except (serial.SerialException, OSError) as e:  # type: ignore[attr-defined]
                log(f"[capture] waiting for {port}: {e}")
                time.sleep(1.0)
                continue
        try:
            raw = ser.readline()
        except (serial.SerialException, OSError) as e:  # type: ignore[attr-defined]
            log(f"[capture] link lost: {e}; reconnecting")
            try:
                ser.close()
            except Exception:
                pass
            ser = None
            sink.close()
            time.sleep(1.0)
            continue
        if not raw:
            continue
        res = sink.handle_line(raw.decode("utf-8", errors="replace"))
        if res["ack"]:
            try:
                ser.write(ACK_BYTE)
            except (serial.SerialException, OSError):  # type: ignore[attr-defined]
                pass
    if ser is not None:
        ser.close()
    sink.close()
    return 0


def run_fixture(path: str, sink: Sink) -> int:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            sink.handle_line(line)
    sink.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="HelmKit capture service: serial NDJSON -> one file per boot, with acks and integrity")
    ap.add_argument("--port", default=None, help="serial port (default: first match of %s)" % ", ".join(PORT_GLOBS))
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--out", default="captures")
    ap.add_argument("--label", default="")
    ap.add_argument("--min-free-mb", type=float, default=200.0)
    ap.add_argument("--replay-fixture", default=None, help="offline: run the sink over a recorded NDJSON file")
    args = ap.parse_args(argv)
    if free_mb(args.out) < args.min_free_mb:
        print(f"error: {free_mb(args.out):.0f} MB free under {args.out}, need {args.min_free_mb:.0f}", file=sys.stderr)
        return 3
    sink = Sink(args.out, args.label)
    if args.replay_fixture:
        if not Path(args.replay_fixture).exists():
            print(f"error: {args.replay_fixture} not found", file=sys.stderr)
            return 1
        rc = run_fixture(args.replay_fixture, sink)
        print(f"[capture] {sink.file}: {sink.lines} lines, {sink.lost()} lost, {sink.rejects} rejected")
        return rc
    port = args.port or find_port()
    if not port:
        print("error: no serial port found; pass --port", file=sys.stderr)
        return 1
    stopping = {"flag": False}

    def _stop(*_):
        stopping["flag"] = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    return run_live(port, args.baud, sink, lambda: stopping["flag"])


if __name__ == "__main__":
    sys.exit(main())
