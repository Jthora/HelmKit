# Sprint 0.2 — HelmKit Mk0 Circuit Spec (Inventory-Driven)

**Sprint goal:** A *document*, not a board. Define what goes inside the 0.1 CAD shell.
**Hard constraint:** Near-zero cash budget. Build from existing tote inventory. Anything not in the totes is **defer or omit**, not "buy."
**Status:** DRAFT — sections marked `[INVENTORY-TBD]` get filled after today's physical count. Many sections already concretized from operator-stated inventory (2026-05-12). See [inventory_capability_map.md](inventory_capability_map.md).

> **Scope expansion (2026-05-12 inventory):** Operator confirmed Pi 4, Jetson Nano, Arduino Nano v3, 9-axis IMU(s), Pi sensor kit, PCB CNC mill + stock, SDR modules, HV/VHV modules, Faraday fabric, EMI shielding spray, neodymium magnets, ferrofluid all on hand. **This pushes the achievable ceiling from Mk0-sensors-only to Mk0 + Mk1-coil-prefab.** Sprint 0.2 doc now covers both: §§1–10 = Mk0 board; §11–14 = parallel Mk1 prep tasks made possible by current inventory.

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

| Tier | Sensor class | Why it matters | Wiki Mk1 part | Mk0 pick (inventory-confirmed) |
|---|---|---|---|---|
| **Must-have** | 3-axis IMU (accel+gyro) | head pose, motion artifact rejection | MPU6050 / ICM-20948 | ✅ **9-axis IMU module** (operator-stated; specific part TBD — MPU-9250 / ICM-20948 / BNO055 class) |
| **Strong nice-to-have** | 3-axis magnetometer | ambient field baseline; F4-relevant geomagnetic-sensitivity studies | HMC5883L / LIS3MDL | ✅ **integrated on the 9-axis IMU above** |
| **Strong nice-to-have** | Environmental (T/RH/P/VOC) | session-context logging; thermal-safety floor | BME680 | 🟡 **Pi sensor kit** likely contains BME280/680, BMP280, or DHT22 — confirm during inventory |
| **Want** | PPG (heart rate / HRV) | primary biomarker for stabilization studies | MAX30102 | 🟡 **Pi sensor kit** — confirm MAX30100/30102 presence |
| **Want** | Skin-contact electrodes (EEG / GSR) | optional Mk0.5 — needs analog front-end | ADS1299 / AD8232 | ❌ defer; not in scope without analog front-end IC |
| **Optional** | Microphone | ambient audio context | ICS-43434 / MEMS | 🟡 likely in Pi sensor kit (MAX9814 / electret) |
| **Optional** | Ambient light | photic stim sham control + circadian context | TSL2591 / VEML7700 | 🟡 likely in Pi sensor kit (BH1750 / TSL2561) |
| **Bonus** | Magnetometer #2 (gradiometer) | wiki Defender 2× mag pattern | second HMC5883L | ✅ **second 9-axis IMU** mounted ~5 cm offset gives free gradiometer |
| **Bonus** | SDR (RF wideband survey) | wiki Defender survey path | RTL-SDR / HackRF | ✅ **SDR module** on hand (model TBD) — connects to Pi 4 USB |

**Inventory rule:** anything we have ≥1 of goes on the spec at its tier. Anything we have zero of moves to "Mk1 procurement list" and **does not block Mk0**.

---

## 3. MCU pick — inventory-driven

Wiki canonical: STM32F407 (doer) + RP2040 (checker). For Mk0 we use whatever MCU we have **the most of and the best toolchain familiarity with**.

### 3.1 Candidate MCUs to look for in the totes

Listed in rough order of preference for an Mk0 build:

**LOCKED — picks based on operator-stated inventory (2026-05-12):**

- **MCU-A (doer): Raspberry Pi 4.** Hosts I²C bus, USB (SDR + sensors), real-time logging, optional ML inference. Runs Linux; Python + C extensions for the bus + control loops. Headless or HDMI debug.
- **MCU-B (checker): Arduino Nano v3 (ATmega328P).** Small enough to formally audit. Holds the 12-row safety blacklist (see [wiki_synthesis.md § Pass 2](wiki_synthesis.md)) in flash. Independent power monitoring + kill GPIO. Talks to Pi 4 over I²C as a watchdog slave; raises an open-drain SAFETY line on any violation.
- **Heavy compute: Jetson Nano (optional Mk0.5+).** Off-board (in pack, on belt) for SDR DSP, FFT, HRV pipeline, FDTD verification. Connected via Pi 4 ethernet or USB.

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

