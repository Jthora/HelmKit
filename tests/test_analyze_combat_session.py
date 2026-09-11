"""Tests for tools/analyze_combat_session.py — Track M host-side sensing reference (M-F2..M-F5) on a synthetic sparring session."""
from __future__ import annotations

import io
import contextlib
import json
import math
import os
import random
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import analyze_combat_session as M  # noqa: E402


def rr_stream(t0: float, t1: float, bpm_fn, jitter_ms: float = 15.0, seed: int = 1, q_bad_every: int = 0):
    """RR events between t0 and t1 with instantaneous rate bpm_fn(t) plus Gaussian jitter (the 'HRV')."""
    rnd = random.Random(seed)
    out, t, k = [], t0, 0
    while t < t1:
        rr = 60000.0 / bpm_fn(t) + rnd.gauss(0.0, jitter_ms)
        t += rr / 1000.0
        k += 1
        q = "out-of-range" if (q_bad_every and k % q_bad_every == 0) else "ok"
        out.append({"t": round(t, 3), "ch": "ppg-rr", "v": int(rr), "q": q})
    return out


def thermal_stream(t0: float, t1: float, breaths_per_min: float, base_c: float = 33.0, slope_c_per_min: float = 0.0,
                   amp_c: float = 0.15, fs: float = 4.0, seed: int = 2, ch: str = "temp-nose"):
    rnd = random.Random(seed)
    out, n = [], int((t1 - t0) * fs)
    for i in range(n):
        t = t0 + i / fs
        v = base_c + slope_c_per_min * (t - t0) / 60.0 + amp_c * math.sin(2 * math.pi * breaths_per_min / 60.0 * (t - t0)) + rnd.gauss(0.0, 0.01)
        out.append({"t": round(t, 3), "ch": ch, "v": round(v, 3), "q": "ok"})
    return out


def eda_stream(t0: float, t1: float, scr_times: list[float], level: float = 2000.0, fs: float = 20.0, seed: int = 3, ch: str = "eda-forehead"):
    rnd = random.Random(seed)
    out, n = [], int((t1 - t0) * fs)
    for i in range(n):
        t = t0 + i / fs
        v = level
        for ts in scr_times:                      # each SCR: 1.5 s ramp up of 3 % then a 6 s decay
            d = t - ts
            if 0 <= d < 1.5:
                v += 0.03 * level * d / 1.5
            elif 1.5 <= d < 7.5:
                v += 0.03 * level * math.exp(-(d - 1.5) / 2.0)
        out.append({"t": round(t, 3), "ch": ch, "v": round(v + rnd.gauss(0.0, 0.5), 2), "q": "ok"})
    return out


def skin_stream(t0: float, t1: float, slope_c_per_min: float, ch: str = "temp-skin.L", fs: float = 5.0):
    return [{"t": round(t0 + i / fs, 3), "ch": ch, "v": round(34.0 + slope_c_per_min * (i / fs) / 60.0, 3), "q": "ok"} for i in range(int((t1 - t0) * fs))]


def still_stream(windows_still: list[tuple[float, float]], t0: float, t1: float):
    out = []
    for i in range(int(t1 - t0)):
        t = t0 + i
        v = 1 if any(a <= t < b for a, b in windows_still) else 0
        out.append({"t": float(t), "ch": "still", "v": v, "q": "ok"})
    return out


