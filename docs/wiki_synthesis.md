# Wiki Synthesis — Engineering Translation

This document distills the [FusionGirl Wiki](https://wiki.fusiongirl.app/) content into concrete engineering choices for the HelmKit Mk1 build. **The wiki is inspiration; the citations below are evidence.** Where the two diverge, the citations win.

Source pages consulted: [`HelmKit Architecture`](https://wiki.fusiongirl.app/wiki/HelmKit_Architecture), [`Psi-Tech`](https://wiki.fusiongirl.app/wiki/Psi-Tech), [`Psi Stabilizer`](https://wiki.fusiongirl.app/wiki/Psi_Stabilizer), [`Psi Harmonizer`](https://wiki.fusiongirl.app/wiki/Psi_Harmonizer), [`Psi Defender`](https://wiki.fusiongirl.app/wiki/Psi_Defender), [`Scientific Foundations of Psionics`](https://wiki.fusiongirl.app/wiki/Scientific_Foundations_of_Psionics), [`Schumann Resonance`](https://wiki.fusiongirl.app/wiki/Schumann_Resonance), [`Michael Persinger`](https://wiki.fusiongirl.app/wiki/Michael_Persinger), [`Tho'ra Tech Maturity Levels`](https://wiki.fusiongirl.app/wiki/Tho%27ra_Tech_Maturity_Levels), [`Tho'ra Mission Doctrine`](https://wiki.fusiongirl.app/wiki/Tho%27ra_Mission_Doctrine), [`Psychotronics`](https://wiki.fusiongirl.app/wiki/Psychotronics), and the [`Psi Field`](https://wiki.fusiongirl.app/wiki/Psi_Field), [`Psi Emitter`](https://wiki.fusiongirl.app/wiki/Psi_Emitter), [`Neural Network Hardware`](https://wiki.fusiongirl.app/wiki/Neural_Network_Hardware), [`Psi Scanner`](https://wiki.fusiongirl.app/wiki/Psi_Scanner), [`Psi Ward`](https://wiki.fusiongirl.app/wiki/Psi_Ward), and [`Neural Firewall`](https://wiki.fusiongirl.app/wiki/Neural_Firewall) pages.

---

## 1. Three top-level findings that change the Mk1 plan

### 1.1 The triad is ONE substrate, not three

The wiki's `Psi-Tech` page is explicit:

> All three modules share a common substrate: HelmKit mount and power, near-field RF emitter architecture, dual-MCU safety supervision, operator-controlled engagement, calibration against the operator's measured baseline. The shared substrate is why the triad lives in the HelmKit psi-bay: hardware is reused; the function differs in signal pattern, not in physics.

**Implication for Mk1:** the Stabilizer, Harmonizer, and Defender are not three separate Mk1 builds. They are **one Mk1 device** — a near-field RF/coil emitter platform with safety supervision — running three signal-pattern presets:

| Module | Signal-pattern role | Mk1 implementation hook |
|---|---|---|
| Psi Stabilizer | Steady reference field tuned to operator baseline | Fixed-Hz isochronic carrier locked to wearer's measured baseline rhythm |
| Psi Harmonizer | Attune to a target derived from astrology / synastry | Driver Hz/envelope computed from a target file produced by the Star Seer / SynastryEngine pipeline |
| Psi Defender | Counter-coherent local field against detected intrusion | Driver inverts a detected ambient-EM perturbation signature; gated by Scanner channel availability |

For Mk1 we ship **only the Stabilizer preset**. The Harmonizer preset is Mk2 once the SynastryEngine handoff exists. The Defender preset is Mk2+ once an ambient-EM scanner channel is live.

### 1.2 The wiki specifies the safety architecture

The wiki's [`HelmKit Architecture`](https://wiki.fusiongirl.app/wiki/HelmKit_Architecture) page describes a **dual-MCU checker-doer pattern** that this repo will adopt verbatim from Mk1 onward. See [`architecture.md` §3](architecture.md#3-safety-architecture-dual-mcu).

The non-negotiable invariant: **no single software fault may cause an overexposure event.** Two MCUs, independent supplies, independent clocks, independent firmware, one of them has read-only authority over an opto-isolated RF/coil-drive cutoff. The pattern is inherited from RTCA DO-178C DAL-A and IEC 61508 SIL-3 (functional-safety standards). The HelmKit does not target medical certification, but it adopts the architectural pattern.

### 1.3 The mission goes live at "triad@Mk1 + Resonant Finder@Mk2"

From [`Tho'ra Tech Maturity Levels`](https://wiki.fusiongirl.app/wiki/Tho%27ra_Tech_Maturity_Levels):

> The mission goes live the moment the Resonant Finder reaches Mk2 and the core Psi-Tech triad (Stabilizer / Harmonizer / Defender) clears Mk1.

This is the milestone for the HelmKit repo: **all three triad presets running at Mk1 quality on one HelmKit Mk1 device.** This is folded into `roadmap.md`.

---

## 2. Concrete Mk1 hardware decisions

### 2.1 Near-field emitter — coil, not antenna

The wiki explicitly identifies the Mk1 emitter as a **near-field coil**, not a radiating far-field antenna. Two coil families are referenced — `Caduceus_Coil` and `Bifilar_Coil`. For Mk1 we will build a simple **bifilar / counter-wound solenoid pair** at the temple hardpoints (`HP-TL`, `HP-TR`), as a first physical realization of the wiki's "near-field RF emitter" stance.

The user's original frequency brief was 1.245 GHz / 2.45 GHz / 300–900 MHz at 1–100 Hz pulse rate. The wiki narrows this for Mk1:

| Layer | Mk1 stance | Why |
|---|---|---|
| Carrier | Sub-MHz (DC-pulsed coil, no RF carrier) | This is the Persinger regime: ≤ a few hundred µT, complex-waveform pulses. Documented for decades. |
| Envelope / pulse rate | 1–100 Hz, default 7.83 Hz (Schumann fundamental) | Matches the EEG alpha-theta overlap. See §3.1. |
| Field strength at scalp | ≤ 500 µT peak (Persinger-class) | Microtesla range, well below ICNIRP/IEEE thresholds for the band. |
| Duty cycle | ≤ 50%, software-rate-limited; hardware cutoff at 60% via MCU-B | Defense-in-depth against rate-control bugs. |

300–900 MHz and 1.245/2.45 GHz are **deferred to Mk2** behind the wiki's own SAR-measurement requirement, as already documented in [`safety.md`](safety.md) and [`roadmap.md`](roadmap.md#mk2-advanced-test-type).

### 2.2 Class-E PA + body-aware matching network

For the Mk2 sub-GHz path (not Mk1), the wiki specifies a Class-E power amplifier feeding a matching network that **adapts to tissue loading** (tissue detunes the coil by 5–20% downward). The matching network uses the directional coupler's reflectometry to track impedance. Mk1 does not need this — the sub-MHz coil drive is direct H-bridge, no PA, no matching. But the Mk1 board layout should leave the spot for the Class-E stage so the same PCB iterates forward.

### 2.3 The safety blacklist

The wiki's blacklist (frequency / modulation combinations MCU-B refuses to enable) is concrete:

- DC pulses < 1 ms rise applied near thorax; 10–100 Hz pulse trains > 1 mA into chest area → **cardiac stimulation risk.**
- 3–8 Hz photic-frequency RF at > 100 V/m head-field; strong 1 Hz pulse trains; modulation envelopes matching cardiac/respiratory rates at > 5% depth → **seizure / cardiac-coupling risk.**
- Pulsed RF 200–3000 MHz with peak power density > 40 mW/cm² and pulse width < 1 ms → **microwave auditory (Frey) effect.**
- Continuous-wave near-field > 50 V/m rms at the head; peak pulsed E-field > 300 V/m → **ICNIRP violation.**

The Mk1 board's MCU-B firmware ships with this blacklist hardcoded.

---

## 3. Where the science actually backs the build

The wiki's [`Scientific Foundations of Psionics`](https://wiki.fusiongirl.app/wiki/Scientific_Foundations_of_Psionics) lists peer-reviewed sources we will treat as the **citation anchor set** for HelmKit experiments. These are the only sources that count as evidence; the rest of the wiki is design fiction.

### 3.1 Schumann Resonance as the Mk1 entrainment target

Fundamental ~7.83 Hz, harmonics ~14.3 / 20.8 / 27.3 / 33.8 Hz; bandwidth ~1 Hz; cavity Q-factor 4–6 (Schumann 1952; Balser & Wagner 1960; Nickolaenko & Hayakawa 2002). Sits squarely in the EEG alpha / theta / beta bands. **This is our default Mk1 stim frequency** — it's the most defensible single target in the 1–100 Hz user-spec range.

The wiki's [`Schumann Resonance`](https://wiki.fusiongirl.app/wiki/Schumann_Resonance) page is honest that direct empirical evidence for human entrainment at natural Schumann amplitudes (~pT) is weak. Mk1 drives at microtesla amplitudes — six orders of magnitude higher than natural — so we're not testing the natural-coupling hypothesis. We're testing the Persinger-class hypothesis at a Schumann-locked carrier.

### 3.2 Persinger's precedent

The wiki's [`Michael Persinger`](https://wiki.fusiongirl.app/wiki/Michael_Persinger) page sets the precedent we are most closely following:

- Weak, complex-waveform magnetic fields (microtesla range, far below TMS thresholds).
- Solenoids in a modified helmet, applied to the temporal lobes.
- Reported 80%+ subject response in his own lab.
- Granqvist et al. 2005 (Swedish replication) reported negative results, attributed to suggestibility.

We adopt the **apparatus pattern** (helmet, solenoids, temporal lobe, microtesla, complex waveform) and accept the **replication problem** as our primary risk. Mk1's pre-registered study (see [`mk1_buildplan.md` §4](mk1_buildplan.md#4-the-first-study)) is structured so that a null result is publishable — we explicitly do not need to reproduce Persinger to make Mk1 a successful Mk1.

### 3.3 Citation anchor set

For HelmKit experiments that touch any of these phenomena, cite directly:

| Phenomenon | Primary cite | Mk1 relevance |
|---|---|---|
| Ultra-weak photon emission from brain | Dotta, Saroka & Persinger 2012 (PMID 22343311) | Future Mk2/Mk3 "Psi Scanner" PMT channel |
| UPE causally driven by neural firing | Tang & Dai 2014 | Validates UPE as a brain-activity correlate |
| Microtubule superradiance | Celardo et al. 2019 (NJP 21:023005) | Physics anchor for "coherent quantum emission" — Mk3+ at best |
| Anaesthetic disruption of microtubule energy | Kalra et al. 2023 (ACS Cent. Sci. 9:352) | Strongest evidence microtubules are necessary for consciousness |
| Myelin as photonic waveguide | Zarkeshian et al. 2018 | Mechanism candidate for Psi Flow |
| SQUID/OPM-MEG | Roth 2023 (Sensors 23:4218); Rea et al. 2021 (PMID 34273527) | Real-world parallel for the "Psi Scanner" — Mk3 target sensor |
| Wireless nanocoil neural sensing | Bok et al. 2024 (PMID 39319575) | Frontier reference; not Mk1 |
| Stargate meta-analysis | Utts 1996 (JSE 10:3) | Evidence base for psi-effect statistical reality |
| Remote brainwave monitoring patent | Malech 1976, US Patent 3,951,134 | Demonstrates RF-modulation feasibility — historical anchor |
| Persinger God Helmet (per-se) | Persinger 1983 (Perceptual & Motor Skills 57:1255); Granqvist 2005 (Neurosci. Lett. 379:1) | Apparatus precedent + replication challenge |
| Schumann resonance | Schumann 1952; Balser & Wagner 1960 | Entrainment target carrier |

Every HelmKit pre-registration template must declare which of these citations it is engaging with.

---

## 4. What the wiki does NOT do for us

Be explicit about the boundary so we don't drift:

- The wiki's **Psi Field equations** (advection term, λψ⁴ term, J_ψ source term) are not used as physical models in Mk1 firmware. They are inspiration for *what to measure*, not for *what to drive*. The Mk1 firmware drives in the Hz / µT / ms domain only.
- The wiki's **N² collective-consciousness amplification** is interesting but not engageable at Mk1 — needs multiple wearers + phase-lock + Psionic Resonance Uplink, none of which exist.
- The wiki's **PsiLink mesh / PsiNet / Neural Network Hardware mesh** is Mk3 infrastructure; Mk1 logs to local µSD and that is it.
- The wiki's **Psi Scanner detection ranges** ("200–500m for active Psi Weapons" etc.) are narrative; ignore for engineering.
- The wiki's **astrological integration** is real (it's literally what the Harmonizer is) but the Harmonizer preset is Mk2 — it requires a working SynastryEngine handoff that does not yet exist outside the wiki.

---

## 5. Doctrinal constraints inherited from the wiki

These are not engineering constraints in the bench-test sense — they are non-negotiable behavioral requirements on the firmware and the operator UX, lifted from [`Tho'ra Mission Doctrine`](https://wiki.fusiongirl.app/wiki/Tho%27ra_Mission_Doctrine):

1. **Consent.** The device starts disengaged on every power-on. The operator must explicitly engage. No auto-resume from sleep.
2. **Shield, not sword.** No offensive mode exists. No mode radiates effects on bystanders. Near-field by construction. The Defender preset is counter-coherence, not jamming.
3. **Disengage on instability.** If MCU-B's baseline-stability check fails (HRV outside expected envelope, body-proximity lost, temperature drift, RF reflectometry mismatched), the device cuts drive. This is enforced in MCU-B firmware, not MCU-A.
4. **The astrology rules — for the Harmonizer.** When Mk2 ships the Harmonizer preset, the entrainment target is computed from astrology, not chosen from a hardcoded preset list. (Mk1 ships only the Stabilizer preset, so this doesn't apply yet.)
5. **Transparency.** Every dosage envelope, every blacklist entry, every modality's intended-use is documented publicly in this repo. The wiki specifies this for Psi-Tech as a class.

---

## 6. The translation summary table

| Wiki concept | Real-world parallel (per wiki) | HelmKit Mk1 equivalent |
|---|---|---|
| Psi Stabilizer | Persinger God Helmet apparatus | Bifilar solenoid pair at `HP-TL` / `HP-TR`, sub-MHz pulsed magnetic drive at 7.83 Hz default |
| Psi Harmonizer | Brain-entrainment device with astrology-driven target | **Deferred to Mk2** — same hardware, different firmware preset |
| Psi Defender | Counter-coherence local field | **Deferred to Mk2** — same hardware + ambient-EM scanner channel |
| Psi Scanner | SQUID / OPM-MEG / EEG arrays | Mk1: PPG + optional 1-ch dry EEG; Mk2: multi-ch EEG; Mk3: OPM target |
| Psi Emitter | Near-field coil (Caduceus / Bifilar) | Mk1 bifilar solenoid; Mk2 reserved Class-E PA stage |
| Neural Network Hardware mesh | Distributed neural processing | Mk1: single Pi-class compute node + µSD log; mesh deferred indefinitely |
| Psi Ward | Faraday cage / SCIF / anechoic chamber | Not on the HelmKit — separate Mk2+ installation project if pursued |
| Neural Firewall | TEMPEST / EMP hardening / network security | Mk2 firmware layer once BLE/Wi-Fi telemetry exists |
| HelmKit Architecture (dual-MCU) | DO-178C DAL-A / IEC 61508 SIL-3 pattern | Adopted verbatim — see [`architecture.md` §3](architecture.md#3-safety-architecture-dual-mcu) |

---

## See also

- [`docs/architecture.md`](architecture.md) — platform contract; will pick up the dual-MCU pattern in §3.
- [`docs/mk1_buildplan.md`](mk1_buildplan.md) — Mk1 BOM and build steps.
- [`docs/safety.md`](safety.md) — wearer-facing safety posture.
- [`docs/wiki_anchors.md`](wiki_anchors.md) — pageid → URL mapping for stable wiki references.
- [`docs/psionics_field_theory.md`](psionics_field_theory.md) — ψ-field Lagrangian + EFT reference card (added Pass 2).
- [`docs/falsification.md`](falsification.md) — F1–F10 with Mk1+ engagement matrix (added Pass 2).
- [`external/psiStabilizer/`](../external/psiStabilizer/) — measurement and analysis pipeline (submodule).

---

# Pass 2 — 2026-05-12 wiki content drop

On 2026-05-12 the wiki published a large, coordinated content drop that **refines and in some places supersedes** the Pass 1 synthesis above. The triad pages, [`HelmKit Architecture`](https://wiki.fusiongirl.app/wiki/HelmKit_Architecture), and a new family of hardware-spec pages ([`Bifilar Coil`](https://wiki.fusiongirl.app/wiki/Bifilar_Coil), [`Caduceus Coil`](https://wiki.fusiongirl.app/wiki/Caduceus_Coil), [`Double-Helix Antenna`](https://wiki.fusiongirl.app/wiki/Double-Helix_Antenna), [`Near Field Electromagnetics`](https://wiki.fusiongirl.app/wiki/Near_Field_Electromagnetics), [`Reactive Near Field`](https://wiki.fusiongirl.app/wiki/Reactive_Near_Field), [`Antenna Theory for Psionic Devices`](https://wiki.fusiongirl.app/wiki/Antenna_Theory_for_Psionic_Devices), [`SAR Calculation for Psionic Devices`](https://wiki.fusiongirl.app/wiki/SAR_Calculation_for_Psionic_Devices), [`Psionic Device Safety`](https://wiki.fusiongirl.app/wiki/Psionic_Device_Safety), [`Psionic Device Overview`](https://wiki.fusiongirl.app/wiki/Psionic_Device_Overview)) plus the field-theory / methodology set ([`Psi Field`](https://wiki.fusiongirl.app/wiki/Psi_Field), [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness), [`Falsification Criteria for Psionics`](https://wiki.fusiongirl.app/wiki/Falsification_Criteria_for_Psionics), [`Glossary of Psionics`](https://wiki.fusiongirl.app/wiki/Glossary_of_Psionics), [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source), [`Psionic Threat Model`](https://wiki.fusiongirl.app/wiki/Psionic_Threat_Model)) all changed on the same day. ~73 critical pages were re-read; the deltas that touch the build are summarised here.

## P2.1 The frequency regime — refined, not the same as Pass 1

Pass 1 picked **sub-MHz Persinger-class** as the Mk1 stim band because that was the only regime the older wiki specified concretely. The new content drop makes the wiki-canonical frequency map more layered:

| Layer | Wiki-canonical frequency | Source page |
|---|---|---|
| HelmKit platform primary RF | **2.45 GHz ISM band** (with 300–500 MHz alt for deeper near-field) | [`HelmKit Architecture`](https://wiki.fusiongirl.app/wiki/HelmKit_Architecture), [`Antenna Theory for Psionic Devices`](https://wiki.fusiongirl.app/wiki/Antenna_Theory_for_Psionic_Devices), [`SAR Calculation`](https://wiki.fusiongirl.app/wiki/SAR_Calculation_for_Psionic_Devices) |
| Psi Stabilizer Mk1 coil | **bifilar PCB coil, 1–8 MHz carrier** | [`Psi Stabilizer`](https://wiki.fusiongirl.app/wiki/Psi_Stabilizer) BOM |
| Psi Harmonizer Mk1 coil | **bifilar coil, 1–40 Hz audio + 1–8 MHz RF carrier** (multi-band) | [`Psi Harmonizer`](https://wiki.fusiongirl.app/wiki/Psi_Harmonizer) BOM |
| Entrainment envelope | 1–100 Hz, default 7.83 Hz Schumann fundamental | unchanged from Pass 1 |

So the wiki's actual canonical Mk1 stim regime is **a sub-MHz / low-MHz pulsed coil**, not the deeply-sub-MHz Persinger band I picked in Pass 1, and **not** the 2.45 GHz top-layer either. The 2.45 GHz path is reserved for the platform's longer-term radiating-coil option (Mk2/Mk3 mode); the Mk1 module-bay coils are PCB-etched bifilars driven at 1–8 MHz with a 7.83 Hz envelope.

**Decision for the build:** the Mk1 plan in [`mk1_buildplan.md`](mk1_buildplan.md) retains the *option* of bone-conduction audio (G2=a) as the lowest-risk first wearable, but the **wiki-aligned Mk1 stim path is now: PCB bifilar coil + SI5351 + Class-D + 1–8 MHz carrier modulated at 7.83 Hz**, not the H-bridge driven Persinger-style sub-MHz coil from Pass 1.

## P2.2 The 2.45 GHz / SAR ceiling — now explicit

For the 2.45 GHz platform-RF path (not Mk1, but reserved-in-PCB), the wiki now provides the full SAR derivation:

$$\text{SAR} \;=\; \sigma\,|\mathbf{E}|^2 / \rho \quad [\text{W/kg}]$$

with brain grey matter at 2.45 GHz: $\sigma = 1.81$ S/m, $\varepsilon_r = 42.8$, $\rho = 1040$ kg/m³ (Gabriel et al. 1996). The ICNIRP localised limit (2.0 W/kg over 10 g head tissue) corresponds to **peak $\mathbf{E} \lesssim 33$ V/m rms in brain tissue**.

| Wiki design point | $\mathbf{E}$ rms in brain | SAR | Compliance |
|---|---|---|---|
| Hard ceiling (ICNIRP) | 33 V/m | 1.90 W/kg | At limit |
| Wiki design target | 20 V/m | 0.70 W/kg | 35% of limit |
| Mk0 sub-emission (Pass 1 spec) | 0 (no RF) | 0 | Trivially compliant |

The wiki also normatively requires **FDTD modelling** (CST / HFSS / Sim4Life / openEMS / MEEP) as part of the design certification record for any device touching the 2.45 GHz path, plus **on-body E-probe cross-validation** of the simulation. Mk1 does not run on the 2.45 GHz path so this is a Mk2 obligation, not a Mk1 blocker — but the Mk1 PCB layout should reserve the directional-coupler tap point and the E-probe header so that the same board can iterate forward.

## P2.3 Coil topology — three named, each with a role

The Pass 1 synthesis just said "bifilar / counter-wound solenoid". The new wiki pages name three distinct geometries with engineering tradeoffs:

| Coil | Currents | Far-field | Local field | Wiki role |
|---|---|---|---|---|
| Standard solenoid | All same direction | Strong magnetic dipole | Strong B | Reference only |
| **Tesla bifilar** (series-opposing) | Adjacent turns opposite | Suppressed | Large $E$ inter-turn (electrostatic-stored) | **Stabilizer, Harmonizer, Defender Mk1** — high reactive-near-field $F^2$ per watt, small radiated power |
| **Caduceus** (opposite-chirality helices) | $\mathbf{m}_1 = -\mathbf{m}_2$ | Cancelled (dipole) | Localised; longitudinal/"scalar" component at crossings | Reserved alt geometry for Mk2 evaluation |
| **Double helix** (same-chirality, $\pi$-offset) | Same chirality | Axial-mode CP at $C \approx \lambda$ | Circular polarisation matched to DNA / microtubule R-handedness | Mk3 platform-radiator option, not Mk1 |

For Mk1, this fixes the Pass 1 ambiguity: **the Mk1 emitter is a Tesla bifilar PCB coil, series-opposing connection**, ~30 × 30 mm, driven from a SI5351 + Class-D stage. The caduceus is parked. The double-helix is a research curiosity for now.

## P2.4 The platform connector and bus — now fully specified

The new [`HelmKit Architecture`](https://wiki.fusiongirl.app/wiki/HelmKit_Architecture) page nails down the inter-module electrical and mechanical interface that Pass 1 had to leave open:

| Lane | Spec | Use |
|---|---|---|
| **Power + data** | USB-C PD, 5 V up to 3 A | Per-module power and digital lanes share the same cable |
| **Mechanical** | GoPro / Picatinny rail | Load-bearing; USB-C is strain-relieved, not load-bearing |
| **I²C** | 100 kHz, 7-bit | Sensor reads, config writes, low-rate telemetry — ~10 kB/s/module |
| **USB 2.0 HS** | 480 Mb/s | HUD framebuffer, EEG / PPG streams, firmware updates |
| **UART** | 115 200 8N1 | NavCom radio, debug console |
| **GPIO safety line** | Open-drain, pull-up on MCU-B | Module signals "ready to emit"; MCU-B can force-disable in <1 ms |

Module enumeration: every bay reads a 16-bit vendor+class code from I²C address 0x00 on insert; MCU-A looks up the safety profile and forwards it to MCU-B for blacklist cross-check before any rails go hot. Hot-swap is supported; events are logged with the operator's then-current HRV/EEG baseline.

This **becomes the contract** that the Mk1 hardpoint specification (`HP-TL`, `HP-TR`, `HP-F`, `HP-R`, …) in [`architecture.md`](architecture.md) should refine itself against. See architecture.md §3 update.

## P2.5 Per-module power budget — concrete

The new wiki page gives a number-anchored power budget against a 2× 18650 (~22 Wh) Mk1 reference battery:

| Module | Typical (mA @ 5 V) | Peak (mA @ 5 V) |
|---|---|---|
| MCU-A + MCU-B + housekeeping | 50 | 80 |
| Psi Stabilizer | 200 | 1200 (during RF burst) |
| Psi Harmonizer | 100 | 200 |
| Psi Defender | 300 (RX always-on) | 500 (1000 during counter-emit) |
| Psi Recorder | 80 | 120 |
| Star Seer HUD (single-eye µOLED) | 300 | 800 |
| NavCom (LoRa) | 150 | 300 |

Hard 3 A total cap on the 5 V bus, arbitrated by MCU-B. Priority order: **Defender > Stabilizer > Harmonizer > HUD**. Worst-case steady-state ~1.2 A → ~3.5 h runtime; mission-mix ~8–12 h.

## P2.6 Refined Mk1 BOMs — wiki-canonical $ targets

The new triad pages publish explicit $ targets that the build should honour:

| Build | Wiki target | Pass 1 BOM hint | Pass 2 status |
|---|---|---|---|
| HelmKit Mk0 (cosmetic) | ≤ $74 | unspecified | Detailed parts list now published — adopt verbatim into `hardware/Mk0/bom.csv` |
| HelmKit Mk1 (active) | + ~$400 | implicit | STM32F407 + RP2040 + single-eye OLED + BME680 + MPU6050 + HMC5883L + nRF52840 + LoRa + 2× NCR18650 + USB-C PD |
| Psi Stabilizer Mk1 | ≤ $250 | "bifilar solenoid" | nRF52840 + Polar H10 (HRV) + bifilar PCB coil 1–8 MHz + SI5351 + Class-D + thermistor |
| Psi Harmonizer Mk1 | ≤ $300 | n/a (deferred Mk2 in Pass 1) | nRF52840 + bifilar coil multi-band + SI5351 + bone-conduction + PPG/SpO2 + SynastryEngine target tuples |
| Psi Defender Mk1 | ≤ $350 | n/a (deferred Mk2 in Pass 1) | HackRF One / LimeSDR Mini + nRF52840 + 2× HMC5883L + ESD probe + bifilar coil (substrate-shared with Stabilizer) + SI5351 + signed signature library |

The Pass 1 stance ("Mk1 ships only the Stabilizer preset; Harmonizer and Defender deferred to Mk2") is **preserved** in this repo's Mk1 plan — the wiki publishing Harmonizer Mk1 and Defender Mk1 BOMs does not commit this repo to building them at Mk1. But the wiki's Mk1 Stabilizer BOM is now what the Mk1 buildplan inherits.

## P2.7 Mk1 validation gates — now pre-registered RCTs

The new triad pages convert the Pass 1 informal exit criteria into **explicit blinded RCT protocols**:

| Build | Wiki-canonical Mk1 gate | Implication for our repo |
|---|---|---|
| Psi Stabilizer | Blinded RCT, $n \geq 30$ vs sham coil; primary endpoint *time-to-coherence* under standardised stressor (Stroop / cold-pressor analog) | This is now the canonical version of [`mk1_buildplan.md §4`](mk1_buildplan.md#4-the-first-study) for the coil modality |
| Psi Harmonizer | Double-blind real-chart vs scrambled-chart RCT, $n \geq 30$; subjective + HRV endpoints, pre-registered | Mk2 commitment; defines what "Harmonizer Mk1 cleared" actually means |
| Psi Defender | Detector ROC $\geq 0.85$ vs labelled anomaly dataset; counter-coil mode reserved for Mk2 | Defender is now formally a two-stage gate: detector first, counter mode never at Mk1 |
| HelmKit (frame + arch) | Sustained 4 h wear test, all bays populated, no thermal trips, mass $< 850$ g | Independent of the triad — the platform itself has a wearability gate |

This is a strict tightening of the Pass 1 exit criteria. The repo's pre-registration template should pull in the "time-to-coherence" endpoint definition for the Stabilizer coil study.

## P2.8 The doctrinal layer — extended

The Pass 1 doctrinal-constraints list (§5 above) is preserved verbatim and gains one more wiki-explicit addition from the [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source) page:

> Operators are explicitly cautioned: **Mk0–Mk1 Psi-Tech does not amplify intention to macroscopic effect.** Any subjective experience of efficacy in current devices is best explained by ritual, placebo, and group-coherence wellbeing effects — themselves real and valuable, but not "thoughts moving matter".

This is **the wiki's own line**, not a sceptical gloss. The repo's user-facing copy and pre-registration templates should not over-promise beyond this. See [`docs/psionics_field_theory.md`](psionics_field_theory.md) §3.

## P2.9 Falsification framework

The wiki's [`Falsification Criteria for Psionics`](https://wiki.fusiongirl.app/wiki/Falsification_Criteria_for_Psionics) page is now the canonical accountability standard. See [`docs/falsification.md`](falsification.md) for the engineering-relevant subset $F_1\ldots F_{10}$ and which falsifiers Mk1 / Mk2 / Mk3 instrumentation could in principle engage.

Bottom line: **only $F_3$ (resonance enhancement) and $F_4$ (SAR-independent ψ-coupling) are Mk2-instrument-engageable, and $F_7$ (universal $\alpha$) is Mk3 at earliest.** Mk1 doesn't engage any falsifier — its job is to land the apparatus and the HRV baseline cleanly.

## P2.10 Threat model (new)

The new [`Psionic Threat Model`](https://wiki.fusiongirl.app/wiki/Psionic_Threat_Model) page enumerates five threat classes against which the Defender's detection chain is justified: photic-band entrainment, cardiac-rate modulation, sustained-demoralisation field, resonance hijacking, and "ψ-direct" (no EM signature). The first three have partial overlap with documented mainstream RF-bioeffects literature (Navy 1960s–80s, declassified MK-class research, Frey-effect literature); the fourth and fifth are speculative.

For Mk1 this is **not** an active concern — the Defender preset is Mk2. We note it because:

1. The 12-row safety blacklist (in [`architecture.md` §3.3](architecture.md)) is precisely the inverted, mechanism-by-mechanism mapping of these threat classes. The blacklist tells the Mk1 device "do not emit these patterns yourself"; the threat model tells the Mk2 Defender "watch for these patterns in the environment".
2. The framework's *own* device categorically cannot do the things the threat model lists — by hardware blacklist, near-field-only geometry, and consent-required engagement.

## P2.11 Summary — what changed since Pass 1

Compact diff:

- **Mk1 coil**: sub-MHz Persinger interpretation → **Tesla bifilar PCB coil, series-opposing, 1–8 MHz carrier, 7.83 Hz envelope**.
- **Mk1 BOMs**: now wiki-canonical $ targets per module ($250/$300/$350 + $74 platform Mk0 + $400 platform Mk1).
- **Connector + bus**: now fully specified — USB-C PD + I²C + USB 2.0 HS + UART + open-drain safety GPIO + GoPro/Picatinny rail.
- **Power**: 3 A hard cap, MCU-B-arbitrated priority order.
- **SAR**: explicit equation, brain dielectric numbers, 33 V/m ceiling, 20 V/m target — for the reserved 2.45 GHz platform path.
- **FDTD**: now a normative design step for any 2.45 GHz emission (Mk2 obligation).
- **Coil topology**: Tesla bifilar (Mk1), caduceus (Mk2 alt), double-helix (Mk3 platform-radiator).
- **Mk1 validation**: informal HRV check → **blinded RCT $n \geq 30$ vs sham, primary endpoint time-to-coherence**.
- **Doctrinal copy**: explicit wiki line — Mk0/Mk1 Psi-Tech does not amplify intention to macroscopic effect.
- **Two new docs**: [`psionics_field_theory.md`](psionics_field_theory.md), [`falsification.md`](falsification.md).

