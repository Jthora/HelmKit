// HelmKit Mk0.5 — retry schedule for a faulted stream (Track N, N-F4).
//
// Pure, header-only, native-tested. A driver whose health is a sticky fault
// (no-ack, overflow, error) used to stay dead until the operator re-ran the
// smoke test. The supervisor in main.cpp arms one of these per stream and
// re-runs begin() on the schedule 5 s, 10 s, 20 s, then every 60 s until it
// succeeds or the operator stops the stream.
//
//   arm(now)      first fault seen: the first retry is due 5 s later
//   due(now)      true when a retry may run
//   fail(now)     the retry failed: push the next one out one step
//   succeed()     back to healthy: schedule cleared, attempts reset
//
// millis()-wrap safe: comparisons are done on the signed difference.

#pragma once

#include <stdint.h>

namespace helmkit::layers {

class Backoff {
 public:
    static constexpr uint8_t  kSteps     = 4;
    static constexpr uint32_t kStepMs[kSteps] = {5000, 10000, 20000, 60000};

    void arm(uint32_t now_ms) {
        if (armed_) return;
        idx_      = 0;
        next_ms_  = now_ms + kStepMs[0];
        armed_    = true;
    }
    bool due(uint32_t now_ms) const {
        return armed_ && (int32_t)(now_ms - next_ms_) >= 0;
    }
    void fail(uint32_t now_ms) {
        if (idx_ + 1 < kSteps) ++idx_;
        next_ms_ = now_ms + kStepMs[idx_];
        ++attempts_;
        armed_ = true;
    }
    void succeed() {
        idx_ = 0;
        attempts_ = 0;
        armed_ = false;
    }

    bool     armed()    const { return armed_; }
    uint16_t attempts() const { return attempts_; }
    uint32_t next_ms()  const { return next_ms_; }
    uint32_t step_ms()  const { return kStepMs[idx_]; }

 private:
    uint8_t  idx_      = 0;
    uint16_t attempts_ = 0;
    uint32_t next_ms_  = 0;
    bool     armed_    = false;
};

}  // namespace helmkit::layers
