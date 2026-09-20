"""Unit tests for tools/experiment_design.py."""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.experiment_design import (
    GANZFELD_HIT_RATE_PRESETS,
    achieved_power,
    achieved_power_binomial,
    bic_bayes_factor,
    binomial_bayes_factor,
    build_preregistration,
    dicke_scaling_effect_size,
    dicke_scaling_predictions,
    interpret_bayes_factor,
    norm_cdf,
    norm_ppf,
    one_proportion_z_test,
    required_n,
    required_n_binomial,
    required_replicates_for_dicke_test,
    t_stat_from_summary,
    write_preregistration,
    _cli,
)


class NormalHelperTests(unittest.TestCase):

    def test_norm_ppf_is_inverse_of_norm_cdf(self) -> None:
        for p in (0.01, 0.05, 0.1, 0.5, 0.8, 0.9, 0.975, 0.999):
            z = norm_ppf(p)
            self.assertAlmostEqual(norm_cdf(z), p, places=6)

    def test_known_critical_values(self) -> None:
        # Standard two-sided alpha=0.05 critical value.
        self.assertAlmostEqual(norm_ppf(0.975), 1.959964, places=4)
        self.assertAlmostEqual(norm_ppf(0.5), 0.0, places=6)

    def test_norm_ppf_rejects_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            norm_ppf(0.0)
        with self.assertRaises(ValueError):
            norm_ppf(1.0)


class RequiredNTests(unittest.TestCase):

    def test_classic_cohen_medium_effect_two_sample(self) -> None:
        # Textbook value for d=0.5, alpha=0.05, power=0.80, two-sample is
        # ~64/group (Cohen 1988 tables, exact noncentral-t). The normal
        # approximation used here should land within a couple of subjects.
        n = required_n(0.5, alpha=0.05, power=0.80, design="two-sample")
        self.assertTrue(60 <= n <= 66, f"expected ~64, got {n}")

    def test_paired_needs_fewer_than_two_sample_for_same_d(self) -> None:
        n_paired = required_n(0.5, design="paired")
        n_two_sample = required_n(0.5, design="two-sample")
        self.assertLess(n_paired, n_two_sample)

    def test_smaller_effect_needs_more_subjects(self) -> None:
        n_small_effect = required_n(0.2, design="paired")
        n_large_effect = required_n(0.8, design="paired")
        self.assertGreater(n_small_effect, n_large_effect)

    def test_higher_power_needs_more_subjects(self) -> None:
        n_80 = required_n(0.3, power=0.80, design="paired")
        n_95 = required_n(0.3, power=0.95, design="paired")
        self.assertGreater(n_95, n_80)

    def test_rejects_nonpositive_effect_size(self) -> None:
        with self.assertRaises(ValueError):
            required_n(0.0, design="paired")
        with self.assertRaises(ValueError):
            required_n(-0.1, design="paired")

    def test_rejects_unknown_design(self) -> None:
        with self.assertRaises(ValueError):
            required_n(0.3, design="bogus")  # type: ignore[arg-type]


class AchievedPowerTests(unittest.TestCase):

    def test_round_trips_with_required_n(self) -> None:
        for d, design in [(0.5, "two-sample"), (0.2, "paired"), (0.8, "one-sample")]:
            n = required_n(d, alpha=0.05, power=0.80, design=design)
            p = achieved_power(n, d, alpha=0.05, design=design)
            # required_n rounds UP, so achieved power at that n must be
            # at least the target (allowing tiny float slack).
            self.assertGreaterEqual(p, 0.80 - 1e-6)

    def test_more_subjects_gives_more_power(self) -> None:
        p_low = achieved_power(20, 0.3, design="paired")
        p_high = achieved_power(200, 0.3, design="paired")
        self.assertGreater(p_high, p_low)


class BayesFactorTests(unittest.TestCase):

    def test_null_result_favors_h0(self) -> None:
        bf01, bf10 = bic_bayes_factor(t_stat=0.1, n=30)
        self.assertGreater(bf01, 1.0)
        self.assertLess(bf10, 1.0)

    def test_strong_effect_favors_h1(self) -> None:
        bf01, bf10 = bic_bayes_factor(t_stat=4.0, n=30)
        self.assertGreater(bf10, 1.0)
        self.assertLess(bf01, 1.0)

    def test_bf01_and_bf10_are_reciprocal(self) -> None:
        bf01, bf10 = bic_bayes_factor(t_stat=2.0, n=15)
        self.assertAlmostEqual(bf01 * bf10, 1.0, places=6)

    def test_larger_t_monotonically_favors_h1_more(self) -> None:
        _, bf10_small = bic_bayes_factor(t_stat=1.0, n=20)
        _, bf10_large = bic_bayes_factor(t_stat=3.0, n=20)
        self.assertGreater(bf10_large, bf10_small)

    def test_rejects_non_positive_df(self) -> None:
        with self.assertRaises(ValueError):
            bic_bayes_factor(t_stat=1.0, n=1)  # df = 0

    def test_interpretation_labels(self) -> None:
        self.assertIn("H1", interpret_bayes_factor(50.0))
        self.assertIn("H0", interpret_bayes_factor(0.05))

    def test_t_stat_from_summary_matches_manual_formula(self) -> None:
        t = t_stat_from_summary(mean_diff=5.0, sd_diff=10.0, n=25)
        self.assertAlmostEqual(t, 5.0 / (10.0 / math.sqrt(25)), places=9)


