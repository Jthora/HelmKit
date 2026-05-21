# `tools/blender/` — parametric mesh generators

This directory holds the **authoritative shape definition** for every
printable part of the HelmKit Mk0.5-β topology. Each `build_*.py`
script generates one STL deterministically from canon parameters
imported from [`interfaces.py`](interfaces.py) (the machine-readable
mirror of §12 in
[`docs/mechanical/mk0.5_topology_beta_architecture.md`](../../docs/mechanical/mk0.5_topology_beta_architecture.md)).

Generated STLs (and their `.txt` sidecars) live in
`3D-Models/HelmKit/_generated/` and are **not** committed — they
are regenerable on demand and `.gitignore`d.

## How to run a single generator

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
    --background --python tools/blender/<script>.py -- \
    --out 3D-Models/HelmKit/_generated/<name>_r1.stl
```

Linux equivalent: replace the macOS app path with `blender`.

## How to regenerate every part

```sh
mkdir -p 3D-Models/HelmKit/_generated
for s in top_yoke temple_plate \
         forward_visor_band rear_visor_band \
         psi_pylon pylon_live_hinge \
         psi_defender_cradle psi_stabilizer_panel \
         visor_detent_leaf \
         sidehelm_pod_battery sidehelm_pod_compute; do
  /Applications/Blender.app/Contents/MacOS/Blender --background \
    --python tools/blender/build_${s}.py -- \
    --out 3D-Models/HelmKit/_generated/${s}_r1.stl
