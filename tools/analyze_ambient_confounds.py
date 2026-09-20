#!/usr/bin/env python3
"""
analyze_ambient_confounds.py — correlate an ambient reference channel
(RF spectrum survey, magnetometer/gradiometer reading, or any other
scalar environmental channel) against a biometric-anomaly channel, to
check whether a "significant" dyadic or forced-choice result might be
explained by a mundane shared external stimulus instead of anything
psi-adjacent.

Design doc: docs/psionic_engineering/computational_toolkit.md

Why this exists: `tools/analyze_dyadic_coherence.py` can flag "anomalous
synchrony" between two subjects' biosignals, surrogate-tested against
chance. That flag means "more correlated than the circular-shift null" —
it does NOT mean "not explained by a shared external cause." Two
subjects in the same room will show correlated HRV/GSR if a shared
ambient RF transient, an HVAC cycle, or an audible click happens to
coincide with both subjects' physiological response. Before any dyadic
or forced-choice result is treated as interesting, it should be checked
against whatever ambient channel was recorded during the same session.

Deliberate scope/safety decision: this tool does NOT capture ambient
data itself and contains NO SDR/radio invocation code whatsoever. It
only analyzes an already-captured NDJSON log (e.g. periodic broadband RF
power readings from a `hackrf_sweep`-class session, or magnetometer/
gradiometer readings, run and logged separately by the operator). Per
`docs/inventory.md`, the HackRF One is transmit-capable (TX+RX) — rather
than adding SDR-driving code here and then trying to constrain it to
RX-only calls, this tool sidesteps that hazard class entirely by never
touching the hardware at all. Capture is a separate, human-operated step
outside this tool's scope.

No microphone/audio confound channel exists in the current inventory
(`docs/inventory.md`) — that is a real, named gap, not a silent
omission. An ambient audio channel could be added the same way (any
NDJSON scalar channel works) once a microphone capture path exists.

Architecture note: the actual correlation/surrogate-testing logic is NOT
reimplemented here. "Is the ambient channel correlated with the target
channel beyond a circular-shift null" is the exact same statistical
question `analyze_dyadic_coherence.py`'s `analyze_dyadic` already
answers for two-subject synchrony — this file imports and reuses it
directly against a (ambient, target) pair instead of a (subject A,
subject B) pair, and adds only confound-specific framing, CLI, and
reporting on top. Per this session's own retrospective on premature
infrastructure: no new shared module was extracted for this — direct
reuse of an existing, already-tested function was sufficient.

Stdlib only, same discipline as the rest of tools/ — see
tools/requirements.txt.

Exit codes:
    0 — analysis completed (regardless of finding — see the report for
        the actual verdict)
    2 — file/parse error
    3 — usage error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from tools.analyze_dyadic_coherence import (
        DyadicReport,
        analyze_dyadic,
        load_scalar_channel_from_ndjson,
        report_to_json,
        synth_dyad,
    )
except ImportError:
    # See tools/analyze_dyadic_coherence.py for why this fallback exists —
    # running this script directly only puts tools/ on sys.path, not the
    # repo root the `tools` namespace package lives under.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools.analyze_dyadic_coherence import (
        DyadicReport,
        analyze_dyadic,
        load_scalar_channel_from_ndjson,
        report_to_json,
        synth_dyad,
    )


def format_confound_report(
    report: DyadicReport, *, ambient_channel: str, target_channel: str
) -> str:
    out = ["Ambient Confound Check", "=" * 60, ""]
    out.append(f"ambient channel: {ambient_channel}    target channel: {target_channel}")
    out.append(f"n_samples={report.n_samples} at dt={report.dt}s "
               f"({report.n_samples * report.dt:.0f}s overlap window)")
    out.append("")
    out.append(
        f"Lagged cross-correlation: peak |r| = {report.xcorr_peak:.4f} at "
        f"lag {report.xcorr_peak_lag * report.dt:.1f}s, "
        f"surrogate p={report.xcorr_surrogate.p_value:.4f}"
    )
    out.append(
        f"CRQA determinism = {report.crqa_result.determinism:.4f}, "
        f"surrogate p={report.det_surrogate.p_value:.4f}"
    )
    out.append("")
    flagged = report.xcorr_surrogate.p_value < 0.05 or report.det_surrogate.p_value < 0.05
    if flagged:
        out.append(
            "VERDICT: CONFOUND RISK — the ambient channel correlates with the "
            "target beyond chance (p<0.05 on at least one metric). Any "
            "concurrent dyadic-synchrony or forced-choice finding recorded "
            "during this session should be treated with suspicion until this "
            "is ruled out or explained."
        )
    else:
        out.append(
            "VERDICT: no ambient confound detected beyond chance on this "
            "channel. This does NOT clear every possible confound — only "
            "the specific ambient channel actually checked here."
        )
    return "\n".join(out)


def confound_report_to_json(
    report: DyadicReport, *, ambient_channel: str, target_channel: str
) -> dict:
    data = report_to_json(report)
    data["ambient_channel"] = ambient_channel
    data["target_channel"] = target_channel
    data["confound_flagged"] = data.pop("significant")
    return data


def _cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="analyze_ambient_confounds.py",
        description="Check whether an ambient reference channel correlates with a biometric target channel beyond chance.",
    )
    p.add_argument("--ambient", help="NDJSON capture containing the ambient reference channel.")
    p.add_argument("--ambient-channel", default="rf-power-dbm",
                    help="Channel name for the ambient reference (default: rf-power-dbm).")
    p.add_argument("--target", help="NDJSON capture containing the biometric/target channel.")
    p.add_argument("--target-channel", default="ppg-rr",
                    help="Channel name for the target signal (default: ppg-rr).")
    p.add_argument("--dt", type=float, default=1.0, help="Resample interval, seconds (default 1.0).")
    p.add_argument("--max-lag-s", type=float, default=10.0, help="Max cross-correlation lag, seconds.")
    p.add_argument("--n-surrogates", type=int, default=200)
    p.add_argument("--seed", type=int, default=1729)
    p.add_argument("--json", action="store_true")
    p.add_argument("--self-test", choices=["confounded", "clean"], default=None,
                    help="Run on a synthetic ambient/target pair instead of real files.")
    args = p.parse_args(argv)

    if args.self_test:
        ambient, target = synth_dyad(correlated=(args.self_test == "confounded"))
        ambient_channel, target_channel = "synthetic-ambient", "synthetic-target"
    else:
        if args.ambient is None or args.target is None:
            print("analyze_ambient_confounds: --ambient and --target are required (or use --self-test).",
                  file=sys.stderr)
            return 3
        try:
            ambient = load_scalar_channel_from_ndjson(args.ambient, channel=args.ambient_channel)
            target = load_scalar_channel_from_ndjson(args.target, channel=args.target_channel)
        except FileNotFoundError as exc:
            print(f"analyze_ambient_confounds: file not found: {exc.filename}", file=sys.stderr)
            return 2
        ambient_channel, target_channel = args.ambient_channel, args.target_channel

    try:
        report = analyze_dyadic(
            ambient, target, dt=args.dt, max_lag_s=args.max_lag_s,
            n_surrogates=args.n_surrogates, seed=args.seed,
        )
    except ValueError as exc:
        print(f"analyze_ambient_confounds: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(
            confound_report_to_json(report, ambient_channel=ambient_channel, target_channel=target_channel),
            indent=2, sort_keys=True,
        ))
    else:
        print(format_confound_report(report, ambient_channel=ambient_channel, target_channel=target_channel))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
