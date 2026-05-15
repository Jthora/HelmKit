// HelmKit Mk0.5 — GSR driver (Wave 1 skeleton).
// See gsr.h. Wave 2 will populate pump() and smoke_test() proper.

#include "drivers/gsr.h"
#include "board/adc_mutex.h"
#include "board/pins.h"

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
    // Wave 2: 100 Hz read with adc1_acquire() RAII lock, push to log/sink.
}

SmokeResult gsr_smoke_test() {
    // Smoke procedure (Wave 2): contend with battery.cpp by issuing 10 reads
    // each while battery is also reading; verify no corrupted samples and
    // that the mutex was actually acquired both ways. For now: stub fail.
    Gsr g;
    if (!g.begin()) return SmokeResult::fail("gsr-begin-failed", 0, 0);

    // Single-shot raw read proving the mutex path links.
    helmkit::board::Adc1Lock lock(50);
    if (!lock.ok()) return SmokeResult::fail("adc1-mutex-timeout", 0, 0);
    const uint16_t raw = analogRead(pins::kGsrAdc);
    return SmokeResult::fail("not-yet-implemented", raw, 0);
}

}  // namespace helmkit::drivers
