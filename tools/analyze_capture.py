#!/usr/bin/env python3
"""
analyze_capture.py — channel-agnostic NDJSON capture inspector for Mk0.5.

Spec: docs/plans/2026-tier1-launch/track-K-bench-readiness.md (commit K-1)

Reads an NDJSON capture file (as produced by tools/capture_ndjson.py) and
emits a one-page per-channel sanity report:

    - sample count
    - observed duration (s)
    - observed rate (Hz) vs SCHEMA-expected rate (Hz)
    - in-range percentage (from `q` field)
    - q-flag distribution
    - gap count (inter-sample dt > 2× expected period; continuous channels)
    - v field mean / std / min / max (numeric channels)
    - channels-seen vs channels-expected

No oracle, no HRV math, no pass/fail gate — those belong in
tools/analyze_g2.py (Track J commit 7). This module is a reporter.

Exit codes:
    0 — analyzed successfully (report may flag concerns)
    1 — file/parse error
    2 — usage error

Importable: `analyze(path) -> CaptureReport`, `format_report(r) -> str`.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# Channel registry — mirrors firmware/mk0.5/docs/SCHEMA.md §2.1 + §2.2.
# Authority: SCHEMA.md wins. If this table and SCHEMA.md disagree, fix this.
# ---------------------------------------------------------------------------

# kind == "continuous": expected_hz applies; rate-ratio + gap detection on.
# kind == "event":      no rate check; only count + value stats.
CHANNEL_REGISTRY: dict[str, dict[str, Any]] = {
    # v0.1 (psiStabilizer-ratified)
    "ppg-hrv":          {"kind": "continuous", "expected_hz": 100.0},
    # v0.2-proposed (HelmKit Mk0.5 adds)
    "ppg-rr":           {"kind": "event"},
    "gsr":              {"kind": "continuous", "expected_hz": 50.0},
    "temp-forehead":    {"kind": "continuous", "expected_hz": 4.0},
    "temp-forehead.amb":{"kind": "continuous", "expected_hz": 4.0},
    "ecg":              {"kind": "continuous", "expected_hz": 250.0},
    "ecg-rr":           {"kind": "event"},
    "temp-skin.L":      {"kind": "continuous", "expected_hz": 5.0},
    "temp-skin.R":      {"kind": "continuous", "expected_hz": 5.0},
    "vbat":             {"kind": "continuous", "expected_hz": 1.0},
    "cue":              {"kind": "event"},
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ChannelStats:
    name: str
    count: int = 0
    t_first: float | None = None
    t_last: float | None = None
    q_counts: dict[str, int] = field(default_factory=dict)
    v_sum: float = 0.0
    v_sumsq: float = 0.0
    v_min: float = math.inf
    v_max: float = -math.inf
    v_numeric_count: int = 0
    gap_count: int = 0
    prev_t: float | None = None

    @property
    def duration_s(self) -> float:
        if self.t_first is None or self.t_last is None:
            return 0.0
        return max(0.0, self.t_last - self.t_first)

    @property
    def observed_hz(self) -> float | None:
        if self.count < 2 or self.duration_s <= 0:
            return None
        return (self.count - 1) / self.duration_s

    @property
    def in_range_pct(self) -> float | None:
        total = sum(self.q_counts.values())
        if total == 0:
            return None
        return 100.0 * self.q_counts.get("ok", 0) / total

    @property
    def v_mean(self) -> float | None:
        if self.v_numeric_count == 0:
            return None
        return self.v_sum / self.v_numeric_count

    @property
    def v_std(self) -> float | None:
        n = self.v_numeric_count
        if n < 2:
            return None
        mean = self.v_sum / n
        var = max(0.0, (self.v_sumsq / n) - (mean * mean))
        return math.sqrt(var)


@dataclass
class CaptureReport:
    path: str
    total_lines: int = 0
    data_lines: int = 0
    meta_lines: int = 0      # `kind` = hello/smoke/error
    parse_errors: int = 0
    channels: dict[str, ChannelStats] = field(default_factory=dict)
    boot_ids: set[str] = field(default_factory=set)
    schemas_seen: set[str] = field(default_factory=set)
    smoke_results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------


def _ingest_line(report: CaptureReport, raw: str) -> None:
    raw = raw.strip()
    if not raw:
        return
    report.total_lines += 1
    try:
        rec = json.loads(raw)
    except json.JSONDecodeError:
        report.parse_errors += 1
        return
    if not isinstance(rec, dict):
        report.parse_errors += 1
        return

    boot = rec.get("boot")
    if isinstance(boot, str):
        report.boot_ids.add(boot)

    if "kind" in rec:
        report.meta_lines += 1
        kind = rec["kind"]
        if kind == "hello":
            schema = rec.get("schema")
            if isinstance(schema, str):
                report.schemas_seen.add(schema)
        elif kind == "smoke":
            report.smoke_results.append(rec)
        elif kind == "error":
            report.errors.append(rec)
        return

    ch = rec.get("ch")
    if not isinstance(ch, str):
        report.parse_errors += 1
        return
    report.data_lines += 1

    stats = report.channels.get(ch)
    if stats is None:
        stats = ChannelStats(name=ch)
        report.channels[ch] = stats

    t = rec.get("t")
    if isinstance(t, (int, float)):
        t = float(t)
        if stats.t_first is None:
            stats.t_first = t
        stats.t_last = t

        # Gap detection: only for continuous channels with a known rate.
        spec = CHANNEL_REGISTRY.get(ch, {})
        if spec.get("kind") == "continuous":
            expected_hz = spec.get("expected_hz")
            if expected_hz and stats.prev_t is not None:
                dt = t - stats.prev_t
                if dt > 2.0 / expected_hz:
                    stats.gap_count += 1
        stats.prev_t = t

    stats.count += 1

    q = rec.get("q")
    if isinstance(q, str):
        stats.q_counts[q] = stats.q_counts.get(q, 0) + 1

    v = rec.get("v")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        v = float(v)
        stats.v_sum += v
        stats.v_sumsq += v * v
        stats.v_numeric_count += 1
        if v < stats.v_min:
            stats.v_min = v
        if v > stats.v_max:
            stats.v_max = v


def analyze(path: str | Path) -> CaptureReport:
    """Analyze an NDJSON capture file and return a CaptureReport."""
    p = Path(path)
    report = CaptureReport(path=str(p))
    with open(p, "r", encoding="utf-8") as fh:
        for line in fh:
            _ingest_line(report, line)
    return report


def analyze_lines(lines: Iterable[str], label: str = "<stream>") -> CaptureReport:
    """Analyze an iterable of NDJSON lines (for tests / piping)."""
    report = CaptureReport(path=label)
    for line in lines:
        _ingest_line(report, line)
    return report


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _fmt_hz(hz: float | None) -> str:
    return f"{hz:6.2f}" if hz is not None else "   n/a"


def _fmt_pct(pct: float | None) -> str:
    return f"{pct:5.1f}%" if pct is not None else "  n/a"


def _fmt_num(v: float | None, w: int = 8, prec: int = 2) -> str:
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return f"{'n/a':>{w}}"
    return f"{v:{w}.{prec}f}"


def format_report(report: CaptureReport) -> str:
    lines: list[str] = []
    lines.append(f"capture: {report.path}")
    lines.append(
        f"  total={report.total_lines}  data={report.data_lines}  "
        f"meta={report.meta_lines}  parse_errors={report.parse_errors}"
    )
    if report.boot_ids:
        bids = ", ".join(sorted(report.boot_ids))
        lines.append(f"  boot_ids: {bids}")
        if len(report.boot_ids) > 1:
            lines.append("  ⚠ multiple boot_ids — session spans a reboot")
    if report.schemas_seen:
        lines.append(f"  schema: {', '.join(sorted(report.schemas_seen))}")

    # Smoke summary
    if report.smoke_results:
        oks = sum(1 for s in report.smoke_results if s.get("ok"))
        lines.append(
            f"  smoke: {oks}/{len(report.smoke_results)} passed"
        )
        for s in report.smoke_results:
            mark = "✓" if s.get("ok") else "✗"
            lines.append(
                f"    {mark} {s.get('source','?'):16s} "
                f"code={s.get('code','?')}  health={s.get('health','?')}  "
                f"ev=({s.get('ev_a','?')},{s.get('ev_b','?')})"
            )
    if report.errors:
        lines.append(f"  ⚠ {len(report.errors)} error event(s) emitted")

    # Channel table
    if report.channels:
        lines.append("")
        lines.append(
            f"  {'channel':<18s} {'count':>7s} {'dur':>7s} "
            f"{'obs':>7s} {'exp':>7s} {'rate%':>7s} "
            f"{'inrng':>6s} {'gaps':>5s} "
            f"{'v_mean':>10s} {'v_std':>8s} {'v_min':>8s} {'v_max':>8s}"
        )
        for ch in sorted(report.channels):
            s = report.channels[ch]
            spec = CHANNEL_REGISTRY.get(ch, {})
            kind = spec.get("kind", "unknown")
            expected = spec.get("expected_hz")
            observed = s.observed_hz
            if kind == "continuous" and expected and observed:
                ratio_pct = 100.0 * observed / expected
                ratio_str = f"{ratio_pct:6.1f}%"
            else:
                ratio_str = "    n/a"
            lines.append(
                f"  {ch:<18s} {s.count:7d} "
                f"{s.duration_s:7.1f} "
                f"{_fmt_hz(observed)} {_fmt_hz(expected if kind=='continuous' else None)} "
                f"{ratio_str} "
                f"{_fmt_pct(s.in_range_pct):>6s} "
                f"{s.gap_count:5d} "
                f"{_fmt_num(s.v_mean,10,2)} "
                f"{_fmt_num(s.v_std,8,2)} "
                f"{_fmt_num(s.v_min,8,2)} "
                f"{_fmt_num(s.v_max,8,2)}"
            )
            # Surface non-ok quality flags inline.
            non_ok = {k: v for k, v in s.q_counts.items() if k != "ok"}
            if non_ok:
                qstr = ", ".join(f"{k}={v}" for k, v in sorted(non_ok.items()))
                lines.append(f"    q-flags: {qstr}")

        # Channels-expected vs channels-seen sanity callout.
        seen = set(report.channels)
        registered = set(CHANNEL_REGISTRY)
        unregistered = seen - registered
        if unregistered:
            lines.append(
                f"  ⚠ unknown channels (not in SCHEMA): {sorted(unregistered)}"
            )
    else:
        lines.append("  (no data channels observed)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="analyze_capture.py",
        description="Channel-agnostic NDJSON capture inspector for Mk0.5.",
    )
    p.add_argument("path", help="Path to an NDJSON capture file.")
    p.add_argument(
        "--json", action="store_true",
        help="Emit a machine-readable JSON summary instead of the text report.",
    )
    args = p.parse_args(argv)

    try:
        report = analyze(args.path)
    except FileNotFoundError:
        print(f"analyze_capture: file not found: {args.path}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"analyze_capture: {exc}", file=sys.stderr)
        return 1

    if args.json:
        out = {
            "path": report.path,
            "total_lines": report.total_lines,
            "data_lines": report.data_lines,
            "meta_lines": report.meta_lines,
            "parse_errors": report.parse_errors,
            "boot_ids": sorted(report.boot_ids),
            "schemas_seen": sorted(report.schemas_seen),
            "smoke_results": report.smoke_results,
            "error_count": len(report.errors),
            "channels": {
                ch: {
                    "count": s.count,
                    "duration_s": s.duration_s,
                    "observed_hz": s.observed_hz,
                    "expected_hz": CHANNEL_REGISTRY.get(ch, {}).get("expected_hz"),
                    "kind": CHANNEL_REGISTRY.get(ch, {}).get("kind", "unknown"),
                    "in_range_pct": s.in_range_pct,
                    "q_counts": s.q_counts,
                    "gap_count": s.gap_count,
                    "v_mean": s.v_mean,
                    "v_std": s.v_std,
                    "v_min": s.v_min if s.v_numeric_count else None,
                    "v_max": s.v_max if s.v_numeric_count else None,
                }
                for ch, s in report.channels.items()
            },
        }
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
