# Mk0.5 Base-Crown Architecture

- **Status**: `v0` (2026-05-20)
- **Scope**: Physical / 3D-printed architecture of the Mk0.5 frame —
  the headgear that hosts Sensor Wave 1 + Wave 2 modules without a
  stim payload. Defines the *rail-forever* mechanical contract that
  Mk1 and later marks inherit.
- **Status vs. canon**: Establishes a new mechanical contract that
  *replaces* the two-bolt M3 socket spec in
  [`docs/field-notes/volume-1/02_platform.md`](../field-notes/volume-1/02_platform.md)
  §"The hardpoint specification". The named hardpoint IDs
  (`HP-F`, `HP-FL`, `HP-FR`, `HP-TL`, `HP-TR`, `HP-EL`, `HP-ER`,
  `HP-SL`, `HP-SR`, `HP-R`) are preserved — only their physical
  implementation changes from "molded socket" to "named rail station."
- **Print target**: QIDI X-MAX3 (build volume 325 × 325 × 315 mm,
  heated chamber, hardened nozzle). Single-piece crown shell.

---

## 1. Design goal — retention against motion

Mk0.5 is the first mark with electronics on the head, and the first
mark intended to be *worn during activity* (Tranquil baseline + a
biofeedback floor that the wearer can move with). The retention
specification is therefore explicit:

> The Mk0.5 frame, fully loaded with Sensor Wave 1 + Wave 2 modules,
> stays seated on the head during:
> - Walking, head-turns, looking up / down.
> - "Michael Jackson-style dancing" — sharp head snaps, ~3 g lateral.
> - Mid-air martial-arts kicks, flips, and combative impulses —
>   ~5–8 g for ≤ 100 ms.
> Failure mode: the helm may rotate ≤ 5° before R2 + chin-strap
> arrest the motion. The helm may not separate from the head, and
> no module may separate from the rail.

That retention spec is *the* design driver. Every choice below is
downstream of it.

---

## 2. The three-ring topology

A single rigid headband fails the retention spec because heads are
not round and skin slides over bone. Mk0.5 is therefore a
three-ring assembly:

| Ring | Anatomical seat | Job | Material |
|---|---|---|---|
| **R1 — Crown** | Glabella → supraorbital ridges → squamous temporal (sits just above the brow) | Primary signal ring. Carries the full Picatinny rail and every hardpoint ID. Load-bearing. | PETG, 3 mm wall, gyroid 40 % infill |
| **R2 — Occipital cradle** | Inion + occipital protuberance + mastoid tips | Anti-pitch + anti-roll lock. Height-adjustable on a vertical rail off the back of R1. Carries **no** hardpoints. | PETG, 3 mm wall, gyroid 30 % infill |
| **R3 — Chin / sub-occipital strap** | Mandibular angle → behind ear → under occiput | Pulls R1 and R2 together via a Y-yoke. Not printed; off-the-shelf nylon webbing + cam buckle. | 25 mm nylon webbing, side-release cam buckle |

The three rings form a tetrahedral lock: any escape direction (slide
fore, slide aft, lift, yaw) is constrained by at least two rings
under tension. This is the same retention topology motorcycle and
combat helmets converged on independently — it is load-path
geometry, not aesthetic.

**Critical invariant:** only R1 is structural for sensor/module
geometry. R2 and R3 carry no hardpoints. This decouples retention
fit (which is wearer-specific) from payload mechanical contract
(which is frozen platform canon). R2 can be re-tuned for head size
without re-validating any module's mechanical contract.

### 2.1 R1 dimensions (reference adult head, 58 cm circumference)

| Dimension | Value | Notes |
|---|---|---|
| Inner forehead radius | 95 mm | Sized for 58 cm head; epoxy-pad takes up the per-wearer delta |
| Shell wall thickness | 3.0 mm | PETG, gyroid 40 % infill |
| Rail outer radius | 102 mm | 7 mm rail height above shell |
| Vertical band height | 35 mm | Brow to top-of-forehead |
| Rail axial position | Centered on the band's vertical midline | Modules sit at brow height ± rail-station drop |
| Crown arc | 220° (forward 220° of the head) | Front + both temples; back is open for R2 cradle to dock |

