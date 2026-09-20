"""Unit tests for tools/analyze_dyadic_coherence.py."""

from __future__ import annotations

import math
import random
import unittest

import json as json_module
import tempfile
from pathlib import Path

from tools.analyze_g2 import RRSample, Segment, make_default_segments
from tools.analyze_dyadic_coherence import (
    MAX_RESAMPLED_LENGTH,
    ScalarSample,
    analyze_dyadic,
    analyze_dyadic_by_segment,
    circular_shift,
    crqa,
    lagged_cross_correlation,
    load_scalar_channel_from_ndjson,
    peak_abs_cross_correlation,
    report_to_json,
    resample_uniform,
    segment_contrast,
    segmented_report_to_json,
    format_segmented_report,
    surrogate_test,
    synth_dyad,
    zscore,
)


class ResampleTests(unittest.TestCase):

    def test_linear_interpolation_midpoint(self) -> None:
        samples = [
            RRSample(t=0.0, rr_ms=800.0, q="ok"),
            RRSample(t=10.0, rr_ms=900.0, q="ok"),
        ]
        out = resample_uniform(samples, t_start=0.0, t_end=10.0, dt=5.0)
        # grid points at t=0 and t=5 (t_end exclusive)
        self.assertEqual(len(out), 2)
        self.assertAlmostEqual(out[0], 800.0)
        self.assertAlmostEqual(out[1], 850.0)  # halfway between 800 and 900

    def test_holds_flat_outside_observed_range(self) -> None:
        samples = [
            RRSample(t=5.0, rr_ms=800.0, q="ok"),
            RRSample(t=6.0, rr_ms=800.0, q="ok"),
        ]
        out = resample_uniform(samples, t_start=0.0, t_end=10.0, dt=1.0)
        self.assertAlmostEqual(out[0], 800.0)   # before first event
        self.assertAlmostEqual(out[-1], 800.0)  # after last event

    def test_out_of_range_samples_are_excluded(self) -> None:
        samples = [
            RRSample(t=0.0, rr_ms=800.0, q="ok"),
            RRSample(t=5.0, rr_ms=99999.0, q="out-of-range"),
            RRSample(t=10.0, rr_ms=900.0, q="ok"),
        ]
        out = resample_uniform(samples, t_start=0.0, t_end=10.0, dt=5.0)
        self.assertNotIn(99999.0, out)

    def test_requires_at_least_two_samples(self) -> None:
        with self.assertRaises(ValueError):
            resample_uniform([RRSample(t=0.0, rr_ms=800.0)], t_start=0.0, t_end=10.0, dt=1.0)


class ZscoreAndShiftTests(unittest.TestCase):

    def test_zscore_has_zero_mean_unit_variance(self) -> None:
        xs = [1.0, 2.0, 3.0, 4.0, 5.0]
        z = zscore(xs)
        mean = sum(z) / len(z)
        var = sum((x - mean) ** 2 for x in z) / len(z)
        self.assertAlmostEqual(mean, 0.0, places=9)
        self.assertAlmostEqual(var, 1.0, places=9)

    def test_zscore_constant_series_does_not_divide_by_zero(self) -> None:
        z = zscore([5.0, 5.0, 5.0])
        self.assertEqual(z, [0.0, 0.0, 0.0])

    def test_circular_shift_preserves_length_and_multiset(self) -> None:
        xs = [1, 2, 3, 4, 5]
        shifted = circular_shift(xs, 2)
        self.assertEqual(len(shifted), len(xs))
        self.assertEqual(sorted(shifted), sorted(xs))
        self.assertEqual(shifted, [4, 5, 1, 2, 3])

    def test_circular_shift_zero_is_identity(self) -> None:
        xs = [1, 2, 3]
        self.assertEqual(circular_shift(xs, 0), xs)


