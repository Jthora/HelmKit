// HelmKit Mk0.5 — L0 paced-breathing pacer (impl).
// See pacer.h.

#include "layers/pacer.h"

#include <Arduino.h>
#include <stdio.h>

#include "log/ndjson.h"
#include "log/session.h"

namespace helmkit::layers {

namespace {

// Cue lines go through the shared NDJSON emitter (Track M): same wire shape
// as before, one Serial.println per line.
void emit_cue(const char* value) { helmkit::log::emit_cue(value); }

}  // namespace

const char* phase_str(Phase p) {
    switch (p) {
        case Phase::kIdle:   return "idle";
        case Phase::kInhale: return "inhale";
        case Phase::kExhale: return "exhale";
    }
    return "?";
}

void Pacer::begin(uint32_t inhale_ms, uint32_t exhale_ms) {
    inhale_ms_ = inhale_ms;
    exhale_ms_ = exhale_ms;
    running_ = false;
    phase_ = Phase::kIdle;
    cycle_ = 0;
}

void Pacer::enter_(Phase p, uint32_t now_ms) {
    phase_ = p;
    phase_started_ms_ = now_ms;
    emit_cue(phase_str(p));
}

void Pacer::start(uint32_t now_ms) {
    if (running_) return;
    running_ = true;
    cycle_ = 0;
    emit_cue("session-start");
    enter_(Phase::kInhale, now_ms);
}

void Pacer::stop(uint32_t now_ms) {
    if (!running_) return;
    running_ = false;
    phase_ = Phase::kIdle;
    emit_cue("session-end");
    (void)now_ms;
}

void Pacer::tick(uint32_t now_ms) {
    if (!running_) return;
    const uint32_t dur = (phase_ == Phase::kInhale) ? inhale_ms_ : exhale_ms_;
    const uint32_t elapsed = now_ms - phase_started_ms_;
    if (elapsed < dur) return;
    // Phase boundary. Advance.
    if (phase_ == Phase::kInhale) {
        enter_(Phase::kExhale, phase_started_ms_ + inhale_ms_);
    } else {
        // Completed one full cycle.
        ++cycle_;
        enter_(Phase::kInhale, phase_started_ms_ + exhale_ms_);
    }
}

uint32_t Pacer::phase_elapsed_ms(uint32_t now_ms) const {
    if (!running_) return 0;
    return now_ms - phase_started_ms_;
}

void Pacer::retune(uint32_t inhale_ms, uint32_t exhale_ms, uint32_t now_ms) {
    inhale_ms_ = inhale_ms;
    exhale_ms_ = exhale_ms;
    if (running_) enter_(Phase::kInhale, now_ms);
}

void Pacer::suspend() {
    running_ = false;
    phase_ = Phase::kIdle;
}

void Pacer::resume(uint32_t now_ms) {
    if (running_) return;
    running_ = true;
    enter_(Phase::kInhale, now_ms);
}

uint8_t Pacer::intensity_u8(uint32_t now_ms) const {
    if (!running_) return 0;
    const uint32_t e = phase_elapsed_ms(now_ms);
    if (phase_ == Phase::kInhale) {
        const uint32_t scaled = (e * 255UL) / (inhale_ms_ ? inhale_ms_ : 1);
        return scaled > 255 ? 255 : (uint8_t)scaled;
    }
    if (phase_ == Phase::kExhale) {
        const uint32_t denom = exhale_ms_ ? exhale_ms_ : 1;
        if (e >= denom) return 0;
        const uint32_t scaled = ((denom - e) * 255UL) / denom;
        return scaled > 255 ? 255 : (uint8_t)scaled;
    }
    return 0;
}

}  // namespace helmkit::layers
