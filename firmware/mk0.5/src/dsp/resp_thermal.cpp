// HelmKit Mk0.5 — Streaming thermal-respiration extractor (Track M, M-F2).
// Behavioural spec: tools/analyze_combat_session.py (breath_times,
// breaths_per_min, nose_slope_c_per_min). Keep the two in step.

#include "dsp/resp_thermal.h"

#include <math.h>

namespace helmkit::dsp {

namespace {
constexpr float kPi = 3.14159265358979f;
}

RespThermal::RespThermal(const RespThermalConfig& cfg) : cfg_(cfg) { reset(); }

void RespThermal::reset() {
    diag_ = RespThermalDiag{};
    have_first_ = false;
    t_prev_ms_ = 0;
    lp_ = hp_mean_ = 0.0f;
    n_y_ = 0;
    y_prev_ = y_prev2_ = 0.0f;
    t_prev_y_ms_ = 0;
    recent_n_ = recent_head_ = 0;
    breath_n_ = breath_head_ = 0;
    have_last_breath_ = false;
    last_breath_ms_ = 0;
    raw_n_ = raw_head_ = 0;
}

void RespThermal::push_recent_(float abs_y) {
    recent_[recent_head_] = abs_y;
    recent_head_ = (recent_head_ + 1) % kSpreadWindow;
    if (recent_n_ < kSpreadWindow) ++recent_n_;
}

float RespThermal::spread_() const {
    // Python: statistics.pstdev(recent) if len(recent) > 2 else 0.0
    if (recent_n_ <= 2) return 0.0f;
    double s = 0.0, s2 = 0.0;
    for (size_t i = 0; i < recent_n_; ++i) {
        const double v = recent_[i];
        s += v;
        s2 += v * v;
    }
    const double mean = s / (double)recent_n_;
    double var = s2 / (double)recent_n_ - mean * mean;
    if (var < 0.0) var = 0.0;
    return (float)sqrt(var);
}

void RespThermal::push_raw_(uint32_t t_ms, float v) {
    raw_t_[raw_head_] = t_ms;
    raw_v_[raw_head_] = v;
    raw_head_ = (raw_head_ + 1) % kRawCap;
    if (raw_n_ < kRawCap) ++raw_n_;
}

void RespThermal::push_breath_(uint32_t t_ms) {
    breath_ms_[breath_head_] = t_ms;
    breath_head_ = (breath_head_ + 1) % kBreathCap;
    if (breath_n_ < kBreathCap) ++breath_n_;
    have_last_breath_ = true;
    last_breath_ms_ = t_ms;
    ++diag_.breaths;
}

bool RespThermal::process(uint32_t t_ms, float temp_c) {
    ++diag_.samples_in;
    push_raw_(t_ms, temp_c);

    // 1-2. band-pass: EMA low-pass then EMA high-pass, both time-based.
    float y;
    if (!have_first_) {
        have_first_ = true;
        lp_ = temp_c;
        hp_mean_ = lp_;
        y = 0.0f;
    } else {
        float dt = (float)(t_ms - t_prev_ms_) / 1000.0f;
        if (dt < 1e-6f) dt = 1e-6f;
        const float tau_hi = 1.0f / (2.0f * kPi * cfg_.f_hi_hz);
        const float tau_lo = 1.0f / (2.0f * kPi * cfg_.f_lo_hz);
        lp_ += (dt / (tau_hi + dt)) * (temp_c - lp_);
        hp_mean_ += (dt / (tau_lo + dt)) * (lp_ - hp_mean_);
        y = lp_ - hp_mean_;
    }
    t_prev_ms_ = t_ms;
    diag_.y_last = y;

    // 3. evaluate the previous sample as a breath candidate (needs y[k-2], y[k-1], y[k]).
    bool breath = false;
    if (n_y_ >= 2) {
        const float spread = spread_();          // |y| history up to and including the candidate
        float thr = cfg_.thr_frac * spread * 1.41421356f;
        if (thr < cfg_.min_peak_c) thr = cfg_.min_peak_c;
        diag_.threshold = thr;
        const bool local_max = (y_prev_ > y_prev2_) && (y_prev_ >= y);
        const bool refractory_ok = !have_last_breath_ ||
            ((float)(t_prev_y_ms_ - last_breath_ms_) / 1000.0f >= cfg_.refractory_s);
        if (y_prev_ > thr && local_max && refractory_ok) {
            push_breath_(t_prev_y_ms_);
            breath = true;
        }
    }

    // shift the candidate window and record |y| for the next threshold
    y_prev2_ = y_prev_;
    y_prev_ = y;
    t_prev_y_ms_ = t_ms;
    ++n_y_;
    push_recent_(y < 0.0f ? -y : y);
    return breath;
}

bool RespThermal::rate_bpm(uint32_t now_ms, float* out) const {
    // breaths with now - window <= t < now  (Python Window.contains: t_start <= t < t_end)
    const uint32_t win_ms = (uint32_t)(cfg_.rate_window_s * 1000.0f);
    uint32_t first = 0, last = 0;
    size_t n = 0;
    for (size_t i = 0; i < breath_n_; ++i) {
        const uint32_t t = breath_ms_[i];
        const uint32_t age = now_ms - t;            // wrap-safe
        if (age > win_ms || age == 0) continue;     // age == 0 means t == now: excluded (half-open window)
        if (n == 0 || (int32_t)(t - first) < 0) first = t;
        if (n == 0 || (int32_t)(t - last) > 0) last = t;
        ++n;
    }
    if (n < 2 || last == first) return false;
    *out = 60.0f * (float)(n - 1) / ((float)(last - first) / 1000.0f);
    return true;
}

bool RespThermal::slope_c_per_min(uint32_t now_ms, float* out) const {
    const uint32_t win_ms = (uint32_t)(cfg_.slope_window_s * 1000.0f);
    double st = 0.0, sv = 0.0;
    size_t n = 0;
    for (size_t i = 0; i < raw_n_; ++i) {
        const uint32_t age = now_ms - raw_t_[i];
        if (age > win_ms) continue;
        st += (double)raw_t_[i];
        sv += (double)raw_v_[i];
        ++n;
    }
    if (n < 3) return false;
    const double mt = st / (double)n, mv = sv / (double)n;
    double sxx = 0.0, sxy = 0.0;
    for (size_t i = 0; i < raw_n_; ++i) {
        const uint32_t age = now_ms - raw_t_[i];
        if (age > win_ms) continue;
        const double dt = (double)raw_t_[i] - mt;
        sxx += dt * dt;
        sxy += dt * ((double)raw_v_[i] - mv);
    }
    if (sxx <= 0.0) return false;
    *out = (float)(sxy / sxx * 1000.0 * 60.0);     // per ms -> per minute
    return true;
}

}  // namespace helmkit::dsp
