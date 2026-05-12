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

### 4.1 Power source — inventory-confirmed paths

With confirmed inventory (4× MakerHawk 18650, 20× TP4056 USB-C chargers, DUTTY 5–20 A bench supplies, multiple boost/buck modules, mini-UPS units, Pololu U3V12F12 12 V step-up):

| Option | Source | Pros / cons |
|---|---|---|
| **A (Mk0 bench):** USB-C cable + DUTTY 5 A buck or wall-wart 5 V / 3 A | confirmed | trivial; safe; bench-only |
| **B (Mk0/Mk1 portable, RECOMMENDED):** **Talentcell 12V/11Ah + 9V/14.5Ah + 5V/26.4Ah** triple-output pack → 5V USB out direct → Pi 4 (USB-C); 12V out → coil-drive subsystem | confirmed (2 in stock) | ~132 Wh portable; 8–12 h Pi 4 + sensors; dual-rail (5V + 12V) needed for coil bench |
| **B' (Mk0 portable, lighter):** **Talentcell 12V/6Ah + 5V/12Ah** dual-output | confirmed (2 in stock) | ~72 Wh; 5–7 h Pi 4 |
| **B" (legacy/DIY):** 2× 18650 in 2S → Pololu U3V12F12 → 12 V → buck → 5 V 3 A → Pi 4 | confirmed | wiki-canonical path; preserved for redundancy / pure-DIY demo |
| **C (UPS-backed bench):** **TalentCell 27 Ah / 97 Wh Mini-UPS** w/ USB-C PD → Pi 4 direct | confirmed (1 in stock) | bench UPS; USB-C PD output is Pi 4-native; ride-through during HV pulse tests |
| **D (rack UPS):** mini-UPS 10 Ah 5/9/12 V | confirmed | secondary bench backup |

**Mk0 lock: Option A bench, Option B portable.** The Talentcell triple-output is the cleanest portable supply we have (12V for coil rail, 5V USB for Pi, 9V if needed for analog front-end). Mk0.5+ uses Option C (TalentCell Mini-UPS USB-C PD) for fixed-bench long-session logging.

### 4.1.1 Confirmed power inventory used in this spec

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
| 12 V → 5 V 3 A buck | DUTTY 6–24 V USB buck | 1 (Pi 4 supply) |
| Bench rail | DUTTY 20 A constant-V/I + DUTTY 5 A w/ display | 1 each |
| Surge buffer (optional, HV side) | 500 F 2.7 V supercap | 10 |
| Coil drive HV | Multiple HV modules from 1.8 kV up to 1000 kV | many (overstocked) |

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

### 6.1 Platform-side connectors (Mk0)

| Connector | Mk0 spec | Notes |
|---|---|---|
| Host data + charge in | **USB-C** on the Pi 4 directly | wiki Mk1-aligned (USB-C PD ≤ 5 V / 3 A) |
| Portable battery in | **DC-022 5.5×2.1 mm panel-mount jack** (30 in stock) | accepts Talentcell 12 V output; goes to onboard buck → 5 V Pi rail + 12 V module-bus rail |
| Debug | **6-pin 2.54 mm header** (TX / RX / GND / 3V3 / RST / GPIO0) | UART + reset; from XXXL passive kit |
| Status LEDs | **3× through-hole LEDs on Nano-driven side** | red=HV-armed (off at Mk0), amber=watchdog-OK, green=session-active |
| Mount to 0.1 shell | **M4 thumbscrews × 4** into shell hardpoints | from inventory M4 kit |

### 6.2 Module bus connector (the headline addition — see §6.5)

See §6.5 for the full spec. Headline: **6-pin JST-XH on the platform, mating 6-pin JST-XH lead on each module.** Delivers 12 V (module rail) + 5 V (logic) + GND + I²C SDA/SCL + open-drain SAFETY line.

## 6.5 Module bus specification (NEW — first-class platform feature)

This is the architectural commitment that makes HelmKit a *platform* rather than a one-off device. Every clip-on module (Stabilizer, Defender, HUD, Field Recorder, future PBM-halo, TDOA-localizer, etc.) connects via this bus.

### 6.5.1 Electrical

6-pin connector, JST-XH 2.5 mm pitch (operator pick — robust, polarized, in inventory; alternative: 5-pin Mini-DIN if connector stock dictates).

| Pin | Signal | Direction | Spec |
|---|---|---|---|
| 1 | **GND** | shared | 0 V reference, ≥ 3 A return capacity |
| 2 | **+5V_LOGIC** | platform → module | 5 V ± 5 %, 1 A continuous, fused on platform side |
| 3 | **+12V_RAIL** | platform → module | 12 V ± 10 %, 2 A continuous, soft-start on platform side, current-monitored by Nano |
| 4 | **I²C_SDA** | bidirectional | 100 kHz default, 3.3 V logic (with 5 V tolerant pull-ups on platform); module presents a single I²C device with unique address |
| 5 | **I²C_SCL** | platform → module | clock master is the Pi 4 |
| 6 | **SAFETY_n** | open-drain, bidirectional | active-low; any participant can pull low to kill the bus; Nano monitors and latches |

**Power topology rationale:** Pi 4 stays on 5 V from the platform UPS; the module gets 12 V for any coil drive / HV-module enable / Peltier / fan / high-current LED string. Module-internal buck regulates 12 V → 3.3 V as needed (modules are responsible for their own logic-rail buck).

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
  1. Cut 12 V rail to module bus within 5 ms
  2. Log the event with timestamp + last I²C transaction
  3. Hold latched until operator clears via the platform key-switch (Mk1+) or power-cycle (Mk0)

### 6.5.4 Why this matters for the techno-mage capstone

The module bus is what lets the **Psi Stabilizer Mk1 be lightweight and clip-on** (operator's stated requirement). Stabilizer Mk2 / Mk3 / Mk5 can change radically — different coil, different audio, different sensors, different drive chemistry — and the **platform doesn't change**. That's the whole point of a platform. The operator-as-techno-mage iterates on payload; the rig remains the rig.

**Mk0 rule:** the platform exposes one charge/data port + one debug header + the module bus. That's it. Modules clip on.

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
| 18650 cell + TP4056 USB-C charge module | 1+1 | inventory §4 | module battery (~6–8 h session life) |
| 6-pin JST-XH plug + 30 cm lead | 1 | inventory | mates platform module bus |
| PLA-printed clip-on enclosure | 1 | 3D printer | mechanical |

No procurement. Build month: now.

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
