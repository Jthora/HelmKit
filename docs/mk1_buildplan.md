# HelmKit Mk1 — Build Plan

The first generation that has to **work**. This document is what the Mk1 build will look like, concretely, before any electronics are ordered.

> **Key insight from [`wiki_synthesis.md`](wiki_synthesis.md):** the Psi-Tech triad (Stabilizer / Harmonizer / Defender) is **one substrate, three signal-pattern presets** — same coil, same MCUs, same power, same matching. Mk1 ships the device + the **Stabilizer preset only**. Harmonizer and Defender presets are firmware additions in Mk2 once their input pipelines (SynastryEngine handoff for Harmonizer; ambient-EM scanner channel for Defender) exist.

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
| Indicator LEDs (status + record-active) | UX | Inventory | `HP-F` |
| JST-SH 6-pin pigtails | Bus cabling | — | Per hardpoint |
| **If G2 = audio:** bone-conduction transducers ×2, headphone amp | Stimulation | — | `HP-EL`, `HP-ER` |
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

Mk1 software in this repo is a thin wrapper:
- `software/helmkit_mk1/capture.py` — wraps `psistabilizer.capture.a01_capture` and adds the chosen entrainment driver.
- `software/helmkit_mk1/entrainment/{audio,photic,coil}.py` — one of these is implemented per G2.
- `software/helmkit_mk1/cli.py` — `helmkit run --session-id ... --modality audio --hz 10 --duration 1800`.
- Session log writes to `sessions/<UTC>/<session_id>.ndjson` in the schema the psiStabilizer analyzer expects.

The recording-active hardware line is wired to a GPIO that the capture loop toggles. The stim driver hardware-ANDs against that line. **No stim without recording.**

---

## 4. The first study

### 4.0 What "works" means — the three-layer pass/fail

The HelmKit Mk1 is a **Psychological State Stabilizer**: a head-worn
device whose Stabilizer preset is meant to *shorten the time the
wearer's autonomic state takes to return to a defined coherent
baseline after a standardised stressor.* "It works" is a claim with
three independent layers, each of which must be satisfied
separately, and the outer two are *publishable as nulls* — there is
no escape hatch where a failed device gets called a success.

#### Layer 1 — Engineering pass/fail (the device does what it claims, mechanically)

Necessary but not sufficient. Verifies the apparatus itself, before
any biology is invoked.

