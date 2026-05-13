# HelmKit Mk1 — Build Plan

The first generation that has to **work**. This document is what the Mk1 build will look like, concretely, before any electronics are ordered.

> **Key insight from [`wiki_synthesis.md`](wiki_synthesis.md):** the Psi-Tech triad (Stabilizer / Harmonizer / Defender) is **one substrate, three signal-pattern presets** — same coil, same MCUs, same power, same matching. Mk1 ships the device + the **Stabilizer preset only**. Harmonizer and Defender presets are firmware additions in Mk2 once their input pipelines (SynastryEngine handoff for Harmonizer; ambient-EM scanner channel for Defender) exist.

## 0a. Mission — what this device is *for*

The project has **two legitimate goals**, in priority order:

1. **Primary — wearer benefit.** The HelmKit Mk1 with Stabilizer preset must deliver a real, benevolent, measurable improvement to the wearer's experience: lower baseline autonomic reactivity over weeks of use, shorter recovery from acute stressors, and a subjective experience the wearer reports as stabilizing. **This is the deliverable.** Whether or not the ψ-field framework underneath the device turns out to be the correct physics, the device has to *actually work for the wearer in a benefic way.* That is the bar.
2. **Secondary — framework validation.** Because we now have hardware in hand that can carry $F^2$-instrumented sessions (see [`docs/mk1_f2_probe.md`](mk1_f2_probe.md)), Mk1 also produces data that *contributes toward* the longer programme of testing ψ-field theory empirically (F1–F11 in [`docs/falsification.md`](falsification.md)). Mk1 cannot land any of F1–F11 by itself — those require Mk2+ instrumentation and/or population-scale studies — but it can produce calibrated, pre-registered, sham-controlled session data that Mk1.5 and Mk2 inherit. The framework programme is a real goal of this project; it is just not the Mk1 success criterion.

