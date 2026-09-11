# `tools/blender/vp0/` — HelmKit visual prototype (clean-slate part set)

Current revision: **vp0.11** (2026-09-05). Spec, print order and BOM:
[`docs/mechanical/vp0_visual_prototype.md`](../../../docs/mechanical/vp0_visual_prototype.md).
Earlier revisions are archived in `archive_v01/` … `archive_v08/`.

## Files

| File | Role |
|---|---|
| `canon.py` | Every number: wearer measurements, disk + bayonet + lock boss, cylinder port standard, cradle nodes / lug / sockets, nexus, captive pin, crown, brow rails and tabs, pylons, rear halves, nape modules, foam. `python3 canon.py` prints a summary. |
| `vp0lib.py` | Mesh helpers: revolve, chamfered ribbon sweep, centripetal Catmull-Rom, CDT-triangulated polygon extrusion, involute gear / rack / sawtooth / ridge / serration profiles, fillet pass, EXACT booleans, BVH overlap, mass properties, print-orientation export. |
| `build_disk.py` | Enclosed disk: dome shell with screw bosses, apex knob dish + boss; L and R back plates with the cam bayonet groove (lofted ring), the lock notch and the cable hole (`--out-dir`). `bayonet_boss()` / `bayonet_cuts()` are shared with the coupon |
| `build_nexus.py` | The NEXUS (PETG): L and R Ø68 flanges (hollow filleted stalk with the lock-pin hole, coil-cable bore, lanyard hole, head counterbores); spool with the notched hub and the spacer block; disk knob (shaft + eccentric); knob clip (`--out-dir`) |
| `build_cradle_front.py` | Cradle U: 7 mm forehead + side band (lower edge rises at the forehead) with spine channels between the nodes, hub nodes (nexus bolt holes + inner-face nut pockets, arch socket, coil bore), LED bores, rear nodes (tenon socket, pylon socket), strap slots (×1, PETG) |
| `build_crown_arch_half.py` | 20 × 7 arch half with a socketed foot over the hub node (coupler) (×2, same STL) |
| `build_apex_block.py` | Apex sleeve with M4 clamp |
| `build_brow_center.py`, `build_brow_rail.py`, `build_brow_link.py`, `build_visor_slider.py`, `build_brow_lid.py` | 160 mm centre panel with back-face link pockets and a front faceplate recess; rails with their Ø44 rings, gusseted bar, pawl tunnel, half-lap and underside cable groove (`--mirror`); links (lap + 55° bar; `--mirror`); pawl slider; faceplate |
| `build_rear_band_half.py` | Rear half: tapered tenon into the rear node, strap slots, spine channel, phased rack (×2, same STL, PETG) |
| `build_spine_covers.py` | Flush cover strips for the spine channels: front arc half, side span, rear half (`--out-dir`) |
| `build_nape_dial.py` | Nape modules: `nape_pinlock` (print one; four-lobe nail slot, prints standing) and the enclosed PULL dial set: body (ratchet ring), cover (window), lid, dial, key cap, pinion, retainer with M5 nut pocket (`--out-dir`) |
| `build_pylon.py` | Antenna pylon: pegged base with a serrated clevis, faceted blade, lock knob (`--out-dir`) |
| `build_port_parts.py` | Cylinder port spares: plug, coupler, drill guide (`--out-dir`) |
| `build_fit_coupon.py` | Print-first tolerance coupon: hole gauges, port, bayonet boss + stub, ratchet pair |
| `print_check.py` | Audit of every exported STL in print orientation: bed contact, flat overhang / bridge area, 45..70 deg overhang, thinnest wall (inward ray cast from every face); flags wrong-way-up parts and walls under 1.2 mm |
| `assemble_vp0.py` | Builds everything (nape parts per `NAPE_MODULE`; right pylons as rotated copies of the left print) + reference foam / coil / nails / springs / head + EAR phantoms, plus check-only objects (rails in the parked pose, cable runs); writes clearance (head + ears), mass, collision (worn + parked + cables) and snag reports, renders, saves `3D-Models/HelmKit_vp0/vp0_assembly.blend` |

## Regenerate everything

```sh
B=/Applications/Blender.app/Contents/MacOS/Blender   # linux: B=blender
OUT=3D-Models/HelmKit/_generated/vp0
for p in fit_coupon cradle_front rear_band_half crown_arch_half apex_block brow_center brow_lid visor_slider; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/$p.stl
done
for p in brow_rail brow_link; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/${p}_L.stl
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/${p}_R.stl --mirror
done
for p in disk nexus nape_dial pylon port_parts spine_covers; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out-dir $OUT
done
$B --background --python tools/blender/vp0/print_check.py -- $OUT
$B --background --python tools/blender/vp0/assemble_vp0.py -- --out $OUT/renders   # ~10 min with renders
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
