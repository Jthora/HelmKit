# Track P — Print to completion: the one-shot campaign

**Status:** `scoped + P1 run` (2026-09-13). One printer, one shot at the material, no second helm if the first set fails.
This track is the set of deep investigations that have to close before the large parts print, the order the parts
print in so that every expensive print is gated by a cheap one, and the safety case that governs the first wear.
Companion to [track-N-capability-robustness.md](track-N-capability-robustness.md) (firmware) and
[`../../safety_case_vp0.md`](../../safety_case_vp0.md) (hazards). The mechanical spec is
[`../../mechanical/vp0_visual_prototype.md`](../../mechanical/vp0_visual_prototype.md).

## 1. What "not good enough" means, concretely

What has been verified so far is geometry: exact booleans, clearances against a head phantom, collisions between
parts, thin walls, overhangs, and a home-made print audit. What has not been verified is everything that decides
whether the first print survives contact with the world:

| Unverified until now | Why it can sink a one-shot build | Deep run |
|---|---|---|
| The real slicer's view of every part | our audit is not the slicer; the slicer is what the printer obeys | P1, run 2026-09-13 |
| Printed tolerances on this printer | a 0.3 mm clearance on paper is an interference on an Ender at worst case | P2 + coupons |
| Head fit on the real head | the phantom is a superellipsoid; the 8 h cradle print is the first real test otherwise | P3, the gauge |
| Strength with layer adhesion, not bulk strength | the stalk and pins load their layers in tension | P4 |
| The assembly sequence with real hands and tools | deadlocks were found twice on paper already | P5 |
| Materials against heat and preload | PLA under bolts in a hot car | P4 |
| Safety, as a written case | there was posture, not a case | P6, written 2026-09-13 |
| Electronics on the bench before the head | Track N gates were never run on hardware | P7 |

## 2. Printer and settings (fixed inputs)

Creality Ender-3 V2 Neo: 220 × 220 × 250 mm, 0.4 mm nozzle, 1.75 mm filament, Creality Slicer 4.8 (Cura engine
4.8.2). Every part in the set fits the bed; the largest footprints are the cradle (176 × 200) and coupon A
(183 × 89); the dome stands 122 mm tall on edge. Settings used for every figure in this document: 0.2 mm layers,
20 % infill, skirt, supports only where the sidecar note asks for them (the dome). PLA at the slicer's defaults;
PETG parts at the printer's PETG profile when printed.

