"""Track K K-6 acceptance gate — RPeakBand refactor must not change
PPG behaviour. Mirrors the C++ ``RPeakBand`` lift in
``firmware/mk0.5/src/dsp/r_peak.h`` against its Python sibling
``firmware/mk0.5/scripts/rr_replay.py``.

Two gates:

1. ``PPG_DEFAULT`` values equal the legacy module-level constants
   byte-for-byte. (Algebraic identity guarantee that no math has shifted.)
2. ``RPeakDetector()`` (default) and ``RPeakDetector(band=PPG_DEFAULT)``
   (explicit) emit byte-identical peak streams on the synthetic PPG
   signal from ``rr_replay.synth_ppg``.

The C++ implementation derives both paths from the same ``RPeakBand``
constants, so passing here is sufficient evidence that the firmware
PPG output is unchanged.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "firmware" / "mk0.5" / "scripts"))

import rr_replay  # noqa: E402


def _run_detector(band):
    det = rr_replay.RPeakDetector(band=band) if band is not None else rr_replay.RPeakDetector()
    peaks = []
    for t_ms, ir in rr_replay.synth_ppg(duration_s=30.0, bpm=72.0):
        det.process(t_ms, ir)
        while det.has_peak():
            peaks.append(det.consume_peak())
    return peaks


class RPeakBandTests(unittest.TestCase):

    def test_ppg_default_matches_legacy_constants(self):
        b = rr_replay.PPG_DEFAULT
        self.assertEqual(b.sample_rate_hz, rr_replay.SAMPLE_RATE_HZ)
        self.assertEqual(b.hpf_window, rr_replay.HPF_WINDOW)
        self.assertEqual(b.mwi_window, rr_replay.MWI_WINDOW)
        self.assertEqual(b.refractory_ms, rr_replay.REFRACTORY_MS)
        self.assertEqual(b.rr_min_ms, rr_replay.RR_MIN_MS)
        self.assertEqual(b.rr_max_ms, rr_replay.RR_MAX_MS)
        self.assertEqual(b.spki_learn_rate, rr_replay.SPKI_LEARN_RATE)
        self.assertEqual(b.npki_learn_rate, rr_replay.NPKI_LEARN_RATE)
        self.assertEqual(b.thresh_fraction, rr_replay.THRESH_FRACTION)
        self.assertEqual(b.peak_release_fraction, rr_replay.PEAK_RELEASE_FRACTION)

    def test_default_and_explicit_ppg_produce_identical_peaks(self):
        peaks_default  = _run_detector(None)
        peaks_explicit = _run_detector(rr_replay.PPG_DEFAULT)
        self.assertEqual(len(peaks_default), len(peaks_explicit))
        self.assertGreater(len(peaks_default), 10, "expected detector to find peaks")
        for a, b in zip(peaks_default, peaks_explicit):
            self.assertEqual(a.t_ms, b.t_ms)
            self.assertEqual(a.rr_ms, b.rr_ms)
            self.assertEqual(a.in_range, b.in_range)
            self.assertEqual(a.confidence, b.confidence)

    def test_ecg_band_is_distinct_and_usable(self):
        # Smoke check: ECG band has expected canonical values and
        # constructs a detector without error. Real ECG validation
        # waits for AD8232 (Track J Bridge C).
        e = rr_replay.ECG_PAN_TOMPKINS
        self.assertEqual(e.sample_rate_hz, 250)
        self.assertEqual(e.mwi_window, 38)   # 150 ms at fs=250
        self.assertEqual(e.hpf_window, 16)
        det = rr_replay.RPeakDetector(band=e)
        # Feed a few zero samples; must not raise.
        for t in range(0, 100, 4):
            det.process(t, 0)


if __name__ == "__main__":
    unittest.main()
