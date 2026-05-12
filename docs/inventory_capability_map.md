# Inventory ↔ Wiki BOM Capability Map

**Date:** 2026-05-12
**Purpose:** Map stated lab inventory against wiki Mk1 BOM (HelmKit + Stabilizer + Harmonizer + Defender). Identify what's already covered, what's substitutable, what's the gap.
**Stance reminder:** See [../README.md § Note to AI assistants](../README.md). Wiki BOMs are engineering intent. We use what we have to implement that intent — not to "approximate" it.

---

## 1. Stated inventory (from operator, 2026-05-12)

- General electronics workbench (soldering, multimeter, scope assumed, hand tools, passives, breadboards, jumpers, etc.)
- **Multiple SDR modules** (model TBD — RTL-SDR / HackRF / LimeSDR / USRP class)
- **Multiple Raspberry Pi 4** computers
- **Multiple Jetson Nanos** (CUDA-capable edge compute)
- **Multiple Arduino Nano v3** (ATmega328P, 5V, 16 MHz)
- **Multiple 9-axis IMU modules** (3-axis accel + gyro + mag — likely MPU-9250 / ICM-20948 / BNO055 class)
- **Raspberry Pi sensor module kit** (env / light / pressure / etc. — exact contents TBD)
- **Many neodymium magnets** (size/grade TBD)
- Full passives + everything needed to build circuits
- **Small CNC PCB mill** + copper-clad substrate stock + bits
- **Ferrofluid**
- **Industrial EMI/RFI shielding sprays** (likely Ni / Cu / Ag conductive aerosol)
- **Faraday fabric** (silver- or nickel-plated conductive textile)
- **High-voltage and very-high-voltage modules** (boost / inverter / flyback / multiplier class)
- Plus "many other modules"

This inventory is **way above Mk0 spec**. It's at or above wiki Mk1 spec on every functional axis except the BLE-mesh / nRF52840 path.

---

## 2. Coverage matrix vs. wiki Mk1 BOMs

Legend: ✅ covered · 🟡 substitutable · ❌ gap

### 2.1 HelmKit core (wiki: STM32F407 + RP2040 + OLED + IMU + env + mag + USB-C PD + 2× 18650)

