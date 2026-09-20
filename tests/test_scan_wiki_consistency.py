"""Unit tests for tools/scan_wiki_consistency.py.

Uses small synthetic wikitext fixtures rather than the real
docs/wiki_cache/ corpus, so these tests are deterministic and don't
break every time the wiki drops new content.
"""

from __future__ import annotations

import unittest

from tools.scan_wiki_consistency import (
    Conflict,
    extract_infobox_pairs,
    extract_numeric_claims,
    find_cross_page_label_conflicts,
    find_within_page_conflicts,
    is_known_issue,
)


class NumericClaimExtractionTests(unittest.TestCase):

    def test_extracts_number_and_unit(self) -> None:
        claims = extract_numeric_claims("Drive voltage is 200 V across the gap.")
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].value, 200.0)
        self.assertEqual(claims[0].unit, "V")

    def test_extracts_multiple_claims_in_order(self) -> None:
        claims = extract_numeric_claims("Gap 0.2 mm, width 0.3 mm, drive 200 V.")
        self.assertEqual([c.value for c in claims], [0.2, 0.3, 200.0])
        self.assertEqual([c.unit for c in claims], ["mm", "mm", "V"])

    def test_handles_thousands_separator(self) -> None:
        claims = extract_numeric_claims("Resistance 1,000 Ω.")
        self.assertEqual(claims[0].value, 1000.0)

    def test_math_ratio_treated_as_percent_when_in_unit_interval(self) -> None:
        claims = extract_numeric_claims(r"<math>\tau \geq 0.70</math>")
        self.assertEqual(len(claims), 1)
        self.assertAlmostEqual(claims[0].value, 70.0)
        self.assertEqual(claims[0].unit, "%")

    def test_math_ratio_outside_unit_interval_is_ignored(self) -> None:
        # e.g. "m = 2.5" inside a math block shouldn't be misread as 250%.
        claims = extract_numeric_claims(r"<math>k \geq 2.5</math>")
        self.assertEqual(claims, [])

    def test_canonicalizes_unit_aliases(self) -> None:
        claims = extract_numeric_claims("Inductance 6 uH, field 27 uT.")
        units = {c.unit for c in claims}
        self.assertIn("µH", units)
        self.assertIn("µT", units)


class InfoboxExtractionTests(unittest.TestCase):

    def test_extracts_paired_label_data(self) -> None:
        text = (
            "{{Infobox\n"
            "| title = Foo\n"
            "| label8 = Trace gap\n"
            "| data8 = 0.2 mm\n"
            "| label9 = Max drive voltage\n"
            "| data9 = 200 V\n"
            "}}\n"
        )
        pairs = extract_infobox_pairs(text)
        as_dict = {p.label: p.value for p in pairs}
        self.assertEqual(as_dict["Trace gap"], "0.2 mm")
        self.assertEqual(as_dict["Max drive voltage"], "200 V")

    def test_ignores_unpaired_label_or_data(self) -> None:
        text = "{{Infobox\n| label3 = Orphan label\n| data9 = Orphan data\n}}\n"
        self.assertEqual(extract_infobox_pairs(text), [])

    def test_pair_carries_parsed_claims(self) -> None:
        text = "{{Infobox\n| label1 = Drive voltage\n| data1 = 200 V\n}}\n"
        pairs = extract_infobox_pairs(text)
        self.assertEqual(len(pairs[0].claims), 1)
        self.assertEqual(pairs[0].claims[0].value, 200.0)


class CrossPageLabelConflictTests(unittest.TestCase):

    def _page(self, label: str, value: str) -> str:
        return f"{{{{Infobox\n| label1 = {label}\n| data1 = {value}\n}}}}\n"

    def test_flags_same_label_different_value_across_pages(self) -> None:
        pages = {
            "page_a": self._page("Drive voltage", "200 V"),
            "page_b": self._page("Drive voltage", "400 V"),
        }
        conflicts = find_cross_page_label_conflicts(pages)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].kind, "cross_page_label")
        self.assertEqual(conflicts[0].confidence, "high")

    def test_does_not_flag_same_label_same_value(self) -> None:
        pages = {
            "page_a": self._page("Drive voltage", "200 V"),
            "page_b": self._page("Drive voltage", "200 V"),
        }
        self.assertEqual(find_cross_page_label_conflicts(pages), [])

    def test_does_not_flag_within_tolerance(self) -> None:
        pages = {
            "page_a": self._page("Drive voltage", "200 V"),
            "page_b": self._page("Drive voltage", "200.5 V"),  # 0.25% diff
        }
        self.assertEqual(find_cross_page_label_conflicts(pages), [])

    def test_does_not_flag_different_labels(self) -> None:
        pages = {
            "page_a": self._page("Drive voltage", "200 V"),
            "page_b": self._page("Trace gap", "0.2 mm"),
        }
        self.assertEqual(find_cross_page_label_conflicts(pages), [])

    def test_does_not_flag_single_occurrence(self) -> None:
        pages = {"page_a": self._page("Drive voltage", "200 V")}
        self.assertEqual(find_cross_page_label_conflicts(pages), [])


