#!/usr/bin/env python3
"""
analyze_g2.py — G2 HRV validation analyzer for Mk0.5.

Spec: docs/protocols/g2_hrv_validation.md §5 and §6
      docs/plans/2026-tier1-launch/track-J-mk0.5-sensor-bringup.md (commit J-7)

Compares a DUT `ppg-rr` stream (from Mk0.5 firmware) against an oracle
reference RR stream (Polar H10 CSV export, OR another NDJSON channel —
typically `ecg-rr` from AD8232, the canonical G2 oracle channel per
SCHEMA.md §2.2).

Computes, per segment in the 5/5/5 protocol:
    mean_rr_ms, rmssd_ms, pnn50_pct, n_beats, n_out_of_range

Then applies the three pass criteria from `g2_hrv_validation.md` §6:
    1. Baseline RMSSD relative error ≤ 20 %.
    2. Oracle RMSSD rises ≥ 1.5× baseline→paced AND
       DUT    RMSSD rises ≥ 1.3× baseline→paced.
    3. Paced RMSSD relative error ≤ 20 %.

A session passes G2 iff all three hold. Recovery is reported, not gated.

This module is a reporter + evaluator. It does NOT decide whether the
*device* (across multiple sessions) closes G2 — that is a 3-session
roll-up handled downstream.

Exit codes:
    0 — analysis completed; session PASSED G2 (all three criteria).
    1 — analysis completed; session FAILED G2.
    2 — file/parse error.
    3 — usage error.

Importable surface:
    load_rr_from_ndjson(path, channel="ppg-rr") -> list[RRSample]
    load_rr_from_csv(path, *, oracle_t0=0.0, rr_column=None) -> list[RRSample]
    compute_segment_metrics(samples, segment) -> SegmentMetrics
    evaluate_g2(dut, oracle, segments) -> G2Report
    format_g2_report(report) -> str

Stdlib only. No numpy. No scipy. No matplotlib.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence


# ---------------------------------------------------------------------------
# Pass-criteria thresholds — authoritative source: g2_hrv_validation.md §6.
# If you edit these, edit the doc in the same commit (or vice versa).
# ---------------------------------------------------------------------------

CRIT1_MAX_REL_ERR: float = 0.20    # baseline relative RMSSD error
CRIT2_ORACLE_MIN_RATIO: float = 1.5  # oracle RMSSD paced / baseline
CRIT2_DUT_MIN_RATIO: float = 1.3     # DUT    RMSSD paced / baseline
CRIT3_MAX_REL_ERR: float = 0.20    # paced relative RMSSD error

# Default 5/5/5 segment durations (seconds).
DEFAULT_BASELINE_S: float = 300.0
DEFAULT_PACED_S: float = 300.0
DEFAULT_RECOVERY_S: float = 300.0

SEGMENT_NAMES: tuple[str, ...] = ("baseline", "paced", "recovery")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RRSample:
    """A single RR interval observation."""
    t: float            # session-time seconds (beat time)
    rr_ms: float        # interval to previous accepted peak
    q: str = "ok"       # "ok" | "out-of-range" | "gap" | ...
    conf: float | None = None


@dataclass(frozen=True)
class Segment:
    """A [t_start, t_end) window inside the session timeline."""
    name: str
    t_start: float
    t_end: float

    def contains(self, sample: RRSample) -> bool:
        return self.t_start <= sample.t < self.t_end


@dataclass(frozen=True)
class SegmentMetrics:
    """HRV metrics for one stream over one segment."""
    name: str
    n_beats: int
    n_out_of_range: int
    mean_rr_ms: float | None
    rmssd_ms: float | None
    pnn50_pct: float | None


@dataclass
class G2Report:
    """Full G2 evaluation result for one session."""
    dut_segments: dict[str, SegmentMetrics] = field(default_factory=dict)
    oracle_segments: dict[str, SegmentMetrics] = field(default_factory=dict)
    crit1_baseline_rel_err: float | None = None
    crit1_pass: bool = False
    crit2_oracle_paced_ratio: float | None = None
    crit2_dut_paced_ratio: float | None = None
    crit2_pass: bool = False
    crit3_paced_rel_err: float | None = None
    crit3_pass: bool = False
    overall_pass: bool = False
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_rr_from_ndjson(
    path: str | Path,
    *,
    channel: str = "ppg-rr",
) -> list[RRSample]:
    """Load RR samples from a Mk0.5 NDJSON capture, filtering by channel.

    Per SCHEMA.md §2.2, `ppg-rr` and `ecg-rr` carry `v` as RR-interval in ms
    and may carry a non-standard `conf` field. The first peak in a stream
    emits `v=0` and is silently dropped here (no interval yet).
    """
    samples: list[RRSample] = []
    p = Path(path)
    with open(p, "r", encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            if rec.get("ch") != channel:
                continue
            t = rec.get("t")
            v = rec.get("v")
            if not isinstance(t, (int, float)):
                continue
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            if v <= 0:
                # First-peak sentinel; not a real interval.
                continue
            q = rec.get("q", "ok")
            if not isinstance(q, str):
                q = "ok"
            conf_raw = rec.get("conf")
            conf = float(conf_raw) if isinstance(conf_raw, (int, float)) else None
            samples.append(RRSample(t=float(t), rr_ms=float(v), q=q, conf=conf))
    return samples


def load_rr_from_csv(
    path: str | Path,
    *,
    oracle_t0: float = 0.0,
    rr_column: int | None = None,
) -> list[RRSample]:
    """Load RR samples from a Polar-style CSV export.

    Per g2_hrv_validation.md §3 the canonical layout is:
        Phone timestamp ; sensor name ; RR-interval [ms]

    But the script accepts:
        - any delimiter sniff-able by csv.Sniffer (comma, semicolon, tab),
        - an explicit `rr_column` override (0-indexed),
        - either header-named ("RR-interval ...") or column-index fallback.

    Beat times are synthesized by cumsum of RR (seconds), anchored at
    `oracle_t0`. The first beat is placed at `oracle_t0 + rr0/1000`.
    Out-of-range / non-numeric / zero RR values are dropped.
    """
    p = Path(path)
    with open(p, "r", encoding="utf-8", newline="") as fh:
        head = fh.read(2048)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(head, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.reader(fh, dialect)
        first = next(reader, None)
        if first is None:
            return []

        # Detect header vs first data row.
        def _is_numeric(s: str) -> bool:
            try:
                float(s)
                return True
            except ValueError:
                return False

        header_present = not all(_is_numeric(c.strip()) for c in first if c.strip())

        if rr_column is None:
            if header_present:
                for i, h in enumerate(first):
                    hl = h.strip().lower()
                    if "rr" in hl and "interval" in hl:
                        rr_column = i
                        break
            if rr_column is None:
                rr_column = 2  # protocol default

        samples: list[RRSample] = []
        t = float(oracle_t0)

        def _ingest_row(row: list[str]) -> None:
            nonlocal t
            if len(row) <= rr_column:
                return
            try:
                rr = float(row[rr_column])
            except ValueError:
                return
            if rr <= 0 or not math.isfinite(rr):
                return
            t += rr / 1000.0
            samples.append(RRSample(t=t, rr_ms=rr, q="ok"))

        if not header_present:
            _ingest_row(first)
        for row in reader:
            _ingest_row(row)
        return samples


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _in_range(samples: Iterable[RRSample]) -> list[float]:
    """Return RR (ms) of `ok` samples only, preserving order."""
    return [s.rr_ms for s in samples if s.q == "ok"]


def compute_segment_metrics(
    samples: Sequence[RRSample],
    segment: Segment,
) -> SegmentMetrics:
    """Compute the §5 metric block for one stream over one segment.

    `mean_rr_ms`, `rmssd_ms`, `pnn50_pct` are computed on the in-range
    subsequence. `n_beats` counts in-range samples; `n_out_of_range`
    counts dropped ones. RMSSD/PNN50 require ≥ 2 in-range samples.
    """
    in_seg = [s for s in samples if segment.contains(s)]
    rr = _in_range(in_seg)
    n_oor = sum(1 for s in in_seg if s.q != "ok")
    n = len(rr)

    if n == 0:
        return SegmentMetrics(
            name=segment.name,
            n_beats=0,
            n_out_of_range=n_oor,
            mean_rr_ms=None,
            rmssd_ms=None,
            pnn50_pct=None,
        )

    mean_rr = sum(rr) / n

    if n < 2:
        return SegmentMetrics(
            name=segment.name,
            n_beats=n,
            n_out_of_range=n_oor,
            mean_rr_ms=mean_rr,
            rmssd_ms=None,
            pnn50_pct=None,
        )

    diffs = [rr[i + 1] - rr[i] for i in range(n - 1)]
    # RMSSD: sqrt( (1/(N-1)) * sum d_i^2 ) where d_i are successive diffs.
    # With N samples there are N-1 diffs; the normalization is (N-1) per
    # the protocol formula in §5.
    rmssd = math.sqrt(sum(d * d for d in diffs) / (n - 1))
    pnn50 = 100.0 * sum(1 for d in diffs if abs(d) > 50.0) / len(diffs)

    return SegmentMetrics(
        name=segment.name,
        n_beats=n,
        n_out_of_range=n_oor,
        mean_rr_ms=mean_rr,
        rmssd_ms=rmssd,
        pnn50_pct=pnn50,
    )


# ---------------------------------------------------------------------------
# Segment construction
# ---------------------------------------------------------------------------


def make_default_segments(
    t0: float,
    *,
    baseline_s: float = DEFAULT_BASELINE_S,
    paced_s: float = DEFAULT_PACED_S,
    recovery_s: float = DEFAULT_RECOVERY_S,
) -> tuple[Segment, Segment, Segment]:
    """Build the standard 5/5/5 segments anchored at session-time `t0`."""
    bs = Segment("baseline", t0, t0 + baseline_s)
    ps = Segment("paced", bs.t_end, bs.t_end + paced_s)
    rs = Segment("recovery", ps.t_end, ps.t_end + recovery_s)
    return bs, ps, rs


# ---------------------------------------------------------------------------
# Evaluation (§6 pass criteria)
# ---------------------------------------------------------------------------


def _rel_err(dut: float | None, oracle: float | None) -> float | None:
    """Relative error |dut - oracle| / oracle (oracle is the denominator)."""
    if dut is None or oracle is None or oracle == 0:
        return None
    return abs(dut - oracle) / oracle


def _ratio(paced: float | None, baseline: float | None) -> float | None:
    """Paced / baseline ratio. None if either is missing or baseline == 0."""
    if paced is None or baseline is None or baseline == 0:
        return None
    return paced / baseline


def evaluate_g2(
    dut: Sequence[RRSample],
    oracle: Sequence[RRSample],
    segments: Sequence[Segment],
) -> G2Report:
    """Run the §6 G2 evaluation. Caller supplies (baseline, paced, recovery)."""
    if len(segments) != 3:
        raise ValueError("evaluate_g2 expects exactly 3 segments")
    if tuple(s.name for s in segments) != SEGMENT_NAMES:
        raise ValueError(
            f"segments must be named {SEGMENT_NAMES}, got "
            f"{tuple(s.name for s in segments)}"
        )

    report = G2Report()
    for seg in segments:
        report.dut_segments[seg.name] = compute_segment_metrics(dut, seg)
        report.oracle_segments[seg.name] = compute_segment_metrics(oracle, seg)

    dut_base = report.dut_segments["baseline"].rmssd_ms
    dut_paced = report.dut_segments["paced"].rmssd_ms
    orc_base = report.oracle_segments["baseline"].rmssd_ms
    orc_paced = report.oracle_segments["paced"].rmssd_ms

    # Criterion 1: baseline agreement.
    err1 = _rel_err(dut_base, orc_base)
    report.crit1_baseline_rel_err = err1
    report.crit1_pass = err1 is not None and err1 <= CRIT1_MAX_REL_ERR

    # Criterion 2: paced response engaged on both streams.
    r_orc = _ratio(orc_paced, orc_base)
    r_dut = _ratio(dut_paced, dut_base)
    report.crit2_oracle_paced_ratio = r_orc
    report.crit2_dut_paced_ratio = r_dut
    report.crit2_pass = (
        r_orc is not None
        and r_dut is not None
        and r_orc >= CRIT2_ORACLE_MIN_RATIO
        and r_dut >= CRIT2_DUT_MIN_RATIO
    )

    # Criterion 3: paced agreement.
    err3 = _rel_err(dut_paced, orc_paced)
    report.crit3_paced_rel_err = err3
    report.crit3_pass = err3 is not None and err3 <= CRIT3_MAX_REL_ERR

    report.overall_pass = (
        report.crit1_pass and report.crit2_pass and report.crit3_pass
    )

    # Diagnostic notes for the human-readable report.
    if not report.crit2_pass and r_orc is not None and r_orc < CRIT2_ORACLE_MIN_RATIO:
        report.notes.append(
            "oracle did not exhibit a paced-breathing RMSSD rise — "
            "the manoeuvre likely did not engage (operator nasal/laboured "
            "breathing? talking? fidgeting?). Per protocol §8 this is NOT "
            "a device failure; re-run the session."
        )
    if dut_base is None:
        report.notes.append(
            "DUT baseline RMSSD is None — insufficient in-range beats in "
            "the baseline segment. Check capture coverage / sensor mount."
        )
    if orc_base is None:
        report.notes.append(
            "Oracle baseline RMSSD is None — insufficient in-range beats. "
            "Check oracle alignment (--oracle-t0) and CSV column mapping."
        )

    return report


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _fmt_ms(v: float | None) -> str:
    return f"{v:8.2f}" if v is not None else f"{'n/a':>8}"


def _fmt_pct(v: float | None) -> str:
    return f"{v:6.2f}%" if v is not None else f"{'n/a':>7}"


def _fmt_ratio(v: float | None) -> str:
    return f"{v:5.2f}x" if v is not None else f"{'n/a':>6}"


def _fmt_rel_err(v: float | None) -> str:
    return f"{100.0 * v:6.2f}%" if v is not None else f"{'n/a':>7}"


def _fmt_pass(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def format_g2_report(report: G2Report) -> str:
    out: list[str] = []
    out.append("G2 HRV Validation Report")
    out.append("=" * 60)
    out.append("")
    out.append(f"{'segment':<10s}  {'stream':<7s}  "
               f"{'n':>5s}  {'oor':>4s}  "
               f"{'mean_rr':>9s}  {'rmssd':>9s}  {'pnn50':>8s}")
    for seg_name in SEGMENT_NAMES:
        for stream_label, segs in (
            ("DUT", report.dut_segments),
            ("oracle", report.oracle_segments),
        ):
            m = segs.get(seg_name)
            if m is None:
                continue
            out.append(
                f"{seg_name:<10s}  {stream_label:<7s}  "
                f"{m.n_beats:5d}  {m.n_out_of_range:4d}  "
                f"{_fmt_ms(m.mean_rr_ms)}  {_fmt_ms(m.rmssd_ms)}  "
                f"{_fmt_pct(m.pnn50_pct)}"
            )
        out.append("")

    out.append("-" * 60)
    out.append("Pass criteria (g2_hrv_validation.md §6):")
    out.append(
        f"  [{_fmt_pass(report.crit1_pass)}] 1. baseline rel err "
        f"{_fmt_rel_err(report.crit1_baseline_rel_err)} "
        f"(≤ {100.0 * CRIT1_MAX_REL_ERR:.0f}%)"
    )
    out.append(
        f"  [{_fmt_pass(report.crit2_pass)}] 2. paced response: "
        f"oracle {_fmt_ratio(report.crit2_oracle_paced_ratio)} "
        f"(≥ {CRIT2_ORACLE_MIN_RATIO:.2f}x), "
        f"DUT {_fmt_ratio(report.crit2_dut_paced_ratio)} "
        f"(≥ {CRIT2_DUT_MIN_RATIO:.2f}x)"
    )
    out.append(
        f"  [{_fmt_pass(report.crit3_pass)}] 3. paced rel err "
        f"{_fmt_rel_err(report.crit3_paced_rel_err)} "
        f"(≤ {100.0 * CRIT3_MAX_REL_ERR:.0f}%)"
    )
    out.append("")
    out.append(f"SESSION RESULT: {_fmt_pass(report.overall_pass)}")
    out.append(
        "  (G2 closes after 3 independent passing sessions on 3 days, "
        "same firmware commit.)"
    )

    if report.notes:
        out.append("")
        out.append("Notes:")
        for n in report.notes:
            out.append(f"  - {n}")

    return "\n".join(out)


def report_to_json(report: G2Report) -> dict:
    """Machine-readable form of a G2Report."""
    def _seg_dict(m: SegmentMetrics) -> dict:
        return {
            "name": m.name,
            "n_beats": m.n_beats,
            "n_out_of_range": m.n_out_of_range,
            "mean_rr_ms": m.mean_rr_ms,
            "rmssd_ms": m.rmssd_ms,
            "pnn50_pct": m.pnn50_pct,
        }
    return {
        "dut": {n: _seg_dict(m) for n, m in report.dut_segments.items()},
        "oracle": {n: _seg_dict(m) for n, m in report.oracle_segments.items()},
        "criteria": {
            "crit1": {
                "pass": report.crit1_pass,
                "baseline_rel_err": report.crit1_baseline_rel_err,
                "threshold": CRIT1_MAX_REL_ERR,
            },
            "crit2": {
                "pass": report.crit2_pass,
                "oracle_paced_ratio": report.crit2_oracle_paced_ratio,
                "dut_paced_ratio": report.crit2_dut_paced_ratio,
                "oracle_threshold": CRIT2_ORACLE_MIN_RATIO,
                "dut_threshold": CRIT2_DUT_MIN_RATIO,
            },
            "crit3": {
                "pass": report.crit3_pass,
                "paced_rel_err": report.crit3_paced_rel_err,
                "threshold": CRIT3_MAX_REL_ERR,
            },
        },
        "overall_pass": report.overall_pass,
        "notes": report.notes,
    }


# ---------------------------------------------------------------------------
# Self-test fixture generator
# ---------------------------------------------------------------------------


def synth_session(
    *,
    seed: int = 1729,
    t0: float = 30.0,
    baseline_s: float = DEFAULT_BASELINE_S,
    paced_s: float = DEFAULT_PACED_S,
    recovery_s: float = DEFAULT_RECOVERY_S,
    mean_rr_ms: float = 900.0,
    sigma_baseline_ms: float = 25.0,
    sigma_paced_ms: float = 75.0,
    sigma_recovery_ms: float = 35.0,
    dut_noise_ms: float = 12.0,
    dut_bias_ms: float = 0.0,
) -> tuple[list[RRSample], list[RRSample], tuple[Segment, Segment, Segment]]:
    """Generate a correlated DUT + oracle RR pair plus the 5/5/5 segments.

    Oracle gets the "true" RR sequence; DUT = oracle + N(bias, noise).
    Default knobs produce a session that comfortably passes all three
    criteria. Crank up `dut_bias_ms` to fail crit1/crit3, or drop
    `sigma_paced_ms` close to baseline to fail crit2.
    """
    rng = random.Random(seed)
    segments = make_default_segments(
        t0, baseline_s=baseline_s, paced_s=paced_s, recovery_s=recovery_s
    )

    oracle: list[RRSample] = []
    t = t0
    for seg, sigma in (
        (segments[0], sigma_baseline_ms),
        (segments[1], sigma_paced_ms),
        (segments[2], sigma_recovery_ms),
    ):
        while t < seg.t_end:
            rr = rng.gauss(mean_rr_ms, sigma)
            # Clip to physiological range; protocol §2.2 marks
            # out-of-range as 250..2000.
            rr = max(400.0, min(1600.0, rr))
            t += rr / 1000.0
            if t < seg.t_end:
                oracle.append(RRSample(t=t, rr_ms=rr, q="ok"))

    dut: list[RRSample] = []
    for s in oracle:
        rr_dut = s.rr_ms + dut_bias_ms + rng.gauss(0.0, dut_noise_ms)
        rr_dut = max(250.0, min(2000.0, rr_dut))
        dut.append(RRSample(t=s.t, rr_ms=rr_dut, q="ok"))

    return dut, oracle, segments


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_oracle(
    *,
    oracle_path: str | None,
    oracle_ndjson: bool,
    oracle_channel: str,
    oracle_t0: float,
    oracle_rr_column: int | None,
) -> list[RRSample]:
    if oracle_path is None:
        return []
    if oracle_ndjson or oracle_path.lower().endswith(".ndjson"):
        return load_rr_from_ndjson(oracle_path, channel=oracle_channel)
    return load_rr_from_csv(
        oracle_path, oracle_t0=oracle_t0, rr_column=oracle_rr_column
    )


def _cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="analyze_g2.py",
        description="G2 HRV validation analyzer for Mk0.5.",
    )
    p.add_argument("--dut", help="Mk0.5 NDJSON capture (DUT).")
    p.add_argument("--dut-channel", default="ppg-rr",
                   help="NDJSON channel to use as DUT (default: ppg-rr).")
    p.add_argument("--oracle",
                   help="Oracle source: Polar CSV or another NDJSON file.")
    p.add_argument("--oracle-ndjson", action="store_true",
                   help="Force NDJSON interpretation of --oracle even without "
                        ".ndjson suffix.")
    p.add_argument("--oracle-channel", default="ecg-rr",
                   help="NDJSON channel when oracle is NDJSON "
                        "(default: ecg-rr — the canonical G2 oracle channel).")
    p.add_argument("--oracle-t0", type=float, default=0.0,
                   help="Session-time (s) of the first oracle beat. Aligns "
                        "CSV oracle to DUT session clock. Ignored for NDJSON.")
    p.add_argument("--oracle-rr-column", type=int, default=None,
                   help="0-indexed column of RR-interval in oracle CSV "
                        "(default: auto-detect, fallback column 2).")
    p.add_argument("--t0", type=float, default=0.0,
                   help="Session-time (s) where the baseline segment begins.")
    p.add_argument("--baseline-s", type=float, default=DEFAULT_BASELINE_S)
    p.add_argument("--paced-s", type=float, default=DEFAULT_PACED_S)
    p.add_argument("--recovery-s", type=float, default=DEFAULT_RECOVERY_S)
    p.add_argument("--json", action="store_true",
                   help="Emit machine-readable JSON instead of text report.")
    p.add_argument("--self-test", action="store_true",
                   help="Run a synthetic correlated session and analyze it.")
    args = p.parse_args(argv)

    if args.self_test:
        dut, oracle, segments = synth_session()
        report = evaluate_g2(dut, oracle, segments)
    else:
        if args.dut is None or args.oracle is None:
            print("analyze_g2: --dut and --oracle are required "
                  "(or use --self-test).", file=sys.stderr)
            return 3
        try:
            dut = load_rr_from_ndjson(args.dut, channel=args.dut_channel)
            oracle = _load_oracle(
                oracle_path=args.oracle,
                oracle_ndjson=args.oracle_ndjson,
                oracle_channel=args.oracle_channel,
                oracle_t0=args.oracle_t0,
                oracle_rr_column=args.oracle_rr_column,
            )
        except FileNotFoundError as exc:
            print(f"analyze_g2: file not found: {exc.filename}", file=sys.stderr)
            return 2
        except OSError as exc:
            print(f"analyze_g2: {exc}", file=sys.stderr)
            return 2
        segments = make_default_segments(
            args.t0,
            baseline_s=args.baseline_s,
            paced_s=args.paced_s,
            recovery_s=args.recovery_s,
        )
        report = evaluate_g2(dut, oracle, segments)

    if args.json:
        print(json.dumps(report_to_json(report), indent=2, sort_keys=True))
    else:
        print(format_g2_report(report))

    return 0 if report.overall_pass else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
