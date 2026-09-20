#!/usr/bin/env python3
"""
analyze_dyadic_coherence.py — cross-subject physiological synchrony
analysis for two (or more, run pairwise) simultaneous HelmKit wearers.

Design doc: docs/psionic_engineering/computational_toolkit.md

Why this exists: `tools/analyze_g2.py` already computes RMSSD/pNN50 for
a SINGLE subject. That is standard biometrics and does not engage the
wiki's `Collective Consciousness` claim, which is specifically about
CROSS-subject correlation (field energy density claimed to scale as
N^4 with practitioner coherence — a statement about coupling BETWEEN
wearers, not about any one wearer's own HRV). This tool tests that
class of claim directly: is there more RR-interval synchrony between
two simultaneous wearers than chance (and than shared mundane
confounds — room temperature, shared audio cues, coincidental breathing
entrainment) would produce?

Two synchrony metrics, both computed on RR-interval streams resampled
to a common uniform time grid:

  1. Lagged cross-correlation — Pearson r between the two z-scored
     series at every lag in [-max_lag, +max_lag], reporting the peak
     |r| and its lag.
  2. Cross-recurrence quantification (CRQA) — recurrence rate (RR) and
     determinism (DET, fraction of recurrent points lying on diagonal
     lines >= lmin), a standard method in dyadic physiological-coupling
     research (see e.g. Marwan et al. 2007, "Recurrence plots for the
     analysis of complex systems," Physics Reports 438).

CRITICAL: neither metric means anything without a null distribution.
Two people breathing in the same room, or both entrained to the same
background audio, will show real cross-correlation for entirely mundane
reasons. This tool's `surrogate` test is not optional decoration — it
is what turns "these two numbers correlate" into "these two numbers
correlate MORE than would happen if each subject's own dynamics were
preserved but the cross-timing between them were destroyed." The
surrogate method is circular time-shift (Theiler et al. 1992, "Testing
for nonlinearity in time series: the method of surrogate data," Physica
D 58) — it preserves each individual signal's own autocorrelation
structure while randomizing the alignment between the two subjects.

A significant result here is evidence of ANOMALOUS SYNCHRONY, not
evidence of psi. Ordinary explanations (shared paced-breathing cue,
shared room acoustics affecting both subjects' respiratory sinus
arrhythmia, clock skew between two capture devices) must be ruled out
before any psi-adjacent interpretation is entertained — see
`docs/falsification.md`'s sham-control requirements and the wiki's own
`Sham Control Design` page.

Two extensions beyond the original single-window, RR-interval-only
version:

  - **Segment-aware analysis** (`analyze_dyadic_by_segment`). Reuses
    `analyze_g2.py`'s `Segment`/`make_default_segments` so the same
    baseline/paced/recovery (or any named) windows used for single-
    subject G2 analysis can be applied here — this is what makes "did
    synchrony rise specifically during the intervention window" an
    askable question, instead of only "was there synchrony somewhere in
    the whole session" (a much weaker, more confound-prone claim).
  - **Generic scalar-channel support** (`ScalarSample`,
    `load_scalar_channel_from_ndjson`). The original version only
    accepted `RRSample`/RR-interval data. GSR and temperature channels
    already exist in the Mk0.5 sensor roster and may show cross-subject
    coupling that HRV does not (or vice versa) — the resample/
    correlate/CRQA/surrogate machinery was already channel-agnostic
    under the hood; only the loading layer was RR-specific. Note the
    RR-specific "v<=0 is a first-peak sentinel" convention does NOT
    apply to a generic scalar channel, so this is a genuinely separate
    loader, not a parameterization of `load_rr_from_ndjson`.

Stdlib only. No numpy, no scipy — see tools/requirements.txt and the
same discipline in tools/analyze_g2.py. This means the CRQA distance
matrix is O(n^2) in pure Python; see `MAX_RESAMPLED_LENGTH` below.

Exit codes:
    0 — analysis completed (regardless of significance — see --json/-text
        output for the actual finding)
    2 — file/parse error
    3 — usage error
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

try:
    from tools.analyze_g2 import RRSample, Segment, load_rr_from_ndjson, make_default_segments
except ImportError:
    # Running as `python3 tools/analyze_dyadic_coherence.py` directly (not
    # via `-m` or an already-importing test runner) only puts tools/ itself
    # on sys.path, not the repo root `tools` is a namespace package under.
    # Fall back to adding the repo root explicitly.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools.analyze_g2 import RRSample, Segment, load_rr_from_ndjson, make_default_segments

# O(n^2) distance matrix in pure Python -- guard against accidental
# multi-hour sessions at 1 Hz blowing up to minutes of runtime.
MAX_RESAMPLED_LENGTH = 3600  # e.g. 1 hour at 1 Hz, or 30 min at 2 Hz


# ---------------------------------------------------------------------------
# Generic scalar-channel support (GSR, temperature, ... not just RR)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScalarSample:
    """A single (time, value) observation on any scalar NDJSON channel
    (GSR conductance, temperature, etc.) — the generic counterpart to
    `RRSample` for channels that are not RR-interval streams."""
    t: float
    value: float
    q: str = "ok"


def load_scalar_channel_from_ndjson(path: str | Path, *, channel: str) -> list[ScalarSample]:
    """Load samples from an arbitrary scalar NDJSON channel (e.g. `gsr`,
    `temp-ir`, `temp-skin`).

    Unlike `load_rr_from_ndjson`, this does NOT drop `v <= 0` as a
    "first-peak sentinel" — that convention is specific to RR-interval
    streams (the first beat has no preceding interval yet). A GSR
    reading of 0 or a sub-zero relative temperature is a real
    observation, not a sentinel, so dropping it here would silently
    corrupt non-RR channels.
    """
    samples: list[ScalarSample] = []
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
            if not isinstance(rec, dict) or rec.get("ch") != channel:
                continue
            t, v = rec.get("t"), rec.get("v")
            if not isinstance(t, (int, float)):
                continue
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
                continue
            q = rec.get("q", "ok")
            if not isinstance(q, str):
                q = "ok"
            samples.append(ScalarSample(t=float(t), value=float(v), q=q))
    return samples


def _sample_value(s: RRSample | ScalarSample) -> float:
    """Duck-typed value extraction: RRSample carries `.rr_ms`, ScalarSample
    (and anything else scalar-channel-shaped) carries `.value`. Lets every
    downstream function in this module accept either without a manual
    conversion step at every call site."""
    return s.rr_ms if hasattr(s, "rr_ms") else s.value


# ---------------------------------------------------------------------------
# Resampling: irregular scalar-channel events -> uniform time grid
# ---------------------------------------------------------------------------


def resample_uniform(
    samples: Sequence[RRSample] | Sequence[ScalarSample], *, t_start: float, t_end: float, dt: float
) -> list[float]:
    """Linearly interpolate the channel value onto a uniform grid at
    t_start, t_start+dt, ..., < t_end.

    `samples` are (t, value) event points — either `RRSample` (RR-
    interval streams) or `ScalarSample` (any other scalar channel), via
    `_sample_value`. Before the first event or after the last, the
    nearest value is held flat (no extrapolation beyond the observed
    range).
    """
    ok = sorted((s.t, _sample_value(s)) for s in samples if s.q == "ok")
    if len(ok) < 2:
        raise ValueError("need >= 2 in-range samples to resample")
    times = [t for t, _ in ok]
    values = [v for _, v in ok]

    n_steps = int(math.floor((t_end - t_start) / dt))
    if n_steps <= 0:
        raise ValueError("t_end must be after t_start by at least one dt")

    out: list[float] = []
    idx = 0
    n_events = len(times)
    for i in range(n_steps):
        t = t_start + i * dt
        while idx < n_events - 2 and times[idx + 1] < t:
            idx += 1
        if t <= times[0]:
            out.append(values[0])
        elif t >= times[-1]:
            out.append(values[-1])
        else:
            t0, t1 = times[idx], times[idx + 1]
            v0, v1 = values[idx], values[idx + 1]
            frac = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            out.append(v0 + frac * (v1 - v0))
    return out


# ---------------------------------------------------------------------------
# Basic stats helpers
# ---------------------------------------------------------------------------


def zscore(xs: Sequence[float]) -> list[float]:
    n = len(xs)
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / n
    sd = math.sqrt(var) if var > 0 else 1.0
    return [(x - mean) / sd for x in xs]


def circular_shift(xs: Sequence[float], shift: int) -> list[float]:
    n = len(xs)
    shift = shift % n
    if shift == 0:
        return list(xs)
    return list(xs[-shift:]) + list(xs[:-shift])


# ---------------------------------------------------------------------------
# Metric 1: lagged cross-correlation
# ---------------------------------------------------------------------------


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Pearson correlation of two equal-length sequences, computed from
    their OWN local mean/variance (not a caller-supplied global
    z-score). This is the definition that guarantees |r| <= 1 for any
    slice — see `lagged_cross_correlation`'s docstring for why that
    matters."""
    n = len(xs)
    if n == 0:
        return 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    denom = math.sqrt(var_x * var_y)
    return cov / denom if denom > 0 else 0.0


