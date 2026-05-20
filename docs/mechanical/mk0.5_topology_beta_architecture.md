# Mk0.5 Topology β Architecture

- **Status**: `v0` (2026-05-20) — **PRIMARY**
- **Supersedes**: [`mk0.5_base_crown_architecture.md`](mk0.5_base_crown_architecture.md) (ring-frame variant, retained as fallback).
- **Scope**: Physical / 3D-printed architecture of the Mk0.5 frame
  with three named **psi-actuator** classes (Pylons, Defenders,
  Stabilizers) as primary payload, plus a slim sensor sub-rail for
  wearer-tunable Wave-1 sensors.
- **Print target**: QIDI X-MAX3 (325 × 325 × 315 mm, heated chamber).

---

## 1. Why β replaces the ring-frame

The original three-ring topology (R1 forehead crown / R2 occipital
cradle / R3 chin yoke) was sized for the Mk1 sensor-pod vision —
~10 generic-ish sensor pods, all small, all on a single Picatinny
rail across the brow. It does not fit the actual Mk0.5 payload:

- **Psi-Pylons** need a *hinge*, not a slide-dovetail.
- **Psi-Defenders** need precise *inward-aim* into the temple bone.
- **Psi-Stabilizers** need *tilted* mounting platforms, and the rear
  one has nowhere on R1 to attach (R1 is the forward 220°).

β replaces the ring-frame with a **frame-and-yoke** topology
borrowed from headphone ergonomics + ODST/N7/Halo helmet aesthetics:
weight rides on a top yoke over the parietal bones, and two foldable
visor-bands swing down to cover the brow and the occiput. The visor
bands *are* the Stabilizer mounting wedges — one part doing two jobs.

---

## 2. Components

| Component | Material | Wall | Job | Carries |
|---|---|---|---|---|
| **Top Yoke** | PETG | 4 mm | Headphone arch over parietal; primary weight path | Cable raceway; no payload |
| **Forward Visor-Band** | PETG | 3 mm | Folds over forehead, locks at 5 detent positions | Front Psi-Stabilizer (integral); slim Picatinny sub-rail along outer edge for tunable sensors |
| **Rear Visor-Band** | PETG | 3 mm | Folds over occiput, locks at 5 detent positions; replaces R2 | Rear Psi-Stabilizer (integral) |
| **Temple Plate L/R** | PETG | 4 mm (3 mm shell + 1 mm ribs at pivots/bolts) | Anatomical anchor at temple; visual hero feature; structural confluence | **4 independent co-located pivots**: Pylon live-hinge, Defender 2-axis gimbal, Forward Visor-Band hinge, Rear Visor-Band hinge — plus Cheek Hook integral to lower edge and 3× M3 bolt cluster to Top Yoke at upper edge |
| **Chin Yoke** | 25 mm nylon webbing + cam buckle + printed cheek hooks | — | Anti-lift retention | Hooks integral to Temple Plates |
| **Sensor Sub-Rail** | PETG, integral to Forward Visor-Band lower edge | — | Continuous Picatinny for Wave-1 sensor pods (PPG, EEG, IMU) | Generic dovetail pods (per ring-frame doc §4) |

---

## 3. Topology

```
                   ┌─── Top Yoke ───┐
                  /                  \
                 /   (over parietal,  \
                /    ear-to-ear)       \
   Forward     /                        \   Rear
   Visor-Band /                          \  Visor-Band
   (folds    /   ┌──Temple ──┐  ┌──Temple─┐  (folds
   down)    /    │   Plate   │  │  Plate  │   down)
           /     │     L     │  │    R    │
        [front]  │ • Pylon-L │  │•Pylon-R │  [back]
                 │ • Defndr-L│  │•Defndr-R│
                 │ • side-jt │  │•side-jt │
                 └───────────┘  └─────────┘
                       │              │
                       └─ chin yoke ──┘
```

The temple plates are the **structural confluence** — yoke bolt
cluster, both visor-band hinges, Pylon hinge, Defender gimbal, and
chin-strap cheek hook all anchor to the same plate. **Four**
separate small pivots (not one shared pin) keep the failure modes
uncoupled; see §12 for the full joint contracts and §2 table for
the rib spec that handles the resulting stress concentration.