done
```

Each run also writes `<name>_r1.txt` next to the STL with bbox,
estimated mass, consumed interfaces, fastener list, and acceptance-
gate notes.

## Canon (read this first)

- **[`interfaces.py`](interfaces.py)** — 9 frozen `@dataclass`
  interfaces (`IFACE_*`) + M2/M3 clearance and heat-set constants.
  Every generator imports from here. If a script's value disagrees
  with `interfaces.py`, the interface wins and the script is wrong.
- **[`docs/mechanical/mk0.5_topology_beta_architecture.md`](../../docs/mechanical/mk0.5_topology_beta_architecture.md)**
  §12 — human-readable spec these dataclasses mirror.
- **Datum convention (Temple-Plate-local)**: +X forward, +Y up,
  +Z outward (away from head). World-frame parts (Top Yoke, both
  Visor-Bands) document their own conventions in their docstrings.

## Generators — Mk0.5-β set

Material legend: **PETG** = matte black structural; **PETG-W** =
matte white accent; **TPU** = TPU 95A flex.

| # | Script | Output | Material | Bbox (mm) | Interfaces consumed | Gate |
|---|---|---|---|---|---|---|
| 1 | [`build_top_yoke.py`](build_top_yoke.py) | `top_yoke_r1.stl` | PETG | 172 × 102 × 28 | `IFACE_YOKE_TEMPLE` ×2 | G-Yoke |
| 2 | [`build_temple_plate.py`](build_temple_plate.py) | `temple_plate_r1.stl` | PETG | 65 × 59.4 × 22 | 7× (Yoke, FwdBand, RearBand, Pylon, Defender, Cheek, SidehelmPod) | G-Fit, G-Pull |
| 3 | [`build_forward_visor_band.py`](build_forward_visor_band.py) | `forward_visor_band_r1.stl` | PETG | 198.5 × 38 × 99 | `IFACE_TEMPLE_FWDBAND`, `IFACE_BAND_STABILIZER`, `IFACE_BAND_SUBRAIL` | G-Print, G-Cable |
| 4 | [`build_rear_visor_band.py`](build_rear_visor_band.py) | `rear_visor_band_r1.stl` | PETG | ~190 × 38 × 99 | `IFACE_TEMPLE_REARBAND`, `IFACE_BAND_STABILIZER` | G-Print, G-Cable |
| 5 | [`build_psi_pylon.py`](build_psi_pylon.py) | `psi_pylon_r1.stl` ×2 | PETG | 68 × 12 × 4 | `IFACE_TEMPLE_PYLON` | G-Fold |
| 6 | [`build_pylon_live_hinge.py`](build_pylon_live_hinge.py) | `pylon_live_hinge_r1.stl` ×2 | **TPU** | 20 × 12 × 1.5 | `IFACE_TEMPLE_PYLON` | **G-Pylon** |
| 7 | [`build_psi_defender_cradle.py`](build_psi_defender_cradle.py) | `psi_defender_cradle_r1.stl` ×2 | PETG | 25 × 25 × 20 | `IFACE_TEMPLE_DEFENDER` | G-Defender-Aim, G-SAR |
| 8 | [`build_psi_stabilizer_panel.py`](build_psi_stabilizer_panel.py) | `psi_stabilizer_panel_r1.stl` ×2 | PETG | 63.6 × 33.6 × 3.6 | `IFACE_BAND_STABILIZER` | G-Fit |
| 9 | [`build_visor_detent_leaf.py`](build_visor_detent_leaf.py) | `visor_detent_leaf_r1.stl` ×4 | **TPU** | 25 × 8 × 3 | `IFACE_TEMPLE_FWDBAND` / `IFACE_TEMPLE_REARBAND` | G-Motion |
| 10 | [`build_sidehelm_pod_battery.py`](build_sidehelm_pod_battery.py) | `sidehelm_pod_battery_r1.stl` | PETG | 43.4 × 50 × 70 | `IFACE_TEMPLE_SIDEHELM_POD` | G-Pod |
| 11 | [`build_sidehelm_pod_compute.py`](build_sidehelm_pod_compute.py) | `sidehelm_pod_compute_r1.stl` | PETG | 43.4 × 50 × 70 | `IFACE_TEMPLE_SIDEHELM_POD` | G-Pod |

**Per-helm print counts**: 1× Top Yoke, 2× Temple Plate (mirror at
install), 1× Fwd Band, 1× Rear Band, 2× Pylon, 2× Live-hinge, 2×
Defender Cradle, 2× Stabilizer Panel, 4× Detent Leaf, 1× HP-SL
Battery Pod, 1× HP-SR Compute Pod.

## Legacy / scaffolding scripts

These predate the Mk0.5-β interface contract and remain only for
reference. **Do not consume their outputs for the β build.**

| Script | Notes |
|---|---|
| [`build_crown_shell_r1.py`](build_crown_shell_r1.py) | Pre-β monolithic 220° forward crown band with integral curved Picatinny — superseded by `build_forward_visor_band.py`. Tooth slots never subtracted. |
| [`build_pod_blank.py`](build_pod_blank.py) | Original undifferentiated sidehelm pod — superseded by the split battery/compute pair (10, 11). |
| [`build_occipital_cradle_r2.py`](build_occipital_cradle_r2.py) | r2 occipital ring concept; folded into `build_rear_visor_band.py` for the β topology. Useful pattern reference for boolean workflow. |

## Envelope studies (throwaway)

`envelope_pylon_fold.py`, `envelope_temple_stackup.py`,
`envelope_visor_swing.py` — fast clearance probes with a rotated
axis convention. **Do NOT back-port their coordinates into the
production generators.** Re-run any time the canon shifts to
re-verify swing/fold envelopes.

## Acceptance gates referenced

| Gate | Means |
|---|---|
| G-Print | First-layer + bridging clean, no support scarring on visible faces |
| G-Fit | All M2/M3 heat-sets seat flush; mating parts slip-fit without filing |
| G-Pod | L+R pods seat with thumbscrew lock, no shake under 1 m bench drop |
| G-Pull | 150 N anti-lift on yoke joint without strip |
| G-Motion | Visor bands hold each detent against 250 N·mm |
| G-Cable | RG-178 + USB-C routes don't pinch through any joint motion |
| G-Fold | Pylons fold flat (≤ 75 mm aft, ≤ 15 mm proud) |
| G-Pylon | TPU live-hinge survives 100 fold cycles 0↔90° no crack init |
| G-Yoke | Top Yoke arch transfers full helm mass to plates without splay |
| G-Defender-Aim | L+R coil exits collinear within 2° |
| G-SAR | Paired-drive SAR within IEEE C95.1 limits at 2.45 GHz |

Detailed pass criteria live in
[`docs/mechanical/mk0.5_topology_beta_architecture.md`](../../docs/mechanical/mk0.5_topology_beta_architecture.md)
§11.

## License hygiene

Generators may *reference* (read, measure) third-party STLs under
`3D-Models/HelmKit/_derived/` but must produce **original HelmKit
geometry**. The Picatinny tooth dimensions in
`build_forward_visor_band.py` come from MIL-STD-1913 (US-government
public spec).