class BinomialDesignTests(unittest.TestCase):

    def test_required_n_binomial_rejects_equal_rates(self) -> None:
        with self.assertRaises(ValueError):
            required_n_binomial(0.25, p0=0.25)

    def test_required_n_binomial_larger_effect_needs_fewer_trials(self) -> None:
        n_small = required_n_binomial(0.30, p0=0.25)
        n_large = required_n_binomial(0.50, p0=0.25)
        self.assertGreater(n_small, n_large)

    def test_achieved_power_binomial_round_trips(self) -> None:
        n = required_n_binomial(0.35, p0=0.25, power=0.80)
        power = achieved_power_binomial(n, 0.35, p0=0.25)
        self.assertGreaterEqual(power, 0.80 - 1e-6)

    def test_one_proportion_z_test_null_case(self) -> None:
        # Exactly at chance: z should be ~0, p should be ~1.
        z, p_value = one_proportion_z_test(25, 100, 0.25)
        self.assertAlmostEqual(z, 0.0, places=9)
        self.assertAlmostEqual(p_value, 1.0, places=9)

    def test_one_proportion_z_test_elevated_hit_rate(self) -> None:
        z, p_value = one_proportion_z_test(40, 100, 0.25)
        self.assertGreater(z, 0.0)
        self.assertLess(p_value, 0.05)

    def test_one_proportion_z_test_rejects_bad_inputs(self) -> None:
        with self.assertRaises(ValueError):
            one_proportion_z_test(5, 0, 0.25)
        with self.assertRaises(ValueError):
            one_proportion_z_test(-1, 10, 0.25)
        with self.assertRaises(ValueError):
            one_proportion_z_test(11, 10, 0.25)

    def test_binomial_bayes_factor_null_favors_h0(self) -> None:
        bf01, bf10 = binomial_bayes_factor(25, 100, 0.25)
        self.assertGreater(bf01, bf10)

    def test_binomial_bayes_factor_strong_effect_favors_h1(self) -> None:
        bf01, bf10 = binomial_bayes_factor(60, 100, 0.25)
        self.assertGreater(bf10, bf01)

    def test_binomial_bayes_factor_reciprocal(self) -> None:
        bf01, bf10 = binomial_bayes_factor(40, 100, 0.25)
        self.assertAlmostEqual(bf01 * bf10, 1.0, places=6)

    def test_binomial_bayes_factor_perfect_score_is_decisive(self) -> None:
        bf01, bf10 = binomial_bayes_factor(20, 20, 0.25)
        self.assertGreater(bf10, 100.0)


class GanzfeldPresetTests(unittest.TestCase):
    """docs/psionic_engineering/literature_grounding.md is the source of
    truth for these values -- if this test needs to change, that doc's
    citations need to change first, not the other way around."""

    def test_presets_are_plausible_hit_rates_above_quarter_chance(self) -> None:
        for name, p1 in GANZFELD_HIT_RATE_PRESETS.items():
            with self.subTest(name=name):
                self.assertGreater(p1, 0.25, "presets should be hit rates above 4-AFC chance")
                self.assertLess(p1, 0.5, "sanity bound -- not a plausible ganzfeld hit rate")

    def test_optimistic_preset_matches_storm_2010_headline_figure(self) -> None:
        self.assertAlmostEqual(GANZFELD_HIT_RATE_PRESETS["ganzfeld-storm2010-optimistic"], 0.301)

    def test_cli_preset_and_p1_are_mutually_exclusive(self) -> None:
        exit_code = _cli(["binom", "--p0", "0.25",
                           "--preset", "ganzfeld-storm2010-optimistic", "--p1", "0.5"])
        self.assertEqual(exit_code, 3)

    def test_cli_preset_resolves_to_a_required_n(self) -> None:
        # Just confirm it runs end-to-end without error; required_n_binomial
        # itself is covered by BinomialDesignTests.
        exit_code = _cli(["binom", "--p0", "0.25", "--preset", "ganzfeld-storm2010-conservative"])
        self.assertEqual(exit_code, 0)


