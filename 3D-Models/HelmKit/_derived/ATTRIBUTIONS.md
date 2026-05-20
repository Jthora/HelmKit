# Third-Party Asset Attributions

This directory contains third-party open-source 3D models that
HelmKit references or derives from. Each subfolder preserves the
original `LICENSE.txt` and `README.txt` from the upstream
Thingiverse page.

**Discipline**: only 🟢 CC-BY (or 🟢 PD) assets live here. If a 🟡
CC-BY-SA asset ever lands, it goes under `_derived/_sa/` to make
the viral-license boundary obvious. 🔴 CC-BY-NC* assets never
enter the repo (see [`docs/mechanical/mk0.5_prior_art_index.md`](../../../docs/mechanical/mk0.5_prior_art_index.md) §1).

---

## Imported assets

| Thingiverse # | Author | License | Imported | Source folder | How HelmKit uses it |
|---|---|---|---|---|---|
| [23185](https://www.thingiverse.com/thing:23185) | SFE_Tim | CC-BY | 2026-05-20 | [`picatinny_rail_23185_SFE_Tim/`](picatinny_rail_23185_SFE_Tim/) | **Primary tooth-profile reference** for R1's integral curved Picatinny rail. The cross-sectional dovetail profile is extracted from `picatinny_rail.stl` and swept along R1's 220° forward arc to produce a new (original) curved-rail STL. See `tools/blender/build_crown_shell_r1.py`. |
| [2897402](https://www.thingiverse.com/thing:2897402) | cmdctrl | CC-BY | 2026-05-20 | [`picatinny_rail_female_2897402_cmdctrl/`](picatinny_rail_female_2897402_cmdctrl/) | **Pod-side tolerance check.** Female mating geometry with `.svg` source — used to verify that `pod_blank.stl`'s dovetail slot dimensions match MIL-STD-1913 within ±0.05 mm. |
| [5160208](https://www.thingiverse.com/thing:5160208) | LucidVR | CC-BY | 2026-05-20 | [`esp32u_mount_5160208_LucidVR/`](esp32u_mount_5160208_LucidVR/) | **ESP32 board-mount pattern.** Reference for how the HelmKit compute-pod (HP-R, Mk0.5) holds an ESP32-S3 Heltec module — antenna keep-out, USB-C clearance, standoff spacing. |
| [4667048](https://www.thingiverse.com/thing:4667048) | (see README.txt) | CC-BY | 2026-05-20 | [`oneal_visor_screw_4667048/`](oneal_visor_screw_4667048/) | **HP-F visor pivot fastener** geometry. The two-piece screw-with-captive-nut idiom is the candidate fastener for any forward HUD optic that needs to pivot relative to the crown. |

---

## Citation idiom

When a derived STL is generated from any source above, the
derived STL's preamble (or accompanying README) must include:

> Derived from Thingiverse #&lt;ID&gt; by &lt;author&gt;, used under CC-BY 4.0.
> Original: https://www.thingiverse.com/thing:&lt;ID&gt;.

This satisfies the BY clause without requiring the derivative to
adopt any specific license itself.

---

## What this directory is NOT

- **Not a vendoring of upstream binaries for distribution.** These STLs
  exist to make the geometric reference auditable: if someone reviews
  HelmKit's `crown_shell_R1.stl` and asks "where did the tooth profile
  come from?", the answer is in this folder with provenance intact.
- **Not authoritative.** The authoritative shape of HelmKit components
  is defined by the parametric scripts in `tools/blender/`, not by
  these reference STLs.
- **Not redistributed under HelmKit's repo license.** Each file remains
  under its own LICENSE.txt; the repo as a whole does not relicense them.
