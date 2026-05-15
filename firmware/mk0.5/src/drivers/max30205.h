// HelmKit Mk0.5 — MAX30205 high-precision contact-temp driver. Wave 2.
// TODO(Day 4): I2C @ 0x48/0x49 on Wire1.
#pragma once
#include <Arduino.h>
namespace helmkit::drivers {
struct Max30205Sample {
    uint32_t t_ms;
    float temp_c;       // ±0.1°C accuracy per datasheet
    uint8_t addr;       // distinguishes left/right temple
};
}  // namespace helmkit::drivers