These two goals are not in tension. The wiki calls the wearer-benefit outcome "operator-state stabilization" on the [`Psi Stabilizer`](https://wiki.fusiongirl.app/wiki/Psi_Stabilizer) page. In the framing of [`docs/psionics_field_theory.md §2`](psionics_field_theory.md), it is *driving the consciousness order parameter $C$ toward the symmetric phase and away from the runaway phase*. The same physical session that delivers (1) for the wearer produces the dataset that contributes to (2).

### How Mk1 actually delivers the wearer-benefit primary — the L0/L1/L2 floor

Mk1's wearer-benefit deliverable is not the bifilar coil. It is a **three-layer evidence-graded biofeedback floor** that runs on every session, active *or* sham, and which has decades of meta-analytic evidence supporting it independent of any ψ-field claim. The coil stim payload is an *experimental addition on top* of that floor.

| Layer | What it is | Evidence base |
|---|---|---|
| **L0** | Resonance-frequency breath pacer (~6 bpm), audio + LED breathing cue | Lehrer & Gevirtz RFB literature, $d \approx 0.4$–$0.8$ for stress/anxiety endpoints |
| **L1** | Closed-loop HRV-coherence biofeedback, live coherence metric rendered as audio harmonic | HeartMath / biofeedback meta-analyses (Goessl 2017), $d \approx 0.3$–$0.6$ |
| **L2** | Structured session container: settling → onboarding → active → closure → reflection, 30 min total | Standard biofeedback / mindfulness protocol structure |

Full specification: [`mk1_session_protocol.md`](mk1_session_protocol.md). The bifilar coil stim payload runs *only during the `active` phase* and *only on active-arm sessions*. L0+L1+L2 run identically on both arms.

**Consequence for the RCT.** The sham wearer is not deprived of benefit on the sham arm; the sham arm still gets L0+L1+L2. The active-vs-sham contrast isolates the *marginal* contribution of the coil stim payload above an already-working evidence-graded device. This is why a Mk1 unit can pass on wearer-benefit grounds (G2, §4.0) even if the coil stim payload nulls (G3, §4.0) — the biofeedback floor is the deliverable, the stim is the experiment.

### Why the discipline (sham, blinding, pre-registration) is mandatory

The sham-controlled discipline in §4.0 is not negotiable, for reasons that serve both goals simultaneously:

- **Placebo response in biofeedback devices is real, measurable, and large.** Any well-designed-looking head device worn with intent produces meaningful HRV/state response purely from expectation and ritual. This is a well-replicated finding in the biofeedback and neurofeedback literature, not an academic technicality.
- **Without sham-controlled blinding, we cannot tell whether the coil is doing anything beyond what L0+L1+L2 plus an empty enclosure would do.** That matters for goal (1): if the coil is no better than sham, the wearer is getting all their benefit from the biofeedback floor, and we are spending battery and bench iteration on a coil that adds nothing.
- A G3 pass means the coil contributes beyond the L0+L1+L2 floor; a G3 null means L0+L1+L2 is doing all the work — still a wearer-benefit pass on G2.
- The same discipline also makes the data useful to goal (2): only pre-registered, sham-controlled, $F^2$-instrumented sessions can later be re-analyzed as input to the F1–F11 programme.

### What the framework reframe (psion ontology) does and does not change here

The recent ontology work in [`docs/psion_quasiparticle.md`](psion_quasiparticle.md) sharpens *what the device is theoretically doing* (reactive-near-field Primakoff-class converter; driving $C$ on the EFT phase diagram via both direct CEMI and indirect psion-mediated channels). It does **not** change the Mk1 build, BOM, safety architecture, or operator-claim language. The wearer-facing description of the device remains **"a head-worn stabilizer that uses paced breathing and HRV biofeedback to help your autonomic state return to a calm coherent baseline

The sham-controlled discipline in §4.0 is not negotiable, for reasons that serve both goals simultaneously:

- **Placebo response in biofeedback devices is real, measurable, and large.** Any well-designed-looking head device worn with intent produces meaningful HRV/state response purely from expectation and ritual. This is a well-replicated finding in the biofeedback and neurofeedback literature, not an academic technicality.
- **Without sham-controlled blinding, we cannot tell whether the coil is doing anything beyond what L0+L1+L2 plus an empty enclosure would do.** That matters for goal (1): if the coil is no better than sham, the wearer is getting all their benefit from the biofeedback floor, and we are spending battery and bench iteration on a coil that adds nothing.
- A G3 pass means the coil contributes beyond the L0+L1+L2 floor; a G3 null means L0+L1+L2 is doing all the work — still a wearer-benefit pass on G2.
- The same discipline also makes the data useful to goal (2): only pre-registered, sham-controlled, $F^2$-instrumented sessions can later be re-analyzed as input to the F1–F11 programme.

### What the framework reframe (psion ontology) does and does not change here

The recent ontology work in [`docs/psion_quasiparticle.md`](psion_quasiparticle.md) sharpens *what the device is theoretically doing* (reactive-near-field Primakoff-class converter; driving $C$ on the EFT phase diagram via both direct CEMI and indirect psion-mediated channels). It does **not** change the Mk1 build, BOM, safety architecture, or operator-claim language. The wearer-facing description of the device remains **"a head-worn stabilizer that uses paced breathing and HRV biofeedback to help your autonomic state return to a calm coherent baseline."** That description is honest at Mk1 and consistent with both the ψ-field framework and any future framework that displaces it.

The build-side firewall from [`docs/psion_quasiparticle.md §7`](psion_quasiparticle.md) applies in full: psion vocabulary is internal engineering language; wearer-facing copy stays in physiological-effect language.

## 0. Decision gates (decide BEFORE ordering parts)

These three choices fix everything else in this plan. Don't skip them.

| Gate | Choice | Implication |
|------|--------|-------------|
| **G1 — Sensing channel** | (a) PPG-only, **or** (b) PPG + single dry EEG | (a) is faster, cheaper, lower-risk. (b) is the more interesting Mk1 but adds scalp-contact + cleaning discipline. |
| **G2 — Entrainment modality** | (a) Bone-conduction audio, (b) Photic, **or** (c) Sub-MHz pulsed coil | Mk1 ships exactly one. Audio is lowest-risk; coil is closest to the wiki "Psi Stabilizer" archetype. |
| **G3 — Compute node** | (a) Pi Zero 2 W, **or** (b) Pi 5 | (a) if G1=a and G2=a/b. (b) if G1=b (EEG benefits from more CPU). |

Default recommendation if no other constraints: **G1 = (a) PPG-only, G2 = (a) audio, G3 = (a) Pi Zero 2 W.** This is the fastest path to a working device that logs and entrains, and it reuses the psiStabilizer A01 capture pipeline verbatim.

**Wiki-aligned recommendation** (per [`wiki_synthesis.md`](wiki_synthesis.md)): **G1 = (a) PPG-only, G2 = (c) sub-MHz pulsed coil at 7.83 Hz default, G3 = (a) Pi Zero 2 W.** This is the Persinger-class apparatus the wiki specifies for the Mk1 Stabilizer preset. It costs an extra build pass — the dual-MCU safety architecture (see [`architecture.md` §3](architecture.md#3-safety-architecture-dual-mcu)) must be on the bench and validated before the first wear session, which audio entrainment does not require. Choose this path if the goal is to land the Stabilizer preset of the Psi-Tech triad rather than to land a working device fastest.

> **Pass 2 refresh (2026-05-12 wiki drop, see [`wiki_synthesis.md` §P2.1](wiki_synthesis.md#p21-the-frequency-regime--refined-not-the-same-as-pass-1)):** the wiki-canonical Mk1 stim path is now a **Tesla bifilar PCB coil (~30 × 30 mm, series-opposing connection) driven 1–8 MHz carrier modulated at 7.83 Hz** via SI5351 + Class-D, *not* the H-bridge-driven sub-MHz coil Pass 1 inferred. The G2=(c) option above remains the wiki-aligned path; the parts list under §1 changes from "Persinger-class solenoid + H-bridge + isolated supply" to "bifilar PCB coil + SI5351 + Class-D + thermistor". Mk1 stim target per the wiki Stabilizer Mk1 page is **≤ $250**, primary endpoint **time-to-coherence under standardised stressor**, blinded RCT $n \geq 30$ vs sham coil.

---

## 1. Bill of materials (representative; finalize after G1–G3)

Reusing the psiStabilizer A01 BOM where possible. Indicative line items, not authoritative:

| Item | Purpose | Source | Notes |
|------|---------|--------|-------|
| Pi Zero 2 W or Pi 5 | Compute node | — | Per G3 |
| MAX30102 breakout | PPG / HRV | Same as psiStabilizer A01 | Mounts at `HP-TL` or `HP-EL` |
| RM3100 magnetometer (optional) | Ambient EM context | Same as psiStabilizer A01 | Mounts at temple boom |
| 1S Li-ion 18650 cell + protection PCB | Power | Inventory | Mounts at `HP-R` |
| Buck/boost regulator (3.3 V, 5 V rails) | Bus power | — | At compute board |
| µSD ≥ 32 GB, high-endurance | Session logging | — | In compute board |
| Indicator LEDs (status + record-active + L1 coherence-render) | UX + closed-loop biofeedback rendering | Inventory | `HP-F` (status), forehelm interior (L1 render) |
| Bone-conduction transducers ×2 + headphone amp | **L0 breath-pacer + L1 coherence-render audio (always-on)** | — | `HP-EL`, `HP-ER`; required by the L0/L1 floor regardless of G2 choice |
| JST-SH 6-pin pigtails | Bus cabling | — | Per hardpoint |
| **If G2 = audio (legacy default):** additional binaural/isochronic audio routing through the same transducers | Stim payload | — | Reuses the L0/L1 transducers; payload is the entrainment tone on top |
| **If G2 = photic:** addressable LED strip segment, current-limited driver | Stimulation | Inventory | Inside visor accessory |
| **If G2 = coil (Pass 1 spec):** Persinger-class solenoid coils ×2, H-bridge driver, isolated supply | Stimulation | Custom-build | Temple booms; requires safety review |
| **If G2 = coil (Pass 2 wiki-canonical):** Tesla bifilar PCB coil ~30×30 mm + SI5351 clock + Class-D amp + low-pass + current-sense + thermistor | Stimulation | Custom PCB | Per wiki Stabilizer Mk1 BOM (≤ $250); 1–8 MHz carrier, 7.83 Hz envelope |
| **If G1 = (b) EEG:** OpenBCI Ganglion or equivalent single-channel module + dry electrodes | EEG | — | Fp1 or Fp2 contact at forehelm |

A real `hardware/Mk1/bom.csv` gets committed before the order is placed, in the same format as `external/psiStabilizer/hardware/A01/bom.csv`.

---

## 2. Frame work

Start from the existing Mk1-named modular geometry already in `3D-Models/HelmKit/`:
- `helmkit_DevType_v1_mk1_modular-proto1.{blend,stl}`
- `helmkit-forehelm_DevType_v1_mk1_modular-proto1.stl`
- `helmkit-rearhelm_DevType_v1_mk1_modular-proto1.stl`
- `helmkit-sidehelm_DevType_v1_mk1_modular-proto1.stl`
- `helmkit_Dev_v1-mk1-templeLeft-proto1{,b}.stl`
- `helmkit_headpiece_interlink-Dev_v1-mk1--proto1b.stl`

Mk1-specific deltas to add (in Blender, then re-export):
1. **Hardpoint footprints** standardized per [architecture.md §2](architecture.md#22-mechanical-contract). Add captive-nut pockets.
2. **Cable raceway** as a printed-in channel along the headband interior; minimum 6 × 6 mm cross-section.
3. **Battery bay** on `HP-R` sized to the chosen cell + protection PCB + 3 mm of foam.
4. **Compute bay** on `HP-R` adjacent to battery, with a hinged or magnetic door for µSD access.
5. **Temple sensor boom** on `HP-TL` / `HP-TR` for the PPG and/or magnetometer.

When the Mk1 frame freezes, **copy** the final files into a new `3D-Models/HelmKit/Mk1/` folder and tag the commit. Do not edit the iter geometry in place.

---

## 3. Software

Bootstrap via the submodule:

```bash
# from repo root
cd external/psiStabilizer
pip install -e software/
```

Mk1 software in this repo is a ree independent grades (G1 / G2 / G3)

Mk1 success is graded on **three independent axes**, each pre-registered, each publishable as its own outcome, each shippable independently. A Mk1 that scores **G1✓ / G2✓ / G3 null** is a *success* on wearer-benefit grounds with a clean null on the stim payload — the device ships, the wearer benefits, the framework hypothesis takes a hit on this implementation. That's an honest outcome. The old single-axis pass/fail collapsed these three independent questions into one and is replaced.

#### G1 — Engineering grade (the apparatus does what it claims, mechanically)

Necessary but not sufficient. Verifies the apparatus itself before any biology is invoked.

- Canonical frame tagged, BOM committed, schematic frozen.
- Stim driver scope-verified: carrier in band, envelope at target Hz, $\leq 500$ µT at scalp distance with the [`mk1_f2_probe.md`](mk1_f2_probe.md) calibrated probe.
- **Stim-disabled-when-not-recording interlock verified on bench** with a scope; forcing the capture loop off must drop stim output to zero with no software in the loop.
- **Stim-disabled-when-not-active-phase interlock verified**: MCU-B confirms phase=`active` and arm=`active` before passing stim. The L2 session-container state machine is the software side; MCU-B is the hardware side.
- MCU-B refuses every entry on the [`wiki_synthesis.md` §2.3](wiki_synthesis.md#23-the-safety-blacklist) blacklist (firmware unit test + bench fuzz).
- **Sham-equivalence verified across all sensory channels** (visual, mechanical, audible, thermal, EMI, vibrational) per [`mk1_session_protocol.md §7`](mk1_session_protocol.md). A coil with only visual indistinguishability is **not** a valid sham.
- L0 / L1 / L2 software bench-verified per [`mk1_session_protocol.md §10`](mk1_session_protocol.md).
- One valid 30-minute end-to-end session recorded and ingested by the psiStabilizer analyzer with zero $> 1$ s data dropouts.

If any G1 line fails, Mk1 fails on the engineering grade regardless of what biometrics later say. This is the floor.

#### G2 — Wearer-benefit grade (the device actually helps the wearer over time)

**This is the primary deliverable per §0a.** A G2 pass is the honest claim that this device benefits the wearer's life in measurable, sustained, subjectively-felt ways.

**Design:** within-subject **4-week ABAB or AB-BA crossover**, single wearer (developer self) initially.

**Primary endpoint — pre-registered composite:**

$$\text{G2 score} = w_1 \cdot \Delta\text{RMSSD}_{\text{morning}} + w_2 \cdot \Delta\text{PSS}_{\text{weekly}} + w_3 \cdot \Delta\text{SOL}_{\text{night}}$$

where

- $\Delta\text{RMSSD}_{\text{morning}}$ = change in waking-window resting HRV RMSSD across the active block vs the sham/baseline block.
- $\Delta\text{PSS}_{\text{weekly}}$ = change in weekly perceived-stress Likert composite ([`mk1_session_protocol.md §5`](mk1_session_protocol.md) panel, aggregated).
- $\Delta\text{SOL}_{\text{night}}$ = change in self-reported sleep-onset latency proxy (next-morning Likert).
- $w_1, w_2, w_3$ pre-registered, sum to 1, defaults $(0.4, 0.4, 0.2)$.

**Pass criteria, *all* required:**

1. **Pre-registration filed** at `experiments/Mk1/EH02_g2_wearer_benefit.md` before any session.
2. Pre-registered analysis on the locked dataset shows composite shift active-vs-baseline at $p < 0.05$ on the composite metric.
3. **Result published either direction.**

**Secondary endpoints:** each component of the composite, individually; individual Likert items; free-text qualitative analysis.

**What G2 does NOT use:** the cold-pressor stressor. Stressor sessions belong to G3 only; G2 is about trait-level stabilization across weeks of ordinary life, which is what wearers actually care about.

#### G3 — Stim-payload grade (does the bifilar coil contribute above the biofeedback floor?)

This is the framework-contribution endpoint and the single-session sham-controlled RCT.

**Design:** sham-controlled, blinded, paired active/sham sessions, $n \geq 30$, $\geq 80\%$ power at $\alpha = 0.05$.

**Primary endpoint:** time-to-coherence under cold-pressor stressor (procedure locked in [`mk1_session_protocol.md §6`](mk1_session_protocol.md)), measured from stressor offset until smoothed HRV coherence returns above pre-stressor 60 s baseline.

**Stressor:** **cold pressor**, 4 ± 1 °C water, non-dominant hand to wrist, 90 s, at minute 22 of the `Active` phase. Locked at pre-registration; not substitutable.

**Pass criteria, *all* required:**

1. **Pre-registration filed** at `experiments/Mk1/EH01_g3_stim_payload.md` before any session.
2. **Sham coil built and sham-equivalence verified** per G1 above.
3. **Operator blinded** to arm; randomization log sealed until analysis completes.
4. **$n \geq 30$** paired sessions completed under the protocol.
5. **Pre-registered statistical test** on locked dataset shows time-to-coherence shorter on active than sham at $p < 0.05$.
6. **Result published either direction.** A G3 null at G1✓ G2✓ is honest: the biofeedback floor is doing the wearer-benefit work, the coil is not contributing measurably above it on this endpoint.

**What does NOT count as G3 pass:**

- *"I tried it on myself and felt calmer."* No sham comparison.
- *"My HRV looked better in the second half of a session."* No blinding, no pre-registered endpoint.
- *"We re-analyzed the data and found a different metric that did reach significance."* Post-hoc fishing; pre-registered metric only.

#### Independence of G1 / G2 / G3

The three grades are computed and pre-registered separately. A unit that scores:

| G1 | G2 | G3 | Interpretation |
|---|---|---|---|
| ✓ | ✓ | ✓ | Full Mk1 success. Device works, wearer benefits, stim payload contributes. Strongest possible Mk1 outcome. |
| ✓ | ✓ | null | **Honest success.** Device works, wearer benefits from biofeedback floor; stim payload nulls. Ship the device on G2 grounds; iterate stim payload at Mk1.5. |
| ✓ | null | ✓ | Anomalous: stim payload moved a single-session endpoint but no trait-level benefit. Possible noise, possible real-but-narrow effect. Investigate before shipping. |
| ✓ | null | null | Engineering pass, no demonstrable wearer benefit. Don't ship; redesign protocol or modality. |
| null | * | * | Engineering fail; Mk1 fails regardless of G2/G3. Fix apparatus before re-running. |

#### Framework engagement at Mk1

Framework-level claims (F1–F11 in [`falsification.md`](falsification.md)) are **not adjudicated at Mk1.** F3 (resonance enhancement) and F4 (SAR-independence) require Mk2 instrumentation; F11 (Primakoff null-search) requires haloscope-class apparatus; F1, F2, F5, F6 are population-scale.

But Mk1 is **not framework-irrelevant**: sessions logged with the $F^2$ probe and pre-registered protocol produce calibrated data that Mk1.5 (matched-$F^2$ H1-vs-H2 comparison) and Mk2 (F3, F4) inherit directly. Landing Mk1 honestly is what makes the rest of the falsification programme defensible by inheritance rather than from-
- *"We re-analyzed the data and found a different metric that did reach significance."* Post-hoc fishing; pre-registered metric only.
s

Three pre-registrations, one per grade. File **before** any session of that grade runs.

| File | Grade | Design | Primary endpoint |
|---|---|---|---|
| `experiments/Mk1/EH00_g1_engineering.md` | G1 | Bench checklist; not a wearer study | Sign-off on all G1 line items |
| `experiments/Mk1/EH02_g2_wearer_benefit.md` | G2 | 4-week within-subject ABAB or AB-BA crossover, no stressor | Composite of $\Delta$ morning RMSSD + weekly PSS Likert + sleep-onset Likert, pre-registered weights |
| `experiments/Mk1/EH01_g3_stim_payload.md` | G3 | Sham-controlled blinded paired RCT, $n \geq 30$, cold-pressor stressor | Time-to-coherence post-stressor, active vs sham |

Template inherited from `external/psiStabilizer/experiments/00_preregistration_template.md`
Framework-level claims (F1–F11 in [`falsification.md`](falsification.md)) are **not adjudicated at Mk1.** F3 (resonance enhancement) and F4 (SAR-independence) require Mk2 instrumentation; F11 (Primakoff null-search) requires haloscope-class apparatus; F1, F2, F5, F6 are population-scale.

But Mk1 is **not framework-irrelevant**: sessions logged with the $F^2$ probe and pre-registered protocol produce calibrated data that Mk1.5 (matched-$F^2$ H1-vs-H2 comparison) and Mk2 (F3, F4) inherit directly. Landing Mk1 honestly is what makes the rest of the falsification programme defensible by inheritance rather than from-scratch.

### 4.1 The pre-registrations
1.5 when **G1 is passed and at least one of G2 or G3 has a published outcome (either direction)**. The remaining grade can be in progress.

### 5.1 G1 (engineering) gates

- [ ] Canonical Mk1 frame is tagged in git and lives in `3D-Models/HelmKit/Mk1/`.
- [ ] `hardware/Mk1/bom.csv` committed and matches the device built.
- [ ] `docs/architecture.md` rev tagged at `Mk1`.
- [ ] Stim driver scope-verified: carrier in band, envelope at target Hz, $\leq 500$ µT at scalp distance.
- [ ] Stim-disabled-when-not-recording interlock verified on-bench with an oscilloscope.
- [ ] Stim-disabled-when-not-`active`-phase interlock verified (MCU-B confirms L2 phase + arm).
- [ ] MCU-B refuses every entry on the [`wiki_synthesis.md` §2.3](wiki_synthesis.md#23-the-safety-blacklist) blacklist (firmware unit test + bench fuzz).
- [ ] Sham coil built and **sham-equivalence verified across visual, mechanical, audible, thermal, EMI, vibrational channels** per [`mk1_session_protocol.md §7`](mk1_session_protocol.md). A spectrum-analyzer pass at the wearer ear position is the audible-channel gate.
- [ ] L0 pacer, L1 coherence metric, L2 state machine bench-verified per [`mk1_session_protocol.md §10`](mk1_session_protocol.md).
- [ ] At least one valid 30-minute end-to-end session recorded, ingested by the psiStabilizer analyzer, with no data dropouts > 1 s.

### 5.2 G2 (wearer-benefit) gates

- [ ] Pre-registered G2 study filed at `experiments/Mk1/EH02_g2_wearer_benefit.md` *before* any G2-arm session.
- [ ] Composite endpoint weights $(w_1, w_2, w_3)$ pre-registered.
- [ ] 4-week within-subject ABAB or AB-BA crossover completed (single wearer at Mk1).
- [ ] Likert panel ([`mk1_session_protocol.md §5`](mk1_session_protocol.md)) administered every session pre/post + weekly + next-morning.
- [ ] Pre-registered analysis run on the locked dataset — **result published either direction.**

### 5.3 G3 (stim-payload) gates

- [ ] Pre-registered G3 study filed at `experiments/Mk1/EH01_g3_stim_payload.md` *before* any G3-arm session.
- [ ] Cold-pressor procedure locked per [`mk1_session_protocol.md §6`](mk1_session_protocol.md).
- [ ] Blinding protocol written, randomization log sealed.
- [ ] $n \geq 30$ paired active/sham sessions completed under the protocol.
- [ ] Pre-registered analysis run on the locked dataset — **result published either direction.**
- [ ] A written, dated decision exists for whether the bifilar coil payload contributes above the L0+L1+L2 floor,
- [ ] `hardware/Mk1/bom.csv` committed and matches the device built.
- [ ] `docs/architecture.md` rev tagged at `Mk1`.
- [ ] Stim driver scope-verified: carrier in band, envelope at target Hz, $\leq 500$ µT at scalp distance.
- [ ] Stim-disabled-when-not-recording interlock verified on-bench with an oscilloscope.
- [ ] Stim-disabled-when-not-`active`-phase interlock verified (MCU-B confirms L2 phase + arm).
- [ ] MCU-B refuses every entry on the [`wiki_synthesis.md` §2.3](wiki_synthesis.md#23-the-safety-blacklist) blacklist (firmware unit test + bench fuzz).
- [ ] Sham coil built and **sham-equivalence verified across visual, mechanical, audible, thermal, EMI, vibrational channels** per [`mk1_session_protocol.md §7`](mk1_session_protocol.md). A spectrum-analyzer pass at the wearer ear position is the audible-channel gate.
- [ ] L0 pacer, L1 coherence metric, L2 state machine bench-verified per [`mk1_session_protocol.md §10`](mk1_session_protocol.md). to Mk1.5/Mk2.)
- No multi-payload stimulation. One stim payload only (the bifilar coil). Biofeedback layers L0, L1, L2 always on and are *not* stim payloads.
- No closed-loop **stim** control. Stim schedule is open-loop, fixed per arm. (Closed-loop **biofeedback rendering** — L1 — *is* present, and modulates only the wearer-facing perceptual signal, not the stim hardware.)
- No EEG channel. Deferred to Mk2
### 5.2 G2 (wearer-benefit) gates

- [ ] Pre-registered G2 study filed at `experiments/Mk1/EH02_g2_wearer_benefit.md` *before* any G2-arm session.
- [ ] Composite endpoint weights $(w_1, w_2, w_3)$ pre-registered.
- [ ] 4-week within-subject ABAB or AB-BA crossover completed (single wearer at Mk1).
- [ ] Likert panel ([`mk1_session_protocol.md §5`](mk1_session_protocol.md)) administered every session pre/post + weekly + next-morning.
- [ ] Pre-registered analysis run on the locked dataset — **result published either direction.**

### 5.3 G3 (stim-payload) gates

- [ ] Pre-registered G3 study filed at `experiments/Mk1/EH01_g3_stim_payload.md` *before* any G3-arm session.
- [ ] Cold-pressor procedure locked per [`mk1_session_protocol.md §6`](mk1_session_protocol.md).
- [ ] Blinding protocol written, randomization log sealed.
- [ ] $n \geq 30$ paired active/sham sessions completed under the protocol.
- [ ] Pre-registered analysis run on the locked dataset — **result published either direction.**
- [ ] A written, dated decision exists for whether the bifilar coil payload contributes above the L0+L1+L2 floor, committed to the repo regardless of outcome.

---

## 6. What Mk1 does NOT do

Tape this list to the inside of the helmet:

- No 1.245 GHz, 2.45 GHz, or 300–900 MHz RF emission. (See [safety.md](safety.md). Hypothesis preserved; physical implementation deferred to Mk1.5/Mk2.)
- No multi-payload stimulation. One stim payload only (the bifilar coil). Biofeedback layers L0, L1, L2 always on and are *not* stim payloads.
- No closed-loop **stim** control. Stim schedule is open-loop, fixed per arm. (Closed-loop **biofeedback rendering** — L1 — *is* present, and modulates only the wearer-facing perceptual signal, not the stim hardware.)
- No EEG channel. Deferred to Mk2.
- No claim about cognitive enhancement, protection, or "psionic" effect on a wearer other than the developer self.
- No second-wearer sessions until at least 10 self-sessions are in the books and reviewed.
