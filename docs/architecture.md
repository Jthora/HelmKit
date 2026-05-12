# HelmKit Architecture

The HelmKit is a **platform**, not a device. Its job is to give Psi-Tech modules a reliable place to live, with reliable power, data, and head-fit. This document specifies the platform contract.

## 1. The four-layer model

| Layer | What it is | Where it lives |
|-------|------------|----------------|
| **L0 — Fit** | Headband + frame ring; sets where the device sits on the head | `3D-Models/HelmKit/` headRing + Mk1 frame parts |
| **L1 — Structure** | Forehelm, sidehelm, rearhelm, temple booms; the load-bearing skeleton | `3D-Models/HelmKit/` Mk1 modular parts |
| **L2 — Bus** | Power rails + data bus + cable raceway; carries V, GND, I²C, SPI, audio diff pair | Printed-in channels; documented connector pinout |
| **L3 — Modules** | Sensing, stimulation, optics, comms — the actual Psi-Tech | Mount via the L1 hardpoints, plug into L2 |

A module is replaceable if and only if it conforms to the L1 hardpoint and the L2 bus contract.

---

## 2. Hardpoint spec (v1, frozen at Mk1)

Every module mounts at a **hardpoint**: a printed feature on the frame with a fixed mechanical and electrical contract.

### 2.1 Hardpoint locations (Mk1 frame)
| ID | Location | Typical occupant | Notes |
|----|----------|------------------|-------|
| `HP-F` | Forehelm, centerline | HUD optic mount, indicator LEDs, forward-facing sensor | Closest to gaze axis |
| `HP-FL`, `HP-FR` | Forehelm, left/right of centerline | Camera, ambient EM antenna, photic LED bar | Symmetric pair |
| `HP-TL`, `HP-TR` | Temple boom, left/right | EEG electrode, magnetometer boom, coil driver, PPG | Closest to skin contact line; most signal-relevant |
| `HP-EL`, `HP-ER` | Ear-shield, left/right | Bone-conduction transducer, in-ear audio, ear-canal sensor | Existing `earShield-v3` accessory family |
| `HP-SL`, `HP-SR` | Sidehelm, left/right | Battery bay (one side), comms radio bay (other side) | Larger volume than temple |
| `HP-R` | Rearhelm | Compute node, primary battery, µSD/IO door | Largest volume; furthest from face |

### 2.2 Mechanical contract
- **Bolt pattern:** 2-bolt M3, 20 mm centers, captive-nut pocket on the frame side. Tolerance ±0.2 mm at print scale.
- **Keying:** every module has a polarity rib so it cannot be installed rotated 180°.
- **Module footprint envelope:** documented per hardpoint; modules that exceed envelope are not Mk1-compatible.
- **Cable pass-through:** every hardpoint has a 4 mm × 8 mm slot to the L2 raceway.

### 2.3 Electrical contract (L2 bus)
- **Power:** 3.3 V (≤ 500 mA per hardpoint) + 5 V (≤ 1 A per hardpoint) + GND. Per-hardpoint poly-fuse.
- **Data:** I²C (SDA / SCL) + SPI (MOSI / MISO / SCK + per-hardpoint CS) on the bus. Modules use one, declare which.
- **Audio:** dedicated diff pair between `HP-EL`, `HP-ER`, and the compute node — not on the I²C/SPI bus.
- **Stim:** dedicated isolated pair from compute → stim driver → temple hardpoint. Hardware interlock between stim-enable and recording-active. **No stim without recording.**
- **Connector:** Mk1 — JST-SH 6-pin per hardpoint, color-keyed. Mk2 — promoted to a keyed harness connector.

> Stim-without-recording is forbidden in firmware and in hardware. This is the single hardest interlock in the device.

---

## 3. Module classes

Modules fall into five classes. Each class has its own design rules.

### 3.1 Sensing modules
- Must declare: channel name, sample rate, units, calibration procedure.
- Must emit data in the psiStabilizer NDJSON channel schema (`external/psiStabilizer/docs/data_schemas.md`).
- Mk1 examples: PPG (HRV), dry EEG (single channel), ambient magnetometer.

### 3.2 Stimulation modules
- Must declare: modality, dosage envelope (min/max/typical), contraindication list, interlock conditions.
- Must accept a hardware enable line and an emergency stop line. Both lines OR'd into disable.
- Mk1 examples: bone-conduction audio entrainment, photic entrainment, sub-MHz pulsed magnetic coil.
- Mk2+ examples: tACS electrode, sub-GHz RF emitter (SAR-gated).

### 3.3 Optics / HUD modules
- Mk2+ only. Mk1 reserves the `HP-F` hardpoint but does not populate it with optics.
- Must not occlude the gaze cone; off-axis combiners only.

### 3.4 Comms modules
- BLE / Wi-Fi / sub-GHz radio for telemetry off-head.
- Mk1 may use the compute node's onboard radio; Mk2+ may add dedicated comms in `HP-SL` or `HP-SR`.

### 3.5 Power / compute modules
- Live in the larger rear and side hardpoints.
- Compute reference: same family as psiStabilizer A01 (Raspberry Pi class).
- Battery reference: 1S Li-ion with protection PCB; Mk2+ moves to hot-swap pairs.

---

## 4. Coordinate system & fit

- **Origin** = midpoint between the tragi (ear-canal openings), projected to the headband plane.
- **+X** = right, **+Y** = forward, **+Z** = up (anatomical convention).
- Module placement and EEG-electrode positions reference the 10-20 system; Fp1 / Fp2 / Cz / T7 / T8 are the primary Mk1/Mk2 positions of interest, all of which are reachable from the existing frame's forehelm and temple hardpoints.

---

## 5. Relationship to the psiStabilizer submodule

The HelmKit repo **does not duplicate** anything in `external/psiStabilizer/`:

| Concern | Lives in | HelmKit role |
|---------|----------|--------------|
| Sensor data schema | psiStabilizer `docs/data_schemas.md` | Consumed as-is |
| Capture pipeline | psiStabilizer `software/src/psistabilizer/capture/` | Imported as a library |
| Analysis (HRV, anomaly) | psiStabilizer `software/src/psistabilizer/analysis/` | Imported as a library |
| Experiment pre-reg template | psiStabilizer `experiments/00_preregistration_template.md` | Copied per HelmKit study |
| BOM for the A01 sensor stack | psiStabilizer `hardware/A01/bom.csv` | Subset adopted; HelmKit BOM extends it |
| Frame geometry / hardpoint spec / module bus | **This repo** | Owned here |
| Stimulation drivers | **This repo** | Owned here (Stabilizer is measurement-first; HelmKit is the place stim hardware lives) |
| Wearer-facing safety doc | This repo, citing psiStabilizer `safety_guidelines.md` | Lifted and extended for head-mounted hardware |

---

## 6. Versioning

Every generation freezes:
1. **Frame**: one canonical `.blend` and matching `.stl` set, tagged.
2. **Hardpoint spec**: this document at that tag (`docs/architecture.md@MkN`).
3. **Bus pinout**: one canonical connector diagram per tag.
4. **BOM**: one CSV at `hardware/MkN/bom.csv`.
5. **Firmware**: one git tag, same name as the generation.

A module is "Mk1-compatible" iff it builds against the Mk1 tag's frozen spec.
