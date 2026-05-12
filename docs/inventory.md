# HelmKit Lab Inventory — Confirmed 2026-05-12

**Status:** Authoritative inventory snapshot. Operator-confirmed during 2026-05-12 tote pass.
**Use:** Single source of truth for "what we have." Sprint planning docs reference back here. Update as new totes are opened or parts are consumed.

> Stance: Wiki-canonical parts (SI5351, nRF52840, etc.) are *engineering intent*, not part numbers we must match. Where we have a part that fulfills the **electrical role** the wiki specifies — same band, same function — we use it. See [../README.md § Note to AI assistants](../README.md) and [inventory_capability_map.md](inventory_capability_map.md).

---

## 1. Compute / MCU

| Qty | Item | Notes |
|---|---|---|
| Several | **Raspberry Pi 4B** | MCU-A doer; Linux host; USB to SDR; full DSP / ML pipeline |
| Several | **Jetson Nano** | CUDA edge compute; FDTD/ML offload; Mk2+ |
| 5 | **Arduino Nano v3** (ATmega328P, 16 MHz) | MCU-B watchdog candidate |
| 5 | **Arduino Nano Terminal Adapter v2** | screwless breakout for the Nanos |
| 2 | **Heltec LoRa 32** (ESP32 + 0.96" OLED + Li-Po PMIC + WiFi + BLE + LoRa 863–928 MHz, in enclosures) | **Wiki Mk1 Stabilizer-class MCU package, one board.** OLED HUD + BLE + LoRa mesh + battery management all integrated. |
| 1 | **ESP8266 Deauth Detector v3** (DSTIKE / MakerFocus, ESP12N, 4 MB, RGB LED, buzzer, pre-flashed) | WiFi defensive monitoring; threat-sense at 2.4 GHz |
| 1 | **RangePi Board 433 MHz** (sb components) + **RangePi Enclosure** | LoRa-class long-range receiver at 433 MHz |
| 1 | **Keywishbot MEGA2560 starter bundle** (breadboard, passives) | spare AVR + breadboard kit |

**Verdict:** dual-MCU + BLE + LoRa + WiFi mesh **all covered**, with redundancy. The 2× Heltec LoRa 32 are the single most useful items in the entire inventory for Mk1.

---

## 2. SDR / RF signal generation / antenna

### 2.1 SDR receivers

| Qty | Item | Range | Notes |
|---|---|---|---|
| 1 | **HackRF One** | 1 MHz – 6 GHz, ±20 MS/s, TX+RX half-duplex | Wiki Defender Mk1 spec part. TX-capable. |
| 2 | **Nooelec NESDR Smart v4** (RTL2832U + R820T2, 0.5 PPM TCXO, SMA, Al enclosure) | 24 MHz – 1.7 GHz RX-only | survey receivers; identical, can phase-correlate |
| 1 | **Nooelec NESDR Smart XTR** (extended range) | ~65 MHz – 2.3 GHz typical XTR | replaces R820T2 with E4000 for wider tuning |
| 1 | **Nooelec Ham It Up** (upconverter, ~125 MHz LO) | shifts HF/MF/LF up into RTL range | enables 1–8 MHz coil-drive band reception on NESDR |

### 2.2 RF signal sources

| Qty | Item | Range | Role |
|---|---|---|---|
| 1 | **YUANJS / NWDZ MAX2870 PLL signal source** (X002V4BDU5, screen, USB-C) | 23.5 MHz – 6 GHz | clean PLL carrier; **direct candidate for bifilar coil drive in the 23.5 MHz lower bound** (above wiki 1–8 MHz, but matches Mk2 GHz path) |
| 1 | **ADF4351 dev board** (NWDZ X003MKAO0H or equivalent GOTOTOP) | 35 MHz – 4.4 GHz | second PLL source; SPI-controllable; **also above 1–8 MHz natively** |
| 2 | **XR2206 function generator kit** (ICQUANZX, assembly required) | 1 Hz – 1 MHz, sine/tri/square | **the 7.83 Hz Schumann envelope generator** AND **a low-side coil drive option for sub-MHz Persinger-style work** |
| 1 | **MiOYOOW PWM frequency generator** | 1 Hz – 150 kHz | likely broken per operator; bench triage |

**Important note re: coil drive band.** Wiki Mk1 Stabilizer specifies **1–8 MHz** carrier. Our PLL sources start at 23.5 MHz (MAX2870) / 35 MHz (ADF4351). For the wiki 1–8 MHz band the path is:
- **XR2206** can produce up to 1 MHz — covers the lower edge of the wiki band.
- **Pi 4 + Si5351 via I²C** would cover natively if we had it (don't — see procurement gap).
- **Heltec LoRa 32 / ESP32 LEDC PWM** can synthesize square-wave clocks 1–8 MHz with on-chip dividers, then filter to sine. **This is the cleanest current-inventory path.**
- For 23.5 MHz – 6 GHz Mk2 work the PLL sources are direct.

### 2.3 Antennas + RF accessories

| Qty | Item | Notes |
|---|---|---|
| 1 | **HYS TC-77 1FR 144/430 MHz antenna** | dual-band amateur |
| 3 | **Cradlepoint 4G/LTE 170760-000** | 600 MHz – 6 GHz wideband |
| 1 set | **Baufeng unique antennas** (HT-class) | UHF/VHF |
| 1 bag | **Antenna - 433 MHz** | pairs with RangePi |
| 1 kit | **5 unique antennas** (mixed connectors) | survey/spare |
| 1 | **Nooelec 1:9 antenna balun** (v1.0c2, 2020-03-16) | HF reception balancing, ~500 kHz – 50 MHz; **valuable for coil emission monitoring** |
| 1 | **Antenna stand, magnetic base** | ground-plane bench mount |
| 1 | **Nooelec small antenna stand** | tabletop |
| 18 | **Type S antenna FPV connectors** (ALLiSHOP) | RP-SMA-class adapters |
| 20 | **Exgoofit exotic antenna adapters** | wide compatibility |
| 5 | **SDTC RF jumper cables, 6"** | SMA jumpers |
| 1 bag | **BingFu antenna connectors** (variety) | adapter stock |
| 1 bag | **4 unique antenna adapters incl. coax** | TV/F-type bridging |
| 1 | **Mystery antenna kit "G9000-SY" (xerials Corporation)** | mounts to unknown; investigate during build |

**Verdict:** RF stack massively over-spec for Mk1; clears wiki Defender requirements. The 1:9 balun is the sleeper hit — perfect for SDR-based coil-emission monitoring.

---

## 3. Sensors

### 3.1 IMU / mag — CONFIRMED

| Qty | Part | Notes |
|---|---|---|
| 2 | **CHENBO GY-9250** — MPU9250/6500 9-DOF (accel + gyro + mag), SPI/I²C | wiki-spec class for HelmKit core IMU + gradiometer pair |
| 1 | **HiLetgo GY-9250** — MPU9250/6500 9-DOF, 16-bit, SPI/I²C | spare / second gradiometer head |
| 1 | **Diymore GY-521** — MPU-6050 6-DOF (accel + gyro only, no mag) | secondary motion sense; MCU-B (Nano) attitude watchdog (decoupled from main IMU bus) |

**Total: 3× 9-DOF (MPU9250 class) + 1× 6-DOF (MPU6050).** This locks the IMU pick.

- I²C addresses: MPU9250 = 0x68 (AD0 low) / 0x69 (AD0 high); on-die AK8963 mag = 0x0C (via I²C master pass-through). MPU6050 = 0x68 — collides with MPU9250 default, so wire MPU6050 to MCU-B's bus or strap to 0x69.
- **Recommended deployment:**
  - HelmKit core (Pi 4 bus): 1× GY-9250 @ 0x68 (head-pose / motion)
  - Defender gradiometer pair (Pi 4 bus): 2× GY-9250 at known offset — one at 0x68, one at 0x69, mounted ~5 cm apart
  - MCU-B (Nano) watchdog: 1× GY-521 @ 0x68 on Nano's independent I²C bus — redundant motion sense for the safety blacklist ("helm-on-ground" detection independent of Pi 4)
  - Spare: 1× GY-9250 cold spare

### 3.2 Smart Home Sensor Kit (DKHK100200) — confirmed contents

| Module | Use in HelmKit context |
|---|---|
| Voltage Detection Sensor | battery rail monitor for MCU-B |
| MQ-2 Gas + Smoke | environmental hazard sense |
| MQ-5 Combustible Gas | environmental hazard sense |
| MQ-7 CO Carbon Monoxide | environmental hazard sense |
| Flame Detection | environmental hazard sense |
| **DS18B20 Temperature** | **coil-pot temp sense (mandatory safety floor)** |
| DHT11 Temp + Humidity | head-cavity climate log |
| BMP180 Barometric Pressure | atmospheric / altitude log |
| Digital Touch | UI input |
| Photosensitive Light | photic-stim sham control |
| **Vibration** | mechanical-shock detection |
| Sound Detection | ambient audio context |
| Buzzer Alarm | MCU-B safety alarm output |
| **5V 2-Channel Relay** | **coil-drive hard cutoff via MCU-B** |
| HC-SR501 PIR Motion | proximity / wearer-present check |
| Water Level | leak detection if liquid cooling added |
| Analog-to-Digital Converter | (likely ADS1115 or similar) — analog sensor front-end |

### 3.3 Raspberry Pi 4B Sensor Starter Kit (KS3016) — confirmed contents

Highlights only (full list in original inventory):

| Module | Use |
|---|---|
| RPI GPIO–**PCF8591 Shield** | 4-ch 8-bit ADC + 1-ch DAC on I²C — analog front-end for Pi 4 |
| White / Red / RGB / 3W LEDs | photic-stim output + status |
| Active + Passive Buzzers | UI + alarm |
| IR Obstacle Avoid | proximity |
| PIR Motion | proximity |
| Flame, Tilt, Collision, Vibration | hazard sensors |
| **Hall Magnetic + Reed Switch** | magnetic-field digital sense (coarse) |
| 5D Relay | drive output cutoff |
| **Capacitive Touch** | wearer-skin-contact detection |
| Photo Interrupter, TEMT6000, Photoresistor, **GUVA-S12SD UV** | optical stack |
| Servo + Joystick | mechanical control |
| **I²C LCD1602** | secondary status display |
| Water Level, Soil Humidity, Steam | (likely repurposed for sweat / scalp-moisture later) |
| **LM35** + Analog Temp | analog temp for redundancy |
| **MQ-2 + MQ-3 Alcohol** | gas / breath analysis |
| **Thin-film Pressure** | head-mount pressure check (proper fit verification) |
| **Ultrasonic HC-SR04-class** | range-find / proximity |
| 40-pin F-F Dupont | wiring |

### 3.4 Specialty sensors (loose)

| Qty | Item | Use |
|---|---|---|
| 1 | **MLX90640 thermal imaging IR array** (NGW-1pc Grove, 55° FOV, 32×24 px) | **wiki Defender thermal sense; head-radiation monitor** |
| 1 | **SGP40 VOC gas sensor** | environmental air-quality, **better than BME680 for VOC alone** |

### 3.5 Audio I/O

| Qty | Item | Use |
|---|---|---|
| 3 | **Anything Speaker Pro** (1 wired internal, 1 broken 3.5 mm port) | audio stim source |
| 1 | **Anything Speaker** (small) | audio stim source |
| Multiple | **Bluetooth Amplifier Board 2×5 W (BT 5.0, 3.7–5 V)** ×2+ | DIY wireless speaker / wearable audio |
| 6 | **abcGoodefg 40 mm 4 Ω 3 W full-range drivers** | bone-conduction substitute / direct ear-pad |
| 2 | **Cylewet 2" 4 Ω 10 W full-range drivers** | larger driver option |
| 1 | **M-Audio M-Track Duo USB audio interface** (dual XLR/line/DI) | studio-grade ADC for biometric audio capture |
| 1 | **Hey Mic! Bluetooth lavalier mic** | wireless audio capture |
| 1 | **Sound Amplifier** ("through wall/door" type) | high-gain mic; possible scalp acoustic pickup |
| 1 | **Panlong 5.1 Dolby decoder** | optical/coax in, 5.1 analog out |
| 1 | **USB Bluetooth dongle TP-Link UB400** | desktop BT for Pi/Linux |
| Several | **USB-C / USB-A audio adapters** (CableCreation, DuKabel, LOKUKA, jstma) | bridging |
| 1 | **TosLink optical 3 ft** | digital audio routing |
| Many | **3.5 mm / 2.5 mm / 6.35 mm / XLR adapters & cables** | audio plumbing |
| 1 spool | **16 AWG speaker wire 100 ft** | bulk audio cable |

### 3.6 Optical I/O

| Qty | Item | Use |
|---|---|---|
| 730 | **IR LEDs (small package)** | **photic stim at IR; wiki-relevant for retinal-IR** |
| 365 | **UV LEDs** | curing / sterilization / experimental photic |
| Various | **Colored LEDs** | status / photic stim |
| 1 | **ELP 170° fisheye 8MP USB camera** | **head-cam / situational awareness; Defender vision** |
| 10 pairs | **Gikfun IR emit+receive diode pair** (EK8460) | IR comms / IR sense |
| 5 sets | **MELIFE 38 kHz IR receiver + transmitter module** (EK8477) | discrete IR |
| 5 sets | **M14178 38 kHz IR modules** | discrete IR |

---

## 4. Power

### 4.1 Cells / batteries

| Qty | Item | Notes |
|---|---|---|
| 4 | **MakerHawk 18650** (3000 mAh, 3.7 V, 11.1 Wh) | wiki spec calls for 2× 18650 NCR — **wiki Mk1 power covered with 2 spares** |
| Various | **Battery clips** for 18650 / AAA / AA / 9V + unique types | holders |
| Some | **48 V eBike battery recovered components** | high-energy spare parts; bench-only |

### 4.2 Charging modules

| Qty | Item | I/O | Notes |
|---|---|---|---|
| 5 | **TP4056 USB-C 5 V 1 A** (Diymore) | charges single 18650 with protection | wiki-spec charger |
| 20 | **1362_2 USB-C 3.7 V / 4.2 V Li-ion charger** (1 A, with LED) | duplicate of XIITIA below | abundant |
| 20 | **XIITIA Mini USB-C 3.7 V Li-ion charger** (4.2 V, protection circuit + LED) | (same item, restated by operator) | abundant |

### 4.3 Step-up / step-down / regulators

| Qty | Item | Spec | Role |
|---|---|---|---|
| 1 | **DUTTY 20 A constant-V/I synchronous rectifier step-down** | high-current bench PSU | bench rail for HV module test |
| 1 | **DUTTY 5 A constant-V/I step-down with display** (USB + buttons) | adjustable + display | bench rail |
| 1 | **DUTTY 5 A constant-V/I step-down 4–38 V** (low ripple) | adjustable | low-noise rail |
| 1 | **DROK Boost-Buck 5.5–30 V to 0.5–30 V, 4 A 35 W, LCD** | bidirectional | versatile bench |
| 2 | **Pololu U3V12F12 12 V step-up** | 12 V boost | clean 12 V rail |
| 1 | **Buck DC-DC 6–24 V → 5 V 3 A** (USB car-charger style) | clean 5 V from 12 V | Pi 4 rail from boosted battery |
| 5 | **Icstation 1–5 V → 5 V 500 mA boost** | low-power boost | small loads |
| 10 | **Dorhea MT3608 2–24 V → 5–28 V 2 A boost** (µUSB in) | mid-power boost | many copies |
| 10 | **Eiechip MT3608 2–24 V → 5–28 V 2 A boost** (µUSB) | mid-power boost | duplicate of above |
| 5 | **WINGONEER SX1308 2–24 V → 2–28 V 2 A boost** | small boost | |
| 2 | **Generic 2-pack boost converter, adjustable** | step-up | |

### 4.4 Backup / UPS modules

| Qty | Item | Notes |
|---|---|---|
| Several | **Battery-backup / mini-UPS modules** outputting 12 V / 9 V / 5 V | bench fail-over for Pi 4 during long-session logging |
| 10 | **500 F 2.7 V supercaps** (35×60 mm) | **HV-pulse current reservoir** if needed for coil; or smoothing for noisy rails |

### 4.5 Power connectors

| Qty | Item |
|---|---|
| 6 | DC barrel jacks 5.5×2.1 mm threaded female (Ruibapa) |
| 500 | Auto/electrical pin terminals 1–3.5 mm M/F (Swpeet kit) |
| 700 | Automotive 2–9 pin connectors + 4 mm bullet (Swpeet) |

### 4.6 High voltage / Very high voltage

| Qty | Item | Output |
|---|---|---|
| 5 | **VHV Generator 1000 kV** modules | extreme HV (bench-only, treat as live always) |
| 5 | **VHV Generator 400 kV** modules | extreme HV |
| 3 | **OCESTORE 3.6–6 V → 20 kV arc/pulse** | wiki-coil-drive class |
| 1 | **DC 3.6–12 V → 3–11 kV boost** | medium HV |
| 2 | **JESSINIE 3.7 V → 1800 V arc/pulse** | low-end HV |
| 1 | **30 kV ignition boost coil** (3.5–7 V in) | automotive-class |
| 1 | **15 kV pulse generator inverter** (2 sets of parts) | DIY ignition |

**Safety note:** *Every one of these will kill you if mishandled.* They stay in their bench drawer until enclosed, current-limited, and on a Faraday-bagged test rig. **No HV module touches the helm chassis until Mk1.2 coil-drive bring-up has passed all bench gates.** See [safety.md](safety.md).

---

## 5. Fabrication

### 5.1 PCB fabrication

| Qty | Item | Notes |
|---|---|---|
| 1 | **Genmitsu CNC 3018-PRO** (GRBL, 300×180×45 mm work area) | **PCB mill confirmed; bifilar coil fab path enabled** |
| 10 | **Chanzon single-sided copper-clad 70×100 mm** | **stock for bifilar coil milling** (note: single-sided only — see [mk0_pcb_bifilar_coil.md § 1.4](mk0_pcb_bifilar_coil.md) for single-sided fallback geometry) |
| 18 | **Pure copper sheet kit** (3 sizes, 0.02" / 0.5 mm thick) | EMI shield / antenna ground plane / coil shield |
| 1 set | **MK10 nozzles + 3D printer cleaning tools** | (3D-print tooling, adjacent) |

**Important:** stock is **single-sided** copper-clad. The wiki-canonical bifilar coil is two-layer series-opposing. We need **either** (a) double-sided stock procured (~$15 for a small batch) **or** (b) the single-sided fallback geometry (two side-by-side spirals on one face, connected by an underside jumper). The single-sided path **does work** but loses the through-substrate E-field — we get dipole cancellation but not the high-V inter-layer gradient.

**Decision pending:** procure 5–10 pieces of double-sided FR4 70×100 mm (~$15) or proceed with single-sided fallback. Operator's call given the budget posture.

### 5.2 Hand tools / mechanical

| Qty | Item |
|---|---|
| 1 | Silbingan 24-in-1 precision screwdriver set |
| 1 | Rustark 3D-print finishing tool kit (42 pcs) |
| 1 | Build plate stickers (QIDI X-MAX) |
| ≥4 sets | M3/M4 + M1–M1.6 + M6 screw / nut / washer kits |
| 1 | 800-pc flat washer kit M2–M12 |
| 1 | 220-pc fender washer M3–M12 |
| 1 | 140-pc hex flange nut kit M3–M12 |
| 1 | 100-pc + 148-pc + 200-pc spring assortment kits |
| 1 | Grommet hand press + 500× 3/8" grommets |
| 1 | Heat-shrink tubing 200-pc 1.5–10 mm |

### 5.3 Test equipment

| Qty | Item | Notes |
|---|---|---|
| 1 | **YEAPOOK ADS1014D dual-channel DSO** (100 MHz BW, 1 GS/s, 2 ch, 240 Kb depth, built-in signal generator + 14 wave types) | **wiki coil drive band (1–8 MHz) is comfortably in scope passband; 5× over-sampling at 8 MHz; built-in signal gen replaces a function generator** |

---

## 6. Passives + ICs

| Qty | Item | Notes |
|---|---|---|
| 1 | **5228-pc XXXL component kit** (caps, transistors, pots, diodes, ICs, inductors, regulators, MOSFETs, trim pots, LEDs, PCB scrap, photoresistors, terminals, resistors) | the catch-all passive stash |
| 1 | **240-pc tactile push-button kit** (24 values) | UI / debug |
| 1 | **180-pc 6×6 mm tactile push-button kit** (10 values) | UI |
| 1 | **60-pc potentiometer kit** B5K–B100K (Taiss) | analog UI |
| 1 | **100-pc WH148 pot kit** B1K–B1M (Taiss) | analog UI |
| 1 | **150-pc 6mm pot kit** 100Ω–2MΩ (Taiss) | analog UI |
| 1 | **64-pc WH148 pot kit** B5K–B100K (TWTADE) | analog UI |
| 1 | **70-pc 14-value voltage regulator transistor kit** TO-220 (L7805…L7915, LM317) | linear regs |
| 1 | **2-position boat rocker switch kit** (20 pc) | power switching |
| Various | **22/20/18 AWG silicone hookup wire** 7-color sets | wiring |
| Many | **EDGELEC Dupont jumper wires** 20 cm M/M, M/F, F/F | breadboard |
| 1 | **635-pc 2.54 mm Dupont housing + pin kit** + 5-ft 10-wire ribbon | wiring |
| 1 | **Copper magnet wire spools + audio cable spools + enameled wire** (various gauges, heavy stock) | **hand-wound coil stock if PCB-coil path fails or for solenoid alternatives** |
| 1 | **BNTECHGO 20 AWG enameled magnet wire**, 1.0 lb spool, 0.0315" Ø, 155°C-rated | **wiki Mk1-class hand-wound bifilar coil stock** — ~315 ft per lb at 20 AWG; ample for multiple 30×30 mm coil rewinds + Mk2 solenoid experiments |
| 25 | **E BAVITE neodymium bar magnets 60×10×3 mm, double-side-adhesive** | calibration jig + experimental field generators |
| 7 | **Junarter neodymium cube magnets** | calibration / DIY field sources |
| 100 | **LOVIMAG neodymium cube magnets 10×10×10 mm** (2× 50-pc packs) | uniform-cube experimental field arrays; ferrofluid-pattern jigs |
| 500 (mixed) | **Small magnets, 7 sizes** | fridge-mag class; cumulative field sources |

---

## 7. Thermal management

| Qty | Item | Notes |
|---|---|---|
| 1 | **Lsgoodcare 5V USB Peltier kit** + 1 **KOOBOOK 12V Peltier kit** | active cooling for HV-module enclosure |
| 4 | **40 mm Al heatsinks** | TEC1-12706 + stepper / MOSFET / regulator |
| Multiple | **Heatsink + Peltier modules** (in adjacent items) | thermal control |

---

## 8. Shielding / specialty materials

| Item | Notes |
|---|---|
| **Faraday fabric** (silver/nickel-plated textile) | EMI cavity inside helm + sham coil pouch |
| **Industrial EMI/RFI shielding spray** (conductive paint) | inside enclosures, grounded |
| **Ferrofluid** | passive magnetic damper / field-line visualizer (Mk2 demo + QA) |

---

## 9. Procurement gap (what we do NOT have)

| Item | Cost | Priority | Use |
|---|---|---|---|
| **Double-sided 70×100 mm FR4 copper-clad** (5–10 pc) | ~$15 | **medium-high** — enables wiki-canonical two-layer bifilar | coil PCB |
| Polar H10 chest strap | ~$80 | medium | Mk1 Stabilizer HRV gold standard |
| Bone-conduction transducer pair | ~$10 | low (we have 6× 40 mm full-range that can substitute on cheek/temple) | Harmonizer |
| Si5351 breakout if we want exact wiki carrier IC | ~$5 | low (ESP32 LEDC PWM substitutes natively in 1–8 MHz) | coil carrier |
| nRF52840 dev board (Adafruit Feather / XIAO BLE) | ~$15 | low (Heltec LoRa 32 substitutes) | BLE-only path |

**Total procurement gap < $130. Of that, the $15 double-sided FR4 batch is the only item that actually unlocks a meaningful capability we don't already have.**

---

## 10. Wiki Mk1 BOM coverage — final tally

| Wiki Mk1 module | Coverage from this inventory |
|---|---|
| **HelmKit core (frame + MCU + sensors + OLED + bus)** | ✅ complete (Pi 4 + Nano + Heltec LoRa 32 OLED + 9-axis IMU + dual sensor kits) |
| **Stabilizer Mk1** | ✅ ~95% (bifilar coil fab path via CNC; ESP32 PWM at 1–8 MHz; HV/medium-HV drive modules; Polar H10 is only gap, can substitute Pi-sensor-kit PPG if MAX30102 present) |
| **Harmonizer Mk1** | ✅ ~90% (same as Stabilizer + Schumann envelope via XR2206; bone-conduction substitutable by 40 mm full-range against bone) |
| **Defender Mk1** | ✅ complete (HackRF One + 3× NESDR + Ham It Up + 9-axis IMU dual for gradiometer + MLX90640 thermal + SGP40 VOC + DSO for emission verification) |
| **Platform safety floor** | ✅ complete (Faraday fabric + EMI spray + DS18B20 thermistor + relays + supercaps for surge + Peltier for HV-module cooling) |

**Verdict:** Inventory clears wiki Mk1 spec end-to-end. The only hardware purchase that meaningfully changes the achievable build is **$15 of double-sided FR4** to enable the two-layer bifilar coil geometry exactly as the wiki specifies. Everything else is a substitution within engineering-equivalent envelopes.

---

## 11. Open items (continue inventory pass)

- [x] ~~**9-axis IMU module(s)** — count, exact part number(s), confirm I²C address(es)~~ — resolved §3.1: 3× MPU9250 (CHENBO×2 + HiLetgo×1) + 1× MPU6050 (Diymore)
- [ ] **USB-C power bank(s)** — count, capacity (mAh), output current rating
- [ ] **Shielded cable / coax / twisted pair** stock
- [ ] **PCB CNC bit set** — V-bit angles, end-mill diameters, drill sizes available
- [ ] Specific HV module enable-pin behavior (active-high vs active-low, opto-isolation present?)
- [ ] **Spare 18650 holders** — confirm 2-cell holders for wiki-spec series pack
- [ ] **BMS / protection boards for 2S 18650 pack** — likely in TP4056-adjacent stock

---

## 12. Cross-refs

- [inventory_capability_map.md](inventory_capability_map.md) — coverage matrix vs wiki BOM (now backed by this inventory)
- [sprint_0.2_circuit_spec.md](sprint_0.2_circuit_spec.md) — circuit spec referencing these parts
- [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) — fab spec for the coil
- [wiki_synthesis.md § Pass 2](wiki_synthesis.md) — wiki BOM source
- [safety.md](safety.md) — HV/VHV safety posture