def lagged_cross_correlation(
    a: Sequence[float], b: Sequence[float], max_lag: int
) -> dict[int, float]:
    """Pearson r between `a` and `b` at every integer lag in
    [-max_lag, +max_lag]. Positive lag means `b` is shifted later
    relative to `a` (b lags a).

    Each lag's correlation is computed from the OVERLAPPING sub-window's
    OWN local mean/variance via `_pearson`, not from a global z-score of
    the full series sliced afterward. Using a global z-score and then
    summing a slice of it (an earlier version of this function did
    exactly that) is only a good approximation when the overlap is a
    large fraction of the series -- at large |lag| relative to series
    length, the local mean/variance of a short, possibly non-
    representative slice can differ enough from the global values that
    the resulting quantity is no longer a true Pearson correlation and
    can exceed magnitude 1. Recomputing locally per lag guarantees
    |r| <= 1 always, at the cost of being O(max_lag * n) instead of
    O(max_lag + n); fine at the session lengths this tool targets.
    """
    if len(a) != len(b):
        raise ValueError("a and b must be the same length (resample both first)")
    n = len(a)
    out: dict[int, float] = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            xa, xb = (a[: n - lag] if lag else a), b[lag:]
        else:
            xa, xb = a[-lag:], b[: n + lag]
        m = min(len(xa), len(xb))
        if m < 2:
            out[lag] = 0.0
            continue
        out[lag] = _pearson(xa[:m], xb[:m])
    return out


