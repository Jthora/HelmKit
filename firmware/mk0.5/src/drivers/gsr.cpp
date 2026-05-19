// HelmKit Mk0.5 — GSR driver implementation (Wave J Bridge B).
// See gsr.h. ADC1 mutex discipline is mandatory; see board/adc_mutex.h.

#include "drivers/gsr.h"

#include "board/adc_mutex.h"
#include "board/pins.h"
#include "drivers/smoke_fail.h"

namespace helmkit::drivers {

namespace {
// SCHEMA §4 quality gate.
inline bool in_range(uint16_t raw) {
    return raw > 100 && raw < 4000;
}
}  // namespace

bool Gsr::begin(const GsrConfig& cfg) {
    cfg_ = cfg;
    // CALIBRATION: 12-bit ADC; ADC_11db on ESP32-S3 → 0..~3.1 V input range.
    // Tied to PINOUT.md §3.
    analogReadResolution(12);
    analogSetPinAttenuation(pins::kGsrAdc, ADC_11db);
    last_emit_      = 0;
    total_samples_  = 0;
    mutex_timeouts_ = 0;
    health_         = Health::kOk;
    return true;
}

uint8_t Gsr::pump(GsrCallback cb) {
    if (health_ == Health::kUninit) return 0;
    const uint32_t now = millis();
    if (now - last_emit_ < cfg_.period_ms) return 0;

    uint16_t raw = 0;
    const bool got_lock = helmkit::board::with_adc1_lock(cfg_.adc_timeout_ms,
        [&] { raw = analogRead(pins::kGsrAdc); });
    if (!got_lock) {
        ++mutex_timeouts_;
        health_ = Health::kError;
        // Do NOT advance last_emit_ — retry next tick. The 20 ms cadence
        // is forgiving enough that a single timeout doesn't desync the
        // sample stream.
        return 0;
    }

    last_emit_ = now;
    ++total_samples_;

    GsrSample s{};
    s.t_ms     = now;
    s.raw      = raw;
    s.in_range = in_range(raw);

    // Sticky precedence: only begin() clears kNoAck/kOverflow/kError on
    // the other sensors; for GSR we have no sticky failure modes besides
    // mutex contention (handled above), so refresh on every good sample.
    health_ = s.in_range ? Health::kOk : Health::kOutOfRange;

    if (cb) cb(s);
    return 1;
}

// ---- Smoke test -----------------------------------------------------------

namespace {
struct SmokeAccum {
    uint32_t count   = 0;
    uint16_t raw_min = 0xFFFF;
    uint16_t raw_max = 0;
    uint32_t raw_sum = 0;
};
SmokeAccum g_smoke;

void on_sample(const GsrSample& s) {
    ++g_smoke.count;
    if (s.raw < g_smoke.raw_min) g_smoke.raw_min = s.raw;
    if (s.raw > g_smoke.raw_max) g_smoke.raw_max = s.raw;
    g_smoke.raw_sum += s.raw;
}
}  // namespace

SmokeResult gsr_smoke_test() {
    Serial.println(F("[smoke] GSR start"));

    Gsr dev;
    GsrConfig cfg;
    cfg.period_ms      = 20;     // SCHEMA §2.2 = 50 Hz
    cfg.adc_timeout_ms = 5;
    if (!dev.begin(cfg)) {
        return SmokeResult::fail(SmokeFail::kBeginFailed,
                                 "gsr begin failed", 0, 0, dev.health());
    }

    // CALIBRATION: 3-second window @ 50 Hz target = expect >=140 samples
    // (allowing for ~5% mutex-contention slop). Bridge B gate.
    g_smoke = {};
    const uint32_t t_start = millis();
    const uint32_t t_end   = t_start + 3000;
    while (millis() < t_end) {
        dev.pump(on_sample);
        delay(2);
    }

    const uint32_t mean = g_smoke.count ? (g_smoke.raw_sum / g_smoke.count) : 0;
    Serial.printf("[smoke] GSR RESULT: n=%lu raw=[%u..%u] mean=%lu "
                  "mutex_timeouts=%lu\n",
                  (unsigned long)g_smoke.count,
                  (unsigned)g_smoke.raw_min,
                  (unsigned)g_smoke.raw_max,
                  (unsigned long)mean,
                  (unsigned long)dev.mutex_timeouts());

    if (g_smoke.count < 140) {
        return SmokeResult::fail(SmokeFail::kLowSampleRate,
                                 "gsr <140 samples in 3s (target 150 @ 50 Hz)",
                                 g_smoke.count, dev.mutex_timeouts(),
                                 dev.health());
    }
    if (dev.mutex_timeouts() > 8) {
        // >5% timeouts in a 3-second window is contention-pathological;
        // surface it rather than hide it.
        return SmokeResult::fail(SmokeFail::kMutexTimeout,
                                 "gsr: ADC1 mutex contention >5%",
                                 g_smoke.count, dev.mutex_timeouts(),
                                 dev.health());
    }
    // Plausibility: with electrodes open or shorted to ground the raw value
    // pegs near a rail. A genuine open-bench reading (no skin) should still
    // sit in the mid-band on the CJMCU breakout because of its internal
    // pull-up network. We only flag the obvious-stuck case.
    if (g_smoke.raw_max == g_smoke.raw_min) {
        return SmokeResult::fail(SmokeFail::kOutOfRange,
                                 "gsr raw stuck (no variance over 3s)",
                                 g_smoke.count, mean, dev.health());
    }
    return SmokeResult::pass(g_smoke.count, dev.mutex_timeouts(), dev.health());
}

}  // namespace helmkit::drivers
