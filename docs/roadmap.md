# HelmKit Roadmap: Mk0 → Mk3

The HelmKit is staged in four generations. Each generation has a **defining question** it must answer before the next begins.

| Gen | Defining question | Status |
|-----|-------------------|--------|
| **Mk0** | Does it fit a real head, can it be printed, does it look the part? | Done (v2 type-b iter 9) |
| **Mk1** | Can it measure neural/biometric state and apply *one* safe entrainment modality, on-head, logged, reproducibly? | Next |
| **Mk2** | Can a wearer use it standalone, multi-modality, in real environments, with a defensible safety envelope? | Scoped |
| **Mk3** | Can it be manufactured, fit a population, and pass a documentation/regulatory bar suitable for distribution? | Scoped |

The bridge from each generation to the next is **gated on evidence**, not on aesthetics or hardware count.

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

## <a name="mk1"></a>Mk1 — Working Prototype

> **Defining question:** *Can it measure neural/biometric state and apply ONE safe entrainment modality, on-head, logged, reproducibly?*

Mk1 is the first generation that has to *work*. "Work" here is the same definition the psiStabilizer project uses: **a measurement is recorded, a stimulus is delivered, and the relationship between them is logged falsifiably.**

Mk1 also bears the first preset of the wiki's Psi-Tech triad. Because the [wiki specifies](https://wiki.fusiongirl.app/wiki/Psi-Tech) that all three modules share one substrate, Mk1 ships the **Stabilizer preset only**: a baseline-locked steady reference field. The Harmonizer and Defender presets are firmware additions in Mk2 once their input pipelines exist (see [`wiki_synthesis.md`](wiki_synthesis.md)).

### Scope: minimum viable Psi-Tech
Mk1 carries exactly two functional payloads:

1. **One sensing module** — biometric/neural channel, chosen for safety and signal quality:   - PPG (heart-rate / HRV) — `MAX30102` class, on the temple or behind-ear.
   - **Optional** single-channel dry EEG over Fp1 / Fp2 — only if the Mk1 wearer accepts the cleanliness/contact discipline that requires.
   - Ambient triaxial magnetometer (`RM3100`) on a temple boom — same sensor family the psiStabilizer A01 uses, so data pipelines are shared.

2. **One entrainment module** — *safe-by-construction* options only:
   - **Bone-conduction binaural / isochronic audio** via the existing ear-shield hardpoint. Lowest-risk entrainment modality on the menu.
   - **Photic entrainment** via low-current LEDs on the inside of a visor accessory (with explicit photic-epilepsy exclusion per wearer screening).
   - **Sub-MHz pulsed-magnetic coil** (Persinger-class, ≤ a few hundred µT, ≤ 100 Hz pulse rate) mounted at temple hardpoint. Documented, low-energy, decades of literature; safety envelope is well-characterized.

> **What Mk1 explicitly does NOT do (deferred to Mk2+):** transmit 1.245 GHz, 2.45 GHz, or 300–900 MHz RF at the head. These bands require SAR measurement, FCC licensing review, and a biological-effects literature review that Mk1 will not have completed. See [safety.md](safety.md). The user's hypothesis space for those frequencies is preserved as Mk2/Mk3 R&D, not killed.

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
- [ ] Wearable for ≥ 30 min with no skin irritation or thermal drift > 1 °C.
- [ ] Records at least one biometric channel at ≥ 95 % uptime across a 30-min session.
- [ ] Delivers one entrainment modality with documented dosage (Hz, amplitude/SPL/intensity, duration).
- [ ] Produces a session log file that the psiStabilizer analysis CLI can ingest.
- [ ] A pre-registered Mk1 study has been **filed before** the first wear-session.

---

## <a name="mk2"></a>Mk2 — Advanced Test Type

> **Defining question:** *Can a wearer use it standalone, multi-modality, in real environments, with a defensible safety envelope?*

Mk2 is where the user's "real psi-tech" ambition is allowed to land, gated behind Mk1's measurement discipline.

