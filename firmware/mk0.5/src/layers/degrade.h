// HelmKit Mk0.5 — degradation order (Track N, N-F7).
//
// Pure, header-only, native-tested. One place decides what is shed under
// link pressure. Fed at every heartbeat with the writer's cumulative drop
// count:
//
//   shed raw streams (gsr, temp-* samples) when more than `shed_drops` lines
//   were dropped since the previous heartbeat; the derived events (RR,
//   breaths, cues, health, hb) keep going. Restore the raw streams after
//   `restore_quiet_ms` without a drop.
//
// Derived events are never shed by this policy, and cues are owned by the
// mode machine, which never emits one in a mode that forbids it.

#pragma once

#include <stdint.h>

namespace helmkit::layers {

struct DegradeConfig {
    uint32_t shed_drops       = 20;      // per heartbeat interval (5 s)
    uint32_t restore_quiet_ms = 30000;
};

class Degrade {
 public:
    explicit Degrade(const DegradeConfig& cfg = {}) : cfg_(cfg) {}

    // Returns the current decision: true = shed the raw streams.
    bool feed(uint32_t t_ms, uint32_t drops_total) {
        const uint32_t delta = drops_total - last_total_;
        last_total_ = drops_total;
        if (delta > cfg_.shed_drops) {
            shed_ = true;
            last_bad_ms_ = t_ms;
            ++episodes_;
        } else if (shed_ && (int32_t)(t_ms - last_bad_ms_) >= (int32_t)cfg_.restore_quiet_ms) {
            shed_ = false;
        }
        return shed_;
    }

    bool     shed_raw() const { return shed_; }
    uint32_t episodes() const { return episodes_; }

 private:
    DegradeConfig cfg_;
    uint32_t last_total_ = 0, last_bad_ms_ = 0, episodes_ = 0;
    bool     shed_ = false;
};

}  // namespace helmkit::layers