def peak_abs_cross_correlation(a: Sequence[float], b: Sequence[float], max_lag: int) -> tuple[float, int]:
    xc = lagged_cross_correlation(a, b, max_lag)
    best_lag = max(xc, key=lambda k: abs(xc[k]))
    return xc[best_lag], best_lag


# ---------------------------------------------------------------------------
# Metric 2: cross-recurrence quantification (CRQA)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CRQAResult:
    recurrence_rate: float
    determinism: float
    eps: float
    n: int


def crqa(
    a: Sequence[float], b: Sequence[float], *, eps_percentile: float = 10.0, lmin: int = 2
) -> CRQAResult:
    """Cross-recurrence quantification between z-scored `a` and `b`.

    Recurrence threshold `eps` is chosen as the `eps_percentile`-th
    percentile of all pairwise |za[i]-zb[j]| distances (the "fixed
    recurrence rate" convention — keeps RR comparable across sessions
    with different absolute variability instead of using an arbitrary
    fixed threshold).

    O(n^2) time and space. Caller must keep `n <= MAX_RESAMPLED_LENGTH`.
    """
    if len(a) != len(b):
        raise ValueError("a and b must be the same length")
    n = len(a)
    if n > MAX_RESAMPLED_LENGTH:
        raise ValueError(
            f"resampled length {n} exceeds MAX_RESAMPLED_LENGTH="
            f"{MAX_RESAMPLED_LENGTH} (O(n^2) CRQA would be too slow in pure "
            f"Python) -- increase --dt to shrink the resampled series."
        )
    za, zb = zscore(a), zscore(b)
    dist = [[abs(za[i] - zb[j]) for j in range(n)] for i in range(n)]
    flat_sorted = sorted(x for row in dist for x in row)
    idx = max(0, min(len(flat_sorted) - 1, int(len(flat_sorted) * eps_percentile / 100.0)))
    eps = flat_sorted[idx]

    total_recur = 0
    diag_points_in_lines = 0
    for d in range(-(n - 1), n):
        run = 0
        i_lo, i_hi = max(0, d), min(n, n + d)
        for i in range(i_lo, i_hi):
            j = i - d
            if dist[i][j] <= eps:
                run += 1
                total_recur += 1
            else:
                if run >= lmin:
                    diag_points_in_lines += run
                run = 0
        if run >= lmin:
            diag_points_in_lines += run

    rr = total_recur / (n * n)
    det = diag_points_in_lines / total_recur if total_recur > 0 else 0.0
    return CRQAResult(recurrence_rate=rr, determinism=det, eps=eps, n=n)


