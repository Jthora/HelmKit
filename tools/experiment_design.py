#!/usr/bin/env python3
"""
experiment_design.py — power analysis, approximate Bayes factors, and a
pre-registration lock generator for HelmKit's F1–F11 / TML falsification
work (docs/falsification.md; the wiki's own TML-3/TML-4 pass criteria).

Design doc: docs/psionic_engineering/computational_toolkit.md

Why this exists: `docs/falsification.md`'s methodological floor requires
(1) pre-registration of hypotheses/predictions/analyses, (2) statistical
power >= 80% for the predicted effect, (3) standard frequentist or
Bayesian methods — "No special psi statistics." This tool is the
mechanical enforcement of that floor: compute the N a study actually
needs before running it, compute a Bayes factor after running it, and
lock the analysis plan (hashed, timestamped) before data collection so
the analysis can't be quietly changed after seeing the data.

Three independent capabilities:

  1. Power / sample-size planning (`power` subcommand). Normal
     approximation to the noncentral-t power function — standard
     textbook formula, accurate for planning purposes at the N ranges
     TML-3/TML-4 use (N=10-30). NOT exact for very small N; see
     `required_n`'s docstring for the caveat.

  2. Approximate Bayes factor (`bayes` subcommand). BIC-based
     approximation to the JZS Bayes factor for a one-sample/paired
     t-test (Wagenmakers 2007; Masson 2011) — NOT the exact Rouder et
     al. (2009) JZS integral, which requires numerical integration
     against a Cauchy prior. Treat as order-of-magnitude guidance;
     cross-check against a package like the R `BayesFactor` library or
     JASP before quoting in a publication.

  3. Pre-registration lock (`preregister` subcommand). Takes a YAML/JSON
     spec (hypothesis, primary endpoint, effect size, alpha, power,
     design) and emits a timestamped, SHA-256-hashed lock file — the
     mechanical version of "the analysis plan existed before the data."

Stdlib only. No numpy, no scipy — see tools/requirements.txt. PyYAML is
already a project dependency (used by wiki_sync.py) and is used here
only for reading a human-authored spec file, not for any numerics.

Exit codes:
    0 — success
    2 — file/spec error
    3 — usage error
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Normal distribution helpers (stdlib-only inverse CDF via bisection)
# ---------------------------------------------------------------------------


def norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def norm_ppf(p: float, *, tol: float = 1e-12, max_iter: int = 200) -> float:
    """Inverse standard normal CDF via bisection on math.erf. Stdlib-only
    substitute for scipy.stats.norm.ppf; accurate to `tol` in z-space."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be strictly between 0 and 1")
    lo, hi = -10.0, 10.0
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0


# ---------------------------------------------------------------------------
# Power / sample-size planning
# ---------------------------------------------------------------------------

_DESIGNS = ("paired", "one-sample", "two-sample")


def _z_alpha(alpha: float, two_sided: bool) -> float:
    return norm_ppf(1.0 - alpha / 2.0) if two_sided else norm_ppf(1.0 - alpha)


def required_n(
    effect_size_d: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
    design: str = "paired",
    two_sided: bool = True,
) -> int:
    """Minimum N for the given standardized effect size (Cohen's d).

    Normal approximation to the noncentral-t power function:
        paired / one-sample:  n = ((z_a + z_b) / d)^2
        two-sample (per group): n = 2 * ((z_a + z_b) / d)^2

    This is the standard large-sample approximation used for planning
    (e.g. it is what most back-of-envelope power calculators compute).
    It slightly UNDERESTIMATES the true noncentral-t-based N at small N
    (below ~20) because it ignores the extra uncertainty from estimating
    the variance. For TML-3-class studies (N=10-30), add a few subjects
    of margin rather than treating this as an exact minimum.
    """
    if effect_size_d <= 0:
        raise ValueError("effect_size_d must be positive")
    if design not in _DESIGNS:
        raise ValueError(f"design must be one of {_DESIGNS}, got {design!r}")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0,1)")
    if not 0.0 < power < 1.0:
        raise ValueError("power must be in (0,1)")

    z_a = _z_alpha(alpha, two_sided)
    z_b = norm_ppf(power)
    base = ((z_a + z_b) / effect_size_d) ** 2
    n = 2 * base if design == "two-sample" else base
    return math.ceil(n)


