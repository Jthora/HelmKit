// HelmKit Mk0.5 — I²C bus recovery (Track N, N-F4).
//
// A slave that was mid-byte when the master lost sync holds SDA low forever
// and every address on the bus stops answering. The standard cure is nine
// clock pulses on SCL (the slave finishes its byte and releases SDA), a STOP,
// and a fresh master init. The stream supervisor in main.cpp calls this
// before a re-begin when the bus looks stuck; nothing else touches it.

#pragma once

#include <Wire.h>
#include <stdint.h>

namespace helmkit::board {

// True when SDA reads low with the bus idle: a device is holding it.
bool i2c_bus_stuck(uint8_t sda);

// End the driver, clock SCL until SDA is released (at most 9 pulses),
// generate a STOP, restart the driver. Returns true if SDA was released.
bool i2c_bus_recover(TwoWire& bus, uint8_t sda, uint8_t scl, uint32_t hz);

}  // namespace helmkit::board
