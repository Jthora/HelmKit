// HelmKit Mk0.5 — MLX90614 driver implementation (Wave J Bridge B).
//
// See mlx90614.h for the public API + design notes. This translation unit
// hides Adafruit_MLX90614 from the rest of the firmware via a type-erased
// void* — same discipline as max30102.cpp.

#include "drivers/mlx90614.h"

#include <new>                     // std::nothrow
#include <Adafruit_MLX90614.h>

#include "board/pins.h"
#include "drivers/smoke_fail.h"

namespace helmkit::drivers {

namespace {
constexpr uint8_t kI2cAddr = 0x5A;   // MLX90614 default; not configurable
                                     // without permanent EEPROM write.

// SCHEMA §4: object range gate.
inline bool in_range(float obj_c) {
    return obj_c > 15.0f && obj_c < 45.0f;
}
}  // namespace

Mlx90614::~Mlx90614() {
    if (impl_) {
        delete static_cast<Adafruit_MLX90614*>(impl_);
        impl_ = nullptr;
    }
}

bool Mlx90614::begin(TwoWire& bus, const Mlx90614Config& cfg) {
    cfg_ = cfg;
    // Floor enforcement (see header comment).
    if (cfg_.period_ms < 100) cfg_.period_ms = 100;

    // Wave-I-style cleanup on re-begin so a smoke retry doesn't leak.
    if (impl_) {
        delete static_cast<Adafruit_MLX90614*>(impl_);
        impl_ = nullptr;
    }

    auto* dev = new (std::nothrow) Adafruit_MLX90614();
    if (!dev) {
        health_ = Health::kNoAck;     // closest pre-existing terminal state;
                                      // smoke_test maps to kHeapExhausted.
        return false;
    }
    impl_ = dev;

    if (!dev->begin(kI2cAddr, &bus)) {
        delete dev;
        impl_ = nullptr;
        health_ = Health::kNoAck;
        return false;
    }

    last_emit_ = 0;
    health_ = Health::kOk;
    return true;
}

uint8_t Mlx90614::pump(Mlx90614Callback cb) {
    if (!impl_) return 0;
    const uint32_t now = millis();
    if (now - last_emit_ < cfg_.period_ms) return 0;
    last_emit_ = now;

    auto* dev = static_cast<Adafruit_MLX90614*>(impl_);

    // Adafruit returns NAN on SMBus failure. Treat NAN as a no-ACK transient
    // — health flips, but we do not invoke the callback with a poisoned
    // value. The streaming consumer will see the gap in t_ms cadence;
    // emit_temp_forehead handles the q field at the wire layer.
    const float amb = dev->readAmbientTempC();
    const float obj = dev->readObjectTempC();
    if (isnan(amb) || isnan(obj)) {
        // Sticky-precedence rules in sensor.h: kNoAck only cleared by begin().
        health_ = Health::kNoAck;
        return 0;
    }

    Mlx90614Sample s{};
    s.t_ms       = now;
    s.ambient_c  = amb;
    s.object_c   = obj;
    s.in_range   = in_range(obj);

    if (health_ != Health::kNoAck &&
        health_ != Health::kError) {
        health_ = s.in_range ? Health::kOk : Health::kOutOfRange;
    }

    if (cb) cb(s);
    return 1;
}

// ---- Smoke test -----------------------------------------------------------

namespace {
struct SmokeAccum {
    uint32_t count       = 0;
    float    obj_min_c   = 1000.0f;
    float    obj_max_c   = -1000.0f;
    float    amb_last_c  = 0.0f;
};
SmokeAccum g_smoke;

void on_sample(const Mlx90614Sample& s) {
    ++g_smoke.count;
    if (s.object_c  < g_smoke.obj_min_c)  g_smoke.obj_min_c  = s.object_c;
    if (s.object_c  > g_smoke.obj_max_c)  g_smoke.obj_max_c  = s.object_c;
    g_smoke.amb_last_c = s.ambient_c;
}
}  // namespace

SmokeResult mlx90614_smoke_test() {
    Serial.println(F("[smoke] MLX90614 start"));
    // Wire1 is initialised by max30102_smoke_test() ahead of us; harmless
    // to call begin() again — second call is a no-op on the ESP32 driver.
    Wire1.begin(pins::kExtI2cSda, pins::kExtI2cScl, pins::kExtI2cHz);

    Mlx90614 dev;
    Mlx90614Config cfg;
    cfg.period_ms = 250;            // SCHEMA §2.2 = 4 Hz
    if (!dev.begin(Wire1, cfg)) {
        Serial.println(F("[smoke] FAIL: MLX90614 no ACK on Wire1@0x5A"));
        return SmokeResult::fail(SmokeFail::kNoAck,
                                 "MLX90614 no ACK on Wire1@0x5A",
                                 0, 0, dev.health());
    }
    Serial.println(F("[smoke] MLX90614 begin OK"));

    // CALIBRATION: 5-second window @ 4 Hz target = expect >=18 samples
    // (allowing for 1-tick miss). G2 + Bridge B gate.
    g_smoke = {};
    const uint32_t t_start    = millis();
    const uint32_t t_end      = t_start + 5000;
    uint32_t last_sample_ms   = t_start;
    uint32_t last_count       = 0;

    while (millis() < t_end) {
        dev.pump(on_sample);
        if (g_smoke.count != last_count) {
            last_count = g_smoke.count;
            last_sample_ms = millis();
        } else if (millis() - last_sample_ms > 2000) {
            Serial.println(F("[smoke] FAIL: MLX90614 SMBus stalled (no sample in 2s)"));
            return SmokeResult::fail(SmokeFail::kI2cStalled,
                                     "MLX90614 no sample in 2s",
                                     g_smoke.count, 0, dev.health());
        }
        delay(10);
    }

    Serial.printf("[smoke] MLX90614 RESULT: n=%lu obj=[%.2f..%.2f] amb=%.2f\n",
                  (unsigned long)g_smoke.count,
                  (double)g_smoke.obj_min_c,
                  (double)g_smoke.obj_max_c,
                  (double)g_smoke.amb_last_c);

    const bool rate_ok    = g_smoke.count >= 18;
    const bool amb_plaus  = g_smoke.amb_last_c > 0.0f && g_smoke.amb_last_c < 50.0f;

    if (!rate_ok) {
        return SmokeResult::fail(SmokeFail::kLowSampleRate,
                                 "MLX90614 <18 samples in 5s (target 20 @ 4 Hz)",
                                 g_smoke.count, 0, dev.health());
    }
    if (!amb_plaus) {
        return SmokeResult::fail(SmokeFail::kOutOfRange,
                                 "MLX90614 ambient implausible (expected 0..50C)",
                                 g_smoke.count,
                                 (uint32_t)g_smoke.amb_last_c,
                                 dev.health());
    }
    return SmokeResult::pass(g_smoke.count, 0, dev.health());
}

}  // namespace helmkit::drivers
