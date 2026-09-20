"""Unit tests for tools/analyze_ambient_confounds.py."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from tools.analyze_ambient_confounds import (
    _cli,
    confound_report_to_json,
    format_confound_report,
)
from tools.analyze_dyadic_coherence import analyze_dyadic, synth_dyad


class SafetyInvariantTests(unittest.TestCase):
    """This tool's core safety property is architectural, not run-time —
    it must never invoke SDR/radio hardware at all. Verify by inspecting
    the actual source file, not just by running it, so this test fails
    loudly if that invariant is ever violated by a future edit."""

    def test_source_contains_no_process_invocation(self) -> None:
        src = Path(__file__).resolve().parent.parent / "tools" / "analyze_ambient_confounds.py"
        text = src.read_text(encoding="utf-8")
        # No mechanism for running an external process (shelling out to an
        # SDR tool, or anything else) should exist in this file at all --
        # not just "no transmit calls", no process invocation whatsoever.
        suspicious = re.findall(
            r"\b(subprocess|os\.system|os\.popen|Popen)\s*\(", text
        )
        self.assertEqual(suspicious, [], "found subprocess/shell invocation code")

    def test_source_never_names_a_specific_sdr_cli_invocation(self) -> None:
        src = Path(__file__).resolve().parent.parent / "tools" / "analyze_ambient_confounds.py"
        text = src.read_text(encoding="utf-8")
        # The docstring discusses hackrf_sweep/hackrf_transfer only as
        # prose examples of what an operator might run SEPARATELY -- there
        # should be no runnable invocation of either as a command (e.g. no
        # occurrence immediately followed by a flag like "-t"/"-x"/"-r").
        self.assertNotRegex(text, r"hackrf_(transfer|sweep)\s+-[a-zA-Z]")


class ConfoundReportTests(unittest.TestCase):

    def test_confounded_pair_is_flagged(self) -> None:
        ambient, target = synth_dyad(correlated=True)
        report = analyze_dyadic(ambient, target, n_surrogates=100)
        text = format_confound_report(report, ambient_channel="a", target_channel="b")
        self.assertIn("CONFOUND RISK", text)

    def test_clean_pair_is_not_flagged(self) -> None:
        ambient, target = synth_dyad(correlated=False)
        report = analyze_dyadic(ambient, target, n_surrogates=100)
        text = format_confound_report(report, ambient_channel="a", target_channel="b")
        self.assertIn("no ambient confound detected", text)
        self.assertNotIn("CONFOUND RISK", text)

    def test_json_report_has_confound_flagged_key_not_significant(self) -> None:
        ambient, target = synth_dyad(correlated=True)
        report = analyze_dyadic(ambient, target, n_surrogates=100)
        data = confound_report_to_json(report, ambient_channel="rf-power-dbm", target_channel="ppg-rr")
        self.assertIn("confound_flagged", data)
        self.assertNotIn("significant", data)
        self.assertEqual(data["ambient_channel"], "rf-power-dbm")
        self.assertEqual(data["target_channel"], "ppg-rr")


class CliSelfTestTests(unittest.TestCase):

    def test_confounded_self_test_exits_zero(self) -> None:
        self.assertEqual(_cli(["--self-test", "confounded", "--n-surrogates", "50"]), 0)

    def test_clean_self_test_exits_zero(self) -> None:
        self.assertEqual(_cli(["--self-test", "clean", "--n-surrogates", "50"]), 0)

    def test_missing_args_without_self_test_is_usage_error(self) -> None:
        self.assertEqual(_cli([]), 3)

    def test_missing_file_is_file_error(self) -> None:
        exit_code = _cli(["--ambient", "/nonexistent/path.ndjson", "--target", "/nonexistent/path2.ndjson"])
        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
