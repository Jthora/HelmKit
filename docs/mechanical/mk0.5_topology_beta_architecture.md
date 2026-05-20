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
| **Temple Plate L/R** | PETG | 3 mm | Anatomical anchor at temple; visual hero feature | Pylon live-hinge mount + Defender dish cradle + side-band joint (3 *independent* pivots, co-located) |
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

The temple plates are the **structural confluence** — yoke ends,
visor-band joints, Pylon hinges, Defender cradles, and chin-strap
cheek hooks all anchor to the same plate. Three separate small
pivots (not one shared pin) keep the failure modes uncoupled.

---

## 4. Psi-actuator mounts (bespoke, frozen at print time)

### 4.1 Psi-Pylons (×2)

| Parameter | Value |
|---|---|
| Antenna length | **6 cm** per leg (λ/2 at 2.45 GHz) |
| Cross-section | Long flat triangle, ~6 mm wide at base, ~2 mm at tip, 4 mm thick |
| Hinge axis | Anatomical temple, integral to Temple Plate, axis horizontal fore-aft |
| Hinge type | **Live-hinge with retention spring** (TPU 95A flexure) |
| Detent positions | 3: straight-up / 45°-back / fold-flat |
| Fail mode under lateral load | Folds flat against side of helm at ~30 N; re-deploys after impact |
| Mass per Pylon | Target ≤ 25 g loaded (housing + element + RF feed) |

### 4.2 Psi-Defenders (×2)

| Parameter | Value |
|---|---|
| Dish diameter | 12.24 mm (the dish itself; cradle housing larger) |
| Aim direction | **Inward** at the temple bone (toward the brain along T1–T2 axis) |
| Aim adjustment | ±15° pitch, ±15° yaw via 2-axis pin pivot on Temple Plate |
| Lock | Friction-fit knurl + small set-screw for repeatable session-to-session aim |
| Cradle envelope | ~25 × 25 × 20 mm housing around the 12.24 mm dish + electronics |

### 4.3 Psi-Stabilizers (×2 panel assemblies, 4 bifilar spirals total)

| Parameter | Value |
|---|---|
| Panel dimensions | ~70 × 40 × 6 mm (houses 2 bifilar spirals side-by-side, ~30 × 30 mm PCBs each) |
| Mount | Integral to Forward and Rear Visor-Bands |
| Aim direction | Inward toward the crown apex (front panel pitched down-and-back, rear panel pitched down-and-forward) |
| Aim adjustment | Discrete: 5 detent positions on the visor-band hinge — 0° / 30° / 45° / 60° / 90° from horizontal |
| Per panel: bifilar spirals | 2 × ~30 × 30 mm bifilar PCB coils, left + right of head midline |
| Total spirals on helm | 4 (front-L, front-R, back-L, back-R) |

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

## 10. Open questions / G-gates pending

- **Anatomical fit of Top Yoke** — circular vs elliptical sweep over
  the parietal. Same ovoid-skull issue as ring-frame R1; G-Fit
  gate must measure on real heads before committing the canon arc.
- **Live-hinge fatigue cycles** for Pylon spring — TPU 95A typically
  good for >5000 cycles in flexure; needs accelerated test.
- **Defender aim repeatability** — set-screw + knurl sufficient, or
  do we need a printed alignment jig?
- **Temple Plate-to-Yoke joint** — bonded (epoxy), bolted (M3 ×3),
  or printed integral (single-shot, more print failure risk)?

---

## 11. Cross-references

- [`mk0.5_base_crown_architecture.md`](mk0.5_base_crown_architecture.md) — fallback ring-frame variant; canonical for rail / pod / retention spec carry-forward.
- [`mk0.5_prior_art_index.md`](mk0.5_prior_art_index.md) — third-party 3D model references (Halo Mark VI, ODST, N7 — relevant to β aesthetics).
- [`../wiki_anchors.md`](../wiki_anchors.md) — psi-coil canon (bifilar 30 × 30 mm, 1–8 MHz; 2.45 GHz primary RF).
