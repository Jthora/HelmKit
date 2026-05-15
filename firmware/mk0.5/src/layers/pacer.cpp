// HelmKit Mk0.5 — L0 paced-breathing pacer (impl).
// See pacer.h.

#include "layers/pacer.h"

#include <Arduino.h>
#include <stdio.h>

#include "log/ndjson.h"
#include "log/session.h"

namespace helmkit::layers {

namespace {

// Emit a v0.1 channel-sample line for the "cue" channel.
// Wire shape: {"t":<s>,"ch":"cue","v":"<phase-or-event>","boot":"<hex>"}
//
// The `boot` field is non-standard for the v0.1 sample format but the
// validator accepts it (additionalProperties on SAMPLE_SCHEMA is
// permissive for forward-compat). It exists here because firmware-emit
// time is millis()-since-boot, so the boot id is needed to disambiguate
// cue lines from concatenated sessions.
void emit_cue(const char* value) {
    if (!helmkit::log::serial_attached()) return;
    char hex[17];
    helmkit::log::boot_id_hex(hex);
    char buf[160];
    const float t = (float)millis() / 1000.0f;
    snprintf(buf, sizeof buf,
             "{\"t\":%.3f,\"ch\":\"cue\",\"v\":\"%s\",\"boot\":\"%s\"}",
             t, value, hex);
    Serial.println(buf);
}

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