def achieved_power(
    n: float,
    effect_size_d: float,
    *,
    alpha: float = 0.05,
    design: str = "paired",
    two_sided: bool = True,
) -> float:
    """Inverse of `required_n`: power achieved at a given N. Same normal
    approximation, same caveat at small N."""
    if design not in _DESIGNS:
        raise ValueError(f"design must be one of {_DESIGNS}, got {design!r}")
    z_a = _z_alpha(alpha, two_sided)
    ncp_z = effect_size_d * math.sqrt(n / 2.0 if design == "two-sample" else n)
    return norm_cdf(ncp_z - z_a)


# ---------------------------------------------------------------------------
# Binomial / forced-choice designs (Ganzfeld/Star-Gate-style hit-rate tests)
# ---------------------------------------------------------------------------
#
# The wiki's own F1/F2 falsifiers (docs/falsification.md) cite Ganzfeld and
# Star Gate results, which are classically FORCED-CHOICE hit-rate designs —
# a proportion test against a known chance rate (1/k for k alternatives),
# not a mean-difference t-test. `required_n`/`bic_bayes_factor` above do not
# cover this design; the functions in this section do. See
# `tools/forced_choice_protocol.py` for a standalone tool built on top of
# these.

# Real primary-source hit rates, NOT the wiki's own citation (which conflates
# an r-type effect size with Cohen's d for a design that's binomial in the
# first place -- see docs/psionic_engineering/literature_grounding.md for the
# full derivation). Both entries are from Storm, Tressoldi & Di Risio (2010),
# "Meta-analysis of free-response studies, 1992-2008" -- a homogeneous set of
# 29 ganzfeld studies (1997-2008), 4-alternative forced choice (chance=0.25).
# Treat "optimistic" as an upper bound: a MORE RECENT (~2020-2021)
# preregistered replication found a smaller effect (r=0.08 vs 0.142 here,
# roughly half); no hit-rate figure for that newer study was available via
# search at write time, so it is not offered as a preset -- see
# literature_grounding.md's "Open items". Do not add a preset here without a
# real citation behind it.
GANZFELD_HIT_RATE_PRESETS: dict[str, float] = {
    "ganzfeld-storm2010-optimistic": 0.301,    # combined hit rate, all data
    "ganzfeld-storm2010-conservative": 0.27,   # earlier/homogeneous subset
}


def required_n_binomial(
    p1: float,
    *,
    p0: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
) -> int:
    """Minimum number of forced-choice trials to detect a true hit rate
    `p1` against chance rate `p0` (e.g. p0=0.25 for 4-alternative forced
    choice).

    Normal approximation with separate variances under H0 and H1 (the
    standard one-proportion power formula, e.g. Fleiss, Levin & Paik,
    "Statistical Methods for Rates and Proportions," 3rd ed., ch. 3):

        n = ( z_a*sqrt(p0(1-p0)) + z_b*sqrt(p1(1-p1)) )^2 / (p1-p0)^2
    """
    if not 0.0 < p0 < 1.0 or not 0.0 < p1 < 1.0:
        raise ValueError("p0 and p1 must be in (0,1)")
    if p1 == p0:
        raise ValueError("p1 must differ from p0 (no effect to detect)")
    z_a = _z_alpha(alpha, two_sided)
    z_b = norm_ppf(power)
    numerator = z_a * math.sqrt(p0 * (1 - p0)) + z_b * math.sqrt(p1 * (1 - p1))
    n = (numerator / (p1 - p0)) ** 2
    return math.ceil(n)


def achieved_power_binomial(
    n: int, p1: float, *, p0: float, alpha: float = 0.05, two_sided: bool = True
) -> float:
    """Inverse of `required_n_binomial`: power achieved at a given trial
    count `n`. Same normal approximation, same reference."""
    if not 0.0 < p0 < 1.0 or not 0.0 < p1 < 1.0:
        raise ValueError("p0 and p1 must be in (0,1)")
    z_a = _z_alpha(alpha, two_sided)
    se0 = math.sqrt(p0 * (1 - p0) / n)
    se1 = math.sqrt(p1 * (1 - p1) / n)
    z = (abs(p1 - p0) - z_a * se0) / se1
    return norm_cdf(z)


