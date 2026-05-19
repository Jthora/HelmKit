#!/usr/bin/env python3
"""
generate_fixtures.py — produce deterministic NDJSON fixtures for
tests/test_analyze_capture.py.

Run once when wire-format changes; commits the .ndjson outputs.

Usage:
    python3 tests/generate_fixtures.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
BOOT = "deadbeefcafef00d"


def _hello(t: float) -> dict:
    return {
        "t": t, "kind": "hello", "mk": 0,
        "git": "fixture", "dirty": 0, "schema": "0.1",
        "boot": BOOT, "build": "fixture fixture",
    }


def _smoke(t: float, source: str, ok: bool,
           ev_a: int = 0, ev_b: int = 0,
           code: str = "kOk", health: str = "kOk") -> dict:
    return {
        "t": t, "kind": "smoke", "source": source,
        "ok": 1 if ok else 0, "code": code, "code_num": 0,
        "health": health, "ev_a": ev_a, "ev_b": ev_b,
        "note": "", "boot": BOOT,
    }


def _dump(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def gen_ppg_60s_good() -> None:
    """60 seconds of ppg-hrv at 100 Hz, all q=ok, plus a few ppg-rr events."""
    recs: list[dict] = [_hello(0.0), _smoke(0.5, "ppg-hrv", True, ev_a=600)]
    # 100 Hz for 60 s = 6000 samples
    for i in range(6000):
        t = 1.0 + i * 0.01
        # Sinusoidal-ish PPG ADC counts around 250000 with 60 BPM modulation.
        v = int(250000 + 5000 * math.sin(2 * math.pi * t * (60.0 / 60.0)))
        recs.append({"t": round(t, 3), "ch": "ppg-hrv", "v": v,
                     "q": "ok", "boot": BOOT})
    # ~60 RR events over 60 s, ~1000 ms apart
    for i in range(60):
        t = 1.5 + i * 1.0
        rr = 1000 if i > 0 else 0
        recs.append({"t": round(t, 3), "ch": "ppg-rr", "v": rr,
                     "q": "ok", "conf": 1.4, "boot": BOOT})
    recs.sort(key=lambda r: (r["t"], r.get("ch", "")))
    _dump(FIXTURE_DIR / "ppg_60s_good.ndjson", recs)


def gen_mlx_gsr_30s_good() -> None:
    """30 s of MLX (4 Hz, paired obj/amb) + GSR (50 Hz)."""
    recs: list[dict] = [
        _hello(0.0),
        _smoke(0.5, "temp-forehead", True, ev_a=120),
        _smoke(0.6, "gsr", True, ev_a=1500),
    ]
    # MLX 4 Hz for 30 s = 120 paired samples
    for i in range(120):
        t = round(1.0 + i * 0.25, 3)
        obj_c = 36.5 + 0.05 * math.sin(i * 0.1)
        amb_c = 22.0 + 0.02 * math.sin(i * 0.05)
        recs.append({"t": t, "ch": "temp-forehead",
                     "v": round(obj_c, 2), "q": "ok", "boot": BOOT})
        recs.append({"t": t, "ch": "temp-forehead.amb",
                     "v": round(amb_c, 2), "q": "ok", "boot": BOOT})
    # GSR 50 Hz for 30 s = 1500 samples
    for i in range(1500):
        t = round(1.0 + i * 0.02, 3)
        raw = int(2048 + 200 * math.sin(i * 0.01))
        recs.append({"t": t, "ch": "gsr", "v": raw,
                     "q": "ok", "boot": BOOT})
    recs.sort(key=lambda r: (r["t"], r.get("ch", "")))
    _dump(FIXTURE_DIR / "mlx_gsr_30s_good.ndjson", recs)


def gen_ppg_60s_with_gap() -> None:
    """60 s of ppg-hrv with a deliberate 0.5 s gap at the 30 s mark."""
    recs: list[dict] = [_hello(0.0), _smoke(0.5, "ppg-hrv", True, ev_a=600)]
    for i in range(6000):
        t = 1.0 + i * 0.01
        # Skip 50 samples (0.5 s) between sample 3000 and 3050 to create a gap.
        if 3000 <= i < 3050:
            continue
        v = int(250000 + 5000 * math.sin(2 * math.pi * t))
        recs.append({"t": round(t, 3), "ch": "ppg-hrv", "v": v,
                     "q": "ok", "boot": BOOT})
    recs.sort(key=lambda r: (r["t"], r.get("ch", "")))
    _dump(FIXTURE_DIR / "ppg_60s_with_gap.ndjson", recs)


def main() -> None:
    gen_ppg_60s_good()
    gen_mlx_gsr_30s_good()
    gen_ppg_60s_with_gap()
    print(f"wrote fixtures into {FIXTURE_DIR}")


if __name__ == "__main__":
    main()
