"""Unit tests for tools/analyze_g2.py — Track J commit 7 substrate."""

from __future__ import annotations

import io
import json
import math
import tempfile
import unittest
from pathlib import Path

from tools.analyze_g2 import (
    CRIT1_MAX_REL_ERR,
    CRIT2_DUT_MIN_RATIO,
    CRIT2_ORACLE_MIN_RATIO,
    CRIT3_MAX_REL_ERR,
    DEFAULT_BASELINE_S,
    DEFAULT_PACED_S,
    DEFAULT_RECOVERY_S,
    G2Report,
    RRSample,
    Segment,
    compute_segment_metrics,
    evaluate_g2,
    format_g2_report,
    load_rr_from_csv,
    load_rr_from_ndjson,
    make_default_segments,
    report_to_json,
    synth_session,
)


# ---------------------------------------------------------------------------
# Metric correctness on hand-computed signals
# ---------------------------------------------------------------------------


class MetricsTests(unittest.TestCase):

    def _seg(self) -> Segment:
        return Segment("baseline", 0.0, 1e9)

    def test_empty_segment_returns_all_none(self) -> None:
        m = compute_segment_metrics([], self._seg())
        self.assertEqual(m.n_beats, 0)
        self.assertEqual(m.n_out_of_range, 0)
        self.assertIsNone(m.mean_rr_ms)
        self.assertIsNone(m.rmssd_ms)
        self.assertIsNone(m.pnn50_pct)

    def test_single_sample_has_mean_but_no_variability(self) -> None:
        m = compute_segment_metrics(
            [RRSample(t=1.0, rr_ms=900.0)], self._seg()
        )
        self.assertEqual(m.n_beats, 1)
        self.assertAlmostEqual(m.mean_rr_ms, 900.0)
        self.assertIsNone(m.rmssd_ms)
        self.assertIsNone(m.pnn50_pct)

    def test_rmssd_known_formula(self) -> None:
        # RR = [800, 850, 800, 850] -> diffs = [50, -50, 50]
        # sum(d^2) = 7500; N=4; rmssd = sqrt(7500 / 3) = 50.0
        samples = [
            RRSample(t=1.0, rr_ms=800.0),
            RRSample(t=2.0, rr_ms=850.0),
            RRSample(t=3.0, rr_ms=800.0),
            RRSample(t=4.0, rr_ms=850.0),
        ]
        m = compute_segment_metrics(samples, self._seg())
        self.assertEqual(m.n_beats, 4)
        self.assertAlmostEqual(m.mean_rr_ms, 825.0)
        self.assertAlmostEqual(m.rmssd_ms, 50.0, places=6)

    def test_pnn50_known_signal(self) -> None:
        # diffs = [60, 40, 60, 40] -> 2 of 4 > 50 ms -> 50%
        samples = [
            RRSample(t=1.0, rr_ms=800.0),
            RRSample(t=2.0, rr_ms=860.0),  # +60
            RRSample(t=3.0, rr_ms=820.0),  # -40
            RRSample(t=4.0, rr_ms=880.0),  # +60
            RRSample(t=5.0, rr_ms=840.0),  # -40
        ]
        m = compute_segment_metrics(samples, self._seg())
        self.assertAlmostEqual(m.pnn50_pct, 50.0, places=6)

    def test_out_of_range_excluded(self) -> None:
        samples = [
            RRSample(t=1.0, rr_ms=800.0, q="ok"),
            RRSample(t=2.0, rr_ms=99999.0, q="out-of-range"),
            RRSample(t=3.0, rr_ms=850.0, q="ok"),
            RRSample(t=4.0, rr_ms=800.0, q="ok"),
        ]
        m = compute_segment_metrics(samples, self._seg())
        # The out-of-range sample is dropped; remaining sequence is
        # [800, 850, 800] with diffs [50, -50] -> rmssd = sqrt(5000/2) = 50.
        self.assertEqual(m.n_beats, 3)
        self.assertEqual(m.n_out_of_range, 1)
        self.assertAlmostEqual(m.mean_rr_ms, (800 + 850 + 800) / 3)
        self.assertAlmostEqual(m.rmssd_ms, 50.0, places=6)

    def test_segment_slicing(self) -> None:
        seg = Segment("baseline", 10.0, 20.0)
        samples = [
            RRSample(t=5.0, rr_ms=800.0),    # before
            RRSample(t=10.0, rr_ms=810.0),   # inclusive lower bound
            RRSample(t=15.0, rr_ms=820.0),   # inside
            RRSample(t=20.0, rr_ms=830.0),   # exclusive upper bound
            RRSample(t=25.0, rr_ms=840.0),   # after
        ]
        m = compute_segment_metrics(samples, seg)
        self.assertEqual(m.n_beats, 2)
        self.assertAlmostEqual(m.mean_rr_ms, 815.0)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


