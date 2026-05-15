# HelmKit Sensor Roster — In-Inventory + Purchase Candidates

**Companion to:** [modes.md](modes.md). This document maps the **sensor catalog** (what each sensor measures, what it costs, which mode-tuples need it) so purchase decisions can be made against the mode roadmap.

**Status:** Mk1-era roster, May 2026. Inventory snapshot per [inventory.md](inventory.md) (operator-confirmed 2026-05-12) plus [MAX30102 PPG breakout added 2026-05-14 per psiStabilizer v0.1 buy list].

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

## 2. What's already in inventory (Mk1-relevant)

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

### 3.1 Tier-1 — directly enables Mk1 Tranquil + Combat

| # | Item | Axis | $ Amazon | $ AliExpress | Modes enabled | Notes |
|---|---|---|---:|---:|---|---|
| **P1** | **EMG module + electrodes** (MyoWare clone or AD8232) + Ag/AgCl ECG electrode bag (50×) + snap-to-TRS cable | Motor activation | $12 + $5 + $3 = **$20** | $8 + $4 + $2 = **$14** | **Combat ✅✅** | The single highest-value purchase for Combat Mode. Deltoid placement = strike-tension detector. |
| **P2** | **MLX90614 IR temp** (GY-906 breakout) | Peripheral vasomotor | $8 | $3 | Tranquil ◐, Combat ◐, Social ✅, Recovery ✅ | Non-contact forehead, fast (~150 ms), robust to sweat. Best single skin-temp choice. |
| **P3** | **MAX30205 contact temp (×2)** | Peripheral vasomotor (absolute) | $12 each → $24 for two | $4–6 each → $10 for two | Tranquil ◐, Combat ◐, Social ✅, Recovery ✅✅ | Clinical 0.1°C accuracy. Two units → dual-temple differential, or temple+wrist central-vs-peripheral. Three address-select pins → can grow to 8 units on one bus. |
| **P4** | **EDA / GSR**: CJMCU-6701 module + Ag/AgCl electrodes (shared bag with P1) | Sympathetic arousal | $8 (electrodes already in P1) | $3 | Tranquil ✅, Combat ◐ (motion-noisy), Vigilance ✅, Recovery ◐ | Adds sympathetic axis. Tranquil-mode-rock-solid; Combat-mode-secondary due to motion artifact. |
| **P5** | **Polar H10 chest strap ECG** | Vagal tone (gold-standard) | $80–90 | $40–50 (refurb) | All HRV-using modes | Cross-validates the MAX30102 PPG. Single biggest credibility upgrade for G1 instrumentation-grade evidence. **Expensive relative to budget.** |

**P1 + P2 + P3(×2) + P4 = $60 Amazon / $30 AliExpress.** Buys EMG (Combat unlock), IR + contact temp redundancy, and EDA. Leaves $25 of the $85 budget for Polar H10 down the road or other extras.

### 3.2 Tier-2 — Mk2 modes

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

## 4. Budget allocation against $85

### Plan A — "Full Mk1 sensor stack" — $60 Amazon

| Item | $ |
|---|---:|
| P1 EMG (MyoWare clone + electrodes + cable) | $20 |
| P2 MLX90614 IR temp | $8 |
| P3 MAX30205 contact temp (×2) | $24 |
| P4 EDA module | $8 |
| **Subtotal** | **$60** |
| **Reserve** | **$25** |

**What this gets you:** Combat Mode unlocked (EMG). Tranquil Mode upgraded (EDA + temp). Sham-equivalence thermal channel hardened (dual MAX30205). Reserve $25 for: respiration belt, RT tactor parts, or saving toward Polar H10 ($80–90).

**Modes unlocked at Mk1 with this plan:** Tranquil ✅, Combat ✅, Social-precursor ✅, Recovery-precursor ✅. Three out of seven non-dyadic modes operational at Mk1.

### Plan B — "Aggressive Combat focus" — $50 Amazon

| Item | $ |
|---|---:|
| P1 EMG (MyoWare clone + electrodes + cable) | $20 |
| P2 MLX90614 IR temp | $8 |
| P3 MAX30205 contact temp (×1, not ×2) | $12 |
| P4 EDA module | $8 |
| Extra Ag/AgCl electrodes (100-pack bulk) | $5 |
| **Subtotal** | **$53** |
| **Reserve** | **$32** |

