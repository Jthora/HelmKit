// HelmKit Mk0.5 — VBAT monitor (Track N, N-F3: real reads).
// See battery.h. Shares ADC1 with gsr.cpp through board/adc_mutex; the
// divider is gated on only for the read (ADC_CTRL active-low, ~50 µs settle).

#include "drivers/battery.h"
#include "board/adc_mutex.h"
#include "board/pins.h"
#include "drivers/smoke_fail.h"
#include "layers/power_policy.h"

namespace helmkit::drivers {

namespace {
// CALIBRATION: Heltec V3 VBAT divider = 390k / 100k → factor 4.9 nominal.
//              Refine after the first calibrated read against a known LiPo.
constexpr float kVbatDividerFactor = 4.9f;
// CALIBRATION: ESP32-S3 ADC1 reference ~3.3 V; ADC_11db full-scale ~3.1 V.
constexpr float kAdcRefV = 3.3f;

BatterySample g_last{};
uint16_t      g_last_raw = 0;

bool read_raw(uint16_t* raw, uint32_t timeout_ms) {
    return helmkit::board::with_adc1_lock(timeout_ms, [&] {
        digitalWrite(pins::kAdcCtrl, LOW);    // enable the divider (active-low)
        delayMicroseconds(50);
        *raw = (uint16_t)analogRead(pins::kVbatAdc);
        digitalWrite(pins::kAdcCtrl, HIGH);   // disable: no leak path through the divider
    });
}
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
    uint16_t raw = 0;
    if (!read_raw(&raw, 5)) { health_ = Health::kError; return; }   // mutex busy: try next second
    g_last_raw = raw;
    g_last.t_ms     = millis();
    g_last.volts    = (raw / 4095.0f) * kAdcRefV * kVbatDividerFactor;
    g_last.percent  = helmkit::layers::PowerPolicy::percent(g_last.volts);
    g_last.charging = false;   // no Vbus sense on this board; the charger IC's LED is the indicator
    health_ = Health::kOk;
}

const BatterySample& battery_last() { return g_last; }
uint16_t battery_last_raw() { return g_last_raw; }

SmokeResult battery_smoke_test() {
    Battery b;
    if (!b.begin()) {
        return SmokeResult::fail(SmokeFail::kBeginFailed, "battery begin failed", 0, 0, b.health());
    }
    uint16_t raw = 0;
    if (!read_raw(&raw, 50)) {
        return SmokeResult::fail(SmokeFail::kMutexTimeout, "vbat: adc1 mutex timeout", 0, 0, b.health());
    }
    const float v = (raw / 4095.0f) * kAdcRefV * kVbatDividerFactor;
    const uint32_t mv = static_cast<uint32_t>(v * 1000.0f);
    // A LiPo reads 3.0..4.3 V; with no battery the divider floats near 0.
    if (v < 2.5f) {
        return SmokeResult::fail(SmokeFail::kOutOfRange, "vbat: no battery (USB only) or divider fault", raw, mv, b.health());
    }
    if (v > 4.4f) {
        return SmokeResult::fail(SmokeFail::kOutOfRange, "vbat: above 4.4 V (divider factor or wiring)", raw, mv, b.health());
    }
    return SmokeResult::pass(raw, mv, b.health());
}

}  // namespace helmkit::drivers