# ---------------------------------------------------------------------------
# Surrogate significance testing (Theiler et al. 1992, circular shift)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SurrogateReport:
    statistic_name: str
    observed: float
    null_mean: float
    null_max: float
    p_value: float
    n_surrogates: int


def surrogate_test(
    a: Sequence[float],
    b: Sequence[float],
    *,
    statistic: str,
    max_lag: int = 10,
    n_surrogates: int = 200,
    seed: int = 1729,
) -> SurrogateReport:
    """Circular-shift surrogate test. Shifts `b` by a random circular
    offset (preserving b's own autocorrelation structure while
    destroying the true cross-subject alignment), recomputes the chosen
    statistic, and repeats `n_surrogates` times to build a null
    distribution. Empirical p-value uses add-one smoothing (standard
    for permutation/surrogate tests -- avoids a reported p=0.0 with
    finite surrogates).
    """
    if statistic == "xcorr":
        observed, _lag = peak_abs_cross_correlation(a, b, max_lag)
        stat_fn = lambda bb: abs(peak_abs_cross_correlation(a, bb, max_lag)[0])
    elif statistic == "det":
        observed = crqa(a, b).determinism
        stat_fn = lambda bb: crqa(a, bb).determinism
    else:
        raise ValueError("statistic must be 'xcorr' or 'det'")

    rng = random.Random(seed)
    n = len(b)
    null: list[float] = []
    for _ in range(n_surrogates):
        shift = rng.randrange(1, n)  # never 0 -- that would be the observed alignment
        null.append(stat_fn(circular_shift(b, shift)))

    n_ge = sum(1 for s in null if s >= observed)
    p_value = (n_ge + 1) / (len(null) + 1)

    return SurrogateReport(
        statistic_name=statistic,
        observed=observed,
        null_mean=sum(null) / len(null),
        null_max=max(null),
        p_value=p_value,
        n_surrogates=n_surrogates,
    )


# ---------------------------------------------------------------------------
# End-to-end analysis
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DyadicReport:
    n_samples: int
    dt: float
    xcorr_peak: float
    xcorr_peak_lag: int
    xcorr_surrogate: SurrogateReport
    crqa_result: CRQAResult
    det_surrogate: SurrogateReport