class WithinPageConflictTests(unittest.TestCase):

    def test_flags_distinctive_keyword_with_contradicting_nearby_value(self) -> None:
        text = (
            "{{Infobox\n| label1 = BST tunability target\n| data1 = <math>\\tau \\geq 0.70</math>\n}}\n\n"
            "Predicted BST tunability is only about 35% in practice, well short of target.\n"
        )
        conflicts = find_within_page_conflicts("test_page", text)
        self.assertTrue(any(c.label == "BST tunability target" for c in conflicts))

    def test_does_not_flag_when_values_agree(self) -> None:
        text = (
            "{{Infobox\n| label1 = Drive voltage\n| data1 = 200 V\n}}\n\n"
            "The drive voltage of 200 V is applied across the gap.\n"
        )
        self.assertEqual(find_within_page_conflicts("test_page", text), [])

    def test_ignores_infobox_self_reference(self) -> None:
        # The infobox block itself is stripped before scanning the body,
        # so the pair should never conflict with its own restatement.
        text = "{{Infobox\n| label1 = Drive voltage\n| data1 = 200 V\n}}\n"
        self.assertEqual(find_within_page_conflicts("test_page", text), [])

    def test_no_keyword_match_means_no_conflict(self) -> None:
        text = (
            "{{Infobox\n| label1 = Drive voltage\n| data1 = 200 V\n}}\n\n"
            "Somewhere else entirely unrelated, a trace is 0.3 mm wide.\n"
        )
        self.assertEqual(find_within_page_conflicts("test_page", text), [])

    def test_confidence_is_always_low(self) -> None:
        text = (
            "{{Infobox\n| label1 = BST tunability target\n| data1 = <math>\\tau \\geq 0.70</math>\n}}\n\n"
            "BST tunability measured at 35% in the lab.\n"
        )
        conflicts = find_within_page_conflicts("test_page", text)
        self.assertTrue(all(c.confidence == "low" for c in conflicts))


class KnownIssuesTests(unittest.TestCase):

    def test_matching_issue_suppresses_conflict(self) -> None:
        conflict = Conflict(
            kind="within_page_keyword", confidence="low", page="smart_composite_fill",
            label="BST tunability target", value_a="70%", value_b="35%", context="tunability blah",
        )
        known_issues = [{"page": "smart_composite_fill", "match": "BST tunability", "reason": "x"}]
        self.assertIsNotNone(is_known_issue(conflict, known_issues))

    def test_non_matching_page_does_not_suppress(self) -> None:
        conflict = Conflict(
            kind="within_page_keyword", confidence="low", page="other_page",
            label="BST tunability target", value_a="70%", value_b="35%", context="tunability blah",
        )
        known_issues = [{"page": "smart_composite_fill", "match": "BST tunability", "reason": "x"}]
        self.assertIsNone(is_known_issue(conflict, known_issues))

    def test_non_matching_text_does_not_suppress(self) -> None:
        conflict = Conflict(
            kind="within_page_keyword", confidence="low", page="smart_composite_fill",
            label="Cure protocol", value_a="120C", value_b="80C", context="cure temperature",
        )
        known_issues = [{"page": "smart_composite_fill", "match": "BST tunability", "reason": "x"}]
        self.assertIsNone(is_known_issue(conflict, known_issues))

    def test_empty_known_issues_suppresses_nothing(self) -> None:
        conflict = Conflict(
            kind="cross_page_label", confidence="high", page="a", label="L", value_a="1", value_b="2", context="",
        )
        self.assertIsNone(is_known_issue(conflict, []))


if __name__ == "__main__":
    unittest.main()
