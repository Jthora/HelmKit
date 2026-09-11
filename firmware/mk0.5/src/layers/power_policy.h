// HelmKit Mk0.5 — low-battery policy (Track N, N-F3).
//
// Pure, header-only, native-tested. Fed once per second with the pack
// voltage. `feed()` returns true exactly once when the low state is entered:
// main.cpp ends the session cleanly (summary line, `cue: low-battery`), stops
// the streams and shows the fault pattern. The state clears when the voltage
// recovers by the hysteresis (charger plugged in).
//
//   low when v < low_v for debounce_ms without interruption
//   clear when v > low_v + hyst_v
//
// percent(): a 1S LiPo open-circuit curve, linear between the knots. Under
// load the reading sags, so the number is a guide, not a gauge.

#pragma once

#include <stdint.h>

namespace helmkit::layers {

struct PowerConfig {
    float    low_v       = 3.50f;
    float    hyst_v      = 0.10f;
    uint32_t debounce_ms = 10000;
};

class PowerPolicy {
 public:
    explicit PowerPolicy(const PowerConfig& cfg = {}) : cfg_(cfg) {}

    bool feed(uint32_t t_ms, float volts) {
        last_v_ = volts;
        if (low_) {
            if (volts > cfg_.low_v + cfg_.hyst_v) { low_ = false; below_since_ = 0; }
            return false;
        }
        if (volts < cfg_.low_v) {
            if (below_since_ == 0) below_since_ = t_ms ? t_ms : 1;
            if ((int32_t)(t_ms - below_since_) >= (int32_t)cfg_.debounce_ms) {
                low_ = true;
                return true;                       // the one-shot trigger
            }
        } else {
            below_since_ = 0;
        }
        return false;
    }

    bool  low()    const { return low_; }
    float last_v() const { return last_v_; }

    static uint8_t percent(float v) {
        static const float kV[]   = {3.30f, 3.45f, 3.68f, 3.74f, 3.77f, 3.79f, 3.82f, 3.87f, 3.92f, 3.98f, 4.06f, 4.20f};
        static const float kPct[] = {0.0f,  5.0f,  10.0f, 20.0f, 30.0f, 40.0f, 50.0f, 60.0f, 70.0f, 80.0f, 90.0f, 100.0f};
        constexpr int n = 12;
        if (v <= kV[0]) return 0;
        if (v >= kV[n - 1]) return 100;
        for (int i = 1; i < n; ++i) {
            if (v <= kV[i]) {
                const float f = (v - kV[i - 1]) / (kV[i] - kV[i - 1]);
                return (uint8_t)(kPct[i - 1] + f * (kPct[i] - kPct[i - 1]) + 0.5f);
            }
        }
        return 100;
    }

 private:
    PowerConfig cfg_;
    bool     low_ = false;
    uint32_t below_since_ = 0;
    float    last_v_ = 0.0f;
};

}  // namespace helmkit::layers
