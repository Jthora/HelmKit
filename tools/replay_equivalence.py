#!/usr/bin/env python3
"""
replay_equivalence.py — do the helm's derived channels match the host references on the same raw data? (Track N, N-H4)

Spec: docs/plans/2026-tier1-launch/track-N-capability-robustness.md §4 (N-H4) and gate N-G6. The Python
implementations in tools/analyze_combat_session.py are the behavioural spec; the firmware ports must produce the same
events from the same raw streams. This tool takes one capture that holds both (the raw `temp-nose` / `gsr` /
`eda-forehead` samples and the firmware's `resp-thermal` / `scr` / `mode:` lines) and reports, per check:

  breathing   host breath_times() on the thermal channel vs firmware `resp-thermal` lines: count and rate
              within `--breaths-tol` per minute, and >= 80 % of firmware breaths within 1 s of a host breath
  scr         host scr_times() on the EDA channel vs firmware `scr` events: count within `--scr-tol`
  modes       the operator cues replayed through the host CombatModes (ticked at 1 Hz with the fused HR)
              vs the firmware's `mode:*` cue sequence: identical
  rr          skipped unless raw `ppg-hrv` samples are present (the firmware does not stream them by default);
              when present, scripts/rr_replay.py is the reference (RMS RR error <= `--rr-tol` ms)

Exit 0 when every performed check passes, 2 otherwise, 1 on a bad input. `--json` for machines.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_combat_session as A  # noqa: E402


@dataclass
class Check:
    name: str
    performed: bool
    ok: bool
    detail: str
    host: float | int | None = None
    firmware: float | int | None = None


@dataclass
class Report:
    path: str
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks if c.performed)


def _match_fraction(fw_times: list[float], host_times: list[float], tol_s: float) -> float:
    if not fw_times:
        return 0.0
    hit = 0
    j = 0
    hs = sorted(host_times)
    for t in sorted(fw_times):
        while j < len(hs) and hs[j] < t - tol_s:
            j += 1
        if j < len(hs) and abs(hs[j] - t) <= tol_s:
            hit += 1
    return hit / len(fw_times)


def check_breathing(cap: A.Capture, tol_per_min: float) -> Check:
    th_name, thermal = cap.channel(*A.THERMAL_CHANNELS)
    fw = cap.numeric.get("resp-thermal", [])
    if th_name is None or not fw:
        return Check("breathing", False, True, "skipped: needs a thermal channel and firmware resp-thermal lines")
    host = A.breath_times(thermal)
    span = max(1e-9, (cap.t_max or 0.0) - (cap.t_min or 0.0))
    host_rate = 60.0 * len(host) / span
    fw_rate = 60.0 * len(fw) / span
    frac = _match_fraction([s.t for s in fw], host, 1.0)
    ok = abs(host_rate - fw_rate) <= tol_per_min and frac >= 0.8
    return Check("breathing", True, ok,
                 f"host {len(host)} breaths ({host_rate:.1f}/min) vs firmware {len(fw)} ({fw_rate:.1f}/min); "
                 f"{100 * frac:.0f} % of firmware breaths within 1 s of a host breath", host_rate, fw_rate)


def check_scr(cap: A.Capture, tol: int) -> Check:
    eda_name, eda = cap.channel(*A.EDA_CHANNELS)
    fw = cap.numeric.get("scr", [])
    if eda_name is None or "scr" not in cap.numeric:
        return Check("scr", False, True, "skipped: needs an EDA channel and firmware scr lines")
    host = A.scr_times(eda)
    ok = abs(len(host) - len(fw)) <= tol
    return Check("scr", True, ok, f"host {len(host)} responses vs firmware {len(fw)} (tolerance {tol})", len(host), len(fw))


def _firmware_modes(cap: A.Capture) -> list[str]:
    return [e.v[5:] for e in cap.cues if e.v.startswith("mode:")]


def _host_modes(cap: A.Capture) -> list[tuple[float, str]]:
    """Replay the operator cues through the host state machine at 1 Hz with the fused HR: [(t, mode name)]."""
    ops = [e for e in cap.cues if e.v in (A.CUE_SESSION_START, A.CUE_SESSION_END, A.CUE_ROUND_START, A.CUE_ROUND_END,
                                          A.CUE_PRIME, A.CUE_SANCTUARY, A.CUE_TALLY)]
    if not ops:
        return []
    rr_sources = {n: cap.numeric[n] for n in ("ppg-rr", "ecg-rr", "oracle-rr") if n in cap.numeric}
    still_name, still = cap.channel("still")
    impacts = cap.numeric.get("impact", [])
    m = A.CombatModes()
    t = ops[0].t
    t_end = max(cap.t_max or t, ops[-1].t) + 1.0
    k = 0
    while t <= t_end:
        while k < len(ops) and ops[k].t <= t:
            m.event(ops[k].t, ops[k].v)
            k += 1
        w = A.Window("tick", t - A.HR_WINDOW_S, t)
        fused = A.fuse_hr({n: A.hr_windows(rr, w) for n, rr in rr_sources.items()})
        hr = fused[-1].hr_bpm if fused else None
        st = None
        if still_name:
            f = A.still_fraction(still, A.Window("s", t - 2.0, t))
            st = None if f is None else f >= 0.5
        imp = max((s.v for s in impacts if t - 1.0 < s.t <= t), default=None)
        m.tick(t, hr, st, imp)
        t += 1.0
    return [(t, c[5:]) for t, c in m.cues if c.startswith("mode:")]


def check_modes(cap: A.Capture) -> Check:
    fw = _firmware_modes(cap)
    if not fw:
        return Check("modes", False, True, "skipped: no firmware mode: cues")
    host = [name for _, name in _host_modes(cap)]
    ok = host == fw
    detail = "identical" if ok else f"host {host} vs firmware {fw}"
    return Check("modes", True, ok, f"{len(fw)} transitions: {detail}", len(host), len(fw))


def check_rr(cap: A.Capture, tol_ms: float) -> Check:
    if "ppg-hrv" not in cap.numeric or "ppg-rr" not in cap.numeric:
        return Check("rr", False, True, "skipped: raw ppg-hrv samples are not in the capture")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "firmware" / "mk0.5" / "scripts"))
        import rr_replay  # type: ignore
    except ImportError:
        return Check("rr", False, True, "skipped: rr_replay.py not importable")
    raw = cap.numeric["ppg-hrv"]
    ref = rr_replay.replay_samples([(s.t, s.v) for s in raw]) if hasattr(rr_replay, "replay_samples") else None
    if ref is None:
        return Check("rr", False, True, "skipped: rr_replay has no replay_samples() entry point")
    fw = [(s.t, s.v) for s in cap.numeric["ppg-rr"] if s.q == "ok" and s.v > 0]
    pairs = []
    j = 0
    for t, v in fw:
        while j < len(ref) and ref[j][0] < t - 0.1:
            j += 1
        if j < len(ref) and abs(ref[j][0] - t) <= 0.1:
            pairs.append((v, ref[j][1]))
    if not pairs:
        return Check("rr", True, False, "no matching peaks between firmware and reference", 0, len(fw))
    rms = (sum((a - b) ** 2 for a, b in pairs) / len(pairs)) ** 0.5
    return Check("rr", True, rms <= tol_ms, f"RMS RR error {rms:.1f} ms over {len(pairs)} matched beats", rms, len(fw))


def compare(path: str | Path, *, breaths_tol: float = 1.0, scr_tol: int = 1, rr_tol_ms: float = 15.0) -> Report:
    cap = A.load_capture(path)
    rep = Report(str(path))
    rep.checks.append(check_breathing(cap, breaths_tol))
    rep.checks.append(check_scr(cap, scr_tol))
    rep.checks.append(check_modes(cap))
    rep.checks.append(check_rr(cap, rr_tol_ms))
    return rep


def format_report(r: Report) -> str:
    lines = [f"replay equivalence: {r.path}"]
    for c in r.checks:
        tag = "skip" if not c.performed else ("PASS" if c.ok else "FAIL")
        lines.append(f"  {c.name:<10} {tag:<4} {c.detail}")
    lines.append("  result: " + ("PASS" if r.ok else "FAIL"))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="firmware-vs-host equivalence on one capture (Track N gate N-G6)")
    ap.add_argument("capture")
    ap.add_argument("--breaths-tol", type=float, default=1.0, help="breaths per minute")
    ap.add_argument("--scr-tol", type=int, default=1)
    ap.add_argument("--rr-tol", type=float, default=15.0, help="RMS RR error, ms")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not Path(args.capture).exists():
        print(f"error: {args.capture} not found", file=sys.stderr)
        return 1
    rep = compare(args.capture, breaths_tol=args.breaths_tol, scr_tol=args.scr_tol, rr_tol_ms=args.rr_tol)
    if args.json:
        print(json.dumps({"path": rep.path, "ok": rep.ok, "checks": [asdict(c) for c in rep.checks]}, indent=2))
    else:
        print(format_report(rep))
    return 0 if rep.ok else 2


if __name__ == "__main__":
    sys.exit(main())