- Canonical frame tagged, BOM committed, schematic frozen
  (this sprint's exit checklist, §5).
- Stim driver produces the **specified** waveform at the temple
  coil — verified on oscilloscope: carrier in band, envelope at the
  target Hz, amplitude $\leq 500$ µT at scalp distance with a
  calibrated probe.
- **Stim-disabled-when-not-recording interlock verified on bench**
  with a scope: forcing the capture loop off must drop the stim
  output to zero with no software in the loop.
- MCU-B refuses to enable any blacklisted modulation pattern from
  the [`wiki_synthesis.md` §2.3](wiki_synthesis.md#23-the-safety-blacklist)
  blacklist (seizure / cardiac-coupling / Frey-effect bands).
- One valid 30-minute session recorded and ingested by the
  psiStabilizer analyzer with zero $> 1$ s data dropouts.

If any of these fail, Mk1 fails on the engineering layer, regardless
of what biometrics later say. This is the floor.

#### Layer 2 — Functional pass/fail (does the Stabilizer preset stabilize anything measurable above placebo?)

This is the layer most "psi" devices conveniently never address.

**Primary endpoint (wiki-canonical, Pass 2):**
**time-to-coherence under a standardised stressor**, measured as the
wall-clock seconds from stressor offset until **HRV RMSSD** returns
to a pre-stressor baseline window — computed by the
`psistabilizer.capture.a01_capture` analyzer on PPG data from the
MAX30102.

**Pass criteria, *all* required:**

1. **Pre-registration filed** at `experiments/Mk1/EH01_<modality>.md`
   *before* the first session. Hypothesis, the primary endpoint
   above, $n$, stopping rule, analysis code stub all locked.
2. **Sham coil built** — physically and visually indistinguishable
   from the active coil, electrically inert. Same enclosure,
   same weight, same temple-strap mount.
3. **Blinded** — operator running each session does not know
   whether the helmet contains the active or sham coil; the
   randomization log is sealed until analysis completes.
4. **Powered** — paired sessions, $n \geq 30$, $\geq 80\%$
   statistical power for the predicted effect size, $\alpha = 0.05$.
5. **The pre-registered statistical test** on the locked dataset
   shows time-to-coherence is **shorter under active** than under
   sham at $p < 0.05$ on the *pre-registered* RMSSD-based metric.
6. **Result published either direction.** A null is a Mk1 pass on
   Layer 1 (the device worked, the study ran clean) and a Mk1 fail
   on Layer 2 (the Stabilizer preset, in this implementation, did
   not stabilize anything beyond placebo). Either outcome ships.

**What does NOT count as Layer 2 pass:**

- *"I tried it on myself and felt calmer."* No sham comparison.
- *"My HRV looked better in the second half of a session."* No
  blinding, no pre-registered endpoint.
- *"We re-analyzed the data and found a different metric that did
  reach significance."* Post-hoc fishing; pre-registered metric is
  the only metric that counts.

#### Layer 3 — Framework pass/fail (is the science underneath real?)

**Mk1 deliberately does not engage any framework-level falsifier.**
Per [`falsification.md`](falsification.md), framework-level claims
(F1–F10) require population-scale studies (F1, F2, F5, F6) or
apparatus capabilities Mk1 does not yet have (F3 resonance
enhancement, F4 SAR-independence, F7 universal $\alpha$, all
$\geq$ Mk2). A Layer-2 Mk1 pass means: *this specific intervention
produced this specific physiological effect under blinded control on
this wearer cohort.* It does **not** mean "psi is real" — that claim
is structurally out of scope at Mk1.

The point of landing Mk1 honestly is to make a **Mk2 apparatus**
that *can* engage F3 and F4 defensible by inheritance.

### 4.1 The pre-registration

Before the first wear session, file a pre-registration based on the psiStabilizer template:
`external/psiStabilizer/experiments/00_preregistration_template.md`

Mk1's first study should be the simplest defensible one:

| | If G2 = audio | If G2 = photic | If G2 = coil |
|---|---|---|---|
| **Primary measure** | HRV (RMSSD) before/during/after | HRV; photic-driving in EEG if G1=b | HRV; subjective state report; **time-to-coherence under standardised stressor** (wiki-canonical, Pass 2) |
| **Stimulus** | 10 Hz isochronic tone, 30 min | 10 Hz LED flicker, 20 min, photic-screened wearer only | bifilar PCB coil, 1–8 MHz carrier modulated at 7.83 Hz, 20 min, single-blind sham/active |
| **N** | self, ≥ 10 sessions before any second wearer | self, ≥ 10 sessions | self-pilot first; **wiki Mk1 gate: $n \geq 30$ blinded RCT vs sham coil** before claiming Mk1 cleared |
| **Falsifier** | No measurable RMSSD shift outside expected diurnal variance | No photic driving response | No time-to-coherence improvement vs sham at $\alpha = 0.05$, primary endpoint pre-registered |

Commit the pre-registration to `experiments/Mk1/EH01_<modality>.md` **before** the first session.

---

## 5. Exit checklist for Mk1

Move to Mk2 when **all** of these are true.

### 5.1 Layer-1 (engineering) gates

- [ ] Canonical Mk1 frame is tagged in git and lives in `3D-Models/HelmKit/Mk1/`.
- [ ] `hardware/Mk1/bom.csv` committed and matches the device built.
- [ ] `docs/architecture.md` rev tagged at `Mk1`.
- [ ] Stim driver scope-verified: carrier in band, envelope at target Hz, $\leq 500$ µT at scalp distance.
- [ ] Stim-disabled-when-not-recording interlock verified on-bench with an oscilloscope.
- [ ] MCU-B refuses every entry on the [`wiki_synthesis.md` §2.3](wiki_synthesis.md#23-the-safety-blacklist) blacklist (firmware unit test + bench fuzz).
- [ ] Sham coil built and visually/mechanically indistinguishable from the active coil.
- [ ] At least one valid 30-minute session recorded, ingested by the psiStabilizer analyzer, with no data dropouts > 1 s.

### 5.2 Layer-2 (functional) gates

- [ ] Pre-registered Mk1 study filed at `experiments/Mk1/EH01_<modality>.md` *before* any wear session.
- [ ] Blinding protocol written, randomization log sealed.
- [ ] $n \geq 30$ paired active/sham sessions completed under the protocol.
- [ ] Pre-registered analysis run on the locked dataset — **result published either direction.**
- [ ] A written, dated decision exists for whether the Stabilizer preset, as implemented, reduces time-to-coherence below sham — and is committed to the repo regardless of outcome.

---

## 6. What Mk1 does NOT do

Tape this list to the inside of the helmet:

- No 1.245 GHz, 2.45 GHz, or 300–900 MHz RF emission. (See [safety.md](safety.md). Hypothesis preserved; physical implementation deferred.)
- No multi-modality stimulation. One modality only.
- No closed-loop control. Open-loop, fixed-schedule stim, with measurement around it.
- No claim about cognitive enhancement, protection, or "psionic" effect on a wearer other than the developer self.
- No second-wearer sessions until at least 10 self-sessions are in the books and reviewed.
