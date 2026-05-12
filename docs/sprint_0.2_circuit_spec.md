# Sprint 0.2 — HelmKit Mk0 Circuit Spec (Inventory-Driven)

**Sprint goal:** A *document*, not a board. Define what goes inside the 0.1 CAD shell.
**Hard constraint:** Near-zero cash budget. Build from existing tote inventory salvaged from the old tech lab. Anything not in the totes is **defer or omit**, not "buy."
**Status:** DRAFT — sections marked `[INVENTORY-TBD]` get filled after today's physical count.

> **Wiki alignment:** The wiki Mk1 BOMs are treated as **engineering intent**, not aspiration. Sprint 0.2 (Mk0) defers the coil drive chain only because we cannot yet enclose, current-limit, and watchdog it on this budget — not because the geometry is in doubt. Mk0 collects the biomarkers and platform that Mk1 will need; the wiki Mk1 spec is the next jump. See [wiki_synthesis.md § Pass 2](wiki_synthesis.md), [mk1_buildplan.md](mk1_buildplan.md), and the AI-onboarding note in [../README.md](../README.md).

---

## 1. Scope of Mk0

Mk0 is the **minimum-viable instrumented helm**: sensors-only or sensors + low-risk audio/photic stim. **No coil emitter at Mk0.** The coil (Tesla bifilar) is a Mk1 task gated behind:
- enclosed, instrumented, current-limited drive stage
- MCU-B watchdog firmware against the 12-row blacklist
- skin/scalp distance verified by CAD shell

For Sprint 0.2 we lock down only what we will *actually populate* on the Mk0 board.

### 1.1 Mk0 functional blocks (locked)

1. **MCU-A (doer):** sensor sampling, USB, optional audio/LED stim PWM.
2. **MCU-B (checker):** independent watchdog, kill-line on rail current / RF drive / temperature excursion. *May be deferred to Mk0.5 if we have only one MCU in inventory — see §3.*
3. **Sensor front-end:** whatever IMU / env / bio sensors we have.
4. **Power:** single-cell Li-ion or USB-bus, regulated to 3.3 V logic + isolated stim rail (Mk1).
5. **Connector / interface:** USB (data + charge) + at minimum one debug header.

### 1.2 Explicitly OUT of Mk0

- Coil drive stage
- nRF52840 / LoRa / mesh
- HackRF or SDR
- OLED HUD
- Bone-conduction transducers
- BLE pairing to Polar H10 (Mk1 if H10 is in inventory)

---

## 2. Sensor list — inventory pass required

Wiki-canonical Mk1 sensor stack is BME680 + MPU6050 + HMC5883L + PPG + Polar H10 BLE. For Mk0 we use whatever subset is **in the totes**. Tier by usefulness:

| Tier | Sensor class | Why it matters | Wiki Mk1 part | Mk0 inventory candidate |
|---|---|---|---|---|
| **Must-have** | 3-axis IMU (accel+gyro) | head pose, motion artifact rejection | MPU6050 / ICM-20948 | `[INVENTORY-TBD]` |
| **Strong nice-to-have** | 3-axis magnetometer | ambient field baseline; F4-relevant geomagnetic-sensitivity studies | HMC5883L / LIS3MDL | `[INVENTORY-TBD]` |
| **Strong nice-to-have** | Environmental (T/RH/P/VOC) | session-context logging; thermal-safety floor | BME680 | `[INVENTORY-TBD]` (BME280 is acceptable substitute) |
| **Want** | PPG (heart rate / HRV) | primary biomarker for stabilization studies | MAX30102 | `[INVENTORY-TBD]` |
| **Want** | Skin-contact electrodes (EEG / GSR) | optional Mk0.5 — needs analog front-end | ADS1299 / AD8232 | `[INVENTORY-TBD]` — almost certainly not in totes; deferred |
| **Optional** | Microphone | ambient audio context | ICS-43434 / MEMS | `[INVENTORY-TBD]` |
| **Optional** | Ambient light | photic stim sham control | TSL2591 / VEML7700 | `[INVENTORY-TBD]` |

**Inventory rule:** anything we have ≥1 of goes on the spec at its tier. Anything we have zero of moves to "Mk1 procurement list" and **does not block Mk0**.

---

## 3. MCU pick — inventory-driven

Wiki canonical: STM32F407 (doer) + RP2040 (checker). For Mk0 we use whatever MCU we have **the most of and the best toolchain familiarity with**.

### 3.1 Candidate MCUs to look for in the totes

Listed in rough order of preference for an Mk0 build:

