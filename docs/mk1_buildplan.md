# HelmKit Mk1 — Build Plan

The first generation that has to **work**. This document is what the Mk1 build will look like, concretely, before any electronics are ordered.

## 0. Decision gates (decide BEFORE ordering parts)

These three choices fix everything else in this plan. Don't skip them.

| Gate | Choice | Implication |
|------|--------|-------------|
| **G1 — Sensing channel** | (a) PPG-only, **or** (b) PPG + single dry EEG | (a) is faster, cheaper, lower-risk. (b) is the more interesting Mk1 but adds scalp-contact + cleaning discipline. |
| **G2 — Entrainment modality** | (a) Bone-conduction audio, (b) Photic, **or** (c) Sub-MHz pulsed coil | Mk1 ships exactly one. Audio is lowest-risk; coil is closest to the wiki "Psi Stabilizer" archetype. |
| **G3 — Compute node** | (a) Pi Zero 2 W, **or** (b) Pi 5 | (a) if G1=a and G2=a/b. (b) if G1=b (EEG benefits from more CPU). |

Default recommendation if no other constraints: **G1 = (a) PPG-only, G2 = (a) audio, G3 = (a) Pi Zero 2 W.** This is the fastest path to a working device that logs and entrains, and it reuses the psiStabilizer A01 capture pipeline verbatim.

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
| Indicator LEDs (status + record-active) | UX | Inventory | `HP-F` |
| JST-SH 6-pin pigtails | Bus cabling | — | Per hardpoint |
| **If G2 = audio:** bone-conduction transducers ×2, headphone amp | Stimulation | — | `HP-EL`, `HP-ER` |
| **If G2 = photic:** addressable LED strip segment, current-limited driver | Stimulation | Inventory | Inside visor accessory |
| **If G2 = coil:** Persinger-class solenoid coils ×2, H-bridge driver, isolated supply | Stimulation | Custom-build | Temple booms; requires safety review |
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

Mk1 software in this repo is a thin wrapper:
- `software/helmkit_mk1/capture.py` — wraps `psistabilizer.capture.a01_capture` and adds the chosen entrainment driver.
- `software/helmkit_mk1/entrainment/{audio,photic,coil}.py` — one of these is implemented per G2.
- `software/helmkit_mk1/cli.py` — `helmkit run --session-id ... --modality audio --hz 10 --duration 1800`.
- Session log writes to `sessions/<UTC>/<session_id>.ndjson` in the schema the psiStabilizer analyzer expects.

The recording-active hardware line is wired to a GPIO that the capture loop toggles. The stim driver hardware-ANDs against that line. **No stim without recording.**

---

## 4. The first study

Before the first wear session, file a pre-registration based on the psiStabilizer template:
`external/psiStabilizer/experiments/00_preregistration_template.md`

Mk1's first study should be the simplest defensible one:

| | If G2 = audio | If G2 = photic | If G2 = coil |
|---|---|---|---|
| **Primary measure** | HRV (RMSSD) before/during/after | HRV; photic-driving in EEG if G1=b | HRV; subjective state report |
| **Stimulus** | 10 Hz isochronic tone, 30 min | 10 Hz LED flicker, 20 min, photic-screened wearer only | 5–10 Hz sub-MHz pulsed field, 20 min, single-blind sham/active |
| **N** | self, ≥ 10 sessions before any second wearer | self, ≥ 10 sessions | self, ≥ 10 sessions |
| **Falsifier** | No measurable RMSSD shift outside expected diurnal variance | No photic driving response | No HRV shift; no subjective state shift vs sham |

Commit the pre-registration to `experiments/Mk1/EH01_<modality>.md` **before** the first session.

---

## 5. Exit checklist for Mk1

Move to Mk2 when **all** of these are true:

- [ ] Canonical Mk1 frame is tagged in git and lives in `3D-Models/HelmKit/Mk1/`.
- [ ] `hardware/Mk1/bom.csv` committed and matches the device built.
- [ ] `docs/architecture.md` rev tagged at `Mk1`.
- [ ] Pre-registered Mk1 study filed at `experiments/Mk1/EH01_<modality>.md`.
- [ ] At least one valid 30-minute session recorded, ingested by the psiStabilizer analyzer, with no data dropouts > 1 s.
- [ ] Stim-disabled-when-not-recording interlock verified on-bench with an oscilloscope.
- [ ] A written, dated decision exists for whether the chosen Mk1 modality reproduces a measurable effect — published either way.

---

## 6. What Mk1 does NOT do

Tape this list to the inside of the helmet:

- No 1.245 GHz, 2.45 GHz, or 300–900 MHz RF emission. (See [safety.md](safety.md). Hypothesis preserved; physical implementation deferred.)
- No multi-modality stimulation. One modality only.
- No closed-loop control. Open-loop, fixed-schedule stim, with measurement around it.
- No claim about cognitive enhancement, protection, or "psionic" effect on a wearer other than the developer self.
- No second-wearer sessions until at least 10 self-sessions are in the books and reviewed.