def analyze_dyadic(
    samples_a: Sequence[RRSample] | Sequence[ScalarSample],
    samples_b: Sequence[RRSample] | Sequence[ScalarSample],
    *,
    dt: float = 1.0,
    max_lag_s: float = 10.0,
    n_surrogates: int = 200,
    seed: int = 1729,
) -> DyadicReport:
    """Full pipeline: resample both subjects onto a shared grid spanning
    their overlapping in-range time window, then compute both synchrony
    metrics with surrogate significance."""
    a_ok = [s for s in samples_a if s.q == "ok"]
    b_ok = [s for s in samples_b if s.q == "ok"]
    if len(a_ok) < 2 or len(b_ok) < 2:
        raise ValueError("both subjects need >= 2 in-range RR samples")

    t_start = max(min(s.t for s in a_ok), min(s.t for s in b_ok))
    t_end = min(max(s.t for s in a_ok), max(s.t for s in b_ok))
    if t_end <= t_start:
        raise ValueError("subjects' RR streams do not overlap in time")

    a = resample_uniform(a_ok, t_start=t_start, t_end=t_end, dt=dt)
    b = resample_uniform(b_ok, t_start=t_start, t_end=t_end, dt=dt)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]

    if n > MAX_RESAMPLED_LENGTH:
        raise ValueError(
            f"overlap window resamples to {n} points at dt={dt}s, exceeding "
            f"MAX_RESAMPLED_LENGTH={MAX_RESAMPLED_LENGTH} -- pass a larger --dt."
        )

    max_lag = max(1, int(round(max_lag_s / dt)))
    xcorr_peak, xcorr_lag = peak_abs_cross_correlation(a, b, max_lag)
    xcorr_surr = surrogate_test(
        a, b, statistic="xcorr", max_lag=max_lag, n_surrogates=n_surrogates, seed=seed
    )
    crqa_res = crqa(a, b)
    det_surr = surrogate_test(
        a, b, statistic="det", max_lag=max_lag, n_surrogates=n_surrogates, seed=seed + 1
    )

    return DyadicReport(
        n_samples=n,
        dt=dt,
        xcorr_peak=xcorr_peak,
        xcorr_peak_lag=xcorr_lag,
        xcorr_surrogate=xcorr_surr,
        crqa_result=crqa_res,
        det_surrogate=det_surr,
    )


# ---------------------------------------------------------------------------
# Segment-aware analysis
# ---------------------------------------------------------------------------


def analyze_dyadic_by_segment(
    samples_a: Sequence[RRSample] | Sequence[ScalarSample],
    samples_b: Sequence[RRSample] | Sequence[ScalarSample],
    segments: Sequence[Segment],
    *,
    dt: float = 1.0,
    max_lag_s: float = 10.0,
    n_surrogates: int = 200,
    seed: int = 1729,
) -> dict[str, DyadicReport | str]:
    """Run `analyze_dyadic` independently within each named segment
    (e.g. baseline/paced/recovery from `analyze_g2.make_default_segments`,
    or any custom set). This is what makes "did synchrony rise
    specifically during the intervention window" askable — a single
    whole-session correlation number cannot distinguish a transient,
    intervention-locked effect from a stable trait-level correlation
    (which is far more likely to be a mundane confound: two people who
    are simply both calm, or both stressed, for the whole session).

    Returns a dict keyed by segment name. A segment with too little
    data (e.g. too few in-range samples, or the two subjects don't
    overlap within that window) maps to a short error string instead of
    a `DyadicReport`, rather than raising — so one bad segment doesn't
    prevent reporting on the others.
    """
    out: dict[str, DyadicReport | str] = {}
    for seg in segments:
        a_seg = [s for s in samples_a if s.q == "ok" and seg.contains(s)]
        b_seg = [s for s in samples_b if s.q == "ok" and seg.contains(s)]
        try:
            out[seg.name] = analyze_dyadic(
                a_seg, b_seg, dt=dt, max_lag_s=max_lag_s, n_surrogates=n_surrogates, seed=seed
            )
        except ValueError as exc:
            out[seg.name] = str(exc)
    return out


