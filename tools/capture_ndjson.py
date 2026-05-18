#!/usr/bin/env python3
"""
capture_ndjson.py — serial → file capture for Mk0.5 NDJSON streams.

Spec: docs/plans/2026-tier1-launch/track-I-pre-hardware-sprint.md (commit 4)

Reads NDJSON lines from a USB-CDC serial port (or, with --replay-fixture,
from a local file) and writes them to a timestamped capture file under
captures/, alongside a sibling .meta.yaml describing the session.

Usage:
    # Live capture
    tools/capture_ndjson.py --port /dev/tty.usbmodem* --label g2-op-jt

    # Offline pipeline test against a recorded fixture
    tools/capture_ndjson.py --replay-fixture path/to/fixture.ndjson \\
                            --label fixture-roundtrip
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import platform
import signal
import socket
import sys
import time
from pathlib import Path

# pyserial is only required for live capture. For --replay-fixture (and for
# CI, which never has a serial device), we tolerate its absence.
try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover
    serial = None


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = REPO_ROOT / "captures"


def utc_now_iso_basic() -> str:
    """Return UTC time as compact ISO-8601 basic, e.g. 20260622T144312Z."""
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def open_source(args: argparse.Namespace) -> tuple[io.TextIOBase, dict]:
    """Return (line-iterable text stream, meta-fragment dict)."""
    if args.replay_fixture is not None:
        path = Path(args.replay_fixture).resolve()
        if not path.exists():
            sys.exit(f"capture_ndjson: fixture not found: {path}")
        return open(path, "r", encoding="utf-8"), {
            "source_kind": "fixture",
            "source_path": str(path),
        }

    if serial is None:
        sys.exit(
            "capture_ndjson: pyserial is required for live capture; "
            "install it (`pip install pyserial`) or use --replay-fixture."
        )
    ser = serial.Serial(args.port, args.baud, timeout=1.0)
    # Wrap raw bytes into a text stream so the line loop below is shared.
    text = io.TextIOWrapper(ser, encoding="utf-8", errors="replace",
                            newline="\n", write_through=True)
    return text, {
        "source_kind": "serial",
        "source_port": args.port,
        "source_baud": args.baud,
    }


def write_meta(meta_path: Path, fields: dict) -> None:
    # Tiny hand-rolled YAML emitter; we only ship scalars + simple strings
    # so we don't pay for the PyYAML dependency just for this one writer.
    lines = []
    for k, v in fields.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            s = str(v).replace("\n", " ").strip()
            lines.append(f"{k}: {s}")
    meta_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--port",
                     help="serial device path (e.g. /dev/tty.usbmodem*).")
    src.add_argument("--replay-fixture",
                     help="path to a recorded NDJSON file (offline test mode).")
    p.add_argument("--baud", type=int, default=115200,
                   help="serial baud rate (default: 115200).")
    p.add_argument("--label", default="capture",
                   help="short tag baked into the output filename.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR),
                   help=f"output directory (default: {DEFAULT_OUT_DIR}).")
    p.add_argument("--max-lines", type=int, default=0,
                   help="stop after N lines (default: 0 = unlimited).")
    args = p.parse_args(argv)

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = utc_now_iso_basic()
    base = f"{stamp}_{args.label}"
    ndjson_path = out_dir / f"{base}.ndjson"
    meta_path = out_dir / f"{base}.meta.yaml"

    source, source_meta = open_source(args)
    start_wall = time.time()

    # Graceful Ctrl-C: flip a flag, drain on next loop entry.
    stop = {"requested": False}

    def _on_sigint(_signum, _frame):
        stop["requested"] = True

    signal.signal(signal.SIGINT, _on_sigint)

    line_count = 0
    with open(ndjson_path, "w", encoding="utf-8") as out:
        try:
            for line in source:
                if not line:
                    continue
                line = line.rstrip("\r\n")
                if not line:
                    continue
                out.write(line + "\n")
                line_count += 1
                if line_count % 100 == 0:
                    out.flush()
                if args.max_lines and line_count >= args.max_lines:
                    break
                if stop["requested"]:
                    break
        finally:
            out.flush()
            # If the source is a serial port wrapper, close it cleanly.
            try:
                source.close()
            except Exception:
                pass

    end_wall = time.time()

    meta = {
        "session_id": base,
        "label": args.label,
        "ndjson_path": str(ndjson_path.relative_to(REPO_ROOT))
            if ndjson_path.is_relative_to(REPO_ROOT) else str(ndjson_path),
        "host": socket.gethostname(),
        "host_platform": platform.platform(),
        "start_utc": dt.datetime.fromtimestamp(start_wall, dt.timezone.utc).isoformat(),
        "end_utc": dt.datetime.fromtimestamp(end_wall, dt.timezone.utc).isoformat(),
        "duration_s": round(end_wall - start_wall, 3),
        "line_count": line_count,
        "stopped_via": "sigint" if stop["requested"] else "eof-or-max",
        **source_meta,
    }
    write_meta(meta_path, meta)

    print(f"capture_ndjson: wrote {ndjson_path.relative_to(out_dir.parent)} "
          f"({line_count} line(s))")
    print(f"capture_ndjson: wrote {meta_path.relative_to(out_dir.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
