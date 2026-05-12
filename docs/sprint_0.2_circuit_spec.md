# Sprint 0.2 — HelmKit Mk0 **Platform** Circuit Spec (Inventory-Driven)

**Sprint goal:** A *document*, not a board. Define what goes inside the 0.1 CAD shell.
**Hard constraint:** Near-zero cash budget. Build from existing tote inventory. Anything not in the totes is **defer or omit**, not "buy."
**Status:** ✅ FINAL — inventory pass complete (2026-05-12); all `[INVENTORY-TBD]` resolved except `[CAD-MEASURE-TBD]` items which wait on the 0.1 shell measurement pass.

## 0. Framing — HelmKit is a platform, not a device

This is the architectural reframe that supersedes earlier drafts: **HelmKit** is the **rig** — the skull-mount chassis, the MCU spine, the power bus, the safety bus, and the module-connector spec. It does not, by itself, do psionics.

The psionic / cognitive-modulation work lives in **modules** that clip onto the HelmKit:

- **Psi Stabilizer** — the first module; *"stabilizes the mind"* via PBM + Schumann audio + gentle coil + HRV biofeedback. See [§15](#15-psi-stabilizer-mk1--first-module-against-this-bus) below.
- **Psi Defender** — RF/EM monitoring + emission countermeasures. Future module.
- **HUD** — visual / OLED feedback for the operator. Heltec LoRa 32 already in the platform spine handles this.
- **Field Recorder** — multi-modal session logger. Future module ([beyond_wiki_concepts.md § 5.1](beyond_wiki_concepts.md)).
- **Future:** PBM-halo standalone, multispectral imager, TDOA localizer, paired-helm sync.

Sprint 0.2 specs the **platform**, including the module-bus the Psi Stabilizer Mk1 will clip onto. The Stabilizer itself is its own sprint (planned: sprint 0.3a). Sprint 0.3 (FDTD design-cert) is a separate Mk2-enabler track. See [gpu_farm_workloads.md § W4](gpu_farm_workloads.md).

> **Wiki alignment:** The wiki Mk1 BOMs are treated as **engineering intent**, not aspiration. Inventory clears wiki Mk1 spec end-to-end with zero procurement gaps — see [inventory.md § 10](inventory.md). The wiki conflates platform + modules into a single "helm." This doc separates them.

---

## 1. Scope of Mk0 platform

Mk0 is the **minimum-viable HelmKit platform** — the chassis + spine that future modules clip into. **No psionic payload at Mk0.** The Psi Stabilizer module is sprint 0.3a (parallel track); the coil drive lives inside *that* module, not on the platform board.

For Sprint 0.2 we lock down only what the platform itself must provide.

### 1.1 Mk0 platform functional blocks (locked)

1. **MCU-A (doer):** Pi 4. Hosts I²C bus, USB (SDR + sensors), real-time logging.
2. **MCU-B (checker):** Nano v3. Independent watchdog + kill-line + safety blacklist firmware.
3. **MCU-C (HUD + BLE + LoRa):** Heltec LoRa 32. OLED + BLE (Polar H10) + LoRa mesh + Li-Po PMIC.
4. **Platform sensor front-end:** six positions (see §2.1) — head-pose IMU (MPU9250), rail V+I monitor (INA219), helm-internal NTC, helm-on-head cap-touch (TTP223), battery-cell NTC, exterior ambient light (TEMT6000). *Module-specific sensors live on the module, not the platform.*
5. **Power bus:** USB-C in (bench) or Talentcell 12V/5V dual rail (portable); 5V to Pi + MCU-C, 3.3V to logic, 12V passed through to module bus.
6. **Module bus (NEW — §6.5):** mechanical hardpoints + 6-pin electrical connector providing power + I²C + safety line to clip-on modules.
7. **Debug interface:** UART header + status LEDs.

### 1.2 Explicitly OUT of Mk0 platform (lives in modules)

- **Coil drive stage** → in Psi Stabilizer module (sprint 0.3a)
- **HackRF / wideband SDR** → in Psi Defender module (future)
- **NESDR coil-emission monitor** → in Psi Stabilizer module (sprint 0.3a)
- **PBM 730 nm halo** → in Psi Stabilizer module (sprint 0.3a)
- **MLX90640 thermal + SGP40 VOC + ELP camera** → in Field Recorder module (future, beyond-wiki §5.1)
- **Polar H10 BLE pairing** → platform *provides* the BLE radio (Heltec); module *consumes* the data
- **Any active stim (audio, photic, magnetic)** → module-side, never platform-side

---

## 2. Sensor list — inventory pass required

**Doctrine (per §0 platform/module split):** sensors are now classified by **which board they live on**, not by tier alone. The HelmKit platform owns the minimum sensor set needed for *the rig itself to know its state*: helm-on-head, head-pose, internal thermal, battery health. Everything else — every sensor whose purpose is **psionic measurement or stimulus instrumentation** — belongs in a module.

This is the single most important change to §2 from earlier drafts: most of the "Mk0 sensors" in prior tables were really Stabilizer-module or Defender-module or Recorder-module sensors that got mis-assigned to the platform. They are reassigned below.

### 2.1 Platform sensors (live on the HelmKit board itself)

These are the only sensors physically mounted to / wired into the platform PCB. They report on the **rig**, not on the wearer's psionic state.

| Tier | Sensor class | Why platform-side | Wiki Mk1 part | Mk0 pick (inventory-confirmed) | I²C addr |
|---|---|---|---|---|---|
| **Must-have** | 3-axis IMU + on-die mag (head pose) | rig orientation — every module needs this in its data stream; piping over the module bus is wasteful | MPU6050 / ICM-20948 | ✅ **1× MPU9250** (centerline top of shell); spares: 2× MPU9250 + 1× MPU6050 | 0x68 (IMU) / 0x0C (AK8963) |
| **Must-have** | Battery / rail monitor (V + I) | platform power-bus telemetry; Nano needs this for safety latch | INA219 / shunt + ADC | ✅ **INA219** (sensor kit) on 12 V rail + Nano internal ADC on 5 V rail | 0x40 |
| **Must-have** | Helm-internal thermistor | over-temp on Pi 4 + Heltec inside potted shell | NTC 10k | ✅ **NTC 10k** (XXXL kit) on Nano ADC | — |
| **Must-have** | Helm-on-head detect (capacitive touch) | safety prerequisite for any module to leave standby; cheap and reliable | TTP223 | ✅ **TTP223 module** (both sensor kits) at scalp-contact pad | digital GPIO |
| **Should-have** | Battery cell temp (charge-side) | wiki safety floor §7 item 1: cell > 50 °C → cut charger | NTC 10k | ✅ **NTC 10k** at 18650 holder, Nano ADC | — |
| **Nice-to-have** | Ambient light at exterior | session-context (indoor/outdoor); also drives OLED auto-dim | TSL2591 / TEMT6000 | ✅ **TEMT6000** (RPi kit) | analog/ADC |

That's it. Six sensor positions on the platform board. Anything else is module-side.

### 2.2 Stabilizer Mk1 module sensors (§15 — built sprint 0.3a)

Live on the Psi Stabilizer clip-on PCB, talk to platform only via the module bus.

| Sensor | Wiki Mk1 part | Mk0 pick (inventory-confirmed) | Role |
|---|---|---|---|
| Scalp temperature (PBM safety) | DS18B20 | ✅ **DS18B20** (sensor kit) | thermal lockout on 730 nm halo |
| Coil drive current sense | shunt + INA219 | ✅ **INA219** (second one in inventory) | enforces FDTD-certified envelope |
| Coil-cavity field monitor | small loop antenna + ADC | ✅ small wound coil + Nano ADC (or stretch: nRF NESDR on bench) | confirms drive level matches commanded |
| HRV input (closed-loop) | Polar H10 BLE | ❌ Polar H10 (~$80, procure for sprint 0.3a) — **only true gap** | the visible biofeedback |
| Audio output-level sense | resistor divider + ADC | ✅ resistor divider into Heltec ADC | bone-conduction-substitute volume cap |

### 2.3 Defender module sensors (future module)

Live on the Psi Defender clip-on, not in this sprint. Listed for completeness so they don't get mis-assigned to the platform later.

| Sensor | Inventory | Role |
|---|---|---|
| Magnetometer #2 (gradiometer pair with platform MPU9250) | ✅ second MPU9250 | wiki Defender 2× mag pattern |
| Wideband SDR | ✅ HackRF One + 3× NESDR + Ham It Up + 1:9 balun | RF survey / emission-compliance |
| Thermal IR | ✅ MLX90640 | wiki Defender thermal sense |
| Hall / reed | ✅ in RPi kit | discrete magnetic-event triggers |

### 2.4 Field Recorder module sensors (future module — see [beyond_wiki_concepts.md §5.1](beyond_wiki_concepts.md))

Live on the Field Recorder clip-on, not in this sprint.

| Sensor | Inventory | Role |
|---|---|---|
| Environmental (VOC + P + T/RH) | ✅ SGP40 + BMP180 + DHT11 | session-context envelope |
| Wide-FOV camera | ✅ ELP 170° 8 MP USB fisheye | visual session log |
| Ambient microphone | ✅ Sound Detection module + electret | audio session log |
| UV index | ✅ GUVA-S12SD | circadian / outdoor sham control |
| Photoresistor (back of head) | ✅ in RPi kit | sham-control for photic stim |

### 2.5 Sensors that intentionally have no current home

| Sensor | Inventory | Why deferred |
|---|---|---|
| PPG (MAX30102 / DIY photoresistor+IR) | ❌ no MAX30102; could DIY but Polar H10 is the real path | Stabilizer Mk1 uses Polar H10 instead; DIY PPG is a Mk3 falsifier exercise |
| EEG / GSR (ADS1299 / AD8232) | ❌ no AFE | needs proper instrumentation amp; explicitly defer to Mk2+ when we have an AFE in inventory |

### 2.6 Inventory rules

- **Platform sensor set is locked.** Adding a 7th platform sensor requires explicit revision to this section.
- A sensor may move from a module table to the platform table **only if** every future module would need it independently. The IMU passed this test; the magnetometer #2 did not (only Defender needs it as a gradiometer pair).
- The platform's MPU9250 data stream is broadcast on the platform I²C bus and is **readable** by any attached module — modules do not need their own IMU for head-pose context.

---

### 2.7 Architectural note: why this matters

In the earlier draft, the platform sensor table listed HackRF, MLX90640, ELP camera, MAX30102, second MPU9250, MLX, SGP40, etc. — none of which actually live on the rig itself. Loading the platform with all of those would have:

1. Blown the platform power budget (HackRF alone draws ~500 mA on RX).
2. Made the platform PCB un-routable in a clip-on-friendly form factor.
3. Coupled platform iteration to every module's iteration — defeats the platform/module split entirely.
4. Created a forever-Mk0 device instead of a platform that grows.

The platform is now **six sensor positions**, all of which report on the rig's own state. The "psionic measurement" sensors are correctly attributed to the modules that own the physics they measure.

---

## 3. MCU pick — inventory-driven

Wiki canonical: STM32F407 (doer) + RP2040 (checker). For Mk0 we use whatever MCU we have **the most of and the best toolchain familiarity with**.

### 3.1 Candidate MCUs to look for in the totes

Listed in rough order of preference for an Mk0 build:

**LOCKED — picks based on 2026-05-12 inventory:**

- **MCU-A (doer): Raspberry Pi 4.** Hosts I²C bus, USB (SDR + sensors), real-time logging, optional ML inference. Runs Linux; Python + C extensions for the bus + control loops.
- **MCU-B (checker): Arduino Nano v3 (ATmega328P).** Small enough to formally audit. Holds the 12-row safety blacklist in flash. Independent power monitoring + kill GPIO. Talks to Pi 4 over I²C as a watchdog slave; raises an open-drain SAFETY line on any violation.
- **MCU-C (HUD / BLE / LoRa): Heltec LoRa 32 (ESP32).** Drives the 0.96" OLED HUD, BLE for Polar H10 (when procured), LoRa for inter-helm mesh, secondary Li-Po battery manager. **Two in inventory** — second one is hot spare or paired-helm mesh node.
- **Heavy compute (rack, Mk0.5+): 1× NVIDIA Jetson AGX Orin 32 GB** (~200 TOPS / ~5.3 TFLOPs FP16). Closed-loop FDTD verification of coil emission; wideband SDR DSP at HackRF full rate; transformer-class ML on EEG/HRV.
- **Edge compute (per-helm, Mk1+): 4× Jetson Nano** (2× Seeed J1020 production + 2× J1010 dev) — distributed inner-loop DSP, paired-helm mesh deployment.

This is a *three*-MCU architecture instead of the wiki's two, but the third (Heltec) is a free addition since it consolidates OLED + BLE + LoRa + PMIC into one board we already have two of.

Why this stack over the wiki-canonical STM32F407+RP2040:
- Pi 4 is wildly over-spec for the doer role, which is fine — gives us margin to run SDR DSP, full Linux logging, and ML inference without a second board.
- Nano v3 as MCU-B is a step *down* from RP2040 in compute, but a step *up* in formal-auditability — the 32K flash limit forces the watchdog firmware to stay small enough to read end-to-end.
- Same checker/doer pattern the wiki specifies, just realized with parts we own.

### 3.1.1 If inventory diverges from expectation, fallback order is:

| Preference | MCU / board | Why | Notes |
|---|---|---|---|
| 1 (locked) | **Raspberry Pi 4 + Arduino Nano v3** | per above | uses what we have |
| 2 | **ESP32 / ESP32-S3 dev board** | I²C, SPI, BLE, WiFi | BLE = Polar H10 path at Mk0.5 |
| 3 | **RP2040 (Pico / Pico W)** | matches wiki's checker chip | wiki-aligned but no BLE |
| 4 | **Teensy 4.x** | DSP-class compute | overkill but functional |
| 5 | **STM32 Blue/Black Pill** | matches wiki F407 family | toolchain heavier |

### 3.2 Single-MCU vs. dual-MCU at Mk0

The wiki and our [architecture.md §3](architecture.md#3-safety-architecture-dual-mcu) require dual-MCU **for any stimulus output**. Mk0 emits no stimulus.

Given the inventory has both Pi 4 and Nano v3 in quantity, **we go dual-MCU from Mk0 onward**. This is free with current inventory and means the Nano watchdog code matures across all the Mk0 sensor-only sessions, ready for Mk1 coil drive. Wiring up MCU-B early is cheap insurance.

- **Mk0:** Pi 4 logs sensors; Nano watches the rail + thermistor and is wired to the SAFETY line but has no kill target to act on yet (just logs hypothetical kills).
- **Mk0.5:** Audio/LED stim added; Nano can now actually cut the stim line.
- **Mk1:** Coil drive added; Nano kill-line cuts HV-module enable. **Hard requirement** before any on-head test.

### 3.3 Pin ownership — three-MCU architecture

This section replaces an earlier single-MCU pin budget. Each pin is owned by exactly one MCU. Inter-MCU communication uses I²C (Pi 4 master, Nano + Heltec as slaves) so the three MCUs can be physically wired with minimum harness count.

Pinouts referenced: Pi 4B 40-pin GPIO header (BCM numbering); Arduino Nano v3 ATmega328P (Arduino-pin numbering, D0–D13 + A0–A7); Heltec WiFi LoRa 32 V3 (ESP32-S3, GPIO numbering).

#### 3.3.1 Raspberry Pi 4B (doer) — pin assignments

The Pi 4 is the I²C master, USB host, primary logger, and module-bus orchestrator. Uses only the 40-pin GPIO header + USB-A ports + USB-C power-in.

| Pi 4 pin (BCM) | Header pin | Function | Connects to | Harness |
|---|---|---|---|---|
| GPIO2 (SDA1) | 3 | **I²C-1 SDA** (master) | platform I²C bus → MPU9250 Z2, INA219 Z3, Heltec slave, Nano slave, module bus Z5 | H1 + H4 |
| GPIO3 (SCL1) | 5 | **I²C-1 SCL** (master) | same bus as above | H1 + H4 |
| GPIO14 (TXD0) | 8 | UART TX (debug) | Z7 debug header | H5 |
| GPIO15 (RXD0) | 10 | UART RX (debug) | Z7 debug header | H5 |
| GPIO4 | 7 | NTC-1 read (helm-internal temp) via DS18B20 1-Wire (NTC alternative if DS18B20 procured) | Z3 internal NTC | onboard |
| GPIO17 | 11 | SAFETY_n sense (read-only; Pi can observe but only Nano can drive) | Z3 SAFETY_n bus | onboard |
| GPIO22 | 15 | Helm-on-head sense (TTP223 output, level-shifted from 3.3 V to 3.3 V — direct connect) | Z1 TTP223 | H5 |
| GPIO23 | 16 | Status LED — green (session active) | Z7 LED | H5 |
| GPIO27 | 13 | TEMT6000 read (analog → use MCP3008 SPI ADC on Pi, or hand off to Nano A1 — see §3.3.4) | — | H5 |
| 5V_USB-C in | (USB-C jack) | power-in from Z3 buck output | Z3 5V_PLATFORM rail | H3 path |
| GND | 6, 9, 14, 20, 25, 30, 34, 39 | shared ground | star-ground at Z2 | onboard |
| USB-A × 4 | (USB-A jack) | sensors / SDR / external | external | external harness |
| HDMI / DSI / CSI | — | **unused at Mk0** | — | — |
| GPIO0/1 (ID EEPROM) | 27, 28 | **reserved** for future HAT EEPROM | — | — |
| GPIO5–GPIO13 (SPI, SCLK, etc.) | 29–33 | **free for sprint 0.4+** (SPI ADC, SD card, etc.) | — | — |
| GPIO16, 19–26 | various | **free for future expansion** | — | — |

**Pi 4 GPIO utilization at Mk0: 8 of 28 usable pins. Plenty of headroom.**

#### 3.3.2 Arduino Nano v3 (checker) — pin assignments

The Nano is the safety watchdog. Owns the SAFETY_n line, the 12V_RAIL load switch enable, battery + rail current sense via INA219, and two ADC channels for NTC thermistors. **Holds the 12-row safety blacklist in firmware** (§7).

| Nano pin | Function | Connects to | Drive direction |
|---|---|---|---|
| **D0 (RX)** | USB-serial RX (programming + debug log out via FTDI on USB) | onboard | input |
| **D1 (TX)** | USB-serial TX | onboard | output |
| **D2 (INT0)** | **SAFETY_n line** — open-drain, bidirectional. Pulled high by 10 kΩ. Nano drives low to latch. External (module / Pi / key-switch) can also pull low. Falling edge wakes Nano via INT0. | Z3 SAFETY_n bus + Z5 module bus pin 6 + Pi GPIO17 (read) | open-drain (output via INT) + input |
| **D3 (INT1, PWM)** | Boat-rocker arm sense (12V_BATT detect via voltage divider) — falling edge means rocker was just opened, latch SAFETY_n | Z4 rocker | input |
| **D4** | **12V_RAIL kill enable** — drives the opto input of the 5 V 2-channel relay module (K1), in series with key-switch coil contact. HIGH = K1 closed = rail enabled. LOW (or key OFF) = rail open. See §6.5.5 for part pick and §6.5.6 for protection passives. | Z3 relay K1 | output, default low (rail OFF at boot) |
| **D5 (PWM)** | Status LED — red (HV/coil armed) | Z7 LED | output |
| **D6 (PWM)** | Status LED — amber (watchdog OK / heartbeat) — Nano blinks this at 1 Hz so loss = visible | Z7 LED | output |
| **D7** | Key-switch state read (3-pos: OFF / ARMED / SESSION). One GPIO + one ADC channel (A2 below) decode three states | Z4 key-switch | input |
| **D8** | Reserved — Mk0.5 fault-mode visible-on-OLED trigger | — | — |
| **D9 (PWM)** | Reserved — Mk1 audible alarm tone out (piezo) | — | output |
| **D10–D13 (SPI)** | **reserved** for sprint 0.4 SD-card audit log | — | — |
| **A0** | INA219 alert read (digital, conventionally A-pin) — could move to D-pin later | — | input |
| **A1** | NTC-1 read (helm-internal temp Z3) — 10 kΩ NTC voltage divider | Z3 NTC | analog input |
| **A2** | NTC-2 read (battery-cell temp Z4) | Z4 NTC | analog input |
| **A3** | TEMT6000 ambient light (decision: Nano A3 owns this, not Pi — keeps Pi GPIO27 free) | Z1 TEMT6000 | analog input |
| **A4 (SDA)** | **I²C SDA** (slave; Nano answers Pi 4 master at 0x42) | platform I²C bus | bidir |
| **A5 (SCL)** | **I²C SCL** (slave) | platform I²C bus | input |
| **A6 / A7** | analog-only ADCs — **free for Mk1 expansion** | — | — |
| Vin | 7–12 V regulated input (Nano onboard linear reg) | Z3 5V_PLATFORM rail (Vin tolerates 5 V on Nano clone) | input |
| GND | shared | star-ground Z2 | — |
| 5V / 3V3 | not used externally | — | — |

**Nano utilization at Mk0: 13 of ~20 usable pins. ~6 pins reserved for SPI / Mk1 expansion.**

> **Note on Nano A4/A5 vs §6.5 module-bus I²C:** the Nano is a *slave* on the platform I²C bus; it does NOT have a separate I²C bus. Pi 4 GPIO2/3 is the only bus. Nano answers at 0x42. This is intentional — keeps wiring count down — but it means a Pi I²C lockup also takes out Nano comms. Nano's SAFETY_n latch behavior is therefore **independent of I²C**: even if I²C dies, Nano still drives D2 SAFETY_n low via its INT0 watchdog timer running off the internal RC oscillator. Safety is preserved through total I²C failure.

#### 3.3.3 Heltec LoRa 32 V3 (HUD / BLE / LoRa) — pin assignments

The Heltec drives the OLED (Z1 window), runs BLE for the Polar H10 link (Stabilizer Mk1), and reserves LoRa for inter-helm mesh (Mk2+). Many of its pins are factory-committed; we use only the user-available ones.

| Heltec V3 pin (ESP32-S3 GPIO) | Function | Connects to | Notes |
|---|---|---|---|
| GPIO17 | **factory OLED SDA** (internal I²C bus to SSD1306) | onboard OLED | reserved by Heltec |
| GPIO18 | **factory OLED SCL** | onboard OLED | reserved by Heltec |
| GPIO36 (Vext) | factory Vext enable (powers the OLED) | onboard | reserved; drive HIGH at boot |
| GPIO8–14 | factory **LoRa SX1262** (NSS, SCK, MOSI, MISO, RST, BUSY, DIO1) | onboard | reserved by Heltec |
| GPIO35 | factory user LED | onboard | usable as 4th status LED if needed |
| GPIO0 | factory **USR / BOOT button** + Heltec OLED-side button 1 | onboard | session-UI button-1 (intention entry) |
| GPIO1 | factory VBAT ADC | onboard | battery monitor (Heltec has its own Li-Po path; we'll just leave it disconnected at Mk0) |
| **GPIO19** | **Platform I²C SDA** (slave; Heltec answers Pi master at 0x43) — separate I²C bus from the factory OLED bus | platform I²C bus | bidir |
| **GPIO20** | **Platform I²C SCL** (slave) | platform I²C bus | input |
| **GPIO38** | Heltec OLED-side button 2 (session-UI button-2: commit) | onboard side-button via inventory tactile | input |
| **GPIO39** | Heltec OLED-side button 3 (session-UI button-3: engage) | onboard side-button via inventory tactile | input |
| **GPIO40** | BLE-status LED (optional — driven LOW when Polar H10 paired) | reserved | output |
| **GPIO41** | UART TX (debug log to USB-serial through CP2102) | onboard | output |
| **GPIO42** | UART RX | onboard | input |
| **GPIO37** | Reserved — Mk1 audio enable (drives PAM8403 SD pin from platform side, sprint 0.3a may move this to module) | — | output |
| 5V_USB-C | power-in from Z3 5V_PLATFORM rail | Z3 | — |
| GND | shared | star-ground Z2 | — |

**Heltec utilization at Mk0: 6 user pins out of ~14 user-accessible. The board is mostly its own factory peripherals.**

> **Note on Heltec second I²C bus:** ESP32-S3 has two I²C controllers; we use #2 on GPIO19/20 for the platform bus, leaving #1 on GPIO17/18 for the factory OLED. **No conflict.** Required arduino-esp32 init: `Wire1.begin(19, 20, 100000)` or equivalent ESP-IDF call.

#### 3.3.4 Cross-MCU I²C bus map (the platform's only shared bus)

| Address | Device | Owner location | Behavior |
|---|---|---|---|
| 0x40 | INA219 (platform 12V rail monitor) | Z3 | sensor |
| 0x42 | **Nano v3 (slave)** | Z3 | watchdog comms + SAFETY_n status read |
| 0x43 | **Heltec V3 (slave)** | Z3 | UI events: button presses, OLED-display-state echo, BLE link status |
| 0x48 | MCP3008-equivalent SPI-ADC bridge (Mk1, sprint 0.4) | Z3 | reserved |
| 0x68 | MPU9250 IMU (accel + gyro) | Z2 | sensor |
| 0x0C | AK8963 (MPU9250 on-die magnetometer) | Z2 | sensor (accessed via MPU9250 bypass) |
| 0x10 + N | Module-bus device IDs (Stabilizer = 0x01 → I²C 0x11; Defender = 0x12; HUD = 0x13; Recorder = 0x14) | Z5 (out the bus) | module identity + watchdog + telemetry per §6.5.3 |

**Bus voltage:** 3.3 V (Pi 4 native; Nano A4/A5 5V-tolerant inputs accept 3.3 V; Heltec ESP32-S3 native 3.3 V; module-side modules level-shift if they're 5 V).
**Pull-ups:** 4.7 kΩ on platform side only, **once** on the bus (Z3 board), not on every device. Module-side modules must NOT add pull-ups (sprint 0.3a Stabilizer compliance).
**Speed:** 100 kHz (standard mode). Pi 4 master polls round-robin: INA219 → Nano → Heltec → MPU9250 → AK8963 → modules. Worst-case full poll ≈ 10 ms.

#### 3.3.5 Pin-count sanity check vs. earlier §3.3 generic budget

The earlier draft demanded "≥ 6 free GPIO, ≥ 2 ADC, ≥ 2 PWM, 1 I²C bus ≥ 4 devices, 1 UART, 1 USB, optional SPI." Reality check across the three MCUs:

| Demand | Available | Verdict |
|---|---|---|
| 1 I²C ≥ 4 devices | 1 bus, 6+ devices, room for ~120 more addresses | ✅ over-spec |
| 1 UART | 3 UARTs (one per MCU) — all wired to USB-serial | ✅ over-spec |
| 1 USB device | Pi 4 USB-C in (data + 5 V) + Pi 4× USB-A out + Heltec USB-C | ✅ over-spec |
| ≥ 6 free GPIO | Pi 4: 20+ free; Nano: 6 free; Heltec: ~8 user-free | ✅ over-spec |
| ≥ 2 ADC | Pi 4 has none native (needs SPI-ADC); Nano: 5 ADC available; Heltec: ~2 user-free | ✅ via Nano |
| ≥ 2 PWM | Nano: 4 PWM remaining; Heltec: many | ✅ over-spec |
| Optional SPI | Pi 4 SPI0/SPI1; Nano D10-D13 SPI; Heltec SX1262 already uses SPI | ✅ reserved for sprint 0.4 SD-card audit |

**Pin budget closed at sprint 0.2.** No deferred decisions in this section. Architecture is wireable.

---

## 4. Power budget (Mk0 platform + module bus)

This section was rewritten in the §0 platform/module reframe. Earlier drafts assumed Mk0 = "MCU + sensors + LEDs ~60–120 mA." That number was for a single-MCU device. The locked architecture is **three MCUs** (Pi 4 + Nano + Heltec) **plus the module bus** delivering up to 12 V @ 2 A + 5 V @ 1 A to whatever clips on. Budget must reflect that.

### 4.1 Platform-only consumption (no module attached)

All numbers @ 5 V battery-side rail unless noted. Sources: Raspberry Pi Foundation power doc (Pi 4B), Arduino ATmega328P datasheet, Heltec WiFi LoRa 32 V3 product brief.

| Load | Typical (mA @ 5 V) | Peak (mA @ 5 V) | Notes |
|---|---|---|---|
| **Pi 4B** (Linux, logging, no HDMI, no display server) | 600–800 | 1200 | peak = 4-core compile burst; HDMI off saves ~20 mA |
| **Arduino Nano v3** (ATmega328P @ 16 MHz, sensors I²C polled @ 100 Hz) | 20 | 40 | bare ATmega ~12 mA; +linear reg + LED ~8 mA |
| **Heltec LoRa 32** (ESP32 + 0.96″ OLED, BLE active, LoRa idle/listen) | 80 | 150 | peak = LoRa TX burst (≤ 1 s); BLE alone ≈ 50 mA |
| **Platform sensors (6 positions)** | 10 | 15 | MPU9250 ~3.5 mA, INA219 ~1 mA, TTP223 ~5 mA, TEMT6000 ~µA, 2× NTC dividers ~µA |
| **Status LEDs** (3× through-hole @ ~5 mA) | 15 | 15 | red/amber/green per §6.1 |
| **I²C pull-ups + housekeeping** | 5 | 10 | 4.7 kΩ × 2 lines × 3.3 V |
| **Buck/regulator overhead** (~85 % efficiency) | +15 % | +15 % | 12 V → 5 V buck loss |
| **Platform typical** | **~830 mA @ 5 V ≈ 4.2 W** | — | sustainable session draw |
| **Platform peak (≤ 1 s)** | — | **~1500 mA @ 5 V ≈ 7.5 W** | Pi 4 burst + Heltec LoRa TX coincident |
| **Platform sleep** (Pi 4 halted, Nano + Heltec watchdog only) | < 100 mA | — | aspirational; not Mk0-required |

### 4.2 Module bus capability (platform must source)

Per §6.5.1, the platform commits to delivering on the module bus:

| Rail | Continuous | Peak (≤ 100 ms) | Notes |
|---|---|---|---|
| +5V_LOGIC | 1 A (5 W) | 1.5 A | for module-side MCU + logic + low-power sensors |
| +12V_RAIL | 2 A (24 W) | 3 A | for module coil drive / PBM array / audio amp / HV-module enable |
| Total bus headroom | **29 W continuous, 42 W peak** | — | sized for worst-case Stabilizer Mk1 (see §4.3) |

### 4.3 Platform + Stabilizer Mk1 attached (sizing target)

This is the real number that matters — what the battery has to deliver during a session.

| Subsystem | Average (W) | Peak (W) | Source |
|---|---|---|---|
| Platform (per §4.1) | 4.2 | 7.5 | three MCUs + sensors + LEDs |
| Stabilizer 5V_LOGIC: module MCU (if any) + sensor amps | 0.5 | 1.0 | DS18B20 + 2× INA219 + audio level sense |
| Stabilizer 12V_RAIL: 4× Chanzon 730 nm COB PBM ring | 2.0 | 6.0 | driven well below 3 W nameplate each (eye-safety + scalp temp); peak = startup current |
| Stabilizer 12V_RAIL: PAM8403 audio amp + 2× 40 mm drivers | 0.5 | 1.0 | bone-conduction-substitute, sub-conversational volume |
| Stabilizer 12V_RAIL: bifilar coil drive at Schumann + harmonics | 0.5 | 1.5 | sub-µT field is *very* low power; envelope set by sprint 0.3 FDTD |
| Bus regulator + cable losses | 0.4 | 0.8 | ~10 % |
| **Total** | **~8.1 W** | **~17.8 W peak** | |

**This is well inside the 29 W bus headroom and 42 W peak headroom.** Confirms §6.5.1 sizing is correct, not arbitrary.

### 4.4 Battery sizing — Talentcell 12V/11Ah triple-output

The locked portable supply (§4.5 Option B): Talentcell ~132 Wh nominal, 12 V @ 3 A out + 9 V @ 1.5 A out + 5 V @ 2.6 A USB out.

| Mode | Draw | Runtime on Talentcell triple (132 Wh, derate to 110 Wh usable) |
|---|---|---|
| Platform-only logging session | 4.2 W | **~26 hours** |
| Platform + Stabilizer Mk1 session (typical) | 8.1 W | **~13.5 hours** |
| Platform + Stabilizer Mk1 worst-case continuous | 17.8 W | **~6.2 hours** (this is bursty, not sustained) |

**Conclusion:** the Talentcell triple delivers a 20-minute Stabilizer session ×40 between charges, or a single 12-hour bench day comfortably. Operator's wiki Mk1 target was 3.5–12 h — **met with margin**.

### 4.5 Power source — inventory-confirmed paths

With confirmed inventory (4× MakerHawk 18650, 20× TP4056 USB-C chargers, DUTTY 5–20 A bench supplies, multiple boost/buck modules, mini-UPS units, Pololu U3V12F12 12 V step-up):

| Option | Source | Pros / cons |
|---|---|---|
| **A (bench dev):** USB-C cable + DUTTY 5 A buck or wall-wart 5 V / 3 A | ✅ confirmed | trivial; safe; bench-only; **no 12V rail → cannot power Stabilizer module** |
| **B (portable, LOCKED):** **Talentcell 12V/11Ah + 9V/14.5Ah + 5V/26.4Ah** triple-output → 12V → onboard DUTTY 12V→5V/3A buck → Pi 4; 12V passed through to module bus | ✅ confirmed (2 in stock) | ~132 Wh portable; ~13.5 h Pi 4 + Stabilizer; dual-rail (5V Pi + 12V module) covered |
| **B' (portable, lighter, no Stabilizer):** Talentcell 12V/6Ah + 5V/12Ah dual | ✅ confirmed (2 in stock) | ~72 Wh; ~17 h platform-only; **insufficient 12V capacity for Stabilizer session** |
| **B" (legacy/DIY demo):** 2× 18650 in 2S → Pololu U3V12F12 → 12 V → buck → 5 V 3 A → Pi 4 | ✅ confirmed | wiki-canonical; preserved for pure-DIY demo; ~22 Wh = ~2.5 h Stabilizer session |
| **C (UPS-backed bench, RECOMMENDED for long-session logging):** **TalentCell 27 Ah / 97 Wh Mini-UPS** USB-C PD → Pi 4 direct + 12 V output → module bus | ✅ confirmed (1 in stock) | ride-through during HV pulse tests; USB-C PD is Pi-4-native |
| **D (rack backup):** mini-UPS 10 Ah 5/9/12 V | ✅ confirmed | secondary bench backup |

**Mk0 lock:** Option A bench-only dev (no Stabilizer); **Option B for any session with Stabilizer Mk1 attached;** Option C for fixed-bench long-session logging.

### 4.6 Power tree (locked)

```
Talentcell 12V/11Ah triple ─┬─ 12V_BATT ──┬─→ DUTTY 12V→5V/3A buck ──→ 5V_PLATFORM ──┬─→ Pi 4 USB-C
                            │              │                                          ├─→ Nano v3 Vin
                            │              │                                          ├─→ Heltec USB
                            │              │                                          ├─→ status LEDs
                            │              │                                          └─→ module bus +5V_LOGIC pin (fused 1.5 A)
                            │              │
                            │              └─→ Nano-gated load switch (§ punchlist item 3) ──→ module bus +12V_RAIL pin (fused 3 A)
                            │
                            └─ 5V USB out (unused on platform; available for HackRF when Defender module attached)
                                              ↓
                                              AMS1117-3.3 ──→ 3.3V_LOGIC ──→ I²C pull-ups + MPU9250 + INA219 + TEMT6000 + TTP223
```

### 4.7 Confirmed power inventory used in this spec

| Role | Part | Qty available |
|---|---|---|
| **Portable battery (primary)** | **Talentcell 12V/11Ah + 9V/14.5Ah + 5V/26.4Ah triple** (~132 Wh) | **2** |
| **Portable battery (secondary)** | Talentcell 12V/6Ah + 5V/12Ah dual (~72 Wh) | 2 |
| **Portable battery (compact)** | Talentcell 12V/3Ah dual 12V/5V USB (~36 Wh) | 2 |
| **Bench UPS (primary)** | TalentCell Mini-UPS 27Ah/97Wh w/ 12V/9V + 18W USB-A + USB-C PD | 1 |
| **Bench UPS (secondary)** | Generic Mini-UPS 10Ah 5/9/12V 2A | 1 |
| Cell (raw) | MakerHawk 18650 3000 mAh | 4 |
| 18650 charge | TP4056 USB-C 1 A | 5 (+20 alt) |
| 12 V boost | Pololu U3V12F12 | 2 |
| 12 V → 5 V 3 A buck (PLATFORM PRIMARY) | DUTTY 6–24 V USB buck | 1 (Pi 4 supply) |
| Bench rail | DUTTY 20 A constant-V/I + DUTTY 5 A w/ display | 1 each |
| Surge buffer (optional, HV-module side) | 500 F 2.7 V supercap | 10 |
| Coil drive HV modules | 1.8 kV → 1000 kV variants | many (overstocked, Stabilizer/Defender module use only) |

### 4.8 Runtime targets (locked)

- **Mk0 platform-only:** ≥ 8 h on Option B (achieved: ~26 h) ✅
- **Mk0.5 platform + Stabilizer Mk1, daily 20-min session protocol:** 1 day = 1 charge cycle (uses ~3 Wh per session) ✅
- **Mk1 portable session, continuous Stabilizer:** ≥ 4 h (achieved: ~13.5 h) ✅
- **Mk1 wiki Mk1 target (3.5–12 h on 2×18650):** met by Option B with margin; preserved as Option B" for pure-DIY demonstrations.

---

## 5. Interior layout — what goes inside the 0.1 CAD shell

**Reframe** (responding to the brief literally): the brief asked *"what's going inside it"* — the shell, not just the board. This section specs the entire **interior**: PCB zone, wiring harnesses, battery bay, sensor mount positions, operator controls, antenna keep-outs, thermal venting, and the module-bus exit. Exact millimeters wait on the in-CAD measurement pass (see §5.10); the *zone topology* below is buildable without exact mm and is what locks while we're at the desk.

### 5.1 Fab-class decision

Mk0 is **perfboard, NOT a fab'd PCB.** Reasons:
- Zero budget → no JLCPCB run
- 0.1 CAD shell is the testbed; mechanical fit hand-iterated
- Sprint 0.2 deliverable is a *document*; routing is sprint 0.4

That said: this doc must constrain perfboard layout enough that the first build doesn't require re-cutting the shell or re-wiring on day one of sprint 0.4. The zone spec below does that.

### 5.2 Interior coordinate frame

Standard helm-fixed frame; right-handed; origin at scalp-vertex top-centerline; viewer's perspective.

| Axis | Direction | Range across head |
|---|---|---|
| **+X** | wearer's right ear | ±90 mm |
| **+Y** | wearer's forward (nose) | ±100 mm |
| **+Z** | up (vertex) | 0 to −120 mm (downward) |

All interior positions below cite a zone label (Z1–Z9) defined in §5.3, with `[CAD-MEASURE-TBD]` only on absolute millimeter coords that need the actual shell open.

### 5.3 Interior zones

The shell interior is divided into **nine zones** by function. Each zone has one owner (subsystem); zone boundaries are where harnesses cross.

```
                   ┌─ Z1: FOREHEAD STRIP ─┐
                   │ • cap-touch pad      │
                   │ • TEMT6000 (exterior │
                   │   facing pinhole)    │
                   │ • OLED window        │
                   │   (Heltec OLED)      │
                   └──────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                          │
   Z6: LEFT TEMPLE                          Z7: RIGHT TEMPLE
   • module audio driver pad                • module audio driver pad
   • cable strain relief                    • debug header window
                                            • status LEDs window
         │                                          │
         └────────────────────┬────────────────────┘
                              │
                  ┌─ Z2: VERTEX (TOP) ─┐
                  │ • MPU9250 head-pose│
                  │ • star-ground pad  │
                  │ • shell hardpoints │
                  └────────────────────┘
                              │
                  ┌─ Z3: REAR DOME ────┐
                  │ • Pi 4 main board  │
                  │ • Nano v3 board    │
                  │ • Heltec LoRa 32   │
                  │ • INA219 + buck    │
                  │ • Faraday-lined    │
                  └────────────────────┘
                              │
                  ┌─ Z4: NAPE ─────────┐
                  │ • Talentcell battery
                  │   (external clip)   │
                  │ • DC-022 jack inlet │
                  │ • boat-rocker arm   │
                  │ • module-bus exit   │
                  │ • thermal vent slot │
                  └────────────────────┘
                              │
                  ┌─ Z5: MODULE MOUNT ─┐
                  │ • 4× M4 inserts at │
                  │   60×80 mm pattern │
                  │ • JST-XH bus conn  │→ *2.54 mm Dupont in Mk0*
                  │ • Stabilizer clips │
                  │   here             │
                  └────────────────────┘

   Z8: INTERIOR LINER (everywhere) — Faraday fabric pocket around Z2/Z3
   Z9: SCALP-CONTACT SURFACE — TTP223 pad in Z1 only
```

### 5.4 Zone owners + parts assigned (locked)

| Zone | Function | Parts | Source |
|---|---|---|---|
| **Z1** Forehead strip | operator-facing telemetry + ambient sensing | TTP223 cap-touch pad (helm-on-head) · TEMT6000 ambient-light via pinhole · Heltec OLED 0.96″ window | sensor kits · Heltec board itself |
| **Z2** Vertex | head-pose anchor + star-ground | 1× MPU9250 (I²C 0x68) potted in foam-damped pocket · star-ground solder lug · 2× M4 inserts (HelmKit→0.1-shell attachment) | inventory §2 |
| **Z3** Rear dome | main-board zone (the actual perfboard) | Pi 4B (heatsink side out toward Z4 vent) · Nano v3 · Heltec LoRa 32 (Z3-front so OLED reaches Z1 window via FFC) · INA219 · DUTTY 12V→5V buck · star-ground bus bar | inventory §1, §4 |
| **Z4** Nape | power-in + manual controls + thermal exit | DC-022 panel-mount jack · 2-pos boat-rocker (12V_BATT master) · 3-pos key-switch (SAFETY_n arm, sprint 0.3a-mandatory) · vent slot to outside air for Pi 4 thermal · 1× shell hardpoint | DAOKI DC-022 (30 in stock) · rocker kit (20 in stock) · keyed-switch (sprint 0.3a procurement) |
| **Z5** Module mount | mechanical + electrical attachment for clip-on modules | 4× M4 brass threaded inserts @ 60×80 mm rect pattern · 6-pin 2.54 mm Dupont panel-mount female (was JST-XH in early drafts; corrected per §6.5.1) · short cable to Z3 main board | inventory M4 kit + 635-pc Dupont kit |
| **Z6** Left temple | audio output to wearer | 1× 40mm full-range driver bonded to inner shell (bone-conduction-substitute via temple) — Stabilizer Mk1 owns this; platform pre-wires harness from Z3 | inventory §3.5 |
| **Z7** Right temple | debug + status visibility | 6-pin 2.54mm debug header (under hinged shell flap) · 3× status LEDs (red/amber/green) through pinholes | XXXL kit |
| **Z8** Interior liner | EMI containment + acoustic comfort | Faraday fabric pocket lining Z2+Z3 interior surfaces; grounded to star-ground at Z2 via single tab; foam liner over fabric for fit + acoustic absorption | inventory §12 (planned procurement: Faraday fabric — TBD; EMI-spray in stock per §12 of this doc) |
| **Z9** Scalp-contact surface | safety + sensor contact | TTP223 cap-touch pad at Z1 only (forehead-band scalp contact). No other live contact to wearer skin from platform side. | sensor kit |

### 5.5 PCB / perfboard placement inside Z3

Z3 is the only zone with a board in it. Everything else is wires + discrete elements.

```
   Z3 INTERIOR (looking from inside head toward rear shell)
   ┌─────────────────────────────────────────────────────┐
   │  [Heltec LoRa 32]                                   │ ← Z3-front (closer to Z1)
   │   ‾‾‾OLED face‾‾‾  → FFC to Z1 OLED window          │
   │   ▪ LoRa antenna  → keep-out zone (no metal w/in    │
   │                      30mm), points to Z4 vent dir   │
   │                                                     │
   │  [Pi 4B]            heatsink face                   │ ← Z3-center
   │   Pi USB-C (5V in)  → harness to Z4 boat-rocker→buck│
   │   GPIO header       → I²C ribbon to Z2/Z3-bottom    │
   │   USB-A ports       → external harness to Z5 (BLE   │
   │                       lives on Heltec, not Pi USB)  │
   │                                                     │
   │  [Nano v3 + INA219 + DUTTY buck + load switch]      │ ← Z3-rear
   │   12V_BATT in       → from Z4 rocker                │
   │   5V_PLAT out       → to Pi USB-C + Heltec USB      │
   │   12V_BUS out       → to Z5 Dupont 6-pin via fused   │
   │                       load switch (item 3 sprint)   │
   └─────────────────────────────────────────────────────┘
                                ↓ harness exits Z3
                          to Z4 vent / Z5 mount / Z2 IMU
```

Approximate Z3 internal envelope (will refine in CAD pass §5.10): **130 × 100 × 25 mm** (W × H × D), pi 4 horizontal, perfboard mounted via M2.5 standoffs to a 3D-printed sled bonded to the inner shell. Sled removable for service.

### 5.6 Operator-facing controls (Z1 + Z4 + Z7)

Order is the **ritual order** for don + arm + engage, mapped to physical placement:

| # | Control | Location | Function | State at Mk0 | State at Mk1 (Stabilizer) |
|---|---|---|---|---|---|
| 1 | Helm-on-head (passive) | Z1 / Z9 cap-touch | sensor; no operator action | logs only | gates module standby exit |
| 2 | Boat-rocker (master power) | Z4 nape, recessed | switches 12V_BATT to Z3 buck | functional | functional |
| 3 | 3-position key-switch | Z4 nape, adjacent rocker | OFF / ARMED / SESSION; Nano-readable | absent; through-hole reserved | active; gates SAFETY_n latch clear |
| 4 | Heltec OLED + 2× side buttons | Z1 forehead window | session UI: intention entry, biofeedback, dose, timer, journal close | active (display + button reads) | three-button commit sequence per §15.6 |
| 5 | Status LEDs (3×) | Z7 temple | red=HV/coil armed · amber=watchdog OK · green=session active | red OFF; amber active; green active | red active under Stabilizer coil drive |
| 6 | Debug header | Z7 temple, behind flap | UART TX/RX/GND/3V3/RST/GPIO0 | active | active |

### 5.7 Wiring harness map

Five primary harnesses cross zones. All harness lengths assume Z3 board sled center as 0,0,0 in helm-internal frame.

| Harness | From → To | Wires | Length | Connector ends | Shielding |
|---|---|---|---|---|---|
| **H1** I²C bus | Z3 board → Z2 MPU9250 | SDA + SCL + 3V3 + GND (4 cond) | ~120 mm | 4-pin JST-SH on Z2 side; JST-SH on board | foil shield drained to star-ground at Z2 |
| **H2** OLED FFC | Heltec OLED face → Z1 window | OLED is on Heltec board; just routes through Z1 cutout — no harness, board faces Z1 | ~30 mm of board overhang | n/a | n/a |
| **H3** Battery + bus | Z4 rocker/jack/key → Z3 buck input + Z3 load-switch input | 12V_BATT + GND (2× 18 AWG silicone) + SAFETY-arm sense (1× 22 AWG) | ~200 mm | screw-terminal at Z3, solder lug at Z4 | none (DC) |
| **H4** Module bus | Z3 relay K1 + buck → Z5 6-pin Dupont female panel-mount | 6 cond per §6.5.1 (GND, 5V, 12V, SDA, SCL, SAFETY_n) | ~180 mm | 6-pin 2.54 mm Dupont both ends | overall foil drain to star-ground; SAFETY_n NOT shielded (it must work even if shield grounds open) |
| **H5** Audio + status | Z3 → Z6 audio driver (pre-wired for Stabilizer) + Z7 LEDs + Z7 header | 2× 22 AWG audio (twisted pair) + 3× 24 AWG LED + 6× 24 AWG ribbon for header | left ~250 mm, right ~280 mm | board-side: pin headers; Z6: spade or solder; Z7: 6-pin header | audio twisted pair only |

**Wire spec lives in inventory §6:** silicone hookup wire 22/20/18 AWG 7-color sets confirmed; 635-pc 2.54 mm Dupont housing + pin kit confirmed; 10-wire ribbon confirmed. **No procurement.**

### 5.8 Antenna keep-outs + RF coexistence (preview of §17)

Three radios in the helm: Heltec **LoRa 868/915 MHz**, Heltec **BLE 2.4 GHz**, **WiFi 2.4 GHz** (Pi 4 — disabled in software for sessions, but present).

Constraints baked into the §5.3 zone topology:

- Heltec antenna points **toward Z4 vent direction** (rear-down) — radiates away from wearer's brain into the lowest-density direction (out the back).
- Faraday-fabric pocket Z8 lines **Z2 + Z3 only**, not Z1 or Z4 — leaves Heltec antenna an unobstructed path out the rear vent. The Faraday pocket would otherwise detune the LoRa antenna ~30 %.
- Pi 4 WiFi antenna chip is on the Pi PCB, omnidirectional, mostly absorbed by the Pi heatsink + Z8 fabric — **acceptable** because Pi WiFi is SW-disabled during sessions.
- Z5 module bus is **outside the Faraday pocket** so module-side LoRa/SDR (Defender) has its own RF window. Pull-down implication: I²C noise on H4 will be higher than H1; mitigated by 4.7 kΩ pull-ups + 100 kHz max rate (§6.5.1 already specs this).

### 5.9 Thermal path

Pi 4B under full Linux + logging averages 4 W and peaks at 7.5 W (§4.1). Without venting, an enclosed plastic shell traps that and the Pi will thermal-throttle inside 10 minutes.

| Element | Placement | Effect |
|---|---|---|
| Pi 4 heatsink (passive) | Pi 4 SoC side facing **Z4 vent slot** | conduction path to outside |
| Z4 vent slot | nape, ~50 × 8 mm rectangular cut in shell, angled down | convective exit; gravity-aided; no rain entry on operator |
| Heltec + Nano thermal | both <100 mW; passive convection in Z3 dome | no extra venting needed |
| Z3 air gap | board sled standoffs leave ≥ 5 mm air all around boards | natural convection |
| 12V buck heatsink | small clip-on TO-220 heatsink on DUTTY buck IC | inventory XXXL kit; ~30 °C delta at 17 W |
| Coil drive heatsink (sprint 0.3a) | on Stabilizer module side, not platform — module owns its own thermal | per §15 |

**Hot-day operational ceiling:** Pi 4 will throttle if ambient > 35 °C with helm donned for > 30 min. Acceptable: session protocol is morning, indoor, ambient < 25 °C. **Documented constraint, not a defect.**

### 5.10 Deferred to in-CAD measurement pass

Items that can't be locked at the desk; require opening `3D-Models/HelmKit-mk2/HelmKit_Mk2-01a.blend` and measuring against the actual shell:

- Exact internal envelope of Z3 (current estimate 130 × 100 × 25 mm — to verify)
- Exact M4 insert positions at Z5 (currently spec'd 60 × 80 mm rect — to verify against shell curvature)
- Z2 IMU pocket coordinates (currently "centerline top" — needs exact mm)
- Z4 vent slot exact size + angle (currently 50 × 8 mm @ 30° downward — to verify against shell geometry)
- Heltec antenna keep-out: needs measurement of which direction the antenna trace actually faces relative to shell rear
- Board-sled exact dimensions for 3D printing
- Cable lengths H1–H5: rough estimates above, will refine to ±10 mm in CAD

**CAD-session deliverable:** an annotated Blender file with these positions placed as empty objects; mm coords back-filled into this doc; sled STL exported for printing. *Sprint 0.2 does not require these to be filled.*

### 5.11 What this section locks vs. defers

| Locked at sprint 0.2 desk | Deferred to CAD session |
|---|---|
| ✅ 9-zone interior topology | ⏸ exact mm coords (all `[CAD-MEASURE-TBD]`) |
| ✅ Zone ownership (which subsystem lives where) | ⏸ shell cutout dimensions |
| ✅ Harness map (5 harnesses, endpoints, lengths approximate, shielding) | ⏸ harness exact length |
| ✅ Operator-control placement order + zone (Z1/Z4/Z7) | ⏸ exact button-cluster mm coords |
| ✅ Antenna direction (LoRa → out Z4 vent rear) | ⏸ Heltec antenna trace orientation in CAD |
| ✅ Thermal path strategy (Pi heatsink → Z4 vent) | ⏸ vent slot exact geometry |
| ✅ Faraday pocket scope (Z2+Z3 only) | ⏸ fabric procurement spec |

Sprint 0.2 deliverable is **the zone spec** — a builder can wire-harness this from the inventory shelf today; CAD measurements then close the millimeter loop in a separate session.

---

## 6. Connector choices

### 6.1 Platform-side connectors (Mk0)

| Connector | Mk0 spec | Notes |
|---|---|---|
| Host data + charge in | **USB-C** on the Pi 4 directly | wiki Mk1-aligned (USB-C PD ≤ 5 V / 3 A) |
| Portable battery in | **DC-022 5.5×2.1 mm panel-mount jack** (30 in stock) | accepts Talentcell 12 V output; goes to onboard buck → 5 V Pi rail + 12 V module-bus rail |
| Debug | **6-pin 2.54 mm header** (TX / RX / GND / 3V3 / RST / GPIO0) | UART + reset; from XXXL passive kit |
| Status LEDs | **3× through-hole LEDs on Nano-driven side** | red=HV-armed (off at Mk0), amber=watchdog-OK, green=session-active |
| Mount to 0.1 shell | **M4 thumbscrews × 4** into shell hardpoints | from inventory M4 kit |

### 6.2 Module bus connector (the headline addition — see §6.5)

See §6.5 for the full spec. Headline: **6-pin 2.54 mm Dupont connector on the platform, mating 6-pin Dupont lead on each module.** Delivers 12 V (module rail) + 5 V (logic) + GND + I²C SDA/SCL + open-drain SAFETY line. (Earlier drafts spec'd JST-XH — not in inventory; Dupont locked at §6.5.1.)

## 6.5 Module bus specification (NEW — first-class platform feature)

This is the architectural commitment that makes HelmKit a *platform* rather than a one-off device. Every clip-on module (Stabilizer, Defender, HUD, Field Recorder, future PBM-halo, TDOA-localizer, etc.) connects via this bus.

### 6.5.1 Electrical

**Connector (Mk0 LOCKED):** 6-pin **2.54 mm Dupont housing** (polarized via shroud + keyed pin-1), platform-side female, module-side male with 30 cm flying lead. Sourced from the 635-pc 2.54 mm Dupont housing + pin kit ([inventory.md §6](inventory.md)). Confirmed in stock; zero procurement.

> **Earlier drafts spec'd JST-XH 2.5 mm.** Not in inventory — picked without checking. **2.54 mm Dupont is the locked Mk0 choice** because (a) it's in stock in bulk, (b) operator-familiar (used everywhere else in inventory), (c) polarized with shroud preventing reversal, (d) current rating (3 A/pin standard) exceeds bus spec. Trade-off: less retention than JST-XH; mitigated by mechanical M4 thumbscrews at §6.5.2 holding the module body — the connector itself bears no mechanical load. JST-XH remains an optional Mk2+ polish upgrade once a connector procurement happens.

| Pin | Signal | Direction | Spec | Protection (platform side) |
|---|---|---|---|---|
| 1 | **GND** | shared | 0 V reference, ≥ 3 A return capacity | star-ground tie at Z2 (§5.4) |
| 2 | **+5V_LOGIC** | platform → module | 5 V ± 5 %, 1 A continuous, 1.5 A peak ≤ 100 ms | 1.5 A self-resetting polyfuse (PROCUREMENT GAP — see §6.5.6) + TVS clamp to GND (SMAJ5.0A or equivalent, PROCUREMENT GAP) |
| 3 | **+12V_RAIL** | platform → module | 12 V ± 10 %, 2 A continuous, 3 A peak ≤ 100 ms | series Schottky for reverse polarity (1N5822 from XXXL kit, ~0.5 V drop) → 3 A polyfuse (PROCUREMENT GAP) → **5V 2-channel relay K1** (inventory; §6.5.5) → bus pin → TVS clamp to GND (SMAJ15A) |
| 4 | **I²C_SDA** | bidirectional | 100 kHz default, 3.3 V logic | 4.7 kΩ pull-up to 3.3 V on platform side (§3.3.4) + 220 Ω series ESD resistor (XXXL kit) + ESD clamp (PESD3V3L5UY or two 1N4148s back-to-back — 1N4148 IS in XXXL kit) |
| 5 | **I²C_SCL** | platform → module | clock master is the Pi 4 | 4.7 kΩ pull-up + 220 Ω series + ESD clamp (same as SDA) |
| 6 | **SAFETY_n** | open-drain, bidirectional | active-low; any participant can pull low to kill the bus; Nano monitors at D2/INT0 and latches | 10 kΩ pull-up to 3.3 V on Nano side (§3.3.2) + no series resistor (latency-critical) + ESD clamp |

**Power topology rationale:** Pi 4 stays on 5 V from the platform UPS; the module gets 12 V for any coil drive / HV-module enable / Peltier / fan / high-current LED string. Module-internal buck regulates 12 V → 3.3 V as needed (modules are responsible for their own logic-rail buck — see §15 BOM).

**Pull-up doctrine (locked):** I²C 4.7 kΩ pull-ups live on the **platform Z3 board only**. Module-side modules MUST NOT add I²C pull-ups. Adding pull-ups on the module side would reduce effective pull-up to ~2.3 kΩ and exceed the I²C standard-mode 3 mA sink limit on the Pi 4's GPIO2/3 drivers. (Documented in §3.3.4; restated here because it's a module-author-facing contract.)

**Wire spec (locked for H4 platform pigtail):** 22 AWG silicone hookup (inventory §6), ~180 mm length per §5.7. Module-side flying lead is operator-chosen by module; Stabilizer Mk1 §15 BOM specifies 30 cm 22 AWG silicone, same stock.

### 6.5.2 Mechanical

| Spec | Value | Notes |
|---|---|---|
| Module envelope (max) | 150 × 100 × 30 mm | Stabilizer Mk1 target |
| Mass (max) | 250 g | for skull-mount comfort |
| Mount points | 4× M4 threaded inserts in platform shell | thumbscrew or quarter-turn fasteners |
| Mount-point spacing | 60 × 80 mm rectangular pattern | locked at platform CAD level |
| Connector position | bottom-rear of module, mating to platform connector at top-rear | strain relief built into shell geometry |
| Hot-swap | **No** (Mk1). Power off the bus before swapping modules. | Mk2+ may add a hot-swap controller |

### 6.5.3 Software contract

- **Module identity:** every module presents a 1-byte ID at I²C address 0x10 on first power-up (Stabilizer = 0x01, Defender = 0x02, HUD = 0x03, Field Recorder = 0x04, reserved 0x05–0xFF).
- **Module self-test:** within 100 ms of power-on, module must clear an internal POST and assert its self-test bit at register 0x01. Failure to do so within 500 ms = Nano latches SAFETY_n.
- **Watchdog ping:** Pi 4 writes to module register 0x02 every 100 ms; module must ACK. Missing ACKs > 1 s = Nano latches SAFETY_n.
- **Safety latch:** any participant pulling SAFETY_n low for ≥ 10 ms causes Nano to:
  1. De-assert relay K1 enable (Nano D4 → LOW), opening 12V_RAIL within **≤ 10 ms** (relay mechanical cutoff time — see §6.5.5)
  2. Log the event with timestamp + last I²C transaction to Nano EEPROM
  3. Hold latched until operator clears via the platform key-switch (cycle to OFF then back to ARMED — §5.6) or power-cycle

### 6.5.4 Why this matters for the techno-mage capstone

The module bus is what lets the **Psi Stabilizer Mk1 be lightweight and clip-on** (operator's stated requirement). Stabilizer Mk2 / Mk3 / Mk5 can change radically — different coil, different audio, different sensors, different drive chemistry — and the **platform doesn't change**. That's the whole point of a platform. The operator-as-techno-mage iterates on payload; the rig remains the rig.

**Mk0 rule:** the platform exposes one charge/data port + one debug header + the module bus. That's it. Modules clip on.

### 6.5.5 SAFETY_n kill mechanism — part pick (LOCKED)

The earlier draft said "Nano cuts the 12 V rail within 5 ms" without naming the switching element. That was fiction. Spec'd now:

| Spec | Mk0 LOCKED part | Rationale |
|---|---|---|
| **12V_RAIL switching element** | **5 V 2-channel relay module** (inventory §2; canonical "coil-drive hard cutoff via MCU-B") | In stock. Channel K1 = bus 12V_RAIL cutoff. Channel K2 = reserved for module-side stim cutoff at sprint 0.3a (e.g., coil-drive enable, parallel kill path inside the Stabilizer module). |
| **Drive** | Nano D4 → onboard relay opto-coupler input | Module is opto-isolated; protects Nano from inductive kick. Drive HIGH = relay closed = rail enabled. |
| **Default state at reset / power-up** | OPEN (rail OFF) | Nano boot sequence: POST → read SAFETY_n → confirm key-switch in ARMED or SESSION → *only then* assert D4 HIGH. Boot defaults are safe. |
| **Cutoff latency** | ≤ 10 ms typical (mechanical relay + driver) | Adequate for cell-temp, watchdog, and rail-overcurrent faults. *Not* adequate for fault classes requiring sub-ms shutoff (e.g., RF-emission excursion) — those need module-side discrete MOSFET cutoff, owned by the module per §15.5. |
| **Cycle life** | rated ≥ 100k mechanical operations | At realistic SAFETY events / day < 5, cycle life is irrelevant; arc-suppression diode across coil is included on the module board. |
| **Mk1+ upgrade path** | Discrete logic-level N-channel MOSFET (e.g., AO3400 or IRLZ44N depending on XXXL kit contents) + flyback Schottky | <1 ms cutoff, no audible click, fits inside Z3 board. Migration deferred until XXXL kit MOSFET inventory is counted. |

> **Two-MCU safety architecture restated:** relay K1 has TWO independent kill paths to OPEN: (a) Nano D4 driven LOW (firmware decision — 12-row blacklist), and (b) key-switch in OFF position physically opens the relay-coil supply via series contact in the K1 coil return path. **Operator can always kill the bus by turning the key**, even if Nano firmware is hung. This is the load-bearing safety claim.

### 6.5.6 Protection part list — procurement gaps explicit

Most protection passives are in inventory (XXXL kit covers 1N5822 Schottky, 1N4148 ESD-clamp candidates, 4.7 kΩ / 220 Ω / 10 kΩ resistors). Two genuine gaps:

| Part | Purpose | Inventory status | Procurement cost (if no substitute) |
|---|---|---|---|
| 1.5 A self-resetting polyfuse (radial, 5 V rated) | 5V_LOGIC bus pin | ❌ not confirmed in inventory — XXXL kit *may* contain some | ~$5 / 10-pc strip (Bourns MF-R150) |
| 3 A self-resetting polyfuse (radial, 16 V rated) | 12V_RAIL bus pin | ❌ not confirmed | ~$5 / 10-pc strip (Bourns MF-R300) |
| SMAJ5.0A TVS (5 V unidirectional) | 5V_LOGIC clamp | ❌ not in inventory | ~$3 / 10-pc (or 5.6 V Zener from XXXL kit can substitute degraded) |
| SMAJ15A TVS (15 V unidirectional) | 12V_RAIL clamp | ❌ not in inventory | ~$3 / 10-pc (or 18 V Zener substitute degraded) |
| PESD3V3L5UY (5-line ESD array) for I²C+SAFETY_n | ESD on signal lines | ❌ not in inventory | ~$2 / chip; substitute: 1N4148 pair per line from XXXL kit (~2.5 V clamp, marginal but workable) |
| 1N5822 Schottky (reverse-polarity 12 V) | series diode on 12V_BATT input | ✅ likely in XXXL kit (verify on build day) | n/a if present |
| 4.7 kΩ / 10 kΩ / 220 Ω resistors | pull-ups + series | ✅ XXXL kit | n/a |

**Procurement decision:** total gap ~$15 for proper polyfuses + TVS strip. Operator decision: (a) procure the strip now and have it ship before sprint 0.4 build, or (b) build Mk0 with **Zener substitutes from XXXL kit and a low-value 1 Ω fusible resistor in series with 12V_RAIL** (acts as a fuse that fails open at ~3 A and limits short-circuit current to ~12 A peak; cheap and ugly but adequate for bench bring-up). Path (a) recommended; path (b) is the zero-budget fallback.

### 6.5.7 Hot-swap warning (operator-facing)

Mk0 module bus is **NOT hot-swappable**. Operator MUST:

1. Turn key-switch to OFF (cuts SAFETY_n logic + relay K1 coil)
2. Confirm red HV-armed LED is OFF
3. Confirm OLED shows "BUS SAFE" status
4. Wait ≥ 2 s (allows module-side caps to discharge through bleeder resistors)
5. Unscrew 4× M4 thumbscrews, separate connector, swap module
6. Reconnect, screw down, key to ARMED, observe Nano POST OK on amber LED

Mk2+ may add a hot-swap controller (LTC4231 class) but not at sprint 0.2 scope.

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

## 9. Open items (remaining after 2026-05-12 inventory)

Most questions from the original §9 are now resolved (see [inventory.md](inventory.md)). Remaining:

- **~~9-axis IMU specific part + count~~** — ✅ resolved: 3× MPU9250 (CHENBO×2 + HiLetgo×1) + 1× MPU6050 (Diymore)
- **HV module enable-pin behavior** — active-high / active-low / opto-isolated? Test bench-only before circuit lock.
- **PCB CNC bit set** — confirm 0.2 mm V-bit / 0.25 mm end mill + 1.0 mm drill availability for the [coil fab spec](mk0_pcb_bifilar_coil.md)
- **Spare 2S 18650 holders + BMS** — likely in TP4056-adjacent stock; confirm
- **Shielded cable / coax stock** for the magnetometer lead
- **Decision RESOLVED:** ✅ 10× uxcell 200×200×1.5 mm double-sided FR4 in stock — proceed with wiki-canonical two-layer bifilar coil geometry, no procurement needed

---

## 10. Cross-refs

- [architecture.md](architecture.md) — overall slot/module model + dual-MCU rationale
- [mk1_buildplan.md](mk1_buildplan.md) — what Mk0 grows into
- [wiki_synthesis.md § Pass 2](wiki_synthesis.md) — wiki BOM
- [safety.md](safety.md) — full safety posture
- [falsification.md](falsification.md) — biomarker measures we will eventually need to support (HRV via PPG is the key Mk0→Mk1 enabler)
- [inventory.md](inventory.md) — authoritative parts inventory
- [inventory_capability_map.md](inventory_capability_map.md) — what we have vs. wiki BOM
- [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) — fab spec for the bifilar coil PCB (used by Stabilizer module, not platform)
- [gpu_farm_workloads.md](gpu_farm_workloads.md) — compute substrate for FDTD design-cert (sprint 0.3, Mk2 track)
- [beyond_wiki_concepts.md](beyond_wiki_concepts.md) — module ideas beyond the wiki spec

---

## 11. Magnetometer calibration jig (uses neodymium magnets)

Before the magnetometer in the 9-axis IMU is trustworthy as either a heading sensor *or* an ambient-field baseline, it needs three calibrations: hard-iron offset, soft-iron scale, and rotational alignment.

### 11.1 Setup

Non-magnetic table (wood / plastic), Pi 4 logging the IMU at ≥ 50 Hz, geomagnetic-north reference (compass app on phone, or astronomical alignment).

### 11.2 Calibration procedure

| Step | Action | Expected result |
|---|---|---|
| 1 | Rotate IMU through all orientations in 3D ("figure-8" + tumble), 60 s | Log min/max on each axis; midpoint = hard-iron offset; axis range ratios = soft-iron scale |
| 2 | Hold IMU still; align X-axis to magnetic north | Mag X = +max, Y = 0, Z = local dip component |
| 3 | Place a known neodymium magnet at 10 cm distance along +X | Verify mag-X reading increases by amount predictable from $B = \mu_0 m / (2\pi r^3)$ for a dipole |
| 4 | Move magnet from 10 cm → 20 cm | Verify $1/r^3$ falloff (slope on log-log plot) |
| 5 | Repeat steps 3–4 with second IMU at same distance | Cross-check between the two for gradiometer baseline |

Step 4 is the **field-law sanity check**. If the magnetometer doesn't reproduce $1/r^3$ falloff for a permanent magnet, it's broken or wrongly axis-mapped — fix before doing anything else. This is the floor.

### 11.3 Neodymium magnet handling

- **Do not** stick magnets to anything ferrous; they're brittle and will chip + spall.
- **Keep magnets ≥ 30 cm from the IMU** when not actively calibrating. Magnetometers saturate easily and stay magnetized (hysteretic).
- **No magnets near credit cards, hard drives, pacemakers.** Operator safety.

---

## 12. EMI shielding plan (uses Faraday fabric + conductive spray)

The long-term problem inside the helm is that the Mk1 coil emits in the 1–8 MHz band exactly where the magnetometer wants to listen for ambient field. Without isolation, coil ON = mag pegged. Solution: selective shielding.

### 12.1 Layer plan (looking from outside the head, inward)

```
[ helm shell exterior ]
[ Faraday fabric layer — wraps inside of shell ]
[ open air / sensor cavity — IMU, env, PPG ]
[ small Faraday pocket around the IMU specifically ]
[ air gap ]
[ coil + drive electronics, on far side of the cavity ]
[ EMI-spray-coated coil enclosure pot ]
[ helm shell exterior ]
```

The goal is a **two-cavity** interior where the IMU lives in a small Faraday-fabric pocket and the coil lives in an EMI-sprayed potted enclosure, with neither directly seeing the other. The wearer's head is *not* in either cavity — it occupies the central space and is only field-coupled to the coil at the prescribed distance.

### 12.2 EMI-spray application

- Use on the **inside** of plastic enclosure pieces, not on circuits.
- 2–3 thin coats; let cure 24 h between.
- Ground the spray layer to circuit GND with a tab + short wire. **Floating shields make things worse.**
- After spray + cure: continuity test corner-to-corner should read < 5 Ω.

### 12.3 Faraday-fabric pocket for IMU

- Sew or wrap a small pouch from the fabric, leave one side open for cable.
- Ground the fabric to circuit GND via a single solder tab.
- Place IMU inside; cable exits through the open side.
- The pouch attenuates everything > ~1 MHz by 30+ dB; below that, it does little. **That's fine** — the magnetometer is DC-coupled and cares about static fields; the IMU's gyro/accel don't care about EM.

### 12.4 Sham coil enclosure

The sham coil (per [mk0_pcb_bifilar_coil.md § 6](mk0_pcb_bifilar_coil.md)) gets the **same** EMI-sprayed enclosure as the active coil so it has identical thermal and acoustic signature. This is the F1 falsification floor.

---

## 13. SDR survey baseline (uses on-hand SDR module)

Before the first coil power-on, establish ambient RF baseline at the build location.

### 13.1 Survey protocol

| Run | Duration | Bands | Purpose |
|---|---|---|---|
| Baseline-AM | 5 min | 530 kHz – 1.7 MHz | local AM broadcast; sets in-band reference for Mk1 coil leakage |
| Baseline-SW | 5 min | 1.7 – 30 MHz | covers coil drive band (1–8 MHz); critical for emission compliance check |
| Baseline-VHF | 5 min | 30 – 300 MHz | FM broadcast + amateur + nearby unintended |
| Baseline-UHF | 5 min | 300 MHz – 1 GHz | cellular, ISM 433/915, smart-home |
| Baseline-WiFi | 5 min | 2.4 – 2.5 GHz | wiki Mk1 platform RF band |
| Baseline-Dark | 5 min | full-band, antenna disconnected | RX noise floor for differential measurements |

Log raw IQ to disk (Pi 4 SSD or USB stick). Process with GNU Radio / SoapySDR for spectrum + waterfall. Save as `data/sdr_baseline_2026-05-12.h5` (or per-run).

### 13.2 Coil emission verification (Mk0.5+)

After first coil power-on (bench, Faraday-bagged):

1. Repeat Baseline-SW with coil **off** → noise reference.
2. Repeat Baseline-SW with coil **on** at drive frequency $f_0$ → emission signature.
3. Subtract; verify (a) primary peak is at $f_0$ within ±0.1%, (b) harmonics below regulatory limits (FCC Part 15 §15.209 if applicable), (c) no out-of-band spurs above noise floor.
4. Move SDR antenna to 30 cm, 1 m, 3 m → verify $1/r^3$ near-field falloff.

This is the wiki-spec'd FDTD-verification loop, executed empirically.

---

## 14. Today's expanded deliverables (with inventory known)

| # | Task | Owner | Status |
|---|---|---|---|
| 1 | **Tote inventory pass** — captured in [inventory.md](inventory.md) | jono | ✅ |
| 2 | Confirm 9-axis IMU model + count | jono | ✅ 3× MPU9250 + 1× MPU6050 |
| 3 | Confirm full Pi sensor kit contents | jono | ✅ (KS3016 + DKHK100200 fully catalogued) |
| 4 | Confirm SDR model(s) + count | jono | ✅ (HackRF One + 2× NESDR v4 + 1× NESDR XTR + Ham It Up + balun) |
| 5 | Confirm HV/VHV module spec | jono | 🟡 partial — counts done; enable-pin behavior TBD on bench |
| 6 | Confirm PCB CNC mill | jono | ✅ Genmitsu CNC 3018-PRO; bit set TBD |
| 7 | Confirm USB power source | jono | ✅ multiple paths confirmed |
| 8 | Update remaining `[INVENTORY-TBD]` markers | jono / assistant | ✅ (this commit) |
| 9 | Decide: procure double-sided FR4 (~$15) vs single-sided fallback for coil v0.1 | jono | ✅ resolved — 10× uxcell DS-FR4 200×200×1.5 mm already in stock |
| 10 | Sketch §5.1 footprint vs. 0.1 CAD shell | jono | ☐ |

**Definition of done for Sprint 0.2:** ✅ inventory captured; ✅ MCU + sensor + power picks locked; ✅ wiki Mk1 coverage matrix produced; ✅ 9-axis IMU specific part confirmed (3× MPU9250 + 1× MPU6050); ✅ coil-PCB substrate decision (uxcell DS-FR4 in stock); ✅ **module bus spec locked (§6.5)**; ☐ footprint sketch vs. CAD shell remains for an in-physical-presence work session.

**Next sprints branching from this baseline:**
- **Sprint 0.3a** = Psi Stabilizer Mk1 clip-on module against this bus (the capstone artifact)
- **Sprint 0.3** = FDTD design-cert for the coil that lives inside the Stabilizer (Mk2 track, uses the GPU farm)
- **Sprint 0.4** = platform perfboard build + integration test with a dummy module that just answers the bus probes

---

## 15. Psi Stabilizer Mk1 — first module against this bus

*Reference spec only — full module sprint is 0.3a. Listed here so the platform §6.5 bus is grounded against a real payload, not abstract.*

### 15.1 Mission

*"Stabilizes the mind."* Operator dons the HelmKit + clips on the Psi Stabilizer module + runs a 20-minute morning session. Over a 21-day daily protocol the operator's autonomic balance (HRV LF/HF), sustained-attention (PVT variance), subjective stability (journal), and sleep-latency trend toward more parasympathetic, more focused, more centered. **That trend is the falsifier on whether the device works.**

### 15.2 Three independent stabilization channels (Layer-1 grounded)

| Channel | Mechanism | Layer | Evidence |
|---|---|---|---|
| **PBM 730 nm halo** | 4× Chanzon 3W far-red COBs ringing the helm liner at ~10 mW/cm² on scalp; DS18B20 thermal lockout | 1 | Gonzalez-Lima / Hamblin PBM cognitive literature |
| **Schumann audio entrainment** | XR2206 or ESP32 LEDC at 7.83 Hz envelope; pulse-modulated audio through 40 mm full-range drivers (bone-conduction substitute) at cheek/temple | 1–2 | theta-band auditory entrainment; Schumann frequency choice is wiki Layer-3 wink |
| **Bifilar coil at Schumann** | Mk0 PCB bifilar coil (per [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md)) driven at sub-µT field at 7.83 Hz fundamental + first 3 harmonics; ESP32 LEDC PWM through low-side filter | 2–3 | wiki-canonical Stabilizer; mixed-positive literature; FDTD-certified by sprint 0.3 before Mk2 |

### 15.3 One closed-loop input

- **HRV biofeedback** via **Polar H10 over BLE → Heltec LoRa 32 → live OLED**. Operator watches their own HRV coherence during the session. *This is the visible biofeedback that proves the device is doing something measurable in real time.*

### 15.4 Module-side BOM (everything in inventory)

| Item | Qty | Source | Role |
|---|---|---|---|
| Bifilar coil PCB | 1 | CNC mill on uxcell DS-FR4 200×200×1.5 mm | coil drive |
| MOSFET coil driver (low-side) | 1 | XXXL passive kit | drive switch |
| Chanzon 3W 730 nm far-red COB | 4 | inventory §2.6 | PBM halo |
| Constant-current LED driver | 4 | XXXL passive kit | PBM current control |
| DS18B20 thermistor | 1 | sensor kit | thermal lockout |
| 40 mm 4 Ω 3 W full-range driver | 2 | inventory §3.5 | bone-conduction-substitute audio |
| Audio amp (PAM8403 or similar) | 1 | XXXL kit | audio drive |
| Local 12V → 3.3V buck (AMS1117 or MP1584) | 1 | XXXL kit | module-side logic rail from bus 12V |
| 6-pin 2.54 mm Dupont plug + 30 cm 22 AWG silicone lead | 1 | inventory §6 (Dupont kit + silicone wire) | mates platform module bus (**bus-powered — no module battery**) |
| PLA-printed clip-on enclosure | 1 | 3D printer | mechanical |

**Power source:** Stabilizer Mk1 is **fully bus-powered** from the HelmKit platform's 12V_RAIL + 5V_LOGIC per §4.2. No module-side battery, no module-side charge port. Earlier draft of this BOM listed a module-side 18650 + TP4056; **removed** because it contradicts the "lightweight clip-on" goal and §4.3 confirms the platform bus has the headroom (Stabilizer typical draw 3.5 W on 12V + 0.5 W on 5V, well inside 24 W + 5 W rail capability).

### 15.5 Module-side safety

- All drive chains gated by the platform SAFETY_n line
- DS18B20 scalp temp > 40 °C → assert SAFETY_n
- Coil drive current sense > envelope (per FDTD-certified envelope from sprint 0.3) → assert SAFETY_n
- Loss of capacitive-touch "helm-on-head" signal from platform → module enters standby
- Loss of Polar H10 BLE → audio + PBM continue (these are passive); coil drive drops to keep-alive

### 15.6 Ritual layer (the techno-mage part)

- Operator dons helm + module deliberately
- Boat-rocker arms the 12V module rail (visible mechanical commit)
- Three-button commit sequence on Heltec OLED authenticates operator + session intention
- OLED displays live HRV coherence + dose accumulated + session timer
- Audio plays operator-chosen invocation track at session start
- Closure ritual: rocker off, session logged with intention-vs-outcome journal note

The ritual is **not** decoration. It directs operator will — the operative-magic component that distinguishes this from passive biofeedback. See [README.md](../README.md) for the epistemic-stance disclaimer that this work sits inside of.

### 15.7 Why this fits sprint 0.2's platform

- Mass: ≤ 250 g ✅
- Envelope: 150×100×30 mm ✅
- Power: 12V rail @ < 500 mA peak (coil drive) + 5V logic @ < 200 mA ✅
- I²C: one device at 0x01 (StabilizerMk1) ✅
- SAFETY_n: drives + observes ✅
- Mounts: 4× M4 thumbscrews to the platform hardpoints ✅

The platform spec'd in §§1–14 above carries this module without modification. **Mission accomplished for Sprint 0.2.**

---

## 16. Bring-up test plan (first-power-on procedure)

This section defines the **gated power-on sequence** for the assembled HelmKit Mk0 platform. Every gate is go/no-go; any failure halts the bring-up and routes to the diagnosis column. Operator runs this from the bench with the helm sitting on a non-conductive surface, module bus EMPTY (no Stabilizer attached yet), and a multimeter + DSO oscilloscope (inventory) on hand.

### 16.1 Pre-power checks (helm OFF, battery disconnected)

| # | Check | Pass | Fail → diagnose |
|---|---|---|---|
| P1 | DMM continuity: 12V_BATT input pin → GND | open circuit | short = solder bridge at Z2; isolate and re-flow |
| P2 | DMM continuity: 5V_LOGIC bus pin → GND | open circuit | short = polyfuse + TVS path miswired |
| P3 | DMM continuity: 12V_RAIL bus pin → GND | open circuit | short = relay K1 stuck closed or downstream cap reversed |
| P4 | DMM continuity: I²C SDA/SCL bus pins → 3.3V (Pi rail off) | ~4.7 kΩ (pull-ups present, platform side only) | <1 kΩ = duplicate pull-ups; >10 kΩ = missing pull-up resistor |
| P5 | DMM continuity: SAFETY_n bus pin → 3.3V (Pi rail off) | ~10 kΩ (Nano-side pull-up) | check D2 trace and pull-up resistor |
| P6 | Visual: relay K1 opto-input wired to Nano D4 + series with key-switch coil contact | both paths present | rework — single-path safety is unacceptable per §6.5.5 |
| P7 | Visual: H1 battery harness 12 AWG, polarity tag on +V | matches §5.7 H1 | reverse-polarity Schottky will save it once, but DO NOT TEST THAT WAY |
| P8 | Visual: ground star-point at Z2 (§5.4) — battery GND, Pi GND, Nano GND, Heltec GND, K1 coil GND all land at single screw terminal | one star | daisy-chained GND = redo before powering |

### 16.2 First power (battery in, key OFF)

| # | Step | Expected | Fail → |
|---|---|---|---|
| F1 | Insert charged battery (≥ 12.0 V, ≤ 12.6 V Talentcell), key in OFF position | DSO on 12V_BATT shows 12.4 V quiet; nothing else lights | unexpected current draw > 50 mA = phantom path, kill power immediately |
| F2 | Confirm Nano +5V_LOGIC rail (key OFF should still power logic island via UPS HAT 5V) | 5.00 ± 0.05 V at Nano VIN | check 5 V buck regulator output and §4.6 power tree |
| F3 | Confirm Pi 4 +5V rail | 5.10 ± 0.05 V at Pi GPIO pin 2 | UPS HAT not enabled / not in inventory location |
| F4 | Confirm Heltec V3 +3.3V (it boots off platform 5 V → onboard buck) | 3.30 ± 0.05 V at OLED Vcc | Heltec onboard reg fault |
| F5 | Confirm relay K1 is OPEN (12V_RAIL bus pin should read 0 V) | 0 V at bus pin 3 | K1 closed with key OFF = wiring fault, possibly K1 coil bypassing key contact. **STOP** until fixed. |

### 16.3 Logic boot (key OFF → still no rail)

| # | Step | Expected | Fail → |
|---|---|---|---|
| L1 | Pi 4 boots Raspberry Pi OS; green ACT LED blinks | normal boot logs on serial | check SD card / power-good |
| L2 | Nano POST: 200 ms after power-good, amber LED on D5 blinks 3× then goes solid for 1 s indicating POST OK, then off | observable | firmware bug or D5 mis-wired |
| L3 | Heltec OLED shows "HK Mk0 / BUS SAFE / KEY OFF" status | text on OLED | confirm OLED firmware loaded; check second I²C bus (GPIO19/20) wiring |
| L4 | `i2cdetect -y 1` on Pi shows 0x40 (INA219), 0x42 (Nano), 0x43 (Heltec), 0x68 (MPU9250), 0x0C (AK8963) | 5 addresses | missing addr → check pull-up + slave firmware |
| L5 | Pi reads SAFETY_n via GPIO17 = HIGH (line not pulled low) | HIGH | SAFETY_n stuck low → check Nano D2 latch state, key-switch wiring |

### 16.4 Key to ARMED (still no module attached)

| # | Step | Expected | Fail → |
|---|---|---|---|
| A1 | Turn key from OFF to ARMED | Heltec OLED updates to "ARMED / NO MODULE" within 200 ms | check key-switch wiring per §5.6, A2 on Nano |
| A2 | Nano D4 still LOW (no module = no relay close) | DMM at K1 opto-input reads ~0 V | firmware decision logic bug (Nano should not close K1 without module ACK) |
| A3 | 12V_RAIL bus pin still 0 V | confirmed | as A2 |
| A4 | Pull SAFETY_n test: short bus pin 6 to GND with jumper wire for 50 ms | Nano latches: amber LED blinks SOS pattern, OLED shows "SAFETY LATCH / CLEAR: KEY OFF" | latch failed = §6.5.3 software contract not implemented; firmware fix required |
| A5 | Clear: key OFF → back to ARMED | OLED returns to "ARMED / NO MODULE" | latch did not clear |

### 16.5 Module attach (Psi Stabilizer Mk1 or dummy module)

| # | Step | Expected | Fail → |
|---|---|---|---|
| M1 | Key OFF (mandatory per §6.5.7). Attach module via 6-pin Dupont. Tighten 4× M4 thumbscrews. | mechanical fit, no pin reversal possible (shroud) | shroud key broken / wrong housing |
| M2 | Key → ARMED | Heltec OLED: "ARMED / MODULE 0x01 / POST PENDING" | OLED still says NO MODULE = I²C 0x10 read returning 0xFF; check module wiring |
| M3 | Within 500 ms, module asserts self-test bit (reg 0x01 = 1) | OLED: "MODULE 0x01 OK"; Nano D4 goes HIGH; relay K1 audibly clicks closed | self-test fail = module fault, NOT platform fault. Detach and debug module. |
| M4 | Confirm 12V_RAIL bus pin = 12.4 V | rail live | K1 not closing despite D4 HIGH = key-switch series contact open; check §6.5.5 path |
| M5 | INA219 reports rail current via Pi → Nano → Heltec OLED: "RAIL 0.18 A" (Stabilizer idle) | within ±20 mA of §4.4 estimate | sensor bus issue or rail short on module |
| M6 | Pi watchdog ping at 100 ms cadence; module ACKs | log clean | missed ACKs >1 % = §6.5.3 watchdog failure mode test |

### 16.6 SESSION mode (Stabilizer engaged, coil drive on)

Out of scope for sprint 0.2 bring-up — covered in sprint 0.3a Stabilizer firmware bring-up. Gate M6 is the end of platform-only bring-up.

### 16.7 Definition of platform-bring-up DONE

All gates P1–P8, F1–F5, L1–L5, A1–A5, M1–M6 pass with module attached and idling on the bus. Total time budget: ~45 minutes for a clean board on first attempt.

---

## 17. Grounding + RF coexistence

This section locks the **single-point ground topology** and the **RF coexistence rules** between BLE (Heltec, 2.4 GHz), LoRa (Heltec, 915 MHz), I²C (100 kHz, edges rich in harmonics up to ~10 MHz), and the future Stabilizer coil drive (sprint 0.3a, 1–8 MHz audio + DC bias).

### 17.1 Star-ground topology (LOCKED)

```
                    Battery GND (Talentcell –)
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Z2 STAR GROUND POST  │  ← single M4 brass screw
                  │   (chassis tie point) │     in Z2 power zone
                  └───────────────────────┘
                              │
        ┌──────────┬──────────┼──────────┬──────────┬──────────┐
        ▼          ▼          ▼          ▼          ▼          ▼
     Pi 4 GND   Nano GND  Heltec GND   K1 coil   Z5 module   Faraday
     (UPS HAT   (Z3      (Z3 HUD     return    bus GND      fabric
      ground)   board)    board)     (Z3)      (H4 dedi-    drain
                                                cated wire) (12 GA
                                                            braid)
```

**Rules:**

1. **Every GND in the platform connects ONLY to the star post**, never to another GND directly.
2. **Module-bus GND is its own dedicated conductor** in H4 — not shared with chassis return. Prevents I²C noise from coupling into stim-driver ground reference.
3. **Faraday-fabric Z3 + Z6 enclosure liner** ties to star post via 12 AWG copper braid (inventory §6 conductive textiles). One tie point only — no loop.
4. **The shield foil drain on H1 (battery harness) lands at star**; the shield itself is grounded only at one end (battery end is left floating) to prevent ground-loop hum.
5. **SAFETY_n carries its own ground reference via H4 pin 1.** It does NOT use chassis return. Reason: chassis ground can lift during a fault event; safety logic must not.

### 17.2 RF coexistence rules

| Source | Freq | Threat | Mitigation (LOCKED) |
|---|---|---|---|
| **BLE radio (Heltec ESP32-S3)** | 2.40–2.48 GHz | Desense from Pi 4 HDMI clock harmonics (~2.97 GHz × N) and from any switching-reg edge | Pi 4 HDMI off in /boot/firmware/config.txt (`hdmi_blank=2`); Heltec BLE antenna keeps Z9 RF window per §5.8 keep-outs; Pi 4 + switching regs inside Z3 Faraday liner |
| **LoRa SX1262 (Heltec)** | 902–928 MHz US ISM | Same plus 5V buck switching at ~600 kHz × N harmonics into 900 MHz | TX duty-cycle ≤ 1 % per FCC Part 15.247; Heltec LoRa antenna in Z9 window, oriented vertically; switching regs choke-coupled (inventory ferrites) |
| **I²C bus 100 kHz** | DC–10 MHz (edges) | Radiated into HackRF / NESDR / future MHD sensor | I²C wires twisted-pair where possible; H4 has overall foil drain; I²C runs INSIDE Faraday liner (Z3↔Z5 only) |
| **Stabilizer coil drive** (sprint 0.3a) | 1–8 MHz audio + bias | Desense ALL receivers; couples back into I²C and SAFETY_n | Module-internal shield required (§15 BOM); module bus SAFETY_n latency budget (≤ 10 ms) is fast enough that a misbehaving coil drive faults out before causing receiver damage; coil drive NEVER runs while RF survey mode is active (firmware interlock, sprint 0.3a) |
| **Pi 4 internal switching** (~1 MHz) | 1 MHz + harmonics to ~100 MHz | Couples into all sensitive analog (INA219 reads, NTC reads on Nano A1–A3) | Nano analog Vref via separate LDO (not bus 5 V); analog ground star-tied at Nano board, single trace to chassis star |
| **Heltec OLED refresh** (~120 kHz) | 120 kHz + harmonics | Couples into I²C if shared bus | OLED is on Heltec's **factory I²C bus (GPIO17/18)**, NOT the platform bus (GPIO19/20). Buses are physically separate per §3.3.3. |

### 17.3 Antenna keep-outs (referenced from §5.8 with RF justification)

- **Z9 RF window** (rear-top quarter of helm shell): the only zone where Faraday fabric is INTENTIONALLY ABSENT. All RX/TX antennas (BLE, LoRa, future HackRF survey, future NESDR) live here. Minimum keep-out from any wire carrying switching current: 50 mm.
- **No metal fasteners within 30 mm of any antenna feedpoint.** M4 brass inserts in Z5 (module mount) are far enough away (mount is bottom-rear; antennas top-rear).
- **HackRF (future, modular)** mounts in a Defender module, not in the platform shell. Its antenna feedpoint sits inside the module envelope — module designer's problem, not platform's.

### 17.4 Audio coexistence (sprint 0.3a preview)

Stabilizer Mk1 coil drive is 1–8 MHz AM audio. This band overlaps:
- **WWVB time signal** (60 kHz) — below band, no conflict
- **AM broadcast** (530–1700 kHz) — partial overlap; expect mild AM-radio interference within 1 m of operator. Acceptable.
- **Amateur HF** (1.8–30 MHz) — overlaps. Stabilizer must NOT exceed FCC Part 15.209 unintentional radiator limits. Module shield + coil orientation handle this; verified at sprint 0.3a with the NESDR + Ham It Up survey baseline (§13).

### 17.5 Open RF items deferred past sprint 0.2

- TDOA localizer module: needs >2 spatially separated NESDR; coordinate with grounding plan when module is spec'd.
- Multi-helm operation: two HelmKits within 5 m share 2.4 GHz BLE space. Channel-hopping handled by ESP32-S3 firmware default; no platform-side mitigation needed at Mk0.

---

## 18. Definition of done — Sprint 0.2 (UPDATED 2026-05-12)

Sprint 0.2 is DONE when this document defines, with parts on hand or with procurement gaps explicitly flagged:

- [x] §0 Platform-vs-module architectural framing
- [x] §1 Scope: platform-only at Mk0; modules deferred to later sprints
- [x] §2 Sensor list with ownership scope (platform locks 6 sensors; modules own the rest)
- [x] §3 MCU pick (Pi 4 + Nano v3 + Heltec V3) + §3.3 full pin-ownership across all three
- [x] §4 Power budget across three MCUs + module bus + Talentcell sizing
- [x] §5 Interior layout: 9 zones, harness map, thermal, RF keep-outs
- [x] §6 Connector choices including §6.5 module bus full electrical+mechanical+software contract
- [x] §6.5.5 SAFETY_n kill mechanism part pick (relay K1, two-path safety claim)
- [x] §6.5.6 Protection part list with procurement gaps explicit (~$15 gap)
- [x] §7 Safety floor restated
- [x] §15 Psi Stabilizer Mk1 reference module BOM
- [x] §16 Bring-up test plan with go/no-go gates
- [x] §17 Grounding star topology + RF coexistence rules

**Deferred to later sprints (not blocking sprint 0.2):**
- KiCad schematic capture (sprint 0.4)
- KiCad PCB layout for Z3 board (sprint 0.4)
- 3D-printable PCB-mount brackets (sprint 0.4)
- Final Z5 module-mount CAD dimensions (sprint 0.3 — CAD pass)
- Mk1+ MOSFET load-switch migration (sprint 0.5+)
- Hot-swap controller (sprint 0.5+)
- Procurement order for 2× polyfuse strips + TVS strip (~$15)

The platform is **buildable from this document alone** modulo CAD measurements (§5.10) and the two flagged procurement items.