def segment_contrast(
    reports: dict[str, DyadicReport | str], name_a: str, name_b: str
) -> dict:
    """Descriptive contrast between two segments' synchrony metrics
    (e.g. `segment_contrast(reports, "paced", "baseline")`).

    IMPORTANT: the returned deltas are descriptive only. Each segment's
    OWN `p_value` (in its `xcorr_surrogate`/`det_surrogate`) is a
    rigorous surrogate-tested significance statement about that segment
    in isolation. The DIFFERENCE between two segments has NOT itself
    been surrogate-tested here — doing that properly needs a
    block-permutation scheme across the segment boundary (shuffle which
    contiguous blocks of time get the "paced" vs "baseline" label,
    preserving within-block structure), which is not yet implemented.
    Use this to describe the direction and size of a contrast, and use
    each segment's own p-value for the significance claim.
    """
    ra, rb = reports.get(name_a), reports.get(name_b)
    if not isinstance(ra, DyadicReport) or not isinstance(rb, DyadicReport):
        raise ValueError(
            f"both segments need a valid DyadicReport to contrast; "
            f"got {name_a}={type(ra).__name__}, {name_b}={type(rb).__name__}"
        )
    return {
        "segments": (name_a, name_b),
        "xcorr_peak_delta": ra.xcorr_peak - rb.xcorr_peak,
        "determinism_delta": ra.crqa_result.determinism - rb.crqa_result.determinism,
        f"{name_a}_p_values": {
            "xcorr": ra.xcorr_surrogate.p_value, "det": ra.det_surrogate.p_value,
        },
        f"{name_b}_p_values": {
            "xcorr": rb.xcorr_surrogate.p_value, "det": rb.det_surrogate.p_value,
        },
        "note": (
            "deltas are descriptive only -- not themselves surrogate-tested; "
            "see segment_contrast's docstring"
        ),
    }


def format_segmented_report(reports: dict[str, DyadicReport | str]) -> str:
    out = ["Dyadic Coherence Report — segmented", "=" * 60, ""]
    for name, r in reports.items():
        out.append(f"-- segment: {name} --")
        if isinstance(r, str):
            out.append(f"  (skipped: {r})")
            out.append("")
            continue
        out.append(
            f"  n_samples={r.n_samples} at dt={r.dt}s ({r.n_samples * r.dt:.0f}s window)"
        )
        out.append(
            f"  xcorr peak |r|={r.xcorr_peak:.4f} at lag {r.xcorr_peak_lag * r.dt:.1f}s, "
            f"p={r.xcorr_surrogate.p_value:.4f}"
        )
        out.append(
            f"  CRQA determinism={r.crqa_result.determinism:.4f}, "
            f"p={r.det_surrogate.p_value:.4f}"
        )
        sig = r.xcorr_surrogate.p_value < 0.05 or r.det_surrogate.p_value < 0.05
        out.append(f"  verdict: {'FLAGGED (p<0.05)' if sig else 'not significant'}")
        out.append("")
    out.append(
        "Compare segments by eye or via segment_contrast(); a rise specific to an "
        "intervention window is a stronger, less confound-prone finding than "
        "significance anywhere in the whole session (see module docstring)."
    )
    return "\n".join(out)


def segmented_report_to_json(reports: dict[str, DyadicReport | str]) -> dict:
    out: dict = {}
    for name, r in reports.items():
        if isinstance(r, str):
            out[name] = {"skipped": r}
        else:
            out[name] = report_to_json(r)
    return out


