// HelmKit Mk0.5 — board pin map.
//
// Canonical source: firmware/mk0.5/docs/PINOUT.md
// If this header disagrees with PINOUT.md, PINOUT.md wins. Fix the header.
//
// All pin numbers are ESP32-S3 GPIO numbers (not header positions).

#pragma once

#include <Arduino.h>

namespace helmkit::pins {

// ---- Internal (board-reserved) -------------------------------------------
inline constexpr uint8_t kOledSda      = 17;
inline constexpr uint8_t kOledScl      = 18;
inline constexpr uint8_t kOledRst      = 21;
inline constexpr uint8_t kVextCtrl     = 36;  // active LOW
inline constexpr uint8_t kAdcCtrl      = 37;  // active LOW; enables VBAT divider
inline constexpr uint8_t kVbatAdc      = 1;   // ADC1_CH0

// ---- External I2C bus (Wire1) --------------------------------------------
inline constexpr uint8_t kExtI2cSda    = 41;
inline constexpr uint8_t kExtI2cScl    = 42;
inline constexpr uint32_t kExtI2cHz    = 400000;

// ---- Per-sensor pins ------------------------------------------------------
inline constexpr uint8_t kMax30102Int  = 38;  // active LOW, FIFO almost-full
inline constexpr uint8_t kMlx90614Alarm = 39; // optional, pull-up
inline constexpr uint8_t kGsrAdc       = 4;   // ADC1_CH3 — see PINOUT §3
inline constexpr uint8_t kAd8232Out    = 5;   // ADC1_CH4 — Wave 2
inline constexpr uint8_t kAd8232LoPlus = 6;
inline constexpr uint8_t kAd8232LoMinus= 7;
inline constexpr uint8_t kStatusLed    = 35;

// ---- Planned (Track N, not wired yet) -------------------------------------
// Nape pod buttons and the IMU interrupt. Chosen off the ESP32-S3 strapping
// pins (0, 3, 45, 46): a pulled-up button on GPIO 45 would select 1.8 V for
// VDD_SPI at reset. See PINOUT.md §2 (planned rows) and Track N N-U1 / N-S4.
inline constexpr uint8_t kBtnRound     = 26;  // tact: short = round start / end
inline constexpr uint8_t kBtnPrime     = 33;  // tact: short = prime, long = session start / end
inline constexpr uint8_t kBtnTally     = 34;  // tact (large cap): intrusion tally
inline constexpr uint8_t kSlideSanct   = 40;  // slide: sanctuary on / off
inline constexpr uint8_t kImuInt       = 47;  // IMU INT1 (high-g / data ready), optional

// ---- Reserved for Mk1.0+ --------------------------------------------------
// GPIO 45 / 46 are strapping pins: keep them for a dual-MCU UART or the stim
// interlock, never for anything pulled up at reset.
inline constexpr uint8_t kReservedA    = 45;
inline constexpr uint8_t kReservedB    = 46;

}  // namespace helmkit::pins
