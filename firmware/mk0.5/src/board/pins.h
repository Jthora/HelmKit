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

// ---- Reserved for Mk1.0+ --------------------------------------------------
inline constexpr uint8_t kReservedA    = 45;
inline constexpr uint8_t kReservedB    = 46;

}  // namespace helmkit::pins
