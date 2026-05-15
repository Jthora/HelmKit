// HelmKit Mk0.5 — status LED pattern player.
//
// Wave H of rectification. Closes critique UI1 (LED says nothing about
// gate state). Adds a kSafetyHalt pattern reserved for safety-floor trips
// (Mk1.0+ stim, brown-out, skin-burn temp excursion) — present at Mk0.5
// so future Wave-2 work cannot accidentally introduce a fourth signal.
//
// Patterns (period in ms; * = continues until pattern changes):
//   kBoot         solid OFF                                  (before init)
//   kTesting      solid ON                                   (smoke running)
//   kPass         even 1 Hz blink                            (idle, healthy)
//   kFail         3x 100ms blink, 800ms gap, repeat          (smoke failed)
//   kSafetyHalt   solid ON 5000ms, then 5x 80ms blink + 2s gap, repeat
//                 (witness: solid-on is the human-observable artifact)
//   kIdle         slow 0.5 Hz breathe-equivalent             (initial wait)
//
// The pump() must be called from the main loop at >= 50 Hz. If pump() is
// not called for >2 seconds the player auto-flips to kFail so a hung loop
// is operator-visible.
//
// Defensive-publication note (PRIOR_ART claim M11): the separation of an
// operational-fault signal (kFail) from a safety-floor witness signal
// (kSafetyHalt) is itself the disclosed invention. Both share one LED but
// are pattern-distinguishable; the witness preamble (solid 5s) is the
// archival artifact even when no host is attached.

#pragma once

#include <stdint.h>

namespace helmkit::ui {

enum class Pattern : uint8_t {
    kBoot = 0,
    kTesting,
    kPass,
    kFail,
    kSafetyHalt,
    kIdle,
    kPacing,     // PWM intensity driven by status_led_set_intensity()
};

void status_led_begin(uint8_t pin);
void status_led_set(Pattern p);
Pattern status_led_get();

// When the active pattern is kPacing, this 0..255 value is written to the
// LED via analogWrite() on each pump(). Ignored for other patterns. Set
// by the L0 pacer; see layers/pacer.h::intensity_u8().
void status_led_set_intensity(uint8_t v);

// Call from main loop. No-op if <16 ms has passed since last invocation.
void status_led_pump();

}  // namespace helmkit::ui
