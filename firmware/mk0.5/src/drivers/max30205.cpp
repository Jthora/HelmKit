// HelmKit Mk0.5 — MAX30205 implementation. See max30205.h.

#include "drivers/max30205.h"

#include "board/pins.h"
#include "drivers/smoke_fail.h"

namespace helmkit::drivers {

namespace {
constexpr uint8_t kRegTemp   = 0x00;
constexpr uint8_t kRegConfig = 0x01;
inline bool in_range(float c) { return c > 30.0f && c < 42.0f; }
}  // namespace

bool Max30205::begin(TwoWire& bus, const Max30205Config& cfg) {
    bus_ = &bus;
    cfg_ = cfg;
    if (cfg_.period_ms < 100) cfg_.period_ms = 100;
    const uint8_t addrs[2] = {kAddrL, kAddrR};
    for (uint8_t i = 0; i < 2; ++i) {
        bus_->beginTransmission(addrs[i]);
        bus_->write(kRegConfig);
        bus_->write((uint8_t)0x00);              // continuous conversion, comparator mode defaults
        present_[i] = (bus_->endTransmission() == 0);
    }
    last_ms_ = 0;
    if (!present_[0] && !present_[1]) { health_ = Health::kNoAck; return false; }
    health_ = Health::kOk;
    return true;
}

bool Max30205::read_temp(uint8_t addr, float* c) {
    bus_->beginTransmission(addr);
    bus_->write(kRegTemp);
    if (bus_->endTransmission(false) != 0) return false;
    if (bus_->requestFrom((int)addr, 2) != 2) return false;
    const uint8_t hi = (uint8_t)bus_->read();
    const uint8_t lo = (uint8_t)bus_->read();
    const int16_t raw = (int16_t)((hi << 8) | lo);
    *c = (float)raw / 256.0f;
    return true;
}

uint8_t Max30205::pump(Max30205Callback cb) {
    if (bus_ == nullptr || (!present_[0] && !present_[1])) return 0;
    const uint32_t now = millis();
    if (now - last_ms_ < cfg_.period_ms) return 0;
    last_ms_ = now;
    uint8_t n = 0;
    bool any_fail = false, any_bad = false;
    const uint8_t addrs[2] = {kAddrL, kAddrR};
    for (uint8_t i = 0; i < 2; ++i) {
        if (!present_[i]) continue;
        float c = 0.0f;
        if (!read_temp(addrs[i], &c)) { any_fail = true; continue; }
        Max30205Sample s{};
        s.t_ms = now; s.temp_c = c; s.addr = addrs[i]; s.in_range = in_range(c);
        if (!s.in_range) any_bad = true;
        if (cb) cb(s);
        ++n;
    }
    if (any_fail) health_ = Health::kNoAck;                      // sticky: the supervisor re-begins
    else if (health_ != Health::kNoAck && health_ != Health::kError) health_ = any_bad ? Health::kOutOfRange : Health::kOk;
    return n;
}

SmokeResult max30205_smoke_test() {
    Wire1.begin(pins::kExtI2cSda, pins::kExtI2cScl, pins::kExtI2cHz);
    Max30205 dev;
    if (!dev.begin(Wire1)) {
        return SmokeResult::fail(SmokeFail::kNoAck, "MAX30205: no ACK on 0x48 or 0x49", 0, 0, dev.health());
    }
    delay(60);                                                    // one conversion (~50 ms)
    float c = 0.0f;
    uint32_t n = 0, sum_mc = 0;
    for (uint8_t i = 0; i < 2; ++i) {
        if (!dev.present(i)) continue;
        if (dev.read_temp(i == 0 ? Max30205::kAddrL : Max30205::kAddrR, &c)) { ++n; sum_mc += (uint32_t)(c * 1000.0f); }
    }
    if (n == 0) return SmokeResult::fail(SmokeFail::kI2cStalled, "MAX30205: no reading", 0, 0, dev.health());
    const uint32_t mean_mc = sum_mc / n;
    if (mean_mc < 15000 || mean_mc > 45000) {
        return SmokeResult::fail(SmokeFail::kOutOfRange, "MAX30205: reading outside 15..45 C", dev.devices(), mean_mc, dev.health());
    }
    return SmokeResult::pass(dev.devices(), mean_mc, dev.health());
}

}  // namespace helmkit::drivers
