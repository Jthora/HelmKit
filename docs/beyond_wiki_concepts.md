# Beyond-Wiki Concepts — what the inventory enables that the wiki doesn't describe

**Status:** Speculative concept catalog. Not a build commitment. Each entry tagged with maturity gate.
**Date:** 2026-05-12
**Method:** systematic cross-reference of every inventory section against [wiki_synthesis.md](wiki_synthesis.md) BOMs. Items that appear in inventory but have no corresponding wiki use-case get inspected for **plausible adjacent builds**.

> **Epistemic stance:** This document is a *concept inventory*, not a research program. Items are tagged by:
> - 🟢 **Build-now** — buildable today; clear safety floor; no doctrinal risk
> - 🟡 **Build-after-gate** — buildable but needs an explicit gate (IRB, safety review, regulatory check) before any work
> - 🔴 **Document-only** — parts exist; should not be built without external oversight; included here so the temptation is named rather than buried

---

## 1. Compute hardware (wiki silent → inventory overstocked)

The wiki spec for the Stabilizer Mk1 is "Heltec LoRa 32 + bench Pi 4 for analysis." It has no plan at all for **22 GPUs, 1× AGX Orin (200 TOPS), 4× Jetson Nano boxes**. The wiki Resonant Finder Mk1 spec (workstation with 2× RTX 4080-class) is ~4× **less** compute than what we have.

See [gpu_farm_workloads.md](gpu_farm_workloads.md) for the full 7-workload analysis. The wiki-extending highlights:

- 🟢 **FDTD design-cert closure** ([sprint_0.3_fdtd_coil_design.md](sprint_0.3_fdtd_coil_design.md)) — the wiki demands this gate; nobody's met it yet.
- 🟢 **Metamaterial liner inverse-design** — design axis the wiki Defender section doesn't even mention.
- 🟢 **In-device Resonant-Finder-class scoring** — push Mk1 → almost-Mk2 by topology, not by money.

---

## 2. Photic stim hardware (wiki minimal → inventory wall-of-LEDs)

**Wiki status:** photic stim is mentioned briefly in Harmonizer / Stabilizer Mk1 as a single "photic stim LED at 7.83 Hz envelope." That's it.

**Inventory:** **730× IR LEDs + 365× UV LEDs + 10× Chanzon 3 W 365 nm UV COB + 10× uxcell 3 W 365 nm UV COB + 10× Chanzon 3 W 730 nm far-red COB + 10× Jammas 3 W 730 nm IR COB + 100× white 3 mm + GUVA-S12SD UV sensor + GEZEE G4 12 V daylight LEDs.**

### 2.1 🟢 Far-red 730 nm photobiomodulation halo (PBM helm liner)

730 nm photobiomodulation has a real published cognitive-effect literature (Gonzalez-Lima, Hamblin et al.). The wiki Harmonizer doesn't mention PBM at all. With 20× 3 W 730 nm COBs available, we can build a **PBM halo** ringing the inside of the helm at ~10 mW/cm² irradiance on the scalp — within the published-effective dose range.

- **Build:** 12–20 COBs on a flexible PCB strip routing inside the helm liner, each driven by a constant-current sink (already in the XXXL component kit), thermal-protected by DS18B20 + the HKWANTAT fans.
- **Safety floor:** scalp temp under DS18B20 watchdog ≤ 40 °C; total dose < 60 J/cm² per session.
- **Beyond-wiki value:** PBM is the **most evidence-supported single biomarker-modulating modality** in the entire helm concept space. Adding it is uncontroversial.

### 2.2 🟢 UV-A excitation channel + fluorescence imaging (visualization layer)

365 nm UV-A excites a huge range of fluorescent dyes + naturally fluorescent biological compounds. With 20× 3 W 365 nm COBs + 365× small UV LEDs + a **GUVA-S12SD UV detector** + the **ELP fisheye 8MP camera** + the **MLX90640 32×24 thermal array**, the helm becomes a **multispectral imaging rig**.

