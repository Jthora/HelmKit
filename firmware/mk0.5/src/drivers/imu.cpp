// HelmKit Mk0.5 — IMU driver implementation. See imu.h.

#include "drivers/imu.h"

#include <math.h>

#include "board/watchdog.h"
#include "drivers/smoke_fail.h"

namespace helmkit::drivers {

namespace {
// MPU-6050 family
constexpr uint8_t kMpuWhoAmI     = 0x75;
constexpr uint8_t kMpuPwrMgmt1   = 0x6B;
constexpr uint8_t kMpuSmplrtDiv  = 0x19;
constexpr uint8_t kMpuConfig     = 0x1A;
constexpr uint8_t kMpuAccelCfg   = 0x1C;
constexpr uint8_t kMpuAccelOut   = 0x3B;
constexpr uint8_t kMpuIds[]      = {0x68, 0x70, 0x71, 0x73, 0x74};   // 6050, 6500, 9250, 9255, 6515
// LSM6DS3 family
constexpr uint8_t kLsmWhoAmI     = 0x0F;
constexpr uint8_t kLsmCtrl1Xl    = 0x10;
constexpr uint8_t kLsmCtrl3C     = 0x12;
constexpr uint8_t kLsmOutXlXl    = 0x28;
constexpr uint8_t kLsmIds[]      = {0x69, 0x6A, 0x6C};               // DS3, DS3TR-C, DSO
}  // namespace

bool Imu::write_reg(uint8_t reg, uint8_t val) {
    bus_->beginTransmission(addr_);
    bus_->write(reg);
    bus_->write(val);
    return bus_->endTransmission() == 0;
}

bool Imu::read_regs(uint8_t reg, uint8_t* buf, uint8_t n) {
    bus_->beginTransmission(addr_);
    bus_->write(reg);
    if (bus_->endTransmission(false) != 0) return false;
    if (bus_->requestFrom((int)addr_, (int)n) != n) return false;
    for (uint8_t i = 0; i < n; ++i) buf[i] = (uint8_t)bus_->read();
    return true;
}

bool Imu::probe(uint8_t addr, uint8_t who_reg, const uint8_t* ids, uint8_t n_ids, uint8_t* id_out) {
    addr_ = addr;
    uint8_t who = 0;
    if (!read_regs(who_reg, &who, 1)) return false;
    for (uint8_t i = 0; i < n_ids; ++i) {
        if (who == ids[i]) { *id_out = who; return true; }
    }
    return false;
}

bool Imu::begin(TwoWire& bus, const ImuConfig& cfg) {
    bus_ = &bus;
    cfg_ = cfg;
    chip_ = Chip::kNone;
    for (uint8_t a : {(uint8_t)0x68, (uint8_t)0x69}) {
        if (probe(a, kMpuWhoAmI, kMpuIds, sizeof kMpuIds, &who_)) { chip_ = Chip::kMpu6050; break; }
    }
    if (chip_ == Chip::kNone) {
        for (uint8_t a : {(uint8_t)0x6A, (uint8_t)0x6B}) {
            if (probe(a, kLsmWhoAmI, kLsmIds, sizeof kLsmIds, &who_)) { chip_ = Chip::kLsm6ds3; break; }
        }
    }
    if (chip_ == Chip::kNone) { addr_ = 0; health_ = Health::kNoAck; return false; }

    bool ok = true;
    if (chip_ == Chip::kMpu6050) {
        ok &= write_reg(kMpuPwrMgmt1, 0x01);    // wake, PLL on the X gyro
        ok &= write_reg(kMpuConfig, 0x03);      // DLPF 44 Hz -> 1 kHz internal rate
        ok &= write_reg(kMpuSmplrtDiv, 9);      // 1 kHz / (1 + 9) = 100 Hz
        ok &= write_reg(kMpuAccelCfg, 0x18);    // +-16 g
        lsb_per_g_ = 2048.0f;
    } else {
        ok &= write_reg(kLsmCtrl3C, 0x44);      // BDU + register auto-increment
        ok &= write_reg(kLsmCtrl1Xl, 0x44);     // ODR 104 Hz, +-16 g
        lsb_per_g_ = 1.0f / 0.000488f;          // 0.488 mg / LSB
    }
    if (!ok) { health_ = Health::kNoAck; return false; }
    last_ms_ = 0;
    health_ = Health::kOk;
    return true;
}

const char* Imu::chip_name() const {
    switch (chip_) {
        case Chip::kMpu6050: return "mpu6050";
        case Chip::kLsm6ds3: return "lsm6ds3";
        default:             return "none";
    }
}

uint8_t Imu::pump(ImuCallback cb) {
    if (chip_ == Chip::kNone || bus_ == nullptr) return 0;
    const uint32_t now = millis();
    if (now - last_ms_ < cfg_.period_ms) return 0;
    last_ms_ = now;
    uint8_t b[6];
    int16_t x, y, z;
    if (chip_ == Chip::kMpu6050) {
        if (!read_regs(kMpuAccelOut, b, 6)) { ++errors_; health_ = Health::kNoAck; return 0; }
        x = (int16_t)((b[0] << 8) | b[1]); y = (int16_t)((b[2] << 8) | b[3]); z = (int16_t)((b[4] << 8) | b[5]);
    } else {
        if (!read_regs(kLsmOutXlXl, b, 6)) { ++errors_; health_ = Health::kNoAck; return 0; }
        x = (int16_t)(b[0] | (b[1] << 8)); y = (int16_t)(b[2] | (b[3] << 8)); z = (int16_t)(b[4] | (b[5] << 8));
    }
    if (health_ != Health::kNoAck && health_ != Health::kError) health_ = Health::kOk;
    ImuSample s{};
    s.t_ms = now;
    s.ax = (float)x / lsb_per_g_;
    s.ay = (float)y / lsb_per_g_;
    s.az = (float)z / lsb_per_g_;
    ++total_;
    if (cb) cb(s);
    return 1;
}

SmokeResult Imu::self_test() {
    if (chip_ == Chip::kNone) {
        return SmokeResult::fail(SmokeFail::kNoAck, "imu: no chip on 0x68/0x69/0x6A/0x6B", 0, 0, health_);
    }
    float sum = 0.0f;
    uint32_t n = 0;
    const uint32_t t_end = millis() + 800;
    const uint32_t err0 = errors_;
    while (millis() < t_end && n < 50) {
        board::wdt_feed();
        uint8_t b[6];
        const uint8_t reg = (chip_ == Chip::kMpu6050) ? kMpuAccelOut : kLsmOutXlXl;
        if (read_regs(reg, b, 6)) {
            int16_t x, y, z;
            if (chip_ == Chip::kMpu6050) {
                x = (int16_t)((b[0] << 8) | b[1]); y = (int16_t)((b[2] << 8) | b[3]); z = (int16_t)((b[4] << 8) | b[5]);
            } else {
                x = (int16_t)(b[0] | (b[1] << 8)); y = (int16_t)(b[2] | (b[3] << 8)); z = (int16_t)(b[4] | (b[5] << 8));
            }
            const float ax = x / lsb_per_g_, ay = y / lsb_per_g_, az = z / lsb_per_g_;
            sum += sqrtf(ax * ax + ay * ay + az * az);
            ++n;
        } else {
            ++errors_;
        }
        delay(10);
    }
    const float mean_g = n ? sum / (float)n : 0.0f;
    const uint32_t mg = (uint32_t)(mean_g * 1000.0f);
    if (n < 40) {
        return SmokeResult::fail(SmokeFail::kLowSampleRate, "imu: fewer than 40 of 50 reads answered", n, errors_ - err0, health_);
    }
    if (mean_g < 0.9f || mean_g > 1.1f) {
        return SmokeResult::fail(SmokeFail::kOutOfRange, "imu: |a| at rest not within 1 g +- 10 % (moving, or wrong scale)", mg, n, health_);
    }
    return SmokeResult::pass(mg, n, health_);
}

}  // namespace helmkit::drivers
