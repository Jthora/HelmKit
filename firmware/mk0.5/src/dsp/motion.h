// HelmKit Mk0.5 — motion features from an accelerometer stream (Track N, N-S4; Track M, M-F1).
//
// Pure, header-only, native-tested. Feed accelerometer samples in g (any rate
// from 25 to 200 Hz) and pop events:
//
//   still     once per second: 1 when the RMS dynamic acceleration over the
//             trailing 2 s window is below `still_thresh_g`, else 0. The
//             analyser computes HRV only inside runs of 1 lasting >= 60 s.
//   impact    once per hit: the peak dynamic acceleration (|a| - 1 g) inside
//             a 200 ms window opened when it first crosses `impact_thresh_g`;
//             the window doubles as the refractory period.
//   activity  once per 10 s: the mean dynamic acceleration over the window
//             (an exertion index; the analyser does not use it yet).
//
// Clipping (any axis at the range limit) is counted, not emitted: the IMU's
// self-test line reports it.

#pragma once

#include <math.h>
#include <stdint.h>

namespace helmkit::dsp {

struct MotionConfig {
    float    still_thresh_g       = 0.05f;   // RMS dynamic acceleration below this = still (a resting head is ~0.02)
    uint32_t still_window_ms      = 2000;
    float    impact_thresh_g      = 10.0f;   // M-F1 / SCHEMA 2.3: impact events >= 10 g
    uint32_t impact_window_ms     = 200;     // peak capture + refractory
    uint32_t activity_window_ms   = 10000;
    float    clip_g               = 15.5f;   // +-16 g range
};

struct MotionEvent {
    enum class Kind : uint8_t { kNone = 0, kStill, kImpact, kActivity };
    Kind     kind  = Kind::kNone;
    uint32_t t_ms  = 0;
    float    value = 0.0f;   // still: 0/1; impact: peak g; activity: mean g
};

class MotionDetector {
 public:
    explicit MotionDetector(const MotionConfig& cfg = {}) : cfg_(cfg) {}

    void reset() {
        n_ = 0;
        for (auto& b : bins_) b = Bin{};
        bin_head_ = 0; bin_count_ = 0;
        bin_start_ms_ = 0; started_ = false;
        in_impact_ = false; impact_peak_ = 0.0f; impact_t_ = 0; impact_open_ms_ = 0;
        clips_ = 0; last_still_ = -1;
        q_head_ = q_tail_ = 0;
        act_sum_ = 0.0f; act_n_ = 0; act_start_ms_ = 0;
    }

    // One accelerometer sample in g. Events are queued; drain with pop().
    void feed(uint32_t t_ms, float ax, float ay, float az) {
        if (!started_) { started_ = true; bin_start_ms_ = t_ms; act_start_ms_ = t_ms; }
        if (fabsf(ax) >= cfg_.clip_g || fabsf(ay) >= cfg_.clip_g || fabsf(az) >= cfg_.clip_g) ++clips_;
        const float mag = sqrtf(ax * ax + ay * ay + az * az);
        const float dyn = fabsf(mag - 1.0f);
        ++n_;

        // --- impact: open a peak window on the first crossing, emit at its end
        if (in_impact_) {
            if (dyn > impact_peak_) impact_peak_ = dyn;
            if ((int32_t)(t_ms - impact_open_ms_) >= (int32_t)cfg_.impact_window_ms) {
                push({MotionEvent::Kind::kImpact, impact_t_, impact_peak_});
                in_impact_ = false;
            }
        } else if (dyn >= cfg_.impact_thresh_g) {
            in_impact_ = true;
            impact_peak_ = dyn;
            impact_t_ = t_ms;
            impact_open_ms_ = t_ms;
        }

        // --- 1 s bins of dyn^2 for the still window (2 bins) ...
        Bin& cur = bins_[bin_head_];
        cur.sum_sq += dyn * dyn;
        cur.sum    += dyn;
        cur.n      += 1;
        if ((int32_t)(t_ms - bin_start_ms_) >= 1000) {
            // close the bin: compute still over the last `still_window_ms / 1000` bins
            const uint8_t want = (uint8_t)(cfg_.still_window_ms / 1000);
            float ss = 0.0f; uint32_t nn = 0;
            for (uint8_t k = 0; k < kBins && k < want && k <= bin_count_; ++k) {
                const Bin& b = bins_[(bin_head_ + kBins - k) % kBins];
                ss += b.sum_sq; nn += b.n;
            }
            const float rms = nn ? sqrtf(ss / (float)nn) : 0.0f;
            const int still = (nn > 0 && rms < cfg_.still_thresh_g) ? 1 : 0;
            push({MotionEvent::Kind::kStill, t_ms, (float)still});
            last_still_ = still;
            // ... and the activity accumulator (mean dyn over 10 s)
            act_sum_ += cur.sum; act_n_ += cur.n;
            if ((int32_t)(t_ms - act_start_ms_) >= (int32_t)cfg_.activity_window_ms) {
                push({MotionEvent::Kind::kActivity, t_ms, act_n_ ? act_sum_ / (float)act_n_ : 0.0f});
                act_sum_ = 0.0f; act_n_ = 0; act_start_ms_ = t_ms;
            }
            bin_head_ = (uint8_t)((bin_head_ + 1) % kBins);
            bins_[bin_head_] = Bin{};
            if (bin_count_ < kBins - 1) ++bin_count_;
            bin_start_ms_ = t_ms;
        }
    }

    bool pop(MotionEvent& out) {
        if (q_head_ == q_tail_) return false;
        out = q_[q_tail_];
        q_tail_ = (uint8_t)((q_tail_ + 1) % kQ);
        return true;
    }

    int      last_still() const { return last_still_; }   // -1 until the first second closes
    uint32_t clips()      const { return clips_; }
    uint32_t samples()    const { return n_; }

 private:
    struct Bin { float sum_sq = 0.0f; float sum = 0.0f; uint32_t n = 0; };
    static constexpr uint8_t kBins = 4;
    static constexpr uint8_t kQ    = 8;

    void push(const MotionEvent& e) {
        const uint8_t next = (uint8_t)((q_head_ + 1) % kQ);
        if (next == q_tail_) return;          // full: drop the newest (impacts are rare, stills are periodic)
        q_[q_head_] = e;
        q_head_ = next;
    }

    MotionConfig cfg_;
    uint32_t n_ = 0;
    Bin      bins_[kBins];
    uint8_t  bin_head_ = 0, bin_count_ = 0;
    uint32_t bin_start_ms_ = 0;
    bool     started_ = false;
    bool     in_impact_ = false;
    float    impact_peak_ = 0.0f;
    uint32_t impact_t_ = 0, impact_open_ms_ = 0;
    uint32_t clips_ = 0;
    int      last_still_ = -1;
    MotionEvent q_[kQ];
    uint8_t  q_head_ = 0, q_tail_ = 0;
    float    act_sum_ = 0.0f;
    uint32_t act_n_ = 0, act_start_ms_ = 0;
};

}  // namespace helmkit::dsp
