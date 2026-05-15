// HelmKit Mk0.5 — VBAT monitor.
// TODO(Day 2): GPIO37=ADC_CTRL active-low gate, GPIO1=ADC1_CH0 divider read.
// MUST share a mutex with drivers::gsr to avoid ADC contention. See
// firmware/mk0.5/docs/PINOUT.md §3.
#pragma once
#include <Arduino.h>
namespace helmkit::drivers {
struct BatterySample {
    uint32_t t_ms;
    float volts;
    uint8_t percent;
    bool charging;  // CP2102 USB Vbus presence (Day 2 heuristic)
};
// bool battery_smoke_test();  // Day 2
}  // namespace helmkit::drivers
