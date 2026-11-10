# `tools/blender/vp0/` — HelmKit visual prototype (clean-slate part set)

Current revision: **vp0.11** (2026-09-05). Spec, print order and BOM:
[`docs/mechanical/vp0_visual_prototype.md`](../../../docs/mechanical/vp0_visual_prototype.md).
Earlier revisions are archived in `archive_v01/` … `archive_v08/`.

## Files

| File | Role |
|---|---|
| `canon.py` | Every number: wearer measurements, disk + bayonet + lock boss, cylinder port standard, cradle nodes / lug / sockets, nexus, captive pin, crown, brow rails and tabs, pylons, rear halves, nape modules, foam, pad frames, sensor bar, cable channel, headgear fit rule. `python3 canon.py` prints a summary. |
| `vp0lib.py` | Mesh helpers: revolve, cones (countersinks), teardrop holes and L/R notches (v0.17), chamfered ribbon sweep, centripetal Catmull-Rom, CDT-triangulated polygon extrusion, involute gear / rack / sawtooth / ridge / serration profiles, fillet pass, EXACT booleans, BVH overlap, mass properties, print-orientation export.; `bed_plane(ob, print_rot, depth)` cuts the bed face to ONE plane after the last union (Track P: the generators' 0.1-0.2 boolean-safety offsets became steps in the bed face) |
| `build_disk.py` | Enclosed disk: dome shell with screw bosses, apex knob dish + boss, rim print flat and unlock mark, PRINTED SADDLE for the on-edge print (92 x 30 plate, six fins necked to the rim; snap off); L and R back plates with the OPEN cam bayonet groove (Track P coupon H: floor 3.2 -> 3.8, Ø21 bore, slot 1.1 beyond the lug, reverse block, wall 7.6; lofted ring), the lock notch and the cable hole (`--out-dir`). `bayonet_boss()` / `bayonet_cuts()` are shared with the coupon |
| `build_nexus.py` | The NEXUS (PETG): L and R Ø68 flanges (hollow filleted stalk with the lock-pin hole, coil-cable bore, lanyard hole, head counterbores); spool with the notched hub and the spacer block; disk knob (shaft + eccentric); knob clip (`--out-dir`) |
| `build_cradle_front.py` | Cradle U: 7 mm forehead + side band (lower edge rises at the forehead) with spine channels between the nodes, hub nodes (nexus bolt holes + inner-face nut pockets, arch socket, coil bore), LED bores, rear nodes (tenon socket, pylon socket), strap slots, pad-frame taps, sensor-bar pin sockets, and the v0.13 bottom-face cable channel with its groove up to the LED bore (×1, PETG). Exact-arc helpers `front_run` / `arc_span` / `arc_point` / `s_at_x` are shared with the pad and bar builders |
| `build_crown_arch_half.py` | 20 × 7 arch half with a socketed foot over the hub node (coupler) (×2, same STL) |
| `build_apex_block.py` | Apex sleeve with M4 clamp |
| `build_brow_center.py`, `build_brow_rail.py`, `build_brow_link.py`, `build_visor_slider.py`, `build_brow_lid.py` | 160 mm centre panel with back-face link pockets and a front faceplate recess; rails with their Ø44 rings, gusseted bar, pawl tunnel, half-lap and underside cable groove (`--mirror`); links (lap + 55° bar; `--mirror`); pawl slider; faceplate |
| `build_rear_band_half.py` | Rear half: one-sided tapered tenon into the rear node, strap slots, spine channel, inner harness channel (v0.15), phased rack (×2, same STL, PETG; the right half is the left print flipped over, which is why the pin-lock has an upper and a lower tunnel) |
| `build_spine_covers.py` | Flush cover strips for the spine channels: front arc half, side span, rear half; the rear half's inner harness cover (`--out-dir`) |
| `build_nape_dial.py` | Nape modules: `nape_pinlock` (print one; four-lobe nail slot, prints standing) and the enclosed PULL dial set: body (ratchet ring), cover (window), lid, dial, key cap, pinion, retainer with M5 nut pocket (`--out-dir`) |
| `build_pylon.py` | Antenna pylon: pegged base with a serrated clevis, faceted blade, lock knob (`--out-dir`) |
| `build_port_parts.py` | Cylinder port spares: plug, flush plug (combat trim), coupler, drill guide (`--out-dir`) |
| `build_pad_frames.py` | v0.12 pad frames under the foam (both trims): curved forehead plate with three carrier windows + the PPG and EDA carriers, hub plates (bone-conduction seat, coil-cable hole, cross-bolt clearance), rear plates (MAX30205 pillar); `foam_refs()` and `carrier_in_place()` for the assembly (`--out-dir`) |
| `build_nape_core.py` | v0.15 electronics core: the nape core base (pin-lock block + junction bay: web harness holes, junction posts, umbilical window with zip-tie slots, jumper window, pod bosses), its cap, the nape pod and the slab pod with lids (tact-switch pockets, OLED and USB windows, slide-switch slot), the socket foot (port-standard peg), button caps; placement matrices for the assembly (`--out-dir`) |
| `build_belt_pack.py` | v0.15 belt pack box + lid: corner bosses, belt slots, umbilical hole with zip-tie slots, USB window (`--out-dir`) |
| `build_coil_former.py` | v0.17 spool formers: the disk spool (Ø109.4 × 1.8 flange, Ø44 × 3 hub, six boss holes, solder-pad boss, back-face lead groove, lead hole over the plate's arc slot, two stacked per disk) and the visor-bay spool; the v0.15 spiral former stays selectable (`COIL_FORMER["style"]`). |
| `build_sensor_bar.py` | v0.12 combat-trim sensor bar: hollow curved brow bar on the band's front face with the floor window + flush recess, the sensor carrier (thermopile, camera, IR LEDs), LED lane, pin sockets; the Ø4 shear pins (`--out-dir`) |
| `build_fit_coupon.py` | Print-first tolerance coupon A: hole gauges, port, bayonet boss + stub, ratchet pair |
| `build_fit_coupon_h.py` | Track P coupon H. Coupon G turned and measured four faults: the lug could turn the wrong way onto the other sector's entry floor (a reverse block now fills it), the Ø20 stalk was a friction fit in a bore printing ~20.25 (bore Ø21.0), the full-reach lug would not enter a slot printing ~0.2 clear (slot +0.4, reach 2.6), and a square-edged lug cannot climb the cam's 0.2 mm layer steps (45-deg lead-in chamfers on stub A; B is the control). Floors 3.2 flat (control) / 3.4 / 3.6. `bayonet_cuts` gained `bore_clear`, `notch_clear`, `reverse_block`, defaults still canon |
| `build_fit_coupon_g.py` | Track P coupon G: the bayonet with PRINTER-SIZED clearances. Coupon F failed on every combination because its bearing faces sat on slice planes (0.1 steps at 0.2 layers) and the lug shelf sagged. G puts every bearing face on a layer boundary (asserted at import), floors 3.2 -> 3.4 / 3.6 / 3.8 under a 4.0 lug, elephant-foot relief on, chamfered lugs, one stub with 0.4 less reach. Preload becomes a washer, not a dimension |
| `build_fit_coupon_f.py` | Track P coupon F: the bayonet CAM corrected. Coupon E proved the then-canon cam (4.5, 3.8) was upside down against lugs at n 4..7 (jams 20 deg in, loose at the stop) and that the groove ceiling never touches the lug. Four open-top bosses with the floor rising 3.5 -> 3.9 / 4.0 / 4.1 / 4.2, no cap, no lock notch; two stubs, one with a 45-deg chamfer under the lug. Uses `bayonet_cuts(cam=, open_top=, lock=)`, whose defaults still reproduce canon |
| `build_fit_coupon_e.py` | Track P coupon E: the SPLIT bayonet boss. The one-piece boss retains its groove with a 3.3 mm annular roof printed in mid air; this cuts the boss at the groove ceiling into a base (groove open upward, zero overhang) and a bonded cap ring, both sliced from the EXISTING boss geometry so nothing is re-derived. Plus three under-size stubs |
| `build_fit_coupon_d.py` | Track P coupon D (`--out-dir`, emits d1 + d2): the bracketing coupons. Ladders for every fit that failed on 2026-09-16 (pin-lock, M3 tap/clear, M4, sensor pins), horizontal round-vs-teardrop pairs, three Ø8 sockets opening UP and four opening on the BED face, a peg on a sacrificial foot, one bayonet boss with three under-size stubs, three ring bores on the Ø36 hub, and coupon C's ratchet pair. One print brackets every answer |
| `build_fit_coupon_c.py` | Track P coupon C: the nape ratchet on its own (base ring + centring spigot, loose dial at the real 34 x 5 with a flatted grip); coupon A's pair cannot be engaged on the printed plate. Decides `NAPE_RATCHET_DIR` |
| `build_fit_coupon_b.py` | v0.17 coupon B: horizontal hole row (round vs teardrop), sideways nut pocket, hub + ring, stalk with the lock-pin hole, bar pin sockets |
| `make_usb.py` | Track P: builds the USB print folder `helmkit/<colour>/<part>/` for the QIDI X-Max 3: STL, a QIDI Studio project (`.3mf`) with the X-Max 3 presets and the part's overrides embedded (written by QIDI Studio's own command line from flattened bundled presets; its slice step crashes in build 02.06.00.51, so Slice and Export G-code happen in the app), settings sheet, notes, plus MANIFEST.md, PRINT_LOG.md and README.md; `make_usb_plates.py` first builds the two small-parts plates |
| `build_band_gauge.py` | Track P head-fit gauge: the bottom 3 mm of the band as a 7 mm ribbon along the centreline (about 1.5 h with supports against the cradle's eight) |
| `gcode_check.py` | Track P: reads the EXPORTED G-CODE layer by layer (height, filament, travel, longest travel, separate extrusion runs, retractions, z-hops, shortest run, feature types). Two files compares them side by side, which is how a part that printed is read against one that failed. Needs no printer, filament or USB |
| `print_deep.py` | Track P deep audit (v2, 2026-09-20): for every steep downward face, the drop to whatever is beneath and four horizontal rays classify it as a BRIDGE (both sides within 20 mm, span the short way), a CANTILEVER (one side) or an ISLAND; bed contact within one layer and as % of the footprint; bed LEVELS (a bed face in two planes is a slicer trap: the first slice plane cuts through it). Flags PERCH / CANTILEVER / CLIFF / LONGBRIDGE / ISLAND / LEVELS. Writes `docs/mechanical/vp0_deep_audit.md`. It does not know which overhangs have supports designed for them (the dome crown, the gauge) |
| `layer_islands.py` | The slicer's "floating regions" check done the slicer's way: slices the print-oriented STL at every layer and reports each section loop with no overlap on the layer below (where it starts, how big, how many layers it floats). print_deep reasons from faces and cannot see a sliver that begins in mid air next to solid material; this can. Found the cradle's node-groove wedge flake (0.5 mm², one layer) that tripped QIDI Studio's warning |
| `slice_layers.py` + `qidi_support_check.py` | QIDI Studio's own "floating cantilever" test, reproduced from its source: per-layer outlines (Blender), then the overhang / contour / 3 mm / 6 mm rule on a 0.05 mm raster (system Python: numpy, scipy, Pillow). Found the cradle's front spine-run lip that three approximations had passed. Run it on any part before slicing |
| `build_first_layers.py` | A first-layer test for a big, low-contact part: the bottom 0.6 mm of its print-oriented STL, printed with the part's own settings and brim, so adhesion across the whole footprint is proven in minutes. `cradle_front_first_layers` is in the print set, to print before the cradle |
| `print_check.py` | Audit of every exported STL in print orientation: bed contact, flat overhang / bridge area, 45..70 deg overhang, thinnest wall (inward ray cast from every face); flags wrong-way-up parts and walls under 1.2 mm |
| `assemble_vp0.py` | Builds everything (nape parts per `NAPE_MODULE`; right pylons as rotated copies of the left print; pad frames with the foam on them) + reference coil / nails / springs / head + EAR phantoms, plus check-only objects (rails in the parked pose, cable runs); writes clearance (head + ears), mass, collision (worn + parked + cables) and snag reports, renders, saves `3D-Models/HelmKit_vp0/vp0_assembly.blend`. `--trim combat` builds the cradle + pads + sensor bar + flush plugs only, adds the headgear phantom, the bar cable routes as check-only objects, and writes `fit.txt` (the 20 mm sparring rule, bar excepted; overlaps with the headgear shell), saves `vp0_assembly_combat.blend`. `--core nape|slab|none` picks the electronics core (nape pod on the base, two slab pods on the rear sockets, or belt-only with the cap) and the mass report adds the electronics as reference masses |

## Regenerate everything

```sh
B=/Applications/Blender.app/Contents/MacOS/Blender   # linux: B=blender
OUT=3D-Models/HelmKit/_generated/vp0
for p in fit_coupon fit_coupon_b fit_coupon_c fit_coupon_e fit_coupon_f fit_coupon_g fit_coupon_h cradle_front rear_band_half crown_arch_half apex_block brow_center brow_lid visor_slider; do   # band_gauge uses --out-dir below
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/$p.stl
done
for p in brow_rail brow_link; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/${p}_L.stl
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/${p}_R.stl --mirror
done
for p in disk nexus nape_dial pylon fit_coupon_d port_parts spine_covers pad_frames sensor_bar nape_core belt_pack coil_former band_gauge; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out-dir $OUT
done
$B --background --python tools/blender/vp0/print_check.py -- $OUT
$B --background --python tools/blender/vp0/assemble_vp0.py -- --out $OUT/renders   # ~10 min with renders
$B --background --python tools/blender/vp0/assemble_vp0.py -- --out $OUT/renders_combat --trim combat   # combat trim + fit report
$B --background --python tools/blender/vp0/assemble_vp0.py -- --out $OUT/val --trim combat --core slab --no-render   # or --core none: the other two electronics options
```

Each STL is exported in its print orientation with a `.txt` sidecar (bbox, mass,
manifold check, notes). Output is `.gitignore`d; the `.blend` is tracked.

## Working in the Blender UI

Open `3D-Models/HelmKit_vp0/vp0_assembly.blend`. 1 unit = 1 mm. Collections:
Cradle (with Nape and the spine covers), Disks.L/R (dome, back, nexus, spool, disk knob, clip), Crown (arches, couplers, apex), Brow (panel, rails with rings, links, sliders, faceplate),
AddOns (pylons), Checks (parked rails, cable runs; not printed), Reference (foam, coil, lock pins, pawl springs, rope, head, ears; not printed), PrintLayout (hidden). The `README_vp0` text block explains the edit → export
workflow. Re-running `assemble_vp0.py` overwrites the file.

## Boolean and print hygiene (Blender 5.0 EXACT solver)

- Revolves, never cylinder primitives, for anything a serration or ridge is unioned onto.
- Polygon extrusions triangulate their caps with a constrained Delaunay (ear clipping emits zero-area triangles on collinear outlines such as rack roots).
- No two bodies share a face plane or a tangent line: offsets of 0.1 mm everywhere it matters.
- Ribbons use centripetal Catmull-Rom (uniform loops back on itself at uneven waypoints) and a chamfered section.
- `fillet()` runs the bevel modifier and reverts itself if the result is not manifold; call it after every cut, never before one. Ribbons get their rounding from `chamfer=` instead.
- Ridge and serration valleys sit 0.1 mm below their host face; a vertex exactly on a face is a non-manifold edge waiting to happen.
- Resample spline centrelines to uniform arc length (`resample_polyline`) before sweeping; bunched stations make sliver quads the solver cannot cut.
- Coaxial cuts (pin hole + counterbore) go counterbore first; give them different vertex counts.
- `finalize_and_export` warns on any non-manifold edge; treat that as a failed build.
- Serration rings must sit entirely inside their host face (no overhang past an edge) and use an odd phase (`phase_ear` 7.9°, `phase_tongue` 0.4°) so no tooth vertex lands on a mesh line.
- Revolve segment counts vs cutter vertex counts matter: the Ø34 dial needs 100 segments against its 24-tooth ring.
- `clean()` must not recalculate normals: a sealed cavity would flip outward and double the volume. Mirrors use `reverse_faces`.
- Boolean ORDER matters even without coincidences: on the crown arch the apex ridges are unioned before the foot; on the cradle the strap slots are cut first and the nexus bolt holes go in as one combined tool per side. When a step fails, try it earlier.
- Two coaxial cutters/revolves with different vertex counts still share radial lines wherever `phase_a + step_a*k == phase_b + step_b*j`; pick phases so the difference is never a multiple of the steps' common resolution (disk back: bore 72 verts @1.3°, groove 100 @2.37°, plate 120 @0°, boss 100 @0°). Features that must survive inside a groove are carved out of the groove TOOL, not unioned afterwards.
- Coaxial cutters on a revolve (bore, groove, hole circles) get an odd rotation about the axis (`rot(1.3)` etc.) so no cutter vertex sits on a radial line; use annulus revolves, not full discs, where the centre gets bored anyway; and no bevel pass on such a plate before the bore.
- Anything that protrudes from a part's bed face lifts the whole part off the bed: `print_check.py` shows it as a tiny bed contact and a huge flat overhang (the v0.9 disk lock boss moved to the cavity side for this reason).
- Overlapping holes (the pin-lock's 2.2 mm holes 1.96 mm apart) are NOT fine as separate cylinder cuts (142 non-manifold edges): cut them as one lobed polygon extrusion (`lobed_poly`). Check the physical waist (1.0 mm here, so a 2 mm nail stays in its lobe).
- Two boxes that touch on a face (the cap's shroud walls) leave non-manifold edges after the union: make such shapes one polygon extrusion (a U), inset 0.2 from the plate they sit on.
- A profile that varies with angle (the bayonet cam groove) is a `loft_ring`, not a revolve; the same phase rules apply.
- Build the disc + tab of the spool as one CDT polygon: two 1 mm plates sharing both faces cannot be unioned.
- A hole that ends just inside a slanted edge leaves a sliver (rail index holes through the gusset): either pass all the way through or keep holes off the feature; the thin-wall scan in `print_check.py` finds these.
- Overlapping-lobe slots and involute tooth tips show up in the thin-wall scan as sub-millimetre walls: they are cusps, not walls.
- An angled pocket meeting a flat face leaves a knife-edge lip at the acute side: cut a straight mouth relief around it, slightly taller than the pocket so the two cutters share no plane.
- Two counterbores closer than their diameter merge into one; two holes and a slot end that touch leave zero walls. Space fasteners by at least their head diameter plus 1.5 mm.
- A box that fills part of a filleted body must carry the same fillet, or its corners poke through the rounding as 0.3 mm slivers.
- Cable placeholders are check objects: any pair they hit that is not in the expected set is a real routing conflict, so keep the expected set honest.

### Print-readiness lessons (v0.14)

- A shallow recess on the face that prints on the bed does not exist after slicing: the first layers bridge it and droop onto the bed (the nexus flange's 0.5 mm spool pocket). Put locating recesses on the top face or make them through-holes.
- Symmetric tapers on a tenon always put one face at a shallow overhang; taper one side only and keep the straight face on the bed side of the print.
- A shallow dome (sag 10 on Ø122) is within 19° of vertical everywhere when printed on edge and needs support over its whole interior when printed rim-down. Cut a 0.15 mm flat at the rim for a real first layer.
- Countersinks and counterbores need their full diameter plus a wall inside the part's outline: a Ø5.6 countersink 3 mm from an edge breaks out.
- Give a cone cutter's narrow end 0.1 mm more than the hole it meets so the solver never sees two coincident cylinders.
- Expected-contact pairs in the collision report can hide real interference (the pawl tip against the un-notched hub): when a pair is expected, read the face count and the location, not just the flag.
- Fastener tips: count the stack (counterbore floor to nut face) against the bolt length and relieve whatever the last 0.5 mm lands on.
- A rotation you write as a number is a claim; derive it from the geometry that limits it. The bayonet's "98° past the pin" ignored that a 6 mm lug spans 30° of an 11.5 mm radius and the stop bump 14°: the real travel was 76° and the lock could never engage. `lock_travel_deg()` now computes it and every dependent feature (notch, cam flat, lead slot, former exit, unlock mark) reads it.
- Anything that turns while something else stays fixed needs a slot, not a hole: the coil lead through the flange bore and the plate's exit hole.
- A part that is reused by flipping it (the right rear half) carries every feature at the mirrored edge; add features on the left, then check the flipped copy against the neighbours it meets.
- Holes that print horizontal get teardrop profiles (`add_teardrop`, roof toward the print's up) and a note to drill clearance holes anyway; sideways hex pockets get 0.3 mm of extra depth; snug holes that exit the bed face get an entry relief.
- A teardrop's apex reaches r(√2 − 1) past the round hole: leave ~1.7 r of material above it or keep the hole round (the stalk's lock-pin hole, the bar's pin sockets under the bottom channel).
- A cutter face coplanar with a cavity wall leaves non-manifold edges after the boolean (the nape base's end-wall window): start the cutter 0.5 mm inside the cavity.
- L / R marks on a plate under 2 mm thick are nicks THROUGH the edge (`lr_notches(..., thru=)`), not corner notches: a 1.5 mm corner notch on a 1.5 mm plate is a 0.7 mm wall.
- A spline cable route (Catmull-Rom) overshoots at a sharp rise: ramp the entry into a channel over two waypoints or the reference tube pokes through the channel's ceiling.
- A groove cut into a side face has one wall that faces down in the print: a 4 mm ledge printed in the air, not a bridge (the cradle's spine channels, upside down, had 290 mm of it; the print audit had reported the area but nobody read it as a ledge). `groove_section()` adds a 45-degree wedge below the groove so that wall becomes an overhang; where the wedge would cut into something (the sensor bar's pin sockets) the groove is a closed tunnel for 8 mm instead (a 2.5 mm bridge) and the cover strip skips it. Read every flat-overhang cluster against the geometry: its span says nothing about whether its far side is supported.
- A pentagon section whose 'face' vertex lies outside the cutter's overshoot crosses itself and the exact boolean deletes most of the part (the first tunnel-station cradle came out 8 mm tall). Clamp the face to the cutter edge and decide the polygon's orientation from the geometry, never from a sign test that can flip between stations.
- Audit residuals by design after v0.17: the 1 mm cover strips, the bay spool's 1.2 flange, the 1 mm floor of the dome bosses' blind taps, the nape family's lobe cusps (0.17..0.36), the pad plates' 1.2 pillar walls and the countersink rims 1.15 from the plate edge.
