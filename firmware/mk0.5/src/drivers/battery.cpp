// HelmKit Mk0.5 — VBAT monitor (Wave 1 skeleton).
// See battery.h.

#include "drivers/battery.h"
#include "board/adc_mutex.h"
#include "board/pins.h"
#include "drivers/smoke_fail.h"

namespace helmkit::drivers {

namespace {
// CALIBRATION: Heltec V3 VBAT divider = 390k / 100k → factor 4.9 nominal.
//              Refine after first calibrated read against a known LiPo.
constexpr float kVbatDividerFactor = 4.9f;
// CALIBRATION: ESP32-S3 ADC1 reference ~3.3 V; ADC_11db full-scale ~3.1 V.
//              Use 3.3 V here, then correct via per-board offset in Wave 2.
constexpr float kAdcRefV = 3.3f;
}  // namespace

bool Battery::begin() {
    pinMode(pins::kAdcCtrl, OUTPUT);
    digitalWrite(pins::kAdcCtrl, HIGH);  // disabled at rest (active-low)
    analogReadResolution(12);
    analogSetPinAttenuation(pins::kVbatAdc, ADC_11db);
    health_ = Health::kOk;
    return true;
}

void Battery::pump() {
    // Wave 2: 1 Hz read with adc1_acquire() RAII lock; gate ADC_CTRL low only
    //         for the duration of the read; restore high; release mutex.
}

SmokeResult battery_smoke_test() {
    Battery b;
    if (!b.begin()) {
        return SmokeResult::fail(SmokeFail::kBeginFailed,
                                 "battery begin failed", 0, 0, b.health());
    }

    uint16_t raw = 0;
    const bool got_lock = helmkit::board::with_adc1_lock(50, [&] {
        digitalWrite(pins::kAdcCtrl, LOW);    // enable divider (active-low)
        delayMicroseconds(50);                // settle (R8: TODO Wave 2 verify)
        raw = analogRead(pins::kVbatAdc);
        digitalWrite(pins::kAdcCtrl, HIGH);   // disable — RAII inside lambda
                                              // closes R7 (ADC_CTRL leak path)
    });
    if (!got_lock) {
        return SmokeResult::fail(SmokeFail::kMutexTimeout,
                                 "vbat: adc1 mutex timeout", 0, 0, b.health());
    }

    const float v = (raw / 4095.0f) * kAdcRefV * kVbatDividerFactor;
    // Evidence: raw in evidence_a; millivolts in evidence_b.
    return SmokeResult::fail(SmokeFail::kNotImplemented,
                             "vbat-wave2-stub",
                             raw,
                             static_cast<uint32_t>(v * 1000.0f),
                             b.health());
}

}  // namespace helmkit::drivers
