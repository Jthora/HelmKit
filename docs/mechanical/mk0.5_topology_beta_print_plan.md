# Mk0.5-β print plan — first physical validation pass

**Status**: v0, 2026-08-06. All 11 STLs regenerated fresh today (`tools/blender/`, Blender 5.0.0 headless, zero errors) and confirmed present in `3D-Models/HelmKit/_generated/` (`.gitignore`d, regenerable on demand — not committed). **Nothing in this set has been printed yet** — this document is the execution plan for closing that gap, not a record of it being closed. Fill in results in `tools/blender/README.md`'s tracking table as each part clears its gate(s).

## Why this order

Grouped into three passes so a failure in an early part doesn't waste filament on parts that depend on it, and so the one genuinely novel material (TPU 95A — flagged in the generator's own sidecar as "FIRST TPU PRINT IN PROJECT") gets isolated to its own small, cheap test print before committing to the full set.

### Pass 1 — Structural skeleton (PETG, print first, everything else depends on fit against these)

| Order | Part | File | Qty | Est. mass (PETG) | Gate(s) to run immediately after |
|---|---|---|---|---|---|
| 1 | Top Yoke | `top_yoke_r1.stl` | 1 | 156.0 g | G-Print, G-Yoke (visual/dimensional only until temple plates exist for G-Fit/G-Pull) |
| 2 | Temple Plate | `temple_plate_r1.stl` | 2 (mirror at install — same STL both sides) | 21.6 g each | G-Print, G-Fit against Top Yoke |
| 3 | Forward Visor-Band | `forward_visor_band_r1.stl` | 1 | 142.3 g | G-Print, G-Fit against Temple Plates |
| 4 | Rear Visor-Band | `rear_visor_band_r1.stl` | 1 | 159.9 g | G-Print, G-Fit against Temple Plates |

Do not proceed past part 2 until G-Fit passes against the Top Yoke — every other part's dimensional assumptions chain through the temple plate.

### Pass 2 — Small mechanism parts (PETG structural + TPU flex, test TPU here first)

| Order | Part | File | Qty | Material | Gate(s) |
|---|---|---|---|---|---|
| 5 | Pylon Live-Hinge | `pylon_live_hinge_r1.stl` | 2 | **TPU 95A — new material, print this alone first as a standalone calibration piece before committing the rest of the batch** | G-Pylon (100 fold cycles, 0↔90°, no crack) |
| 6 | Psi-Pylon | `psi_pylon_r1.stl` | 2 | PETG | G-Fold |
| 7 | Visor Detent-Leaf | `visor_detent_leaf_r1.stl` | 4 | TPU 95A | G-Motion |
| 8 | Psi-Defender Cradle | `psi_defender_cradle_r1.stl` | 2 | PETG | G-Defender-Aim (G-SAR deferred — needs coil-drive electronics, not just the cradle) |
| 9 | Psi-Stabilizer Panel | `psi_stabilizer_panel_r1.stl` | 2 | PETG | G-Fit |

Print part 5 alone first. TPU is flagged in the generator's own sidecar as this project's first-ever TPU print — confirm the QIDI X-MAX3's extruder/retraction settings handle a flexible filament cleanly on a small, cheap 20×12×1.5mm part before running the visor-detent-leaf batch (part 7, also TPU) or committing more filament.

### Pass 3 — Side pods (largest single-part prints)

| Order | Part | File | Qty | Material | Gate(s) |
|---|---|---|---|---|---|
| 10 | Sidehelm Pod — Battery (HP-SL) | `sidehelm_pod_battery_r1.stl` | 1 | PETG | G-Pod |
| 11 | Sidehelm Pod — Compute (HP-SR) | `sidehelm_pod_compute_r1.stl` | 1 | PETG | G-Pod |

## Print settings — starting points, not verified values

None of these have been bench-confirmed against your specific filament spools; treat as sane defaults to start from and tune, not as pre-validated settings the way the geometry itself is.

