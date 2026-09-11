// HelmKit Mk0.5 — electrodermal features and the sweat rule (Track N, N-S6; Track M, M-F3).
//
// Pure, header-only, native-tested. Streaming port of the host reference in
// tools/analyze_combat_session.py (scr_times, ema_lowpass, linear_slope,
// sweat_flag); the constants are the same and a change here is a change
// there in the same commit.
//
//   ScrDetector   tonic = EMA of the raw conductance with tau 5 s;
//                 phasic = raw - tonic. A rise of the phasic component from a
//                 trough to the following peak counts as a skin-conductance
//                 response when it lasts 0.5..3 s and its amplitude is at
//                 least 0.5 % of the tonic level at the trough. The event is
//                 stamped at the peak.
//   SlopeWindow   least-squares slope over a trailing window (skin
//                 temperature, 60 s); the sweat rule fires above
//                 0.05 C per minute and the host withholds EDA statistics
//                 while it holds.

#pragma once

#include <math.h>
#include <stdint.h>

namespace helmkit::dsp {

struct EdaConfig {
    float tonic_tau_s   = 5.0f;    // EDA_TONIC_TAU_S
    float min_rise_s    = 0.5f;    // EDA_SCR_MIN_RISE_S
    float max_rise_s    = 3.0f;    // EDA_SCR_MAX_RISE_S
    float rel_threshold = 0.005f;  // EDA_SCR_REL_THRESHOLD
};

class ScrDetector {
 public:
    explicit ScrDetector(const EdaConfig& cfg = {}) : cfg_(cfg) {}

    void reset() { init_ = false; in_rise_ = false; n_ = 0; }

    // One conductance sample (raw units). Returns true when a response
    // completed; *t_peak_ms and *amplitude describe it.
    bool feed(uint32_t t_ms, float v, uint32_t* t_peak_ms, float* amplitude) {
        if (!init_) {
            init_ = true; m_ = v; t_prev_ = t_ms; prev_phasic_ = 0.0f; prev_tonic_ = m_; n_ = 1;
            return false;
        }
        const float dt = fmaxf((float)(int32_t)(t_ms - t_prev_) / 1000.0f, 1e-6f);
        const float a = dt / (cfg_.tonic_tau_s + dt);
        m_ += a * (v - m_);
        const float phasic = v - m_;
        bool fired = false;
        if (in_rise_) {
            if (phasic >= prev_phasic_) {
                // still rising (non-decreasing run continues)
            } else {
                // the rise ended at the previous sample = the peak
                const float rise    = prev_phasic_ - trough_v_;
                const float rise_dt = (float)(int32_t)(t_prev_ - trough_t_) / 1000.0f;
                const float level   = fmaxf(fabsf(trough_tonic_), 1e-9f);
                if (rise_dt >= cfg_.min_rise_s && rise_dt <= cfg_.max_rise_s && rise >= cfg_.rel_threshold * level) {
                    if (t_peak_ms) *t_peak_ms = t_prev_;
                    if (amplitude) *amplitude = rise;
                    fired = true;
                }
                in_rise_ = false;
            }
        } else if (phasic > prev_phasic_) {
            in_rise_ = true;
            trough_t_ = t_prev_; trough_v_ = prev_phasic_; trough_tonic_ = prev_tonic_;
        }
        prev_phasic_ = phasic; prev_tonic_ = m_; t_prev_ = t_ms;
        ++n_;
        return fired;
    }

    float tonic() const { return m_; }
    uint32_t samples() const { return n_; }

 private:
    EdaConfig cfg_;
    bool     init_ = false, in_rise_ = false;
    float    m_ = 0.0f, prev_phasic_ = 0.0f, prev_tonic_ = 0.0f;
    uint32_t t_prev_ = 0, trough_t_ = 0, n_ = 0;
    float    trough_v_ = 0.0f, trough_tonic_ = 0.0f;
};

class SlopeWindow {
 public:
    static constexpr uint16_t kCap = 320;           // 60 s at 5 Hz plus slack

    explicit SlopeWindow(uint32_t window_ms = 60000) : window_ms_(window_ms) {}

    void reset() { head_ = 0; n_ = 0; }

    void feed(uint32_t t_ms, float v) {
        t_[head_] = t_ms; v_[head_] = v;
        head_ = (uint16_t)((head_ + 1) % kCap);
        if (n_ < kCap) ++n_;
        // drop samples older than the window (they sit at the tail)
        while (n_ > 0) {
            const uint16_t tail = (uint16_t)((head_ + kCap - n_) % kCap);
            if ((int32_t)(t_ms - t_[tail]) > (int32_t)window_ms_) --n_; else break;
        }
    }

    // Least-squares slope in units per second over the window; false with
    // fewer than 3 points or no time spread (the host's None).
    bool slope(float* per_s) const {
        if (n_ < 3) return false;
        const uint16_t tail = (uint16_t)((head_ + kCap - n_) % kCap);
        const uint32_t t0 = t_[tail];
        float mt = 0.0f, mv = 0.0f;
        for (uint16_t i = 0; i < n_; ++i) {
            const uint16_t k = (uint16_t)((tail + i) % kCap);
            mt += (float)(int32_t)(t_[k] - t0) / 1000.0f; mv += v_[k];
        }
        mt /= (float)n_; mv /= (float)n_;
        float sxx = 0.0f, sxy = 0.0f;
        for (uint16_t i = 0; i < n_; ++i) {
            const uint16_t k = (uint16_t)((tail + i) % kCap);
            const float dt = (float)(int32_t)(t_[k] - t0) / 1000.0f - mt;
            sxx += dt * dt; sxy += dt * (v_[k] - mv);
        }
        if (sxx <= 0.0f) return false;
        *per_s = sxy / sxx;
        return true;
    }

    uint16_t count() const { return n_; }

 private:
    uint32_t window_ms_;
    uint32_t t_[kCap] = {};
    float    v_[kCap] = {};
    uint16_t head_ = 0, n_ = 0;
};

// SWEAT_SLOPE_C_PER_MIN: skin temperature rising faster than this = thermal sweating.
inline bool sweat_rule(float slope_c_per_s) { return 60.0f * slope_c_per_s > 0.05f; }

}  // namespace helmkit::dsp
