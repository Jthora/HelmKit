"""Unit tests for tools/verify_psi_equations.py."""

from __future__ import annotations

import unittest

from tools.verify_psi_equations import (
    ALL_CHECKS,
    check_bifilar_adiabatic_pulse,
    check_bifilar_average_power_consistency,
    check_bifilar_bfield_cancellation,
    check_bifilar_efield_peak,
    check_bifilar_farfield_falloff,
    check_dispersion_relation,
    check_impedance_analogy,
    check_retarded_greens_function,
    check_shepard_tone_carrier_frequency_consistency,
    check_yukawa_screening,
    format_report,
    results_to_json,
    run_all,
)


class DispersionRelationTests(unittest.TestCase):

    def test_correct_omega_has_near_zero_residual(self) -> None:
        r = check_dispersion_relation(k=2.0, m=0.7)
        self.assertTrue(r.passed)

    def test_check_is_not_vacuous(self) -> None:
        # Different (k, m) should still pass -- the check must hold
        # generally, not just for the default parameters.
        for k, m in [(1.0, 0.1), (5.0, 2.0), (0.3, 3.0)]:
            with self.subTest(k=k, m=m):
                self.assertTrue(check_dispersion_relation(k=k, m=m).passed)


class YukawaScreeningTests(unittest.TestCase):

    def test_yukawa_ansatz_solves_screened_laplace_eq(self) -> None:
        r = check_yukawa_screening(m=0.5)
        self.assertTrue(r.passed)

    def test_coherence_length_is_inverse_mass(self) -> None:
        r = check_yukawa_screening(m=0.25)
        self.assertIn("4.0000", r.detail)  # L_psi = 1/m = 4.0


class CitationChecksTests(unittest.TestCase):

    def test_greens_function_is_citation_method(self) -> None:
        r = check_retarded_greens_function()
        self.assertEqual(r.method, "citation")
        self.assertTrue(r.passed)

    def test_impedance_analogy_flagged_as_overstated(self) -> None:
        r = check_impedance_analogy()
        self.assertEqual(r.method, "citation")
        self.assertFalse(r.passed)


class BifilarWorkedExampleTests(unittest.TestCase):
    """These reproduce the arithmetic actually present on the wiki's
    Bifilar Coil Engineering page (docs/wiki_cache/bifilar_coil_engineering.wikitext)
    as of the 2026-08-05 sync."""

    def test_efield_peak_matches_wiki(self) -> None:
        r = check_bifilar_efield_peak()
        self.assertTrue(r.passed)

    def test_farfield_falloff_table_matches_wiki(self) -> None:
        r = check_bifilar_farfield_falloff()
        self.assertTrue(r.passed)

    def test_bfield_cancellation_matches_wiki(self) -> None:
        r = check_bifilar_bfield_cancellation()
        self.assertTrue(r.passed)

    def test_adiabatic_pulse_discrepancy_is_flagged(self) -> None:
        # This is the genuine ~1000x discrepancy found during translation:
        # literally plugging the wiki's own stated P_peak into its own
        # stated formula does not reproduce its own stated 9.7 degC answer.
        r = check_bifilar_adiabatic_pulse()
        self.assertFalse(r.passed)
        self.assertIn("9689", r.detail.replace(",", ""))

    def test_adiabatic_pulse_root_cause_is_identified(self) -> None:
        # Substituting average power (P_peak * duty_cycle) for the
        # formula's labeled P_peak reproduces the wiki's stated 9.7 degC
        # almost exactly -- this pins down the precise nature of the
        # error rather than leaving it as an unexplained 1000x gap.
        r = check_bifilar_adiabatic_pulse()
        self.assertIn("ROOT CAUSE IDENTIFIED", r.detail)
        self.assertIn("9.7", r.detail.rsplit("degC", 1)[0][-30:])


class ShepardToneCrossPageTests(unittest.TestCase):

    def test_carrier_frequency_mismatch_is_flagged(self) -> None:
        r = check_shepard_tone_carrier_frequency_consistency()
        self.assertFalse(r.passed)
        self.assertEqual(r.method, "citation")
        self.assertIn("10, 20, 40", r.detail)
        self.assertIn("40, 80, 160", r.detail)

    def test_average_power_internal_inconsistency_is_flagged(self) -> None:
        r = check_bifilar_average_power_consistency()
        self.assertFalse(r.passed)
        self.assertIn("contradicts itself", r.detail)

    def test_recomputed_average_matches_sanity_table_not_body_text(self) -> None:
        # Independent of the CheckResult wrapper: the raw arithmetic
        # P_peak * duty_cycle must equal 20 W (sanity table), not 20 mW
        # (body text).
        p_peak_w = 20_000.0
        duty_cycle = 0.001
        self.assertAlmostEqual(p_peak_w * duty_cycle, 20.0)
        self.assertNotAlmostEqual(p_peak_w * duty_cycle, 0.020, places=1)


class OverallReportTests(unittest.TestCase):

    def test_run_all_returns_one_result_per_check_function(self) -> None:
        results = run_all()
        self.assertEqual(len(results), len(ALL_CHECKS))

    def test_known_discrepancies_are_exactly_the_expected_four(self) -> None:
        # Locks in the current, understood state: 1 citation-flagged
        # overstated analogy (impedance) + 2 genuine wiki-arithmetic
        # discrepancies (adiabatic pulse, average power) + 1 cross-page
        # citation discrepancy (Shepard Tone carrier frequencies) = 4
        # flags out of 10 checks. If this test starts failing, either a
        # real bug was introduced here, or the wiki page changed and the
        # checks need updating.
        results = run_all()
        flagged = {r.name for r in results if not r.passed}
        self.assertEqual(
            flagged,
            {
                "psi_impedance_vs_em_wave_impedance_analogy",
                "bifilar_adiabatic_pulse_temperature_rise",
                "bifilar_average_power_internal_consistency",
                "shepard_tone_carrier_frequency_cross_page_consistency",
            },
        )

    def test_format_report_mentions_every_check_name(self) -> None:
        results = run_all()
        text = format_report(results)
        for r in results:
            self.assertIn(r.name, text)

    def test_json_round_trip_has_matching_counts(self) -> None:
        results = run_all()
        data = results_to_json(results)
        self.assertEqual(data["n_total"], len(results))
        self.assertEqual(data["n_pass"], sum(1 for r in results if r.passed))
        self.assertEqual(len(data["checks"]), len(results))


if __name__ == "__main__":
    unittest.main()
