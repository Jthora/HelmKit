// HelmKit Mk0.5 — CJMCU-6701 GSR analog driver.
// TODO(Day 2): implement ADC1_CH3 reads on GPIO 4 with battery-monitor mutex.
// See firmware/mk0.5/docs/PINOUT.md §3 for the ADC conflict resolution.
#pragma once
#include <Arduino.h>
namespace helmkit::drivers {
struct GsrSample {
    uint32_t t_ms;
    uint16_t raw;       // 0..4095 (12-bit ADC)
    float microsiemens; // calibrated, Day 2
};
// bool gsr_smoke_test();  // Day 2
}  // namespace helmkit::drivers