| Wiki spec | Have | Status | Notes |
|---|---|---|---|
| MCU-A (doer): STM32F407 class | Raspberry Pi 4 | ✅ over-spec | Pi 4 has more compute than F407 by 2 orders of magnitude. Runs Linux, full SDR stack, ML inference. |
| MCU-B (checker): RP2040 | Arduino Nano v3 (ATmega328P) | 🟡 acceptable | ATmega328P is small enough to formally audit; runs the watchdog firmware. Wiki specifies RP2040 for dual-core; for Mk1 watchdog scope, Nano is sufficient. |
| 9-DOF IMU (MPU6050+HMC5883L) | 9-axis IMU modules ×N | ✅ better | One integrated 9-axis is cleaner than two separate parts. |
| Env sensor (BME680) | Pi sensor kit | 🟡 likely | Confirm during inventory; BME280/680 commonly in Pi kits. |
| OLED HUD (SSD1306 0.96") | Pi sensor kit / spare | 🟡 likely | Common in Pi kits; otherwise defer to Mk1.5. |
| USB-C PD 5V/3A | USB micro/C cables + Pi 4 USB-C | 🟡 partial | Pi 4 input is USB-C 5V/3A native. Power path covered for tethered ops. |
| 2× 18650 NCR | TBD | ❌ inventory pass | Almost certainly in totes. Confirm. |
| GoPro/Picatinny mount | 3D-printable on existing CAD shell | ✅ | Print as part of the 0.1 shell iteration. |

**Verdict:** HelmKit core is **fully buildable** from current inventory. Pi 4 + Nano v3 + one 9-axis IMU + Pi sensor kit env board = complete platform.

### 2.2 Stabilizer module (wiki: nRF52840 + Polar H10 + bifilar PCB coil 1–8 MHz + SI5351 + Class-D)

| Wiki spec | Have | Status | Notes |
|---|---|---|---|
| MCU (nRF52840) | Pi 4 / Nano | 🟡 substitute | Pi 4 hosts; Nano can drive coil PWM directly. BLE-to-Polar-H10 path = Pi 4 BT or add a $4 BLE breakout later. |
| Polar H10 chest strap | ❌ | ❌ procurement | Defer or use PPG via Pi sensor kit if MAX30102 present. |
| **Bifilar PCB coil ~30×30 mm** | **PCB CNC mill + copper-clad** | ✅ **CAN FAB** | This is the unlock. See [`mk0_pcb_bifilar_coil.md`](mk0_pcb_bifilar_coil.md). |
| SI5351 clock gen (3-output, 8 kHz – 160 MHz) | Likely in modules box | 🟡 confirm | If absent: any of Pi 4 GPIO PWM, Nano PWM (audio-band only), or HV module's own oscillator. |
| Class-D audio amp (PAM8403 / TPA3116) | 🟡 confirm | 🟡 likely | If absent: discrete MOSFET H-bridge from your passives — even better for the wiki coil drive at 1–8 MHz where audio-band Class-D won't reach. |
| **Coil driver up to 1–8 MHz at safe V** | **HV/VHV modules** | ✅ over-spec | Your HV modules can drive the coil; we'll current-limit and instrument it. |

**Verdict:** Stabilizer-class module is buildable **now**, including the wiki-canonical coil drive chain. This is the single biggest piece of news from your inventory description.

### 2.3 Harmonizer module (wiki: same as Stabilizer + bone-conduction + PPG + 1–40 Hz drive layer)

| Wiki spec | Have | Status |
|---|---|---|
| Bone-conduction transducer | ❌ | $8 part; defer. |
| PPG | Pi sensor kit likely | 🟡 confirm |
| 1–40 Hz envelope on top of coil | Same coil chain as Stabilizer | ✅ |

**Verdict:** Coil + PPG path covered. Bone-conduction is the only gap.

### 2.4 Defender module (wiki: HackRF + nRF52840 + 2× HMC5883L + ESD probe + bifilar coil)

| Wiki spec | Have | Status |
|---|---|---|
| SDR for survey + jamming-aware listening | **SDR modules ×N** | ✅ |
| 2× magnetometer (gradiometer) | 9-axis IMUs ×N — each has mag — pair two | ✅ |
| ESD probe | Build from passives | ✅ |
| Bifilar coil | Same fab path | ✅ |

**Verdict:** Defender survey/sense path is **fully covered**. Active counter-emit at GHz is Mk2; you have the parts for the *sense* half today.

### 2.5 Cross-cutting platform

| Capability | Have | Status |
|---|---|---|
| Heavy compute (ML inference, FDTD simulation, real-time SDR DSP) | **Jetson Nano** | ✅ huge unlock |
| EM shielding for sensors (isolate mag from coil) | **Faraday fabric + EMI spray** | ✅ |
| Magnetic field source for IMU calibration | **Neodymium magnets** | ✅ |
| Field-visualization media (Mk2 demo / Q.A. tool) | **Ferrofluid** | ✅ niche use |
| **Selective shielding inside the helm shell** | **EMI spray + Faraday fabric** | ✅ |

---

## 3. Real gaps (what to procure later, **not** today)

| Item | Cost | Priority | Used in |
|---|---|---|---|
| Polar H10 chest strap | ~$80 | medium | Mk1 Stabilizer primary biomarker (HRV gold standard) |
| Bone-conduction transducer pair | ~$10 | low | Harmonizer Mk1 |
| nRF52840 dev board (Adafruit Feather / Seeed XIAO) | ~$15 | low | BLE mesh path; substitutable by Pi 4 BT |
| SI5351 module if not in totes | ~$5 | low | 1–8 MHz signal gen; substitutable by HV module's own oscillator or discrete H-bridge clocked by Nano |
| Class-D audio amp module if not in totes | ~$3 | low | substitutable by discrete MOSFET H-bridge |

**Total procurement gap: ≤ $120. Not blocking. Phase 1 (Mk0 + Stabilizer-instrumented) is buildable from totes alone.**

---

## 4. Rescoped sprint plan

Because the inventory clears Mk1 hardware-wise, Sprint 0.2 shifts from "minimum-viable Mk0" to "Mk0 + lay the Mk1 coil fab in parallel":

| Sprint | Was | Now |
|---|---|---|
| 0.1 | CAD shell baselined | ✅ done |
| **0.2 (today)** | Circuit spec doc for Mk0 sensors-only | **Circuit spec doc + bifilar PCB coil Gerber spec (CNC-fab ready). Still no soldering today.** |
| 0.3 | Mk0 perfboard build | Mk0 perfboard build **+ mill bifilar coil PCB v0.1** |
| 0.4 | Mk0 power-on, basic sensor logging | Same; coil isolated, instrumented, **not yet driven** |
| 0.5 | Add MCU-B watchdog firmware (Nano) | Same |
| 0.6 | **Coil drive bring-up at low V, instrumented, in Faraday-bagged bench fixture (not on head)** | Mk1 Stabilizer first power |

This is the **Mk0 + Mk1-coil-prefab combo**, executable from totes.

---

## 5. Highest-leverage pre-inventory prep tasks (done in parallel docs)

1. ✅ This capability map.
2. ✅ Bifilar PCB coil fab spec (next-doc) → [`mk0_pcb_bifilar_coil.md`](mk0_pcb_bifilar_coil.md).
3. ✅ Updated Sprint 0.2 with inventory-confirmed picks (Pi 4 + Nano + 9-axis IMU + Pi sensor kit).
4. Magnetometer 3-point calibration jig spec using neodymium magnets — appended to Sprint 0.2 §11.
5. Faraday-fabric sensor isolation plan — appended to Sprint 0.2 §12.
6. SDR survey baseline protocol — appended to Sprint 0.2 §13.

---

## 6. Notes on specific inventory items the wiki has uses for

### 6.1 Ferrofluid
- **Wiki engineering use:** non-trivial — ferrofluid in a sealed lens cell, biased by a small magnet, can serve as a **passive low-pass magnetic damper** at AC. The Rosensweig instability also makes a striking field-strength visualizer for demos and for quick qualitative checks of coil emission patterns. Save for Mk2 demo/QA work.
- **Calibration use:** drop a ferrofluid pellet near a magnetometer and verify field-gradient response is correctly polarity-mapped during IMU calibration. Quick sanity check.

### 6.2 Neodymium magnets
- **Calibration jig:** known-field source for magnetometer scale + hard-iron offset calibration. See §11 of [`sprint_0.2_circuit_spec.md`](sprint_0.2_circuit_spec.md).
- **Hard-iron bias check:** place magnet at fixed distance, rotate IMU, verify Lissajous trace closes to a circle.
- **Gradiometer baseline:** two magnetometers + a known magnet at known offset = closed-form check of subtractive gradient computation (per the wiki Defender 2× HMC5883L pattern).
- **Do not** mount permanent magnets inside the helm shell. They will dominate any field measurement and saturate sensors.

### 6.3 HV / VHV modules
- **Wiki-aligned use:** drive the bifilar coil. The wiki coil's intent is high inter-turn E-field with suppressed B dipole — that wants **voltage, not current**. HV modules are the right primitive.
- **Safety floor:** current-limited via series resistor + active fuse; coil potted; primary winding behind opto-isolation from MCU-A; MCU-B kill-line cuts the HV enable pin, not the HV rail itself.
- **Mk0/0.5: HV modules stay in their box.** Bench-only when first powered; never on head until full safety chain is verified.

### 6.4 SDR modules
- **Mk0 use:** baseline ambient RF survey of the build location and the wearer's home/lab. Establishes the noise floor F8/F9 falsification will measure against.
- **Mk0.5 use:** record sham vs. active coil-drive sessions to verify coil emission stays in the design band (1–8 MHz) and below leak thresholds at GSM/WiFi bands.
- **Mk1 use:** Defender module's primary sensor.

### 6.5 Jetson Nano
- **Mk0/Mk1 use:** offload real-time SDR DSP, FFT, HRV analysis. Pi 4 handles control; Jetson handles compute.
- **Mk2 use:** onboard FDTD coil-emission model (openEMS / MEEP), verifying SAR compliance live against the field the SDR measures. This is the wiki-spec'd "FDTD modelling required for design cert" loop, but **in the device**.
- **ML use:** EEG/HRV biomarker inference if/when EEG path lands.

### 6.6 Faraday fabric + EMI spray
- **Inside the helm:** line the inner cavity around the magnetometer to reduce coupling from the coil. This is what makes co-located mag+coil viable.
- **Sham control:** wrap a sham coil in Faraday fabric so its emission is suppressed but its weight/heat profile is identical. **Required for blinded RCT per F1.**
- **Bench fixture:** Faraday cage / tent for first coil power-on so emission is contained and characterized before any on-head test.

---

## 7. Cross-refs

- [sprint_0.2_circuit_spec.md](sprint_0.2_circuit_spec.md) — circuit spec with concrete picks
- [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) — fab-ready PCB coil spec
- [mk1_buildplan.md](mk1_buildplan.md) — Mk1 jump target
- [wiki_synthesis.md § Pass 2](wiki_synthesis.md) — wiki BOM source
- [safety.md](safety.md) — safety floor
- [falsification.md](falsification.md) — measurement targets
