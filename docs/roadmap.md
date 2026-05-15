# HelmKit Roadmap: Mk0.0 → Mk3.0

The HelmKit is staged across seven steps along an `x.0` / `x.5` ladder. Each step has a **defining question** it must answer before the next begins. The semantic pattern (what `.0` vs `.5` mean across every rung) is defined canonically in [mk_ladder.md](mk_ladder.md); this roadmap supplies the per-step engineering detail.

| Gen | Defining question | Status |
|-----|-------------------|--------|
| **Mk0.0** | Does it fit a real head, can it be printed, does it look the part? | ✅ Done (v2 type-b iter 9) |
| **Mk0.5** | Does the L0+L1+L2 biofeedback floor (sensing + feedback, no stim) deliver measurable wearer benefit on its own? | 🚧 In flight (Sensor Wave 1 ETA 2026-05-16) |
| **Mk1.0** | Does the bifilar-coil stim payload, sham-controlled, add value above the Mk0.5 floor for a stationary wearer (Tranquil mode)? | ⏸ Pending Mk0.5 G2 |
| **Mk1.5** | Does the device retain Tranquil performance AND deliver a Combat-mode loop (motion-tolerant, sweat-tolerant) for a moving / exerting wearer? | ⏸ Pending Mk1.0 |
| **Mk2.0** | Can the wearer use a state-aware closed-loop device standalone, with EEG + adaptive stim, and engage F3 / F4 directly? Focus / Creative / Vigilance / Social / Recovery modes unlocked. | ⏸ Pending Mk1.x |
| **Mk2.5** | Does a matched-$F^2$ H1-vs-H2 comparison favour either stim path above the closed-loop biofeedback floor? *(Repositioned from legacy Mk1.5 — matched-$F^2$ rigour requires the Mk2.0 state-aware substrate.)* | ⏸ Pending Mk2.0 |
| **Mk3.0** | Can two synchronized helmets deliver dyadic stabilization to a pair while engaging F7 and the Dicke superradiance $N^2$ scaling prediction? Manufacturable, regulatory-defensible. | ⏸ Pending Mk2.x |

The bridge from each step to the next is **gated on evidence**, not on aesthetics or hardware count. See [mk_ladder.md §3](mk_ladder.md) for the gating logic.

> **Note on numbering.** Earlier revisions of this roadmap used a coarser five-step ladder (`Mk0 / Mk1 / Mk1.5 / Mk2 / Mk3`). The current seven-step ladder is the May-2026 refinement after the sensor-wave purchase and the Tranquil-only vs Tranquil+Combat split was made explicit. The legacy `Mk1.5` (matched-$F^2$ H1-vs-H2) has been repositioned to `Mk2.5`; the legacy `Mk1` is now `Mk1.0`; a new `Mk0.5` and `Mk1.5` step have been inserted. The per-step detail in this file is being migrated to the new numbering; sections below may still reflect the legacy names until updated.

## Cross-cutting principles (the spine of the whole ladder)

These principles hold across every Mk. They are the connective tissue between generations.

1. **The L0/L1/L2 biofeedback floor is the spine.** Every Mk inherits the resonance-breath pacer (L0), closed-loop HRV-coherence rendering (L1), and structured session container (L2) from [`mk1_session_protocol.md`](mk1_session_protocol.md). Stim payloads are *additions on top*, never replacements. Mk2 adds L3 (EEG neurofeedback) and L4 (state-aware container adaptation); each is additive. A Mk3 wearer always has L0–L4 working *even if every stim payload nulls* — the device benefits them regardless.

2. **Three independent grades per Mk: G1, G2, G3.**
   - **G1 — Engineering:** apparatus does what it claims, mechanically. Calibrated, interlocked, sham-equivalent across all sensory channels.
   - **G2 — Wearer-benefit:** trait-level improvement to the wearer's life under within-subject multi-week ABAB design. Composite endpoint (RMSSD trend + PSS Likert + sleep). **This is the primary deliverable.**
   - **G3 — Framework-contribution:** single-session sham-controlled blinded RCT with the locked stressor; contributes data to the F1–F11 programme.
   Each grade is pre-registered separately, each shippable as its own outcome. A G1✓ G2✓ G3-null Mk is an **honest success**.

