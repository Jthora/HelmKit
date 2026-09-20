# vp0.17 printability matrix (Track P, deep run P8)

**Status:** v1, 2026-09-15. Three rosters and their cross-check: everything that can go wrong printing a part on the
QIDI X-Max 3 (roster A), every part in the set (roster B), and A checked against B, by machine where a rule is
computable (`tools/blender/vp0/print_matrix.py`) and by hand where it is not. Findings that changed the generators
are in §4; what remains as an accepted note is in §5. Companion to
[`../plans/2026-tier1-launch/track-P-print-to-completion.md`](../plans/2026-tier1-launch/track-P-print-to-completion.md)
and the parts table in [`vp0_visual_prototype.md`](vp0_visual_prototype.md) §4.

**Addendum 2026-09-20.** The classified deep audit (`tools/blender/vp0/print_deep.py`, table in [`vp0_deep_audit.md`](vp0_deep_audit.md)) found a class this matrix could not see, a bed face in two planes, on six parts, plus the dome's 5 % perch and the brow rail's half-lap cantilever. The fixes and the print-process rules that came out of them are in [`vp0_visual_prototype.md`](vp0_visual_prototype.md) §6.1.

Printer and settings for every threshold below: QIDI X-Max 3, 325 × 325 × 315 mm, enclosed, direct drive, 0.4 mm
nozzle, textured PEI plate; QIDI Studio presets at 0.2 mm layers (0.16 for the dome), 3 walls, 20 % gyroid, PLA at
220 / 60 °C and PETG at the spool's 220 °C on an 80 °C bed (Track P §2). The times in the machine columns and in roster B were produced with
the Cura 4.8 engine at Ender-class speeds before the printer was corrected (2026-09-15); they are upper bounds for the
X-Max 3. The geometry columns do not depend on the printer.

## 1. Roster A: what to check

Thresholds come from the FDM design guides listed at the end, tightened where PETG or a first-time print is less
forgiving than the guide's assumption (the X-Max 3's enclosure and direct drive earn no relaxation: the set prints once), and from this project's own print-readiness lessons (the vp0 README).

