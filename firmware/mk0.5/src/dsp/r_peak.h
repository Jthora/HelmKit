// HelmKit Mk0.5 — Streaming R-peak (heartbeat) detector.
//
// Wave J (2026-05-18). Closes the dsp.h TODO for L1 RR-interval extraction.
// Track K K-6 (2026-05-18): band coefficients lifted into RPeakBand config
// struct so the same detector can run against PPG (Wave J default) or ECG
// (AD8232 / Bridge C) without code duplication. Default construction is
// byte-identical to the pre-K-6 PPG-only constants.
//
// Algorithm: Pan-Tompkins variant adapted to photoplethysmography. The
// canonical Pan-Tompkins pipeline targets ECG (QRS energy at 5-15 Hz). PPG
// pulse energy lives lower (fundamental 0.7-3 Hz for 40-180 bpm), so the
// bandpass moves accordingly. Pipeline:
//
//   1. High-pass detrend: subtract a 50-sample SMA (cutoff ~0.5 Hz at
//      fs=100 Hz; removes DC + slow respiratory baseline drift).
//   2. 3-tap derivative: y[n] = x[n] - x[n-2]. Emphasises pulse upstrokes.
//   3. Square: point-wise y^2. All-positive, peaks amplified.
//   4. Moving-window integration: 150 ms = 15 samples @ 100 Hz.
//   5. Adaptive threshold (Pan-Tompkins SPKI/NPKI scheme):
//        SPKI = a * peak_amp + (1-a) * SPKI    (a = 0.125, on each peak)
//        NPKI = b * mwi + (1-b) * NPKI         (b = 0.01,  continuously)
//        threshold = NPKI + 0.25 * (SPKI - NPKI)
//   6. Refractory window: 250 ms hard reject between accepted peaks.
//   7. Sanity gate: RR in [250, 2000] ms; out-of-range emitted with flag.
//
// Latency: one sample lookahead for derivative is avoided by using the
// causal 3-tap form (x[n] - x[n-2]). Worst-case end-to-end latency from
// pulse upstroke to peak emission is dominated by the MWI window: 150 ms.
// Per spec acceptance gate, <250 ms latency.
//
// Determinism: All state is per-instance. Two instances fed the same
// sample stream will emit identical peaks. The companion Python reference
// in tools/rr_replay.py mirrors this code bit-for-bit (within float
// rounding) so on-target output can be verified against offline analysis.
//
// Schema: peaks emit on the `ppg-rr` channel per docs/SCHEMA.md §2.2.
//
// References:
//   - Pan, J. & Tompkins, W.J. (1985). A Real-Time QRS Detection Algorithm.
//     IEEE Trans. Biomed. Eng., BME-32(3), 230-236.
//   - Elgendi, M. (2013). Detection of c, d, and e waves in the
//     acceleration photoplethysmogram. Comput. Methods Programs Biomed.
//     117(2), 125-136.

#pragma once

#include <stddef.h>
#include <stdint.h>

