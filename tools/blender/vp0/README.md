# `tools/blender/vp0/` — HelmKit visual prototype (clean-slate part set)

Current revision: **vp0.11** (2026-09-05). Spec, print order and BOM:
[`docs/mechanical/vp0_visual_prototype.md`](../../../docs/mechanical/vp0_visual_prototype.md).
Earlier revisions are archived in `archive_v01/` … `archive_v08/`.

## Files

| File | Role |
|---|---|
| `canon.py` | Every number: wearer measurements, disk + bayonet + lock boss, cylinder port standard, cradle nodes / lug / sockets, nexus, captive pin, crown, brow rails and tabs, pylons, rear halves, nape modules, foam, pad frames, sensor bar, cable channel, headgear fit rule. `python3 canon.py` prints a summary. |
| `vp0lib.py` | Mesh helpers: revolve, cones (countersinks), teardrop holes and L/R notches (v0.17), chamfered ribbon sweep, centripetal Catmull-Rom, CDT-triangulated polygon extrusion, involute gear / rack / sawtooth / ridge / serration profiles, fillet pass, EXACT booleans, BVH overlap, mass properties, print-orientation export. |
| `build_disk.py` | Enclosed disk: dome shell with screw bosses, apex knob dish + boss, rim print flat and unlock mark (prints on edge); L and R back plates with the cam bayonet groove (lofted ring), the lock notch and the cable hole (`--out-dir`). `bayonet_boss()` / `bayonet_cuts()` are shared with the coupon |
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
| `build_fit_coupon_b.py` | v0.17 coupon B: horizontal hole row (round vs teardrop), sideways nut pocket, hub + ring, stalk with the lock-pin hole, bar pin sockets |
| `build_band_gauge.py` | Track P head-fit gauge: the bottom 3 mm of the band as a 7 mm ribbon along the centreline (about 1.5 h with supports against the cradle's eight) |
| `print_check.py` | Audit of every exported STL in print orientation: bed contact, flat overhang / bridge area, 45..70 deg overhang, thinnest wall (inward ray cast from every face); flags wrong-way-up parts and walls under 1.2 mm |
| `assemble_vp0.py` | Builds everything (nape parts per `NAPE_MODULE`; right pylons as rotated copies of the left print; pad frames with the foam on them) + reference coil / nails / springs / head + EAR phantoms, plus check-only objects (rails in the parked pose, cable runs); writes clearance (head + ears), mass, collision (worn + parked + cables) and snag reports, renders, saves `3D-Models/HelmKit_vp0/vp0_assembly.blend`. `--trim combat` builds the cradle + pads + sensor bar + flush plugs only, adds the headgear phantom, the bar cable routes as check-only objects, and writes `fit.txt` (the 20 mm sparring rule, bar excepted; overlaps with the headgear shell), saves `vp0_assembly_combat.blend`. `--core nape|slab|none` picks the electronics core (nape pod on the base, two slab pods on the rear sockets, or belt-only with the cap) and the mass report adds the electronics as reference masses |

## Regenerate everything

```sh
B=/Applications/Blender.app/Contents/MacOS/Blender   # linux: B=blender
OUT=3D-Models/HelmKit/_generated/vp0
for p in fit_coupon fit_coupon_b cradle_front rear_band_half crown_arch_half apex_block brow_center brow_lid visor_slider; do   # band_gauge uses --out-dir below
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/$p.stl
done
for p in brow_rail brow_link; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/${p}_L.stl
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/${p}_R.stl --mirror
done
for p in disk nexus nape_dial pylon port_parts spine_covers pad_frames sensor_bar nape_core belt_pack coil_former band_gauge; do
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
- Audit residuals by design after v0.17: the 1 mm cover strips, the bay spool's 1.2 flange, the 1 mm floor of the dome bosses' blind taps, the nape family's lobe cusps (0.17..0.36), the pad plates' 1.2 pillar walls and the countersink rims 1.15 from the plate edge.