- **Build:** pulse-modulate UV-A; gate camera capture to UV-OFF window; image visible + thermal in same frame. Fluorescent dye on test coupons (or naturally-fluorescent skin) becomes a session-traceable provenance marker.
- **Beyond-wiki value:** the wiki has no concept of *imaging* the operator's session beyond an HRV trace. This is a *Field Recorder Mk1.5* extension that produces visually striking, repeatable artifacts — useful for both science (false-positive control, session provenance) and outreach.

### 2.3 🟡 Patterned IR scene illumination for dark-room Psi Recorder

730× small IR LEDs is enough to flood-illuminate a sealed dark room. Combined with the ELP camera (visible+IR sensitive without IR-cut filter), this produces a **night-vision Psi Recorder** for sleep-state sessions which the wiki gestures at but doesn't equip. Gate: operator-aware consent for video capture during sleep.

---

## 3. Magnetic & high-field hardware (wiki minimal → inventory absurdly stocked)

**Wiki status:** Stabilizer Mk1 uses 2× N52 magnets in the coil. Defender doesn't really discuss bulk magnets.

**Inventory:** **~1700+ neodymium pieces** (1047 bars, ~100+ cubes, 6× 150 lb cup magnets, 6× DC electromagnets including 2× 800 N).

### 3.1 🟢 Halbach-array static-field bias for the bifilar coil

A Halbach array of small N52 bars (we have hundreds) produces a one-sided, ~Tesla-class static bias field. The wiki coil is purely AC-driven. **Biasing the AC drive with a static field shifts the magnetization-curve operating point** and may dramatically change the in-cavity field profile.

- **Build:** 16–24 LOVIMAG 25×5×3 bars in a 1D Halbach behind the coil PCB; sweep coil with HackRF in/out of bias to characterize.
- **FDTD support:** the GPU farm can pre-compute the bias-modified field map (W3 in [gpu_farm_workloads.md](gpu_farm_workloads.md)).
- **Beyond-wiki value:** the wiki Defender treats the coil as a linear device. Static-bias operation explores nonlinear regimes — relevant to Persinger-style claims that the wiki cites but doesn't extend.

### 3.2 🟡 Programmable coil-pose mechanical gimbal

Coil position is a major confound. The wiki clamps the coil in one place. With 6× DC electromagnets (incl. 2× 800 N) + GY-9250 IMU readout, build a **2-axis solenoid-actuated gimbal** that automatically sweeps the coil position across an operator-relative grid while logging biomarker response.

- **Build:** repurpose the 50 N electromagnets as voice-coil-style linear actuators; GY-9250 closes position loop; Pi 4 GPIO drives.
- **Safety floor:** all motion stops on Nano-watchdog tilt or skin-contact loss.
- **Beyond-wiki value:** turns "did the coil work?" into "what coil position produces the strongest response?" — a real experimental knob the wiki doesn't equip.

### 3.3 🔴 DOCUMENT-ONLY — single-pulse-TMS-class device

We have iron cores (extractable from 800 N electromagnets), high-turn-count 28 AWG magnet wire (5 lb spool ≈ 7700 ft), and pulse-current capability via 500 F supercaps (~4.7 kJ stored). This is the *raw material* for a TMS-class device. **Do not build.** Single-pulse TMS produces neuronal action potentials and requires IRB oversight under any reasonable interpretation of human-subjects research. Named here so the temptation is explicit rather than discovered later.

---

## 4. HV & VHV (wiki absent → inventory at electrogravitic scale)

**Wiki status:** Mk1 Defender/Stabilizer don't use HV. Electrogravitic Tech is sibling-tree, not HelmKit.

**Inventory:** **5× VHV 1000 kV + 5× VHV 400 kV + 3× 20 kV arc + 1× 30 kV ignition + 15 kV pulse inverter + 500 F supercaps**.

### 4.1 🟡 Biefeld-Brown asymmetric-capacitor thrust demonstrator

The wiki Electrogravitic Tech page literally lists $F = k \cdot C \cdot V^2 \cdot A_G$ as the operative equation. **We have the V (50–400 kV), the supercap bank for pulsed energy, BaTiO₃-class dielectric stock in the conductive-paint chemistry, and the CNC for asymmetric electrode geometry.**

