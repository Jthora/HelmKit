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
| Printed tolerances on this printer | a 0.3 mm clearance on paper is an interference on any FDM printer at worst case | P2 + coupons |
| Head fit on the real head | the phantom is a superellipsoid; the 8 h cradle print is the first real test otherwise | P3, the gauge |
| Strength with layer adhesion, not bulk strength | the stalk and pins load their layers in tension | P4 |
| Every part against a printability roster | the audit had reported a 290 mm ledge on the cradle as an area nobody read | P8, run 2026-09-15: [`../../mechanical/vp0_printability_matrix.md`](../../mechanical/vp0_printability_matrix.md) |
| The assembly sequence with real hands and tools | deadlocks were found twice on paper already | P5 |
| Materials against heat and preload | PLA under bolts in a hot car | P4 |
| Safety, as a written case | there was posture, not a case | P6, written 2026-09-13 |
| Electronics on the bench before the head | Track N gates were never run on hardware | P7 |

## 2. Printer and settings (fixed inputs)

QIDI X-Max 3: 325 × 325 × 315 mm, enclosed with a chamber heater (off for PLA and PETG), direct-drive extruder,
0.4 mm hardened-steel nozzle (the high-temperature hotend is what is installed; steel conducts a third as well as
brass, so `make_usb.py` adds 10 °C to every PETG and 5 °C to every PLA nozzle temperature, and the Z offset must be
recalibrated on the printer after any hotend change), textured PEI plate, Klipper; sliced in QIDI Studio (02.06.00.51 on this Mac) with its bundled
X 3 Series presets: printer `X-Max 3 0.4 nozzle`, process `0.20mm Standard @XMax3` (`0.16mm Optimal @XMax3` for the
dome), filament `Generic PLA @Qidi X-Max 3 0.4 nozzle` (220 / 210 first layer, bed 60, fan 100 %) and
`Generic PETG @Qidi X-Max 3 0.4 nozzle` at the spool's 220 °C from layer two (230 at the heater with the steel nozzle),
first layer 235 at the heater, 0.28 mm thick at 20 mm/s with 8 % less flow and a concentric bottom surface on an 85 °C
plate, chamber exhaust off (the stock PETG preset runs it at 100 % and it drafts the first layer) (coupon A, 2026-09-15: at 220 the first layer
did not wet the plate; at the PLA Z offset the lines rippled and were torn off, the PETG-too-close signature, so the PETG
projects raise the nozzle 0.04 mm through the filament start G-code: a lift after the purge line and a G92 that renames
the height, which the next print's G28 clears, so a cancelled print leaves nothing behind), flow cap lowered from 12
to 8 mm³/s for the cooler melt; bed 80 after the first layer, fan 40 to 90 %, first three layers fan off; retraction
1.25 mm at 35 mm/s, z-hop 0.2 (0.6 oozed onto the first-layer fill) and 2 mm minimum travel as filament overrides,
to be revised from the retraction tower). If a spool is QIDI's own, its named preset replaces the generic one. Overrides on every part: three walls, 5 / 4 shells, 20 % gyroid,
one skirt loop, supports off; per part: brim (5 mm; 8 mm for the dome), infill (cradle and nexus 40 %, spool 80 %, dome
15 %, pylon blades 12 %), supports on the dome (tree, 0.16 mm) and the gauge (build plate only). Every part fits the
plate with room to spare; the largest footprints are the cradle (176 × 200) and coupon A (183 × 89); the dome stands
122 mm tall on edge.

Materials: the prototype prints in PLA and PETG only. The printer can print the PAHT-CF and PC-CF spools on the shelf
(hardened nozzle, 350 °C hotend, chamber heater) and they wait for the beta: the prototype exists to find fit and
design errors cheaply, and a filled material hides in strength what PLA shows in cracks.

Correction (2026-09-15): sections 3 and 4 and the printability matrix were first written for a Creality Ender-3 V2
Neo, inferred from a Creality Slicer profile on this Mac; the project's own documents had named the X-Max 3 since
the topology-B plan. The P1 times below came from the Cura 4.8 engine at that printer's speeds and stand as upper
bounds; the mesh checks (zero slicer errors) and the masses (same walls and infill) carry over. QIDI Studio's own
figures for each part go into `helmkit/PRINT_LOG.md` as it is sliced.

