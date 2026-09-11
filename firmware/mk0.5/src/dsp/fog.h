// HelmKit Mk0.5 — thermopile fog detector and donning check (Track N, N-S2).
//
// Pure, header-only, native-tested.
//
//   FogDetector   sweat condensing on the MLX90614's lens makes the object
//                 reading collapse onto the ambient reading. Object within
//                 `delta_c` of ambient for `hold_ms` without interruption =
//                 fogged: main emits the temperature lines with q="gap" until
//                 the readings separate again.
//
//   DonningCheck  at session start the pacer asks for breaths; if fewer than
//                 `min_breaths` are detected inside `window_ms` the bar is
//                 not aimed at the nose (or the wearer breathes through the
//                 mouth) and main emits `cue: check-nose-sensor`.

#pragma once

#include <math.h>
#include <stdint.h>

namespace helmkit::dsp {

struct FogConfig {
    float    delta_c = 0.3f;
    uint32_t hold_ms = 20000;
};

class FogDetector {
 public:
    explicit FogDetector(const FogConfig& cfg = {}) : cfg_(cfg) {}
    // Returns the fogged state after this sample.
    bool feed(uint32_t t_ms, float object_c, float ambient_c) {
        const bool close = fabsf(object_c - ambient_c) < cfg_.delta_c;
        if (!close) { since_ = 0; fogged_ = false; return false; }
        if (since_ == 0) since_ = t_ms ? t_ms : 1;
        if ((int32_t)(t_ms - since_) >= (int32_t)cfg_.hold_ms) fogged_ = true;
        return fogged_;
    }
    bool fogged() const { return fogged_; }
    void reset() { since_ = 0; fogged_ = false; }
 private:
    FogConfig cfg_;
    uint32_t since_ = 0;
    bool     fogged_ = false;
};

class DonningCheck {
 public:
    enum class Result : uint8_t { kIdle = 0, kPending, kOk, kFail };

    void start(uint32_t t_ms, uint32_t window_ms = 30000, uint8_t min_breaths = 3) {
        start_ms_ = t_ms; window_ms_ = window_ms; min_ = min_breaths; breaths_ = 0; state_ = Result::kPending;
    }
    void breath(uint32_t) { if (state_ == Result::kPending) ++breaths_; }
    // Poll from the 1 Hz tick; returns kOk / kFail once when the window closes (or earlier for kOk), then kIdle.
    Result poll(uint32_t t_ms) {
        if (state_ != Result::kPending) return Result::kIdle;
        if (breaths_ >= min_) { state_ = Result::kIdle; return Result::kOk; }
        if ((int32_t)(t_ms - start_ms_) >= (int32_t)window_ms_) { state_ = Result::kIdle; return Result::kFail; }
        return Result::kPending;
    }
    void cancel() { state_ = Result::kIdle; }
    bool pending() const { return state_ == Result::kPending; }
    uint8_t breaths() const { return breaths_; }
 private:
    uint32_t start_ms_ = 0, window_ms_ = 30000;
    uint8_t  min_ = 3, breaths_ = 0;
    Result   state_ = Result::kIdle;
};

}  // namespace helmkit::dsp