### 2.2 R2 dimensions

| Dimension | Value | Notes |
|---|---|---|
| Cradle width | 110 mm | Spans between mastoid tips |
| Cradle height | 60 mm | Inion to lower occiput |
| Vertical rail | 40 mm of M-LOK-style slot on R1's rear face | Sliding height-adjustable, ~30 mm of travel |
| Lock | Single M4 thumbscrew + nylock | One-handed adjust, retains against vibration |

### 2.3 R3 strap geometry

The chin-strap is a Y-yoke, not a single under-chin strap:

```
       R1 (crown)
        |  |
        |  |   ← two posts per side, printed integral to R1
        |  |     load-rated ~150 N pull each
       /    \
      /      \
     /        \  ← each leg of the Y goes from a crown post,
    /          \    behind the corresponding ear,
   /            \   joining at the mandibular angle below the ear
  *              *  ← yoke junction (each side)
   \            /
    \          /
     \        /
      \      /
       \    /
        \  /
         \/
         []   ← cam buckle under the chin
```

The Y splits the load so the chin pad stays gentle while the
behind-the-ear leg does the real anti-lift work. This is the same
scheme bicycle helmets use, and it is why bike helmets do not fly
off in a crash. A straight under-chin strap *fails* the kick test —
do not substitute one.

**Strap anchor posts** are printed integral to R1, two per side,
each rated ≥ 150 N pull, both mechanically tied to the rail
backbone so payload mass on the rail cannot tear free of the strap.

---

## 3. The rail — MIL-STD-1913 Picatinny

The base-crown's outer surface, around the 220° forward arc, is a
**continuous MIL-STD-1913 Picatinny rail** printed integral to R1.

### 3.1 Why Picatinny

- 60-year-old open mil-spec; full dimensional documentation is public.
- Massive existing accessory ecosystem (lights, action cams, IMU
  mounts, even neuro-EEG dev-board adapters) inherit for free.
- 5.0 mm tooth pitch is FDM-printable in PETG at 0.2 mm layer height,
  especially with the X-MAX3 heated chamber holding the part stable.
- Wider profile than M-LOK; the extra teeth do real work catching
  shear from a lateral impact.

### 3.2 Rail cross-section

Standard MIL-STD-1913 dimensions, no modification:

| Dimension | Value |
|---|---|
| Top width | 10.2 mm |
| Bottom width | 19.0 mm |
| Tooth pitch | 5.0 mm |
| Slot width (between teeth) | 5.55 mm |
| Slot depth | 3.4 mm |
| Recoil-shoulder angle | 45° |

### 3.3 Rail arc and "stations"

The rail runs continuously around the forward 220° of the crown.
A **station** is a named angular position along the rail. The ten
canonical Mk1 hardpoint IDs map to stations:

| ID | Angle from forward centerline | Typical occupant |
|---|---|---|
| `HP-F`  | 0° (front-center) | HUD optic, indicator LED, forward sensor |
| `HP-FL` | −30° L | Camera, ambient EM antenna, photic LED bar |
| `HP-FR` | +30° R | Camera, ambient EM antenna, photic LED bar |
| `HP-TL` | −90° L (left temple) | PPG (Wave 1), magnetometer, EEG electrode |
| `HP-TR` | +90° R (right temple) | PPG (Wave 1), magnetometer, EEG electrode |
| `HP-EL` | −105° L (ear-shield) | Bone-conduction transducer, in-ear audio |
| `HP-ER` | +105° R (ear-shield) | Bone-conduction transducer, in-ear audio |
| `HP-SL` | −115° L (sidehelm) | Battery bay |
| `HP-SR` | +115° R (sidehelm) | Comms / Compute |
| `HP-R`  | (R2 cradle, not on R1 rail) | µSD / IO door |

