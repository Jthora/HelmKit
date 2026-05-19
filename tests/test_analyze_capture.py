"""Unit tests for tools/analyze_capture.py — Track K commit 2."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.analyze_capture import (
    CHANNEL_REGISTRY,
    analyze,
    analyze_lines,
    format_report,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class AnalyzerCoreTests(unittest.TestCase):

    def test_empty_input(self) -> None:
        r = analyze_lines([])
        self.assertEqual(r.total_lines, 0)
        self.assertEqual(r.data_lines, 0)
        self.assertEqual(r.channels, {})

    def test_parse_error_counted(self) -> None:
        r = analyze_lines(['{"t":1.0,"ch":"gsr"', "not json at all"])
        self.assertEqual(r.parse_errors, 2)
        self.assertEqual(r.data_lines, 0)

    def test_meta_lines_partitioned(self) -> None:
        r = analyze_lines([
            json.dumps({"t": 0.0, "kind": "hello", "schema": "0.1",
                        "boot": "abc"}),
            json.dumps({"t": 0.1, "kind": "smoke", "source": "gsr",
                        "ok": 1, "ev_a": 100, "boot": "abc"}),
            json.dumps({"t": 0.2, "ch": "gsr", "v": 2048,
                        "q": "ok", "boot": "abc"}),
        ])
        self.assertEqual(r.meta_lines, 2)
        self.assertEqual(r.data_lines, 1)
        self.assertIn("0.1", r.schemas_seen)
        self.assertEqual(len(r.smoke_results), 1)
        self.assertIn("abc", r.boot_ids)

    def test_rate_detection_within_5pct(self) -> None:
        """50 Hz GSR ⇒ observed_hz within 5 % of expected (50 Hz)."""
        lines = [
            json.dumps({"t": round(i * 0.02, 3), "ch": "gsr",
                        "v": 2048, "q": "ok", "boot": "abc"})
            for i in range(1500)  # 30 s @ 50 Hz
        ]
        r = analyze_lines(lines)
        stats = r.channels["gsr"]
        expected = CHANNEL_REGISTRY["gsr"]["expected_hz"]
        self.assertAlmostEqual(stats.observed_hz, expected, delta=expected * 0.05)
        self.assertEqual(stats.count, 1500)

    def test_in_range_percentage(self) -> None:
        lines = []
        for i in range(80):
            lines.append(json.dumps({"t": i * 0.02, "ch": "gsr",
                                     "v": 2048, "q": "ok", "boot": "x"}))
        for i in range(20):
            lines.append(json.dumps({"t": (80 + i) * 0.02, "ch": "gsr",
                                     "v": 0, "q": "out-of-range", "boot": "x"}))
        r = analyze_lines(lines)
        stats = r.channels["gsr"]
        self.assertAlmostEqual(stats.in_range_pct, 80.0, places=4)
        self.assertEqual(stats.q_counts["out-of-range"], 20)

    def test_gap_detection(self) -> None:
        """Gap > 2× expected period must be counted exactly once."""
        # GSR @ 50 Hz: expected period 20 ms; gap threshold 40 ms.
        lines = [
            json.dumps({"t": 0.00, "ch": "gsr", "v": 1, "q": "ok"}),
            json.dumps({"t": 0.02, "ch": "gsr", "v": 1, "q": "ok"}),
            # 200 ms gap = 10× expected period
            json.dumps({"t": 0.24, "ch": "gsr", "v": 1, "q": "ok"}),
            json.dumps({"t": 0.26, "ch": "gsr", "v": 1, "q": "ok"}),
        ]
        r = analyze_lines(lines)
        self.assertEqual(r.channels["gsr"].gap_count, 1)

    def test_event_channel_no_rate_check(self) -> None:
        """ppg-rr is event-typed; no expected_hz, no gap_count.

        Even with irregular timing, no gaps should be flagged."""
        lines = [
            json.dumps({"t": 1.0, "ch": "ppg-rr", "v": 1000, "q": "ok",
                        "conf": 1.4}),
            json.dumps({"t": 10.0, "ch": "ppg-rr", "v": 1100, "q": "ok",
                        "conf": 1.5}),
        ]
        r = analyze_lines(lines)
        self.assertEqual(r.channels["ppg-rr"].gap_count, 0)

    def test_multiple_boot_ids_recorded(self) -> None:
        lines = [
            json.dumps({"t": 0.0, "ch": "gsr", "v": 1, "q": "ok",
                        "boot": "aaa"}),
            json.dumps({"t": 0.1, "ch": "gsr", "v": 1, "q": "ok",
                        "boot": "bbb"}),
        ]
        r = analyze_lines(lines)
        self.assertEqual(r.boot_ids, {"aaa", "bbb"})

    def test_unknown_channel_passes_through(self) -> None:
        """Channels not in CHANNEL_REGISTRY still get counted."""
        r = analyze_lines([
            json.dumps({"t": 0.0, "ch": "speculative-channel",
                        "v": 1.0, "q": "ok"}),
        ])
        self.assertIn("speculative-channel", r.channels)
        self.assertEqual(r.channels["speculative-channel"].count, 1)


class FixtureTests(unittest.TestCase):

    def test_ppg_60s_good_fixture(self) -> None:
        r = analyze(FIXTURES / "ppg_60s_good.ndjson")
        self.assertEqual(r.parse_errors, 0)
        self.assertIn("ppg-hrv", r.channels)
        self.assertIn("ppg-rr", r.channels)
        hrv = r.channels["ppg-hrv"]
        self.assertEqual(hrv.count, 6000)
        self.assertAlmostEqual(hrv.observed_hz, 100.0, delta=5.0)
        self.assertEqual(hrv.gap_count, 0)
        self.assertAlmostEqual(hrv.in_range_pct, 100.0, places=4)

    def test_mlx_gsr_30s_good_fixture(self) -> None:
        r = analyze(FIXTURES / "mlx_gsr_30s_good.ndjson")
        self.assertEqual(r.parse_errors, 0)
        for ch in ("gsr", "temp-forehead", "temp-forehead.amb"):
            self.assertIn(ch, r.channels)
        gsr = r.channels["gsr"]
        self.assertEqual(gsr.count, 1500)
        self.assertAlmostEqual(gsr.observed_hz, 50.0, delta=2.5)
        self.assertEqual(gsr.gap_count, 0)
        mlx = r.channels["temp-forehead"]
        self.assertEqual(mlx.count, 120)
        self.assertAlmostEqual(mlx.observed_hz, 4.0, delta=0.2)

    def test_ppg_with_gap_fixture(self) -> None:
        r = analyze(FIXTURES / "ppg_60s_with_gap.ndjson")
        self.assertEqual(r.parse_errors, 0)
        hrv = r.channels["ppg-hrv"]
        # Gap of 0.5 s ≫ 2× 10 ms ⇒ exactly one gap.
        self.assertEqual(hrv.gap_count, 1)
        # 6000 - 50 samples elided
        self.assertEqual(hrv.count, 5950)

    def test_format_report_runs_clean(self) -> None:
        """format_report must produce a non-empty string for every fixture."""
        for name in ("ppg_60s_good.ndjson", "mlx_gsr_30s_good.ndjson",
                     "ppg_60s_with_gap.ndjson"):
            r = analyze(FIXTURES / name)
            out = format_report(r)
            self.assertGreater(len(out), 0)
            self.assertIn("capture:", out)


if __name__ == "__main__":
    unittest.main()