def one_proportion_z_test(hits: int, n: int, p0: float, *, two_sided: bool = True) -> tuple[float, float]:
    """Standard one-proportion z-test: observed hit rate `hits/n` against
    chance rate `p0`. Returns (z, p_value)."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= hits <= n:
        raise ValueError("hits must be in [0, n]")
    if not 0.0 < p0 < 1.0:
        raise ValueError("p0 must be in (0,1)")
    p_hat = hits / n
    se = math.sqrt(p0 * (1 - p0) / n)
    z = (p_hat - p0) / se if se > 0 else 0.0
    p_value = 2.0 * (1.0 - norm_cdf(abs(z))) if two_sided else 1.0 - norm_cdf(z)
    return z, p_value


def _log_beta(x: float, y: float) -> float:
    return math.lgamma(x) + math.lgamma(y) - math.lgamma(x + y)


def binomial_bayes_factor(
    hits: int, n: int, p0: float, *, prior_a: float = 1.0, prior_b: float = 1.0
) -> tuple[float, float]:
    """Bayes factor for forced-choice/binomial data: H0 (point null, hit
    rate exactly p0) vs H1 (hit rate ~ Beta(prior_a, prior_b), the
    standard uninformative default being Beta(1,1) = uniform on (0,1)).

    This is the exact (not approximate) Beta-Binomial Bayes factor — a
    closed form, unlike `bic_bayes_factor`'s BIC approximation for the
    t-test case:

        BF10 = [B(hits+a, n-hits+b) / B(a,b)] / [p0^hits * (1-p0)^(n-hits)]

    where B is the Beta function. Computed in log-space via math.lgamma
    for numerical stability at large n. Reference: standard Bayesian
    binomial test, e.g. Kass & Raftery (1995), "Bayes Factors," JASA 90.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= hits <= n:
        raise ValueError("hits must be in [0, n]")
    if not 0.0 < p0 < 1.0:
        raise ValueError("p0 must be in (0,1)")
    misses = n - hits
    log_ml_h1 = _log_beta(hits + prior_a, misses + prior_b) - _log_beta(prior_a, prior_b)
    log_ml_h0 = hits * math.log(p0) + misses * math.log(1.0 - p0) if n > 0 else 0.0
    log_bf10 = log_ml_h1 - log_ml_h0
    bf10 = math.exp(log_bf10)
    bf01 = 1.0 / bf10 if bf10 > 0 else float("inf")
    return bf01, bf10


# ---------------------------------------------------------------------------
# Dicke N^2 scaling test design (the Mk3.0 G3 gate in docs/mk_ladder.md:
# "F7 + 2-emitter Dicke superradiance N^2 scaling test")
# ---------------------------------------------------------------------------
#
# Dicke superradiance (Dicke 1954, "Coherence in Spontaneous Radiation
# Processes," Phys. Rev. 93) is the textbook result that N independent
# (incoherent) emitters radiate INTENSITY proportional to N (their powers
# simply add), while N phase-locked (coherent) emitters radiate intensity
# proportional to N^2 (their field AMPLITUDES add, and intensity ~
# amplitude^2). The wiki's `Collective Consciousness` page and
# `docs/mk_ladder.md`'s Mk3.0 gate both invoke this specific N^2-vs-N
# distinction as the signature of genuine group coherence, as opposed to
# N independent practitioners producing no more than a simple sum.
#
# This section does NOT test whether that framework is correct. It answers
# a narrower, useful question: GIVEN that framework, and given an assumed
# single-source signal level and a measurement noise floor, how many
# replicate measurements are needed to statistically tell "N^2" apart from
# "N" at N=2 (the specific comparison the ladder names)? This reduces to a
# one-sample power-analysis problem: the two hypotheses make two different
# point predictions for the same measured quantity, and the "effect size"
# is how far apart those two predictions are relative to measurement noise
# -- so this reuses `required_n`/`achieved_power` above rather than
# inventing new statistical machinery.
#
# What this does NOT do: model any specific real detector's noise
# characteristics, response nonlinearity, or whether "intensity" is even
# the right measured quantity for whatever Mk3 actually measures (a field
# reading, a dyadic biometric-coherence metric, etc.). `noise_sd` and
# `baseline_intensity` must be supplied by the caller in whatever units
# the eventual real measurement uses -- this is a test-design calculator,
# not a physical simulation.