Why the slicing is done in the app: QIDI Studio's command line loads flattened presets, arranges and exports a
project or the merged settings, but its slice step crashes in this build (a null option in the multi-filament
update, reproduced from its own exported project). `make_usb.py` therefore writes one QIDI Studio project per part
with everything embedded; Slice and Export G-code are two clicks in the app.

## 3. P1 result: every part through the real slicer

All 63 STLs sliced with zero engine errors (Cura 4.8 engine at Ender-class speeds; §2's correction). Figures for one of each part, upper bounds for the X-Max 3; the set needs some twice (rear halves,
nexus, disk backs, domes, crown halves, pylons, covers) and the spool four times.

| Part | Time | Filament | g PLA |
|---|---|---|---|
| cradle_front (PETG) | 8 h 09 | 32.9 m | 98 |
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
| coil_former (spool, each of four) | 1 h 51 | 7.1 m | 21 |
| crown_arch_half (each) | 1 h 40 | 7.3 m | 22 |
| band_gauge_front (build-plate supports) | 1 h 33 | 6.6 m | 20 |
| everything else (43 parts) | 15 h total | | 170 |

Totals: one of each part is 79 h and 966 g; the full print-one set with its duplicates is about 105 h and
1.3 kg; the combat trim alone (cradle, two rear halves, nape module, pad frames, sensor bar, carriers, pins,
covers) is about 22 h and 300 g. At eight attended printer hours a day the full set is two to three weeks; the combat trim is three days. These hours are the upper bound: the X-Max 3's presets run the walls at 200 to
300 mm/s against 30 to 50 in that pass, so expect roughly a third to a half of them, and the same grams. One failed
dome costs 95 g, five percent of the PLA on hand.

## 4. P2: the tolerance stack on this printer

Error budget for FDM at 0.4 / 0.2 before calibration (the X-Max 3, with pressure advance, a probed bed and the preset's 0.15 mm elephant's-foot compensation, sits at the good end of every range; the coupons decide): outer dimensions +0.05 to +0.20 mm;
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

Hours are the P1 upper bounds (§3); the X-Max 3 will be faster. Every step's gate is something that can fail cheaply. Nothing after step 1 prints until step 1's findings are in
canon.

## 11. The USB folder (the runbook)

`python3 tools/blender/vp0/make_usb.py` (after `blender --background --python tools/blender/vp0/make_usb_plates.py`
for the two small-parts plates) writes `helmkit/<colour>/<part>/` at the repo root, ignored by git: the STL in print
orientation, a QIDI Studio project (`<part>.3mf`) with the X-Max 3 printer, filament and process presets and the
part's overrides embedded, a `_settings.txt` that lists them for the sidebar check, and the generator's print note.
`helmkit/MANIFEST.md` lists every part with quantity, presets, budget hours and grams; `helmkit/PRINT_LOG.md` is the
log to keep, with the four-bin triage rule (slicer, fit, design, accept) and the coupon calibration table;
`helmkit/README.md` has the five steps. Copy `helmkit/` to the USB stick as it is. Slicing a part is: open the project
in QIDI Studio, check the three preset names against `_settings.txt`, Slice, Export G-code as `<part>.gcode` (or
Print over the network).

Colours, from the filament on hand and the grey / silver / black rule: silver PETG for every structural part
(cradle, rear halves, nexus pair, spools, knobs, sliders, cover strips, coupon A and one coupon B); matte grey PLA
for the visible shells (domes, brow centre and lid, sensor bar, crown, apex, pylons); black PLA for internals and
housings (nape module, pad frames, disk back plates, formers, pods, belt pack, small parts, the gauge, the second
coupon B). Coupon B prints in both materials because a coupon calibrates the material it is printed in. The
red, orange, white, transparent and blue spools are not used; the TPU waits for printed pads and grommets later;
the PAHT-CF and PC-CF spools wait for the beta (§2).

The presets in the script are the X-Max 3's own (§2); the common overrides are three walls, 5 / 4 shells, gyroid
20 %, one skirt loop, supports off, textured PEI plate; per part brim, infill and supports as the manifest lists. The
first coupon's first layer is the test of the pipeline itself; if a project opens with the wrong presets, set them
from the part's `_settings.txt`. At the printer: chamber heater off; PLA with the door ajar or the top vented, PETG
with the door closed.

## 12. Open inputs

- The filament actually loaded (brand: if a spool is QIDI's own, its named preset replaces the generic one in
  `make_usb.py`), and whether PETG has printed on this machine before: it decides whether the cradle is the first PETG print.
