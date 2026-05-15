// HelmKit Mk0.5 — VBAT monitor.
// Channel: "vbat" (psiStabilizer v0.2-proposed; see docs/SCHEMA.md).
// Pins: GPIO37=ADC_CTRL (active-low gate), GPIO1=ADC1_CH0 divider read.
// Shares ADC1 with gsr.cpp via board/adc_mutex (see PRIOR_ART claim M8).
//
// Conforms to the Sensor duck-typed concept.
// Wave 1: skeleton only.
#pragma once
#include <Arduino.h>
#include "drivers/sensor.h"
#include "drivers/smoke_result.h"
namespace helmkit::drivers {
struct BatterySample {
    uint32_t t_ms;
    float volts;
    uint8_t percent;
    bool charging;  // CP2102 USB Vbus presence (Day 2 heuristic)
};
class Battery {
public:
    bool begin();
    void pump();
    static constexpr const char* name() { return "vbat"; }
    Health health() const { return health_; }
private:
    Health health_ = Health::kUninit;
};
SmokeResult battery_smoke_test();
}  // namespace helmkit::drivers
