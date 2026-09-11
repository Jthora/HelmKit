// HelmKit Mk0.5 — Streaming thermal-respiration extractor (Track M, M-F2).
//
// Turns the MLX90614 object temperature aimed at the nose tip into breath
// events, a breathing rate and the slow nose-tip temperature slope (the
// thermal arousal marker). Contactless, sweat-tolerant: the combat trim's
// breathing channel (docs/plans/2026-tier1-launch/track-M-combat-trim.md §3).
//
// Pipeline (mirrors tools/analyze_combat_session.py::breath_times exactly —
// that Python is the behavioural spec, this file is the on-target port):
//
//   1. Time-based EMA low-pass, tau = 1 / (2 pi f_hi), f_hi = 1.0 Hz.
//   2. Time-based EMA high-pass on that (x - EMA, tau = 1 / (2 pi f_lo),
//      f_lo = 0.1 Hz): the band-passed nostril-airflow swing.
//   3. Candidate = previous sample. Breath when it is a local maximum
//      (y[i] > y[i-1] and y[i] >= y[i+1]) above an adaptive threshold
//      max(0.01 degC, 0.3 * sqrt(2) * pstdev(|y| over the last 81 samples
//      up to and including the candidate)) and >= 1 s after the last breath
//      (<= 60 breaths / min).
//   4. Rate = 60 * (n - 1) / span over the breaths inside the trailing 30 s.
//   5. Slope = least-squares slope of the RAW temperature over the trailing
//      60 s, in degC per minute. Falling nose tip = sympathetic arousal.
//
// Feed only in-range samples (the driver's `in_range`), as the analyser only
// uses q = "ok" samples. Determinism: all state per instance; no Arduino
// dependencies so the same code runs in the native unit tests.
//
// Schema: breaths emit on `resp-thermal` (docs/SCHEMA.md §2.3, v0.3-proposed)
// with v = breaths per minute at the time of the breath.

#pragma once

#include <stddef.h>
#include <stdint.h>

namespace helmkit::dsp {

struct RespThermalConfig {
    float    f_lo_hz        = 0.1f;   // band-pass low edge
    float    f_hi_hz        = 1.0f;   // band-pass high edge
    float    refractory_s   = 1.0f;   // minimum breath spacing
    float    min_peak_c     = 0.01f;  // absolute floor on the peak threshold
    float    thr_frac       = 0.3f;   // threshold = thr_frac * sqrt(2) * pstdev(|y|)
    float    rate_window_s  = 30.0f;  // breathing-rate window
    float    slope_window_s = 60.0f;  // arousal-slope window
};

struct RespThermalDiag {
    uint32_t samples_in;
    uint32_t breaths;
    float    y_last;        // last band-passed value (degC)
    float    threshold;     // last threshold used
};

class RespThermal {
 public:
    static constexpr size_t kSpreadWindow = 81;   // |y| history for the adaptive threshold (Python: y[i-80 .. i])
    static constexpr size_t kBreathCap    = 64;   // >= 60 bpm * 30 s
    static constexpr size_t kRawCap       = 256;  // >= 4 Hz * 60 s

    explicit RespThermal(const RespThermalConfig& cfg = RespThermalConfig{});

    void reset();

    // One in-range object-temperature sample. Returns true when a breath was
    // detected (at the PREVIOUS sample's time; see last_breath_ms()).
    bool process(uint32_t t_ms, float temp_c);

    bool     has_breath()     const { return have_last_breath_; }
    uint32_t last_breath_ms() const { return last_breath_ms_; }
    uint32_t breaths()        const { return diag_.breaths; }

    // Breaths per minute over the trailing rate window. false when fewer than
    // two breaths fall inside it.
    bool rate_bpm(uint32_t now_ms, float* out) const;

    // Raw-temperature slope over the trailing slope window, degC per minute.
    // false with fewer than three samples or no time spread.
    bool slope_c_per_min(uint32_t now_ms, float* out) const;

    const RespThermalDiag& diag() const { return diag_; }

 private:
    void  push_recent_(float abs_y);
    float spread_() const;                 // population stdev of the |y| history
    void  push_raw_(uint32_t t_ms, float v);
    void  push_breath_(uint32_t t_ms);

    RespThermalConfig cfg_;
    RespThermalDiag   diag_{};

    // filters
    bool     have_first_ = false;
    uint32_t t_prev_ms_  = 0;
    float    lp_         = 0.0f;   // low-pass state
    float    hp_mean_    = 0.0f;   // slow mean subtracted by the high-pass
    // candidate window
    uint32_t n_y_        = 0;      // band-passed samples produced so far
    float    y_prev_     = 0.0f;   // y[k-1]
    float    y_prev2_    = 0.0f;   // y[k-2]
    uint32_t t_prev_y_ms_ = 0;     // time of y[k-1]
    // |y| history
    float    recent_[kSpreadWindow]{};
    size_t   recent_n_    = 0;
    size_t   recent_head_ = 0;
    // breaths
    uint32_t breath_ms_[kBreathCap]{};
    size_t   breath_n_    = 0;
    size_t   breath_head_ = 0;
    bool     have_last_breath_ = false;
    uint32_t last_breath_ms_   = 0;
    // raw ring for the slope
    uint32_t raw_t_[kRawCap]{};
    float    raw_v_[kRawCap]{};
    size_t   raw_n_    = 0;
    size_t   raw_head_ = 0;
};

}  // namespace helmkit::dsp