def dicke_scaling_effect_size(
    *, n_coherent: int = 2, n_baseline: int = 1, noise_sd: float, baseline_intensity: float = 1.0
) -> float:
    """Standardized effect size (Cohen's-d-equivalent) between the
    incoherent (intensity ~ N) and coherent/Dicke (intensity ~ N^2)
    predictions at `n_coherent` emitters, normalized so the incoherent
    model reproduces `baseline_intensity` at `n_baseline` emitters.

    d = |I_coherent(n_coherent) - I_incoherent(n_coherent)| / noise_sd
    """
    if n_baseline <= 0:
        raise ValueError("n_baseline must be positive")
    if n_coherent <= n_baseline:
        raise ValueError("n_coherent must be greater than n_baseline")
    if noise_sd <= 0:
        raise ValueError("noise_sd must be positive")
    if baseline_intensity <= 0:
        raise ValueError("baseline_intensity must be positive")

    per_source_intensity = baseline_intensity / n_baseline
    i_incoherent = n_coherent * per_source_intensity
    i_coherent = (n_coherent ** 2) * per_source_intensity
    return abs(i_coherent - i_incoherent) / noise_sd


def required_replicates_for_dicke_test(
    *,
    n_coherent: int = 2,
    n_baseline: int = 1,
    noise_sd: float,
    baseline_intensity: float = 1.0,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Minimum number of replicate measurements AT n_coherent emitters
    needed to distinguish the coherent (N^2) prediction from the
    incoherent (N) prediction at the given alpha/power, via
    `dicke_scaling_effect_size` fed into the existing one-sample
    `required_n` power calculation (same normal-approximation caveat at
    small N applies -- see `required_n`'s docstring)."""
    d = dicke_scaling_effect_size(
        n_coherent=n_coherent, n_baseline=n_baseline,
        noise_sd=noise_sd, baseline_intensity=baseline_intensity,
    )
    return required_n(d, alpha=alpha, power=power, design="one-sample")


def dicke_scaling_predictions(
    *, n_coherent: int = 2, n_baseline: int = 1, baseline_intensity: float = 1.0
) -> dict[str, float]:
    """The two competing point predictions at n_coherent emitters, for
    reporting alongside the required-replicates figure so a caller can see
    what's actually being distinguished, not just an abstract effect size."""
    if n_baseline <= 0:
        raise ValueError("n_baseline must be positive")
    per_source_intensity = baseline_intensity / n_baseline
    return {
        "incoherent_prediction": n_coherent * per_source_intensity,
        "coherent_dicke_prediction": (n_coherent ** 2) * per_source_intensity,
    }


# ---------------------------------------------------------------------------
# Approximate Bayes factor (BIC-based, Wagenmakers 2007 / Masson 2011)
# ---------------------------------------------------------------------------


def bic_bayes_factor(t_stat: float, n: int, *, df: int | None = None) -> tuple[float, float]:
    """BIC-based approximation to BF01, BF10 for a one-sample/paired
    t-test with observed t-statistic `t_stat` and sample size `n`.

        BF01 ~= sqrt(n) * (1 + t^2/df)^(-n/2),   df = n-1 by default

    Reference: Wagenmakers (2007), "A practical solution to the
    pervasive problems of p values," Psychonomic Bulletin & Review
    14(5); Masson (2011), "A tutorial on a practical Bayesian
    alternative to null-hypothesis significance testing," Behavior
    Research Methods 43.

    This is an APPROXIMATION, not the exact Rouder et al. (2009) JZS
    Bayes factor. Do not quote it as a precise Bayes factor in a
    publication without cross-checking against an exact implementation.
    """
    if df is None:
        df = n - 1
    if df <= 0:
        raise ValueError("df must be positive (need n >= 2)")
    bf01 = math.sqrt(n) * (1.0 + (t_stat ** 2) / df) ** (-n / 2.0)
    bf10 = 1.0 / bf01 if bf01 > 0 else float("inf")
    return bf01, bf10


def _jeffreys_label(bf_favoring: float) -> str:
    """Jeffreys (1961) verbal categories for a Bayes factor >= 1."""
    if bf_favoring < 1.0:
        return "essentially no evidence"
    if bf_favoring < 3.0:
        return "anecdotal"
    if bf_favoring < 10.0:
        return "moderate"
    if bf_favoring < 30.0:
        return "strong"
    if bf_favoring < 100.0:
        return "very strong"
    return "decisive"


def interpret_bayes_factor(bf10: float) -> str:
    """Human-readable Jeffreys (1961) interpretation of BF10."""
    if bf10 >= 1.0:
        return f"{_jeffreys_label(bf10)} evidence for H1 (an effect) — BF10={bf10:.3g}"
    bf01 = 1.0 / bf10 if bf10 > 0 else float("inf")
    return f"{_jeffreys_label(bf01)} evidence for H0 (the null) — BF01={bf01:.3g}"


def t_stat_from_summary(mean_diff: float, sd_diff: float, n: int) -> float:
    """Paired/one-sample t-statistic from summary statistics."""
    if sd_diff <= 0:
        raise ValueError("sd_diff must be positive")
    if n < 2:
        raise ValueError("n must be >= 2")
    return mean_diff / (sd_diff / math.sqrt(n))


# ---------------------------------------------------------------------------
# Pre-registration lock
# ---------------------------------------------------------------------------

_PREREG_REQUIRED_KEYS = (
    "hypothesis",
    "primary_endpoint",
    "effect_size_d",
    "alpha",
    "power",
    "design",
)


def build_preregistration(spec: dict) -> dict:
    """Validate a pre-registration spec, compute its required N, and
    return a locked (hashed, timestamped) document. Does not write to
    disk — see `write_preregistration` / the `preregister` CLI
    subcommand for that.
    """
    missing = [k for k in _PREREG_REQUIRED_KEYS if k not in spec]
    if missing:
        raise ValueError(f"preregistration spec missing required keys: {missing}")

    n_needed = required_n(
        float(spec["effect_size_d"]),
        alpha=float(spec["alpha"]),
        power=float(spec["power"]),
        design=str(spec["design"]),
        two_sided=bool(spec.get("two_sided", True)),
    )

    doc = dict(spec)
    doc["required_n"] = n_needed
    doc["locked_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    doc["tool"] = "tools/experiment_design.py"

    payload = json.dumps(doc, indent=2, sort_keys=True)
    doc["lock_hash_sha256"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return doc


def write_preregistration(spec: dict, out_path: str | Path) -> dict:
    """Build and write a locked preregistration. Refuses to overwrite an
    existing lock file (pre-registrations are append-only artifacts —
    if you need to change one, write a new dated file, don't edit the
    old one)."""
    out_path = Path(out_path)
    if out_path.exists():
        raise FileExistsError(
            f"{out_path} already exists — pre-registrations are immutable "
            "once locked. Write a new dated file instead of overwriting."
        )
    doc = build_preregistration(spec)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return doc


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cmd_power(args: argparse.Namespace) -> int:
    if args.n is not None:
        p = achieved_power(
            args.n, args.d, alpha=args.alpha, design=args.design,
            two_sided=not args.one_sided,
        )
        result = {"n": args.n, "effect_size_d": args.d, "alpha": args.alpha,
                  "design": args.design, "achieved_power": p}
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"At n={args.n}, d={args.d}, alpha={args.alpha}, design={args.design}: "
                  f"achieved power = {p:.3f}")
        return 0

    n = required_n(
        args.d, alpha=args.alpha, power=args.power, design=args.design,
        two_sided=not args.one_sided,
    )
    result = {"effect_size_d": args.d, "alpha": args.alpha, "power": args.power,
              "design": args.design, "required_n": n}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        unit = "per group" if args.design == "two-sample" else "subjects"
        print(f"For d={args.d}, alpha={args.alpha}, power={args.power}, design={args.design}: "
              f"required N = {n} {unit} "
              f"(normal approximation — add margin for N<20; see docstring).")
    return 0


def _cmd_bayes(args: argparse.Namespace) -> int:
    if args.t is not None:
        t_stat = args.t
    else:
        if args.mean_diff is None or args.sd_diff is None:
            print("experiment_design bayes: need --t, or --mean-diff and --sd-diff",
                  file=sys.stderr)
            return 3
        t_stat = t_stat_from_summary(args.mean_diff, args.sd_diff, args.n)

    bf01, bf10 = bic_bayes_factor(t_stat, args.n, df=args.df)
    result = {
        "t_stat": t_stat, "n": args.n, "df": args.df or (args.n - 1),
        "bf01": bf01, "bf10": bf10, "interpretation": interpret_bayes_factor(bf10),
        "method": "BIC approximation (Wagenmakers 2007) -- not exact JZS",
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"t={t_stat:.4f}, n={args.n}, df={result['df']}")
        print(f"BF10 = {bf10:.4g}   BF01 = {bf01:.4g}")
        print(interpret_bayes_factor(bf10))
        print("(BIC approximation, not exact JZS -- see docstring.)")
    return 0


def _cmd_binom(args: argparse.Namespace) -> int:
    if args.preset is not None:
        if args.p1 is not None:
            print("experiment_design binom: --preset and --p1 are mutually exclusive.",
                  file=sys.stderr)
            return 3
        args.p1 = GANZFELD_HIT_RATE_PRESETS[args.preset]

    if args.hits is not None:
        z, p_value = one_proportion_z_test(args.hits, args.n, args.p0, two_sided=not args.one_sided)
        bf01, bf10 = binomial_bayes_factor(args.hits, args.n, args.p0)
        result = {
            "hits": args.hits, "n": args.n, "p0": args.p0, "p_hat": args.hits / args.n,
            "z": z, "p_value": p_value, "bf01": bf01, "bf10": bf10,
            "interpretation": interpret_bayes_factor(bf10),
        }
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"hits={args.hits}/{args.n} (p_hat={result['p_hat']:.4f}) vs chance p0={args.p0}")
            print(f"z={z:.4f}  p={p_value:.4g}")
            print(f"BF10={bf10:.4g}  BF01={bf01:.4g}  -- {interpret_bayes_factor(bf10)}")
        return 0

    if args.n is not None:
        power = achieved_power_binomial(args.n, args.p1, p0=args.p0, alpha=args.alpha,
                                          two_sided=not args.one_sided)
        result = {"n": args.n, "p0": args.p0, "p1": args.p1, "alpha": args.alpha, "achieved_power": power}
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"At n={args.n} trials, p0={args.p0}, p1={args.p1}, alpha={args.alpha}: "
                  f"achieved power = {power:.3f}")
        return 0

    n = required_n_binomial(args.p1, p0=args.p0, alpha=args.alpha, power=args.power,
                              two_sided=not args.one_sided)
    result = {"p0": args.p0, "p1": args.p1, "alpha": args.alpha, "power": args.power, "required_n": n}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"For chance p0={args.p0}, target hit rate p1={args.p1}, alpha={args.alpha}, "
              f"power={args.power}: required N = {n} trials.")
    return 0


