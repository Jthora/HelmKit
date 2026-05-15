// HelmKit Mk0.5 — AD8232 ECG analog front-end. Wave 2.
// TODO(Day 4): ADC1_CH4 on GPIO 5, leads-off on GPIO 6/7.
#pragma once
#include <Arduino.h>
namespace helmkit::drivers {
struct Ad8232Sample {
    uint32_t t_ms;
    uint16_t raw;
    bool leads_off_plus;
    bool leads_off_minus;
};
}  // namespace helmkit::drivers
