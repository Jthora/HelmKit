"""Tests for tools/replay_equivalence.py — firmware-vs-host equivalence checks (Track N, N-H4 / gate N-G6)."""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
sys.path.insert(0, os.path.dirname(__file__))
import analyze_combat_session as A  # noqa: E402
import replay_equivalence as R  # noqa: E402
import test_analyze_combat_session as T  # noqa: E402


def write_capture(path: str, *, drop_breaths: bool = False, extra_scr: int = 0, wrong_mode: bool = False) -> None:
    """A synthetic capture whose 'firmware' derived lines are produced by the host references themselves."""
    t0, t1 = 0.0, 240.0
    rows = []
    thermal = T.thermal_stream(t0, t1, 15.0)
    eda = T.eda_stream(t0, t1, [30.0, 90.0, 150.0])
    rr = T.rr_stream(t0, t1, lambda t: 70.0)
    rows += thermal + eda + rr
    cues = [(1.0, "session-start"), (10.0, "prime"), (20.0, "round-start"), (140.0, "round-end"), (60.0, "tally"), (239.0, "session-end")]
    rows += [{"t": t, "ch": "cue", "v": v} for t, v in cues]
    # host references -> "firmware" lines
    th = [A.Sample(r["t"], r["v"], r.get("q", "ok")) for r in thermal]
    breaths = A.breath_times(th)
    if drop_breaths:
        breaths = breaths[::2]
    rows += [{"t": bt, "ch": "resp-thermal", "v": 15.0, "q": "ok"} for bt in breaths]
    ed = [A.Sample(r["t"], r["v"], r.get("q", "ok")) for r in eda]
    scrs = A.scr_times(ed) + [200.0 + i for i in range(extra_scr)]
    rows += [{"t": st, "ch": "scr", "v": 60.0, "q": "ok"} for st in scrs]
    # the mode lines the firmware would have emitted = the host machine replayed on this very capture
    rows.sort(key=lambda r: r["t"])
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    modes = R._host_modes(A.load_capture(path))
    if wrong_mode:
        modes = modes[:-1]
    rows += [{"t": t, "ch": "cue", "v": "mode:" + name} for t, name in modes]
    rows.sort(key=lambda r: r["t"])
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


class Equivalence(unittest.TestCase):
    def test_self_consistent_capture_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "eq.ndjson")
            write_capture(p)
            rep = R.compare(p)
            by = {c.name: c for c in rep.checks}
            self.assertTrue(by["breathing"].performed and by["breathing"].ok, by["breathing"].detail)
            self.assertTrue(by["scr"].performed and by["scr"].ok, by["scr"].detail)
            self.assertTrue(by["modes"].performed, by["modes"].detail)
            self.assertFalse(by["rr"].performed)
            self.assertTrue(rep.ok, R.format_report(rep))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(R.main([p]), 0)
                self.assertEqual(R.main([p, "--json"]), 0)

    def test_divergence_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "half.ndjson")
            write_capture(p, drop_breaths=True)
            rep = R.compare(p)
            self.assertFalse({c.name: c for c in rep.checks}["breathing"].ok)
            write_capture(p, extra_scr=3)
            self.assertFalse({c.name: c for c in R.compare(p).checks}["scr"].ok)
            write_capture(p, wrong_mode=True)
            self.assertFalse({c.name: c for c in R.compare(p).checks}["modes"].ok)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(R.main([p]), 2)
                self.assertEqual(R.main([os.path.join(tmp, "missing")]), 1)

    def test_nothing_to_check_is_a_pass_with_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "raw.ndjson")
            with open(p, "w", encoding="utf-8") as fh:
                for r in T.rr_stream(0.0, 60.0, lambda t: 60.0):
                    fh.write(json.dumps(r) + "\n")
            rep = R.compare(p)
            self.assertTrue(rep.ok)
            self.assertTrue(all(not c.performed for c in rep.checks))


if __name__ == "__main__":
    unittest.main()
