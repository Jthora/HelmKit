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

#include "drivers/sensor.h"
#include "drivers/smoke_result.h"

namespace helmkit::drivers {

struct Max30102Sample {
    uint32_t t_ms;     // millis() at sample read
    uint32_t red;      // 18-bit raw, left-justified in uint32
    uint32_t ir;       // 18-bit raw
    bool finger_present;
};

using Max30102Callback = void (*)(const Max30102Sample&);

struct Max30102Config {
    // CALIBRATION: LED brightness. Tied to L0 smoke threshold. Do not modify
    // without re-running the G1 gate (mk0.5_firmware_bringup.md §1.1).
    uint8_t led_brightness   = 0x1F;  // ~6 mA, safe default
    // CALIBRATION: hardware averaging. Tied to effective sample rate.
    uint8_t sample_avg       = 4;
    uint8_t led_mode         = 2;     // 1=red, 2=red+IR, 3=red+IR+green
    // CALIBRATION: target sample rate. Schema docs/SCHEMA.md §2.1 declares
    // ppg-hrv at 100 Hz. Changing this requires a SCHEMA.md update.
    uint16_t sample_rate_hz  = 100;
    uint16_t pulse_width_us  = 411;   // wider = more resolution
    uint16_t adc_range       = 4096;
    // CALIBRATION: finger-present threshold. Empirical. Tied to the `q="gap"`
    // emission rule in docs/SCHEMA.md §4. Tuning this invalidates session
    // gap-fraction statistics. DO NOT modify without re-running G1.
    uint32_t finger_ir_threshold = 50000;
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

    // Last-known health, idempotent.
    Health health() const { return health_; }

    // Channel name per docs/SCHEMA.md §2.1.
    static constexpr const char* name() { return "ppg-hrv"; }

    // Diagnostic counters for smoke tests.
    uint32_t total_samples()  const { return total_samples_; }
    uint32_t fifo_overflows() const { return fifo_overflows_; }

private:
    void* impl_ = nullptr;   // type-erased SparkFun MAX30105 instance
    Max30102Config cfg_{};
    bool finger_present_  = false;
    Health health_  = Health::kUninit;
    uint32_t total_samples_  = 0;
    uint32_t fifo_overflows_ = 0;
};

// ---- Day 1 L0 smoke test --------------------------------------------------
//
// Prints sensor presence, sample rate, and 10 seconds of IR/red raw values
// to USB-CDC at 115200. Returns a SmokeResult with:
//   ok=true iff: chip ACKs, >= 950 samples in 10s @ 100 Hz, no FIFO overflows.
// On failure, `reason` identifies which precondition broke.
// `evidence_a` = sample count, `evidence_b` = overflow count.
//
// Used as the L0 gate criterion per docs/mk0.5_firmware_bringup.md §1.1.
//
// CALIBRATION: smoke window = 10s, pass threshold = 950 samples.
// Tied to G1 gate. DO NOT modify without re-running G1.
SmokeResult max30102_smoke_test();

}  // namespace helmkit::drivers