def _cmd_dicke(args: argparse.Namespace) -> int:
    try:
        n_replicates = required_replicates_for_dicke_test(
            n_coherent=args.n_coherent, n_baseline=args.n_baseline,
            noise_sd=args.noise_sd, baseline_intensity=args.baseline_intensity,
            alpha=args.alpha, power=args.power,
        )
        predictions = dicke_scaling_predictions(
            n_coherent=args.n_coherent, n_baseline=args.n_baseline,
            baseline_intensity=args.baseline_intensity,
        )
    except ValueError as exc:
        print(f"experiment_design dicke-scaling: {exc}", file=sys.stderr)
        return 3

    result = {
        "n_baseline": args.n_baseline, "n_coherent": args.n_coherent,
        "noise_sd": args.noise_sd, "baseline_intensity": args.baseline_intensity,
        "alpha": args.alpha, "power": args.power,
        "required_replicates": n_replicates, **predictions,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"At N={args.n_coherent} (baseline N={args.n_baseline}, intensity={args.baseline_intensity}):")
        print(f"  incoherent (~N) prediction:      {predictions['incoherent_prediction']:.4g}")
        print(f"  coherent/Dicke (~N^2) prediction: {predictions['coherent_dicke_prediction']:.4g}")
        print(f"  measurement noise SD:             {args.noise_sd:.4g}")
        print(f"Required replicate measurements at N={args.n_coherent} to distinguish these "
              f"at alpha={args.alpha}, power={args.power}: {n_replicates}")
        print("(Statistical test-design only -- see module docstring for what this does not model.)")
    return 0