---

## 4. Psi-actuator mounts (bespoke, frozen at print time)

### 4.1 Psi-Pylons (×2, fed as differential dipole)

| Parameter | Value |
|---|---|
| Antenna length | **6 cm** per leg (λ/2 at 2.45 GHz) |
| Cross-section | Long flat triangle, ~6 mm wide at base, ~2 mm at tip, 4 mm thick |
| Hinge axis | Anatomical temple, integral to Temple Plate, axis horizontal fore-aft |
| Hinge type | **Live-hinge with retention spring** (TPU 95A flexure) |
| Detent positions | 3: straight-up / 45°-back / fold-flat |
| Fail mode under lateral load | Folds flat against side of helm at ~30 N; re-deploys after impact |
| Mass per Pylon | Target ≤ 25 g loaded (housing + element + RF feed) |
| **Feed topology (decided 2026-05-20)** | **Differential true dipole** — RF source feeds a balun in the Top Yoke; one balanced leg runs down the inside of each Top-Yoke arm via the internal raceway, exits at the Temple Plate, crosses the Pylon hinge as RG-178 coax with 40 mm service loop, and drives the Pylon root. Both Pylons together form a single λ/2 dipole spanning the head crown. |
| Balun spec | 1:1 current balun, 2.45 GHz, ≤ 25 × 15 × 10 mm — mounts inside Top Yoke cavity at the arch apex (between the two arm raceways) |
| Transmission line | Coax inside Top Yoke from feed source up to balun, then balanced parallel pair (3 mm centre-to-centre, controlled-impedance printed channel) from balun down each arm |

### 4.2 Psi-Defenders (×2, paired caduceus shield)

> **Concept (decided 2026-05-20):** the two Defenders are **not** independent directional emitters — they operate as a **bound pair** generating a scalar standing-wave field shell around the head. Mechanism per wiki canon (`/memories/repo/helmkit_anchors.md` §"Coil topology choices"): paired caduceus coils with opposite chirality (m₁ = −m₂) cancel the far-field radiation while leaving a longitudinal/scalar local component that closes into a head-encompassing standing wave geometry. Operating role is **psionic shield**: the standing-wave shell is intended to mitigate, absorb, or dissolve incoming spin-wave / magnon / psion-coupled fluctuations per the ψ-field framework in `helmkit_anchors.md` §"ψ field Lagrangian". Engineering discipline (SAR, F-criteria, dual-MCU safety) stays fully ON per the project epistemic stance.

