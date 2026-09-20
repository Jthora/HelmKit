"""Unit tests for tools/forced_choice_protocol.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.forced_choice_protocol import (
    commitment_hash,
    generate_targets,
    score_session,
    self_test_session,
    write_targets_file,
)


class TargetGenerationTests(unittest.TestCase):

    def test_generate_targets_correct_length_and_range(self) -> None:
        targets = generate_targets(50, 4, seed=1)
        self.assertEqual(len(targets), 50)
        self.assertTrue(all(0 <= t < 4 for t in targets))

    def test_same_seed_is_reproducible(self) -> None:
        a = generate_targets(30, 6, seed=99)
        b = generate_targets(30, 6, seed=99)
        self.assertEqual(a, b)

    def test_no_seed_uses_system_random_and_differs_run_to_run(self) -> None:
        a = generate_targets(200, 4, seed=None)
        b = generate_targets(200, 4, seed=None)
        # Astronomically unlikely to collide for 200 trials of 4 choices.
        self.assertNotEqual(a, b)

    def test_commitment_hash_is_deterministic(self) -> None:
        targets = [0, 1, 2, 3, 0]
        self.assertEqual(commitment_hash(targets), commitment_hash(list(targets)))

    def test_commitment_hash_changes_if_targets_change(self) -> None:
        a = commitment_hash([0, 1, 2])
        b = commitment_hash([0, 1, 3])
        self.assertNotEqual(a, b)

    def test_write_targets_file_round_trips(self) -> None:
        with TemporaryDirectory() as td:
            out = Path(td) / "targets.json"
            doc = write_targets_file(out, [0, 1, 2, 3], k=4)
            on_disk = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(on_disk["commitment_sha256"], doc["commitment_sha256"])
            self.assertEqual(on_disk["commitment_sha256"], commitment_hash([0, 1, 2, 3]))

    def test_write_targets_file_refuses_overwrite(self) -> None:
        with TemporaryDirectory() as td:
            out = Path(td) / "targets.json"
            write_targets_file(out, [0, 1], k=2)
            with self.assertRaises(FileExistsError):
                write_targets_file(out, [1, 0], k=2)


class ScoreSessionTests(unittest.TestCase):

    def test_perfect_score_is_all_hits(self) -> None:
        targets = [0, 1, 2, 3, 0, 1, 2, 3]
        result = score_session(targets, list(targets), k_alternatives=4)
        self.assertEqual(result["hits"], len(targets))
        self.assertEqual(result["hit_rate"], 1.0)
        self.assertLess(result["bf01"], result["bf10"])  # strongly favors H1

    def test_rejects_mismatched_lengths(self) -> None:
        with self.assertRaises(ValueError):
            score_session([0, 1, 2], [0, 1], k_alternatives=4)

    def test_rejects_empty_session(self) -> None:
        with self.assertRaises(ValueError):
            score_session([], [], k_alternatives=4)

    def test_rejects_out_of_range_values(self) -> None:
        with self.assertRaises(ValueError):
            score_session([0, 5], [0, 1], k_alternatives=4)

    def test_chance_rate_matches_1_over_k(self) -> None:
        result = score_session([0, 1, 2, 3], [1, 2, 3, 0], k_alternatives=4)
        self.assertAlmostEqual(result["chance_rate"], 0.25)


class SelfTestSessionTests(unittest.TestCase):

    def test_null_mode_does_not_show_strong_h1_evidence(self) -> None:
        result = self_test_session(mode="null", n_trials=300, k_alternatives=4)
        self.assertLess(result["bf10"], 3.0, "null-mode session should not show even anecdotal H1 evidence")

    def test_psi_mode_shows_elevated_hit_rate_and_h1_evidence(self) -> None:
        result = self_test_session(mode="psi", n_trials=300, k_alternatives=4, true_hit_rate=0.35)
        self.assertGreater(result["hit_rate"], 0.25)
        self.assertGreater(result["bf10"], 3.0, "psi-mode session should show at least moderate H1 evidence")

    def test_deterministic_given_fixed_seed(self) -> None:
        a = self_test_session(mode="psi", seed=42)
        b = self_test_session(mode="psi", seed=42)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
