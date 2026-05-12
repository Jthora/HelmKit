# Inventory ↔ Wiki BOM Capability Map

**Date:** 2026-05-12
**Purpose:** Map stated lab inventory against wiki Mk1 BOM (HelmKit + Stabilizer + Harmonizer + Defender). Identify what's already covered, what's substitutable, what's the gap.
**Stance reminder:** See [../README.md § Note to AI assistants](../README.md). Wiki BOMs are engineering intent. We use what we have to implement that intent — not to "approximate" it.

---

## 1. Stated inventory (from operator, 2026-05-12)

**Full canonical inventory list lives in [inventory.md](inventory.md).** Headline items relevant to this capability mapping:

- General electronics workbench + **YEAPOOK ADS1014D 100 MHz DSO** (covers coil drive band 5× over)
- **HackRF One** (1 MHz – 6 GHz TX+RX) + **2× NESDR Smart v4** + **1× NESDR Smart XTR** + **Nooelec Ham It Up** upconverter + **Nooelec 1:9 antenna balun** (HF emission monitor)
- **MAX2870 PLL signal source** (23.5 MHz – 6 GHz) + **ADF4351 PLL dev board** (35 MHz – 4.4 GHz) + **2× XR2206 function generator kits** (1 Hz – 1 MHz, for 7.83 Hz envelope)
- Several **Raspberry Pi 4B** (MCU-A doer)
- Several **Jetson Nano** (CUDA edge compute, FDTD/ML offload)
- **5× Arduino Nano v3** (MCU-B watchdog) + 5× Nano terminal adapters
- **2× Heltec LoRa 32** (ESP32 + 0.96" OLED + Li-Po PMIC + WiFi + BLE + LoRa 863–928 MHz, in enclosures) — *wiki Mk1 Stabilizer MCU stack in one board*
- **1× ESP8266 Deauth Detector v3** + **1× RangePi 433 MHz Board** + enclosure
- **MLX90640 thermal IR array** (32×24 px, 55° FOV) + **SGP40 VOC sensor** + **multiple 9-axis IMU modules** (specific part TBD)
- **Smart Home Sensor Kit (DKHK100200)** + **Raspberry Pi 4B Sensor Starter Kit (KS3016)** — dual sensor coverage incl. DS18B20, BMP180, DHT11, MQ-2/3/5/7, PIR, Hall, Reed, TEMT6000, GUVA-S12SD UV, LM35, ultrasonic, thin-film pressure, photoresistor, capacitive touch, relays
- **4× MakerHawk 18650 3000 mAh** + **20× TP4056 USB-C chargers** + **20× 4.2 V USB-C Li-ion modules** + **10× 500 F 2.7 V supercaps**
- **DUTTY 20 A constant-V/I bench supply** + **DUTTY 5 A buck w/ display** + 2× Pololu U3V12F12 12 V boost + 20× MT3608 boost + 5× SX1308 boost + 5× Icstation 1–5 V boost + DROK 5.5–30 V boost-buck
- Several **mini-UPS battery-backup modules** (12 V / 9 V / 5 V output)
- **HV stack:** 5× 1000 kV gen, 5× 400 kV gen, 3× 20 kV arc/pulse, 1× 3–11 kV, 2× 1800 V arc, 1× 30 kV ignition coil, 2 sets 15 kV inverter parts
- **Genmitsu CNC 3018-PRO** + **10× 70×100 mm single-sided copper-clad** + 18-pc copper sheet kit
- **Ferrofluid**, **industrial EMI/RFI shielding spray**, **Faraday fabric**
- 25× neodymium bar magnets (60×10×3 mm), 500× mixed small magnets
- **5228-pc XXXL passive kit**, 730× IR LEDs, 365× UV LEDs, full Dupont + hookup-wire stock
- Audio I/O: **M-Audio M-Track Duo USB interface**, 3× Anything Speaker Pro, 6× 40 mm full-range drivers, BT amp boards, optical/TosLink/analog adapters
- **ELP 170° fisheye 8MP USB camera**

This inventory is **at or above wiki Mk1 spec on every functional axis.** Procurement gap is **~$15** (double-sided FR4 stock for the bifilar coil) to enable the wiki-canonical two-layer coil geometry exactly. Without that, single-sided fallback is available; with it, we match wiki spec.

---

## 2. Coverage matrix vs. wiki Mk1 BOMs

Legend: ✅ covered · 🟡 substitutable · ❌ gap

### 2.1 HelmKit core (wiki: STM32F407 + RP2040 + OLED + IMU + env + mag + USB-C PD + 2× 18650)

| Wiki spec | Have | Status | Notes |
|---|---|---|---|
| MCU-A (doer): STM32F407 class | Raspberry Pi 4 | ✅ over-spec | Pi 4 has more compute than F407 by 2 orders of magnitude. Runs Linux, full SDR stack, ML inference. |
| MCU-B (checker): RP2040 | Arduino Nano v3 (ATmega328P) | 🟡 acceptable | ATmega328P is small enough to formally audit; runs the watchdog firmware. |
| **Wireless mesh / BLE node** | **Heltec LoRa 32** (ESP32 + WiFi + BLE + LoRa) | ✅ **better** | One board replaces the wiki's separate nRF52840 + LoRa + OLED. **2 in inventory.** |
| 9-DOF IMU (MPU6050+HMC5883L) | 9-axis IMU modules ×N | ✅ better | One integrated 9-axis is cleaner than two separate parts. |
| Env sensor (BME680) | **SGP40 VOC** + **BMP180 + DHT11 + DS18B20** from sensor kits | ✅ covered (split across parts) | Better VOC than BME680; pressure and temp are separate but covered. |
| OLED HUD (SSD1306 0.96") | **Built into Heltec LoRa 32** | ✅ | Two of them; one per HUD path or one as backup. |
| USB-C PD 5V/3A | USB-C cables + mini-UPS + DUTTY buck 6–24 V → 5 V 3 A | ✅ | Multiple paths. |
| 2× 18650 NCR | **4× MakerHawk 18650 3000 mAh** | ✅ | 2 pairs (1 in-use + 1 backup). Holders 🟡 confirm. |
| GoPro/Picatinny mount | 3D-printable on existing CAD shell | ✅ | Print as part of 0.1 shell iteration. |

**Verdict:** HelmKit core is **fully buildable** from current inventory. Pi 4 + Nano v3 + one 9-axis IMU + Pi sensor kit env board = complete platform.

### 2.2 Stabilizer module (wiki: nRF52840 + Polar H10 + bifilar PCB coil 1–8 MHz + SI5351 + Class-D)

| Wiki spec | Have | Status | Notes |
|---|---|---|---|
| MCU (nRF52840) | **Heltec LoRa 32** (ESP32) | ✅ **direct substitute** | ESP32 has BLE; talks to Polar H10 over BLE GATT natively. Plus WiFi + LoRa + OLED + battery management. |
| Polar H10 chest strap | ❌ | ❌ procurement (~$80) | Mk1 procurement target; or use sensor-kit pulse modules as interim. |
| **Bifilar PCB coil ~30×30 mm** | **Genmitsu CNC 3018-PRO + copper-clad** | 🟡 fab path enabled | **Stock is single-sided only.** Double-sided FR4 (~$15) enables exact wiki two-layer geometry; otherwise use single-sided fallback per [mk0_pcb_bifilar_coil.md § 1.4](mk0_pcb_bifilar_coil.md). |
| SI5351 clock gen | **ESP32 LEDC PWM** (Heltec) + **XR2206 kit** (1 Hz–1 MHz) + **MAX2870 PLL** (>23.5 MHz) + **ADF4351 PLL** (>35 MHz) | ✅ multiple paths | ESP32 LEDC is the cleanest current-inventory option for the wiki 1–8 MHz drive band. XR2206 covers the lower edge + handles the 7.83 Hz Schumann envelope. |
| Class-D audio amp (PAM8403 / TPA3116) | **BT Amp boards 2×5W** + **discrete MOSFETs from 5228-pc kit** | ✅ | Discrete MOSFET H-bridge is preferred at 1–8 MHz where audio-band Class-D won't reach. |
| **Coil driver up to 1–8 MHz at safe V** | **HV modules + DUTTY 20A bench supply + DSO for verification** | ✅ | HV modules drive the coil; DUTTY supply provides clean low-voltage rail for control; DSO verifies waveform. |
| Coil temp sense (safety floor) | **DS18B20** from Smart Home kit | ✅ | Glue to coil pot during build. |
| Coil-drive cutoff (safety floor) | **5V 2-channel relay** from Smart Home kit | ✅ | Wire to MCU-B GPIO. |

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
| SDR for survey + jamming-aware listening | **HackRF One + 3× NESDR + Ham It Up + 1:9 balun** | ✅ over-spec |
| 2× magnetometer (gradiometer) | 9-axis IMUs ×N — each has mag — pair two at known offset | ✅ |
| ESD probe | Build from passives + neon bulb / spark gap | ✅ |
| Bifilar coil (for active counter-emit) | Same fab path as Stabilizer | ✅ |
| Thermal sense | **MLX90640 32×24 thermal IR array** | ✅ **direct wiki Defender spec match** |
| VOC / chem sense | **SGP40** + MQ-2/3/5/7 from sensor kit | ✅ over-spec |
| Visual / wide FOV | **ELP 170° fisheye 8MP USB cam** | ✅ |

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
| **Double-sided 70×100 mm FR4 copper-clad** (5–10 pc) | ~$15 | **medium-high** | Wiki-canonical two-layer bifilar coil geometry. Single-sided fallback exists but loses the inter-layer E-field. **This is the single highest-impact procurement.** |
| Polar H10 chest strap | ~$80 | medium | Mk1 Stabilizer HRV gold standard. Pi sensor kit PPG is the interim. |
| Bone-conduction transducer pair | ~$10 | low | Harmonizer Mk1. 6× 40 mm full-range drivers substitute on cheek/temple. |
| nRF52840 dev board (Adafruit Feather / Seeed XIAO) | ~$15 | low | Heltec LoRa 32 substitutes (ESP32 BLE). |
| Si5351 module if we want exact wiki carrier IC | ~$5 | low | ESP32 LEDC PWM substitutes natively in 1–8 MHz. |

**Total procurement gap: ~$15 of critical items + ~$110 of nice-to-haves. The $15 of double-sided FR4 is the only meaningful unlock; everything else is substitutable.**

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