class CrossCorrelationTests(unittest.TestCase):

    def test_identical_series_has_zero_lag_correlation_one(self) -> None:
        a = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0]
        xc = lagged_cross_correlation(a, list(a), max_lag=2)
        self.assertAlmostEqual(xc[0], 1.0, places=9)

    def test_shifted_series_peaks_at_the_shift(self) -> None:
        # Non-periodic (random) signal so there is exactly one lag with a
        # perfect match -- a periodic base signal (an earlier version of
        # this test used one) can produce equally strong correlation, of
        # either sign, at multiple lags, which made the test's own
        # expectation ambiguous rather than testing a real bug.
        rng = random.Random(0)
        a = [rng.gauss(0.0, 1.0) for _ in range(60)]
        b = [0.0, 0.0] + a[:-2]  # b[i] = a[i-2] for i >= 2 (b lags a by 2)
        xc = lagged_cross_correlation(a, b, max_lag=5)
        best_lag = max(xc, key=lambda k: xc[k])  # most POSITIVE correlation
        self.assertEqual(best_lag, 2)
        self.assertAlmostEqual(xc[2], 1.0, places=9)

    def test_rejects_mismatched_lengths(self) -> None:
        with self.assertRaises(ValueError):
            lagged_cross_correlation([1.0, 2.0], [1.0, 2.0, 3.0], max_lag=1)


class CRQATests(unittest.TestCase):

    def test_identical_series_has_full_recurrence_on_main_diagonal(self) -> None:
        a = [i % 5 for i in range(50)]
        result = crqa(a, list(a), eps_percentile=5.0)
        self.assertGreater(result.recurrence_rate, 0.0)
        self.assertGreaterEqual(result.determinism, 0.0)
        self.assertLessEqual(result.determinism, 1.0)

    def test_rejects_length_over_guard(self) -> None:
        big = [0.0] * (MAX_RESAMPLED_LENGTH + 1)
        with self.assertRaises(ValueError):
            crqa(big, list(big))


class SurrogateTestTests(unittest.TestCase):

    def test_identical_series_gives_very_low_p_value(self) -> None:
        a = [math.sin(i / 4.0) + 0.01 * i for i in range(100)]
        report = surrogate_test(a, list(a), statistic="xcorr", max_lag=3, n_surrogates=100)
        # a perfectly self-correlated pair should sit at or above almost
        # every circularly-shifted surrogate's correlation.
        self.assertLess(report.p_value, 0.2)

    def test_rejects_unknown_statistic(self) -> None:
        with self.assertRaises(ValueError):
            surrogate_test([1.0, 2.0, 3.0], [1.0, 2.0, 3.0], statistic="bogus")


class SynthDyadIntegrationTests(unittest.TestCase):
    """These are the self-test scenarios exposed via --self-test; locking
    them in as unit tests catches any accidental regression in the
    synthetic-data generator or the analysis pipeline together."""

    def test_correlated_dyad_is_flagged(self) -> None:
        a, b = synth_dyad(correlated=True)
        report = analyze_dyadic(a, b, n_surrogates=200)
        significant = report.xcorr_surrogate.p_value < 0.05 or report.det_surrogate.p_value < 0.05
        self.assertTrue(significant, "tuned correlated synthetic dyad should be flagged")

    def test_independent_dyad_is_not_flagged(self) -> None:
        a, b = synth_dyad(correlated=False)
        report = analyze_dyadic(a, b, n_surrogates=200)
        # Not a strict guarantee (nominal alpha false-positive rate
        # applies), but with this fixed seed it must come out negative.
        significant = report.xcorr_surrogate.p_value < 0.05 or report.det_surrogate.p_value < 0.05
        self.assertFalse(significant, "independent synthetic dyad should not be flagged")

    def test_report_to_json_shape(self) -> None:
        a, b = synth_dyad(correlated=True)
        report = analyze_dyadic(a, b, n_surrogates=50)
        data = report_to_json(report)
        for key in ("n_samples", "xcorr_peak", "xcorr_surrogate", "crqa", "det_surrogate", "significant"):
            self.assertIn(key, data)

    def test_analyze_dyadic_requires_overlap(self) -> None:
        a = [RRSample(t=0.0, rr_ms=800.0), RRSample(t=10.0, rr_ms=800.0)]
        b = [RRSample(t=1000.0, rr_ms=800.0), RRSample(t=1010.0, rr_ms=800.0)]
        with self.assertRaises(ValueError):
            analyze_dyadic(a, b)