namespace helmkit::dsp {

// One detected (or out-of-range) heartbeat.
struct Peak {
    uint32_t t_ms;       // millis()-since-boot at peak centroid
    uint16_t rr_ms;      // interval to previous accepted peak (0 = first peak)
    bool     in_range;   // true if 250 <= rr_ms <= 2000 (or rr_ms == 0)
    float    confidence; // normalised peak amplitude vs threshold (>= 1.0)
};

// Diagnostic counters. Polled by main to inform NDJSON `diag` events or
// the OLED display. Not part of the wire protocol.
struct RPeakDiag {
    uint32_t samples_in;
    uint32_t peaks_emitted;            // includes out-of-range
    uint32_t peaks_rejected_refractory;
    float    spki;
    float    npki;
    float    threshold;
};

// All numerical coefficients of the detector. Lifted out of the class
// (Track K K-6) so the same RPeakDetector implementation can run against
// either PPG or ECG by choosing a band at construction time. Two shipped
// bands live in `rpeak_bands::` below.
//
// Buffer-size note: hpf_window and mwi_window MUST be <= the corresponding
// kHpfWindowMax / kMwiWindowMax in RPeakDetector (static-asserted there).
struct RPeakBand {
    uint16_t sample_rate_hz;
    size_t   hpf_window;              // SMA length for high-pass detrend
    size_t   mwi_window;              // moving-window integration length
    uint16_t refractory_ms;
    uint16_t rr_min_ms;
    uint16_t rr_max_ms;
    float    spki_learn_rate;
    float    npki_learn_rate;
    float    thresh_fraction;
    float    peak_release_fraction;
    const char* name;                 // diagnostic label, e.g. "ppg"/"ecg"
};

namespace rpeak_bands {

// PPG @ 100 Hz — Pan-Tompkins adapted to the PPG pulse band.
// These values are byte-identical to the Wave J pre-K-6 class constants
// and are the default for RPeakDetector(). DO NOT modify without re-baselining
// the rr_replay.py self-test and the Track K K-2 fixture.
inline constexpr RPeakBand kPpgDefault = {
    /*sample_rate_hz       */ 100,
    /*hpf_window           */  50,    // ~0.5 Hz cutoff @ 100 Hz
    /*mwi_window           */  15,    // 150 ms @ 100 Hz
    /*refractory_ms        */ 250,
    /*rr_min_ms            */ 250,    // 240 bpm
    /*rr_max_ms            */ 2000,   //  30 bpm
    /*spki_learn_rate      */ 0.125f,
    /*npki_learn_rate      */ 0.01f,
    /*thresh_fraction      */ 0.25f,
    /*peak_release_fraction*/ 0.5f,
    /*name                 */ "ppg",
};

// ECG @ 250 Hz — classical Pan-Tompkins QRS band (5-15 Hz energy,
// 150 ms moving-window integration). For the AD8232 oracle in Bridge C.
// Window sizing:
//   hpf_window = 16 samples → SMA cutoff ≈ fs/(N*pi) ≈ 5 Hz @ fs=250
//   mwi_window = 38 samples → 152 ms @ fs=250  (≈ classical 150 ms)
inline constexpr RPeakBand kEcgPanTompkins = {
    /*sample_rate_hz       */ 250,
    /*hpf_window           */  16,
    /*mwi_window           */  38,
    /*refractory_ms        */ 200,    // QRS refractory floor
    /*rr_min_ms            */ 300,    // 200 bpm
    /*rr_max_ms            */ 2000,
    /*spki_learn_rate      */ 0.125f,
    /*npki_learn_rate      */ 0.01f,
    /*thresh_fraction      */ 0.25f,
    /*peak_release_fraction*/ 0.5f,
    /*name                 */ "ecg",
};

}  // namespace rpeak_bands

class RPeakDetector {
public:
    // Compile-time MAX buffer sizes. The active band may use a shorter
    // window; indices wrap at band_.{hpf,mwi}_window. These bounds must
    // cover every shipped band in rpeak_bands::* below.
    static constexpr size_t   kHpfWindowMax = 64;
    static constexpr size_t   kMwiWindowMax = 64;
    static constexpr size_t   kFifoCapacity = 8;

    // Default constructor → PPG band (Wave J behaviour, byte-identical).
    RPeakDetector();
    // Explicit band constructor → e.g. ECG via rpeak_bands::kEcgPanTompkins.
    explicit RPeakDetector(const RPeakBand& band);

    // Flush all state. Call after a finger-off → finger-on transition so
    // the adaptive thresholds re-learn from the new baseline.
    void reset();

    // Streaming entry. Feed one sample per call at band().sample_rate_hz.
    // t_ms is the timestamp of THIS sample (driver-provided millis()).
    // For PPG: pass IR raw count. For ECG: pass ADC raw count.
    void process(uint32_t t_ms, uint32_t sample_raw);

    // Output FIFO. Drain via has_peak() / consume_peak() each loop tick.
    bool has_peak() const { return head_ != tail_; }
    Peak consume_peak();

    const RPeakDiag& diag() const { return diag_; }
    const RPeakBand& band() const { return band_; }

private:
    void push_peak_(const Peak& p);

    RPeakBand band_;

    // HPF (SMA subtraction) ring + running sum. Indexed mod band_.hpf_window.
    float  hpf_buf_[kHpfWindowMax];
    size_t hpf_idx_;
    double hpf_sum_;
    bool   hpf_warmed_;
    size_t hpf_count_;

    // 3-tap derivative: need x[n-2]. Tiny ring.
    float  hist_[3];
    size_t hist_idx_;

    // MWI ring + sum. Indexed mod band_.mwi_window.
    float  mwi_buf_[kMwiWindowMax];
    size_t mwi_idx_;
    double mwi_sum_;

    // Adaptive thresholds (Pan-Tompkins SPKI/NPKI).
    float spki_;
    float npki_;
    float threshold_;

    // Peak-finder state machine.
    bool     in_peak_;
    float    peak_amp_;
    uint32_t peak_t_ms_;
    uint32_t last_accepted_t_ms_;  // 0 = none yet

    // Output FIFO.
    Peak   fifo_[kFifoCapacity];
    size_t head_;   // consume here
    size_t tail_;   // push here

    RPeakDiag diag_;
};

}  // namespace helmkit::dsp