def format_report(r: DyadicReport) -> str:
    out = ["Dyadic Coherence Report", "=" * 60, ""]
    out.append(f"n_samples={r.n_samples} at dt={r.dt}s "
               f"({r.n_samples * r.dt:.0f}s overlap window)")
    out.append("")
    out.append(f"Lagged cross-correlation: peak |r| = {r.xcorr_peak:.4f} at lag {r.xcorr_peak_lag * r.dt:.1f}s")
    out.append(
        f"  surrogate test (circular shift, n={r.xcorr_surrogate.n_surrogates}): "
        f"null mean={r.xcorr_surrogate.null_mean:.4f}, "
        f"null max={r.xcorr_surrogate.null_max:.4f}, "
        f"p={r.xcorr_surrogate.p_value:.4f}"
    )
    out.append("")
    out.append(
        f"CRQA: recurrence_rate={r.crqa_result.recurrence_rate:.4f}, "
        f"determinism={r.crqa_result.determinism:.4f} (eps={r.crqa_result.eps:.4f})"
    )
    out.append(
        f"  surrogate test (circular shift, n={r.det_surrogate.n_surrogates}): "
        f"null mean={r.det_surrogate.null_mean:.4f}, "
        f"null max={r.det_surrogate.null_max:.4f}, "
        f"p={r.det_surrogate.p_value:.4f}"
    )
    out.append("")
    sig = r.xcorr_surrogate.p_value < 0.05 or r.det_surrogate.p_value < 0.05
    out.append(
        f"VERDICT: {'anomalous synchrony flagged (p<0.05 on at least one metric)' if sig else 'no synchrony beyond chance detected'}"
    )
    out.append(
        "  This is a statistical statement about correlation, not a psi claim. "
        "Before any psi-adjacent interpretation: rule out shared paced-breathing "
        "cues, shared ambient audio, room-temperature covariation, and capture-"
        "device clock skew (see docs/falsification.md Sham Control requirements)."
    )
    return "\n".join(out)


def report_to_json(r: DyadicReport) -> dict:
    return {
        "n_samples": r.n_samples,
        "dt": r.dt,
        "xcorr_peak": r.xcorr_peak,
        "xcorr_peak_lag_s": r.xcorr_peak_lag * r.dt,
        "xcorr_surrogate": {
            "observed": r.xcorr_surrogate.observed,
            "null_mean": r.xcorr_surrogate.null_mean,
            "null_max": r.xcorr_surrogate.null_max,
            "p_value": r.xcorr_surrogate.p_value,
            "n_surrogates": r.xcorr_surrogate.n_surrogates,
        },
        "crqa": {
            "recurrence_rate": r.crqa_result.recurrence_rate,
            "determinism": r.crqa_result.determinism,
            "eps": r.crqa_result.eps,
        },
        "det_surrogate": {
            "observed": r.det_surrogate.observed,
            "null_mean": r.det_surrogate.null_mean,
            "null_max": r.det_surrogate.null_max,
            "p_value": r.det_surrogate.p_value,
            "n_surrogates": r.det_surrogate.n_surrogates,
        },
        "significant": r.xcorr_surrogate.p_value < 0.05 or r.det_surrogate.p_value < 0.05,
    }


# ---------------------------------------------------------------------------
# Self-test fixture generator
# ---------------------------------------------------------------------------


