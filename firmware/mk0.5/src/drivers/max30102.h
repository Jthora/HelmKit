// HelmKit Mk0.5 — MAX30102 PPG driver.
//
// Wraps the SparkFun MAX3010x library with a HelmKit-shaped API:
//   - non-blocking sample pump (`pump()` is called from the main loop)
//   - presence detection (returns false fast if no I2C ack)
//   - finger-detected heuristic (raw IR > threshold)
//   - timestamped sample stream via a callback
//
// Smoke test: see `max30102.cpp::smoke_test()`. Run with `pio test -e mk05_heltec_v3`
// or call from main during Day 1 bringup.
//
// Datasheet: MAX30102, Rev. 1; Maxim Integrated.
// SparkFun library API: SparkFun_MAX3010x v1.1.2 (pinned).

#pragma once

#include <Arduino.h>
#include <Wire.h>
#include <stdint.h>

namespace helmkit::drivers {

struct Max30102Sample {
    uint32_t t_ms;     // millis() at sample read
    uint32_t red;      // 18-bit raw, left-justified in uint32
    uint32_t ir;       // 18-bit raw
    bool finger_present;
};

using Max30102Callback = void (*)(const Max30102Sample&);

struct Max30102Config {
    uint8_t led_brightness   = 0x1F;  // 0..0xFF, ~6 mA at 0x1F (safe default)
    uint8_t sample_avg       = 4;     // 1,2,4,8,16,32 — hardware averaging
    uint8_t led_mode         = 2;     // 1=red only, 2=red+IR, 3=red+IR+green (no green on -102)
    uint16_t sample_rate_hz  = 100;   // 50,100,200,400,800,1000,1600,3200
    uint16_t pulse_width_us  = 411;   // 69,118,215,411 — wider = more resolution
    uint16_t adc_range       = 4096;  // 2048,4096,8192,16384
    uint32_t finger_ir_threshold = 50000;  // raw IR; empirical, validate at smoke test
};

class Max30102 {
public:
    // Initializes the sensor on the given TwoWire instance (default: Wire1
    // for HelmKit's external I2C bus). Returns false if the chip does not
    // ACK on the I2C address (0x57) — caller MUST check this.
    bool begin(TwoWire& bus, const Max30102Config& cfg);

    // Pumps the internal FIFO. Call from the main loop at >= sample_rate_hz
    // (recommended: every loop iteration). Invokes `cb` once per new sample.
    // Returns the number of samples drained on this call (0 if FIFO empty).
    uint8_t pump(Max30102Callback cb);

    // Software shutdown. Idle current after shutdown is ~0.7 µA.
    void shutdown();

    // Wake from shutdown. Sensor needs ~10 ms to start acquiring.
    void wake();

    // Returns true if the most recent sample's IR raw exceeds the
    // finger-detection threshold. Cached from the last `pump()`.
    bool finger_present() const { return finger_present_; }

    // Diagnostic counters for smoke tests.
    uint32_t total_samples()  const { return total_samples_; }
    uint32_t fifo_overflows() const { return fifo_overflows_; }

private:
    void* impl_ = nullptr;   // type-erased SparkFun MAX30105 instance
    Max30102Config cfg_{};
    bool finger_present_  = false;
    uint32_t total_samples_  = 0;
    uint32_t fifo_overflows_ = 0;
};

// ---- Day 1 L0 smoke test --------------------------------------------------
//
// Prints sensor presence, sample rate, and 10 seconds of IR/red raw values
// to USB-CDC at 115200. Returns true if:
//   - chip ACKs on the bus,
//   - >= 950 samples observed in 10 s @ 100 Hz target,
//   - no FIFO overflows.
//
// Used as the L0 gate criterion for MAX30102 per
// `docs/mk0.5_firmware_bringup.md`.
bool max30102_smoke_test();

}  // namespace helmkit::drivers