3. **Always-on instrumentation; opt-in stim.** PPG, EEG (Mk2+), $F^2$ probe ([`mk1_f2_probe.md`](mk1_f2_probe.md)), GSR (Mk2+), thermistor: always recording when the helmet is worn. Stim: opt-in per session, gated by the dual-MCU interlock plus L2 phase + arm.

4. **Sham extends to *all* sensory channels.** Every Mk's sham must be indistinguishable from active on visual, mechanical, audible, thermal, EMI, and vibrational channels. Visual-only sham is insufficient; an L2 null with weak sham is uninterpretable. See [`mk1_session_protocol.md §7`](mk1_session_protocol.md).

5. **Trait endpoints lead state endpoints.** Every Mk's G2 primary is a multi-week trait composite. Single-session stressor-recovery stays as a secondary and as the G3 framework endpoint. Trait is what the wearer experiences and reports; state is what falsifies a hypothesis.

6. **Wearer reports are first-class data.** Subjective Likert panels (calm, energy, clarity, intrusive thoughts, body comfort, sleep) pre/post every session, weekly aggregate. Logged in NDJSON alongside physiological channels. Pre-registered weights in the G2 composite.

7. **Wiki claim-firewall holds at every Mk.** Wearer-facing claim language at any Mk = what *that* Mk's G2 can demonstrate, nothing more. No psion language in wearer-facing copy ever, per [`wiki_refactor_brief.md §1.6`](wiki_refactor_brief.md) and [`psion_quasiparticle.md §7`](psion_quasiparticle.md). Engineering-internal vocabulary is unconstrained.

8. **Forward-compatible NDJSON schema.** Mk1 NDJSON reserves channels for Mk1.5, Mk2, Mk3. New channels are added; old ones are never renamed or repurposed. A Mk1 dataset is queryable by Mk3-era tooling and vice versa.

## Cross-project milestone