### 4.1 Power source — Pi 4 changes the calculation

The Pi 4 needs **5 V @ ~1–2 A** continuous (3 A peak under USB load). That's well above what a single 18650 + LDO will deliver cleanly. Options:

| Option | Source | Pros / cons |
|---|---|---|
| **A (recommended Mk0):** USB-C power bank (5 V / 3 A) on belt | likely in tote, otherwise the operator owns several already | tethered to short USB cable; trivially safe; no charging IC needed |
| **B (Mk1 portable):** 2× 18650 in series + buck to 5 V | inventory + buck module | wiki-canonical 2×18650 path; needs buck rated ≥ 3 A and proper BMS |
| **C (bench):** wall-wart 5 V / 3 A USB-C | inventory | bench-only |

**Mk0 lock: Option A** (USB-C power bank, belt-worn, short tether to helm). Defers the BMS/charger design to Mk1 where it belongs.

`[INVENTORY-TBD]` — confirm during pass: USB-C power bank(s), 5 V buck modules, 18650 cells + holders, BMS modules.

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

- Specific 9-axis IMU model in totes? (MPU-9250 = I²C 0x68; ICM-20948 = I²C 0x68; BNO055 = I²C 0x28 — affects driver pick on Pi 4)
- Exact SDR model(s)? (RTL-SDR R820T2 = 24 MHz–1.7 GHz; HackRF = 1 MHz–6 GHz; LimeSDR = 100 kHz–3.8 GHz) — determines Mk1 Defender survey range
- HV/VHV module spec? (output V, max I, enable pin? built-in oscillator or pure boost?)
- PCB CNC mill min trace/space spec? (drives §1 of [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md))
- Copper-clad stock dimensions + thickness available?
- USB-C power bank capacity + output current rating?
- Pi sensor kit contents (full list — drives §2 confirmations)
- Shielded cable / coax / twisted pair on hand?
- microSD module or breakout? (Pi 4 already takes SD natively, so this is for Nano if needed)
- Neodymium magnet sizes/grades? (needed for §11 calibration jig)

---

## 10. Cross-refs

- [architecture.md](architecture.md) — overall slot/module model + dual-MCU rationale
- [mk1_buildplan.md](mk1_buildplan.md) — what Mk0 grows into
- [wiki_synthesis.md § Pass 2](wiki_synthesis.md) — wiki BOM
- [safety.md](safety.md) — full safety posture
- [falsification.md](falsification.md) — biomarker measures we will eventually need to support (HRV via PPG is the key Mk0→Mk1 enabler)
- [inventory_capability_map.md](inventory_capability_map.md) — what we have vs. wiki BOM
- [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) — fab spec for the bifilar coil PCB

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

Updated from §8 given the parts-on-hand picture:

| # | Task | Owner | Status |
|---|---|---|---|
| 1 | **Tote inventory pass** — categorize by: dev boards, sensors, power, connectors, passives, RF, mechanical, fabric/shielding, magnets, chemicals (ferrofluid) | jono | ☐ |
| 2 | Confirm 9-axis IMU model + count | jono | ☐ |
| 3 | Confirm Pi sensor kit contents (env / PPG / ambient light / mic — list each part) | jono | ☐ |
| 4 | Confirm SDR model(s) + count | jono | ☐ |
| 5 | Confirm HV/VHV module spec (output V, max I, enable pin) | jono | ☐ |
| 6 | Confirm PCB CNC mill min trace/space + copper-clad stock dims | jono | ☐ |
| 7 | Confirm USB-C power bank capacity / output current | jono | ☐ |
| 8 | Fill in remaining `[INVENTORY-TBD]` markers | jono | ☐ |
| 9 | Sketch §5.1 footprint vs. 0.1 CAD shell | jono | ☐ |
| 10 | Commit inventory results back into this doc + [inventory_capability_map.md](inventory_capability_map.md) | jono | ☐ |

**Definition of done for Sprint 0.2:** every `[INVENTORY-TBD]` and `[CAD-MEASURE-TBD]` marker resolved; §§11–13 confirmed feasible with on-hand parts; PCB coil Gerber-generation script queued for Sprint 0.3. No solder iron touched today.
