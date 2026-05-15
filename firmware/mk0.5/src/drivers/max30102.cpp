// HelmKit Mk0.5 — MAX30102 PPG driver implementation.
//
// See header for API doc. This translation unit hides the SparkFun library
// dependency from the rest of the firmware via a type-erased void*.

#include "drivers/max30102.h"

#include <new>          // std::nothrow
#include <MAX30105.h>   // SparkFun MAX3010x library, pinned 1.1.2

#include "board/pins.h"
#include "drivers/smoke_fail.h"

namespace helmkit::drivers {

namespace {
constexpr uint8_t kI2cAddr = 0x57;   // MAX30102 fixed address

// Convert config struct into SparkFun setup() arguments.
struct SfArgs {
    byte powerLevel;
    byte sampleAverage;
    byte ledMode;
    int sampleRate;
    int pulseWidth;
    int adcRange;
};

SfArgs to_sf(const Max30102Config& c) {
    return SfArgs{
        c.led_brightness,
        c.sample_avg,
        c.led_mode,
        c.sample_rate_hz,
        c.pulse_width_us,
        c.adc_range,
    };
}
}  // namespace

bool Max30102::begin(TwoWire& bus, const Max30102Config& cfg) {
    cfg_ = cfg;

    // Wave I (R1): clean up prior instance on re-begin. Without this, every
    // call after the first leaks a MAX30105*.
    if (impl_) {
        delete static_cast<MAX30105*>(impl_);
        impl_ = nullptr;
    }

    // Wave I (R1): nothrow new on the embedded heap. Hard-fault on OOM is
    // worse than a clean kHeapExhausted in the SmokeResult.
    auto* sf = new (std::nothrow) MAX30105();
    if (!sf) {
        health_ = Health::kNoAck;  // closest pre-existing terminal state;
                                   // smoke test maps to kHeapExhausted
        return false;
    }
    impl_ = sf;

    // SparkFun's begin() probes the I2C address and returns false on no-ACK.
    if (!sf->begin(bus, I2C_SPEED_FAST, kI2cAddr)) {
        delete sf;
        impl_ = nullptr;
        health_ = Health::kNoAck;
        return false;
    }

    const auto a = to_sf(cfg);
    sf->setup(a.powerLevel, a.sampleAverage, a.ledMode,
              a.sampleRate, a.pulseWidth, a.adcRange);

    // INT pin: input with pull-up (sensor drives low on FIFO-almost-full).
    pinMode(pins::kMax30102Int, INPUT_PULLUP);

    health_ = Health::kOk;
    return true;
}

Max30102::~Max30102() {
    if (impl_) {
        delete static_cast<MAX30105*>(impl_);
        impl_ = nullptr;
    }
}

uint8_t Max30102::pump(Max30102Callback cb) {
    if (!impl_) return 0;
    auto* sf = static_cast<MAX30105*>(impl_);

    sf->check();
    uint8_t drained = 0;
    while (sf->available()) {
        Max30102Sample s{};
        s.t_ms = millis();
        s.red  = sf->getFIFORed();
        s.ir   = sf->getFIFOIR();
        s.finger_present = (s.ir > cfg_.finger_ir_threshold);

        finger_present_ = s.finger_present;
        ++total_samples_;
        if (cb) cb(s);

        sf->nextSample();
        ++drained;

        // Soft cap per pump() to avoid blocking the loop if the FIFO somehow
        // overflowed. The MAX30102 FIFO is 32 deep; >32 here implies wrap.
        if (drained >= 32) {
            ++fifo_overflows_;
            health_ = Health::kOverflow;
            break;
        }
    }
    // Update health: gap if no finger, else ok. Per Wave F precedence
    // rules in drivers/sensor.h, kNoAck/kOverflow/kError are sticky and
    // only begin() may clear them.
    if (health_ != Health::kOverflow &&
        health_ != Health::kNoAck    &&
        health_ != Health::kError) {
        health_ = finger_present_ ? Health::kOk : Health::kGap;
    }
    return drained;
}

void Max30102::shutdown() {
    if (!impl_) return;
    static_cast<MAX30105*>(impl_)->shutDown();
}

void Max30102::wake() {
    if (!impl_) return;
    static_cast<MAX30105*>(impl_)->wakeUp();
}

// ---- Smoke test -----------------------------------------------------------

namespace {
struct SmokeAccum {
    uint32_t count = 0;
    uint32_t last_print_ms = 0;
    uint32_t ir_max = 0;
    uint32_t ir_min = UINT32_MAX;
};

SmokeAccum g_smoke;

void on_sample(const Max30102Sample& s) {
    ++g_smoke.count;
    if (s.ir > g_smoke.ir_max) g_smoke.ir_max = s.ir;
    if (s.ir < g_smoke.ir_min) g_smoke.ir_min = s.ir;
}
}  // namespace

SmokeResult max30102_smoke_test() {
    Serial.println(F("[smoke] MAX30102 start"));

    Wire1.begin(pins::kExtI2cSda, pins::kExtI2cScl, pins::kExtI2cHz);

    Max30102 dev;
    Max30102Config cfg;
    // CALIBRATION: 100 Hz target tied to docs/SCHEMA.md §2.1 ppg-hrv rate.
    cfg.sample_rate_hz = 100;
    cfg.sample_avg = 4;

    if (!dev.begin(Wire1, cfg)) {
        Serial.println(F("[smoke] FAIL: MAX30102 no ACK on Wire1@0x57"));
        return SmokeResult::fail(SmokeFail::kNoAck,
                                 "MAX30102 no ACK on Wire1@0x57",
                                 0, 0, dev.health());
    }
    Serial.println(F("[smoke] MAX30102 begin OK"));

    const uint32_t t_start = millis();
    // CALIBRATION: 10-second smoke window. Tied to G1 gate.
    const uint32_t t_end = t_start + 10000;
    g_smoke = {};

    // Wave I addition (H4): stall watchdog. If pump() returns 0 samples for
    // >2s consecutive, the I2C bus or sensor has wedged; abort with a
    // structured code rather than wait the full 10s.
    uint32_t last_sample_at = t_start;
    uint32_t last_count = 0;

    while (millis() < t_end) {
        dev.pump(on_sample);
        if (g_smoke.count != last_count) {
            last_count = g_smoke.count;
            last_sample_at = millis();
        } else if (millis() - last_sample_at > 2000) {
            Serial.println(F("[smoke] FAIL: I2C stalled (no samples in 2s)"));
            return SmokeResult::fail(SmokeFail::kI2cStalled,
                                     "no samples in 2s",
                                     g_smoke.count,
                                     dev.fifo_overflows(),
                                     dev.health());
        }
        if (millis() - g_smoke.last_print_ms >= 1000) {
            g_smoke.last_print_ms = millis();
            Serial.printf("[smoke] t=%lus n=%lu ir_min=%lu ir_max=%lu finger=%d\n",
                          (g_smoke.last_print_ms - t_start) / 1000,
                          (unsigned long)g_smoke.count,
                          (unsigned long)g_smoke.ir_min,
                          (unsigned long)g_smoke.ir_max,
                          dev.finger_present() ? 1 : 0);
        }
    }

    // CALIBRATION: >= 950 samples in 10s @ 100 Hz target. Tied to G1 gate.
    const bool rate_ok    = g_smoke.count >= 950;
    const bool no_overflow = dev.fifo_overflows() == 0;

    Serial.printf("[smoke] MAX30102 RESULT: n=%lu rate_ok=%d overflow=%lu\n",
                  (unsigned long)g_smoke.count,
                  rate_ok ? 1 : 0,
                  (unsigned long)dev.fifo_overflows());

    if (!rate_ok) {
        return SmokeResult::fail(SmokeFail::kLowSampleRate,
                                 "sample-count below threshold (>=950 in 10s)",
                                 g_smoke.count, dev.fifo_overflows(),
                                 dev.health());
    }
    if (!no_overflow) {
        return SmokeResult::fail(SmokeFail::kFifoOverflow,
                                 "FIFO overflow during smoke window",
                                 g_smoke.count, dev.fifo_overflows(),
                                 dev.health());
    }
    return SmokeResult::pass(g_smoke.count, 0, dev.health());
}

}  // namespace helmkit::drivers
