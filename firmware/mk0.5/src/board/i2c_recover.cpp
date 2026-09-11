// HelmKit Mk0.5 — I²C bus recovery implementation. See i2c_recover.h.

#include "board/i2c_recover.h"

#include <Arduino.h>
#include <driver/gpio.h>

namespace helmkit::board {

bool i2c_bus_stuck(uint8_t sda) {
    // The pad's input path stays enabled while the I²C peripheral owns the
    // pin, so the level can be read without reconfiguring anything.
    return gpio_get_level((gpio_num_t)sda) == 0;
}

bool i2c_bus_recover(TwoWire& bus, uint8_t sda, uint8_t scl, uint32_t hz) {
    bus.end();
    pinMode(scl, OUTPUT_OPEN_DRAIN);
    pinMode(sda, OUTPUT_OPEN_DRAIN);
    digitalWrite(scl, HIGH);
    digitalWrite(sda, HIGH);           // released: the slave may still hold it low
    delayMicroseconds(5);
    for (int i = 0; i < 9 && digitalRead(sda) == LOW; ++i) {
        digitalWrite(scl, LOW);
        delayMicroseconds(5);
        digitalWrite(scl, HIGH);
        delayMicroseconds(5);
    }
    // STOP: SDA low -> high while SCL is high.
    digitalWrite(sda, LOW);
    delayMicroseconds(5);
    digitalWrite(sda, HIGH);
    delayMicroseconds(5);
    const bool released = digitalRead(sda) == HIGH;
    bus.begin(sda, scl, hz);
    return released;
}

}  // namespace helmkit::board