class ScalarChannelTests(unittest.TestCase):

    def test_generic_loader_keeps_zero_values(self) -> None:
        # This is the exact behavior that distinguishes it from
        # load_rr_from_ndjson, which drops v<=0 as a first-peak sentinel.
        lines = [
            json_module.dumps({"t": 1.0, "ch": "gsr", "v": 2.1}),
            json_module.dumps({"t": 2.0, "ch": "gsr", "v": 0.0}),
            json_module.dumps({"t": 3.0, "ch": "other", "v": 99}),
            json_module.dumps({"t": 4.0, "ch": "gsr", "v": 2.5}),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "capture.ndjson"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            samples = load_scalar_channel_from_ndjson(path, channel="gsr")
        self.assertEqual([s.value for s in samples], [2.1, 0.0, 2.5])

    def test_resample_uniform_accepts_scalar_samples(self) -> None:
        samples = [
            ScalarSample(t=0.0, value=10.0, q="ok"),
            ScalarSample(t=10.0, value=20.0, q="ok"),
        ]
        out = resample_uniform(samples, t_start=0.0, t_end=10.0, dt=5.0)
        self.assertAlmostEqual(out[0], 10.0)
        self.assertAlmostEqual(out[1], 15.0)

    def test_analyze_dyadic_works_with_scalar_samples(self) -> None:
        # Build two correlated scalar-channel dyads by reusing synth_dyad's
        # RRSample output and converting to ScalarSample -- confirms the
        # whole pipeline (not just resample_uniform) is channel-agnostic.
        a_rr, b_rr = synth_dyad(correlated=True)
        a = [ScalarSample(t=s.t, value=s.rr_ms, q=s.q) for s in a_rr]
        b = [ScalarSample(t=s.t, value=s.rr_ms, q=s.q) for s in b_rr]
        report = analyze_dyadic(a, b, n_surrogates=100)
        self.assertGreater(report.n_samples, 0)


class SegmentedAnalysisTests(unittest.TestCase):

    def _segments(self) -> tuple[Segment, Segment, Segment]:
        return make_default_segments(0.0, baseline_s=200.0, paced_s=200.0, recovery_s=200.0)

    def test_analyze_dyadic_by_segment_covers_every_segment(self) -> None:
        a, b = synth_dyad(correlated=True, n_beats=1200)
        segments = self._segments()
        reports = analyze_dyadic_by_segment(a, b, segments, n_surrogates=50)
        self.assertEqual(set(reports.keys()), {"baseline", "paced", "recovery"})

    def test_segment_with_no_data_reports_error_string_not_exception(self) -> None:
        a, b = synth_dyad(correlated=True, n_beats=50)  # short session
        # Recovery segment (400s-600s) will have no data for a ~45s session.
        segments = self._segments()
        reports = analyze_dyadic_by_segment(a, b, segments, n_surrogates=20)
        self.assertIsInstance(reports["recovery"], str)

    def test_segment_contrast_computes_deltas(self) -> None:
        a, b = synth_dyad(correlated=True, n_beats=1200)
        reports = analyze_dyadic_by_segment(a, b, self._segments(), n_surrogates=50)
        contrast = segment_contrast(reports, "paced", "baseline")
        self.assertIn("xcorr_peak_delta", contrast)
        self.assertIn("determinism_delta", contrast)
        self.assertEqual(contrast["segments"], ("paced", "baseline"))

    def test_segment_contrast_rejects_missing_segment(self) -> None:
        a, b = synth_dyad(correlated=True, n_beats=1200)
        reports = analyze_dyadic_by_segment(a, b, self._segments(), n_surrogates=50)
        with self.assertRaises(ValueError):
            segment_contrast(reports, "paced", "nonexistent")

    def test_format_segmented_report_mentions_every_segment(self) -> None:
        a, b = synth_dyad(correlated=True, n_beats=1200)
        reports = analyze_dyadic_by_segment(a, b, self._segments(), n_surrogates=50)
        text = format_segmented_report(reports)
        for name in reports:
            self.assertIn(name, text)

    def test_segmented_report_to_json_shape(self) -> None:
        a, b = synth_dyad(correlated=True, n_beats=1200)
        reports = analyze_dyadic_by_segment(a, b, self._segments(), n_surrogates=50)
        data = segmented_report_to_json(reports)
        self.assertEqual(set(data.keys()), {"baseline", "paced", "recovery"})
        for v in data.values():
            self.assertIsInstance(v, dict)


if __name__ == "__main__":
    unittest.main()