- **Build:** a small benchtop lifter — *not* a HelmKit module, an **adjacent-tech-tree demo** showing the helm hardware stack is capable of this regime. Defensive-publication-grade.
- **Safety floor:** Faraday cage; current-limited (≤ 1 mA RMS); operator behind a polycarbonate shield; supercaps shorted on power-down; written runbook before each test.
- **Beyond-wiki value:** the wiki Electrogravitic page is theoretical scaffolding. Producing a working benchtop lifter validates the *capability* and gates further work.

### 4.2 🟡 Pulsed coil drive regime (supercap-discharge)

10× 500 F supercaps at 2.7 V = ~4.7 kJ stored. Wiki Mk1 Stabilizer is continuous-wave. **Pulsed-discharge regime** produces much higher peak field at vastly lower duty cycle — potentially safer (SAR scales with average power) while producing more dramatic transient effects.

- **Build:** dedicated pulsed-drive PCB; supercap stack → MOSFET switch → coil; ESP32 LEDC controls pulse timing.
- **Safety floor:** pulse duration software-capped before the firmware enables HV-side relay.
- **Beyond-wiki value:** pulse-regime psi-tech is a niche the wiki gestures at (synaptic-plasticity claims) but doesn't equip. Real experimental knob.

---

## 5. Multi-modal session recording (wiki has Field Recorder concept → inventory has the whole suite)

**Wiki status:** Field Recorder Mk1 is "audio + HRV." Psi Recorder is similar but with consent layer.

**Inventory:** **MLX90640 thermal + ELP 170° fisheye 8MP visible + Hey Mic! lavalier + M-Audio M-Track Duo XLR + DHT11 humidity + BMP180 barometric + GUVA-S12SD UV + 38 kHz IR receivers + 9-axis IMU + sensor-kit photoresistor + capacitive touch + thin-film pressure**.

### 5.1 🟢 Field Recorder Mk1.5 multi-modal session capture

Compose every passive sensor into a **single timestamped session log** per Psi Recorder session:

| Channel | Sensor | Wiki coverage |
|---|---|---|
| HRV | (Polar H10 or PPG substitute) | ✅ wiki Mk1 |
| Audio | Hey Mic + M-Track Duo | ✅ wiki Mk1 |
| Visible video | ELP fisheye 8MP | ❌ not in wiki |
| Thermal video | MLX90640 32×24 @ 8 Hz | ❌ not in wiki |
| UV ambient | GUVA-S12SD | ❌ not in wiki |
| Humidity / pressure | DHT11 / BMP180 | ❌ not in wiki |
| Operator motion | GY-9250 9-DOF | partial (helm-IMU only) |
| Wearer contact | capacitive touch + thin-film pressure | ❌ not in wiki |
| Schumann band | Heltec LoRa 32 ADC | ✅ wiki Mk1 |
| Coil emission monitor | NESDR + 1:9 balun | ✅ wiki Defender |

- **Build:** Pi 4 streams all sources to disk, NTP/PPS-disciplined, one session-bundle per timestamp directory. AGX Orin post-processes.
- **Beyond-wiki value:** Mk1.5 produces **a richer provenance record per session than any consumer or DIY psi-tech device on the market**. Defensive-publication-grade artifact.

### 5.2 🟢 Active scalp-temperature management (confound control)

Coil drive produces heat. Skin temperature changes confound HRV, GSR, and most autonomic biomarkers. Wiki doesn't manage this.

- **Build:** Peltier + 12 V boost + HKWANTAT 40 mm fan + DS18B20 closed-loop holding scalp ≤ 33 °C.
- **Beyond-wiki value:** removes a major confounder for any HRV-vs-coil claim. Real experimental hygiene.

---

## 6. Paired-operator and networking (wiki gestures → inventory equipped)

**Wiki status:** wiki Pass 2 mentions paired-operator experiments but doesn't equip them.