class NdjsonLoaderTests(unittest.TestCase):

    def _write(self, lines: list[str]) -> Path:
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ndjson", delete=False, encoding="utf-8"
        )
        for line in lines:
            f.write(line + "\n")
        f.close()
        return Path(f.name)

    def test_filters_to_target_channel(self) -> None:
        path = self._write([
            json.dumps({"t": 1.0, "ch": "ppg-rr", "v": 800, "q": "ok"}),
            json.dumps({"t": 1.05, "ch": "ppg-hrv", "v": 12345, "q": "ok"}),
            json.dumps({"t": 2.0, "ch": "ppg-rr", "v": 850, "q": "ok"}),
            json.dumps({"t": 3.0, "ch": "ecg-rr", "v": 820, "q": "ok"}),
        ])
        rr = load_rr_from_ndjson(path, channel="ppg-rr")
        self.assertEqual(len(rr), 2)
        self.assertAlmostEqual(rr[0].rr_ms, 800.0)
        self.assertAlmostEqual(rr[1].rr_ms, 850.0)

    def test_drops_first_peak_sentinel(self) -> None:
        # Per SCHEMA.md §2.2 the first peak emits v=0.
        path = self._write([
            json.dumps({"t": 1.0, "ch": "ppg-rr", "v": 0, "q": "ok"}),
            json.dumps({"t": 2.0, "ch": "ppg-rr", "v": 850, "q": "ok"}),
        ])
        rr = load_rr_from_ndjson(path, channel="ppg-rr")
        self.assertEqual(len(rr), 1)
        self.assertAlmostEqual(rr[0].rr_ms, 850.0)

    def test_carries_q_and_conf(self) -> None:
        path = self._write([
            json.dumps({"t": 1.0, "ch": "ppg-rr", "v": 800,
                        "q": "out-of-range", "conf": 1.42}),
        ])
        rr = load_rr_from_ndjson(path, channel="ppg-rr")
        self.assertEqual(rr[0].q, "out-of-range")
        self.assertAlmostEqual(rr[0].conf, 1.42)

    def test_skips_malformed_lines(self) -> None:
        path = self._write([
            "{not json",
            "",
            json.dumps({"t": 1.0, "ch": "ppg-rr", "v": 800, "q": "ok"}),
        ])
        rr = load_rr_from_ndjson(path, channel="ppg-rr")
        self.assertEqual(len(rr), 1)


class CsvLoaderTests(unittest.TestCase):

    def _write(self, text: str) -> Path:
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        f.write(text)
        f.close()
        return Path(f.name)

    def test_polar_semicolon_header(self) -> None:
        # Canonical Polar Sensor Logger shape from g2_hrv_validation.md §3.
        path = self._write(
            "Phone timestamp;sensor name;RR-interval [ms]\n"
            "2026-05-20T12:00:00.000;Polar H10;800\n"
            "2026-05-20T12:00:00.800;Polar H10;850\n"
            "2026-05-20T12:00:01.650;Polar H10;820\n"
        )
        rr = load_rr_from_csv(path, oracle_t0=10.0)
        self.assertEqual(len(rr), 3)
        self.assertAlmostEqual(rr[0].rr_ms, 800.0)
        # Cumulative t: 10 + 0.8 = 10.8
        self.assertAlmostEqual(rr[0].t, 10.8, places=6)
        self.assertAlmostEqual(rr[1].t, 10.8 + 0.85, places=6)

    def test_comma_separated_with_header_autodetect(self) -> None:
        path = self._write(
            "time,sensor,RR-interval [ms]\n"
            "0,polar,900\n"
            "1,polar,910\n"
        )
        rr = load_rr_from_csv(path)
        self.assertEqual(len(rr), 2)
        self.assertAlmostEqual(rr[0].rr_ms, 900.0)

    def test_explicit_column_override(self) -> None:
        path = self._write("a,b,c,d\n100,200,300,400\n")
        rr = load_rr_from_csv(path, rr_column=1)
        self.assertEqual(len(rr), 1)
        self.assertAlmostEqual(rr[0].rr_ms, 200.0)

    def test_drops_nonpositive_and_nonfinite(self) -> None:
        path = self._write(
            "Phone timestamp;sensor name;RR-interval [ms]\n"
            "x;y;0\n"
            "x;y;-50\n"
            "x;y;nan\n"
            "x;y;850\n"
        )
        rr = load_rr_from_csv(path)
        self.assertEqual(len(rr), 1)
        self.assertAlmostEqual(rr[0].rr_ms, 850.0)


# ---------------------------------------------------------------------------
# §6 pass-criteria evaluation
# ---------------------------------------------------------------------------