| ID | Check | Rule for this printer | How it is verified |
|---|---|---|---|
| A1 | Bed envelope | footprint ≤ 315 × 315 with skirt or brim, height ≤ 310 (the 325 × 325 × 315 plate); every part fits with room to spare, so a second copy can share the plate once the first has printed well | matrix `fits` |
| A2 | Bed contact and adhesion | contact area ≥ 20 % of the footprint box, or a brim; ≥ 400 mm² for anything over 30 mm tall; PETG parts over 100 mm long get a brim and 80 °C | matrix `contact %`, sidecar brim notes |
| A3 | Contact islands | one island preferred; a standing pin or tab island under 20 mm² needs a brim or a neighbour on the plate | matrix `islands`, `min island` |
| A4 | Tall and thin stability | height / smaller footprint dimension over 3: brim; over 5: brim, slower outer walls, z-hop off | matrix `h/min` |
| A5 | Overhangs | faces more than 45° from vertical need support or a design change; 45 to 60° prints with cooling in PLA, is marginal in PETG; over 60° does not print | matrix `45-60` / `60-70` areas |
| A6 | Bridges | unsupported spans with both ends supported: ≤ 25 mm PLA, ≤ 15 mm PETG at 0.2 mm; a sagging bridge lowers the ceiling of a tunnel or hole by 0.2 to 0.5 mm | matrix flat-overhang clusters (`span`), sidecar |
| A7 | Ledges (one-sided flat overhangs) | a horizontal face supported on one side only prints ≤ 1 mm; anything longer droops and curls: chamfer it to 45° or support it | matrix flat clusters read by hand against the geometry (a cluster's span says nothing about whether its far side is supported) |
| A8 | Wall thickness | structural walls ≥ 1.2 mm (three lines), cosmetic ≥ 0.8; walls in multiples of 0.4 avoid gap fill | matrix `min wall`, thin-wall lesson |
| A9 | Small features | vertical holes ≥ 1.0 mm, horizontal ≥ 2.0; standing pins ≥ 3 mm and ≤ 5:1; embossed text ≥ 0.6 wide | by hand from canon |
| A10 | Minimum layer time | parts with layers under ~5 s (tiny pins, clips, caps) print with a neighbour or a sacrificial tower so each layer cools | roster B grouping |
| A11 | Vertical holes under size | 0.2 to 0.4 mm smaller than modelled: add 0.2 to 0.4 for clearance fits or drill | coupons A and B, tolerance table in Track P §4 |
| A12 | Horizontal holes | the top sags into a D; ≥ 2 mm and teardrop or drilled | `add_teardrop` (v0.17), coupon B round-vs-teardrop row |
| A13 | Elephant's foot | features opening on the bed face come out 0.2 to 0.4 smaller: chamfer or step the mouth, or set the slicer's initial-layer expansion to −0.2 | matrix `bed holes`, mouth reliefs in the generators, coupon B bed-face socket |
| A14 | Bed-side recesses | a recess on the bed face shallower than four layers (0.8 mm) is squashed shut; deeper ones survive as bridged pockets | matrix flat clusters with low z under 0.8 |
| A15 | Load across layers | Z tension and bending see 40 to 75 % of in-plane strength: orient pins, stalks and hooks so the load runs along layers, or use PETG with margin | Track P §6 (P4) |
| A16 | Stress risers | fillets ≥ 0.5 mm at loaded internal corners; no knife edges under 0.4 mm (the slicer drops them) | generator fillets; `fillet()` on every part |
| A17 | Warping and shrinkage | first layers over 100 mm lift at the corners: brim 5 to 8 mm, fan off for three layers, bed hot; PETG worse; shrinkage 0.2 to 0.5 % of length (0.6 mm across the cradle); the enclosure keeps drafts off PETG, the chamber heater stays off for PLA and PETG, PLA prints with the door ajar | roster B brim column, coupon calibration |
| A18 | Supports | only where the sidecar says so; interior supports must be reachable; support scars never on mating faces | sidecar notes, matrix overhang columns |
| A19 | Seams | the Z seam sits on hidden or non-mating faces; cosmetic parts print so the seam is inside | slicer setting "sharpest corner", per-part note |
| A20 | Enclosed ceilings | box lids and pocket ceilings need ≥ 4 top layers; internal bridges over cavities ≤ 20 mm | matrix `span` on pods, nape base, sensor bar |
| A21 | PETG stringing and islands | many separate islands per layer (bosses, stalks) string in PETG: the machine preset's 1 mm direct-drive retraction and 0.4 z-hop, travel avoid, slower | roster B material column |
| A22 | Nozzle collisions | tall prints and curled overhangs get hit: z-hop 0.4 (the machine preset's default) on tall parts; the dome on edge | roster B tall parts |
| A23 | Layer quantisation | heights that must be exact (cam floors, 0.15 flats) come out in 0.2 mm steps; design in multiples or change the layer height | canon numbers; the dome at 0.16 |
| A24 | Print-in-place and loose islands | gaps ≥ 0.3 mm between islands that must stay separate | coupon B ring |
| A25 | Mesh integrity | manifold, outward normals, no coplanar shells, slices with zero engine errors | `finalize_and_export` warning, P1 slicer pass |
| A26 | Material assignment | PETG for anything that carries preload or a load path or lives in a hot car; PLA for shells and pods | roster B material |
| A27 | Post-processing | every drill pass, support removal, deburr and nut insertion written into the assembly step | spec §6 assembly order |
| A28 | Skin-facing surfaces | no support scars or seams on faces that touch the head | pad plates print head face up |

## 2. Roster B: every part that prints

Quantities for one helm. "Both" = combat trim and full trim. Times and masses are the P1 slicer's (Cura 4.8 engine; upper bounds for the
X-Max 3) for one piece at 0.2 mm and 20 % infill, updated for the parts rebuilt in this pass.

| Part | Qty | Trim | Material | Orientation (sidecar) | Supports / brim | Time | g |
|---|---|---|---|---|---|---|---|
| fit_coupon (A) | 1 | first | PLA | flat | no | 4 h 14 | 53 |
| fit_coupon_b | 1 | first | PLA | flat | no | 4 h 00 | 52 |
| band_gauge_front | 1 | first | PLA | flat | build-plate supports | 1 h 33 | 20 |
| port_drill_guide | 1 | first | PLA | flat | no | 0 h 31 | 7 |
| cradle_front | 1 | both | PETG | upside down: top edge, node tops and pin lugs on the bed | brim | 8 h 09 | 98 |
| cover_front | 2 (each file holds the strip in pieces) | both | PETG | standing on the long edge | brim | 0 h 08 | 2 |
| cover_side | 2 | both | PETG | standing on the long edge | brim | 0 h 02 | 0 |
| cover_bottom | 2 | both | PETG | flat (bent into the channel) | no | 0 h 04 | 1 |
| rear_band_half | 2 | both | PETG | top edge on the bed, rack teeth up | brim | 1 h 50 | 23 |
| cover_rear | 2 | both | PETG | standing on the long edge | brim | 0 h 05 | 1 |
| cover_rear_in | 2 | both | PETG | standing on the long edge | brim | 0 h 03 | 1 |
| nape_core_base | 1 | both | PLA | standing on its bottom end, nail holes vertical | brim | 2 h 41 | 31 |
| nape_core_cap | 1 | belt-only | PLA | outer face down | no | 0 h 35 | 7 |
| pad_front | 1 | both | PLA | standing on its bottom edge | brim | 0 h 16 | 3 |
| carrier_ppg | 1 | both | PLA | plug down | no | 0 h 12 | 2 |
| carrier_eda | 2 | both | PLA | plug down | no | 0 h 08 | 2 |
| pad_hub L / R | 1 each | both | PLA | outer face down, seat up | no | 0 h 15 | 3 |
| pad_rear L / R | 1 each | both | PLA | outer face down, pillar up | no | 0 h 11 | 2 |
| sensor_bar | 1 | combat | PLA | on its bottom face | brim | 2 h 19 | 29 |
| bar_carrier | 1 | combat | PLA | flat | no | 0 h 06 | 1 |
| bar_pin | 2 | combat | PLA | standing | print with a neighbour (A10) | 0 h 02 | 0 |
| port_plug_flush | 4 | combat | PLA | cap down | no | 0 h 08 | 1 |
| port_plug | 2 | full | PLA | cap down | no | 0 h 10 | 1 |
| disk_dome | 2 | full | PLA (light) | on edge on the rim flat, 0.16 mm layers | interior tree supports under the apex boss and rim crown; wide brim | 7 h 18 | 95 |
| disk_back L / R | 1 each | full | PLA | flat, boss up | no | 2 h 23 | 28 |
| disk_knob | 2 | full | PETG | knob face down, shaft up | brim | 0 h 21 | 4 |
| knob_clip | 2 | full | PETG | flat | with a neighbour (A10) | 0 h 02 | 0 |
| nexus L / R | 1 each | full | PETG | inner face down, stalk up | no | 2 h 05 | 28 |
| nexus_spool | 2 | full | PETG | plate down, hub up | no | 0 h 47 | 10 |
| coil_former (spool) | 4 | full | PLA | flat, flange down | no | 1 h 51 | 21 |
| bay_spool | 1 | full | PLA | flat | no | 0 h 29 | 6 |
| crown_arch_half | 2 | full | PLA | on edge, ridged face up | brim | 1 h 40 | 22 |
| port_coupler | 2 | full | PLA | standing | brim, with a neighbour | 0 h 14 | 2 |
| apex_block | 1 | full | PLA | on end | brim | 1 h 19 | 17 |
| brow_center | 1 | full | PLA | standing on the bottom face | brim | 4 h 46 | 60 |
| brow_lid | 1 | full | PLA | flat, outer face down | no | 1 h 11 | 14 |
| brow_rail L / R | 1 each | full | PLA | lying on the ring face | no | 1 h 01 | 13 |
| brow_link L / R | 1 each | full | PLA | standing on the bottom edge | brim | 0 h 35 | 8 |
| visor_slider | 2 | full | PETG | flat | with a neighbour | 0 h 02 | 1 |
| pylon_base | 2 | full | PLA | inverted, peg up | no | 0 h 51 | 11 |
| pylon_blade | 2 | full | PLA | on the flat inner face, 10 to 15 % infill | no | 1 h 51 | 25 |
| pylon_knob | 2 | full | PLA | flat | no | 0 h 15 | 3 |
| core_pod_nape + lid | 1 + 1 | core = nape | PLA | open side up; lid outer face down | no | 1 h 52 + 0 h 58 | 21 + 11 |
| core_pod_slab + lid, core_socket_foot | 2 + 2, 2 | core = slab | PLA | open side up; lid outer face down; foot inverted | no | 1 h 44 + 0 h 26, 0 h 31 | 19 + 5, 6 |
| button_cap_s / _l | 2 / 1 | with a pod | PLA | flat | with a neighbour | 0 h 02 / 0 h 04 | 0 / 1 |
| belt_pack + lid | 1 + 1 | belt option | PLA | open side up; lid outer face down | no | 5 h 17 + 2 h 37 | 62 + 30 |
| nape_body, cover, lid, dial, key, pinion, retainer | — | module 2 only | PLA | see sidecars | no | 3 h 40 total | 42 |

Full trim with the nape core pod: about 105 h and 1.3 kg. Combat trim: about 22 h and 300 g.

## 3. A × B: the machine columns

Columns, from `tools/blender/vp0/print_matrix.py` on the exported STLs in print orientation: footprint and height in mm;
contact area as a share of the footprint box with the number of bed-contact islands and of holes or recesses opening on the
bed face; height over the smaller footprint dimension; overhang area between 45 and 60° and between 60 and 70° from vertical
(near-bed modelling offsets excluded); flat downward faces off the bed as clusters: how many, the largest cluster's extent
and the lowest one's height (a bridge, a ledge or a bed-side recess: read against the geometry, §4 and §5); thinnest wall
from an inward ray cast; the P1 slicer time (Cura 4.8, an upper bound for the X-Max 3) and PLA-equivalent mass at 0.2 mm and 20 %. Flags: `brim` (contact under
20 % and taller than 20 mm), `tall` (aspect over 5), `bed-holes:n`, `overhang60` / `overhang45` (over 50 / 200 mm²),
`span:n` (a flat cluster over 25 mm, to be read by hand), `bridge:n` (10 to 25 mm off the bed), `thin:n` (under 1.2 mm).
Every part fits the bed and every part slices with zero engine errors (A1, A25).

| part | footprint | h | contact % (islands, bed holes) | h/min | 45-60 / 60-70 mm² | flat overhang: n, span, low z | min wall | time | g | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| apex_block | 34 × 12 | 64 | 60 (1, 1) | 5.2 | 25 / 32 | 4, 3, 34.1 | 1.83 | 1h19 | 17 | tall bed-holes:1 |
| band_gauge_front | 174 × 193 | 15 | 5 (2, 0) | 0.1 | 0 / 0 | 1, 189, 0.3 | 2.98 | - | - | span:189 |
| bar_carrier | 16 × 59 | 2 | 49 (1, 6) | 0.1 | 0 / 0 | 0, 0, 0.0 | 1.03 | 0h06 | 1 | bed-holes:6 thin:1.03 |
| bar_pin | 4 × 4 | 10 | 78 (1, 0) | 2.6 | 0 / 0 | 0, 0, 0.0 | 3.98 | 0h02 | 0 | ok |
| bay_spool | 100 × 25 | 4 | 99 (1, 1) | 0.2 | 1 / 0 | 2, 4, 4.2 | 1.20 | 0h29 | 6 | bed-holes:1 thin:1.20 |
| belt_pack | 105 × 70 | 38 | 91 (1, 4) | 0.5 | 0 / 1 | 1, 10, 20.0 | 1.61 | 5h17 | 62 | bed-holes:4 |
| belt_pack_lid | 105 × 70 | 4 | 97 (1, 4) | 0.1 | 0 / 0 | 4, 6, 0.7 | 2.50 | 2h37 | 30 | bed-holes:4 |
| brow_center | 15 × 160 | 54 | 98 (1, 2) | 3.6 | 27 / 2 | 16, 124, 2.0 | 0.45 | 4h47 | 60 | bed-holes:2 span:124 thin:0.45 |
| brow_lid | 44 × 124 | 2 | 99 (1, 4) | 0.0 | 0 / 0 | 0, 0, 0.0 | 1.17 | 1h11 | 14 | bed-holes:4 thin:1.17 |
| brow_link_L | 50 × 45 | 20 | 8 (1, 2) | 0.4 | 7 / 3 | 4, 31, 2.5 | 1.82 | 0h35 | 8 | brim bed-holes:2 span:31 |
| brow_link_R | 50 × 45 | 20 | 8 (1, 2) | 0.4 | 7 / 2 | 4, 31, 2.5 | 1.82 | 0h35 | 8 | brim bed-holes:2 span:31 |
| brow_rail_L | 112 × 52 | 7 | 19 (2, 1) | 0.1 | 0 / 0 | 3, 32, 3.5 | 1.60 | 1h01 | 13 | bed-holes:1 span:32 |
| brow_rail_R | 112 × 52 | 7 | 19 (2, 1) | 0.1 | 0 / 0 | 3, 32, 3.5 | 1.42 | 1h01 | 13 | bed-holes:1 span:32 |
| button_cap_l | 14 × 14 | 4 | 56 (1, 1) | 0.3 | 0 / 0 | 1, 4, 2.0 | 2.00 | 0h04 | 1 | bed-holes:1 |
| button_cap_s | 10 × 10 | 4 | 45 (1, 1) | 0.4 | 0 / 0 | 1, 4, 2.0 | 2.00 | 0h02 | 0 | bed-holes:1 |
| carrier_eda | 16 × 18 | 8 | 58 (1, 0) | 0.5 | 0 / 0 | 1, 18, 2.0 | 1.30 | 0h08 | 2 | bridge:18 |
| carrier_ppg | 26 × 18 | 8 | 65 (1, 0) | 0.5 | 0 / 0 | 1, 26, 2.0 | 1.30 | 0h12 | 2 | span:26 |
| coil_former | 109 × 109 | 5 | 67 (1, 2) | 0.0 | 0 / 0 | 3, 21, 0.8 | 1.20 | 1h51 | 21 | bed-holes:2 bridge:21 thin:1.20 |
| core_pod_lid_nape | 62 × 54 | 3 | 84 (1, 5) | 0.1 | 0 / 0 | 4, 6, 0.7 | 1.64 | 0h58 | 11 | bed-holes:5 |
| core_pod_lid_slab | 62 × 22 | 3 | 89 (1, 4) | 0.1 | 0 / 0 | 4, 6, 0.7 | 1.64 | 0h26 | 5 | bed-holes:4 |
| core_pod_nape | 62 × 54 | 22 | 92 (1, 3) | 0.4 | 0 / 1 | 5, 12, 14.2 | 1.20 | 1h52 | 21 | bed-holes:3 bridge:12 |
| core_pod_slab | 62 × 22 | 38 | 91 (1, 2) | 1.7 | 0 / 1 | 7, 26, 11.0 | 1.20 | 1h44 | 19 | bed-holes:2 span:26 |
| core_socket_foot | 50 × 20 | 19 | 88 (1, 2) | 0.9 | 0 / 1 | 0, 0, 0.0 | 2.13 | 0h31 | 6 | bed-holes:2 |
| cover_bottom | 78 × 69 | 1 | 6 (1, 0) | 0.0 | 0 / 0 | 0, 0, 0.0 | 1.00 | 0h04 | 1 | thin:1.00 |
| cover_front | 86 × 92 | 4 | 3 (2, 0) | 0.0 | 0 / 0 | 0, 0, 0.0 | 1.50 | 0h08 | 2 | ok |
| cover_rear | 78 × 51 | 4 | 2 (1, 0) | 0.1 | 0 / 0 | 0, 0, 0.0 | 1.00 | 0h05 | 1 | thin:1.00 |
| cover_rear_in | 59 × 39 | 3 | 3 (1, 0) | 0.1 | 0 / 0 | 0, 0, 0.0 | 1.00 | 0h03 | 1 | thin:1.00 |
| cover_side | 18 × 2 | 4 | 100 (1, 0) | 2.5 | 0 / 0 | 0, 0, 0.0 | 1.50 | 0h02 | 0 | ok |
| cradle_front | 176 × 200 | 48 | 4 (4, 4) | 0.3 | 259 / 86 | 26, 13, 0.6 | 0.48 | 8h09 | 98 | brim bed-holes:4 overhang60 bridge:13 thin:0.48 |
| crown_arch_half | 86 × 138 | 20 | 6 (1, 1) | 0.2 | 33 / 38 | 1, 15, 14.0 | 0.90 | 1h40 | 22 | brim bed-holes:1 bridge:15 thin:0.90 |
| disk_back_L | 121 × 121 | 14 | 73 (1, 8) | 0.1 | 0 / 0 | 8, 27, 0.8 | 1.20 | 2h23 | 28 | bed-holes:8 span:27 thin:1.20 |
| disk_back_R | 121 × 121 | 14 | 73 (1, 8) | 0.1 | 0 / 0 | 8, 27, 0.8 | 1.20 | 2h23 | 28 | bed-holes:8 span:27 thin:1.20 |
| disk_dome | 122 × 23 | 122 | 5 (1, 0) | 5.2 | 1122 / 624 | 20, 40, 0.4 | 1.00 | 7h18 | 95 | brim tall overhang60 span:40 thin:1.00 |
| disk_knob | 28 × 28 | 18 | 66 (1, 0) | 0.6 | 0 / 0 | 4, 22, 0.8 | 1.10 | 0h21 | 4 | bridge:22 thin:1.10 |
| fit_coupon | 183 × 89 | 24 | 44 (4, 8) | 0.3 | 14 / 14 | 11, 27, 7.0 | 1.20 | 4h14 | 53 | bed-holes:8 span:27 thin:1.20 |
| fit_coupon_b | 110 × 107 | 28 | 59 (2, 6) | 0.3 | 8 / 22 | 5, 12, 14.0 | 1.00 | 4h07 | 53 | bed-holes:6 bridge:12 thin:1.00 |
| knob_clip | 13 × 14 | 2 | 55 (1, 0) | 0.1 | 0 / 0 | 0, 0, 0.0 | 2.00 | 0h02 | 0 | ok |
| nape_body | 44 × 60 | 14 | 30 (2, 2) | 0.3 | 0 / 0 | 2, 57, 6.6 | 0.36 | 0h59 | 11 | bed-holes:2 span:57 thin:0.36 |
| nape_core_base | 25 × 60 | 44 | 83 (2, 3) | 1.8 | 13 / 28 | 17, 57, 0.6 | 0.17 | 2h41 | 31 | bed-holes:3 span:57 thin:0.17 |
| nape_core_cap | 44 × 60 | 2 | 93 (1, 2) | 0.0 | 0 / 1 | 2, 6, 0.7 | 1.30 | 0h35 | 7 | bed-holes:2 |
| nape_cover | 44 × 60 | 19 | 62 (1, 1) | 0.4 | 0 / 0 | 9, 6, 2.0 | 0.24 | 1h25 | 17 | bed-holes:1 thin:0.24 |
| nape_dial | 34 × 34 | 6 | 70 (1, 3) | 0.2 | 0 / 0 | 3, 10, 1.5 | 0.17 | 0h23 | 4 | bed-holes:3 bridge:10 thin:0.17 |
| nape_key | 24 × 24 | 7 | 56 (1, 3) | 0.3 | 0 / 0 | 0, 0, 0.0 | 0.17 | 0h07 | 1 | bed-holes:3 thin:0.17 |
| nape_lid | 44 × 60 | 2 | 93 (1, 5) | 0.1 | 0 / 1 | 0, 0, 0.0 | 1.20 | 0h38 | 7 | bed-holes:5 thin:1.20 |
| nape_pinion | 17 × 17 | 10 | 32 (1, 1) | 0.6 | 0 / 0 | 13, 3, 4.8 | 1.39 | 0h08 | 2 | bed-holes:1 |
| nape_retainer | 12 × 12 | 4 | 63 (1, 1) | 0.3 | 0 / 0 | 0, 0, 0.0 | 0.80 | 0h02 | 0 | bed-holes:1 thin:0.80 |
| nexus_L | 68 × 68 | 22 | 74 (1, 5) | 0.3 | 8 / 0 | 3, 6, 12.0 | 1.54 | 2h04 | 28 | bed-holes:5 |
| nexus_R | 68 × 68 | 22 | 74 (1, 5) | 0.3 | 8 / 0 | 3, 6, 12.0 | 1.49 | 2h05 | 28 | bed-holes:5 |
| nexus_spool | 44 × 56 | 9 | 71 (1, 3) | 0.2 | 0 / 20 | 6, 3, 7.0 | 1.00 | 0h47 | 10 | bed-holes:3 thin:1.00 |
| pad_front | 13 × 84 | 18 | 12 (1, 0) | 1.4 | 6 / 0 | 5, 22, 7.4 | 1.57 | 0h16 | 3 | bridge:22 |
| pad_hub_L | 38 × 25 | 6 | 78 (1, 7) | 0.2 | 0 / 1 | 3, 5, 0.8 | 1.20 | 0h15 | 3 | bed-holes:7 thin:1.20 |
| pad_hub_R | 38 × 25 | 6 | 78 (1, 7) | 0.2 | 0 / 1 | 3, 5, 0.8 | 1.20 | 0h15 | 3 | bed-holes:7 thin:1.20 |
| pad_rear_L | 24 × 26 | 6 | 81 (1, 3) | 0.3 | 0 / 1 | 0, 0, 0.0 | 1.17 | 0h11 | 2 | bed-holes:3 thin:1.17 |
| pad_rear_R | 24 × 26 | 6 | 81 (1, 3) | 0.3 | 0 / 1 | 0, 0, 0.0 | 1.30 | 0h11 | 2 | bed-holes:3 |
| port_coupler | 8 × 8 | 30 | 78 (1, 0) | 3.8 | 0 / 0 | 0, 0, 0.0 | 2.13 | 0h14 | 2 | ok |
| port_drill_guide | 24 × 20 | 20 | 71 (1, 1) | 1.0 | 14 / 16 | 2, 8, 14.7 | 5.37 | 0h31 | 7 | bed-holes:1 |
| port_plug | 12 × 12 | 18 | 69 (1, 0) | 1.5 | 0 / 2 | 0, 0, 0.0 | 2.13 | 0h10 | 1 | ok |
| port_plug_flush | 12 × 12 | 16 | 92 (1, 0) | 1.3 | 0 / 0 | 0, 0, 0.0 | 1.30 | 0h08 | 1 | ok |
| pylon_base | 28 × 19 | 44 | 39 (2, 0) | 2.3 | 16 / 36 | 7, 26, 0.7 | 2.13 | 0h51 | 11 | span:26 |
| pylon_blade | 28 × 150 | 14 | 60 (1, 1) | 0.5 | 44 / 0 | 1, 30, 5.4 | 1.28 | 1h51 | 25 | bed-holes:1 span:30 |
| pylon_knob | 24 × 24 | 8 | 73 (1, 1) | 0.3 | 0 / 0 | 0, 0, 0.0 | 5.00 | 0h15 | 3 | bed-holes:1 |
| rear_band_half | 97 × 113 | 36 | 4 (1, 0) | 0.4 | 0 / 0 | 3, 7, 5.0 | 0.18 | 1h50 | 23 | brim thin:0.18 |
| sensor_bar | 38 × 120 | 20 | 25 (1, 2) | 0.5 | 0 / 0 | 6, 109, 0.4 | 0.53 | 2h19 | 29 | bed-holes:2 span:109 thin:0.53 |
| visor_slider | 24 × 21 | 3 | 16 (1, 0) | 0.1 | 0 / 0 | 0, 0, 0.0 | 1.40 | 0h02 | 1 | ok |

## 4. Findings that changed the generators (this pass)

The machine columns and the by-hand reading of the flat-overhang clusters against the geometry produced eight changes.
Every one is in the generators and canon, rebuilt, re-audited, re-sliced and re-validated in both assemblies (0 unexpected
overlaps).

| # | Check | Part(s) | What was wrong | What changed |
|---|---|---|---|---|
| F1 | A7 ledges | cradle_front (spine channels on the outer face, node harness grooves), rear_band_half (spine channel, inner harness channel) | every groove cut into a side face has one wall that faces down in the print. Upside down, the cradle's 4 × 4 spine channel put a 4 mm ledge in the air along 290 mm of the front arc plus both side runs; the rear half's two channels had 3 mm and 2.5 mm ledges over 75 to 90 mm. The v0.14 audit had reported the area (3461 mm² of flat overhang at 0.1 mm) and it was read as the band's fillets. | `vp0lib.groove_section()`: the groove section is a rectangle plus a 45° wedge below it, inside the band, so the wall becomes an overhang. Applied to the cradle's three spine runs, both node grooves and both rear-half channels. The flat clusters at those heights are gone from the matrix. |
| F1b | A7 + A9 | cradle_front front run, cover_front | the wedge under the front run would have cut into the sensor bar's two Ø4.1 pin sockets and the centre tap, which sit 1.45 mm under the channel | the front run is a closed tunnel for 8 mm at each of the three fasteners (a 1.5 mm printed skin; its print-ceiling is a 2.5 mm bridge), with 4 mm wedge ramps either side; the skin ends square. `cover_front` prints in pieces with gaps at the stations. A first version tapered the skin to a knife edge and a second version's self-crossing section deleted most of the cradle in the boolean (see the README lessons); both caught by the matrix before any print. |
| F2 | A14 bed-side recess | coil_former | the spool's back groove (0.55 deep, the wire pair's path to the lead hole) is on the bed face; under four layers a bed-side recess is squashed shut | groove 0.8 deep in a 2.0 mm flange (floor 1.2); +2 g per spool |
| F3 | A13 elephant's foot | disk_back L / R | the stalk bore's mouth relief was a 0.6 mm deep counterbore on the head (bed) face: it would vanish under the first-layer squash and the Ø20.6 bore would close to ~20.2 against the Ø20 stalk | a 45° entry cone, Ø22.6 at the face to Ø20.8 at 0.8 mm deep |
| F4 | A8 wall thickness | brow_center | the link screw counterbore (Ø6.2, 3 deep from the underside) broke out of the panel's back face: 0.58 mm of wall; moving the screw shallower made it 0.38 | the screw sits 7 mm along the 53° pocket (4.2 mm behind the back face) with a Ø6.0 counterbore: 1.2 mm of wall |
| F5 | A13 | sensor_bar | the carrier's 1.5 mm flush recess opens on the bed face; the first two layers squash its edge inward by 0.2 to 0.4 and the carrier would sit proud | a 0.4 × 0.4 step around the recess mouth (two layers, 0.4 wider) that the squash fills |
| F6 | A11 + A13 | fit_coupon_b | the cradle's port sockets open at the node tops, which are on the bed in its upside-down print; coupon A tests sockets that open upward, a different condition | a Ø8.3 socket that opens on the bed face, plus the pin-lock's 2.1 / 2.2 nail holes (the one fit no coupon covered) |
| F7 | A2 adhesion | rear_band_half | PETG, 36 mm tall on a 5 mm chamfered ridge (449 mm², 4 % of its box), no brim in its note | brim added to the print note; the spec's row 2 says so |
| F9 | A8 (a wedge side effect) | cradle_front, rear_band_half | the right rear node's harness-groove wedge reached down beside the tenon nail's head counterbore (0.25 mm apart in x, now overlapping in z): a 0.31 mm wall | the tenon nail moved 2 mm deeper into the node (8 mm from the rear face, `TENON_PIN_X`); the tenon is 14 mm deep, so 6 mm remain beyond the nail; the rear halves' nail holes follow the same constant |
| F8 | matrix itself | `print_matrix.py` | downward faces within 0.3 mm of the bed (a 0.05 mm modelling offset under the rail's bar, the first facet of a chamfer) were counted as 60 to 70° overhangs and flagged the rail, the rear half, the nexus and the pods | near-bed downward faces are their own bucket and not flagged |

Numbers that moved: cradle 8 h 01 → 8 h 10 (the tunnel skins and wedges), spool 1 h 40 → 1 h 51 and 19 → 21 g, disk back
unchanged, brow centre unchanged. Full set still about 105 h and 1.3 kg.


## 5. Accepted notes, part by part

Everything the matrix or the hand pass flags that stays as it is, with the reason. These are the rows a printer should
read before starting the part.

**Bed-edge fillets (A5, A13; belt pack and lid, pods and lids, nape base and cap, nexus, socket foot, pad plates, crown
foot, apex, pylon base).** `fillet()` rounds every edge including the ones on the bed, so the first layer sits 0.6 mm
inside the outline and the next three layers step outward. It prints; the edge is slightly ragged and the first layer is
a little smaller, and the rounding absorbs the elephant's foot. Left as is. Parts with a brim do not notice it.

**Near-bed offsets (A25; brow rails 0.05 mm, chamfered ribbon edges).** Modelling offsets under the first layer height.
The slicer swallows them.

**Lobe cusps (A8; nape body, cover, dial, key, core base: 0.17 to 0.36 mm).** The four-lobe nail slots and the rack
teeth are single lobed polygons whose adjacent lobes meet at a cusp; the audit reads the cusp wedge as a wall. Geometric,
not a print wall.

**Cover strips at 1.0 mm (A8; cover_bottom, cover_rear, cover_rear_in).** One-millimetre PETG strips by design, glued
over cables; 2.5 lines wide, printed on edge or flat. Not structural.

**Bay spool flange 1.2 (A8).** A 100 × 25 flat plate, six layers, no load.

**Dome blind-tap floors 1.0 (A8; disk_dome).** The six M3 tap holes end 1.0 mm before the boss tops; a floor, not a wall.

**Crown arch ribs 1.13 (A8).** The 45° chamfers of the cosmetic ridges on the arch's outer face meet at 1.13 mm. Cosmetic;
over the 0.8 mm cosmetic floor.

**Brow panel pocket mouth 0.45 (A16).** The 1.5 mm straight relief around each angled link pocket meets the pocket's 53°
wall in a wedge that tapers to zero; the audit samples it at 0.45. The slicer drops the sub-0.4 mm end of the wedge, which
is inside the pocket mouth and carries nothing.

**Sensor bar recess step reads 0.53 (A13).** That is the 0.4 mm elephant-foot step itself, intended.

**Pad plates 1.17 to 1.20 and pad_hub pillar walls 1.2 (A8).** Countersink rims 1.15 from the plate edge and the
bone-conduction seat's 1.2 mm walls, as designed in canon.

**bar_carrier 1.03, brow_lid 1.17, disk_back 1.20 (A8).** Thin plates with holes; the values are the rims between holes and
edges in 1.5 to 2 mm plates, above the 0.8 cosmetic floor, under no load.

**coupon B 1.00.** The loose ring's wall; a test piece.

**Tall standing prints (A4, A22; disk_dome 5.2, apex_block 5.2, port_coupler 3.8, cover strips on edge).** Brims as the
notes say; the dome at 0.16 mm layers, slower outer walls; the coupler and the strips print with a neighbour.

**Tiny parts (A10; bar_pin, knob_clip, cover_side, button caps, nape_retainer, visor_slider).** Layers under five seconds:
print them together on one plate so each layer cools, or with a sacrificial tower.

**Bed-face openings that are clearance holes (A13; nexus bolt holes, disk back screw holes and arc slot, pod mount holes,
lid countersinks).** Elephant's foot narrows them by 0.2 to 0.4 mm; all are clearance or countersink fits with more
margin than that, except the lid countersinks, whose screw heads will sit about 0.2 mm proud.

**Wedge grooves' knife-edge lip (A16; cradle spine runs and node grooves, rear-half channels).** The 45° wedge
meets the outer face at the groove's lower edge, so the skin between the slope and the face tapers to zero there; the audit
reads it at 0.5 mm. In the print the slicer drops the sub-0.4 mm end, which turns the groove's lower edge into a 0.4 to
0.8 mm rounded lip: a ledge under one millimetre, inside the rule. The cover strip and the epoxy hide it.

**The cradle's 4 % contact (A2).** Upside down it stands on the band's 5.4 mm top ridge, the node tops and the pin lugs:
1320 mm² under an 8 h PETG print. Brim, 80 °C bed, fan off for the first three layers, and the printer left alone.


## Sources for roster A

- Ultimaker, [Design for FFF 3D printing](https://ultimaker.com/learn/design-for-fff-3d-printing-maximize-your-success/): 45° overhangs, 10 mm bridges by default and 25 mm with tuned cooling.
- Protolabs Network (Hubs), [How to design parts for FDM 3D printing](https://www.hubs.com/knowledge-base/how-design-parts-fdm-3d-printing/): bridges, minimum features, hole compensation.
- Layer X, [FDM design rules](https://layerx3d.in/blog/fdm-design-rules-wall-thickness-overhangs-bridging-tolerances): structural walls ≥ 1.2 mm, bridge spans by material, hole compensation 0.2 to 0.4 mm.
- FacFox, [FDM design guideline](https://facfox.com/docs/kb/fdm-design-guideline) and [How to design parts for FDM](https://facfox.com/docs/kb/how-to-design-parts-for-fdm-3d-printing): minimum hole 1.0 mm vertical / 2.0 mm horizontal, pin sizes, first-layer squish.
- Ucuz3D, [Why do horizontal holes come out oval](https://www.ucuz3d.com/en/why-do-horizontal-holes-come-out-oval-achieving-exact/) and goodprints3d, [Why 3D printed holes come out too small](https://www.goodprints3d.com/blogs/3d/why-do-3d-printed-holes-come-out-too-small-and-how-do-you-fix-them): sag, teardrops, elephant's foot.
- Snapmaker, [How strong are 3D-printed parts](https://www.snapmaker.com/blog/how-strong-are-3d-printed-parts/) and the PET-G / PLA tensile study (PMC9230522): Z strength 40 to 75 % of XY.
- 3D Printerly, [How to fix PETG warping](https://3dprinterly.com/9-ways-how-to-fix-petg-warping-or-lifting-on-bed/) and Xometry, [3D print warping](https://www.xometry.com/resources/3d-printing/3d-print-warping-pla-petg-abs/): brims, fan off for the first layers, 70 to 85 °C beds, mouse ears.
- This project's lessons: `tools/blender/vp0/README.md`, print-readiness sections (bed-side recesses, symmetric tapers, expected-contact masking, teardrops, coplanar cutters).
