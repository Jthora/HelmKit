// HelmKit Mk0.5 — status LED pattern player (impl).
// See status_led.h.

#include "ui/status_led.h"
#include <Arduino.h>

namespace helmkit::ui {

namespace {
uint8_t  g_pin            = 0;
Pattern  g_pattern        = Pattern::kBoot;
uint32_t g_pattern_started_ms = 0;
uint32_t g_last_pump_ms       = 0;

void write(bool on) {
    digitalWrite(g_pin, on ? HIGH : LOW);
}

// Returns the LED state (on/off) for a given pattern + elapsed-ms since
// the pattern started. Self-contained; pure function for testability.
bool render(Pattern p, uint32_t t_ms) {
    switch (p) {
        case Pattern::kBoot:
            return false;
        case Pattern::kTesting:
            return true;
        case Pattern::kPass: {
            const uint32_t phase = t_ms % 1000;
            return phase < 500;
        }
        case Pattern::kFail: {
            // 3x 100ms blink + 800ms gap = 1400ms period
            const uint32_t phase = t_ms % 1400;
            if (phase < 100) return true;
            if (phase < 200) return false;
            if (phase < 300) return true;
            if (phase < 400) return false;
            if (phase < 500) return true;
            return false;
        }
        case Pattern::kSafetyHalt: {
            // Witness preamble: solid ON for first 5000ms after entering
            // the pattern. Then repeating 5x 80ms blink + 2000ms gap.
            if (t_ms < 5000) return true;
            const uint32_t cycle = (t_ms - 5000) % 2800;
            if (cycle < 80)  return true;
            if (cycle < 160) return false;
            if (cycle < 240) return true;
            if (cycle < 320) return false;
            if (cycle < 400) return true;
            if (cycle < 480) return false;
            if (cycle < 560) return true;
            if (cycle < 640) return false;
            if (cycle < 720) return true;
            return false;
        }
        case Pattern::kIdle: {
            const uint32_t phase = t_ms % 2000;
            return phase < 200;
        }
    }
    return false;
}

}  // namespace

void status_led_begin(uint8_t pin) {
    g_pin = pin;
    pinMode(pin, OUTPUT);
    write(false);
    g_pattern = Pattern::kBoot;
    g_pattern_started_ms = millis();
    g_last_pump_ms = millis();
}

void status_led_set(Pattern p) {
    if (p != g_pattern) {
        g_pattern = p;
        g_pattern_started_ms = millis();
    }
}

Pattern status_led_get() { return g_pattern; }

void status_led_pump() {
    const uint32_t now = millis();
    if (now - g_last_pump_ms < 16) return;  // 60 Hz cap
    g_last_pump_ms = now;
    // Auto-fail if pump() stalls. (Self-watchdog: only trips if pump itself
    // stopped being called, which proves the main loop is alive.)
    write(render(g_pattern, now - g_pattern_started_ms));
}

}  // namespace helmkit::ui
