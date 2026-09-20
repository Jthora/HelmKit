#!/usr/bin/env python3
"""
forced_choice_protocol.py — classic forced-choice / RNG-deviation psi
protocol, implemented as pure software (no HelmKit hardware required).

Design doc: docs/psionic_engineering/computational_toolkit.md

Why this exists: the wiki's own F1/F2 falsifiers (docs/falsification.md)
cite Ganzfeld and Star Gate results, which are forced-choice designs — a
subject guesses which of k alternatives a random-number generator picked,
repeated over many trials, and the hit rate is compared to chance (1/k).
This is the best-studied experimental paradigm in the parapsychology
literature and needs zero HelmKit sensor hardware: a target sequence, an
RNG, a way to record guesses, and correct statistics.

The methodological discipline this tool enforces (all historically
significant failure modes of this exact paradigm):

  1. Target pre-commitment. The full target sequence is generated before
     the session and its SHA-256 hash can be published/recorded BEFORE
     any guesses are made (`commit`). This rules out post-hoc target
     selection or "the experimenter remembers wrong" ambiguity — anyone
     can later verify the revealed target file hashes to the
     pre-published commitment.
  2. No optional stopping baked in silently. `score` reports the result
     for exactly the N in the targets file; if you want a sequential
     design with proper stopping boundaries, that is a real statistical
     tool this does NOT implement (see docs/psionic_engineering/
     computational_toolkit.md "what this does not do yet").
  3. Correct statistics for the design. A proportion test and a
     Beta-Binomial Bayes factor (both exact, both imported from
     `tools/experiment_design.py`) — NOT a t-test, which is the wrong
     test family for hit-rate data and would misstate significance.

What this tool does NOT do: conduct a live, blinded, in-person session
(sensory shielding, experimenter blinding, timing) — that is a physical
protocol design question (see the wiki's own `Sham Control Design` page
and `docs/falsification.md`), not a software question. This tool covers
target generation/commitment and post-hoc scoring only.

Stdlib only, plus the existing project dependency on this repo's own
tools/experiment_design.py (also stdlib-only).

Exit codes:
    0 — success
    2 — file/data error
    3 — usage error
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import random
import sys
from pathlib import Path

try:
    from tools.experiment_design import (
        achieved_power_binomial,
        binomial_bayes_factor,
        interpret_bayes_factor,
        one_proportion_z_test,
        required_n_binomial,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools.experiment_design import (
        achieved_power_binomial,
        binomial_bayes_factor,
        interpret_bayes_factor,
        one_proportion_z_test,
        required_n_binomial,
    )


# ---------------------------------------------------------------------------
# Target generation and commitment
# ---------------------------------------------------------------------------


def generate_targets(n_trials: int, k_alternatives: int, *, seed: int | None = None) -> list[int]:
    """Generate `n_trials` targets, each uniform in [0, k_alternatives).

    Uses `random.SystemRandom` (the OS CSPRNG) by default -- deliberately
    NOT the same `random.Random(seed)` used elsewhere in this repo for
    reproducible *synthetic test data*, because a predictable PRNG seed
    is exactly the kind of methodological weakness this protocol exists
    to avoid. Pass an explicit `seed` only for self-tests.
    """
    rng = random.SystemRandom() if seed is None else random.Random(seed)
    return [rng.randrange(k_alternatives) for _ in range(n_trials)]


def commitment_hash(targets: list[int]) -> str:
    """SHA-256 of the canonical JSON encoding of the target sequence.
    Publish this BEFORE the session (e.g. paste it into a lab notebook
    or commit it to version control); reveal the full target file only
    at scoring time. Anyone can then verify `commitment_hash(targets)`
    against the pre-published value to confirm no tampering."""
    payload = json.dumps(targets, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_targets_file(path: str | Path, targets: list[int], k: int) -> dict:
    doc = {
        "targets": targets,
        "k_alternatives": k,
        "n_trials": len(targets),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "commitment_sha256": commitment_hash(targets),
    }
    p = Path(path)
    if p.exists():
        raise FileExistsError(f"{p} already exists -- generate a new dated file instead of overwriting a target set.")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_session(targets: list[int], responses: list[int], *, k_alternatives: int) -> dict:
    """Score a completed session: hits, chance rate, frequentist
    proportion test, and exact Beta-Binomial Bayes factor."""
    if len(targets) != len(responses):
        raise ValueError(
            f"targets ({len(targets)}) and responses ({len(responses)}) must be the same length"
        )
    n = len(targets)
    if n == 0:
        raise ValueError("need at least one trial")
    for label, seq in (("targets", targets), ("responses", responses)):
        for v in seq:
            if not isinstance(v, int) or not 0 <= v < k_alternatives:
                raise ValueError(f"{label} must all be integers in [0, {k_alternatives})")

    hits = sum(1 for t, r in zip(targets, responses) if t == r)
    p0 = 1.0 / k_alternatives
    z, p_value = one_proportion_z_test(hits, n, p0)
    bf01, bf10 = binomial_bayes_factor(hits, n, p0)

    return {
        "n_trials": n,
        "k_alternatives": k_alternatives,
        "hits": hits,
        "hit_rate": hits / n,
        "chance_rate": p0,
        "z": z,
        "p_value": p_value,
        "bf01": bf01,
        "bf10": bf10,
        "interpretation": interpret_bayes_factor(bf10),
    }


def format_score_report(result: dict) -> str:
    out = ["Forced-Choice Protocol Score Report", "=" * 60, ""]
    out.append(
        f"{result['hits']}/{result['n_trials']} hits "
        f"(rate={result['hit_rate']:.4f}) vs chance={result['chance_rate']:.4f} "
        f"(k={result['k_alternatives']})"
    )
    out.append(f"Frequentist: z={result['z']:.4f}, p={result['p_value']:.4g}")
    out.append(f"Bayesian:    BF10={result['bf10']:.4g}, BF01={result['bf01']:.4g}")
    out.append(f"             {result['interpretation']}")
    out.append("")
    out.append(
        "This scores exactly the N in the targets file with no optional "
        "stopping. If the targets file's commitment_sha256 was published "
        "before the session, verify it with `verify-commitment` before "
        "trusting this result."
    )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def self_test_session(
    *, mode: str, n_trials: int = 300, k_alternatives: int = 4, true_hit_rate: float = 0.35, seed: int = 1729
) -> dict:
    """Simulate a full generate -> respond -> score cycle in memory (no
    files). `mode="null"` simulates pure chance guessing; `mode="psi"`
    simulates a subject whose guesses match the target with probability
    `true_hit_rate` (elevated above chance) and guess uniformly at
    random otherwise -- NOT a claim that this is how psi would work if
    real, just a way to validate that the scoring pipeline correctly
    detects an elevated hit rate when one is deliberately injected."""
    targets = generate_targets(n_trials, k_alternatives, seed=seed)
    rng = random.Random(seed + 1)
    p0 = 1.0 / k_alternatives
    responses = []
    for t in targets:
        if mode == "psi" and rng.random() < (true_hit_rate - p0) / (1 - p0):
            responses.append(t)
        else:
            responses.append(rng.randrange(k_alternatives))
    return score_session(targets, responses, k_alternatives=k_alternatives)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cmd_plan(args: argparse.Namespace) -> int:
    n = required_n_binomial(args.p1, p0=1.0 / args.k, alpha=args.alpha, power=args.power)
    print(
        f"For k={args.k} alternatives (chance={1.0/args.k:.4f}), target hit rate "
        f"p1={args.p1}, alpha={args.alpha}, power={args.power}: required N = {n} trials."
    )
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    targets = generate_targets(args.n, args.k, seed=args.seed)
    try:
        doc = write_targets_file(args.out, targets, args.k)
    except FileExistsError as exc:
        print(f"forced_choice_protocol generate: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {doc['n_trials']} targets (k={doc['k_alternatives']}) to {args.out}")
    print(f"commitment_sha256 = {doc['commitment_sha256']}")
    print("Publish that hash BEFORE the session. Keep the targets file hidden until scoring.")
    if args.seed is not None:
        print("WARNING: --seed was given -- this used a reproducible PRNG, not the OS CSPRNG. "
              "Only use --seed for testing, never for a real session.", file=sys.stderr)
    return 0


def _cmd_verify_commitment(args: argparse.Namespace) -> int:
    doc = json.loads(Path(args.targets).read_text(encoding="utf-8"))
    actual = commitment_hash(doc["targets"])
    matches = actual == args.commitment
    print(f"recomputed commitment: {actual}")
    print(f"expected commitment:   {args.commitment}")
    print("MATCH" if matches else "MISMATCH -- targets file does not match the published commitment")
    return 0 if matches else 1


def _cmd_score(args: argparse.Namespace) -> int:
    targets_doc = json.loads(Path(args.targets).read_text(encoding="utf-8"))
    responses = json.loads(Path(args.responses).read_text(encoding="utf-8"))
    if isinstance(responses, dict):
        responses = responses["responses"]
    try:
        result = score_session(targets_doc["targets"], responses, k_alternatives=targets_doc["k_alternatives"])
    except ValueError as exc:
        print(f"forced_choice_protocol score: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_score_report(result))
    return 0


def _cmd_self_test(args: argparse.Namespace) -> int:
    result = self_test_session(mode=args.mode, n_trials=args.n, k_alternatives=args.k)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_score_report(result))
    return 0


def _cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="forced_choice_protocol.py",
        description="Classic forced-choice / RNG-deviation psi protocol: target generation, commitment, and scoring.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("plan", help="Required N for a target hit rate above chance.")
    pl.add_argument("--k", type=int, required=True, help="Number of alternatives (chance = 1/k).")
    pl.add_argument("--p1", type=float, required=True, help="Hypothesized true hit rate.")
    pl.add_argument("--alpha", type=float, default=0.05)
    pl.add_argument("--power", type=float, default=0.80)
    pl.set_defaults(func=_cmd_plan)

    gn = sub.add_parser("generate", help="Generate and commit a target sequence.")
    gn.add_argument("--n", type=int, required=True, help="Number of trials.")
    gn.add_argument("--k", type=int, required=True, help="Number of alternatives.")
    gn.add_argument("--out", required=True, help="Output path for the sealed targets file.")
    gn.add_argument("--seed", type=int, default=None,
                     help="TESTING ONLY: reproducible PRNG seed instead of the OS CSPRNG.")
    gn.set_defaults(func=_cmd_generate)

    vc = sub.add_parser("verify-commitment", help="Check a targets file against a previously published commitment hash.")
    vc.add_argument("--targets", required=True)
    vc.add_argument("--commitment", required=True)
    vc.set_defaults(func=_cmd_verify_commitment)

    sc = sub.add_parser("score", help="Score a completed session (targets file + responses file).")
    sc.add_argument("--targets", required=True, help="Path to the sealed targets file from `generate`.")
    sc.add_argument("--responses", required=True, help="Path to a JSON list (or {\"responses\": [...]}) of integer guesses.")
    sc.add_argument("--json", action="store_true")
    sc.set_defaults(func=_cmd_score)

    st = sub.add_parser("self-test", help="Simulate a full session in memory (no files) to validate the pipeline.")
    st.add_argument("--mode", choices=["null", "psi"], default="null")
    st.add_argument("--n", type=int, default=300)
    st.add_argument("--k", type=int, default=4)
    st.add_argument("--json", action="store_true")
    st.set_defaults(func=_cmd_self_test)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