- **Printer**: QIDI X-MAX3, 325×325×315mm heated chamber (confirmed in `mk0.5_topology_beta_architecture.md` §0). Every part here comfortably fits the build volume individually — the largest single part (rear visor-band) is 199×38×111mm, well under any axis limit, so this is a print-quality question, not a fit-in-the-printer question.
- **PETG** (parts 1–4, 6, 8–11): nozzle ~230–240°C, bed ~70–80°C, chamber heat on (this printer has one — use it, PETG benefits from reduced draft/warping). Structural parts (Top Yoke, Temple Plate, both Visor-Bands) all call for M2/M3 heat-set inserts per `interfaces.py` — print with enough perimeter wall thickness around each insert boss to avoid stripping (the generators' stated wall_mm values, 2.0–4.0mm, already account for this per their sidecars, but confirm boss wall thickness specifically before heat-setting).
- **TPU 95A** (parts 5, 7): slow down significantly versus PETG — TPU's flexibility makes it prone to buckling in the extruder path at PETG-typical speeds. The X-MAX3's direct-drive extruder handles TPU far better than a Bowden path would; still expect a meaningfully slower speed.
- **Orientation**: `pylon_live_hinge_r1.txt` explicitly states `print_orientation: flat on bed, web spans Y axis on bed` — the only part with a stated orientation requirement in its sidecar; the others don't specify one, so use standard largest-flat-face-down practice and check each sidecar's bbox for the obvious choice.

## What happens at G-SAR (part 8, deferred)

`psi_defender_cradle` prints and can clear G-Defender-Aim (mechanical: L+R coil exits collinear within 2°) using just the printed cradle. **G-SAR cannot be run until the coil-drive electronics from `docs/mk0_pcb_bifilar_coil.md` exist and are mounted** — this is an electrical/RF gate, not a mechanical one, and it's correctly expected to lag the other 10 parts. Don't block the rest of the pass on it.

## TPU living-hinge fatigue research (2026-08-06) — the 100-cycle gate looks conservative, orientation is the make-or-break variable

Checked the G-Pylon gate's 100-fold-cycle target against published FDM/TPU living-hinge engineering practice before spending print attempts on it.

**The 100-cycle target is very likely conservative, not aggressive.** Published guidance: a well-designed, correctly-oriented TPU living hinge (1.2–1.6mm thickness) can survive **50,000–100,000** flex cycles; even a poorly-oriented or otherwise suboptimal FDM TPU hinge is reported to typically reach **500–1,000** cycles — five to ten times our gate's target. Our own web thickness (0.8mm) sits right at the low end of the TPU-specific recommended range (0.8–1.2mm) found in this pass, which is a good sign, not a red flag.

**The one variable that actually matters — and can cause instant failure if wrong — is print orientation.** Multiple independent sources agree: layers must run **parallel to the hinge/fold axis**; if the part is oriented so layers stack *across* the bend (Z-direction through the fold), the hinge **delaminates on the first flex**, regardless of material or thickness. Reported effect size of getting this right: a 500–1000% cycle-life improvement from orientation alone — bigger than any other single design variable.

**Cross-check against our own generator**: `pylon_live_hinge_r1.txt`'s stated `print_orientation: flat on bed, web spans Y axis on bed` (the hinge folds about the Y axis; printing flat means layers stack in Z, a short ~3–4-layer stack for the 0.8mm web) appears consistent with the "layers parallel to hinge axis" rule — but given the research's repeated emphasis that getting this backwards causes instant failure, **visually confirm the orientation in the slicer before printing** (layer lines should run along the 12mm Y-axis span, not across the 4mm fold-direction span) rather than trusting the sidecar note alone.

**Concrete TPU print-setting update** (replaces the generic "slow down significantly" guidance above): direct-drive extrusion at **20–30 mm/s**, printed toward the **higher end** of the TPU spool's recommended nozzle-temperature range specifically for better inter-layer bonding in the flex zone (a different priority than PETG's dial-in, where temperature is mostly about surface finish).

## Heat-set insert boss wall thickness — checked against real guidance, and against our own frozen spec (2026-08-06)

The print settings section above flagged "confirm boss wall thickness before heat-setting" without a number. Closed that gap.

**Published guidance**: an M3 heat-set insert boss needs roughly **1.6–2.0mm** of PETG wall thickness around the insert for reliable, crack-free retention as a robust target (a bare-minimum figure of ~0.95mm appears in some references, but multiple sources converge on 1.6–2mm as the number to actually design to — thin walls risk the insert splitting the boss on installation). PETG specifically tends to want a slightly larger starting hole than PLA due to its more ductile, heat-sensitive behavior during insertion.

**Checked against our own frozen spec**: `tools/blender/interfaces.py` already specifies `boss_min_thickness_mm = 6.0` ("PETG around insert OD") for the Top-Yoke↔Temple-Plate M3 joint (`IFACE_YOKE_TEMPLE`, the highest-load joint at 600N design load) — **3–6× the published robust-target range**, well clear of even a generous safety margin. This is a positive confirmation, not a new gap: the joint most likely to matter under load was already over-specified relative to real guidance before this check. **Not yet spot-checked**: the M2 insert locations (pylon foot, defender-cradle aim-lock setscrew) — `interfaces.py` doesn't show an equivalent `boss_min_thickness_mm` constant for those smaller fasteners in what was reviewed here, worth a quick confirmation before printing those specific parts, though M2 bosses are inherently smaller-scale and lower-load than the Yoke joint.

**Installation practice, sourced**: soldering iron ~10–20°C above PETG's print temperature (roughly 245–260°C for PETG printed around 235°C), using a dedicated flat heat-set installation tip (not a pointed soldering tip) for even heat distribution, insert to ~90% depth and stop right as it goes flush, and — the most common real-world failure mode cited — let the iron reach full target temperature before starting, since a not-fully-heated iron forces the insert in crooked rather than letting it melt in straight.

**Recommendation carried into the print order above**: print one small heat-set-insert test coupon (not a full Top Yoke) first, install a real insert, and check pull-out/torque/cracking behavior before committing the full structural-part batch — same "test the risky step small and cheap before committing filament" discipline already applied to the TPU calibration piece in Pass 2.

## After this pass

Record every result — pass, fail, or "not yet run" — in `tools/blender/README.md`'s tracking table, not just here. That table is the authoritative status; this document is the plan for getting there. If a part fails a gate, the fix belongs in the corresponding `build_*.py` generator (regenerate, don't hand-edit an STL) so the fix is reproducible — per the same "STLs are `.gitignore`d and regenerable, `interfaces.py` is canon" discipline the rest of `tools/blender/` already follows.
