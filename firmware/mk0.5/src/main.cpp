// HelmKit Mk0.5 — main dispatcher.
//
// Day 1: runs the MAX30102 smoke test, then idles with a heartbeat LED.
// Day 2+: dispatches to L0/L1/L2 state machines per
//         docs/mk0.5_firmware_bringup.md.

#include <Arduino.h>

#include "board/pins.h"
#include "drivers/max30102.h"

namespace {

void heartbeat() {
    static uint32_t t_last = 0;
    static bool on = false;
    const uint32_t now = millis();
    if (now - t_last >= 500) {
        t_last = now;
        on = !on;
        digitalWrite(helmkit::pins::kStatusLed, on ? HIGH : LOW);
    }
}

void banner() {
    Serial.println();
    Serial.println(F("===================================================="));
    Serial.println(F(" HelmKit Mk0.5  --  Heltec WiFi LoRa 32 V3"));
    Serial.print  (F(" build: "));
    Serial.print  (F(__DATE__));
    Serial.print  (F(" "));
    Serial.println(F(__TIME__));
    Serial.println(F("===================================================="));
}

}  // namespace

void setup() {
    pinMode(helmkit::pins::kStatusLed, OUTPUT);
    digitalWrite(helmkit::pins::kStatusLed, LOW);

    Serial.begin(115200);
    // Give USB-CDC a moment to attach so the banner isn't lost.
    const uint32_t t0 = millis();
    while (!Serial && (millis() - t0) < 2000) { /* wait */ }
    banner();

    // Day 1 smoke test (MAX30102 only; skipped if no chip on bus).
    const bool ok = helmkit::drivers::max30102_smoke_test();
    Serial.print(F("[main] L0 MAX30102 gate: "));
    Serial.println(ok ? F("PASS") : F("FAIL"));
}

void loop() {
    heartbeat();
    // TODO(Day 3): dispatch to layer state machines.
    delay(10);
}
