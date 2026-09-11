"""Tests for tools/capture_service.py — the log sink's pure line handling (Track N, N-H1 / N-L3)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import capture_service as CS  # noqa: E402


class FakeClock:
    def __init__(self, t0: float = 1_700_000_000.0) -> None:
        self.t = t0

    def __call__(self) -> float:
        return self.t


class SinkBehaviour(unittest.TestCase):
    def _lines(self, boot: str, n0: int = 1):
        yield json.dumps({"t": 0.5, "kind": "hello", "boot": boot, "n": n0})
        yield json.dumps({"t": 0.6, "kind": "boot", "reason": "poweron", "boot": boot, "n": n0 + 1})
        yield json.dumps({"t": 1.0, "ch": "gsr", "v": 1500, "q": "ok", "boot": boot, "n": n0 + 2})
        yield json.dumps({"t": 5.0, "ch": "hb", "v": 5.0, "q": "ok", "drops": 0, "boot": boot, "n": n0 + 3})
        yield json.dumps({"t": 6.0, "ch": "cue", "v": "session-start", "boot": boot, "n": n0 + 6})   # n0+4, n0+5 lost

    def test_one_file_per_boot_with_wallclock_and_acks(self):
        with tempfile.TemporaryDirectory() as tmp:
            clock = FakeClock()
            sink = CS.Sink(tmp, label="bench", now=clock)
            acks = 0
            for raw in self._lines("aaaa"):
                clock.t += 1.0
                acks += 1 if sink.handle_line(raw)["ack"] else 0
            self.assertEqual(acks, 1)                       # exactly the hb line
            self.assertEqual(sink.lost(), 2)
            first = sink.file
            self.assertIsNotNone(first)
            self.assertIn("aaaa", first.name)
            self.assertIn("bench", first.name)
            for raw in self._lines("bbbb", n0=1):           # a new boot: a new file
                clock.t += 1.0
                sink.handle_line(raw)
            sink.close()
            second = sink.file
            self.assertNotEqual(first, second)
            self.assertTrue(first.exists() and second.exists())
            rows = [json.loads(l) for l in open(first, encoding="utf-8")]
            samples = [r for r in rows if "ch" in r]
            self.assertTrue(all("t_wallclock" in r for r in samples))
            # offset fixed at the boot line: wallclock - t is constant across the boot
            offs = {round(r["t_wallclock"] - r["t"], 3) for r in samples}
            self.assertEqual(len(offs), 1)
            self.assertTrue(all("t_wallclock" not in r for r in rows if "kind" in r))
            idx = json.loads((sink.out_dir / "sessions.json").read_text())
            self.assertEqual(len(idx), 2)
            self.assertEqual(idx[0]["lost"], 2)
            self.assertEqual(idx[0]["lines"], 5)

    def test_rejects_are_counted_and_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = CS.Sink(tmp, now=FakeClock())
            self.assertEqual(sink.handle_line("garbage")["kind"], "reject")
            self.assertEqual(sink.handle_line("[1,2]")["kind"], "reject")
            self.assertEqual(sink.handle_line("")["kind"], "empty")
            sink.handle_line(json.dumps({"t": 1.0, "ch": "gsr", "v": 1, "boot": "x"}))   # no boot line: a file still opens
            sink.close()
            self.assertEqual(sink.rejects, 2)
            self.assertIn("x", sink.file.name)
            rej = os.path.join(tmp, "rejects.ndjson")
            self.assertTrue(os.path.exists(rej))
            self.assertEqual(len(open(rej, encoding="utf-8").read().splitlines()), 2)

    def test_existing_wallclock_is_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = CS.Sink(tmp, now=FakeClock())
            sink.handle_line(json.dumps({"t": 0.1, "kind": "boot", "boot": "w"}))
            sink.handle_line(json.dumps({"t": 2.0, "t_wallclock": 123.0, "ch": "gsr", "v": 1, "boot": "w"}))
            sink.close()
            rows = [json.loads(l) for l in open(sink.file, encoding="utf-8")]
            self.assertEqual(rows[1]["t_wallclock"], 123.0)

    def test_fixture_replay_and_disk_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = os.path.join(tmp, "fx.ndjson")
            with open(fx, "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"t": 0.1, "kind": "hello", "boot": "f"}) + "\n")
                for i in range(10):
                    fh.write(json.dumps({"t": 1.0 + i, "ch": "gsr", "v": 1500, "q": "ok", "boot": "f", "n": i + 1}) + "\n")
            out = os.path.join(tmp, "out")
            rc = CS.main(["--replay-fixture", fx, "--out", out, "--min-free-mb", "0"])
            self.assertEqual(rc, 0)
            self.assertTrue(any(f.endswith(".ndjson") for f in os.listdir(out)))
            self.assertTrue(CS.free_mb(out) >= 0.0)
            self.assertEqual(CS.main(["--replay-fixture", fx, "--out", out, "--min-free-mb", "1e9"]), 3)
            self.assertEqual(CS.main(["--replay-fixture", os.path.join(tmp, "missing"), "--out", out, "--min-free-mb", "0"]), 1)


if __name__ == "__main__":
    unittest.main()
