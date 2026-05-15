// HelmKit Mk0.5 — MAX30102 PPG driver implementation.
//
// See header for API doc. This translation unit hides the SparkFun library
// dependency from the rest of the firmware via a type-erased void*.

#include "drivers/max30102.h"

#include <MAX30105.h>   // SparkFun MAX3010x library, pinned 1.1.2

#include "board/pins.h"

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

    auto* sf = new MAX30105();
    impl_ = sf;

    // SparkFun's begin() probes the I2C address and returns false on no-ACK.
    if (!sf->begin(bus, I2C_SPEED_FAST, kI2cAddr)) {
        delete sf;
        impl_ = nullptr;
        return false;
    }

    const auto a = to_sf(cfg);
    sf->setup(a.powerLevel, a.sampleAverage, a.ledMode,
              a.sampleRate, a.pulseWidth, a.adcRange);

    // INT pin: input with pull-up (sensor drives low on FIFO-almost-full).
    pinMode(pins::kMax30102Int, INPUT_PULLUP);

    return true;
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
            break;
        }
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

bool max30102_smoke_test() {
    Serial.println(F("[smoke] MAX30102 start"));

    Wire1.begin(pins::kExtI2cSda, pins::kExtI2cScl, pins::kExtI2cHz);

    Max30102 dev;
    Max30102Config cfg;
    cfg.sample_rate_hz = 100;
    cfg.sample_avg = 4;

    if (!dev.begin(Wire1, cfg)) {
        Serial.println(F("[smoke] FAIL: MAX30102 no ACK on Wire1@0x57"));
        return false;
    }
    Serial.println(F("[smoke] MAX30102 begin OK"));

    const uint32_t t_start = millis();
    const uint32_t t_end = t_start + 10000;  // 10 s window
    g_smoke = {};

    while (millis() < t_end) {
        dev.pump(on_sample);
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

    const bool rate_ok    = g_smoke.count >= 950;
    const bool no_overflow = dev.fifo_overflows() == 0;

    Serial.printf("[smoke] MAX30102 RESULT: n=%lu rate_ok=%d overflow=%lu\n",
                  (unsigned long)g_smoke.count,
                  rate_ok ? 1 : 0,
                  (unsigned long)dev.fifo_overflows());

    return rate_ok && no_overflow;
}

}  // namespace helmkit::drivers