**Inventory:** **2× Heltec LoRa 32 (LoRa 863–928 MHz + WiFi + BLE) + Cradlepoint wideband antennas + RangePi 433 MHz**.

### 6.1 🟢 LoRa-synchronized paired-helm protocol

Two Heltec LoRa 32 units = two helms with built-in long-range telemetry **even in EMI-quiet sites with no WiFi**.

- **Build:** synchronized event windows broadcast over LoRa; both helms cross-correlate HRV/Schumann/coil emission against the shared window.
- **Beyond-wiki value:** the wiki HRV-coherence Layer-2 claim is *testable but un-instrumented* in the published spec. Paired-operator data is the cleanest possible test.

### 6.2 🟡 EIN Relay Node integration

The wiki [Schumann Lattice § Subsystems](https://wiki.fusiongirl.app/wiki/Schumann_Lattice) requires an EIN Relay Node for federation. With the Pi 4 + Heltec + RangePi 433 stack, we are *one config-file away* from being the first publicly-online EIN Relay Node. Gate: wiki spec for EIN Relay protocol is not yet published; pin to whatever spec lands.

---

## 7. Conductive-paint + magnet-wire fabrication (wiki absent → inventory printable-electrode capable)

**Wiki status:** wiki Stabilizer/Defender don't spec custom electrodes. Polar H10 chest strap is the gold standard.

**Inventory:** **MG Chemicals 838AR carbon paint + Remington 36 AWG magnet wire (4× spools, ~12,772 ft total) + BNTECHGO 28 AWG (5 lb spool) + CNC + photogrammetry-capable ELP camera**.

### 7.1 🟢 Custom-printed dry HRV/EEG electrodes

Print conductive-carbon patterns on flexible substrate; bond fine magnet wire as lead-out; CNC-mill a head-shape-matched backing piece using photogrammetric scan from the ELP camera. Result: **operator-specific dry electrodes** with no gel, no preparation, repeatable contact pressure.

- **Beyond-wiki value:** moves HelmKit from "uses Polar H10 like everyone else" to "has its own electrode fabrication pipeline." Defensive-publication-grade.

### 7.2 🟢 Custom search-coil pickup-loops at 28 / 36 AWG

For a NESDR-based **passive coil-emission monitor** placed inside the helm, the standard tight-wound search-coil geometry is hand-buildable from the fine magnet wire stock. Wiki Defender uses an antenna + balun; a tight-wound pickup loop is **more sensitive at the wiki 1–8 MHz band** and has known geometry for FDTD comparison.

---

## 8. Composite-material resonant experiments (wiki absent → inventory has the materials lab)

**Wiki status:** the wiki doesn't deeply explore acoustic-mechanical-electromagnetic coupling.

**Inventory:** **4 lb quartz sand + 1 lb quartz tumbled chips + ~2.18 L ferrofluid + 5 lb black iron oxide + 1 qt graphite powder + conductive paints + audio drivers + speakers**.

### 8.1 🟡 Cymatic / Chladni pattern visualizer driven by audio

A quartz-sand or iron-oxide-powder layer on a driven plate visualizes acoustic resonance modes. With abundant audio drivers + amps + powders + a glass plate, this is a **ritual-class UI element** for the helm + a quantitative visualization of acoustic-coupled coil drive.

- **Beyond-wiki value:** the wiki has no concept of visible/visceral session feedback. Cymatics is striking and educational. Build it for the demo room, not the helm proper.

### 8.2 🟡 Ferrofluid-on-glass live coil-emission visualizer

Thin layer of ferrofluid on glass, coil mounted below, observed by ELP camera + MLX90640 thermal. As coil drives at varying frequencies the ferrofluid patterns shift visibly. **Live witness** to the coil-emission field profile.

- **Beyond-wiki value:** a session-time visualization of the coil field that bypasses any cognitive-bias confound — the field is either patterning the fluid or it isn't.

### 8.3 🟡 Quartz-graphite-iron-oxide layered passive resonator

Composite-material resonator stack: piezo (quartz) + conductive (graphite) + magnetic (iron oxide), driven through coil. Characterize via NESDR + scope. This is a literal "passive resonator" demonstrator that the wiki Layer-3 "psi field structure" gestures at metaphorically — done as physics, not as doctrine.

---

## 9. Ritual UI / physical interface (wiki minimal → inventory ritual-class)

**Wiki status:** wiki spec is OLED + a few buttons.

**Inventory:** **240-pc + 180-pc tactile buttons + 60 + 100 + 150 + 64 pot kits (60 + 100 + 150 + 64 pots respectively, multiple value ranges) + 20-pc boat rocker switches + LCD1602 + Heltec OLED + LEDs everywhere**.

### 9.1 🟢 Ritual-class commit interface

Replace the wiki's "instant-on" with a **deliberate startup ritual**:
1. Boat-rocker arms HV bus (visible mechanical commit)
2. Three tactile buttons in sequence + a key-switch class operator-authentication
3. Pot-controlled drive frequency + amplitude (analog tactile vs. menu)
4. Final commit button drives the relay-gated coil bus
5. OLED + LCD1602 display the session-as-data state

- **Beyond-wiki value:** ritual interfaces in safety-critical systems aren't superstition, they're **the same human-factors logic as nuclear-launch protocols**. They prevent absent-minded misuse. The wiki doesn't think this way; it should.

### 9.2 🟢 Multi-modal status display (Heltec OLED + LCD1602 + WS281x LEDs)

Three independent visual channels, each driven by an independent MCU:
- Heltec OLED: rich session state, served by ESP32 (the Mk1 Stabilizer brain)
- LCD1602 on Pi 4 GPIO: human-readable Pi-side status
- LEDs (white/red/RGB) driven by Nano MCU-B: **safety-floor-only** display ("HV armed" / "Coil hot" / "Watchdog OK" / "Emergency stop") — independent of Pi 4 failure modes

- **Beyond-wiki value:** wiki has *one* OLED. We have three independent display channels driven by three independent MCUs — meets the wiki's MCU-A doer / MCU-B checker safety architecture with display redundancy at no extra cost.

---

## 10. Antenna-array + gradiometric SDR (wiki uses 1× HackRF + 2× NESDR → inventory enables full TDOA)

**Wiki status:** Defender uses HackRF + 1× NESDR + balun. Gradiometric IMU pair is mentioned for magnetic-field mode.

**Inventory:** **HackRF + 2× NESDR Smart v4 + 1× NESDR Smart XTR + Ham It Up + 1:9 balun + 3× Cradlepoint wideband antennas + RangePi 433 + Bingfu LTE V-splitter + abundant SMA adapters**.

### 10.1 🟢 3-channel TDOA passive localizer

Three RX-only NESDR receivers (2× v4 + 1× XTR) with **GPS-PPS-disciplined sample clocks** form a time-difference-of-arrival localizer. With known antenna geometry, this can **pinpoint unknown emitters in the operator's environment** in the 24 MHz – 2.3 GHz band.

- **Build:** GPS PPS to each NESDR via the Heltec PPS-style breakout; AGX Orin runs the cross-correlation in real time (well within its compute budget).
- **Beyond-wiki value:** this is the **Resonant Finder Layer-1 in a backpack** — geographic localization of anomalous emitters. Wiki Resonant Finder Mk1 is a workstation; this is a portable scout.

### 10.2 🟢 Coil-emission monitor with 1:9 balun + HackRF TX-side null test

The 1:9 balun + NESDR pair is the wiki-canonical Defender emission monitor. **HackRF's TX-capability lets the same hardware run a "TX null" calibration** — emit a known signal, measure self-receive, calibrate the path loss. Wiki spec uses HackRF only for RX.

---

## 11. Self-contained UV-fluorescence "aura imager" (wiki Layer-3 → buildable physics demo)

**Wiki status:** "aura" is a Layer-3 SPECULATIVE construct.

**Inventory:** UV-A excitation + UV detector + ELP visible camera + MLX90640 thermal + audio + computer.

### 11.1 🟡 Multi-spectral operator imager

- UV-A 365 nm flood from 3 W COBs → activates natural skin / hair / sweat fluorescence
- ELP camera captures fluorescence emission in visible band (UV-OFF gating to prevent direct UV imaging)
- MLX90640 captures thermal differential
- Composite false-color image fusing **UV-fluorescence + visible + thermal** in registered alignment

- **Beyond-wiki value:** whether "auras" are real or not, the **imaging modality is real physics** (UV-induced fluorescence is uncontroversial). Producing a striking, repeatable false-color image of an operator across three spectral bands is a **defensive-publication artifact** that delivers value to both believers and skeptics. The wiki Layer-3 framing of aura becomes a Layer-1 false-color visualization.

---

## 12. Summary by tier

### 🟢 Build-now (high-priority, low-risk, extends HelmKit)

1. **PBM 730 nm halo** (§2.1) — well-evidenced cognitive modality, wiki silent
2. **Multi-modal Field Recorder Mk1.5** (§5.1) — overstocked sensor suite; wiki has the concept
3. **Active scalp-temp management** (§5.2) — removes a major confounder; trivial build
4. **LoRa paired-helm sync** (§6.1) — tests the wiki Layer-2 HRV claim directly
5. **Custom-printed dry electrodes** (§7.1) — replaces Polar-H10 dependency
6. **Custom search-coil pickup loop** (§7.2) — better than antenna+balun for in-helm monitor
7. **Ritual-class commit interface** (§9.1) — safety-critical human factors
8. **Multi-modal status display** (§9.2) — three-MCU display redundancy
9. **3-channel TDOA passive localizer** (§10.1) — Resonant-Finder-in-a-backpack
10. **Coil-emission monitor with TX null** (§10.2) — wiki extension by one HackRF mode

### 🟡 Build-after-gate (needs explicit safety/IRB/regulatory review)

1. **Programmable coil-pose gimbal** (§3.2) — motion safety review
2. **Biefeld-Brown demonstrator** (§4.1) — HV review + Faraday cage
3. **Pulsed coil-drive regime** (§4.2) — pulse-energy review
4. **EIN Relay Node integration** (§6.2) — wait for protocol spec
5. **Cymatic visualizer** (§8.1) — purely demo; gate is just "is this worth the time?"
6. **Ferrofluid live coil visualizer** (§8.2) — ditto; aesthetic + scientific
7. **Composite-material resonator** (§8.3) — purely physics; minor handling gate (powders + amplifiers)
8. **Multi-spectral aura imager** (§11.1) — gate: privacy/consent boundary on imaging
9. **Halbach static-bias coil** (§3.1) — magnet-handling safety review

### 🔴 Document-only (parts exist; should NOT build without external oversight)

1. **Single-pulse TMS** (§3.3) — neuronal action potentials require IRB
2. **RF cell-band notch jammer** — never built; never tested; mentioned only because someone might think of it. **Illegal under FCC Part 15.** Document and forbid.

---

## 13. Cross-refs

- [inventory.md](inventory.md) — authoritative parts list
- [inventory_capability_map.md](inventory_capability_map.md) — coverage matrix
- [wiki_synthesis.md](wiki_synthesis.md) — wiki BOM source material
- [gpu_farm_workloads.md](gpu_farm_workloads.md) — GPU farm workload mapping (some entries here depend on it: §1, §3.1, §3.2)
- [sprint_0.3_fdtd_coil_design.md](sprint_0.3_fdtd_coil_design.md) — first sprint enabled by the farm
- [safety.md](safety.md) — operating envelope for any 🟡 work
- [README.md](../README.md) — epistemic stance disclaimer

## 14. What this document is *not*

- Not a build commitment for any item
- Not a deprecation of the wiki — every 🟢/🟡 entry **extends** wiki concepts rather than contradicting them
- Not a Layer-3 doctrinal claim — every entry above can be evaluated on Layer-1 (physics) or Layer-2 (testable biomarker) grounds without invoking psionic interpretation
- Not exhaustive — this is the **first-pass** beyond-wiki concept inventory; subsequent passes after each sprint may add or retire items