class EvaluateG2Tests(unittest.TestCase):

    def test_synth_session_passes_all_three(self) -> None:
        dut, oracle, segments = synth_session()
        r = evaluate_g2(dut, oracle, segments)
        self.assertTrue(r.crit1_pass,
                        f"crit1 err={r.crit1_baseline_rel_err}")
        self.assertTrue(r.crit2_pass,
                        f"crit2 orc={r.crit2_oracle_paced_ratio} "
                        f"dut={r.crit2_dut_paced_ratio}")
        self.assertTrue(r.crit3_pass,
                        f"crit3 err={r.crit3_paced_rel_err}")
        self.assertTrue(r.overall_pass)

    def test_dut_noise_fails_baseline_agreement(self) -> None:
        # Large per-beat DUT noise inflates DUT RMSSD relative to oracle
        # (RMSSD is shift-invariant, so a DC bias would NOT fail this —
        # variance is what the protocol's §6 criterion 1 actually catches).
        dut, oracle, segments = synth_session(dut_noise_ms=200.0)
        r = evaluate_g2(dut, oracle, segments)
        self.assertFalse(r.crit1_pass)
        self.assertGreater(r.crit1_baseline_rel_err, CRIT1_MAX_REL_ERR)
        self.assertFalse(r.overall_pass)

    def test_no_paced_response_fails_crit2(self) -> None:
        # Force baseline sigma == paced sigma so oracle RMSSD doesn't rise.
        dut, oracle, segments = synth_session(
            sigma_baseline_ms=40.0,
            sigma_paced_ms=40.0,
            sigma_recovery_ms=40.0,
        )
        r = evaluate_g2(dut, oracle, segments)
        self.assertFalse(r.crit2_pass)
        self.assertLess(r.crit2_oracle_paced_ratio, CRIT2_ORACLE_MIN_RATIO)
        self.assertFalse(r.overall_pass)
        # The protocol §8 note about the manoeuvre not engaging should fire.
        self.assertTrue(
            any("did not exhibit" in n for n in r.notes),
            f"expected operator-side note, got: {r.notes}"
        )

    def test_overall_pass_requires_all_three(self) -> None:
        # Pass criteria 1 and 3 (agreement) but fail criterion 2 (response).
        dut, oracle, segments = synth_session(
            sigma_baseline_ms=40.0,
            sigma_paced_ms=40.0,
        )
        r = evaluate_g2(dut, oracle, segments)
        self.assertTrue(r.crit1_pass)
        self.assertTrue(r.crit3_pass)
        self.assertFalse(r.crit2_pass)
        self.assertFalse(r.overall_pass)

    def test_rejects_wrong_segment_names(self) -> None:
        bad = (
            Segment("warmup", 0, 100),
            Segment("paced", 100, 200),
            Segment("recovery", 200, 300),
        )
        with self.assertRaises(ValueError):
            evaluate_g2([], [], bad)

    def test_rejects_wrong_segment_count(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_g2([], [], (Segment("baseline", 0, 100),))


class DefaultSegmentsTests(unittest.TestCase):

    def test_555_layout(self) -> None:
        bs, ps, rs = make_default_segments(30.0)
        self.assertEqual(bs.t_start, 30.0)
        self.assertEqual(bs.t_end, 30.0 + DEFAULT_BASELINE_S)
        self.assertEqual(ps.t_start, bs.t_end)
        self.assertEqual(ps.t_end, bs.t_end + DEFAULT_PACED_S)
        self.assertEqual(rs.t_start, ps.t_end)
        self.assertEqual(rs.t_end, ps.t_end + DEFAULT_RECOVERY_S)


# ---------------------------------------------------------------------------
# Formatting + JSON
# ---------------------------------------------------------------------------


class ReportFormattingTests(unittest.TestCase):

    def test_text_report_includes_pass_lines(self) -> None:
        dut, oracle, segments = synth_session()
        r = evaluate_g2(dut, oracle, segments)
        text = format_g2_report(r)
        self.assertIn("G2 HRV Validation Report", text)
        self.assertIn("baseline rel err", text)
        self.assertIn("paced response", text)
        self.assertIn("SESSION RESULT:", text)
        self.assertIn("PASS", text)

    def test_json_report_round_trips(self) -> None:
        dut, oracle, segments = synth_session()
        r = evaluate_g2(dut, oracle, segments)
        d = report_to_json(r)
        # JSON-serializable end-to-end.
        s = json.dumps(d, sort_keys=True)
        d2 = json.loads(s)
        self.assertEqual(d2["overall_pass"], r.overall_pass)
        self.assertIn("crit1", d2["criteria"])
        self.assertIn("crit2", d2["criteria"])
        self.assertIn("crit3", d2["criteria"])
        self.assertEqual(d2["criteria"]["crit1"]["threshold"],
                         CRIT1_MAX_REL_ERR)


if __name__ == "__main__":
    unittest.main()
