#!/usr/bin/env python3
"""
analyze_combat_session.py — Track M host-side reference for the combat trim's sensing.

Spec: docs/plans/2026-tier1-launch/track-M-combat-trim.md §3 (channel map, fusion and quality), §6 (modes), §7 (M-F2..M-F5).

Reads a Mk0.5-style NDJSON capture (one {"t","ch","v","q"} object per line, firmware/mk0.5/docs/SCHEMA.md) from a sparring
session and produces the per-round summary the plan asks for, using only channels the combat trim can carry without adhesive
electrodes:

    ppg-rr            per-beat RR (ms) from the forehead pad PPG           -> coarse in-round HR, between-round RMSSD
    ecg-rr / oracle   optional second RR source (Polar H10 on the bench)   -> HR agreement rule
    temp-nose         MLX90614 object temperature aimed at the nose tip    -> breathing rate (M-F2), arousal slope
    temp-forehead     the Mk0.5 thermopile channel, accepted as a fallback for temp-nose
    eda-forehead/gsr  GSR module through the forehead fabric patches       -> skin-conductance response rate (M-F3)
    temp-skin.L/R     MAX30205 in the pads                                 -> the sweat rule for EDA
    still             1 Hz flag from the IMU (1 = still), when the IMU exists
    impact            IMU impact events (v = peak g)
    cue               string events: session-start/-end, round-start/-end, tally, prime

Rules implemented (plan §3.2): every derived value carries a quality flag; heart rate is reported only when two RR sources agree
within 5 bpm or the single source is high quality (≥ 80 % in-range beats in the window); HRV (RMSSD) is computed only inside
still windows of ≥ 60 s and never in-round; without an IMU the between-round rest is *assumed* still and the report says so;
breathing rate comes from the thermal channel; EDA responses are not counted while the skin temperature is rising faster than
the sweat threshold. The mode state machine of §6 (M-F5) lives in `CombatModes` for the firmware port to mirror.

This is a reporter and a reference implementation, standard library only. No hardware is required; the tests synthesise a
session. Firmware ports follow the r_peak.cpp / rr_replay.py pattern: the Python here is the behavioural spec.

Usage:
    tools/analyze_combat_session.py capture.ndjson [--rounds 3 --round-s 180 --rest-s 60] [--json]
    tools/analyze_combat_session.py capture.ndjson --thermal-channel temp-forehead --eda-channel gsr

Exit codes: 0 analysed, 1 file/parse error, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_g2 as G2  # noqa: E402  (RRSample, Segment, compute_segment_metrics: the ratified RMSSD math)

# ---------------------------------------------------------------------------
# Constants (plan §3.2 and §6)
# ---------------------------------------------------------------------------

HR_WINDOW_S = 10.0             # coarse HR window
HR_MIN_BEATS = 5               # beats needed in a window
HR_QUALITY_MIN_OK = 0.80       # in-range fraction for "high quality"
HR_AGREE_BPM = 5.0             # two-source agreement
HRV_MIN_STILL_S = 60.0         # RMSSD only in still windows at least this long
RECOVERY_FIT_S = 60.0          # HR recovery slope over the first minute of rest

RESP_BAND_HZ = (0.1, 1.0)      # thermal respiration band
RESP_REFRACTORY_S = 1.0        # ≥ 1 s between breaths (≤ 60 breaths/min)
RESP_WINDOW_S = 30.0           # breathing-rate window
RESP_MIN_PEAK_C = 0.01         # absolute floor on the peak threshold (°C)
AROUSAL_WINDOW_S = 60.0        # nose-tip slope window

EDA_TONIC_TAU_S = 5.0          # high-pass time constant for the phasic component
EDA_SCR_MIN_RISE_S = 0.5       # skin-conductance response rise-time window
EDA_SCR_MAX_RISE_S = 3.0
EDA_SCR_REL_THRESHOLD = 0.005  # SCR amplitude as a fraction of the tonic level (raw units are calibrated downstream)
SWEAT_SLOPE_C_PER_MIN = 0.05   # skin temperature rising faster than this = thermal sweating, EDA not counted

STILL_MIN_FRACTION = 0.9       # a rest window counts as still when ≥ 90 % of its `still` flags are 1

CUE_SESSION_START, CUE_SESSION_END = "session-start", "session-end"
CUE_ROUND_START, CUE_ROUND_END = "round-start", "round-end"
CUE_TALLY, CUE_PRIME, CUE_SANCTUARY = "tally", "prime", "sanctuary"

THERMAL_CHANNELS = ("temp-nose", "temp-forehead")
EDA_CHANNELS = ("eda-forehead", "gsr")
SKIN_TEMP_CHANNELS = ("temp-skin.L", "temp-skin.R", "temp-forehead")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Sample:
    t: float
    v: float
    q: str = "ok"


@dataclass(frozen=True)
class Event:
    t: float
    v: str


@dataclass(frozen=True)
class Window:
    """A [t_start, t_end) span in session time."""
    name: str
    t_start: float
    t_end: float

    @property
    def length_s(self) -> float:
        return self.t_end - self.t_start

    def contains(self, t: float) -> bool:
        return self.t_start <= t < self.t_end


@dataclass
class Capture:
    numeric: dict[str, list[Sample]] = field(default_factory=dict)
    cues: list[Event] = field(default_factory=list)
    t_min: float | None = None
    t_max: float | None = None
    n_lines: int = 0
    n_bad: int = 0            # malformed or non-numeric sample lines skipped
    n_meta: int = 0           # hello / smoke / boot / health / error lines (kind, no ch)
    n_dup: int = 0            # exact duplicate sample lines dropped
    boots: list[str] = field(default_factory=list)   # boot ids in order of first appearance
    seq_lost: int = 0         # lines the firmware numbered (`n`) but the capture never received
    fw_drops: int = 0         # lines the firmware itself reported dropping (`hb` drops, per boot max, summed)
    time_base: str = "boot"   # "wallclock" (t_wallclock on every line) | "boot" | "stitched" (several boots re-based, gaps unknown)

    def channel(self, *names: str) -> tuple[str | None, list[Sample]]:
        """First present channel of `names` (in order) and its samples."""
        for n in names:
            if n in self.numeric and self.numeric[n]:
                return n, self.numeric[n]
        return None, []


@dataclass
class HRPoint:
    t: float                # window centre
    hr_bpm: float | None
    quality: str            # "ok" | "low" | "gap" | "disagree"
    sources: int


@dataclass
class RoundSummary:
    index: int
    t_start: float
    t_end: float
    hr_mean_bpm: float | None
    hr_peak_bpm: float | None
    hr_windows_reported: int
    hr_windows_total: int
    breaths_per_min: float | None
    scr_per_min: float | None
    eda_quality: str
    impacts: int
    impact_peak_g: float | None
    notes: list[str] = field(default_factory=list)


@dataclass
class RestSummary:
    index: int                 # rest after round `index`
    t_start: float
    t_end: float
    still_source: str          # "imu" | "assumed (no IMU)" | "not still"
    rmssd_ms: float | None
    n_beats: int
    hr_recovery_bpm_per_min: float | None
    nose_slope_c_per_min: float | None
    breaths_per_min: float | None
    notes: list[str] = field(default_factory=list)


@dataclass
class SessionReport:
    path: str
    duration_s: float
    channels: dict[str, int]
    thermal_channel: str | None
    eda_channel: str | None
    rr_channels: list[str]
    still_source: str
    rounds: list[RoundSummary] = field(default_factory=list)
    rests: list[RestSummary] = field(default_factory=list)
    tallies: int = 0
    impacts_total: int = 0
    impact_exposure_g: float = 0.0
    notes: list[str] = field(default_factory=list)
    capabilities: dict[str, str] = field(default_factory=dict)   # Track N: each capability is "ok" or says why not
    integrity: dict[str, object] = field(default_factory=dict)   # lines / skipped / meta / duplicates / lost / firmware_drops / boots / time_base


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _finite(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def load_capture(path: str | Path) -> Capture:
    """Read an NDJSON capture without ever raising on its content (Track N, N-H2).

    Malformed lines are counted and skipped. Meta lines (hello / smoke / boot / health) are counted, and boot ids are
    collected from them and from every sample's `boot` field. Exact duplicate samples are dropped. `n` sequence gaps and
    the heartbeat's `drops` counter are turned into a lost-line count. When the capture spans several boots and carries
    no `t_wallclock`, each boot's `t` is re-based to start one second after the previous boot's last sample (the true gap
    is unknown; the report says so). `t_wallclock` (added by the Pi log-sink, SCHEMA §3) is preferred over `t` when
    present on every sample line.
    """
    cap = Capture()
    raw_rows: list[tuple[str, float, str, object, str]] = []   # (boot, t, ch, v, q)
    seen: set[tuple] = set()
    last_seq: dict[str, int] = {}
    hb_drops: dict[str, int] = {}
    n_wall = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            cap.n_lines += 1
            try:
                rec = json.loads(raw)
            except (json.JSONDecodeError, RecursionError, ValueError):
                cap.n_bad += 1
                continue
            if not isinstance(rec, dict):
                cap.n_bad += 1
                continue
            boot = rec.get("boot")
            boot = boot if isinstance(boot, str) and boot else ""
            if boot and boot not in cap.boots:
                cap.boots.append(boot)
            n = rec.get("n")
            if isinstance(n, int) and not isinstance(n, bool):
                prev = last_seq.get(boot)
                if prev is not None and n > prev + 1:
                    cap.seq_lost += n - prev - 1
                if prev is None or n > prev:
                    last_seq[boot] = n
            if "ch" not in rec:
                cap.n_meta += 1 if "kind" in rec else 0
                if "kind" not in rec:
                    cap.n_bad += 1
                continue
            ch, v = rec.get("ch"), rec.get("v")
            if not isinstance(ch, str) or not ch:
                cap.n_bad += 1
                continue
            tw = rec.get("t_wallclock")
            if _finite(tw):
                t = float(tw)
                n_wall += 1
            elif _finite(rec.get("t")):
                t = float(rec["t"])
            else:
                cap.n_bad += 1
                continue
            q = rec.get("q", "ok")
            q = q if isinstance(q, str) else "ok"
            if ch == "hb":
                d = rec.get("drops")
                if _finite(d):
                    hb_drops[boot] = max(hb_drops.get(boot, 0), int(d))
            if ch == "cue" and isinstance(v, str):
                key = (boot, t, ch, v, q)
            elif _finite(v):
                v = float(v)
                key = (boot, t, ch, v, q)
            else:
                cap.n_bad += 1
                continue
            if key in seen:
                cap.n_dup += 1
                continue
            seen.add(key)
            raw_rows.append(key)
    cap.fw_drops = sum(hb_drops.values())

    # time base: wall-clock on every sample line, or per-boot re-basing when the file spans boots
    if raw_rows and n_wall == len(raw_rows):
        cap.time_base = "wallclock"
        offsets: dict[str, float] = {}
    else:
        boots_in_rows: list[str] = []
        for b, *_ in raw_rows:
            if b not in boots_in_rows:
                boots_in_rows.append(b)
        offsets = {}
        if len(boots_in_rows) > 1:
            cap.time_base = "stitched"
            prev_end: float | None = None
            for b in boots_in_rows:
                ts = [r[1] for r in raw_rows if r[0] == b]
                off = 0.0 if prev_end is None else prev_end + 1.0 - min(ts)
                offsets[b] = off
                prev_end = max(ts) + off
    for boot, t, ch, v, q in raw_rows:
        t += offsets.get(boot, 0.0)
        cap.t_min = t if cap.t_min is None else min(cap.t_min, t)
        cap.t_max = t if cap.t_max is None else max(cap.t_max, t)
        if ch == "cue":
            cap.cues.append(Event(t, v))            # type: ignore[arg-type]
        else:
            cap.numeric.setdefault(ch, []).append(Sample(t, v, q))   # type: ignore[arg-type]
    for ch in cap.numeric:
        cap.numeric[ch].sort(key=lambda s: s.t)
    cap.cues.sort(key=lambda e: e.t)
    return cap


# ---------------------------------------------------------------------------
# Rounds and rest windows
# ---------------------------------------------------------------------------


def rounds_from_cues(cues: Sequence[Event]) -> list[Window]:
    rounds: list[Window] = []
    start: float | None = None
    for e in cues:
        if e.v == CUE_ROUND_START:
            start = e.t
        elif e.v == CUE_ROUND_END and start is not None:
            rounds.append(Window(f"round{len(rounds) + 1}", start, e.t))
            start = None
    return rounds


def synth_rounds(t0: float, n: int, round_s: float, rest_s: float) -> list[Window]:
    """Rounds laid out from t0 when the capture has no round cues (gym-timer schedule)."""
    return [Window(f"round{i + 1}", t0 + i * (round_s + rest_s), t0 + i * (round_s + rest_s) + round_s) for i in range(n)]


def rest_windows(rounds: Sequence[Window], t_end: float) -> list[Window]:
    """The gap after each round, up to the next round or the end of the capture."""
    out = []
    for i, r in enumerate(rounds):
        stop = rounds[i + 1].t_start if i + 1 < len(rounds) else t_end
        if stop > r.t_end:
            out.append(Window(f"rest{i + 1}", r.t_end, stop))
    return out


# ---------------------------------------------------------------------------
# Small signal helpers (time-based, irregular sampling tolerated)
# ---------------------------------------------------------------------------


def ema_highpass(samples: Sequence[Sample], tau_s: float) -> list[Sample]:
    """x - EMA(x) with time constant tau: removes the slow (tonic) part."""
    out: list[Sample] = []
    m: float | None = None
    t_prev: float | None = None
    for s in samples:
        if m is None:
            m = s.v
        else:
            dt = max(s.t - (t_prev or s.t), 1e-6)
            a = dt / (tau_s + dt)
            m += a * (s.v - m)
        t_prev = s.t
        out.append(Sample(s.t, s.v - m, s.q))
    return out


def ema_lowpass(samples: Sequence[Sample], tau_s: float) -> list[Sample]:
    out: list[Sample] = []
    m: float | None = None
    t_prev: float | None = None
    for s in samples:
        if m is None:
            m = s.v
        else:
            dt = max(s.t - (t_prev or s.t), 1e-6)
            a = dt / (tau_s + dt)
            m += a * (s.v - m)
        t_prev = s.t
        out.append(Sample(s.t, m, s.q))
    return out


def bandpass(samples: Sequence[Sample], f_lo: float, f_hi: float) -> list[Sample]:
    tau_lo = 1.0 / (2 * math.pi * f_lo)
    tau_hi = 1.0 / (2 * math.pi * f_hi)
    return ema_highpass(ema_lowpass(samples, tau_hi), tau_lo)


def linear_slope(samples: Sequence[Sample]) -> float | None:
    """Least-squares slope in units per second; None with < 3 points or no time spread."""
    pts = [(s.t, s.v) for s in samples if s.q == "ok"]
    if len(pts) < 3:
        return None
    n = len(pts)
    mt = sum(p[0] for p in pts) / n
    mv = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mt) ** 2 for p in pts)
    if sxx <= 0:
        return None
    return sum((p[0] - mt) * (p[1] - mv) for p in pts) / sxx


def in_window(samples: Iterable[Sample], w: Window) -> list[Sample]:
    return [s for s in samples if w.contains(s.t)]


# ---------------------------------------------------------------------------
# M-F2: thermal respiration and the arousal slope
# ---------------------------------------------------------------------------


def breath_times(thermal: Sequence[Sample]) -> list[float]:
    """Breath instants from the band-passed nose-tip temperature: local maxima above an adaptive threshold, refractory 1 s."""
    ok = [s for s in thermal if s.q == "ok"]
    if len(ok) < 8:
        return []
    y = bandpass(ok, *RESP_BAND_HZ)
    times: list[float] = []
    last = -1e9
    for i in range(1, len(y) - 1):
        # adaptive threshold: a fraction of the recent spread, floored
        lo = max(0, i - 80)
        recent = [abs(s.v) for s in y[lo:i + 1]]
        thr = max(RESP_MIN_PEAK_C, 0.3 * (statistics.pstdev(recent) if len(recent) > 2 else 0.0) * math.sqrt(2.0))
        if y[i].v > thr and y[i].v > y[i - 1].v and y[i].v >= y[i + 1].v and (y[i].t - last) >= RESP_REFRACTORY_S:
            times.append(y[i].t)
            last = y[i].t
    return times


def breaths_per_min(times: Sequence[float], w: Window) -> float | None:
    inside = [t for t in times if w.contains(t)]
    if len(inside) < 2:
        return None
    span = inside[-1] - inside[0]
    if span <= 0:
        return None
    return 60.0 * (len(inside) - 1) / span


def nose_slope_c_per_min(thermal: Sequence[Sample], w: Window) -> float | None:
    s = linear_slope(in_window(thermal, w))
    return None if s is None else 60.0 * s


# ---------------------------------------------------------------------------
# M-F3: forehead EDA response rate with the sweat rule
# ---------------------------------------------------------------------------


def scr_times(eda: Sequence[Sample]) -> list[float]:
    """Skin-conductance responses: phasic rises of ≥ EDA_SCR_REL_THRESHOLD × tonic within 0.5..3 s, one per rise."""
    ok = [s for s in eda if s.q == "ok"]
    if len(ok) < 10:
        return []
    tonic = ema_lowpass(ok, EDA_TONIC_TAU_S)
    phasic = [Sample(s.t, s.v - m.v, s.q) for s, m in zip(ok, tonic)]
    out: list[float] = []
    i = 0
    n = len(phasic)
    while i < n - 1:
        # find a trough followed by a rise
        if phasic[i + 1].v > phasic[i].v:
            j = i
            while j + 1 < n and phasic[j + 1].v >= phasic[j].v:
                j += 1
            rise = phasic[j].v - phasic[i].v
            dt = phasic[j].t - phasic[i].t
            level = max(abs(tonic[i].v), 1e-9)
            if EDA_SCR_MIN_RISE_S <= dt <= EDA_SCR_MAX_RISE_S and rise >= EDA_SCR_REL_THRESHOLD * level:
                out.append(phasic[j].t)
            i = max(j, i + 1)
        else:
            i += 1
    return out


def sweat_flag(skin: Sequence[Sample], w: Window) -> bool:
    s = linear_slope(in_window(skin, w))
    return s is not None and 60.0 * s > SWEAT_SLOPE_C_PER_MIN


def scr_per_min(times: Sequence[float], w: Window) -> float | None:
    if w.length_s <= 0:
        return None
    return 60.0 * sum(1 for t in times if w.contains(t)) / w.length_s


# ---------------------------------------------------------------------------
# M-F4: heart rate fusion, stillness and HRV gating
# ---------------------------------------------------------------------------


def rr_to_g2(samples: Sequence[Sample]) -> list[G2.RRSample]:
    return [G2.RRSample(t=s.t, rr_ms=s.v, q=s.q) for s in samples if s.v > 0]


def hr_windows(rr: Sequence[Sample], w: Window, window_s: float = HR_WINDOW_S) -> list[tuple[float, float | None, str]]:
    """(centre t, HR bpm, quality) per window across w. HR = 60000 / median in-range RR; quality 'ok' needs ≥ 5 beats and ≥ 80 % in range."""
    out = []
    t = w.t_start
    while t < w.t_end:
        win = Window("hr", t, min(t + window_s, w.t_end))
        beats = in_window(rr, win)
        ok = [b.v for b in beats if b.q == "ok" and b.v > 0]
        if len(ok) >= HR_MIN_BEATS:
            hr = 60000.0 / statistics.median(ok)
            q = "ok" if len(ok) / max(len(beats), 1) >= HR_QUALITY_MIN_OK else "low"
        else:
            hr, q = None, "gap"
        out.append(((win.t_start + win.t_end) / 2, hr, q))
        t += window_s
    return out


def fuse_hr(per_source: dict[str, list[tuple[float, float | None, str]]]) -> list[HRPoint]:
    """Plan §3.2: report HR when ≥ 2 sources agree within 5 bpm, or one source is high quality."""
    if not per_source:
        return []
    names = list(per_source)
    n_win = min(len(per_source[n]) for n in names)
    out: list[HRPoint] = []
    for i in range(n_win):
        t = per_source[names[0]][i][0]
        vals = [(per_source[n][i][1], per_source[n][i][2]) for n in names]
        present = [(v, q) for v, q in vals if v is not None]
        if len(present) >= 2:
            hrs = [v for v, _ in present]
            if max(hrs) - min(hrs) <= HR_AGREE_BPM:
                out.append(HRPoint(t, sum(hrs) / len(hrs), "ok", len(present)))
            else:
                good = [v for v, q in present if q == "ok"]
                if len(good) == 1:
                    out.append(HRPoint(t, good[0], "ok", 1))
                else:
                    out.append(HRPoint(t, None, "disagree", len(present)))
        elif len(present) == 1 and present[0][1] == "ok":
            out.append(HRPoint(t, present[0][0], "ok", 1))
        elif len(present) == 1:
            out.append(HRPoint(t, None, "low", 1))
        else:
            out.append(HRPoint(t, None, "gap", 0))
    return out


def still_fraction(still: Sequence[Sample], w: Window) -> float | None:
    flags = [s.v for s in in_window(still, w) if s.q == "ok"]
    if not flags:
        return None
    return sum(1 for f in flags if f >= 0.5) / len(flags)


def rmssd_in_window(rr: Sequence[Sample], w: Window) -> tuple[float | None, int]:
    m = G2.compute_segment_metrics(rr_to_g2(rr), G2.Segment(w.name, w.t_start, w.t_end))
    return m.rmssd_ms, m.n_beats


def recovery_slope(points: Sequence[HRPoint], w: Window, fit_s: float = RECOVERY_FIT_S) -> float | None:
    """HR slope (bpm per minute) over the first `fit_s` of the rest window; negative = recovering."""
    fit = Window("fit", w.t_start, min(w.t_start + fit_s, w.t_end))
    pts = [Sample(p.t, p.hr_bpm) for p in points if p.hr_bpm is not None and fit.contains(p.t)]
    s = linear_slope(pts)
    return None if s is None else 60.0 * s


# ---------------------------------------------------------------------------
# Session analysis
# ---------------------------------------------------------------------------


def analyze(path: str | Path, *, rounds: int | None = None, round_s: float = 180.0, rest_s: float = 60.0,
            thermal_channel: str | None = None, eda_channel: str | None = None) -> SessionReport:
    cap = load_capture(path)
    t0 = cap.t_min if cap.t_min is not None else 0.0
    t1 = cap.t_max if cap.t_max is not None else 0.0
    rep = SessionReport(path=str(path), duration_s=t1 - t0, channels={k: len(v) for k, v in cap.numeric.items()},
                        thermal_channel=None, eda_channel=None, rr_channels=[], still_source="")
    rep.integrity = {"lines": cap.n_lines, "skipped": cap.n_bad, "meta": cap.n_meta, "duplicates": cap.n_dup,
                     "lost": cap.seq_lost, "firmware_drops": cap.fw_drops, "boots": len(cap.boots), "time_base": cap.time_base}
    if cap.n_bad:
        rep.notes.append(f"{cap.n_bad} unparseable or non-numeric sample lines skipped")
    if cap.n_dup:
        rep.notes.append(f"{cap.n_dup} duplicate sample lines dropped")
    if cap.time_base == "stitched":
        rep.notes.append(f"{len(cap.boots)} boots re-based end to end (the real gaps are unknown without t_wallclock)")
    if cap.seq_lost or cap.fw_drops:
        rep.notes.append(f"{cap.seq_lost} lines missing from the sequence; the firmware reported dropping {cap.fw_drops}")

    # rounds
    rnds = rounds_from_cues(cap.cues)
    if not rnds:
        start = next((e.t for e in cap.cues if e.v == CUE_SESSION_START), t0)
        n = rounds if rounds else max(1, int((t1 - start) // (round_s + rest_s)) or 1)
        rnds = synth_rounds(start, n, round_s, rest_s)
        rep.notes.append(f"no round cues: {n} round(s) of {round_s:.0f} s with {rest_s:.0f} s rest laid out from t={start:.1f}")
    rests = rest_windows(rnds, t1)

    # channels
    th_name, thermal = cap.channel(*(([thermal_channel] if thermal_channel else []) + list(THERMAL_CHANNELS)))
    eda_name, eda = cap.channel(*(([eda_channel] if eda_channel else []) + list(EDA_CHANNELS)))
    skin_name, skin = cap.channel(*SKIN_TEMP_CHANNELS)
    still_name, still = cap.channel("still")
    _, impacts = cap.channel("impact")
    rr_sources = {n: cap.numeric[n] for n in ("ppg-rr", "ecg-rr", "oracle-rr", "bcg-rr") if n in cap.numeric}
    rep.thermal_channel, rep.eda_channel, rep.rr_channels = th_name, eda_name, list(rr_sources)
    rep.still_source = "imu" if still_name else "assumed (no IMU)"
    if not rr_sources:
        rep.notes.append("no RR channel: heart rate and HRV not available")
    if th_name is None:
        rep.notes.append("no thermal channel: breathing rate and arousal slope not available")
    if th_name == "temp-forehead":
        rep.notes.append("thermal channel is temp-forehead (Mk0.5 wiring): breathing needs the thermopile on the nose tip")
    if eda_name is None:
        rep.notes.append("no EDA channel")
    if not still_name:
        rep.notes.append("no IMU `still` channel: between-round rest is ASSUMED still; RMSSD values are provisional")

    rep.capabilities = {
        "hr": f"ok ({', '.join(rr_sources)})" if rr_sources else "unavailable: no RR channel",
        "hrv": ("unavailable: no RR channel" if not rr_sources else
                ("provisional: no IMU, rest assumed still" if not still_name else "ok")),
        "breathing": ("unavailable: no thermal channel" if th_name is None else
                      ("degraded: thermopile on the forehead, not the nose" if th_name == "temp-forehead" else "ok")),
        "eda": ("unavailable: no EDA channel" if eda_name is None else
                ("unchecked: no skin temperature for the sweat rule" if not skin else "ok")),
        "impacts": "ok" if impacts else "unavailable: no IMU impact channel",
        "stillness": "ok (imu)" if still_name else "unavailable: no IMU",
        "link": ("ok" if not (cap.seq_lost or cap.fw_drops) else
                 f"{cap.seq_lost} lines lost ({cap.fw_drops} reported dropped by the firmware)"),
    }

    breaths = breath_times(thermal) if thermal else []
    scrs = scr_times(eda) if eda else []
    rep.tallies = sum(1 for e in cap.cues if e.v == CUE_TALLY)
    rep.impacts_total = len(impacts)
    rep.impact_exposure_g = sum(s.v for s in impacts)

    # per-round
    for i, r in enumerate(rnds):
        per_source = {n: hr_windows(rr, r) for n, rr in rr_sources.items()}
        fused = fuse_hr(per_source)
        hrs = [p.hr_bpm for p in fused if p.hr_bpm is not None]
        sweat = sweat_flag(skin, r) if skin else False
        eda_q = "none" if eda_name is None else ("sweat" if sweat else ("ok" if skin else "unchecked (no skin temperature)"))
        imp = in_window(impacts, r)
        rs = RoundSummary(index=i + 1, t_start=r.t_start, t_end=r.t_end,
                          hr_mean_bpm=(sum(hrs) / len(hrs)) if hrs else None, hr_peak_bpm=max(hrs) if hrs else None,
                          hr_windows_reported=len(hrs), hr_windows_total=len(fused),
                          breaths_per_min=breaths_per_min(breaths, r) if breaths else None,
                          scr_per_min=None if (eda_name is None or sweat) else scr_per_min(scrs, r),
                          eda_quality=eda_q, impacts=len(imp), impact_peak_g=max((s.v for s in imp), default=None))
        if fused and len(hrs) < 0.5 * len(fused):
            rs.notes.append("HR reported in under half of the windows (motion / perfusion): in-round HR is coarse by design")
        rep.rounds.append(rs)
    n_sweat = sum(1 for r in rep.rounds if r.eda_quality == "sweat")
    if n_sweat and rep.capabilities.get("eda") == "ok":
        rep.capabilities["eda"] = f"ok, sweat rule withheld EDA in {n_sweat} of {len(rep.rounds)} rounds"

    # per-rest
    for i, w in enumerate(rests):
        rr_all: list[Sample] = []
        for n in ("ppg-rr", "ecg-rr", "oracle-rr"):
            if n in rr_sources:
                rr_all = rr_sources[n]
                break
        per_source = {n: hr_windows(rr, w) for n, rr in rr_sources.items()}
        fused = fuse_hr(per_source)
        if still_name:
            f = still_fraction(still, w)
            src = "imu" if (f is not None and f >= STILL_MIN_FRACTION) else "not still"
        else:
            src = "assumed (no IMU)"
        rmssd, nb = (None, 0)
        notes: list[str] = []
        if src != "not still" and w.length_s >= HRV_MIN_STILL_S and rr_all:
            rmssd, nb = rmssd_in_window(rr_all, w)
        elif w.length_s < HRV_MIN_STILL_S:
            notes.append(f"rest shorter than {HRV_MIN_STILL_S:.0f} s: no HRV")
        elif src == "not still":
            notes.append("IMU says not still: no HRV")
        rep.rests.append(RestSummary(index=i + 1, t_start=w.t_start, t_end=w.t_end, still_source=src, rmssd_ms=rmssd, n_beats=nb,
                                     hr_recovery_bpm_per_min=recovery_slope(fused, w),
                                     nose_slope_c_per_min=nose_slope_c_per_min(thermal, w) if thermal else None,
                                     breaths_per_min=breaths_per_min(breaths, w) if breaths else None, notes=notes))
    return rep


# ---------------------------------------------------------------------------
# M-F5: mode state machine (behavioural reference for the firmware)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PacerConfig:
    enabled: bool
    inhale_ms: int = 4000
    exhale_ms: int = 6000
    pattern: str = "resonance"      # "resonance" | "prime" | "cyclic-sigh" | "off"


class CombatModes:
    """Plan §6 modes. Inputs: cue events and periodic ticks (t, hr_bpm, still). Output: mode + pacer configuration + mode cues.

    SANCTUARY       resonance pacer 6 bpm, tally armed (intrusion log)
    TRANQUIL        resonance pacer 6 bpm (default after session-start)
    COMBAT_PRIME    fast priming breaths (2 s / 1 s) for PRIME_S before a round, or on the `prime` cue
    COMBAT_SUSTAIN  pacer off during the round; only impact / HR warnings are cued
    RECOVER         cyclic sighing (double inhale 2+1 s, long exhale 7 s) for RECOVER_S after round-end, then TRANQUIL
    """
    SANCTUARY, TRANQUIL, COMBAT_PRIME, COMBAT_SUSTAIN, RECOVER = "sanctuary", "tranquil", "combat-prime", "combat-sustain", "recover"
    PRIME_S = 60.0
    RECOVER_S = 90.0
    HR_RECOVERED_MARGIN = 20.0

    PACERS = {
        SANCTUARY: PacerConfig(True, 4000, 6000, "resonance"),
        TRANQUIL: PacerConfig(True, 4000, 6000, "resonance"),
        COMBAT_PRIME: PacerConfig(True, 2000, 1000, "prime"),
        COMBAT_SUSTAIN: PacerConfig(False, 0, 0, "off"),
        RECOVER: PacerConfig(True, 3000, 7000, "cyclic-sigh"),
    }

    def __init__(self) -> None:
        self.mode: str | None = None
        self.entered_at: float | None = None
        self.resting_hr: float | None = None
        self.tally = 0
        self.cues: list[tuple[float, str]] = []
        self.in_session = False

    def _enter(self, mode: str, t: float) -> None:
        if mode != self.mode:
            self.mode, self.entered_at = mode, t
            self.cues.append((t, f"mode:{mode}"))

    @property
    def pacer(self) -> PacerConfig:
        return self.PACERS[self.mode] if self.mode else PacerConfig(False, 0, 0, "off")

    def event(self, t: float, cue: str) -> None:
        if cue == CUE_SESSION_START:
            self.in_session = True
            self._enter(self.TRANQUIL, t)
        elif cue == CUE_SESSION_END:
            self.in_session = False
            self.cues.append((t, f"summary:tally={self.tally}"))
            self.mode, self.entered_at = None, None
        elif not self.in_session:
            return
        elif cue == CUE_SANCTUARY:
            self._enter(self.SANCTUARY, t)
        elif cue == CUE_PRIME:
            self._enter(self.COMBAT_PRIME, t)
        elif cue == CUE_ROUND_START:
            self._enter(self.COMBAT_SUSTAIN, t)
        elif cue == CUE_ROUND_END:
            self._enter(self.RECOVER, t)
        elif cue == CUE_TALLY:
            self.tally += 1
            self.cues.append((t, "tally-ack"))

    def tick(self, t: float, hr_bpm: float | None = None, still: bool | None = None, impact_g: float | None = None) -> None:
        if not self.in_session or self.mode is None or self.entered_at is None:
            return
        if self.mode in (self.TRANQUIL, self.SANCTUARY) and hr_bpm is not None and still:
            # resting HR: slowest still HR seen in the calm modes
            self.resting_hr = hr_bpm if self.resting_hr is None else min(self.resting_hr, hr_bpm)
        if self.mode == self.COMBAT_PRIME and t - self.entered_at >= self.PRIME_S:
            self._enter(self.TRANQUIL, t)             # primed but the round did not start: settle
        elif self.mode == self.RECOVER:
            recovered = self.resting_hr is not None and hr_bpm is not None and hr_bpm <= self.resting_hr + self.HR_RECOVERED_MARGIN
            if recovered or t - self.entered_at >= self.RECOVER_S:
                self._enter(self.TRANQUIL, t)
        if self.mode == self.COMBAT_SUSTAIN and impact_g is not None and impact_g >= 10.0:
            self.cues.append((t, f"impact:{impact_g:.0f}g"))


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------


def _f(v: float | None, fmt: str = "{:.1f}", none: str = "—") -> str:
    return none if v is None else fmt.format(v)


def format_report(r: SessionReport) -> str:
    lines = [f"combat session: {r.path}", f"  duration {r.duration_s:.0f} s; channels: " + ", ".join(f"{k} ({n})" for k, n in sorted(r.channels.items())),
             f"  RR sources: {', '.join(r.rr_channels) or 'none'}; thermal: {r.thermal_channel or 'none'}; EDA: {r.eda_channel or 'none'}; stillness: {r.still_source}",
             f"  integrity: {r.integrity.get('lines', 0)} lines, {r.integrity.get('skipped', 0)} skipped, {r.integrity.get('duplicates', 0)} duplicate, "
             f"{r.integrity.get('lost', 0)} lost ({r.integrity.get('firmware_drops', 0)} firmware drops); {r.integrity.get('boots', 0)} boot(s), time base {r.integrity.get('time_base', '?')}",
             "  capabilities: " + "; ".join(f"{k} = {v}" for k, v in r.capabilities.items()),
             f"  intrusion tallies: {r.tallies}; impacts: {r.impacts_total} (cumulative {r.impact_exposure_g:.0f} g)"]
    for n in r.notes:
        lines.append(f"  note: {n}")
    lines.append("  rounds (in-round HR is coarse; HRV is never reported in-round):")
    lines.append("    #  start    end    HR mean  HR peak  HR windows  breaths/min  SCR/min  EDA        impacts")
    for x in r.rounds:
        lines.append(f"    {x.index:<2d} {x.t_start:7.0f} {x.t_end:7.0f}  {_f(x.hr_mean_bpm, '{:6.0f}'):>7s}  {_f(x.hr_peak_bpm, '{:6.0f}'):>7s}  "
                     f"{x.hr_windows_reported:3d}/{x.hr_windows_total:<3d}      {_f(x.breaths_per_min):>6s}      {_f(x.scr_per_min):>5s}  {x.eda_quality:<10s} "
                     f"{x.impacts}{'' if x.impact_peak_g is None else f' (peak {x.impact_peak_g:.0f} g)'}")
        for n in x.notes:
            lines.append(f"       note: {n}")
    lines.append("  rests (RMSSD only in still windows ≥ 60 s):")
    lines.append("    #  start    end    still            RMSSD ms  beats  HR recovery bpm/min  nose °C/min  breaths/min")
    for x in r.rests:
        lines.append(f"    {x.index:<2d} {x.t_start:7.0f} {x.t_end:7.0f}  {x.still_source:<16s} {_f(x.rmssd_ms, '{:7.1f}'):>8s}  {x.n_beats:5d}  "
                     f"{_f(x.hr_recovery_bpm_per_min, '{:+.1f}'):>19s}  {_f(x.nose_slope_c_per_min, '{:+.3f}'):>11s}  {_f(x.breaths_per_min):>11s}")
        for n in x.notes:
            lines.append(f"       note: {n}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1] if __doc__ else "")
    ap.add_argument("capture", help="NDJSON capture file")
    ap.add_argument("--rounds", type=int, default=None, help="number of rounds when the capture has no round cues")
    ap.add_argument("--round-s", type=float, default=180.0)
    ap.add_argument("--rest-s", type=float, default=60.0)
    ap.add_argument("--thermal-channel", default=None, help="override: temp-nose (default) or temp-forehead")
    ap.add_argument("--eda-channel", default=None, help="override: eda-forehead (default) or gsr")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 2 when any line was skipped as malformed (CI gate, Track N)")
    args = ap.parse_args(argv)
    if not Path(args.capture).exists():
        print(f"error: {args.capture} not found", file=sys.stderr)
        return 1
    try:
        rep = analyze(args.capture, rounds=args.rounds, round_s=args.round_s, rest_s=args.rest_s,
                      thermal_channel=args.thermal_channel, eda_channel=args.eda_channel)
    except (OSError, ValueError, TypeError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(asdict(rep), indent=2))
    else:
        print(format_report(rep))
    if args.strict and rep.integrity.get("skipped", 0):
        print(f"strict: {rep.integrity['skipped']} malformed line(s) skipped", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
