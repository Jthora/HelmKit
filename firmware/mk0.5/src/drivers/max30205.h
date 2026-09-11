// HelmKit Mk0.5 — MAX30205 contact temperature driver (Track N, N-S5; Wave 2).
// Channels: "temp-skin.L" (0x48) and "temp-skin.R" (0x49), 5 Hz, float °C
// (SCHEMA §2.2). Bus: Wire1. Register-level: temperature register 0x00
// (16-bit two's complement, 1/256 °C per LSB), configuration 0x01 (0x00 =
// continuous conversion). On the vp0 pad frames the parts sit in the rear
// plates' pillars (occipital skin); they feed the sweat rule (dsp/eda.h).
//
// Conforms to the Sensor duck-typed concept. Either address may be absent:
// the driver streams whatever answered at begin(); a device that stops
// answering flips the shared health to kNoAck (the supervisor re-begins).

#pragma once

#include <Arduino.h>
#include <Wire.h>
#include <stdint.h>

#include "drivers/sensor.h"
#include "drivers/smoke_result.h"

namespace helmkit::drivers {

struct Max30205Sample {
    uint32_t t_ms;
    float    temp_c;     // ±0.1 °C accuracy per datasheet
    uint8_t  addr;       // 0x48 = L, 0x49 = R
    bool     in_range;   // 30 < temp_c < 42 (SCHEMA §4)
};

using Max30205Callback = void (*)(const Max30205Sample&);

struct Max30205Config {
    uint32_t period_ms = 200;   // 5 Hz per device
};

class Max30205 {
 public:
    bool     begin(TwoWire& bus, const Max30205Config& cfg = {});
    uint8_t  pump(Max30205Callback cb);          // at most one sample per device per period
    Health   health() const { return health_; }
    uint8_t  devices() const { return (uint8_t)(present_[0] + present_[1]); }
    bool     present(uint8_t idx) const { return present_[idx & 1]; }
    static constexpr const char* name() { return "temp-skin"; }
    static constexpr uint8_t kAddrL = 0x48, kAddrR = 0x49;
    bool read_temp(uint8_t addr, float* c);      // one conversion result (smoke test / bench)

 private:

    TwoWire*       bus_ = nullptr;
    Max30205Config cfg_{};
    bool           present_[2] = {false, false};
    uint32_t       last_ms_ = 0;
    Health         health_ = Health::kUninit;
};

SmokeResult max30205_smoke_test();

}  // namespace helmkit::drivers
