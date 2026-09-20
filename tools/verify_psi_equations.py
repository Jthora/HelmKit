#!/usr/bin/env python3
"""
verify_psi_equations.py — independent numerical check of the FusionGirl
wiki's "Psionic Engineering" master-equation math and worked examples.

Design doc: docs/psionic_engineering/computational_toolkit.md

What this tool does NOT do: it does not evaluate whether the psi field
is real. That is an empirical question outside the scope of a math
checker.

What it DOES do: it evaluates whether the wiki's OWN stated formulas are
internally consistent — whether a claimed closed-form solution actually
satisfies the claimed PDE, and whether the wiki's own worked numerical
examples reproduce under independent recomputation from the wiki's own
stated inputs. A framework can be wrong about physics and still be
internally consistent, or right about physics and still contain
arithmetic slips; this tool only checks the latter axis.

Two check families:

  1. PDE residual checks (Branch A — Field Engineering Foundation).
     Instantiate a claimed closed-form ansatz on a numerical grid, apply
     the claimed differential operator via central finite differences,
     and confirm the residual vanishes only at the claimed parameter
     value (and grows if that value is perturbed — this rules out the
     check being vacuously satisfied by the finite-difference scheme
     itself).

  2. Worked-example recomputation (Branch D1 — Bifilar Coil Engineering).
     Re-derive every concrete number on that page from its own stated
     inputs, using the same formulas the page states, and flag any
     mismatch against the page's own stated output.

Stdlib only. No numpy, no scipy, no sympy — see tools/requirements.txt
and the same discipline in tools/analyze_g2.py.

Exit codes:
    0 — all checks passed
    1 — at least one check flagged a discrepancy
    3 — usage error
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str
    source: str            # wiki page this check is against
    method: str = "numeric"  # "numeric" (independently computed) or
                              # "citation" (standard textbook result,
                              # not independently re-derived here —
                              # carries less evidentiary weight)


# ---------------------------------------------------------------------------
# Family 1: PDE residual checks (Branch A — Field Engineering Foundation)
# ---------------------------------------------------------------------------


def check_dispersion_relation(
    *, k: float = 2.0, m: float = 0.7, h: float = 1e-4
) -> CheckResult:
    """
    Wiki claim (Psi Dispersion Relations / Psionic Engineering hub §Key
    Equations): linearizing Box(psi) - m_eff^2 psi = 0 around a plane
    wave psi = cos(kx - omega t) requires omega^2 = k^2 + m_eff^2.

    Independent check: build psi(x,t) on a numerical grid at a
    CANDIDATE omega, take the discrete d'Alembertian-minus-mass-term via
    central finite differences, and confirm the residual vanishes only
    when the candidate omega equals sqrt(k^2+m^2) — not merely that it
    is small for any omega (which would mean the check is vacuous).
    """
    omega_claimed = math.sqrt(k * k + m * m)

    def psi(x: float, t: float, omega: float) -> float:
        return math.cos(k * x - omega * t)

    def residual(omega: float, x0: float = 0.31, t0: float = 0.17) -> float:
        # -d^2/dt^2 psi + d^2/dx^2 psi - m^2 psi  (mostly-plus signature;
        # the zero-crossing condition is convention-independent — see
        # docstring of the sibling Yukawa check for the other sign).
        d2t = (psi(x0, t0 + h, omega) - 2 * psi(x0, t0, omega) + psi(x0, t0 - h, omega)) / h**2
        d2x = (psi(x0 + h, t0, omega) - 2 * psi(x0, t0, omega) + psi(x0 - h, t0, omega)) / h**2
        return -d2t + d2x - m * m * psi(x0, t0, omega)

    resid_at_claimed = residual(omega_claimed)
    resid_at_perturbed = residual(omega_claimed * 1.05)  # +5% off claimed value

    passed = (
        abs(resid_at_claimed) < 1e-3
        and abs(resid_at_perturbed) > abs(resid_at_claimed) * 5
    )
    detail = (
        f"omega_claimed = sqrt(k^2+m^2) = sqrt({k}^2+{m}^2) = {omega_claimed:.6f}; "
        f"PDE residual at claimed omega = {resid_at_claimed:.2e} (expect ~0); "
        f"residual at omega+5% = {resid_at_perturbed:.2e} (expect notably larger, "
        f"confirming the check is not vacuous)"
    )
    return CheckResult(
        name="dispersion_relation_omega2_eq_k2_plus_m2",
        passed=passed,
        detail=detail,
        source="Psi Dispersion Relations (Branch A3) / Psionic Engineering hub",
    )


def check_yukawa_screening(
    *, G: float = 1.0, M: float = 1.0, m: float = 0.5, h: float = 1e-4
) -> CheckResult:
    """
    Wiki claim (Psi Boundary Conditions / hub §Key Equations):
        psi(r) = -(G_psi M_psi / r) * exp(-m_eff r)
    solves (Laplacian - m_eff^2) psi = 0 for r > 0 (away from the point
    source at the origin), with coherence length L_psi = 1/m_eff.

    Independent check: evaluate the claimed closed form on a 1-D radial
    grid, compute the radial Laplacian f'' + (2/r)f' by central finite
    differences, and confirm (Laplacian - m^2) psi ~= 0 at several radii
    r > 0.
    """

    def psi(r: float) -> float:
        return -(G * M / r) * math.exp(-m * r)

    def radial_laplacian(r: float) -> float:
        f_p, f_0, f_m = psi(r + h), psi(r), psi(r - h)
        d2f = (f_p - 2 * f_0 + f_m) / h**2
        df = (f_p - f_m) / (2 * h)
        return d2f + (2.0 / r) * df

    radii = [1.0, 2.0, 3.5, 5.0]
    rel_residuals = []
    for r in radii:
        lap = radial_laplacian(r)
        resid = lap - m * m * psi(r)
        rel_residuals.append(abs(resid / psi(r)))

    max_rel_resid = max(rel_residuals)
    passed = max_rel_resid < 1e-3
    detail = (
        f"Yukawa ansatz psi(r) = -GM/r * exp(-m r), checked at r={radii}: "
        f"max |relative PDE residual| = {max_rel_resid:.2e} (expect ~0 for r>0). "
        f"Coherence length L_psi = 1/m = {1.0/m:.4f} (matches wiki's L_psi=1/m_eff)."
    )
    return CheckResult(
        name="yukawa_static_solution_coherence_length",
        passed=passed,
        detail=detail,
        source="Psi Boundary Conditions (Branch A5) / Psionic Engineering hub Key Equations",
    )


def check_retarded_greens_function() -> CheckResult:
    """
    Wiki claim (Psi Green's Functions / hub §Key Equations): the massless
    retarded Green's function is
        G_ret(x,x') = delta(t - t' - |r-r'|) / (4 pi |r-r'|).

    This is a standard distributional identity (the free-space retarded
    Green's function of the wave equation Box G = delta^4(x-x')) — the
    same result as Jackson, "Classical Electrodynamics," 3rd ed., eq.
    6.44. It is not independently re-derived here (finite-difference
    methods cannot cleanly evaluate a delta-function source); flagged as
    a citation check rather than a numeric one so callers can weight it
    accordingly.
    """
    return CheckResult(
        name="retarded_greens_function_massless_limit",
        passed=True,
        detail=(
            "Standard result — matches the free-space retarded Green's "
            "function of the wave equation (cf. Jackson 3rd ed. eq. 6.44). "
            "Not independently numerically re-derived (delta-function "
            "source is not amenable to finite-difference verification)."
        ),
        source="Psi Green's Functions (Branch A6) / Psionic Engineering hub Key Equations",
        method="citation",
    )


def check_impedance_analogy() -> CheckResult:
    """
    Wiki claim (Psi Impedance Theory / hub §Key Equations):
        Z_psi = psi_field_amplitude / J_psi_source_density = 1/(omega * chi_psi)
    presented as analogous to EM wave impedance Z = sqrt(mu/eps) = 377 ohm.

    Consistency check (dimensional/structural, not numeric): EM wave
    impedance Z=sqrt(mu/eps) is a ratio of field STORAGE parameters and
    is frequency-independent for a lossless medium. The wiki's own
    Z_psi = 1/(omega chi_psi) is explicitly frequency-DEPENDENT (an
    admittance-like quantity, structurally closer to a capacitive
    reactance 1/(omega C) than to sqrt(mu/eps)). The two formulas do not
    reduce to one another in any limit shown on the page. This does not
    make Z_psi wrong — it means the "established analog" framing
    overstates how tight the analogy is; the page would be more accurate
    calling Z=sqrt(mu/eps) an inspiration for the NAME "impedance," not
    a limiting case of the same formula.
    """
    return CheckResult(
        name="psi_impedance_vs_em_wave_impedance_analogy",
        passed=False,
        detail=(
            "Z_psi = 1/(omega*chi_psi) is frequency-dependent (reactance-"
            "like); Z_EM = sqrt(mu/eps) is frequency-independent for a "
            "lossless medium. No limit shown on the page reduces one to "
            "the other — the 'established analog' is a naming inspiration, "
            "not a mathematical limiting case. Flagged as an overstated "
            "analogy, not an arithmetic error."
        ),
        source="ψ Impedance Theory (Branch A4) / Psionic Engineering hub Key Equations",
        method="citation",
    )


# ---------------------------------------------------------------------------
# Family 2: worked-example recomputation (Bifilar Coil Engineering, D1)
# ---------------------------------------------------------------------------

_MU0 = 4 * math.pi * 1e-7  # vacuum permeability, H/m


def check_bifilar_efield_peak(
    *, v_drive: float = 200.0, d_gap_m: float = 0.2e-3
) -> CheckResult:
    """Wiki: E_peak = V_drive / d_gap = 200V / 0.2mm = 1 MV/m."""
    e_peak = v_drive / d_gap_m
    claimed = 1.0e6
    rel_err = abs(e_peak - claimed) / claimed
    return CheckResult(
        name="bifilar_efield_peak",
        passed=rel_err < 0.01,
        detail=(
            f"E_peak = V/d = {v_drive}/{d_gap_m} = {e_peak:.4e} V/m "
            f"(wiki states {claimed:.0e} V/m; rel. err {rel_err:.2%})"
        ),
        source="Bifilar Coil Engineering (Branch D1)",
    )


def check_bifilar_farfield_falloff(
    *, d_gap_m: float = 0.2e-3, e_peak: float = 1.0e6
) -> CheckResult:
    """
    Wiki: E(r) ~= E_peak * (d_gap / 2r)^2 for r >> d_gap, with a stated
    falloff table at r = 1, 10, 100, 200 mm. (The r=0.5mm "transition"
    row is explicitly NOT claimed to follow this asymptotic formula —
    excluded here, not silently dropped.)
    """
    table_mm = [1.0, 10.0, 100.0, 200.0]
    claimed_v_per_m = [10_000.0, 100.0, 1.0, 0.25]
    mismatches = []
    computed = []
    for r_mm, claimed in zip(table_mm, claimed_v_per_m):
        r_m = r_mm / 1000.0
        e_r = e_peak * (d_gap_m / (2 * r_m)) ** 2
        computed.append(e_r)
        rel_err = abs(e_r - claimed) / claimed
        if rel_err > 0.02:
            mismatches.append((r_mm, e_r, claimed, rel_err))

    passed = not mismatches
    detail = (
        f"E(r)=E_peak*(d_gap/2r)^2 recomputed at r={table_mm}mm -> "
        f"{[f'{v:.3g}' for v in computed]} V/m vs wiki {claimed_v_per_m} V/m. "
        + ("All match within 2%." if passed else f"Mismatches: {mismatches}")
    )
    return CheckResult(
        name="bifilar_farfield_efield_falloff_table",
        passed=passed,
        detail=detail,
        source="Bifilar Coil Engineering (Branch D1) — E-Field Falloff Profile table",
    )


def check_bifilar_bfield_cancellation(
    *, i_peak: float = 100.0, r_m: float = 0.1, cancel_factor: float = 500.0,
    icnirp_limit_uT: float = 27.0,
) -> CheckResult:
    """
    Wiki: single-trace near-field B at r=10cm from I=100A, then divide
    by the stated bifilar cancellation factor of 500x -> 0.4 uT, vs.
    ICNIRP 27 uT reference level.
    """
    b_single = _MU0 * i_peak / (2 * math.pi * r_m)  # tesla
    b_single_uT = b_single * 1e6
    b_bifilar_uT = b_single_uT / cancel_factor

    claimed_single_uT = 200.0
    claimed_bifilar_uT = 0.4
    err_single = abs(b_single_uT - claimed_single_uT) / claimed_single_uT
    err_bifilar = abs(b_bifilar_uT - claimed_bifilar_uT) / claimed_bifilar_uT

    passed = err_single < 0.02 and err_bifilar < 0.02 and b_bifilar_uT < icnirp_limit_uT
    detail = (
        f"B_single = mu0*I/(2*pi*r) = {b_single_uT:.2f} uT (wiki: {claimed_single_uT} uT); "
        f"B_bifilar = B_single/{cancel_factor:.0f} = {b_bifilar_uT:.3f} uT "
        f"(wiki: {claimed_bifilar_uT} uT); ICNIRP limit {icnirp_limit_uT} uT -> "
        f"margin {icnirp_limit_uT / b_bifilar_uT:.0f}x (wiki claims 67x)"
    )
    return CheckResult(
        name="bifilar_bfield_cancellation_and_icnirp_margin",
        passed=passed,
        detail=detail,
        source="Bifilar Coil Engineering (Branch D1) — B-Field Assessment",
    )


def check_bifilar_adiabatic_pulse(
    *,
    p_peak_w: float = 20_000.0,
    tau_s: float = 1e-6,
    rho_cp: float = 3.44e6,  # J/(m^3*K), copper volumetric heat capacity
    v_trace_m3: float = 6e-13,
) -> CheckResult:
    """
    Wiki: 'At tau_pulse = 1 us: Delta_T = 20000 x 10^-6 / (3.44x10^6 x
    6x10^-13) = 9.7 C per pulse.'

    Independent recomputation of that exact expression, using the wiki's
    own stated P_peak (20 kW — the FULL 10-metre trace's dissipated
    power), tau, rho*cp, and the STATED per-segment trace volume (for a
    1mm-long, 0.3mm-wide, 2 um trace segment).
    """
    delta_t_literal = p_peak_w * tau_s / (rho_cp * v_trace_m3)
    claimed = 9.7
    rel_err = abs(delta_t_literal - claimed) / claimed

    # Root-cause probe: does substituting AVERAGE power (P_peak * duty
    # cycle, the page's own 0.1% figure from its immediately-preceding
    # paragraph) for the labeled "P_peak" reproduce the wiki's stated
    # answer exactly? If so, that's a much sharper diagnosis than "off
    # by 1000x, cause unknown" -- it pinpoints exactly which quantity
    # got swapped for which.
    duty_cycle = 0.001
    p_avg_w = p_peak_w * duty_cycle
    delta_t_using_avg = p_avg_w * tau_s / (rho_cp * v_trace_m3)
    avg_substitution_matches = abs(delta_t_using_avg - claimed) / claimed < 0.01

    passed = rel_err < 0.05
    detail = (
        f"Delta_T = P_peak*tau/(rho*cp*V) = {p_peak_w}*{tau_s}/"
        f"({rho_cp:.2e}*{v_trace_m3:.1e}) = {delta_t_literal:.1f} degC "
        f"(wiki states {claimed} degC per pulse)."
    )
    if not passed:
        detail += (
            " DISCREPANCY: literally plugging the wiki's own stated "
            f"P_peak (the FULL trace's 20kW instantaneous dissipation) "
            "into this formula against a single 1mm SEGMENT's volume "
            "gives a result ~1000x larger than the wiki's stated answer."
        )
        if avg_substitution_matches:
            detail += (
                f" ROOT CAUSE IDENTIFIED: substituting AVERAGE power "
                f"P_avg = P_peak * duty_cycle = {p_avg_w:.0f} W (the page's "
                f"own 0.1% duty-cycle figure, stated one paragraph earlier) "
                f"for the formula's labeled P_peak reproduces {delta_t_using_avg:.2f} "
                f"degC — matching the wiki's stated 9.7 degC almost exactly. "
                "This strongly suggests the page swapped average power for "
                "peak power when computing this specific number, not a random "
                "arithmetic slip. Whether the PHYSICALLY correct quantity for "
                "a per-pulse transient-heating calculation is P_peak (as the "
                "formula's own variable name says) or P_avg (which is what "
                "actually produces the page's stated answer) is a real "
                "modeling question for the wiki maintainers, not something "
                "resolved here — but the arithmetic source of the "
                "discrepancy is now pinned down precisely."
            )
        else:
            detail += (
                " Average-power substitution does not reproduce the stated "
                "answer either -- root cause not identified; flagged for the "
                "wiki maintainers or independent thermal FEA."
            )
    return CheckResult(
        name="bifilar_adiabatic_pulse_temperature_rise",
        passed=passed,
        detail=detail,
        source="Bifilar Coil Engineering (Branch D1) — Pulsed Drive Constraint",
    )


def check_bifilar_average_power_consistency(
    *, p_peak_w: float = 20_000.0, duty_cycle: float = 0.001
) -> CheckResult:
    """
    The wiki page states TWO different numbers for the same quantity
    (average pulsed drive power) in two different sections:

      Body text (Pulsed Drive Constraint): 'average dissipation =
        20 W x 0.001 = 20 mW per metre of trace.'
      Sanity-check table (TML Measurement Protocol): 'Average drive
        power: 20 kW peak x 0.1% duty cycle = 20 W average -> within
        wearable budget.'

    Straightforward average = P_peak * duty_cycle, using the page's OWN
    stated P_peak = 20 kW, gives 20 W — matching the sanity-check table
    and CONTRADICTING the body-text's 20 mW figure. This is an internal
    inconsistency within a single wiki page, not a disagreement with
    this repo's own numbers.
    """
    avg_w = p_peak_w * duty_cycle
    body_text_claim_w = 0.020   # "20 mW"
    sanity_table_claim_w = 20.0  # "20 W"

    matches_sanity_table = abs(avg_w - sanity_table_claim_w) / sanity_table_claim_w < 0.02
    matches_body_text = abs(avg_w - body_text_claim_w) / body_text_claim_w < 0.02

    detail = (
        f"average = P_peak * duty_cycle = {p_peak_w}W * {duty_cycle} = {avg_w:.3f} W. "
        f"Matches sanity-check table's '20 W average': {matches_sanity_table}. "
        f"Matches body text's '20 mW per metre of trace': {matches_body_text}. "
    )
    if matches_sanity_table and not matches_body_text:
        detail += (
            "The wiki page contradicts itself: the body text's 20 mW figure "
            "is 1000x smaller than what its own stated P_peak x duty_cycle "
            "arithmetic (and its own later sanity-check table) produces."
        )
    # `passed` is deliberately always False here: this check exists to
    # SURFACE a found internal inconsistency (two different numbers for
    # the same quantity on the same wiki page), not to pass/fail a
    # single recomputed value. See `detail` for the actual finding.
    return CheckResult(
        name="bifilar_average_power_internal_consistency",
        passed=False,
        detail=detail,
        source="Bifilar Coil Engineering (Branch D1) — internal consistency",
    )


def check_shepard_tone_carrier_frequency_consistency() -> CheckResult:
    """
    Cross-page consistency check, found while triaging scan_wiki_consistency.py's
    output (its within-page heuristic flagged this but it's actually a
    genuine CROSS-page discrepancy — the Psionic Engineering hub's Branch D
    table doesn't live inside an Infobox, so the corpus-wide scanner's
    Infobox-only extraction can't see it; this is hand-curated instead).

    The `Psionic Engineering` hub's Branch D summary table states:
        "DSP implementation: 3 carriers (10, 20, 40 kHz), raised-cosine
        envelopes, geometric spacing"

    The `Shepard Tone Synthesis` page itself (the detailed, derived page
    this hub row summarizes) consistently and repeatedly states three
    carriers at f0=40, 2f0=80, 4f0=160 kHz, with detailed justification
    (FPGA clock-division exactness at 160 MHz, harmonic subordination to
    a 1.5 MHz PZT resonance as the 37th harmonic of 40 kHz, etc.).

    These are two different stated frequency triples for the same design
    element. The Shepard Tone Synthesis page's numbers are load-bearing
    (multiple derivations depend on them); the hub's "10, 20, 40 kHz" is
    a passing summary-table mention with no supporting derivation shown
    on that page. This is not independently computed/verified here (it's
    a direct quote comparison, not arithmetic) -- flagged as a citation
    consistency check, not a numeric one.
    """
    return CheckResult(
        name="shepard_tone_carrier_frequency_cross_page_consistency",
        passed=False,
        detail=(
            "Psionic Engineering hub (Branch D table) states carriers at "
            "10, 20, 40 kHz. Shepard Tone Synthesis's own page states "
            "40, 80, 160 kHz (f0, 2f0, 4f0), with detailed supporting "
            "derivation (FPGA clock division, PZT harmonic subordination) "
            "that only works out for the 40/80/160 triple. The hub's "
            "'10, 20, 40 kHz' mention appears to be a stale summary that "
            "was not updated when the detailed page was written -- "
            "recommend the hub table be corrected to match the derived page."
        ),
        source="Psionic Engineering hub (Branch D) vs Shepard Tone Synthesis (D2)",
        method="citation",
    )


ALL_CHECKS = [
    check_dispersion_relation,
    check_yukawa_screening,
    check_retarded_greens_function,
    check_impedance_analogy,
    check_bifilar_efield_peak,
    check_bifilar_farfield_falloff,
    check_bifilar_bfield_cancellation,
    check_bifilar_adiabatic_pulse,
    check_bifilar_average_power_consistency,
    check_shepard_tone_carrier_frequency_consistency,
]


def run_all() -> list[CheckResult]:
    return [fn() for fn in ALL_CHECKS]


def format_report(results: list[CheckResult]) -> str:
    out = ["Psi Equation / Worked-Example Verification Report", "=" * 60, ""]
    n_pass = sum(1 for r in results if r.passed)
    for r in results:
        tag = "PASS" if r.passed else "FLAG"
        out.append(f"[{tag}] ({r.method}) {r.name}")
        out.append(f"       source: {r.source}")
        out.append(f"       {r.detail}")
        out.append("")
    out.append("-" * 60)
    out.append(f"{n_pass}/{len(results)} checks passed without a flagged discrepancy.")
    out.append(
        "Note: a 'FLAG' on a citation-method check (e.g. the impedance "
        "analogy) means the analogy is looser than presented, not that "
        "the underlying formula is arithmetically wrong."
    )
    return "\n".join(out)


def results_to_json(results: list[CheckResult]) -> dict:
    return {
        "checks": [
            {
                "name": r.name,
                "passed": r.passed,
                "method": r.method,
                "source": r.source,
                "detail": r.detail,
            }
            for r in results
        ],
        "n_pass": sum(1 for r in results if r.passed),
        "n_total": len(results),
    }


def _cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="verify_psi_equations.py",
        description=(
            "Independent numerical check of the wiki's Psionic Engineering "
            "master-equation math and the Bifilar Coil Engineering worked "
            "examples."
        ),
    )
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = p.parse_args(argv)

    results = run_all()
    if args.json:
        print(json.dumps(results_to_json(results), indent=2, sort_keys=True))
    else:
        print(format_report(results))

    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