Station angles are **nominal, not enforced**. A module dovetail can
sit anywhere on the rail — the canonical IDs are simply the
positions that doc, BOM, schema, and protocol stamping default to.
This is the rail-forever design: angles are discoverable per wearer,
and `HP-TL` for a long-temple wearer might sit at −85° rather than
−90°. The bus contract (the module's USB-C cable + I²C identity)
binds to the *name* (`HP-TL`), not the angle.

### 3.4 What replaces the old M3 socket spec

Compared to the original 02_platform.md contract:

| Aspect | Old (Mk1 plan, pre-2026-05-20) | New (rail-forever, Mk0.5 onward) |
|---|---|---|
| Mount geometry | 2-bolt M3 pattern at 20 mm centers | MIL-STD-1913 dovetail |
| Captive feature | Captive-nut pocket on frame | TPU secondary detent leaf on pod |
| Polarity | Polarity rib prevents 180° flip | Dovetail asymmetry + cable raceway entry direction |
| Position | Frozen at print time, ten molded sockets | Continuous rail, ten *named* stations (re-positionable) |
| Cable | 4 mm × 8 mm slot per hardpoint | Continuous raceway behind rail; USB-C exits laterally |
| Tolerance | ±0.2 mm at print scale | ±0.05 mm on tooth pitch, ±0.2 mm on top width |

---

## 4. The pod — module mounting contract

Every Mk0.5 sensor module is built on a common pod chassis. A pod is:

1. A printed PETG body sized to its sensor (footprint per module type).
2. With a **MIL-STD-1913 dovetail** on its underside, printed integral.
3. A **TPU 95A secondary-detent leaf** screwed to the underside,
   printed separately so it can be replaced without reprinting the
   pod.
4. A **USB-C-Female socket** at one end, oriented so the cable exits
   into the crown's printed raceway (not into open air).

### 4.1 The two-step lock

The retention spec demands that no single impact vector can release
a pod. The lock geometry is therefore:

1. **Primary engagement** — dovetail mates with the rail, the pod is
   shoved fore-aft to seat. This alone resists any normal-direction
   lift force.
2. **Secondary detent** — the TPU leaf on the pod's underside snaps
   into one of the rail's transverse grooves. To remove, the
   operator must lift the leaf with a fingernail *and* slide the
   pod. No single-axis impulse can do both at once.

This is the same logic as a ski binding's two-axis release: a
single-action lock fails the kick test because anything that
delivers a directed impulse can also deliver an unlock impulse.

**Material choice for the detent leaf is non-negotiable: TPU 95A.**
PLA leaves fatigue-crack within ~50 release cycles; TPU survives
thousands.

### 4.2 Pod footprint envelope

A pod cannot exceed the footprint envelope for its station type:

| Station type | Length along rail (mm) | Width across rail (mm) | Height above rail (mm) |
|---|---|---|---|
| `HP-F`, `HP-F*` (forehelm) | ≤ 35 | ≤ 35 | ≤ 30 |
| `HP-T*` (temple) | ≤ 45 | ≤ 30 | ≤ 25 |
| `HP-E*` (ear) | ≤ 50 | ≤ 40 | ≤ 35 |
| `HP-S*` (sidehelm) | ≤ 70 | ≤ 50 | ≤ 40 |

Exceeding the envelope risks rail-edge interference with an adjacent
pod. The envelope is enforced at module-spec review, not at
firmware time.

---

## 5. Printable parts list

Six unique printed parts. All FDM-friendly on the X-MAX3; no parts
require dissolvable supports.

| Part | Material | Qty | Print orient | Approx. time | Notes |
|---|---|---|---|---|---|
| `crown_shell_R1.stl` | PETG | 1 | Rail teeth up, brow band flat on bed | ~6 h | Single-piece; rail is *part of* the shell, not bolted on. Fits in X-MAX3 build volume with ~115 mm margin on each side. |
| `occipital_cradle_R2.stl` | PETG | 1 | Open side up | ~3 h | Slides on the vertical rail off the back of R1 |
| `pod_blank.stl` | PETG | n | Dovetail down | ~1 h each | Reference module; every sensor pod (MAX30102, MLX90614, GSR, vbat) derives from this |
| `pod_detent_leaf.stl` | TPU 95A | n | Flat | ~20 min each | The two-step lock element. Replaceable. |
| `strap_post_reinforcement.stl` (optional) | PETG | 4 | Flat | ~30 min each | Glue-on reinforcement if dev-print shows the integral posts flex under > 100 N pull |
| `rail_dust_cap.stl` (optional) | TPU 95A | n | Flat | ~10 min each | Cosmetic; covers unused rail teeth |

Padding (epoxy-glued to the inner faces of R1 and R2) is single-use
EVA foam, not printed.

**Total Mk0.5 base-crown print time:** ~10 h for the structural
parts (crown shell + cradle); then ~1.3 h per sensor pod. One
overnight job for the full Wave 1 + Wave 2 build (≈ 5 pods).

---

## 6. Bill of materials (non-printed)

Sourced where reasonable from McMaster-Carr; substitutes acceptable
if dimensional spec matches.

| Item | Qty | Spec | Approx. cost |
|---|---|---|---|
| Nylon webbing | 1.5 m | 25 mm wide, ~3000 N tensile | $4 |
| Side-release cam buckle | 1 | 25 mm fit; **not** magnetic | $3 |
| Y-yoke triangle ring | 2 | 25 mm, stainless | $2 |
| M4 × 16 mm thumbscrew | 1 | Stainless | $2 (R2 lock) |
| M4 nylock nut | 1 | Stainless | $0.50 |
| M3 × 8 mm bolt | 4 | Stainless | $1 (detent leaf retention, 1 per pod) |
| M3 heat-set insert | 4 | Brass, 5 mm OD | $2 (per pod) |
| EVA foam pad | 1 | 5 mm thick, 30 cm × 10 cm sheet | $4 |
| Two-part epoxy | 1 | ~30 min cure | $6 |

Estimated total non-printed BOM per crown: **~$25.**

---

## 7. Migration from Mk0.0 iter9

The iter9 frame
([`3D-Models/HelmKit/helmkit_prototype_v2_mk0_type-b_iter9.stl`](../../3D-Models/HelmKit/helmkit_prototype_v2_mk0_type-b_iter9.stl))
remains the **Mk0.0 reference**: it demonstrates the "fits a head
for ≥ 30 min" gate per
[`docs/mk_ladder.md`](../mk_ladder.md) §3.

Mk0.5 introduces R1 + R2 + R3 as the *replacement* operating frame.
iter9 is not retired — it remains the form rung's reference
artefact for any reproduction or audit comparison — but Mk0.5 work
proceeds on the new three-ring topology.

The mk_ladder.md gating is unchanged: Mk0.0 → Mk0.5 was already
gated on "frame fits a head ≥ 30 min" (✅, iter9 frozen). The new
crown inherits that property by construction (R1 inner geometry is
within 1 mm of iter9) plus extends the wear duration by adding the
chin-strap-Y-yoke and occipital cradle.

---

## 8. Mk1 inheritance

Mk1 inherits this architecture **unchanged** as its mechanical
contract. The named hardpoint IDs in 02_platform.md persist; their
*implementation* is rail-stations rather than molded sockets.

This is the rail-forever decision (locked 2026-05-20). The
implications for Mk1 and beyond:

- Adding a new module modality at Mk2 (EEG), Mk2.5 (second stim),
  or Mk3 (dyadic) is plug-and-slide, not a shell reprint.
- The mechanical contract becomes mark-invariant: one rail, every
  pod, every mark.
- The aesthetic register is permanently instrument-utility.
  Production / consumer aesthetics, if ever pursued, are Mk3
  product-roadmap territory and may diverge.

The corresponding canon update lives in
[`docs/field-notes/volume-1/02_platform.md`](../field-notes/volume-1/02_platform.md)
§"The hardpoint specification" (rewritten 2026-05-20 to reflect
rail-forever).

---

## 9. Open items

1. **Polar mating to compute node.** R1 holds sensors; the compute
   node (ESP32-S3 Heltec V3) lives at `HP-R` on R2's outer face.
   Cable run from R1's rail raceway down to R2 needs a service loop
   so R2 can be slid for height-adjust without yanking on USB-C
   ends. Service-loop length spec: 30 mm minimum slack at the
   tightest R2 position.
2. **Padding spec.** EVA foam is the assumed material; if sweat
   testing shows EVA goes soft / smelly inside two weeks, switch
   to closed-cell silicone foam (more expensive, washable in
   place). Decision deferred to first Bridge A bench session.
3. **Print-in-place vs. bonded posts.** The four chin-strap posts
   are printed integral to R1. If the first dev-print shows the
   posts flex under > 100 N pull, optional
   `strap_post_reinforcement.stl` glue-on collars are available.
   Decide after pull test.
4. **HP-R location.** Canonically "rearhelm"; in this architecture
   it lives on R2's outer face. The cable run is longer than the
   original canon assumed. If signal integrity on the USB-C lane
   from temple-PPG to rear-compute degrades at the longer run,
   relocate compute to a sidehelm station (`HP-SL` or `HP-SR`) —
   the rail makes this a one-day change.
5. **R2 rail interface.** R2 docks onto R1 via a vertical M-LOK-
   style slot. The slot profile is *not* MIL-STD-1913 Picatinny
   (different aspect ratio); it is a separate, simpler dovetail
   chosen for height-slide rather than fore-aft slide. Spec frozen
   as part of this document.

---

## 10. Acceptance gates

The Mk0.5 base-crown is considered "shipped" when:

| Gate | Test | Status |
|---|---|---|
| G-Print | All six STLs print cleanly on X-MAX3 with PETG and TPU 95A | ⏳ |
| G-Fit | Mk0.5 frame fits the developer's head for ≥ 30 min without fatigue (matches Mk0.0 gate) | ⏳ |
| G-Pod | A pod with two-step lock survives 1000 insertion/release cycles | ⏳ |
| G-Pull | Chin-strap posts survive 150 N pull-test without permanent deflection | ⏳ |
| G-Motion | Loaded crown stays seated through 5 min walking + 1 min head-snap dance + 10 controlled kicks | ⏳ |
| G-Cable | Service-loop survives 100 R2 height-adjust cycles without USB-C connector damage | ⏳ |

All gates pass → Mk0.5 is the new operating frame, replacing iter9
as the active form artefact.

---

## References

- [`mk0.5_prior_art_index.md`](mk0.5_prior_art_index.md) — third-party
  open-source 3D models on the external library that may inform
  Mk0.5 / Mk1+ work, license-tiered for incorporation safety.
- [`docs/field-notes/volume-1/02_platform.md`](../field-notes/volume-1/02_platform.md)
  §"The hardpoint specification" — canonical hardpoint IDs and L2 bus.
- [`docs/mk_ladder.md`](../mk_ladder.md) §3 — Mk0.0 → Mk0.5 gating.
- [`docs/mechanical/ppg_mounting_notes.md`](ppg_mounting_notes.md) — PPG
  skin-coupling notes that constrain pod design at `HP-T*`.
- [`3D-Models/HelmKit/helmkit_prototype_v2_mk0_type-b_iter9.stl`](../../3D-Models/HelmKit/helmkit_prototype_v2_mk0_type-b_iter9.stl)
  — Mk0.0 reference frame (frozen).
- MIL-STD-1913, *Dimensioning of Accessory Mounting Rail for Small Arms
  Weapons*, public mil-spec.