**Trade-off vs Plan A:** lose dual-temple differential temp; gain ~$30 toward Polar H10 saving.

### Plan C — "Cross-validation first" — $85 Amazon

| Item | $ |
|---|---:|
| P5 Polar H10 chest strap (refurbished) | $50 |
| P1 EMG (MyoWare clone + electrodes + cable) | $20 |
| P2 MLX90614 IR temp | $8 |
| (no EDA, no MAX30205) | — |
| **Subtotal** | **$78** |
| **Reserve** | **$7** |

**Trade-off:** sacrifices EDA + clinical-precision contact temp; **gains G1-grade HRV cross-validation** (the strongest possible single boost to scientific credibility of the project). EMG still in for Combat Mode. MLX90614 still in for fast vasomotor.

### Plan D — "AliExpress maximizer" — ~$30 AliExpress + 3-week wait

| Item | $ |
|---|---:|
| P1 EMG module | $8 |
| Electrodes (200-pack from AliExpress) | $5 |
| P2 MLX90614 (GY-906) | $3 |
| P3 MAX30205 ×2 | $10 |
| P4 EDA module | $3 |
| **Subtotal** | **~$30** |
| **Reserve** | **~$55** for Polar H10 or other |

**Trade-off:** 2–3 week shipping delay; somewhat-spotty quality assurance. Best value if Mk1 timeline allows the delay. Reserve nearly covers a Polar H10.

---

## 5. Recommendation

**Plan A if you want the full Mk1 multi-mode stack now.** Plan C if cross-validation credibility matters most for the prior-art / scientific-evidence track. Plan D if you can wait 3 weeks and want maximum hardware per dollar.

**Operator-preference factors to weigh:**

- **Timeline.** If Mk1 session-protocol bench validation is starting this week, Amazon shipping (Plan A or C) wins. If it's a month out, Plan D wins.
- **Primary use case.** Combat Mode is the flagship; EMG is non-negotiable. All four plans include EMG.
- **Validation philosophy.** If you want the *strongest possible defense* against "but your sensor is just a toy" critique, Plan C with the Polar H10 is the answer. If you want *the most modes operational*, Plan A.
- **Mode breadth.** Plan A activates the most modes; Plan C activates the fewest but at higher quality.

### Default recommendation: **Plan A**.

Reasoning: Mk1 is about demonstrating that **the platform** works across multiple modes. Plan A activates Tranquil + Combat as flagship pair and seeds the precursors for Social and Recovery. The $25 reserve is enough to add a Polar H10 in 1–2 paychecks. EMG-for-Combat is the load-bearing buy, and Plan A includes it. The MAX30205 ×2 lets you do dual-temple differential thermography — that's a small but real instrumentation advantage no competitor wearable has.

If you have any concern about the Combat-Mode use case dominating Mk1 attention vs Tranquil Mode being the easier near-term G2 win, downgrade P3 from ×2 to ×1 and add the $12 saving to your Polar H10 fund (effectively Plan B).

---

## 6. Mode-by-purchase decision table

What modes each plan activates at Mk1.

| Mode | Plan A | Plan B | Plan C | Plan D |
|---|:--:|:--:|:--:|:--:|
| **Tranquil** | ✅ full | ✅ full | ◐ no EDA | ✅ full |
| **Combat** | ✅ full | ✅ full | ✅ full | ✅ full |
| Focus | ⏸ Mk2 | ⏸ Mk2 | ⏸ Mk2 | ⏸ Mk2 |
| Creative | ⏸ Mk2 | ⏸ Mk2 | ⏸ Mk2 | ⏸ Mk2 |
| Vigilance | ◐ EDA only | ◐ EDA only | — | ◐ EDA only |
| Social-precursor | ✅ dual temp | ◐ single temp | ◐ IR only | ✅ dual temp |
| Recovery-precursor | ✅ | ◐ single temp | ◐ IR only | ✅ |
| Dyadic | ⏸ Mk3 | ⏸ Mk3 | ⏸ Mk3 | ⏸ Mk3 |
| **G1 cross-validation** | ⏸ Polar later | ⏸ Polar later | ✅ Polar now | ⏸ Polar later |

---

## 7. Next decision required

Operator picks A / B / C / D / a hybrid → I write the purchase list and the firmware-side capture-loop work-items, plus the matching `PRIOR_ART.md` update adding EMG / EDA / dual-temp inventive elements.
