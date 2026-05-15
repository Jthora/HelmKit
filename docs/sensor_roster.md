# HelmKit Sensor Roster — In-Inventory + Purchase Candidates

**Companion to:** [modes.md](modes.md). This document maps the **sensor catalog** (what each sensor measures, what it costs, which mode-tuples need it) so purchase decisions can be made against the mode roadmap.

**Status:** Mk0.5-era roster, May 2026 (seven-step ladder per [mk_ladder.md](mk_ladder.md)). Inventory snapshot per [inventory.md](inventory.md) (operator-confirmed 2026-05-12) plus MAX30102 PPG breakout added 2026-05-14, plus **Sensor Wave 1 + Wave 2 purchase orders placed 2026-05-14** (see [§4](#4-the-actual-purchase-ledger-may-2026))—the Mk0.5 sensor stack is on-order.

---

## 1. Axes of physiological measurement

Stabilizing or steering "psyche state" decomposes into independently-measurable axes. The HelmKit's evidentiary strategy is **multi-axis convergence**: a claim is credible when independent sensors looking at independent axes all move together. No single sensor is the validator; **the study design is the validator**, and the sensor stack is its input.

| Axis | What it measures | Primary sensor candidates |
|---|---|---|
| **Parasympathetic / vagal tone** | "Calm regulation" capacity — heart-rate variability via PPG or ECG | MAX30102 PPG, Polar H10 ECG |
| **Sympathetic arousal** | "Fight-or-flight" activation — skin conductance | EDA / GSR module |
| **Motor activation** | Muscle tension / effort | Surface EMG |
| **Movement / posture** | Linear + rotational kinematics, orientation, sway | IMU 9-DoF |
| **Peripheral vasomotor** | Skin-surface temperature reflecting blood-flow shunting | MLX90614 IR, MAX30205 contact, DS18B20 contact |
| **Cortical state** | Spectral signatures of arousal, focus, drowsiness, etc. | EEG (Muse / OpenBCI) |
| **Cognitive performance** | Reaction time, attention, inhibition | Button-press tactor; software cognitive batteries |
| **Respiratory** | Breath rate, depth, I:E ratio | Respiration belt; derivable from PPG envelope |
| **Visual** | Pupil diameter (LC-noradrenergic arousal), saccade, fixation | Eye-tracking camera |
| **Vocal** | Speech prosody, F0 jitter, speech rate | Mic + DSP |
| **Environmental context** | Confound control — ambient temp, light, EMI, location | BME280, RM3100, GPS, TSL2591 |

---

## 2. What's already in inventory (Mk0.5-relevant)

Pulled from [inventory.md §3](inventory.md). **You already own all of the following.**

| Sensor in stock | Axis | Mk1 fitness | Notes |
|---|---|---|---|
| **MAX30102 PPG** (just acquired) | Vagal tone (HRV) | ✅ primary | Cornerstone Mk1 sensor. Forehead or wrist placement. |
| **MPU9250 9-DoF IMU ×3** | Movement / posture | ✅ primary for Combat | Head pose, sway, strike detection, guard recovery. Multiple addresses available. |
| **MPU6050 6-DoF IMU** | Movement (decoupled bus) | ✅ MCU-B watchdog | Safety-channel "helm-on-ground" detector. |
| **DS18B20 contact temp** | Peripheral vasomotor | ⚠️ workable | Slow (~750 ms), bulky probe head, accuracy ±0.5°C. Usable but not ideal. Better upgrade path: MLX90614 or MAX30205. |
| **MLX90640 thermal IR array** (32×24 px, 55° FOV) | Peripheral vasomotor + Defender vision | ✅ powerful | Full thermal *image*, not just a spot. Overkill for Mk1 stabilizer; perfect for Mk1.5+ Defender or post-session debrief. |
| **LM35 analog temp + analog temp module** | Peripheral vasomotor | ◐ workable | Backup contact-temp; not as accurate as MAX30205. |
| **Capacitive Touch** (Pi4 starter kit) | Wearer presence | ✅ safety | Used by dual-MCU interlock: "is the helm on a head?" |
| **Thin-film Pressure** (Pi4 starter kit) | Fit verification | ✅ Mk1 G1 gate | Verifies headpiece is properly seated. |
| **PIR Motion ×2** (both kits) | Proximity | ◐ | Could trigger session-start when wearer approaches the chair. |
| **Vibration sensor** (Smart Home kit) | Mechanical event | ◐ | Could detect strike impacts in Combat Mode (but IMU is better). |
| **Photosensitive light + TEMT6000 + GUVA-S12SD** | Ambient light + sham control | ✅ sham gate | Used in six-channel sham-equivalence spec. |
| **DHT11 / BMP180 / SGP40** | Environmental | ✅ confound control | Head-cavity climate logging. |
| **MQ-2 / MQ-5 / MQ-7 / Flame** | Environmental hazard | — | Defender / lab safety; not mode-active. |
| **PCF8591 ADC (Pi4 starter kit)** | Analog front-end | ✅ enabler | Reads any analog sensor onto the Pi 4 I²C bus. EDA / EMG / LM35 plug in here. |
| **Bone-conduction-class audio drivers (40 mm)** + Bluetooth amp ×2+ | Feedback output | ✅ primary | Breath pacer, HRV-coherence tone, tension alarm, strike cadence. |
| **GY-9250 / GY-521 IMU** | Combat motor channel | ✅ ready | Already noted above; restated for emphasis — Combat Mode head-pose channel is free. |

**The takeaway:** the *output* side and most of the *contextual* side of the HelmKit is already covered. The gaps are on the **operator-physiology** side: EMG, EDA, and a proper skin-temp sensor. PPG just landed.

---

## 3. The purchase candidate roster

What you might buy. Costs are May 2026 Amazon US ballpark unless noted.

### 3.1 Tier-1 — directly enables Mk0.5 floor + Mk1.0 Tranquil + Mk1.5 Combat

| # | Item | Axis | $ Amazon | $ AliExpress | Modes enabled | Notes |
|---|---|---|---:|---:|---|---|
| **P1** | **EMG module + electrodes** (MyoWare clone or AD8232) + Ag/AgCl ECG electrode bag (50×) + snap-to-TRS cable | Motor activation | $12 + $5 + $3 = **$20** | $8 + $4 + $2 = **$14** | **Combat ✅✅** | The single highest-value purchase for Combat Mode. Deltoid placement = strike-tension detector. |
| **P2** | **MLX90614 IR temp** (GY-906 breakout) | Peripheral vasomotor | $8 | $3 | Tranquil ◐, Combat ◐, Social ✅, Recovery ✅ | Non-contact forehead, fast (~150 ms), robust to sweat. Best single skin-temp choice. |
| **P3** | **MAX30205 contact temp (×2)** | Peripheral vasomotor (absolute) | $12 each → $24 for two | $4–6 each → $10 for two | Tranquil ◐, Combat ◐, Social ✅, Recovery ✅✅ | Clinical 0.1°C accuracy. Two units → dual-temple differential, or temple+wrist central-vs-peripheral. Three address-select pins → can grow to 8 units on one bus. |
| **P4** | **EDA / GSR**: CJMCU-6701 module + Ag/AgCl electrodes (shared bag with P1) | Sympathetic arousal | $8 (electrodes already in P1) | $3 | Tranquil ✅, Combat ◐ (motion-noisy), Vigilance ✅, Recovery ◐ | Adds sympathetic axis. Tranquil-mode-rock-solid; Combat-mode-secondary due to motion artifact. |
| **P5** | **Polar H10 chest strap ECG** | Vagal tone (gold-standard) | $80–90 | $40–50 (refurb) | All HRV-using modes | Cross-validates the MAX30102 PPG. Single biggest credibility upgrade for G1 instrumentation-grade evidence. **Expensive relative to budget.** |

**P1 + P2 + P3(×2) + P4 = $60 Amazon / $30 AliExpress.** Buys EMG (Combat unlock), IR + contact temp redundancy, and EDA. Leaves $25 of the $85 budget for Polar H10 down the road or other extras.

### 3.2 Tier-2 — Mk2.0 modes

| # | Item | Axis | $ | Modes enabled | Notes |
|---|---|---|---:|---|---|
| **Q1** | **OpenBCI Ganglion 4-ch** | Cortical (EEG) | $250 | Focus, Creative, Vigilance, Recovery, Dyadic | Research-grade hobbyist EEG. **Out of $85 budget** — Mk2 spend. |
| **Q2** | **Muse 2 / Muse S** | Cortical (EEG) | $250 new / ~$100 refurb | Same as Q1 | Consumer-grade EEG; well-validated; SDK exists. **Out of $85 budget.** |
| **Q3** | **Respiration belt** (Vernier or DIY strain gauge) | Respiratory | $20–60 | Tranquil ◐, Combat ✅, Recovery ◐ | Direct breath measurement. Mk1.5-relevant for Combat tactical-breathing training. |
| **Q4** | **Reaction-time tactor** (vibration motor + button + wire) | Cognitive performance | $5 (already have from kits?) | Combat ◐, Vigilance ✅, Focus ◐ | Trivial DIY. Likely buildable from existing kit modules. |
| **Q5** | **Hand-grip dynamometer** (HX711 + strain) | Stress-strength | $20 | Combat ◐ | Classic stress-grip metric. Not high-priority. |
| **Q6** | **Eye tracker (Pupil Labs / cheap Tobii)** | Visual | $200+ | Focus, Creative, Vigilance | Out of scope until Mk2. |

### 3.3 Free-from-inventory upgrades

These don't require purchase — just plumbing decisions:

- **MLX90640 thermal IR camera** — already in stock. Use as a *post-session debrief* tool (snap a thermal image at minute 0 and minute 30 of every session; trend the vasomotor map over weeks). Doesn't need to be live.
- **MPU9250 IMUs** — three of them, one already targeted for head pose. Allocate one for Combat-Mode wrist mounting (in-glove or wristband) for strike-velocity measurement.
- **MPU6050 on MCU-B** — already targeted as safety-watchdog "helm-on-ground." No additional plumbing.
- **GUVA-S12SD UV / TEMT6000 / Photosensitive** — already wired for sham-equivalence visual channel.
- **Capacitive touch + thin-film pressure** — already wired for "is helm on wearer's head with proper fit" G1 gate.
- **Audio drivers + Bluetooth amp** — already wired for all feedback output.
- **PCF8591 ADC** — already wired as analog front-end for EDA / EMG / LM35.

---

## 4. The actual purchase ledger (May 2026)

The abstract Plan A / B / C / D analysis that historically lived here has been replaced with the **decision made and acted on 2026-05-14**: a hybrid leaning to Plan A, executed as a two-wave Amazon order (~$76 of an $88.23 gift-card balance, paid via Prime trial). The decision rationale is preserved in commit `cc352d8` history.

### 4.1 Wave 1 — Prime, ETA 2026-05-16

The fast-shipping items that gate the Mk0.5 firmware bringup (see [mk0.5_firmware_bringup.md](mk0.5_firmware_bringup.md)).

| Item | Role | $ | Mk gate served |
|---|---|---:|---|
| **CJMCU-6701 GSR module** (Amazon listing titled "SPI Measurement…" — Chinese listing copy-paste artifact; module is **analog out**, 3.5 mm TRS jack) | EDA / sympathetic arousal | $16.99 | Mk0.5 G1, Mk1.0 Tranquil |
| **EC Buying GY-906 MLX90614** IR temp breakout | Peripheral vasomotor (non-contact) | $12.59 | Mk0.5 G1, Mk1.0 Tranquil |
| **3M Red Dot 2560 Ag/AgCl electrodes** (50-pack clinical-grade ECG monitoring electrodes) | Biopotential sensing electrode — *not* TENS stim pads | $9.96 | All biopotential channels (GSR Mk0.5; EMG Mk1.5; ECG cross-val if Polar deferred) |
| **VOVOU 3.5 mm TENS leads** (snap-to-3.5 mm TRS, direction-agnostic copper — fine for sensing despite "TENS" branding) | Cable, electrode → module | $7.59 | Wires both GSR + (later) EMG |
| **Wave 1 subtotal** | | **$47.13** | |

### 4.2 Wave 2 — slow ship, ETA 2026-05-27 → 2026-06-15

The items that don't block Mk0.5 firmware bringup but land in time for Mk1.0 / Mk1.5.

| Item | Role | $ | Mk gate served |
|---|---|---:|---|
| **AD8232 "Measurement Beat Sensor"** (board + 3-lead cable + pads bundle) | Biopotential amplifier — sold as ECG; used here for **EMG via filter swap** for Mk1.5 Combat | $13.09 | Mk1.5 Combat (EMG primary) |
| **MAX30205MTA** (clinical contact temp, ±0.1 °C, I²C, address-selectable) × 1 | Peripheral vasomotor, temple A | $16.00 | Mk1.0 Tranquil dual-temple thermography |
| **MAX30205MTA** × 1 (with ship) | Peripheral vasomotor, temple B | $5.70 ship | (same; the dual unit enables differential) |
| **Wave 2 subtotal** | | **$34.79** | |

### 4.3 Combined totals + status

| | Amount |
|---|---:|
| Wave 1 + Wave 2 hardware | **$81.92** |
| Prime trial fee (one-time) | $2.00 |
| Tax estimate | est. $4–10 |
| Gift-card balance available | $88.23 |
| **Out-of-pocket** | **$0 (covered by gift card)** |

### 4.4 Items rejected during cart review (caught 2026-05-13)

Documented here as anti-precedent. Future buying decisions should re-check these.

| Rejected item | Why rejected |
|---|---|
| MyoWare 2.0 **Link Shield** ($13.50) | Not a muscle sensor; an Arduino shield accessory that *connects* to a MyoWare sensor. Replaced with AD8232 (true biopotential amplifier IC). |
| Second/duplicate GSR module (Grove GSR $34.50) | Two GSR modules in cart at once; kept the cheaper CJMCU-6701 at $16.99. |
| NURSAL TENS pads ($7.99) | TENS pads are carbon/rubber for **stimulation**, not Ag/AgCl for **sensing**. Wrong chemistry for biopotential pickup. Replaced with 3M Red Dot 2560. |
| VOVOU 2.35 mm TENS leads | Wrong plug diameter for the CJMCU-6701 jack. Plug-diameter verification discipline now codified in `/memories/hardware_buying.md`: never infer connector size from photo alone. |

---

## 5. Mode unlock matrix at each Mk gate, given the actual purchase

| Mode | Mk0.5 (Wave 1 only) | Mk1.0 (+ Wave 2) | Mk1.5 (+ Wave 2 EMG live) | Mk2.0 (+ EEG capex) |
|---|:--:|:--:|:--:|:--:|
| **Tranquil** | ✅ floor (PPG + GSR + IR-temp + audio) | ✅ + stim + dual-temple differential | ✅ | ✅ + EEG-driven |
| **Combat** | ⏸ deferred | ⏸ deferred | ✅ (EMG + IMU + sweat-tolerant electrodes) | ✅ |
| Focus | ⏸ | ⏸ | ⏸ | ✅ |
| Creative | ⏸ | ⏸ | ⏸ | ✅ |
| Vigilance | ◐ GSR-only partial | ◐ GSR-only partial | ◐ GSR-only partial | ✅ |
| Social-precursor | ◐ IR-temp only | ✅ dual-temple differential | ✅ | ✅ |
| Recovery-precursor | ◐ IR-temp only | ✅ dual-temple differential | ✅ | ✅ |
| Dyadic | ⏸ | ⏸ | ⏸ | ⏸ Mk3.0 |
| **G1 cross-validation (Polar H10 chest ECG)** | ⏸ deferred ($80–90 future buy) | ⏸ | ⏸ | ⏸ |

---

## 6. Next purchases scoped (not ordered yet)

Things to add when budget or evidence justifies them:

- **Polar H10 chest-strap ECG, ~$80** — The single biggest G1-credibility upgrade. Cross-validates MAX30102 PPG. Defer until Mk0.5 G2 result is in; if positive, this becomes the strongest argument we have for "the floor really works."
- **Respiration belt, $20–60** — Direct breath measurement (currently derived from PPG envelope). Mk1.0 luxury; Mk1.5 Combat necessity for tactical-breathing training.
- **OpenBCI Ganglion 4-ch / Muse S, $100–250** — Mk2.0 prerequisite. EEG capex.
- **3M Red Dot 2560 refill 50-pack, ~$10** — Reorder when first pack hits ~10 remaining. ~3 pads per session × multiple weeks of ABAB depletes faster than expected.

---

## 7. Bench equipment (not sensors, but on-hand)

Tracked here because the bench-readiness audit (BLACKOUT_PLAN §2 Day 1) needs a single ledger. Promote to a dedicated `docs/inventory_bench.md` if this list grows past ~15 items.

| Equipment | Use | Mk gate where it activates | Status |
|---|---|---|---|
| **WANPTEK DPS3010U** programmable DC supply (0–30 V, 0–10 A, USB control) | Coil-driver bench bring-up; current-limited safety envelope for any stim-payload prototype | **Mk1.0** (Tranquil stim integration) — NOT used at Mk0.5 (USB-powered) | ✅ on hand. Safety lockout: any output ≥50 V open-circuit prohibited near the head per [external/psiStabilizer/docs/safety_guidelines.md HX-1](../external/psiStabilizer/docs/safety_guidelines.md). DPS3010U max output (30 V) is well below that ceiling — safe for benchwork but pre-commit to a 12 V cap at the helm interface. |
| USB-C data cable (not charge-only) | Heltec flash + monitor | Mk0.5 Day 1 | Required — verify with `pio device list`. |
| Breadboard + jumper wires | Sensor bring-up | Mk0.5 Day 2+ | TBD inventory check. |
| Multimeter | Pinout continuity verification (PINOUT.md §5) | Mk0.5 Day 1 afternoon | TBD inventory check. |
| Soldering iron + flux + solder | MAX30205 / AD8232 lead attach | Mk0.5 Day 4 (Wave 2) | TBD inventory check. |
| Digital calipers | 3D-print fit-checks | Mk1.0 enclosure | TBD. |
| Label tape (Brother / Dymo) | Sensor + cable identification | Mk0.5 Day 2 | TBD. |

**TBD items** are the actionable output of the Day 1 afternoon bench-readiness walk-through. Any "TBD" still standing at end-of-Day-1 either gets sourced from inventory or added to the Day 2 acquisition list.