def synth_dyad(
    *,
    seed: int = 1729,
    n_beats: int = 600,
    mean_rr_ms: float = 900.0,
    shared_sigma_ms: float = 60.0,
    independent_sigma_ms: float = 8.0,
    smoothing_window: int = 15,
    correlated: bool = True,
) -> tuple[list[RRSample], list[RRSample]]:
    """Generate two synthetic RR streams.

    If `correlated`, both share a common latent APERIODIC slow-drift
    component (a smoothed random walk, simulating e.g. a shared slow
    autonomic drift) plus independent noise. This should trigger the
    surrogate test. The shared component is deliberately built as
    smoothed *noise*, not a periodic signal (e.g. not a fixed-frequency
    sine) — a periodic shared component is exactly the case where
    circular-shift surrogates lose power, since shifting a periodic
    signal by multiples related to its own period leaves it correlated
    with the original at many shifts, not just shift zero. Using an
    aperiodic shared drift makes this a fair validation of the method.

    If not `correlated`, both subjects are pure independent noise —
    this should NOT trigger the surrogate test (beyond the nominal
    alpha false-positive rate).
    """
    rng = random.Random(seed)
    times: list[float] = []
    t = 0.0
    for _ in range(n_beats):
        t += mean_rr_ms / 1000.0
        times.append(t)

    if correlated:
        raw = [rng.gauss(0.0, 1.0) for _ in times]
        smoothed = []
        for i in range(len(raw)):
            lo = max(0, i - smoothing_window)
            window = raw[lo : i + 1]
            smoothed.append(sum(window) / len(window))
        peak = max(abs(x) for x in smoothed) or 1.0
        shared_drift = [shared_sigma_ms * x / peak for x in smoothed]
    else:
        shared_drift = [0.0] * len(times)

    def _make(offset_seed: int) -> list[RRSample]:
        r = random.Random(seed + offset_seed)
        out = []
        for i, t in enumerate(times):
            rr = mean_rr_ms + shared_drift[i] + r.gauss(0.0, independent_sigma_ms)
            out.append(RRSample(t=t, rr_ms=max(400.0, min(1600.0, rr)), q="ok"))
        return out

    return _make(1), _make(2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="analyze_dyadic_coherence.py",
        description="Cross-subject RR-interval synchrony analysis with surrogate significance testing.",
    )
    p.add_argument("--a", help="NDJSON capture for subject A.")
    p.add_argument("--a-channel", default="ppg-rr")
    p.add_argument("--a-kind", choices=["rr", "scalar"], default="rr",
                    help="'rr' uses the RR-interval loader (drops the first-peak sentinel); "
                         "'scalar' uses the generic loader (GSR, temperature, ...).")
    p.add_argument("--b", help="NDJSON capture for subject B.")
    p.add_argument("--b-channel", default="ppg-rr")
    p.add_argument("--b-kind", choices=["rr", "scalar"], default="rr")
    p.add_argument("--dt", type=float, default=1.0, help="Resample interval, seconds (default 1.0).")
    p.add_argument("--max-lag-s", type=float, default=10.0, help="Max cross-correlation lag, seconds.")
    p.add_argument("--n-surrogates", type=int, default=200)
    p.add_argument("--seed", type=int, default=1729)
    p.add_argument("--json", action="store_true")
    p.add_argument("--self-test", choices=["correlated", "independent"], default=None,
                    help="Run on a synthetic dyad instead of real files.")
    p.add_argument("--segmented", action="store_true",
                    help="Analyze the default 5/5/5 baseline/paced/recovery segments "
                         "independently instead of the whole overlap window.")
    p.add_argument("--t0", type=float, default=0.0, help="Segment-mode: session-time (s) baseline begins.")
    p.add_argument("--baseline-s", type=float, default=300.0)
    p.add_argument("--paced-s", type=float, default=300.0)
    p.add_argument("--recovery-s", type=float, default=300.0)
    args = p.parse_args(argv)

    def _load(path: str, channel: str, kind: str) -> list[RRSample] | list[ScalarSample]:
        if kind == "scalar":
            return load_scalar_channel_from_ndjson(path, channel=channel)
        return load_rr_from_ndjson(path, channel=channel)

    if args.self_test:
        a, b = synth_dyad(correlated=(args.self_test == "correlated"))
    else:
        if args.a is None or args.b is None:
            print("analyze_dyadic_coherence: --a and --b are required (or use --self-test).",
                  file=sys.stderr)
            return 3
        try:
            a = _load(args.a, args.a_channel, args.a_kind)
            b = _load(args.b, args.b_channel, args.b_kind)
        except FileNotFoundError as exc:
            print(f"analyze_dyadic_coherence: file not found: {exc.filename}", file=sys.stderr)
            return 2

    if args.segmented:
        segments = make_default_segments(
            args.t0, baseline_s=args.baseline_s, paced_s=args.paced_s, recovery_s=args.recovery_s
        )
        reports = analyze_dyadic_by_segment(
            a, b, segments, dt=args.dt, max_lag_s=args.max_lag_s,
            n_surrogates=args.n_surrogates, seed=args.seed,
        )
        if args.json:
            print(json.dumps(segmented_report_to_json(reports), indent=2, sort_keys=True))
        else:
            print(format_segmented_report(reports))
        return 0

    try:
        report = analyze_dyadic(
            a, b, dt=args.dt, max_lag_s=args.max_lag_s,
            n_surrogates=args.n_surrogates, seed=args.seed,
        )
    except ValueError as exc:
        print(f"analyze_dyadic_coherence: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report_to_json(report), indent=2, sort_keys=True))
    else:
        print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
