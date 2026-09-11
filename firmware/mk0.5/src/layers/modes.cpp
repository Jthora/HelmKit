// HelmKit Mk0.5 — Combat-trim mode state machine (Track M, M-F5).
// Behavioural spec: tools/analyze_combat_session.py::CombatModes.

#include "layers/modes.h"

#include <math.h>
#include <stdio.h>

namespace helmkit::layers {

const char* mode_str(Mode m) {
    switch (m) {
        case Mode::kNone:          return "none";
        case Mode::kSanctuary:     return "sanctuary";
        case Mode::kTranquil:      return "tranquil";
        case Mode::kCombatPrime:   return "combat-prime";
        case Mode::kCombatSustain: return "combat-sustain";
        case Mode::kRecover:       return "recover";
    }
    return "?";
}

ModePacerConfig CombatModes::pacer_for(Mode m) {
    switch (m) {
        case Mode::kSanctuary:     return {true, 4000, 6000, "resonance"};
        case Mode::kTranquil:      return {true, 4000, 6000, "resonance"};
        case Mode::kCombatPrime:   return {true, 2000, 1000, "prime"};
        case Mode::kCombatSustain: return {false, 0, 0, "off"};
        case Mode::kRecover:       return {true, 3000, 7000, "cyclic-sigh"};
        case Mode::kNone:          break;
    }
    return {false, 0, 0, "off"};
}

CombatModes::CombatModes() : resting_hr_(nanf("")) {}

ModePacerConfig CombatModes::pacer() const { return pacer_for(mode_); }

void CombatModes::emit_(const char* cue) {
    if (emit_fn_) emit_fn_(cue, user_);
}

void CombatModes::enter_(Mode m, uint32_t t_ms) {
    if (m == mode_) return;
    mode_ = m;
    entered_ms_ = t_ms;
    char buf[40];
    snprintf(buf, sizeof buf, "mode:%s", mode_str(m));
    emit_(buf);
}

void CombatModes::event(uint32_t t_ms, ModeCue cue) {
    if (cue == ModeCue::kSessionStart) {
        in_session_ = true;
        enter_(Mode::kTranquil, t_ms);
        return;
    }
    if (cue == ModeCue::kSessionEnd) {
        in_session_ = false;
        char buf[40];
        snprintf(buf, sizeof buf, "summary:tally=%lu", (unsigned long)tally_);
        emit_(buf);
        mode_ = Mode::kNone;        // no "mode:" cue on the way out (matches the Python)
        entered_ms_ = 0;
        return;
    }
    if (!in_session_) return;
    switch (cue) {
        case ModeCue::kSanctuary:  enter_(Mode::kSanctuary, t_ms);     break;
        case ModeCue::kPrime:      enter_(Mode::kCombatPrime, t_ms);   break;
        case ModeCue::kRoundStart: enter_(Mode::kCombatSustain, t_ms); break;
        case ModeCue::kRoundEnd:   enter_(Mode::kRecover, t_ms);       break;
        case ModeCue::kTally:
            ++tally_;
            emit_("tally-ack");
            break;
        default: break;
    }
}

void CombatModes::restore(uint32_t t_ms, uint32_t tally) {
    in_session_ = true;
    tally_ = tally;
    mode_ = Mode::kNone;            // force the mode: line even if we were already Tranquil
    enter_(Mode::kTranquil, t_ms);
}

void CombatModes::tick(uint32_t t_ms, float hr_bpm, int8_t still, float impact_g) {
    if (!in_session_ || mode_ == Mode::kNone) return;
    const bool have_hr = !isnan(hr_bpm);
    const uint32_t elapsed = t_ms - entered_ms_;   // wrap-safe
    if ((mode_ == Mode::kTranquil || mode_ == Mode::kSanctuary) && have_hr && still == 1) {
        // resting HR: slowest still HR seen in the calm modes
        resting_hr_ = isnan(resting_hr_) ? hr_bpm : (hr_bpm < resting_hr_ ? hr_bpm : resting_hr_);
    }
    if (mode_ == Mode::kCombatPrime && elapsed >= kPrimeMs) {
        enter_(Mode::kTranquil, t_ms);              // primed but the round did not start: settle
    } else if (mode_ == Mode::kRecover) {
        const bool recovered = !isnan(resting_hr_) && have_hr && hr_bpm <= resting_hr_ + kHrRecoveredMargin;
        if (recovered || elapsed >= kRecoverMs) enter_(Mode::kTranquil, t_ms);
    }
    if (mode_ == Mode::kCombatSustain && !isnan(impact_g) && impact_g >= kImpactCueG) {
        char buf[32];
        snprintf(buf, sizeof buf, "impact:%.0fg", (double)impact_g);
        emit_(buf);
    }
}

}  // namespace helmkit::layers
