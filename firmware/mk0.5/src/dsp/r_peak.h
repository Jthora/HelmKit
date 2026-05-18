// HelmKit Mk0.5 — Streaming R-peak (heartbeat) detector for PPG IR samples.
//
// Wave J (2026-05-18). Closes the dsp.h TODO for L1 RR-interval extraction.
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

class RPeakDetector {
public:
    // Sample rate (Hz) that all window sizes below are tuned for. If the
    // sensor sample rate changes, this MUST change, or the bandpass and
    // refractory will be wrong. Compile-time constant to keep memory cost
    // bounded and avoid runtime allocation.
    static constexpr uint16_t kSampleRateHz   = 100;
    static constexpr size_t   kHpfWindow      = 50;   // ~0.5 Hz cutoff
    static constexpr size_t   kMwiWindow      = 15;   // 150 ms integration
    static constexpr uint16_t kRefractoryMs   = 250;
    static constexpr uint16_t kRrMinMs        = 250;  // 240 bpm
    static constexpr uint16_t kRrMaxMs        = 2000; //  30 bpm
    static constexpr float    kSpkiLearnRate  = 0.125f;
    static constexpr float    kNpkiLearnRate  = 0.01f;
    static constexpr float    kThreshFraction = 0.25f;
    static constexpr float    kPeakReleaseFraction = 0.5f;  // exit-peak gate
    static constexpr size_t   kFifoCapacity   = 8;

    RPeakDetector();

    // Flush all state. Call after a finger-off → finger-on transition so
    // the adaptive thresholds re-learn from the new baseline.
    void reset();

    // Streaming entry. Feed one IR sample per call at kSampleRateHz.
    // t_ms is the timestamp of THIS sample (driver-provided millis()).
    void process(uint32_t t_ms, uint32_t ir_raw);

    // Output FIFO. Drain via has_peak() / consume_peak() each loop tick.
    bool has_peak() const { return head_ != tail_; }
    Peak consume_peak();

    const RPeakDiag& diag() const { return diag_; }

private:
    void push_peak_(const Peak& p);

    // HPF (50-sample SMA subtraction) ring + running sum.
    float  hpf_buf_[kHpfWindow];
    size_t hpf_idx_;
    double hpf_sum_;
    bool   hpf_warmed_;
    size_t hpf_count_;

    // 3-tap derivative: need x[n-2]. Tiny ring.
    float  hist_[3];
    size_t hist_idx_;

    // MWI (squared-derivative running mean) ring + sum.
    float  mwi_buf_[kMwiWindow];
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
