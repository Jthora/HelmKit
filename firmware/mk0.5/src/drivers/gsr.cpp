// HelmKit Mk0.5 — GSR driver (Wave 1 skeleton).
// See gsr.h. Wave 2 will populate pump() and smoke_test() proper.

#include "drivers/gsr.h"
#include "board/adc_mutex.h"
#include "board/pins.h"
#include "drivers/smoke_fail.h"

namespace helmkit::drivers {

bool Gsr::begin() {
    // CALIBRATION: 12-bit ADC; attenuation pinned to ADC_11db on ESP32-S3
    //              => 0..~3.1 V usable input range. Tied to PINOUT.md §3.
    analogReadResolution(12);
    analogSetPinAttenuation(pins::kGsrAdc, ADC_11db);
    health_ = Health::kOk;
    return true;
}

void Gsr::pump() {
    // Wave 2: 100 Hz read with with_adc1_lock() RAII lock, push to log/sink.
}

SmokeResult gsr_smoke_test() {
    Gsr g;
    if (!g.begin()) {
        return SmokeResult::fail(SmokeFail::kBeginFailed,
                                 "gsr begin failed", 0, 0, g.health());
    }

    uint16_t raw = 0;
    const bool got_lock = helmkit::board::with_adc1_lock(50, [&] {
        raw = analogRead(pins::kGsrAdc);
    });
    if (!got_lock) {
        return SmokeResult::fail(SmokeFail::kMutexTimeout,
                                 "gsr: adc1 mutex timeout", 0, 0, g.health());
    }
    // Stub returns kNotImplemented with sensor-specific note (closes UX5).
    return SmokeResult::fail(SmokeFail::kNotImplemented,
                             "gsr-wave2-stub", raw, 0, g.health());
}

}  // namespace helmkit::drivers
