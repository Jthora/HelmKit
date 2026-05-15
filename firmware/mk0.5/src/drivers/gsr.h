// HelmKit Mk0.5 — CJMCU-6701 GSR analog driver.
// Channel: "gsr" (psiStabilizer v0.2-proposed; see docs/SCHEMA.md).
// Pin: ADC1_CH3 on GPIO 4. Shares ADC1 with battery.cpp via board/adc_mutex.
//
// Conforms to the Sensor duck-typed concept (see drivers/sensor.h).
// Wave 1: skeleton only. begin() succeeds, pump() emits nothing,
//         smoke_test() returns SmokeResult::fail("not-yet-implemented", ...).
#pragma once
#include <Arduino.h>
#include "drivers/sensor.h"
#include "drivers/smoke_result.h"
namespace helmkit::drivers {
struct GsrSample {
    uint32_t t_ms;
    uint16_t raw;       // 0..4095 (12-bit ADC)
    float microsiemens; // calibrated, Day 2
};
class Gsr {
public:
    bool begin();
    void pump();
    static constexpr const char* name() { return "gsr"; }
    Health health() const { return health_; }
private:
    Health health_ = Health::kUninit;
};
SmokeResult gsr_smoke_test();
}  // namespace helmkit::drivers
