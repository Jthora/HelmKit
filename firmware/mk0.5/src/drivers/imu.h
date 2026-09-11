// HelmKit Mk0.5 — 6-axis IMU driver, accelerometer stream (Track N, N-S4; Track M, M-F1).
//
// Register-level, no library dependency, so nothing new is pinned. Two chip
// families are auto-detected on the external I²C bus (Wire1) because the
// part has not been bought yet:
//
//   MPU-6050 / 6500 / 9250 (GY-521 class)   0x68 / 0x69, WHO_AM_I 0x75
//   LSM6DS3 / LSM6DS3TR-C / LSM6DSO          0x6A / 0x6B, WHO_AM_I 0x0F
//
// Both are configured for +-16 g at ~100 Hz and polled (no interrupt line
// needed; kImuInt in pins.h is optional). Only the accelerometer is read at
// Mk0.5: stillness, impacts and the activity index (dsp/motion.h) need
// nothing else, and the gyro would double the bus load.
//
// Conforms to the Sensor duck-typed concept (drivers/sensor.h). Health:
// kNoAck when a read fails (the supervisor re-begins on the backoff
// schedule), kOk otherwise; clipping is counted for the self-test line.

#pragma once

#include <Arduino.h>
#include <Wire.h>
#include <stdint.h>

#include "drivers/sensor.h"
#include "drivers/smoke_result.h"

namespace helmkit::drivers {

struct ImuSample {
    uint32_t t_ms;
    float    ax, ay, az;     // g
};

using ImuCallback = void (*)(const ImuSample&);

struct ImuConfig {
    uint32_t period_ms = 10;   // ~100 Hz poll; the chips sample at 100 / 104 Hz
};

class Imu {
 public:
    enum class Chip : uint8_t { kNone = 0, kMpu6050, kLsm6ds3 };

    bool     begin(TwoWire& bus, const ImuConfig& cfg = {});
    uint8_t  pump(ImuCallback cb);
    Health   health() const { return health_; }
    Chip     chip()   const { return chip_; }
    uint8_t  addr()   const { return addr_; }
    const char* chip_name() const;
    uint32_t total_samples() const { return total_; }
    uint32_t read_errors()   const { return errors_; }
    static constexpr const char* name() { return "imu"; }

    // Boot self-test (Track N, N-S1 family): 50 samples at rest must average
    // 1 g +- 10 %. Evidence: mean |a| in milli-g, read errors.
    SmokeResult self_test();

 private:
    bool write_reg(uint8_t reg, uint8_t val);
    bool read_regs(uint8_t reg, uint8_t* buf, uint8_t n);
    bool probe(uint8_t addr, uint8_t who_reg, const uint8_t* ids, uint8_t n_ids, uint8_t* id_out);

    TwoWire*  bus_    = nullptr;
    ImuConfig cfg_{};
    Chip      chip_   = Chip::kNone;
    uint8_t   addr_   = 0;
    uint8_t   who_    = 0;
    float     lsb_per_g_ = 2048.0f;
    uint32_t  last_ms_ = 0;
    uint32_t  total_  = 0;
    uint32_t  errors_ = 0;
    Health    health_ = Health::kUninit;
};

}  // namespace helmkit::drivers
