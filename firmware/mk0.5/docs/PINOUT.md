# Mk0.5 PINOUT — Heltec WiFi LoRa 32 V3 (HTIT-WB32LAF)

**Status:** DRAFT — pin assignments below are committed to silicon allocation
at the firmware level but await physical bench verification with multimeter
on Day 1 afternoon (Wave 1 arrival).

**Board:** ESP32-S3FN8 on Heltec V3. Verified by silkscreen as
`HTIT-WB32LAF`. Datasheet ref: Heltec Automation "WiFi LoRa 32 V3"
schematic rev. 2.1.

---

## 1. Reserved by board (do not touch)

| Pin (GPIO) | Function                                | Notes |
|------------|-----------------------------------------|-------|
| GPIO 0     | BOOT button / strap                     | Pull low to enter download mode. |
| GPIO 8     | LoRa SX1262 NSS                         | Not used at Mk0.5 but reserved. |
| GPIO 9     | LoRa SX1262 SCK                         | Not used at Mk0.5. |
| GPIO 10    | LoRa SX1262 MOSI                        | Not used at Mk0.5. |
| GPIO 11    | LoRa SX1262 MISO                        | Not used at Mk0.5. |
| GPIO 12    | LoRa SX1262 RST                         | Not used at Mk0.5. |
| GPIO 13    | LoRa SX1262 BUSY                        | Not used at Mk0.5. |
| GPIO 14    | LoRa SX1262 DIO1                        | Not used at Mk0.5. |
| GPIO 17    | OLED SDA (internal I2C bus 0)           | SSD1306 0.96". |
| GPIO 18    | OLED SCL (internal I2C bus 0)           | SSD1306 0.96". |
| GPIO 19    | USB D-                                  | Native USB-CDC. |
| GPIO 20    | USB D+                                  | Native USB-CDC. |
| GPIO 21    | OLED RST                                | Active low. |
| GPIO 36    | Vext control (and OLED power)           | Drive LOW to power Vext rail + OLED. |
| GPIO 37    | ADC_CTRL — battery monitor enable       | Drive LOW to allow VBAT divider read on GPIO 1. **GSR-ADC conflict source — see §3.** |
| GPIO 1     | VBAT ADC (ADC1_CH0)                     | Through internal divider. **GSR-ADC conflict source — see §3.** |

---

## 2. Mk0.5 allocations (sensor smoke-test board)

| Pin (GPIO) | Sensor / function           | Bus / mode      | Notes |
|------------|-----------------------------|-----------------|-------|
| GPIO 41    | External I²C SDA (bus 1)    | I²C @ 400 kHz   | Shared by MAX30102, MLX90614, MAX30205 (Wave 2). 4.7 kΩ pull-ups required. |
| GPIO 42    | External I²C SCL (bus 1)    | I²C @ 400 kHz   | (paired with GPIO 41) |
| GPIO 38    | MAX30102 INT (active low)   | input, pull-up  | FIFO almost-full interrupt. |
| GPIO 39    | MLX90614 alarm (optional)   | input, pull-up  | Not used unless thermography ladder activates. |
| GPIO 4     | GSR analog in (ADC1_CH3)    | analog input    | CJMCU-6701 output, 0–3.3 V range. See §3 conflict resolution. |
| GPIO 5     | AD8232 OUT (ADC1_CH4)       | analog input    | ECG analog. Wave 2 (Day 4). |
| GPIO 6     | AD8232 LO+ (leads-off +)    | input           | Wave 2. |
| GPIO 7     | AD8232 LO- (leads-off -)    | input           | Wave 2. |
| GPIO 35    | Status LED (heartbeat)      | output          | Soft PWM, 1 Hz idle / 4 Hz acquiring / solid on fault. |
| GPIO 45    | RESERVED — Wave 2 spare     | —               | Held for Mk1.0 dual-MCU UART or stim safety interlock. |
| GPIO 46    | RESERVED — Wave 2 spare     | —               | (as above) |

---

## 3. ADC conflict resolution (BLACKOUT_PLAN §3 known gotcha)

**Problem.** Heltec V3 wires the on-board Li-ion battery monitor to **GPIO 1
(ADC1_CH0)**, gated by **GPIO 37 (ADC_CTRL)**. The natural temptation is to
also park the GSR ADC on GPIO 1 because it is the most-documented ADC pin.
Doing so creates two failure modes:

1. **Bus contention** — when the firmware drives ADC_CTRL low to sample
   battery voltage, the GSR sensor's output gets back-driven through the
   internal divider, producing nonsense readings during the battery-sample
   window.
2. **Calibration drift** — the battery divider's parallel resistance shifts
   the GSR signal's source impedance, invalidating any GSR baseline taken
   while the firmware is alternating samples.

**Resolution.**
* GSR moves to **GPIO 4 (ADC1_CH3)**, fully isolated from the battery
  divider.
* Battery sampling stays on GPIO 1, but is rate-limited to **1 Hz** and only
  performed when no GSR acquisition is in flight.
* `drivers/battery.h` exposes `battery::sample_now()` which acquires a
  mutex shared with `drivers/gsr.h::gsr::sample_now()`.
* Both samplers MUST yield to whichever holds the mutex; this is asserted
  in the smoke test on Day 2.

**Why this matters for the ladder.** Mk0.5 is single-MCU. If the GSR-ADC
collision is not nailed down here, every higher Mk gate inherits silent
data corruption that masquerades as "sensor drift" and burns weeks of
chasing the wrong root cause.

---

## 4. Power budget (Mk0.5)

| Rail   | Source            | Budget    | Notes |
|--------|-------------------|-----------|-------|
| 3V3    | Heltec onboard LDO | ~500 mA  | Powers all I²C sensors. |
| 5V     | USB Vbus (CP2102) | ~500 mA   | Pass-through only. |
| Vext   | Heltec controlled | ~250 mA   | Gated by GPIO 36. NOT used at Mk0.5 (OLED powers from 3V3). |

Total expected idle draw: ~80 mA. Acquisition burst: ~140 mA. USB power is
sufficient; no external supply needed at Mk0.5. The WANPTEK DPS3010U bench
supply is reserved for Mk1.0+ coil-driver bring-up.

---

## 5. Verification protocol (Day 1 afternoon)

1. Read silkscreen and photograph board (archive under
   `firmware/mk0.5/docs/photos/`).
2. Continuity-check every pin in §2 with multimeter against header pin
   numbering. Any deviation from this table is a STOP-WORK condition.
3. Smoke-test MAX30102 driver (Day 1).
4. Smoke-test MLX90614 + GSR + battery monitor (Day 2, after Wave 1 arrival).

---

## 6. Change log

| Date       | Author      | Change                                      |
|------------|-------------|---------------------------------------------|
| 2026-05-15 | (operator)  | Initial draft, Day 1 morning.               |