def build_session(path: str, with_imu: bool = True, sweat: bool = False, second_rr: bool = False):
    """2 rounds of 120 s with 90 s rest, 60 s warm-up before, 90 s tail after. Returns the round windows."""
    recs = [{"t": 0.0, "kind": "hello", "schema": "0.1"}]
    cues = [(1.0, "session-start"), (60.0, "round-start"), (180.0, "round-end"), (270.0, "round-start"), (390.0, "round-end"),
            (100.0, "tally"), (480.0, "session-end")]
    for t, v in cues:
        recs.append({"t": t, "ch": "cue", "v": v, "q": "ok"})
    rounds = [(60.0, 180.0), (270.0, 390.0)]

    def bpm(t):
        if 60 <= t < 180 or 270 <= t < 390:
            return 150.0
        for a, b in rounds:                       # exponential recovery after each round
            if b <= t < b + 90:
                return 70.0 + 80.0 * math.exp(-(t - b) / 30.0)
        return 65.0

    recs += rr_stream(1.0, 480.0, bpm, jitter_ms=20.0)
    if second_rr:
        recs += [dict(r, ch="ecg-rr") for r in rr_stream(1.0, 480.0, bpm, jitter_ms=20.0, seed=7)]
    # breathing: 12/min at rest, 30/min in-round; nose tip cools 0.3 °C/min during rounds (arousal), warms in rest
    th = []
    segs = [(1.0, 60.0, 12.0, 0.0), (60.0, 180.0, 30.0, -0.3), (180.0, 270.0, 12.0, 0.2), (270.0, 390.0, 30.0, -0.3), (390.0, 480.0, 12.0, 0.2)]
    for a, b, br, sl in segs:
        th += thermal_stream(a, b, br, slope_c_per_min=sl, seed=int(a))
    recs += th
    recs += eda_stream(1.0, 480.0, scr_times=[20.0, 35.0, 200.0, 215.0, 230.0, 400.0])
    recs += skin_stream(1.0, 480.0, 0.2 if sweat else 0.0)
    if with_imu:
        recs += still_stream([(1.0, 60.0), (180.0, 270.0), (390.0, 480.0)], 1.0, 480.0)
        recs += [{"t": 90.0, "ch": "impact", "v": 14.0, "q": "ok"}, {"t": 300.0, "ch": "impact", "v": 22.0, "q": "ok"}]
    recs.sort(key=lambda r: r["t"])
    with open(path, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return rounds


class SessionAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = os.path.join(cls.tmp.name, "session.ndjson")
        build_session(cls.path)
        cls.rep = M.analyze(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_rounds_from_cues(self):
        self.assertEqual([(r.t_start, r.t_end) for r in self.rep.rounds], [(60.0, 180.0), (270.0, 390.0)])
        self.assertEqual(len(self.rep.rests), 2)
        self.assertEqual(self.rep.tallies, 1)

    def test_in_round_hr_is_coarse_and_right(self):
        for r in self.rep.rounds:
            self.assertIsNotNone(r.hr_mean_bpm)
            self.assertAlmostEqual(r.hr_mean_bpm, 150.0, delta=6.0)
            self.assertGreaterEqual(r.hr_windows_reported, 0.8 * r.hr_windows_total)

    def test_breathing_rate_from_thermal(self):
        for r in self.rep.rounds:
            self.assertAlmostEqual(r.breaths_per_min, 30.0, delta=3.0)
        for w in self.rep.rests:
            self.assertAlmostEqual(w.breaths_per_min, 12.0, delta=2.0)

    def test_arousal_slope_sign(self):
        for w in self.rep.rests:
            self.assertGreater(w.nose_slope_c_per_min, 0.05)       # nose tip re-warms while resting

    def test_hrv_only_in_still_rest_with_imu(self):
        self.assertEqual(self.rep.still_source, "imu")
        for w in self.rep.rests:
            self.assertEqual(w.still_source, "imu")
            self.assertIsNotNone(w.rmssd_ms)
            self.assertGreater(w.n_beats, 60)
            self.assertGreater(w.rmssd_ms, 10.0)                    # 20 ms jitter -> RMSSD ~ 28 ms

    def test_recovery_slope_negative(self):
        for w in self.rep.rests:
            self.assertIsNotNone(w.hr_recovery_bpm_per_min)
            self.assertLess(w.hr_recovery_bpm_per_min, -20.0)

    def test_scr_rate_counts_injected_responses(self):
        rest1 = self.rep.rests[0]                                      # SCRs at 200, 215, 230 in a 90 s rest -> 2/min
        self.assertEqual(self.rep.eda_channel, "eda-forehead")
        rnd1 = self.rep.rounds[0]
        self.assertEqual(rnd1.eda_quality, "ok")
        self.assertIsNotNone(rnd1.scr_per_min)
        self.assertLess(rnd1.scr_per_min, 1.0)                          # no SCRs injected in round 1
        # rest windows are summarised for HRV; check the detector directly on the rest span
        cap = M.load_capture(self.path)
        times = M.scr_times(cap.numeric["eda-forehead"])
        inside = [t for t in times if rest1.t_start <= t < rest1.t_end]
        self.assertEqual(len(inside), 3)

    def test_impacts(self):
        self.assertEqual(self.rep.impacts_total, 2)
        self.assertEqual(self.rep.rounds[1].impact_peak_g, 22.0)


class SessionWithoutImuAndWithSweat(unittest.TestCase):
    def test_assumed_still_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.ndjson")
            build_session(p, with_imu=False)
            rep = M.analyze(p)
            self.assertEqual(rep.still_source, "assumed (no IMU)")
            self.assertTrue(any("ASSUMED still" in n for n in rep.notes))
            self.assertTrue(all(w.still_source == "assumed (no IMU)" for w in rep.rests))
            self.assertEqual(rep.impacts_total, 0)

    def test_sweat_rule_blocks_eda(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.ndjson")
            build_session(p, sweat=True)
            rep = M.analyze(p)
            for r in rep.rounds:
                self.assertEqual(r.eda_quality, "sweat")
                self.assertIsNone(r.scr_per_min)

    def test_two_sources_agree(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.ndjson")
            build_session(p, second_rr=True)
            rep = M.analyze(p)
            self.assertEqual(sorted(rep.rr_channels), ["ecg-rr", "ppg-rr"])
            self.assertAlmostEqual(rep.rounds[0].hr_mean_bpm, 150.0, delta=6.0)


class FusionRules(unittest.TestCase):
    def test_disagreeing_low_quality_sources_report_nothing(self):
        a = [(5.0, 150.0, "low")]
        b = [(5.0, 120.0, "low")]
        out = M.fuse_hr({"a": a, "b": b})
        self.assertIsNone(out[0].hr_bpm)
        self.assertEqual(out[0].quality, "disagree")

    def test_single_good_source_wins_a_disagreement(self):
        out = M.fuse_hr({"a": [(5.0, 150.0, "ok")], "b": [(5.0, 120.0, "low")]})
        self.assertEqual(out[0].hr_bpm, 150.0)

    def test_single_low_quality_source_is_withheld(self):
        out = M.fuse_hr({"a": [(5.0, 150.0, "low")]})
        self.assertIsNone(out[0].hr_bpm)
        self.assertEqual(out[0].quality, "low")

    def test_hr_window_quality_needs_80_percent_in_range(self):
        rr = [M.Sample(t, 500.0, "ok" if i % 2 else "out-of-range") for i, t in enumerate(x * 0.5 for x in range(40))]
        w = M.hr_windows(rr, M.Window("w", 0.0, 10.0))
        self.assertEqual(w[0][2], "low")

    def test_no_hrv_in_short_or_moving_rest(self):
        rr = [M.Sample(t, 800.0) for t in [x * 0.8 for x in range(200)]]
        still_moving = [M.Sample(float(t), 0.0) for t in range(160)]
        f = M.still_fraction(still_moving, M.Window("r", 0.0, 100.0))
        self.assertEqual(f, 0.0)
        rmssd, n = M.rmssd_in_window(rr, M.Window("r", 0.0, 100.0))
        self.assertEqual(rmssd, 0.0)                                   # constant RR: the math is fine, the GATE is what withholds it
        self.assertGreater(n, 100)


class Modes(unittest.TestCase):
    def test_session_flow(self):
        m = M.CombatModes()
        m.event(0.0, "session-start")
        self.assertEqual(m.mode, M.CombatModes.TRANQUIL)
        self.assertTrue(m.pacer.enabled)
        for t in range(1, 30):
            m.tick(float(t), hr_bpm=64.0 + (t % 3), still=True)
        self.assertAlmostEqual(m.resting_hr, 64.0)
        m.event(30.0, "prime")
        self.assertEqual(m.pacer.pattern, "prime")
        m.event(60.0, "round-start")
        self.assertEqual(m.mode, M.CombatModes.COMBAT_SUSTAIN)
        self.assertFalse(m.pacer.enabled)
        m.tick(90.0, hr_bpm=150.0, still=False, impact_g=14.0)
        self.assertIn((90.0, "impact:14g"), m.cues)
        m.event(100.0, "tally")
        self.assertEqual(m.tally, 1)
        m.event(180.0, "round-end")
        self.assertEqual(m.mode, M.CombatModes.RECOVER)
        self.assertEqual(m.pacer.pattern, "cyclic-sigh")
        m.tick(200.0, hr_bpm=120.0, still=True)
        self.assertEqual(m.mode, M.CombatModes.RECOVER)               # not yet within 20 bpm of resting
        m.tick(230.0, hr_bpm=82.0, still=True)
        self.assertEqual(m.mode, M.CombatModes.TRANQUIL)               # recovered: back to resonance
        m.event(300.0, "session-end")
        self.assertIsNone(m.mode)
        self.assertIn((300.0, "summary:tally=1"), m.cues)

    def test_prime_times_out_and_recover_times_out(self):
        m = M.CombatModes()
        m.event(0.0, "session-start")
        m.event(10.0, "prime")
        m.tick(69.0)
        self.assertEqual(m.mode, M.CombatModes.COMBAT_PRIME)
        m.tick(70.0)
        self.assertEqual(m.mode, M.CombatModes.TRANQUIL)
        m.event(100.0, "round-start")
        m.event(200.0, "round-end")
        m.tick(289.0, hr_bpm=140.0)
        self.assertEqual(m.mode, M.CombatModes.RECOVER)
        m.tick(290.0, hr_bpm=140.0)
        self.assertEqual(m.mode, M.CombatModes.TRANQUIL)

    def test_events_outside_a_session_are_ignored(self):
        m = M.CombatModes()
        m.event(5.0, "round-start")
        self.assertIsNone(m.mode)
        m.event(6.0, "session-start")
        m.event(7.0, "sanctuary")
        self.assertEqual(m.mode, M.CombatModes.SANCTUARY)
        self.assertEqual(m.pacer.pattern, "resonance")


class Cli(unittest.TestCase):
    def test_json_and_text_runs(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.ndjson")
            build_session(p)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = M.main([p, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(buf.getvalue())
            self.assertEqual(len(data["rounds"]), 2)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = M.main([p])
            self.assertEqual(rc, 0)
            self.assertIn("rests (RMSSD only in still windows", buf.getvalue())

    def test_missing_file(self):
        self.assertEqual(M.main(["/nonexistent/x.ndjson"]), 1)

    def test_no_cues_uses_schedule(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.ndjson")
            recs = rr_stream(0.0, 400.0, lambda t: 80.0)
            with open(p, "w") as fh:
                for r in recs:
                    fh.write(json.dumps(r) + "\n")
            rep = M.analyze(p, rounds=2, round_s=120.0, rest_s=60.0)
            self.assertEqual(len(rep.rounds), 2)
            self.assertTrue(any("no round cues" in n for n in rep.notes))


if __name__ == "__main__":
    unittest.main()


class Hardening(unittest.TestCase):
    """Track N, N-H2: the analyser never crashes on a capture and reports what it could not use."""

    def _dirty_session(self, tmp: str) -> str:
        path = os.path.join(tmp, "dirty.ndjson")
        build_session(path, with_imu=False)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("this is not json\n")
            fh.write("\x00\xff garbage \n")
            fh.write('{"t": NaN, "ch": "gsr", "v": 1}\n')
            fh.write('{"t": Infinity, "ch": "gsr", "v": 1}\n')
            fh.write('{"t": 1.0, "ch": "gsr", "v": true}\n')
            fh.write('{"t": 1.0, "ch": "gsr", "v": [1, 2]}\n')
            fh.write('{"t": 1.0, "ch": "gsr", "v": {"a": 1}}\n')
            fh.write('{"t": 1.0, "ch": "", "v": 1}\n')
            fh.write('{"t": "1.0", "ch": "gsr", "v": 1}\n')
            fh.write('[1, 2, 3]\n')
            fh.write('"just a string"\n')
            fh.write('{"t": 1.0, "v": 1}\n')
            fh.write('{"t":0.5,"kind":"hello","mk":50,"boot":"abc"}\n')
            fh.write('{"t":0.6,"kind":"boot","reason":"poweron","boot":"abc"}\n')
            fh.write('{"t":5.0,"ch":"hb","v":5.0,"q":"ok","drops":3,"boot":"abc"}\n')
            fh.write('{"t":10.0,"ch":"hb","v":10.0,"q":"ok","drops":7,"boot":"abc"}\n')
            fh.write('{"t":11.0,"ch":"gsr","v":1500,"q":"ok","boot":"abc","n":100}\n')
            fh.write('{"t":11.1,"ch":"gsr","v":1501,"q":"ok","boot":"abc","n":101}\n')
            fh.write('{"t":11.2,"ch":"gsr","v":1502,"q":"ok","boot":"abc","n":105}\n')   # 102..104 lost
            fh.write('{"t":11.2,"ch":"gsr","v":1502,"q":"ok","boot":"abc","n":105}\n')   # duplicate
        return path

    def test_malformed_lines_are_counted_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            rep = M.analyze(self._dirty_session(tmp))
            self.assertEqual(rep.integrity["skipped"], 12)
            self.assertGreaterEqual(rep.integrity["meta"], 2)              # the two appended plus whatever build_session wrote
            self.assertEqual(rep.integrity["duplicates"], 1)
            self.assertEqual(rep.integrity["lost"], 3)
            self.assertEqual(rep.integrity["firmware_drops"], 7)
            self.assertIn("abc", M.load_capture(self._dirty_session(tmp)).boots)
            self.assertTrue(rep.rounds)                                  # the session underneath still scores
            self.assertIn("lost", rep.capabilities["link"])
            self.assertTrue(any("skipped" in n for n in rep.notes))

    def test_strict_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirty = self._dirty_session(tmp)
            clean = os.path.join(tmp, "clean.ndjson")
            build_session(clean, with_imu=True)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(M.main([dirty, "--strict"]), 2)
                self.assertEqual(M.main([dirty]), 0)
                self.assertEqual(M.main([clean, "--strict"]), 0)

    def test_capabilities_name_what_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "s.ndjson")
            build_session(p, with_imu=False)
            rep = M.analyze(p)
            self.assertTrue(rep.capabilities["hr"].startswith("ok"))
            self.assertTrue(rep.capabilities["hrv"].startswith("provisional"))
            self.assertTrue(rep.capabilities["impacts"].startswith("unavailable"))
            self.assertTrue(rep.capabilities["stillness"].startswith("unavailable"))
            self.assertEqual(rep.capabilities["link"], "ok")
            build_session(p, with_imu=True)
            rep = M.analyze(p)
            self.assertEqual(rep.capabilities["hrv"], "ok")
            self.assertEqual(rep.capabilities["impacts"], "ok")

    def test_empty_and_meta_only_captures(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "empty.ndjson")
            open(p, "w").close()
            rep = M.analyze(p)
            self.assertEqual(rep.duration_s, 0.0)
            self.assertTrue(rep.capabilities["hr"].startswith("unavailable"))
            with open(p, "w") as fh:
                fh.write('{"t":0.1,"kind":"hello","boot":"x"}\n{"t":0.2,"kind":"boot","reason":"sw","boot":"x"}\n')
            rep = M.analyze(p)
            self.assertEqual(rep.integrity["meta"], 2)
            self.assertEqual(rep.integrity["boots"], 1)

    def test_two_boots_are_stitched_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "boots.ndjson")
            with open(p, "w", encoding="utf-8") as fh:
                # boot A: 0..100 s with a round, then a reset; boot B restarts at t 0 with another round
                for boot, cue_t in (("aaaa", (10.0, 70.0)), ("bbbb", (5.0, 65.0))):
                    fh.write(json.dumps({"t": 0.1, "kind": "boot", "reason": "poweron" if boot == "aaaa" else "brownout", "boot": boot}) + "\n")
                    fh.write(json.dumps({"t": cue_t[0], "ch": "cue", "v": "round-start", "boot": boot}) + "\n")
                    t = cue_t[0]
                    while t < 100.0:
                        fh.write(json.dumps({"t": round(t, 3), "ch": "ppg-rr", "v": 600, "q": "ok", "boot": boot}) + "\n")
                        t += 0.6
                    fh.write(json.dumps({"t": cue_t[1], "ch": "cue", "v": "round-end", "boot": boot}) + "\n")
            cap = M.load_capture(p)
            self.assertEqual(cap.time_base, "stitched")
            self.assertEqual(cap.boots, ["aaaa", "bbbb"])
            self.assertGreater(cap.t_max, 190.0)                         # second boot re-based after the first
            rep = M.analyze(p)
            self.assertEqual(len(rep.rounds), 2)
            self.assertGreater(rep.rounds[1].t_start, rep.rounds[0].t_end)
            self.assertTrue(any("re-based" in n for n in rep.notes))

    def test_wallclock_preferred_when_present_everywhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "wall.ndjson")
            with open(p, "w", encoding="utf-8") as fh:
                for i in range(20):
                    fh.write(json.dumps({"t": i * 0.6, "t_wallclock": 1.7e9 + i * 0.6, "ch": "ppg-rr", "v": 600, "q": "ok", "boot": "w"}) + "\n")
            cap = M.load_capture(p)
            self.assertEqual(cap.time_base, "wallclock")
            self.assertGreater(cap.t_min, 1.6e9)