| Preference | MCU / board | Why | Notes |
|---|---|---|---|
| 1 | **ESP32 / ESP32-S3 dev board** | I²C, SPI, BLE, WiFi, lots of pins, Arduino+ESP-IDF. Likely in tote. | BLE = optional Polar H10 path at Mk0.5 |
| 2 | **RP2040 (Pico / Pico W)** | Dual-core, PIO, USB native, very common. Pico W gives WiFi. | Matches wiki's checker chip; can also do doer for Mk0 |
| 3 | **Teensy 4.x** | 600 MHz Cortex-M7, fastest available; great for any DSP path. | Usually plentiful in old lab kit |
| 4 | **Arduino Nano 33 BLE / IoT** | nRF52840 onboard; matches wiki nRF52840 spec. | If we have any, prefer for Mk1 stabilizer module not Mk0 main |
| 5 | **STM32 Blue/Black Pill** | Cheap, capable; matches wiki F407 family. | Toolchain heavier than RP2040 |
| 6 | **AVR (Uno / Mega / Nano)** | Last resort; not enough RAM for serious sensor fusion | Mk0 reduced to logger only |

### 3.2 Single-MCU vs. dual-MCU at Mk0

The wiki and our [architecture.md §3](architecture.md#3-safety-architecture-dual-mcu) require dual-MCU **for any stimulus output**. Mk0 emits no stimulus, so:

- **Mk0 = single MCU acceptable.** Just the doer.
- **Mk0.5 (audio/LED stim added) = single MCU still acceptable** because audio/LED can be made safe by passive limits (resistor on LED, fixed-volume audio amp with rail limit).
- **Mk1 (coil) = dual-MCU REQUIRED.** Don't drive the coil until MCU-B is present and tested.

This means: **don't burn the budget on dual-MCU at Mk0 if we don't have two compatible chips in the totes.** Pick the single best MCU and ship.

### 3.3 Pin / peripheral budget (target MCU TBD)

Whatever MCU we pick must provide at least:

| Peripheral | Count | Purpose |
|---|---|---|
| I²C (any speed ≥ 100 kHz) | 1 bus, ≥ 4 devices | sensors |
| UART | 1 | debug / log out |
| USB device | 1 | data + charge (or charge via VBUS pass-through) |
| GPIO (digital) | ≥ 6 free | LEDs, button, safety line stub |
| ADC | ≥ 2 | battery monitor + thermistor |
| PWM | ≥ 2 | future LED stim + future audio |
| SPI | 1 (optional) | SD logging if card slot available |

Confirm against actual MCU spec sheet once selected.

---

## 4. Power budget (Mk0)

Mk0 has no high-current loads. Budget is dominated by MCU + sensors + LEDs.

| Load | Typical (mA @ 3.3 V) | Peak (mA) |
|---|---|---|
| MCU (active, BLE/WiFi off) | 30–80 | 150 |
| MCU (with BLE active) | +15 | +30 |
| I²C sensor bus (4 devices avg) | 5–15 | 30 |
| Status LEDs (2× @ 5 mA via R) | 10 | 10 |
| SD card write (if present) | 0 idle | 100 |
| **Total Mk0 active** | **~60–120 mA** | **~320 mA** |
| **Total Mk0 sleep (logger)** | **< 5 mA target** | — |

### 4.1 Power source decision tree (inventory-driven)

| If we have… | Then Mk0 power = |
|---|---|
| One 18650 cell + TP4056 charger + 3.3 V LDO/buck | single-cell Li-ion, USB-C or micro-USB charge |
| LiPo pouch + dev-board with onboard charger (ESP32-S3 dev, Nano 33, Adafruit Feather) | use the dev-board's PMIC; no separate charger |
| Nothing portable | USB-only Mk0 — no battery, tethered. Acceptable for bench testing. |

`[INVENTORY-TBD]` — fill after tote pass: cells, LiPos, charger ICs (TP4056/MCP73831), regulator ICs (AMS1117, AP2112, MIC5219), buck converters.

### 4.2 Runtime target (if battery present)

Mk0 target: ≥ 4 hours active logging on whatever cell we have. Wiki Mk1 target (3.5–12 h on 2×18650) is the Mk1 goal, not Mk0.

---

## 5. Board outline — Mk0 form factor

**Decision:** Mk0 is **breadboard or perfboard, NOT a fab'd PCB.** Reasons:
- Zero budget → no JLCPCB run.
- 0.1 CAD shell is the testbed; mechanical fit can be hand-iterated.
- Sprint 0.2 deliverable is a *document*, so the board outline is a *target footprint*, not a routed board.

### 5.1 Target footprint inside the helm shell

- Main board zone: behind/above the rear cranium curvature, on the 0.1 shell.
- Approx envelope: `[CAD-MEASURE-TBD]` mm × `[CAD-MEASURE-TBD]` mm × ≤ 12 mm thick.
- Off-board mounting points for: IMU (centerline top), magnetometer (rear, away from speakers/motors), PPG (forehead or earlobe clip), battery (rear nape).

### 5.2 Topology

```
            ┌──── IMU (centerline, top) ──────────────┐
            │                                          │
[BATT]──[PMIC/CHRG]──[3.3V REG]──[MCU]──[I²C bus]──┤
            │                          │              │
            └── thermistor             └── status LEDs│
                                                       │
                                          [MAG] (rear)│
                                          [ENV]       │
                                          [PPG] (off-board, lead)
```

Five-node star around the MCU. No fabrication required — wire it on perfboard.

---

## 6. Connector choices

Wiki-canonical: USB-C PD + GoPro/Picatinny + I²C + USB 2.0 HS + UART + open-drain safety GPIO.
Mk0 reality:

| Connector | Mk0 implementation | Wiki Mk1 target |
|---|---|---|
| Host data + charge | **Whatever the dev-board has** (micro-USB if ESP32, USB-C if Pico W / S3 / Feather). Don't add a second connector. | USB-C PD 5 V / 3 A |
| External sensor (PPG lead, EEG future) | **3.5 mm TRRS** or **4-pin JST-SH** — whichever has more inventory | JST-SH |
| Inter-module bus (Mk1 only) | Not present at Mk0 | I²C 100 kHz on JST-SH 4-pin (SDA/SCL/3V3/GND) |
| Safety kill line (Mk1 only) | Not present at Mk0 | open-drain GPIO, one shared line |
| Debug | 6-pin header (TX/RX/GND/3V3/RST/BOOT) | same |
| Mount | Velcro to 0.1 shell (Mk0). Picatinny/GoPro is Mk1+. | GoPro / Picatinny |

**Mk0 rule:** one charge/data port + one debug header + one off-board sensor lead. That's it.

---

## 7. Safety floor (carry-over from wiki, mandatory even at Mk0)

Even with no stimulus, Mk0 enforces:

1. **Battery thermistor read at ≥ 1 Hz.** If cell > 50 °C, MCU shuts charger and logs event.
2. **No exposed cell terminals.** Battery in a holder or potted.
3. **Single fault tolerance on battery:** the charger IC + a polyfuse on the cell line. PolyFuse value `[INVENTORY-TBD]`.
4. **Skin contact = passive only at Mk0.** No active current injection (no GSR drive, no TENS, no coil).
5. **All firmware-emitted signals (LED brightness, audio volume) capped in code** with a separate constant block reviewed before each flash.

The wiki's [12-row blacklist](wiki_synthesis.md) is Mk1-relevant (coil drive); Mk0 inherits items #1–#5 above as its working safety contract.

---

## 8. Today's deliverables

| # | Task | Owner | Status |
|---|---|---|---|
| 1 | **Tote inventory pass** — categorize by: MCU/board, sensors, power components, connectors, passives, mechanical hardware. Result feeds §2 / §3 / §4 / §6 of this doc. | jono | ☐ |
| 2 | Fill in `[INVENTORY-TBD]` markers in this doc | jono | ☐ |
| 3 | Pick Mk0 MCU (one row from §3.1) and lock it | jono | ☐ |
| 4 | Pick Mk0 sensor stack from §2 inventory subset (must-have IMU mandatory; mag + env + PPG if available) | jono | ☐ |
| 5 | Confirm power source choice from §4.1 tree | jono | ☐ |
| 6 | Sketch §5.1 footprint against 0.1 CAD shell (rough — mm-level OK) | jono | ☐ |
| 7 | Identify Mk1 procurement list = wiki BOM **minus** what's in totes. Save as `docs/mk1_procurement.md` later. | jono | ☐ |

**Definition of done for Sprint 0.2:** every `[INVENTORY-TBD]` and `[CAD-MEASURE-TBD]` marker in §§2–6 resolved. Doc committed. No solder iron touched.

---

## 9. Open questions to resolve during inventory

- Do we have any **isolated DC-DC** (for Mk1 coil stim rail), or do we defer that to a future buy?
- Do we have **shielded cable / coax / twisted pair** for the magnetometer lead?
- Do we have a **second MCU** of the same family for the future MCU-B checker?
- Do we have any **dev-boards with onboard PMIC + battery connector** (Adafruit Feather, ESP32-S3 Devkit-C with battery jack)? This collapses §4 hugely.
- Do we have a **microSD module or breakout**? Enables Mk0-as-logger without a phone tether.

---

## 10. Cross-refs

- [architecture.md](architecture.md) — overall slot/module model + dual-MCU rationale
- [mk1_buildplan.md](mk1_buildplan.md) — what Mk0 grows into
- [wiki_synthesis.md § Pass 2](wiki_synthesis.md) — wiki BOM we are *not* trying to match at Mk0
- [safety.md](safety.md) — full safety posture
- [falsification.md](falsification.md) — biomarker measures we will eventually need to support (HRV via PPG is the key Mk0→Mk1 enabler)
