// HelmKit Mk0.5 — MLX90614 IR forehead-temp driver.
// Channel: "temp-forehead" + "temp-forehead.amb" (psiStabilizer v0.2-proposed;
// see docs/SCHEMA.md §2.2). Bus: Wire1 (Ext I2C, see PINOUT.md). I2C 0x5A.
// Conforms to the Sensor duck-typed concept (drivers/sensor.h).
//
// Wave J Bridge B (2026-05-18): driver populated for streaming + smoke test
// against in-inventory EC Buying GY-906 modules. Adafruit_MLX90614 (pinned
// in platformio.ini lib_deps) is the SMBus backend; we hide it behind a
// type-erased impl_ pointer to match the max30102 driver's discipline and
// keep the public header lib-free.
#pragma once

#include <Arduino.h>
#include <Wire.h>

#include "drivers/sensor.h"
#include "drivers/smoke_result.h"

namespace helmkit::drivers {

struct Mlx90614Sample {
    uint32_t t_ms;
    float ambient_c;
    float object_c;
    bool in_range;     // true iff 15 < object_c < 45 (SCHEMA §4)
};

struct Mlx90614Config {
    // Sample period in milliseconds. SCHEMA §2.2 declares 4 Hz → 250 ms.
    // Lower bound enforced inside the driver: MLX90614 SMBus refresh is
    // datasheet-bounded at ~50 ms per dual-temp read, so the practical
    // floor is ~100 ms; 250 ms is a comfortable default.
    uint32_t period_ms = 250;
};

using Mlx90614Callback = void (*)(const Mlx90614Sample&);

class Mlx90614 {
public:
    Mlx90614() = default;
    ~Mlx90614();
    Mlx90614(const Mlx90614&) = delete;
    Mlx90614& operator=(const Mlx90614&) = delete;

    bool begin(TwoWire& bus, const Mlx90614Config& cfg = {});

    // Non-blocking: emits at most one sample per call when period elapsed.
    // Returns 1 if a sample was produced and the callback fired, else 0.
    uint8_t pump(Mlx90614Callback cb);

    static constexpr const char* name() { return "temp-forehead"; }
    Health health() const { return health_; }

private:
    void*           impl_       = nullptr;   // Adafruit_MLX90614*
    Mlx90614Config  cfg_        = {};
    uint32_t        last_emit_  = 0;
    Health          health_     = Health::kUninit;
};

SmokeResult mlx90614_smoke_test();

}  // namespace helmkit::drivers
