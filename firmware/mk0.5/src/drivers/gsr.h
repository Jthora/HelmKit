// HelmKit Mk0.5 — CJMCU-6701 GSR analog driver.
// Channel: "gsr" (psiStabilizer v0.2-proposed; see docs/SCHEMA.md §2.2).
// Pin: ADC1_CH3 on GPIO 4. Shares ADC1 with battery.cpp via board/adc_mutex.
//
// Conforms to the Sensor duck-typed concept (see drivers/sensor.h).
// Wave J Bridge B (2026-05-18): pump() populated for 50 Hz streaming
// against the in-inventory CJMCU GSR breakout. Calibration to microsiemens
// is deferred (sensor lacks a published transfer fn; calibrate later from
// captured raw data against a known reference). Wire path = `gsr` channel
// raw uint16 0..4095 per SCHEMA §2.2.
#pragma once

#include <Arduino.h>

#include "drivers/sensor.h"
#include "drivers/smoke_result.h"

namespace helmkit::drivers {

struct GsrSample {
    uint32_t t_ms;
    uint16_t raw;       // 0..4095 (12-bit ADC)
    bool     in_range;  // true if 100 < raw < 4000 (SCHEMA §4)
};

struct GsrConfig {
    // Sample period in milliseconds. SCHEMA §2.2 declares 50 Hz → 20 ms.
    uint32_t period_ms = 20;
    // ADC1 mutex acquire timeout. Battery sampler holds the lock briefly;
    // 5 ms is a comfortable ceiling on a 50 Hz cadence (20 ms budget).
    uint32_t adc_timeout_ms = 5;
};

using GsrCallback = void (*)(const GsrSample&);

class Gsr {
public:
    bool begin(const GsrConfig& cfg = {});

    // Non-blocking. Emits at most one sample per call when period elapsed
    // AND the ADC1 mutex is acquired within adc_timeout_ms. Returns 1 if a
    // sample fired, 0 otherwise. mutex-timeout flips health → kError so
    // the operator sees the contention, but is not sticky — the next
    // successful read clears it.
    uint8_t pump(GsrCallback cb);

    static constexpr const char* name() { return "gsr"; }
    Health health() const { return health_; }

    // Counters for smoke-test introspection.
    uint32_t total_samples()   const { return total_samples_; }
    uint32_t mutex_timeouts()  const { return mutex_timeouts_; }

private:
    GsrConfig cfg_              = {};
    uint32_t  last_emit_        = 0;
    uint32_t  total_samples_    = 0;
    uint32_t  mutex_timeouts_   = 0;
    Health    health_           = Health::kUninit;
};

SmokeResult gsr_smoke_test();

}  // namespace helmkit::drivers