- Attended printer hours per day: it sets the calendar.
- The head measurements already on file (width 155, length 202.5, circumference 580) stand unless the gauge says
  otherwise.

## 13. Log: coupons E–G and the deep audit (2026-09-19/20)

- **Coupon E** (split bayonet boss, cap bonded): every stub entered, none turned. Probing the geometry: canon `BAYONET_CAM = (4.5, 3.8)` is inverted against lugs at n 4–7 (jams 20° in, 0.2 loose at the stop) and the groove ceiling (7.8) never reaches the lug top (7.0); the material above the groove exists only for the knob-lock notch. Retired.
- **Coupon F** (cam corrected, ladder 3.9 / 4.0 / 4.1 / 4.2): every combination jammed within 15° of the notch. Every bearing face sat on a slice plane and the lug shelf sagged; the printed lug bottom was ~3.6–3.8 above the flange, not 4.0. Retired.
- **Coupon G** (every bearing face on a 0.2 layer, floors 3.2 → 3.4 / 3.6 / 3.8, elephant-foot relief on, chamfered lugs, stub A with 0.4 less reach): printed 2026-09-20 and it turned, which measured four faults at once. (1) From each slot the lug could turn the wrong way 29° onto the flat tail of the other sector's entry floor and stop at the back of its bump as if locked: the only turns that "worked" were these, in the 3.6 and 3.8 collars. (2) The Ø20 stalk in a bore printing ~20.25 was a friction fit: it held the flange up, read as snug with the lug floating 0.8 above the floor, and turned stiff or not at all collar to collar. (3) The full-reach lug would not enter some slots (0.6 radial prints ~0.2). (4) Nothing climbed the ramp, and the cause was a fifth fault that Jordan caught: the stubs' identification pips stood on the flange's TOP face, the face that seats on the collar, 0.5 mm proud, so every stub sat 0.5 off the collar with its lug at 3.5 instead of 4.0, below every riser (also stub A on F). Marks never go on a seating face again. Retired.
- **Coupon H** (reverse block behind each slot, bore Ø21.0, slot clearance 1.0, both stubs reach 2.6, 45° lead-in chamfers on stub A's lug with B as the control, marks on the stalk's free end, floors 3.2 flat as a cam-free control / 3.6 / 3.8): printed 2026-09-20. **Floor 3.8 seats both stubs snug-tight; 3.2 and 3.6 turn loose.** The lead-in chamfer made no difference, so it is not carried. Applied to canon the same day: `BAYONET_CAM (3.2, 3.8)`, `BAYONET_BOSS 7.6` open, `BAYONET_BORE_CLEAR 0.5`, `BAYONET_NOTCH_CLEAR 1.1` (beyond the lug: slot to r 13.7), `STALK_LUG` reach 2.6 + `STALK_LUG_CHAMFER 1.4` (the nexus lugs rebuilt as the coupon's stubs), reverse block, layer asserts; `bayonet_cuts` defaults are now canon and the retired coupons pin `LEGACY`. Coupons A, B, D2, H leave the print set; d1 remains. `bayonet_cuts` gained `bore_clear`, `notch_clear` and `reverse_block`; defaults still reproduce canon.
- **Deep audit v2** (`print_deep.py`): bridges vs cantilevers vs islands with drop and location, bed levels, contact as % of footprint. Before fixes 24 of 70 parts flagged; after them the two-level bed-face class (cradle, rear band, crown arch, brow rail, nape cover, plus the rails' quarter-layer) is gone, the dome's perch is gone (134 → 2335 mm²), the brow rail's lap cantilever is gone (382 → 80 mm²). 17 remain flagged, all designed-for, accepted with clearance, 20–26 mm bridges, or under 50 mm². Rules 1, 3, 4, 5 in the spec §6.1.
- **Pending:** the knob lock. With the roof gone `BAYONET_LOCK`'s notch has no host: the disk is held by the cam's preload and the stop bump, and the knob's eccentric pushes its pin into air. Proposed: grow the stop bump into a post to 14.5 carrying the notch (no overhang: it stands on the plate), and put the nexus pin at the plate-frame angle that meets it after the turn (the pin's world angle then differs L/R, so it is defined in the lug frame, not `pin_world_deg`). Needs a coupon with a nail as the pin. Then print d1 (cradle gate) → cradle.
