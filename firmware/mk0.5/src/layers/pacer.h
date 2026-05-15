// HelmKit Mk0.5 — L0 paced-breathing pacer.
//
// The L0 layer per docs/mk0.5_firmware_bringup.md §2. State machine that
// drives a 6-bpm resonance-breathing cadence:
//
//     inhale (4 s, rising envelope)  ->  exhale (6 s, falling envelope)
//
// The pacer is pure timekeeping + cue emission. It does NOT own any
// output hardware directly; instead it exposes:
//
//   - phase()        : the current Phase enum
//   - intensity_u8() : a 0..255 breath envelope suitable for analogWrite()
//   - cycle_count()  : monotonic count of completed exhale->inhale boundaries
//
// On every phase transition it emits a kind:"sample" NDJSON line on the
// "cue" channel (psiStabilizer v0.1 SCHEMA.md §2.2) so the analysis
// pipeline can align physiological windows to breath phase.
//
// Defensive-publication note: the 4s/6s asymmetric envelope at 6 bpm is
// the published HeartMath / Lehrer resonance-breathing target. The
// inventive element disclosed here is the *combination* of this pacer
// with the L1 HRV-coherence rendering and the L2 session container
// (PRIOR_ART claim C1+C2+C3 — see PRIOR_ART.md §4 item 2).

#pragma once

#include <stdint.h>

namespace helmkit::layers {

enum class Phase : uint8_t {
    kIdle = 0,
    kInhale,
    kExhale,
};

const char* phase_str(Phase p);

class Pacer {
 public:
    // Defaults: 4 s inhale, 6 s exhale, 0 s hold (6 bpm).
    // Tunable per-instance for future Mk1.x research modes.
    void begin(uint32_t inhale_ms = 4000,
               uint32_t exhale_ms = 6000);

    // Start a new session. Emits a "session-start" cue + the first
    // "inhale" cue. now_ms = millis() at call site.
    void start(uint32_t now_ms);

    // Stop the active session. Emits a "session-end" cue. Idempotent.
    void stop(uint32_t now_ms);

    // Call from main loop at >= 50 Hz while the pacer is running.
    // Emits phase-boundary cues. Safe to call when stopped (no-op).
    void tick(uint32_t now_ms);

    bool    running()       const { return running_; }
    Phase   phase()         const { return phase_; }
    uint32_t cycle_count()  const { return cycle_; }
    uint32_t inhale_ms()    const { return inhale_ms_; }
    uint32_t exhale_ms()    const { return exhale_ms_; }
    uint32_t cycle_ms()     const { return inhale_ms_ + exhale_ms_; }

    // 0..255 breath envelope. Rises 0->255 over inhale, falls 255->0 over
    // exhale. Returns 0 when not running.
    uint8_t intensity_u8(uint32_t now_ms) const;

    // ms into the current phase. 0 when not running.
    uint32_t phase_elapsed_ms(uint32_t now_ms) const;

 private:
    bool     running_         = false;
    Phase    phase_           = Phase::kIdle;
    uint32_t inhale_ms_       = 4000;
    uint32_t exhale_ms_       = 6000;
    uint32_t phase_started_ms_ = 0;
    uint32_t cycle_            = 0;

    void enter_(Phase p, uint32_t now_ms);
};

}  // namespace helmkit::layers
