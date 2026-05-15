// HelmKit Mk0.5 — MLX90614 IR forehead-temp driver.
// TODO(Day 2): implement against Adafruit_MLX90614 (pinned 2.1.5).
#pragma once
#include <Arduino.h>
namespace helmkit::drivers {
struct Mlx90614Sample {
    uint32_t t_ms;
    float ambient_c;
    float object_c;
};
// bool mlx90614_smoke_test();  // Day 2
}  // namespace helmkit::drivers
