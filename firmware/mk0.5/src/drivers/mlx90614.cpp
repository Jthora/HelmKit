// HelmKit Mk0.5 — MLX90614 driver (Wave 1 skeleton).
// See mlx90614.h. Wave 2 will use Adafruit_MLX90614 against Wire1.

#include "drivers/mlx90614.h"
#include "board/pins.h"
#include <Wire.h>

namespace helmkit::drivers {

bool Mlx90614::begin() {
    Wire1.begin(pins::kExtI2cSda, pins::kExtI2cScl, pins::kExtI2cHz);
    // Probe 0x5A for ACK without pulling in Adafruit_MLX90614 in Wave 1.
    Wire1.beginTransmission(0x5A);
    const uint8_t err = Wire1.endTransmission();
    health_ = (err == 0) ? Health::kOk : Health::kNoAck;
    return err == 0;
}

void Mlx90614::pump() {
    // Wave 2: poll TA + TOBJ1 over SMBus and emit "temp-forehead" channel.
}

SmokeResult mlx90614_smoke_test() {
    Mlx90614 m;
    if (!m.begin()) {
        return SmokeResult::fail("no-ack-on-Wire1@0x5A", 0, 0);
    }
    return SmokeResult::fail("not-yet-implemented", 0, 0);
}

}  // namespace helmkit::drivers