### Scope additions over Mk1
- **Multi-channel sensing** — add the channels Mk1 deferred:
  - Dry EEG (multi-channel, Fp1/Fp2/Cz minimum), or OPM-MEG class sensor if budget allows (the wiki's named real-world parallel for HelmKit is OPM-MEG; Rea et al. 2021, PMID 34273527).
  - GSR / EDA.
  - Ambient EM dosimeter (RF survey) — feeds both the Stabilizer logic and a Defender module.
- **Multi-modality stimulation** — Mk1's one entrainment becomes two or three concurrent:
  - Audio + photic + coil.
  - Optional medical-grade tACS module (electrode hardpoint at Fp1/Fp2). Same exclusion list as psiStabilizer's tACS option applies.
- **First RF emitter on the platform** — under safety review:
  - Low-power sub-GHz pulsed RF (300–900 MHz band) with mandatory SAR measurement and an interlock that disables it if SAR exceeds a documented threshold.
  - This is where the user's 300–900 MHz hypothesis is first allowed to physically exist on the device.
  - 2.45 GHz remains deferred until Mk2 evidence exists.
- **Onboard fusion** — compute node correlates sensing channels with stimulation in real time. Closed-loop entrainment (stop / adjust based on EEG state) becomes possible.
- **Defender integration** — Psi Defender module slot is exercised: the ambient EM dosimeter feeds a counter-field or alerting logic.

### Mk2 frame deltas
- Real cable management (printed harness + connectors), not loose internal runs.
- Hot-swap module bays for each hardpoint (electrically keyed, polarity-protected).
- Replace PLA/PETG with a structurally honest material on the temple/rearhelm load points (PA-CF, PETG-CF, or printed-and-machined hybrid).
- Optical hardpoint added: HUD optic mount (offset combiner or waveguide), preparing for an actual HUD module.

### Mk2 exit criteria
- [ ] A wearer can run a multi-channel session standalone (no laptop tethered).
- [ ] Each stimulation modality has its own pre-registered Mk2 study.
- [ ] Any RF emitter has a measured SAR figure + documented interlock.
- [ ] A non-developer can put it on, run a guided session, and take it off — without help.

---

## <a name="mk3"></a>Mk3 — Production Model

> **Defining question:** *Can it be manufactured, fit a population, and pass a documentation/regulatory bar suitable for distribution?*

Mk3 is no longer about novel hardware; it is about **manufacturability, fit, and documentation.**

### Scope shifts vs Mk2
- Frame redesigned for **adjustable head-size population fit** (S/M/L or continuous adjust). Mk0/Mk1/Mk2 fit one head; Mk3 fits a population.
- Aesthetic and ergonomic pass — replaces the cosplay-grade silhouette with a defensible product industrial design (or a defensible-as-cosplay one, deliberately).
- Manufacturing transition:
  - Critical structural parts go to SLS / MJF nylon or injection-molded equivalents.
  - PCBs leave breakout-board form and are designed as integrated boards per module slot.
  - Cabling becomes a flex-PCB harness.
- Documentation pack:
  - Per-modality intended-use, dosage envelope, contraindications.
  - SAR / EMF compliance test results.
  - Battery and thermal safety test results.
  - Wearer onboarding flow, consent flow, data-handling spec (lift the psiStabilizer `data_handling.md` posture).
- **Higher-band RF is decided here, not earlier.** Whether 1.245 GHz / 2.45 GHz emitters ship in Mk3 is a function of what Mk2's evidence and safety review concluded — not what we hoped for at Mk1.
- **Regulatory posture decided here**, not earlier:
  - "Wellness device" framing vs. "research instrument" framing.
  - Distribution model (sell, kit, open-build).

### Mk3 exit criteria
- [ ] Five units built by someone other than the lead designer, all functional.
- [ ] Fits ≥ 90 % of a defined target population in a fit study.
- [ ] Every shipped capability has a published, pre-registered study supporting it.
- [ ] A wearer-facing manual, consent flow, and safety sheet exist and have been reviewed.

---

## Cross-cutting commitments

- **Pre-registration before wear-session.** Every new capability files a pre-reg in `experiments/` before the first session that uses it.
- **One canonical frame per generation.** No "the Mk1 was *kind of* the iter4c branch." Each generation freezes one geometry, one BOM, one schematic, one firmware tag.
- **Submodule contract.** The psiStabilizer submodule provides the measurement/analysis layer. The HelmKit repo does not duplicate that — it integrates it.
- **iOS legacy is retired.** `iOS_oldBuild/` is kept for archival reference and is not part of the Mk1+ build path.