| Parameter | Value |
|---|---|
| Element type | **Bifilar caduceus coil** (opposite-chirality helices, L coil and R coil are mirror enantiomers of each other) |
| Coil diameter | 12.24 mm (matches λ/10 at 2.45 GHz; deeply reactive near-field — r ≪ 0.62·√(D³/λ)) |
| Operating frequency | 2.45 GHz ISM (primary); reactive near-field mode only |
| Drive | **Paired phase-locked drive** — L and R coils driven coherently (phase relationship TBD by RF integration: anti-phase for far-field cancellation per caduceus topology is the canonical baseline) |
| Function | Scalar-field standing-wave shell around the head; psionic shield generator |
| Far-field radiation | **Suppressed by caduceus m₁=−m₂ cancellation + paired-coherent drive** — this is the designed property, not a side-effect |
| Housing aim direction | Coil axis on the ear-to-ear T-T line (both coils share the same physical axis through the head, which is the shell's coherence axis) |
| Aim adjustment | ±15° pitch, ±15° yaw via 2-axis pin pivot — fine-tunes the coil-axis alignment to individual skull shape so the L and R coils are actually colinear through the head's T-T line |
| Aim lock | M2 × 4 mm set-screw + M2 heat-set insert (see §12 `IFACE_TEMPLE_DEFENDER`) |
| Cradle envelope | ~25 × 25 × 20 mm housing around the 12.24 mm coil + drive electronics |
| SAR metric | Near-field SAR (not far-field EIRP) is the relevant safety measure; FDTD must model the **paired** drive geometry, not a single coil. Design target ≤ 0.7 W/kg per `helmkit_anchors.md`. See §11 G-SAR. |

*Replaces and supersedes the 2026-05-20 "engineering caveat" about the 12.24 mm dish — the spec was right (12.24 mm at 2.45 GHz), the word "dish" was wrong. It's a caduceus coil, not an aperture.*

### 4.3 Psi-Stabilizers (×2 standalone Stabilizers, 4 bifilar spirals total)

**Architecture (decided 2026-05-20):** two **standalone Psi-Stabilizer-Mk1** units, one per side. Each side runs its own nRF52840 + SI5351 + Class-D driver per `/memories/repo/helmkit_anchors.md` (Psi Stabilizer Mk1 BOM, ≤$250 each), driving the Front + Rear spiral pair on its own side. This matches the canonical standalone Stabilizer BOM verbatim, supports L/R asymmetric HRV biofeedback experiments, and either side is a drop-in test article (one Stabilizer can be bench-validated without the rest of the helm). MCU lives in the same sidehelm pod as compute (HP-SR) or separately at HP-SL — TBD by power+signal budget pass.

| Parameter | Value |
|---|---|
| Panel dimensions | ~70 × 40 × 6 mm (houses 2 bifilar spirals side-by-side, ~30 × 30 mm PCBs each) |
| Mount | Integral to Forward and Rear Visor-Bands |
| Per side architecture | 1× nRF52840 + 1× SI5351 + Class-D drives that side's Front + Rear spiral pair (2 spirals per MCU) |
| Aim direction | Inward toward the crown apex (front panel pitched down-and-back, rear panel pitched down-and-forward) |
| Aim adjustment | Discrete: 5 detent positions on the visor-band hinge — 0° (wear-low) / 30° / 45° / 60° wear variants / 90° stow (per §12 `IFACE_TEMPLE_FWDBAND`) |
| Per panel: bifilar spirals | 2 × ~30 × 30 mm bifilar PCB coils, left + right of head midline |
| Total spirals on helm | 4 (front-L, front-R, back-L, back-R) |
| Total MCUs for Stabilizer function | **2** (one per side) |

---

## 5. Mechanical contracts (carried forward unchanged from ring-frame doc)

The following stay valid and are **not** restated here — see
[`mk0.5_base_crown_architecture.md`](mk0.5_base_crown_architecture.md):

- §3 **MIL-STD-1913 Picatinny rail** spec (used here on the Forward
  Visor-Band sub-rail).
- §4 **Pod chassis + two-step lock** (used here for the Wave-1
  sensor pods on the sub-rail).
- §6 **Non-printed BOM** (webbing, buckle, screws, foam — applies
  here too).

**Hardpoint ID mapping** (preserved verbatim from ring-frame doc):
- `HP-F` → Forward Visor-Band, front-center → front Stabilizer
- `HP-FL`, `HP-FR` → Forward Visor-Band sub-rail → small sensor pods
- `HP-TL`, `HP-TR` → Temple Plate L/R → Defender cradles
- `HP-EL`, `HP-ER` → Temple Plate L/R, behind-Defender → Pylon hinges
- `HP-SL`, `HP-SR` → Temple Plate L/R, lower → battery/comms pods
- `HP-R` → Rear Visor-Band, back-center → rear Stabilizer

### 5.1 Carry-forward gaps under β (added 2026-05-20)

Three items from the ring-frame BOM/spec that the original §5
"carries forward unchanged" claim glossed:

- **EVA foam padding** (ring-frame doc §6, "5 mm EVA pad, epoxy-glued
to inner R1/R2") **does** carry forward, but the surfaces change:
now under the Top Yoke (parietal contact), Forward Visor-Band
(brow contact), Rear Visor-Band (occipital contact), and Temple
Plate inner face (squamous temporal contact). Per-surface area
estimates are in §10 BOM delta.
- **M3 heat-set inserts × 6** are **required** at the Top Yoke arch
ends (3 per side) for the Temple-Plate bolt joint. PETG threads
directly will strip under the 150 N anti-lift load path (see §12
`IFACE_YOKE_TEMPLE`). Not optional.
- **R2 M4 thumbscrew + nylock** are **removed** — no R2 under β.
BOM delta in §10 reflects this.

---

## 6. Cable routing (hybrid, decided 2026-05-20)

- **Internal** in Top Yoke and the Visor-Bands: USB-C and signal
  trunks run through printed channels in the wall thickness, covered
  by snap-on strip-caps.
- **Visible jumpers** between rings and to Pylon hinges: short flex
  cables (silicone-jacket 28 AWG) acknowledged as a deliberate
  cyberpunk-aesthetic feature, not hidden.

Hinge crossings (Forward/Rear Visor-Band fold joints, Pylon
hinges) use a service loop sized for the worst-case fold angle.

---

## 7. Aesthetics (decided 2026-05-20)

- **Look**: Sci-fi tactical (Halo / Mass Effect / ODST). Hardware is
  visible but reads as intentional, not industrial.
- **Two-tone**: Frame parts (Top Yoke, Visor-Bands, Temple Plates,
  Chin cheek hooks) = **matte BLACK** PETG. Accent parts (Stabilizer
  panels, Defender dish housings, Pylon shells) = **matte WHITE**
  PETG. Stealth-operator silhouette.
- **Fold-positions**: 5-detent visor-band hinge (up / 60° / 45° /
  30° / down) gives repeatable session-to-session Stabilizer aim.

---

## 8. Retention spec (extended from ring-frame doc §1)

Original retention spec preserved (MJ dancing, ≤ 8 g flip kick,
≤ 5° rotation before chin yoke arrests). **Added** under topology β:

> **Ground-roll survival.** During a forward, side, or back ground
> roll (head contacting ground at ≤ 3 m/s, no shoulder shock-load):
> - The helm must stay on the head (no separation).
> - Pylons must fold flat at ≤ 30 N lateral load and re-deploy after.
> - Defender dishes must not crack (cradle must absorb impact).
> - Stabilizer panels must not separate from the visor-bands.
> - Visor-band hinge detents may slip (acceptable; user re-locks).

Wing-chun / capoeira / spinning-kick / running-roll-jump combat is
within scope; rigid-impact (e.g. landing on the helm at full body
weight from height) is **not** within scope and will be addressed
in a future Mk1 hardshell variant.

---

## 9. Print plan (revised parts list)

Eight unique printed parts. All FDM-friendly on the X-MAX3.

| Part | Material | Qty | Print orient | Approx. time |
|---|---|---|---|---|
| `top_yoke.stl` | PETG (black) | 1 | Arch open-side up, supports under arch | ~4 h |
| `forward_visor_band.stl` | PETG (black) | 1 | Curved face flat on bed | ~3 h |
| `rear_visor_band.stl` | PETG (black) | 1 | Curved face flat on bed | ~2.5 h |
| `temple_plate_L.stl` / `temple_plate_R.stl` | PETG (black) | 2 | Outer face up | ~1 h each |
| `psi_pylon.stl` | PETG (white) shell + TPU 95A live-hinge | 2 | Hinge flat | ~45 min each |
| `psi_defender_cradle.stl` | PETG (white) | 2 | Open face up | ~30 min each |
| `psi_stabilizer_panel.stl` | PETG (white) | 4 (2 front, 2 rear) | Flat | ~30 min each |
| `pod_blank.stl` (sensor pods, sub-rail) | PETG (black) | n | Dovetail down | ~1 h each |

**Total Mk0.5 β-frame print time:** ~13 h structural + ~3 h
psi-actuators + per-sensor pods. Two overnight jobs.

---

## 10. BOM delta under β (added 2026-05-20)

Delta against ring-frame `mk0.5_base_crown_architecture.md` §6. Add unless flagged "removes".

| Item | Qty | Spec | Why | Approx. cost |
|---|---|---|---|---|
| M3 × 8 mm bolt, stainless | 6 | DIN 912 | Temple Plate → Top Yoke joint (3 per side) | $2 |
| M3 heat-set insert, brass, 5 mm OD | 6 | Standard | In Top Yoke arch ends; PETG threads strip under 150 N | $3 |
| M2 × 4 mm set-screw, stainless | 2 | Cup-point | Defender aim-lock (1 per Defender) | $1 |
| M2 heat-set insert, brass, 3 mm OD | 2 | Standard | In Defender cradle for set-screw thread retention | $1 |
| M2 × 6 mm bolt, stainless | 4 | Pan-head | Pylon live-hinge foot retention (2 per Pylon) | $1 |
| Steel music-wire pin, 3 mm × 25 mm | 2 | Cut from 3 mm rod | Visor-band hinges (1 per band, spans L↔R via temple plates) | $1 |
| Steel music-wire pin, 2 mm × 12 mm | 4 | Cut from 2 mm rod | Defender gimbal (2 per Defender: pitch + yaw) | $1 |
| TPU 95A detent-leaf, printed | 4 | `visor_detent_leaf.stl`, replaceable | 2 per visor-band hinge; engages 5 detent notches in temple plate | print only |
| EVA foam pad, 5 mm, ~250 cm² | 1 | Closed-cell, adhesive-back | Top Yoke parietal (~80 cm²) + Fwd band brow (~60 cm²) + Rear band occipital (~50 cm²) + 2× Temple Plate inner (~30 cm² each) | $5 |
| Shielded micro-coax, RG-178 or IPEX | ~1 m | 50 Ω | Pylon RF feed across live-hinge with service loop | $4 |
| ~~M4 × 16 mm thumbscrew~~ | ~~1~~ | **REMOVED** — no R2 under β | | −$2 |
| ~~M4 nylock~~ | ~~1~~ | **REMOVED** — no R2 under β | | −$0.50 |

**BOM delta under β: ~+$17** on top of ring-frame ~$25 base → **~$42 total non-printed BOM per Mk0.5 β helm.**

---

## 11. Acceptance gates (delta under β)

Carries forward unchanged from ring-frame doc §10: **G-Print**, **G-Fit**, **G-Pod**, **G-Pull**, **G-Motion**, **G-Cable**. β adds:

| Gate | Test | Threshold |
|---|---|---|
| **G-Fold** | Both visor-band hinges fold-cycle test | 1000 cycles, detent aim drift ≤ ±2° from initial calibration |
| **G-Pylon** | Pylon live-hinge fold-cycle + force test | 5000 fold cycles in TPU 95A; fold threshold 25–35 N lateral; redeploys from fold-flat ≤ 1 s under spring return |
| **G-Yoke** | Top Yoke + temple-plate bolt joint static load | 600 N applied at Cheek Hooks (4× safety factor on 150 N strap), no permanent deformation, no thread pull-out from heat-set inserts |
| **G-Defender-Aim** | Defender aim repeatability over 50 lock/unlock cycles | ±2° in both pitch and yaw |
| **G-SAR** | Bench head-phantom measurement, all 3 emitter classes simultaneously active | ≤ 2.0 W/kg over 10 g head tissue (ICNIRP/IEEE ceiling); design target ≤ 0.7 W/kg per `helmkit_anchors.md` |

All 11 gates pass → Mk0.5 β is the new operating frame.

---

## 12. Interface contracts (the eight joints) — FROZEN

This section is the **single source of truth** for joint dimensions. Generators in `tools/blender/build_*.py` must import these constants from `tools/blender/interfaces.py` (Phase 6 deliverable). Any change here requires regenerating every affected part.

All dimensions in mm. Datum convention: each Temple Plate has its own local frame with origin at the plate centroid on the outer face; **+X = forward** (toward brow), **+Y = up** (toward crown), **+Z = outward** (away from head).

### IFACE_YOKE_TEMPLE (Top Yoke arch end ↔ Temple Plate upper edge)

| Param | Value |
|---|---|
| Bolt count | 3× M3 |
| Pattern | Equilateral triangle, 12 mm side |
| Triangle centroid on plate | (0, +18, 0) — 18 mm above plate datum |
| Bolt-hole Ø in temple plate | 3.4 mm (clearance) |
| Heat-set insert in yoke arch end | M3 × 5 mm OD brass |
| Mate face normal | +Y on temple plate ↔ −Y on yoke end |
| Boss thickness at insert | 6 mm minimum (PETG) around the insert OD |
| Load case | 150 N tension (anti-lift), 4× SF → design to 600 N → ~200 N per bolt = OK at M3 |

### IFACE_TEMPLE_FWDBAND (Temple Plate L/R ↔ Forward Visor-Band)

| Param | Value |
|---|---|
| Hinge pin | Steel music wire 3 mm × 25 mm; spans L↔R through the Forward Visor-Band tabs, passing through both Temple Plates |
| Hinge axis | Horizontal, ear-to-ear; on temple plate at local (+8, −6, 0) — 8 mm forward, 6 mm below datum |
| Detent count | **5 positions** |
| Detent angles (band rotation from horizontal-down) | **0° = wear-low (band hanging fully down, stabilizer aimed +0° from horizontal)** / 30° / 45° / 60° / **90° = stow (band swung up, off forehead, parked against yoke)** |
| Detent mechanism | TPU 95A click-leaf (`visor_detent_leaf.stl`) screwed to inboard face of band tab via 1× M3, engages 5 notches in temple plate — same two-step-lock pattern as sensor-pod detent leaf |
| Aim use | Wear positions = 0°/30°/45°/60° (Stabilizer aim variants); 90° = stow only |
| Service loop for sub-rail cable across hinge | 25 mm slack at hinge axis (worst-case 90° fold) |

### IFACE_TEMPLE_REARBAND (Temple Plate L/R ↔ Rear Visor-Band)

| Param | Value |
|---|---|
| Hinge pin | Steel music wire 3 mm × 25 mm; spans L↔R through Rear Visor-Band tabs |
| Hinge axis | Horizontal, ear-to-ear; on temple plate at local (−8, −6, 0) — 8 mm aft, 6 mm below datum |
| Detent count | 5 positions (mirror of FwdBand) |
| Detent angles | 0° wear-low / 30° / 45° / 60° / 90° stow |
| Detent mechanism | Same TPU click-leaf as FwdBand |
| Service loop | 25 mm at hinge axis |

### IFACE_TEMPLE_PYLON (Temple Plate L/R ↔ Pylon)

| Param | Value |
|---|---|
| Hinge type | TPU 95A live-hinge foot, bolted to temple plate |
| Foot footprint | 8 × 12 mm |
| Foot retention | 2× M2 × 6 mm bolts into M2 heat-set inserts in temple plate |
| Hinge axis | Horizontal fore-aft, at temple plate local (−5, +10, +4) — 5 mm aft, 10 mm up, 4 mm proud of plate face |
| Fold direction | **Backward** (pylon rotates aft, lays alongside head past ear) |
| Detent count | 3: straight-up / 45°-back / fold-flat (≈90°-back) |
| Detent mechanism | Notches in TPU live-hinge geometry itself (no separate leaf) |
| Fold-flat envelope | ≤ 75 mm aft of axis, ≤ 15 mm proud of plate — verified clear of ear, Defender, Rear Visor-Band hinge in all 3 detents |
| RF feed routing | RG-178 coax across hinge with 40 mm service loop |

### IFACE_TEMPLE_DEFENDER (Temple Plate L/R ↔ Defender cradle)

*Revised 2026-05-20 per Phase-3 envelope check.* Original spec placed pitch pin at plate-local (0, 0, +6), which put the 25 × 25 × 20 mm cradle envelope directly on top of the Yoke 3-bolt cluster, Pylon foot, and both Visor-Band hinge bosses. Remediation: stand the cradle off the plate on a short PETG arm and relocate the pitch axis fore-and-up, into the free zone above the FwdBand hinge and forward of the Pylon foot.

| Param | Value |
|---|---|
| Standoff arm | PETG, integral to Temple Plate; root at plate-local (+5, 0, +8), tip at (+15, +10, +10); cross-section 8 × 6 mm; cantilever length ~12 mm |
| Gimbal | 2-axis, pitch outer + yaw inner; mounted on standoff arm tip |
| Pitch pin | Steel music wire 2 mm × 12 mm, axis horizontal fore-aft, at temple plate local (+15, +10, +10) — pin centerline 10 mm proud of plate face |
| Yaw pin | Steel music wire 2 mm × 12 mm, axis vertical, internal to pitch yoke |
| Aim lock | M2 × 4 mm set-screw + M2 heat-set insert in pitch yoke, bears on yaw shaft |
| Aim range | ±15° pitch, ±15° yaw |
| Coil exit window | 14 mm Ø hole in cradle, centered on caduceus coil axis (faces head's T-T line at neutral aim) |
| Cradle envelope | 25 × 25 × 20 mm (per §4.2), centered on pin (+15, +10, +10) — sweeps X∈[+2.5, +27.5], Z∈[0, +20], Y∈[+10, +30] across full aim range |
| Clearance check | Cradle does NOT overlap Yoke cluster (Z<+10), Pylon foot (X<−1), Cheek hook (Z<−18), Sidehelm dovetail (X<−11), or either Visor-Band hinge boss (Z<−2). Verified by `envelope_temple_stackup.py` r2. |

### IFACE_TEMPLE_CHEEK (Temple Plate L/R ↔ Chin-yoke webbing)

| Param | Value |
|---|---|
| Hook count | **1 per side** (Y-yoke topology: each side gets 1 hook; cam buckle under chin) |
| Hook position | Lower-aft corner of temple plate, at local (−15, −20, 0) |
| Webbing slot | 26 mm wide × 4 mm tall (fits 25 mm webbing) |
| Anti-pullout rib | 3 mm rib on inboard face above slot, prevents webbing from wearing through plate edge |
| Load case | 150 N pull at +30° below horizontal, into +X (forward) and −Y (down) |
| Load path | Hook → plate edge → plate body → yoke bolt cluster (§2 ribs handle stress concentration) |

### IFACE_BAND_STABILIZER (Visor-Band ↔ Stabilizer panel pocket)

| Param | Value |
|---|---|
| Pocket internal dims | 64 × 34 × 4 mm |
| Holds | 2× bifilar PCB 30 × 30 mm side-by-side (2 mm gap), max PCB thickness 3.2 mm |
| Retention | 2× M3 × 6 mm bolts into M3 heat-set inserts in band, bolt-through PCB corners |
| Cable exit | Inboard edge of panel (toward midline), 4 mm Ø grommet to band cable channel |
| Cover plate | Snap-fit PETG, accent-color (white) per §7 two-tone aesthetic |
| Pocket placement on band | Centered on band midline (front-center for Fwd Visor-Band, back-center for Rear Visor-Band) |

### IFACE_BAND_SUBRAIL (Forward Visor-Band lower edge ↔ sensor pods)

| Param | Value |
|---|---|
| Rail standard | MIL-STD-1913 Picatinny (carried forward from ring-frame doc §3, unchanged) |
| Rail axial position | Lower edge of Forward Visor-Band, outer face, running the full forward arc the band covers (~180° across the brow) |
| Station angles preserved | HP-FL (−30°), HP-FR (+30°) plus arbitrary user-positioned stations between |
| Pod chassis | Carried forward from ring-frame doc §4, unchanged |
| Two-step lock | Carried forward from ring-frame doc §4.1, unchanged |
| Cable raceway | Continuous channel along inboard edge of rail, USB-C exits inboard toward band cable channel → hinge service loop → temple plate cable hub |

### IFACE_TEMPLE_SIDEHELM_POD (Temple Plate L/R lower-aft face ↔ sidehelm pod)

*Added 2026-05-20 to support compute + battery placement decision.* HP-SL on Temple Plate L hosts the battery pod (2× 18650 + PMIC, ~95 g + ~15 g shell). HP-SR on Temple Plate R hosts the compute pod (ESP32-S3 Heltec V3 + comms + balun-feed-source for Pylons, ~30 g + ~15 g shell). L/R split keeps temple-low CoG balance to within ~50 g.

| Param | Value |
|---|---|
| Mount location | Lower-aft face of Temple Plate, below the Cheek Hook |
| Mount geometry | **Sliding dovetail** (NOT MIL-STD-1913; simpler dovetail chosen for vertical-slide adjust, same family as the ring-frame R2 vertical interface in `mk0.5_base_crown_architecture.md` §2.2) |
| Dovetail dims | Top width 12 mm, bottom width 18 mm, depth 3.4 mm, length 35 mm vertical (no teeth — single sliding dovetail, not a Picatinny rail) |
| Adjust travel | 20 mm vertical |
| Lock | M3 thumbscrew + M3 heat-set insert in Temple Plate, bears on dovetail flat |
| Pod envelope | ≤ 70 mm long × 50 mm tall × 40 mm deep (same as `HP-S*` envelope in ring-frame doc §4.2) |
| Cable exit | Top of pod → routes up Temple Plate inboard face into cable hub → Top Yoke internal raceway |
| HP-SL load | Battery pod ~110 g loaded |
| HP-SR load | Compute pod ~45 g loaded |
| L↔R imbalance | ≤ 65 g (well within retention spec) |

---

## 13. Open questions / G-gates pending

- **Anatomical fit of Top Yoke** — circular vs elliptical sweep over
  the parietal. **Decided 2026-05-20**: elliptical arch, 96 mm fore-aft × 78 mm ear-to-ear semi-axes (per anthropometric data). G-Fit gate still measures on real head before final commit.
- **Live-hinge fatigue cycles** for Pylon spring — TPU 95A typically
  good for >5000 cycles in flexure; **G-Pylon** (§11) now formalizes the test.
- **Defender aim repeatability** — **G-Defender-Aim** (§11) now formalizes the ±2° target.
- **Temple Plate-to-Yoke joint** — **Decided 2026-05-20**: 3× M3 bolts with heat-set inserts (per §12 `IFACE_YOKE_TEMPLE`).
- **Defender radiator topology** — **Decided 2026-05-20**: paired caduceus coil shield generating a scalar standing-wave shell around the head (see §4.2). Far-field cancellation is the *designed* property.
- **Pylon dipole feed topology** — **Decided 2026-05-20**: differential true dipole, 1:1 balun in Top Yoke (see §4.1).
- **Stabilizer channelization** — **Decided 2026-05-20**: 2 standalone Psi-Stabilizer-Mk1 units, one per side (see §4.3).
- **Compute + battery placement** — **Decided 2026-05-20**: split sidehelm pods on a new vertical sliding dovetail interface; battery at HP-SL, compute+balun-source at HP-SR (see §12 `IFACE_TEMPLE_SIDEHELM_POD`).

Remaining truly-open items (need bench / FDTD / empirical work, not design decisions):

- **Defender paired-drive phase relationship** — anti-phase is the canonical caduceus baseline; in-phase / quadrature variants may improve shell coherence for specific skull geometries; needs RF integration pass.
- **Defender SAR with paired drive** — FDTD model of the joint near-field with both coils active and skull tissue; gate is G-SAR (§11).
- **Pylon balun selection** — commercial 1:1 current balun at 2.45 GHz in a 25×15×10 mm envelope; survey + select.
- **Top Yoke arch parametric fit** — elliptical sweep validated on developer head before canon commit.

---

## 14. Cross-references

- [`mk0.5_base_crown_architecture.md`](mk0.5_base_crown_architecture.md) — fallback ring-frame variant; canonical for rail / pod / retention spec carry-forward.
- [`mk0.5_prior_art_index.md`](mk0.5_prior_art_index.md) — third-party 3D model references (Halo Mark VI, ODST, N7 — relevant to β aesthetics).
- [`../wiki_anchors.md`](../wiki_anchors.md) — psi-coil canon (bifilar 30 × 30 mm, 1–8 MHz; 2.45 GHz primary RF).
