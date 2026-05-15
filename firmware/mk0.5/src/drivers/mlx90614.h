// HelmKit Mk0.5 — MLX90614 IR forehead-temp driver.
// Channel: "temp-forehead" (psiStabilizer v0.2-proposed; see docs/SCHEMA.md).
// Bus: Wire1 (Ext I2C, see PINOUT.md). I2C addr 0x5A.
// Conforms to the Sensor duck-typed concept.
// Wave 1: skeleton only; Wave 2 will use Adafruit_MLX90614 (pinned).
#pragma once
#include <Arduino.h>
#include "drivers/sensor.h"
#include "drivers/smoke_result.h"
namespace helmkit::drivers {
struct Mlx90614Sample {
    uint32_t t_ms;
    float ambient_c;
    float object_c;
};
class Mlx90614 {
public:
    bool begin();
    void pump();
    static constexpr const char* name() { return "temp-forehead"; }
    Health health() const { return health_; }
private:
    Health health_ = Health::kUninit;
};
SmokeResult mlx90614_smoke_test();
}  // namespace helmkit::drivers