class DickeScalingTests(unittest.TestCase):

    def test_predictions_at_default_n1_vs_n2(self) -> None:
        preds = dicke_scaling_predictions()
        self.assertAlmostEqual(preds["incoherent_prediction"], 2.0)
        self.assertAlmostEqual(preds["coherent_dicke_prediction"], 4.0)

    def test_predictions_scale_with_baseline_intensity(self) -> None:
        preds = dicke_scaling_predictions(baseline_intensity=10.0)
        self.assertAlmostEqual(preds["incoherent_prediction"], 20.0)
        self.assertAlmostEqual(preds["coherent_dicke_prediction"], 40.0)

    def test_effect_size_is_gap_over_noise(self) -> None:
        # incoherent=2, coherent=4 at defaults -> gap=2
        d = dicke_scaling_effect_size(noise_sd=2.0)
        self.assertAlmostEqual(d, 1.0)

    def test_lower_noise_gives_larger_effect_size(self) -> None:
        d_noisy = dicke_scaling_effect_size(noise_sd=10.0)
        d_clean = dicke_scaling_effect_size(noise_sd=1.0)
        self.assertGreater(d_clean, d_noisy)

    def test_required_replicates_matches_underlying_required_n(self) -> None:
        # d=0.2 at noise_sd=10 (gap=2/10=0.2) should reproduce the same N
        # as calling required_n(0.2, design="one-sample") directly --
        # confirms this correctly reuses existing power machinery rather
        # than reimplementing it.
        n_dicke = required_replicates_for_dicke_test(noise_sd=10.0)
        n_direct = required_n(0.2, design="one-sample")
        self.assertEqual(n_dicke, n_direct)

    def test_higher_noise_needs_more_replicates(self) -> None:
        n_low_noise = required_replicates_for_dicke_test(noise_sd=2.0)
        n_high_noise = required_replicates_for_dicke_test(noise_sd=20.0)
        self.assertGreater(n_high_noise, n_low_noise)

    def test_rejects_n_coherent_not_greater_than_baseline(self) -> None:
        with self.assertRaises(ValueError):
            dicke_scaling_effect_size(n_coherent=1, n_baseline=1, noise_sd=1.0)
        with self.assertRaises(ValueError):
            dicke_scaling_effect_size(n_coherent=1, n_baseline=2, noise_sd=1.0)

    def test_rejects_nonpositive_noise_or_baseline(self) -> None:
        with self.assertRaises(ValueError):
            dicke_scaling_effect_size(noise_sd=0.0)
        with self.assertRaises(ValueError):
            dicke_scaling_effect_size(noise_sd=-1.0)
        with self.assertRaises(ValueError):
            dicke_scaling_effect_size(noise_sd=1.0, baseline_intensity=0.0)

    def test_cli_end_to_end(self) -> None:
        exit_code = _cli(["dicke-scaling", "--noise-sd", "2.0"])
        self.assertEqual(exit_code, 0)

    def test_cli_rejects_invalid_n_values(self) -> None:
        exit_code = _cli(["dicke-scaling", "--noise-sd", "2.0", "--n-coherent", "1", "--n-baseline", "1"])
        self.assertEqual(exit_code, 3)


class PreregistrationTests(unittest.TestCase):

    def _spec(self) -> dict:
        return {
            "hypothesis": "H1 stim increases RMSSD coherence gain vs sham",
            "primary_endpoint": "RMSSD coherence gain",
            "effect_size_d": 0.20,
            "alpha": 0.05,
            "power": 0.80,
            "design": "paired",
        }

    def test_build_preregistration_computes_required_n(self) -> None:
        doc = build_preregistration(self._spec())
        self.assertIn("required_n", doc)
        self.assertEqual(doc["required_n"], required_n(0.20, design="paired"))

    def test_build_preregistration_is_hashed_and_timestamped(self) -> None:
        doc = build_preregistration(self._spec())
        self.assertIn("lock_hash_sha256", doc)
        self.assertEqual(len(doc["lock_hash_sha256"]), 64)
        self.assertIn("locked_at", doc)

    def test_missing_required_key_raises(self) -> None:
        spec = self._spec()
        del spec["effect_size_d"]
        with self.assertRaises(ValueError):
            build_preregistration(spec)

    def test_write_preregistration_creates_file(self) -> None:
        with TemporaryDirectory() as td:
            out = Path(td) / "prereg.json"
            doc = write_preregistration(self._spec(), out)
            self.assertTrue(out.exists())
            on_disk = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(on_disk["lock_hash_sha256"], doc["lock_hash_sha256"])

    def test_write_preregistration_refuses_overwrite(self) -> None:
        with TemporaryDirectory() as td:
            out = Path(td) / "prereg.json"
            write_preregistration(self._spec(), out)
            with self.assertRaises(FileExistsError):
                write_preregistration(self._spec(), out)


if __name__ == "__main__":
    unittest.main()