The command line that produced the figures (the app's engine, no GUI):

```bash
R="/Applications/Creality Slicer.app/Contents/Resources/resources"
E="/Applications/Creality Slicer.app/Contents/MacOS/CuraEngine"
export CURA_ENGINE_SEARCH_PATH="$R/definitions:$R/extruders"
"$E" slice -v -p -j "$R/definitions/creality_ender3v2neo.def.json" -e0 -j "$R/extruders/creality_base_extruder_0.def.json" \
     -s layer_height=0.2 -s infill_sparse_density=20 -s adhesion_type=skirt -s support_enable=false \
     -l part.stl -o part.gcode
```

Read the time and filament from the engine's "Gcode header after slicing" lines; the header inside the gcode is
not filled by the command-line engine.

## 3. P1 result: every part through the real slicer

All 63 STLs sliced with zero engine errors. Figures for one of each part; the set needs some twice (rear halves,
nexus, disk backs, domes, crown halves, pylons, covers) and the spool four times.

| Part | Time | Filament | g PLA |
|---|---|---|---|
| cradle_front (PETG) | 8 h 01 | 32.9 m | 98 |
| disk_dome (with interior supports) | 7 h 18 | 31.8 m | 95 |
| belt_pack | 5 h 17 | 20.8 m | 62 |
| brow_center | 4 h 46 | 20.1 m | 60 |
| fit_coupon (A) | 4 h 14 | 17.6 m | 53 |
| fit_coupon_b | 4 h 00 | 17.3 m | 52 |
| nape_core_base | 2 h 41 | 10.4 m | 31 |
| disk_back L / R (each) | 2 h 23 | 9.4 m | 28 |
| sensor_bar | 2 h 19 | 9.7 m | 29 |
| nexus L / R (each, PETG) | 2 h 05 | 9.4 m | 28 |
| rear_band_half (each, PETG) | 1 h 54 | 8.0 m | 24 |
| coil_former (spool, each of four) | 1 h 40 | 6.4 m | 19 |
| crown_arch_half (each) | 1 h 40 | 7.3 m | 22 |
| band_gauge_front (build-plate supports) | 1 h 33 | 6.6 m | 20 |
| everything else (43 parts) | 15 h total | | 170 |

Totals: one of each part is 79 h and 966 g; the full print-one set with its duplicates is about 105 h and
1.3 kg; the combat trim alone (cradle, two rear halves, nape module, pad frames, sensor bar, carriers, pins,
covers) is about 22 h and 300 g. At eight attended printer hours a day the full set is two to three weeks; the
combat trim is three days. One failed dome costs 95 g, five percent of the PLA on hand.

## 4. P2: the tolerance stack on this printer

Error budget for an Ender-class printer at 0.4 / 0.2, before calibration: outer dimensions +0.05 to +0.20 mm;
vertical holes 0.2 to 0.4 mm under size; horizontal holes a further 0.2 to 0.5 under at the top from sag (the
teardrops exist for this); elephant's foot +0.2 to +0.4 on the first two layers; printed pegs +0.1 to +0.2.

| Fit | Nominal clearance | Worst printed clearance | Verdict | Where it is tested | Knob in canon if it fails |
|---|---|---|---|---|---|
| port peg Ø8 in vertical socket 8.3 | 0.30 | −0.20 | interference likely | coupon A | `CYL_SOCKET_D` +0.2 |
| crown foot socket, horizontal, 8.5 | 0.50 | 0.00 | marginal | coupon A (stub) | `CROWN_FOOT_SOCKET_D` |
| stalk Ø20 in the bayonet boss, lug 6 × 3 in the 4.0 groove | 0.2 preload after the cam, +0.1 sag allowance | may bind at the stop | needs the coupon | coupon A bayonet stub | `BAYONET_GROOVE`, `BAYONET_CAM` |
| lock pin: 3.2 nail in a 3.4 round horizontal hole | 0.20 | −0.30 | will not enter without the 3.5 drill | coupon B (round vs teardrop 3.4) | drill pass in the assembly step |
| knob shaft 7.6 in the stalk bore 8.2 | 0.60 | +0.20 | fine | coupon B stalk stub | none |
| nexus nut pocket 5.7 across flats, sideways, for a 5.5 nut | 0.20 | −0.10 | tight; press fit at best | coupon B | `NEXUS_NUT_POCKET` 5.9 |
| visor ring ID 36.3 on the 36.0 hub | 0.30 | −0.20 | seizes | coupon B ring | `NEXUS_RING` ID 36.6 |
| bar pins Ø4 printed, in 4.1 (band) / 4.3 (bar) | 0.10 / 0.30 | −0.40 / −0.20 | interference both | coupon B pin sockets | `SENSOR_BAR pin_fit` (0.3, 0.5) |
| nape pin-lock: 2 mm nail in 2.1 snug / 2.2 clear | 0.10 / 0.20 | −0.30 | will not enter | coupon B (added 2026-09-13: vertical 2.1 / 2.2 holes) | a 2.0 mm drill pass; the 0.6 entry relief |
| M3 thread-forming in 2.5 tap holes | designed | 2.2 to 2.3 printed | forms but hard | coupon A hole gauges | 2.5 mm drill pass |
| DIN 965 M3 head in a 5.6 countersink | 0.10 | head 0.3 proud | acceptable under foam | pad plates | `PAD_FRAME countersink` 5.8 |
| tenon in the rear node slot, 3.2 nail through | designed | slot 0.2 to 0.3 tight | glue joint anyway | first rear half | tenon clearance in canon |
| spool stack 9.6 + 0.2 + 5 mm foam in the 12 mm cavity | foam compresses to 2.2 | fine | fine | assembly | `COIL_FORMER foam_ring` |

Reading the table: six fits are expected to fail at worst case before calibration, and every one of them is now on
a coupon. The coupons are therefore not optional and not a formality:
the campaign's first day is coupons A and B, and their findings become a calibration table that sets the canon
offsets before any large part is generated again. That table lives in the spec's §7 once measured.

## 5. P3: head fit before the cradle

`band_gauge_front` is the bottom 3 mm of the band as a plain 7 mm wide ribbon along the cradle's centreline, its
lower edge on the band's real bottom edge everywhere (the forehead rise included), in an hour and a half and 20 g
instead of eight hours and 98 g. Two earlier versions cut the real cradle to a slab and both left slivers and
coplanar faces from the grooves and bores; the ribbon has nothing to leave. It prints flat with build-plate
supports under the rise. Worn on the head, it answers the two questions the phantom cannot: does the inner face
touch at the temples, and does the lower edge clear the ear tops by 4 mm with the band level. A fail moves
`HEAD_W` / `HEAD_L` in canon and costs ninety minutes, not a day.

## 6. P4: strength and materials with layer adhesion

To be run before the nexus prints. Re-run the 100 N rim-hit load path with layer-adhesion strength (half to two
thirds of in-plane), decide the factor of safety on the stalk and the bolt group, and confirm the material column:
PETG for everything that carries preload or a load path (cradle, rear halves, nexus, spool, covers, knobs),
PLA for shells and pods, no PLA part under bolt preload in a hot car. The disk stays off the head in any trim worn
near a partner regardless of the number.

## 7. P5: the assembly dry run on paper, then on the bench

Every step of the spec's assembly order walked with the tools in hand: screw lengths against the stacks, nail
cutting, epoxy cure times, cable pulling order, and which steps are irreversible. Output: a printed checklist with
one row per fastener and one photograph per step for the build log.

## 8. P6: the safety case

Written 2026-09-13: [`../../safety_case_vp0.md`](../../safety_case_vp0.md). Its first rule is that nothing on the
head emits energy at the first wear; its coil section fixes a hard current limit of 0.2 A and a frequency limit of
400 Hz for any driver that is ever built, with the reference-level table and the field-model numbers that justify
them. It names a check for every control.

## 9. P7: electronics on the bench before the head

The Track N bench checklist, run in full with the board on the desk, before any sensor is on the pads. The first
capture through `tools/capture_service.py` becomes the golden fixture for the equivalence gate.

## 10. The print order, gated

| Step | Prints | Hours | Gate to pass before the next step |
|---|---|---|---|
| 1 | coupon A, coupon B, band gauge | 10 | fit findings recorded; calibration offsets set in canon; gauge fits the head |
| 2 | regenerate the set from the calibrated canon | 0 | assembly re-run: 0 unexpected overlaps |
| 3 | cradle (PETG), two rear halves (PETG), nape module, pad frames, covers | 20 | first wear per the safety case §7: 30 min moving, no pressure points |
| 4 | sensor bar, carriers, pins, bottom covers | 3 | combat trim complete; headgear fit M-G1 |
| 5 | electronics on the bench (Track N checklist), then on the head with the belt pack | 0 | gates N-G1..G4; first scored session |
| 6 | nexus pair, spool, disk backs, knobs, clips | 11 | bayonet lock engages and holds; stalk fit |
| 7 | one dome | 7 | on-edge print survives; plate seats; only then the second dome |
| 8 | brow centre, lid, rails, links; crown arches, apex; pylons | 17 | visor pawl and links work on the bench |
| 9 | pods, belt pack, four spools | 14 | electronics core option chosen from the three |

Every step's gate is something that can fail cheaply. Nothing after step 1 prints until step 1's findings are in
canon.

## 11. Open inputs

- The filament actually loaded (brand, PLA and PETG temperatures the printer has worked at), and whether PETG has
  printed on this machine before: it decides whether the cradle is the first PETG print.
- Attended printer hours per day: it sets the calendar.
- The head measurements already on file (width 155, length 202.5, circumference 580) stand unless the gauge says
  otherwise.
