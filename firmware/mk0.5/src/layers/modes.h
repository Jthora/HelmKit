// HelmKit Mk0.5 — Combat-trim mode state machine (Track M, M-F5).
//
// Five modes from docs/plans/2026-tier1-launch/track-M-combat-trim.md §6,
// driven by operator cues (round buttons, tally button) and periodic ticks
// carrying the latest heart rate and stillness. Output: the current mode,
// the pacer configuration the mode wants, and "mode:*" / "tally-ack" /
// "impact:Ng" / "summary:*" cue strings for the `cue` channel.
//
//   SANCTUARY       resonance pacer 6 bpm (4 s / 6 s), intrusion tally armed
//   TRANQUIL        resonance pacer 6 bpm; the default after session-start
//   COMBAT_PRIME    fast priming breaths (2 s / 1 s) for kPrimeMs before a
//                   round, entered on the `prime` cue; settles to TRANQUIL
//                   if no round starts
//   COMBAT_SUSTAIN  pacer OFF during the round; only impact cues (>= 10 g)
//   RECOVER         cyclic sighing (3 s / 7 s) after round-end until HR is
//                   within 20 bpm of the resting HR learned in the calm
//                   modes, or kRecoverMs elapse; then TRANQUIL
//
// This mirrors tools/analyze_combat_session.py::CombatModes (the behavioural
// spec; keep them in step). Pure C++, no Arduino: the same code runs in the
// native unit tests. The pacer itself (layers/pacer.h) stays the owner of the
// inhale/exhale cues; main applies `pacer()` to it on mode changes.
//
// Safety: modes only shape the breathing pacer's LED / serial cues. Nothing
// here drives a stim output (safety/no_stim_below_mk1.h still applies).

#pragma once

#include <stdint.h>

namespace helmkit::layers {

enum class Mode : uint8_t {
    kNone = 0,
    kSanctuary,
    kTranquil,
    kCombatPrime,
    kCombatSustain,
    kRecover,
};

const char* mode_str(Mode m);   // "sanctuary", "tranquil", "combat-prime", "combat-sustain", "recover", "none"

enum class ModeCue : uint8_t {
    kSessionStart,
    kSessionEnd,
    kRoundStart,
    kRoundEnd,
    kPrime,
    kSanctuary,
    kTally,
};

struct ModePacerConfig {
    bool        enabled;
    uint32_t    inhale_ms;
    uint32_t    exhale_ms;
    const char* pattern;   // "resonance" | "prime" | "off" | "cyclic-sigh"
};

class CombatModes {
 public:
    static constexpr uint32_t kPrimeMs           = 60000;
    static constexpr uint32_t kRecoverMs         = 90000;
    static constexpr float    kHrRecoveredMargin = 20.0f;
    static constexpr float    kImpactCueG        = 10.0f;

    // Cue sink: called with a NUL-terminated cue value ("mode:tranquil", ...).
    using Emit = void (*)(const char* cue, void* user);
    void set_emitter(Emit fn, void* user) { emit_fn_ = fn; user_ = user; }

    // Operator / timer cues. Outside a session only kSessionStart is honoured.
    void event(uint32_t t_ms, ModeCue cue);

    // Periodic tick (1 Hz is plenty). hr_bpm: NaN when unknown. still: 1, 0,
    // or -1 when there is no IMU. impact_g: NaN when no impact this tick.
    void tick(uint32_t t_ms, float hr_bpm, int8_t still, float impact_g);

    Mode            mode()       const { return mode_; }
    bool            in_session() const { return in_session_; }
    uint32_t        tally()      const { return tally_; }
    float           resting_hr() const { return resting_hr_; }   // NaN until learned
    ModePacerConfig pacer()      const;                          // for the current mode (off when kNone)

    static ModePacerConfig pacer_for(Mode m);

 private:
    void enter_(Mode m, uint32_t t_ms);
    void emit_(const char* cue);

    Mode     mode_        = Mode::kNone;
    uint32_t entered_ms_  = 0;
    bool     in_session_  = false;
    float    resting_hr_;          // NaN until learned (set in ctor)
    uint32_t tally_       = 0;
    Emit     emit_fn_     = nullptr;
    void*    user_        = nullptr;

 public:
    CombatModes();
};

}  // namespace helmkit::layers