def _cmd_preregister(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"experiment_design preregister: spec file not found: {spec_path}",
              file=sys.stderr)
        return 2
    text = spec_path.read_text(encoding="utf-8")
    spec = yaml.safe_load(text) if spec_path.suffix in (".yml", ".yaml") else json.loads(text)

    try:
        doc = write_preregistration(spec, args.out)
    except (ValueError, FileExistsError) as exc:
        print(f"experiment_design preregister: {exc}", file=sys.stderr)
        return 2

    print(f"Locked pre-registration written to {args.out}")
    print(f"  required_n = {doc['required_n']}")
    print(f"  lock_hash_sha256 = {doc['lock_hash_sha256']}")
    return 0


def _cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="experiment_design.py",
        description="Power analysis, approximate Bayes factors, and pre-registration locking.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pw = sub.add_parser("power", help="Required N for a target power, or achieved power at a given N.")
    pw.add_argument("--d", type=float, required=True, help="Standardized effect size (Cohen's d).")
    pw.add_argument("--alpha", type=float, default=0.05)
    pw.add_argument("--power", type=float, default=0.80, help="Target power (ignored if --n given).")
    pw.add_argument("--n", type=float, default=None, help="If given, compute achieved power instead of required N.")
    pw.add_argument("--design", choices=_DESIGNS, default="paired")
    pw.add_argument("--one-sided", action="store_true")
    pw.add_argument("--json", action="store_true")
    pw.set_defaults(func=_cmd_power)

    bf = sub.add_parser("bayes", help="Approximate (BIC) Bayes factor for a one-sample/paired t-test.")
    bf.add_argument("--t", type=float, default=None, help="Observed t-statistic.")
    bf.add_argument("--mean-diff", type=float, default=None, help="Alternative to --t: mean of paired differences.")
    bf.add_argument("--sd-diff", type=float, default=None, help="Alternative to --t: SD of paired differences.")
    bf.add_argument("--n", type=int, required=True)
    bf.add_argument("--df", type=int, default=None)
    bf.add_argument("--json", action="store_true")
    bf.set_defaults(func=_cmd_bayes)

    bn = sub.add_parser("binom", help="Forced-choice/binomial design: required N, achieved power, or score observed hits.")
    bn.add_argument("--p0", type=float, required=True, help="Chance hit rate (e.g. 0.25 for 4-alternative forced choice).")
    bn.add_argument("--p1", type=float, default=None, help="Hypothesized true hit rate (for --n or planning mode).")
    bn.add_argument("--preset", choices=sorted(GANZFELD_HIT_RATE_PRESETS), default=None,
                     help="Use a literature-grounded p1 instead of a hand-typed one "
                          "(see docs/psionic_engineering/literature_grounding.md). "
                          "Mutually exclusive with --p1.")
    bn.add_argument("--alpha", type=float, default=0.05)
    bn.add_argument("--power", type=float, default=0.80, help="Target power (ignored if --n or --hits given).")
    bn.add_argument("--n", type=int, default=None, help="Trial count. With --p1 and no --hits: compute achieved power.")
    bn.add_argument("--hits", type=int, default=None, help="Observed hit count -- scores this result instead of planning.")
    bn.add_argument("--one-sided", action="store_true")
    bn.add_argument("--json", action="store_true")
    bn.set_defaults(func=_cmd_binom)

    dk = sub.add_parser("dicke-scaling",
                         help="Mk3.0 G3 gate test design: replicates needed to distinguish N^2 (coherent) from N (incoherent) scaling.")
    dk.add_argument("--n-baseline", type=int, default=1, help="Baseline emitter count (default 1).")
    dk.add_argument("--n-coherent", type=int, default=2, help="Emitter count under test (default 2, per the Mk3.0 gate).")
    dk.add_argument("--noise-sd", type=float, required=True, help="Measurement noise SD, same units as --baseline-intensity.")
    dk.add_argument("--baseline-intensity", type=float, default=1.0, help="Measured intensity at n-baseline emitters (default 1.0, i.e. normalized units).")
    dk.add_argument("--alpha", type=float, default=0.05)
    dk.add_argument("--power", type=float, default=0.80)
    dk.add_argument("--json", action="store_true")
    dk.set_defaults(func=_cmd_dicke)

    pr = sub.add_parser("preregister", help="Lock a pre-registration spec (YAML/JSON) to a hashed, timestamped file.")
    pr.add_argument("--spec", required=True, help="Path to a YAML or JSON spec file.")
    pr.add_argument("--out", required=True, help="Output path for the locked pre-registration (must not already exist).")
    pr.set_defaults(func=_cmd_preregister)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