Per the wiki's [`Tho'ra Tech Maturity Levels`](https://wiki.fusiongirl.app/wiki/Tho%27ra_Tech_Maturity_Levels) page, the broader mission "goes live" the moment **(a)** the core Psi-Tech triad (Stabilizer / Harmonizer / Defender) clears Mk1, and **(b)** the Resonant Finder reaches Mk2. The HelmKit repo owns (a). Because the wiki's [`Psi-Tech`](https://wiki.fusiongirl.app/wiki/Psi-Tech) page confirms the triad shares one substrate (HelmKit psi-bay + near-field RF emitter + dual-MCU safety), clearing Mk1 means: one Mk1 HelmKit device + all three signal-pattern presets running on it. See [`wiki_synthesis.md`](wiki_synthesis.md) for the engineering translation.

---

## <a name="mk0"></a>Mk0 — Frame-Only Cosplay Prototype (current)

> *"Does it fit, print, and look the part?"* — **Yes.**

### What Mk0 is
- 3D-printed PLA / PETG geometric frame, head-worn, non-enclosed.
- Sized to a real head, with adjustable head ring (ratchet variant in the geometry files).
- Modular ear-shield and temple-piece accessories (already iterated through v3 / iter 4c).
- A passive phone-holder accessory family exists from the legacy iOS phase.

### What Mk0 is NOT
- Not a prototype in the engineering sense. No electronics, no sensors, no claims about wearer state.
- Not safe-rated for anything beyond "wearing a printed plastic frame."

### Existing assets (already in `3D-Models/HelmKit/`)
- Latest frame: `helmkit_prototype_v2_mk0_type-b_iter9*.{blend,stl}`
- Head ring (type-c): `helmkit_prototype_v2m0_type-c_parts_headRing_*.stl`
- Ratchet: `helmkit_prototype_v2m0_type-c_parts_ratchet_1a.stl`
- Ear shield: `helmkit_prototype_earShield-v3_iter4c.{blend,stl}`
- Mk1-named modular frame parts (forehelm / rearhelm / sidehelm / temple) — these are *transitional* geometry already drafted toward Mk1 and should be treated as Mk1 candidates, not Mk0.

### Exit criteria (already met)
- ✅ Wearable, comfortable for at least one 30-minute session.
- ✅ Frame and primary accessories print on a hobbyist FDM printer.
- ✅ Mountable hardpoints exist on the frame (ear shields, temple pieces, fore/rear/side pads).

### Open Mk0 chores before Mk1 begins
- [ ] Pick **one** canonical Mk0 frame from the iter9 set; freeze it as `Mk0/frame_final.stl`.
- [ ] Document the head-fit ranges that frame supports (circumference, ear-to-ear).
- [ ] Photograph and dimension the existing hardpoints; this becomes the input to the Mk1 hardpoint spec.

---

## <a name="mk1"></a>Mk1 — Working Prototype: a Closed-Loop Biofeedback Trainer with a Coil Stim Experiment

> **Defining question:** *Does it deliver real wearer benefit on its own merits (L0+L1+L2 floor), with the bifilar coil as a sham-controlled experiment riding on top?*

Mk1 is the first generation that has to *work*. The redefinition (May 2026) is critical: Mk1 is fundamentally **a closed-loop HRV biofeedback device** with a *layered* stim payload on top. The biofeedback is the floor (G2-graded, evidence-base $d \approx 0.4$–$0.8$ for the L0 pacer alone). The bifilar coil is the experiment (G3-graded, sham-controlled blinded RCT). Earlier roadmap revs had this inverted; the current rev fixes it.

Mk1 also bears the first preset of the wiki's Psi-Tech triad. Because the [wiki specifies](https://wiki.fusiongirl.app/wiki/Psi-Tech) that all three modules share one substrate, Mk1 ships the **Stabilizer preset only**: a baseline-locked steady reference field. The Harmonizer and Defender presets are firmware additions in Mk2 once their input pipelines exist (see [`wiki_synthesis.md`](wiki_synthesis.md)).

### Scope: minimum viable Psi-Tech
Mk1 carries three concurrent functional payloads:

1. **The biofeedback floor (L0 + L1 + L2)** — the wearer-benefit deliverable, runs on every session including sham. Full spec in [`mk1_session_protocol.md`](mk1_session_protocol.md).
   - **L0:** Resonance-breath pacer at ~6 bpm, bone-conduction audio + LED breathing cue.
   - **L1:** Closed-loop HRV-coherence biofeedback, live coherence metric rendered as audio harmonic.
   - **L2:** Structured 30-min session container: settling → onboarding → active → closure → reflection.

2. **One sensing module** — biometric/neural channel, chosen for safety and signal quality:
   - PPG (heart-rate / HRV) — `MAX30102` class, on the temple or behind-ear. **Required for L1.**
   - Ambient triaxial magnetometer (`RM3100`) on a temple boom — same sensor family the psiStabilizer A01 uses, so data pipelines are shared.
   - **$F^2$ probe** (DIY bifilar pickup, [`mk1_f2_probe.md`](mk1_f2_probe.md)) — records stim dose delivered, required for G3 and forward-compatible with Mk1.5 matched-$F^2$.
   - EEG is **deferred to Mk2.**

3. **One stim payload** — the bifilar PCB coil, wiki-canonical:
   - Bifilar PCB coil ~30 × 30 mm, series-opposing connection, driven 1–8 MHz carrier modulated at 7.83 Hz envelope, via SI5351 + Class-D + matching network.
   - $\leq 500$ µT at scalp distance, $\leq 250$ USD BOM, ICNIRP-bounded.
   - **Sham-controlled, blinded RCT, $n \geq 30$ paired sessions** is the G3 gate.

> **What Mk1 explicitly does NOT do (deferred to Mk1.5/Mk2+):** transmit 1.245 GHz, 2.45 GHz, or 300–900 MHz RF at the head. These bands require SAR measurement, FCC licensing review, and a biological-effects literature review that Mk1 will not have completed. See [safety.md](safety.md). The user's hypothesis space for those frequencies is preserved as Mk1.5/Mk2 R&D, not killed.

### Mk1 hardware blocks
| Block | Role | Mounts to |
|-------|------|-----------|
| Compute node | Pi Zero 2 W or Pi 5 (depending on EEG decision) — same family psiStabilizer A01 uses | Rear-helm hardpoint |
| Power | 1S Li-ion + protection PCB, hot-swappable | Rear-helm |
| Sensor bus | I²C/SPI breakout, shielded short runs to temple boom | Internal channel along headband |
| Audio out | Bone-conduction transducers | Ear-shield hardpoint |
| Stim out | Coil driver OR LED driver (one, not both, in Mk1) | Temple hardpoint |
| Indicator | Single status LED + recording-active LED | Forehelm |
| Logging | NDJSON to onboard µSD, exact same schema as psiStabilizer `a01_capture` | Rear-helm compute |

### Mk1 frame deltas vs Mk0
- Convert the iter9 frame into a **modular** assembly. The Mk1-named `forehelm / rearhelm / sidehelm / temple` STLs already in the tree are the starting geometry.
- Add **standardized hardpoints**: see [architecture.md](architecture.md#hardpoint-spec). Mk1 freezes v1 of that spec.
- Internal cable channel along the headband (printed-in cable raceway).
- Mountable battery bay on the rearhelm.

### Mk1 software
- Reuse `psistabilizer.capture.a01_capture` from the submodule. Same NDJSON schema.
- Add one entrainment-driver module (audio, photic, or coil — pick one before build).
- A pre-registered E0X experiment for whichever modality is shipped first (template: `external/psiStabilizer/experiments/00_preregistration_template.md`).

### Mk1 exit criteria
- [ ] **G1 (engineering)** — all gates in [`mk1_buildplan.md §5.1`](mk1_buildplan.md) passed.
- [ ] **G2 (wearer-benefit)** — 4-week within-subject ABAB filed, completed, analyzed, **published either direction**.
- [ ] **G3 (stim-payload)** — $n \geq 30$ paired active/sham cold-pressor sessions completed, analyzed, **published either direction**.
- [ ] **Move-to-Mk1.5 trigger:** G1 ✓ AND (G2 ✓ OR G3 ✓) AND a written, dated decision on the other grade.

A Mk1 result of G1✓ / G2✓ / G3 null is an **honest success** — device works, wearer benefits from L0+L1+L2 floor, coil stim payload nulls. Ship on G2 grounds, iterate stim payload at Mk1.5.

---

## <a name="mk1_5"></a>Mk1.5 — Matched-$F^2$ H1-vs-H2 Comparison

> **Defining question:** *Does a matched-$F^2$ comparison between H1 (sub-MHz bifilar coil) and H2 (Frey-class pulsed UHF) favour either stim path above the L0+L1+L2 biofeedback floor?*

Mk1.5 is **Mk1 hardware + a second stim payload at GHz-range pulsed UHF** for the [H2 hypothesis](h2_modulated_uhf_hypothesis.md). Wearer-side experience: indistinguishable from Mk1. Bench-side: a second emitter, SAR-bounded duty-cycling, and an expanded G3 RCT.

### What's new vs Mk1
- **Second stim payload:** pulsed UHF emitter (~1.245 GHz Frey-anchor or matched band per H2 spec), low duty cycle, SAR-bounded per ICNIRP at scalp.
- **$F^2$-matched comparison:** same delivered $F^2$ envelope on H1 (bifilar coil) vs H2 (pulsed UHF) arms, enabled by the Mk1-inherited $F^2$ probe.
- **Three-arm G3 RCT:** H1-active / H2-active / sham, $n \geq 30$ per arm, blinded, paired-within-wearer where practical.
- One row added to MCU-B blacklist for the H2 band's safety envelope; dual-MCU firewall otherwise identical.

### What stays vs Mk1
- L0 + L1 + L2 biofeedback floor: **identical, runs on all three arms.**
- G2 wearer-benefit endpoint: identical (4-week ABAB, composite trait endpoint).
- Safety architecture, frame, BOM bulk: inherited from Mk1.

### Mk1.5 exit criteria
- [ ] **G1**: H2 emitter calibrated, SAR-bounded on phantom, thermal-rise < 0.1 °C at scalp surface across 20 min active.
- [ ] **G2**: as Mk1 (4-week ABAB across the three-arm sequence).
- [ ] **G3**: three-way active comparison, each pre-registered. Engages F-precursor for F3 (resonance) and F4 (SAR-independence) as well as H1-vs-H2.

Framework contribution: **first matched-$F^2$ comparison data on the ladder.** Engages precursor to F3 and F4; does not yet adjudicate them.

---

## <a name="mk2"></a>Mk2 — State-Aware Closed-Loop Stabilizer (engages F3, F4)

> **Defining question:** *Can the wearer use a state-aware closed-loop device standalone, with EEG + adaptive stim, and engage F3 / F4 directly?*

Mk2 is the first Mk that has *full state-aware control*: PPG + EEG + GSR + $F^2$ probe + closed-loop stim modulation driven by wearer state in real time. This is the apparatus the wiki Stabilizer page actually promises.

### Scope additions over Mk1.5

**Sensing:**
- 4–8 channel dry EEG (Fp1/Fp2/Cz + temporal montage). OpenBCI Cyton-class or equivalent. **Required for L3.**
- Tri-axial $F^2$ probe (vs single-axis Mk1).
- GSR / EDA for sympathetic-channel covariate.
- Ambient EM dosimeter (RF survey) — feeds Defender preset.

**Stim:**
- **Closed-loop stim envelope.** The 7.83 Hz envelope (H1) or H2 pulse repetition rate adapts to wearer EEG/HRV state in real time. **The state-aware Stabilizer the wiki actually describes.** MCU-B interlock unchanged: stim-disabled-when-not-`active`-phase still gates the hardware.
- Multi-payload: H1 coil + photic (alpha-band entrainment via visor) + tACS module (optional, electrode hardpoint at Fp1/Fp2). Co-driven, phase-locked.
- Defender preset slot exercised: ambient EM dosimeter feeds a counter-field or alerting logic.
- Sub-GHz pulsed RF (300–900 MHz) under safety review, mandatory SAR measurement, interlock disables on threshold breach. 2.45 GHz remains deferred.

**Compute:**
- Pi 5 or equivalent (EEG DSP + closed-loop control needs the headroom).

**Wearer-benefit additions (atop the L0+L1+L2 floor):**
- **L3 — EEG neurofeedback.** Alpha/theta-ratio or alpha-band power rendered as a second audio channel alongside L1.
- **L4 — State-aware container adaptation.** L2 container script branches based on detected wearer arousal at session start (high-arousal start → longer settling phase; low-arousal → shorter; etc.).

### Mk2 frame deltas
- Real cable management (printed harness + connectors), not loose internal runs.
- Hot-swap module bays for each hardpoint (electrically keyed, polarity-protected).
- Replace PLA/PETG with a structurally honest material on temple/rearhelm load points (PA-CF, PETG-CF, or printed-and-machined hybrid).
- Optical hardpoint added: HUD optic mount (offset combiner or waveguide), preparing for an actual HUD module.

### Mk2 exit criteria
- [ ] **G1**: cross-unit safety verified, EEG channel calibrated, closed-loop stim controller verified to drop to safe state on any sensor dropout.
- [ ] **G2**: 4-week ABAB with L0+L1+L2+L3+L4 floor; second wearer (non-developer) included in the design.
- [ ] **G3 (F3 engagement)**: scan envelope frequency across 6.5–9.5 Hz at matched $F^2$; pre-registered predict-and-verify for enhancement at Schumann frequency vs detuned.
- [ ] **G3 (F4 engagement)**: holding $F^2$ envelope constant, vary SAR by 3× (low duty vs high duty at matched peak $F^2$); test whether effect tracks $F^2$ (psi-mediated prediction) or SAR (thermal artifact prediction).
- [ ] A non-developer can put it on, run a guided session, and take it off — without help.

Framework contribution: **first Mk that engages F-criteria directly** (F3 + F4).

---

## <a name="mk3"></a>Mk3 — Dyadic Synastry Pair (engages F7, Dicke superradiance) + Production Model

> **Defining question:** *Can two synchronized helmets deliver dyadic stabilization to a couple/pair while engaging F7 and the Resonant-Pipeline $N^2$ scaling prediction?*

Mk3 is the first multi-unit Mk and the first manufacturable design. Two Mk2-class helmets driven from a common synastry compute node, optionally driven by [SynastryEngine](https://github.com/Jthora/SynastryEngine) astrological timing. The Psi Harmonizer preset (one substrate, different signal pattern per wiki triad) goes live here.

### Topology and new capability
- Two helmets, time-synchronized to < 1 ms (PPS or NTP-disciplined RTC).
- Shared session manifest; one wearer's HRV/EEG state available as input to the other wearer's stim controller.
- Optional SynastryEngine handoff: chart-derived timing windows modulate session schedule.
- Cross-unit safety interlock: if either unit's MCU-B faults, *both* units drop stim.

### Wearer-benefit additions (atop L0–L4)
- **Dyadic biofeedback.** Each wearer sees/hears their *partner's* coherence alongside their own. Strong dyadic-HRV-coherence literature exists (couple therapy, parent-infant co-regulation, etc.).
- **Co-regulation protocols.** Structured paced-breathing dyads, mutual coherence training.

### Framework contributions
- **F7 (universal $\alpha$):** same drive, different physical setups (two Mk3 pairs in different rooms / cities) — does the population-averaged response track $\alpha$ as a universal constant across operators?
- **Resonant-pipeline / Dicke superradiance test:** with 2 emitters, predict and test $N^2 = 4\times$ output scaling at matched per-unit drive (vs. $N=2$ linear summation null hypothesis). This is the wiki [`Resonant Pipeline`](https://wiki.fusiongirl.app/wiki/Resonant_Pipeline) prediction made testable.

### Production / regulatory scope (separate axis from framework engagement)
Mk3 is also the manufacturable generation:
- Frame redesigned for **adjustable head-size population fit** (S/M/L or continuous adjust). Mk0–Mk2 fit one head; Mk3 fits a population.
- Aesthetic / ergonomic pass replaces cosplay-grade silhouette with a defensible product industrial design.
- Manufacturing transition: critical structural parts to SLS/MJF nylon or injection-molded equivalents; PCBs leave breakout form; cabling becomes flex-PCB harness.
- Documentation pack: per-modality intended-use, dosage envelope, contraindications; SAR / EMF compliance test results; battery/thermal safety; wearer onboarding flow, consent flow, data-handling spec.
- **Higher-band RF decided here, not earlier.** Whether 1.245 GHz / 2.45 GHz emitters ship in Mk3 depends on Mk1.5/Mk2 evidence + safety review.
- **Regulatory posture decided here:** "wellness device" vs. "research instrument"; distribution model (sell, kit, open-build).

### Mk3 exit criteria
- [ ] **G1**: five units built by someone other than the lead designer, all functional.
- [ ] **G2 (dyadic)**: dyadic coherence improvement vs. independent-Mk2-pair control, across $\geq 5$ dyads.
- [ ] **G3 (F7)**: precision $\alpha$ measurement consistent across $\geq 2$ Mk3 pairs in independent setups, within $3\sigma$.
- [ ] **G3 (Dicke)**: 2-unit $N^2$ scaling test pre-registered and run; result published either direction.
- [ ] Fits ≥ 90% of a defined target population in a fit study.
- [ ] Wearer-facing manual, consent flow, and safety sheet exist and have been reviewed.

---

## Cross-cutting commitments

- **Pre-registration before wear-session.** Every new capability files a pre-reg in `experiments/` before the first session that uses it.
- **One canonical frame per generation.** No "the Mk1 was *kind of* the iter4c branch." Each generation freezes one geometry, one BOM, one schematic, one firmware tag.
- **Submodule contract.** The psiStabilizer submodule provides the measurement/analysis layer. The HelmKit repo does not duplicate that — it integrates it.
- **iOS legacy is retired.** `iOS_oldBuild/` is kept for archival reference and is not part of the Mk1+ build path.
