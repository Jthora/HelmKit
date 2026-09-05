# `tools/blender/vp0/` — HelmKit visual prototype (clean-slate part set)

Current revision: **vp0.9** (2026-09-05). Spec, print order and BOM:
[`docs/mechanical/vp0_visual_prototype.md`](../../../docs/mechanical/vp0_visual_prototype.md).
Earlier revisions are archived in `archive_v01/` … `archive_v08/`.

## Files

| File | Role |
|---|---|
| `canon.py` | Every number: wearer measurements, disk + bayonet + lock boss, cylinder port standard, cradle nodes / lug / sockets, nexus, captive pin, crown, brow rails and tabs, pylons, rear halves, nape modules, foam. `python3 canon.py` prints a summary. |
| `vp0lib.py` | Mesh helpers: revolve, chamfered ribbon sweep, centripetal Catmull-Rom, CDT-triangulated polygon extrusion, involute gear / rack / sawtooth / ridge / serration profiles, fillet pass, EXACT booleans, BVH overlap, mass properties, print-orientation export. |
| `build_disk.py` | Enclosed disk: dome shell with screw bosses; back plate with the bayonet boss and the tapped lock boss (`--out-dir`). `bayonet_boss()` / `bayonet_cuts()` are shared with the coupon |
| `build_nexus.py` | The NEXUS (PETG): Ø60 flange with the bayonet stalk, lock ear and lanyard hole; Ø44/32 spool (visor ring bearing); pin keeper; lock knob; pin collar (`--out-dir`) |
| `build_cradle_front.py` | Cradle U: forehead + side band with a doubler around the hub nodes (nexus bolts, keeper-bolted pin lug, arch socket), rear nodes (tenon socket, pylon socket), strap slots (×1, PETG) |
| `build_crown_arch_half.py` | 20 × 7 arch half with a socketed foot over the hub node (coupler) (×2, same STL) |
| `build_apex_block.py` | Apex sleeve with M4 clamp |
| `build_brow_center.py`, `build_brow_rail.py`, `build_brow_tab.py`, `build_brow_lid.py` | 160 mm centre panel; rails with their nexus rings (24 index holes, two tab bolts; `--mirror`); L-tabs (`--mirror`); lid |
| `build_rear_band_half.py` | Rear half: tapered tenon into the rear node, strap slots, phased rack (×2, same STL, PETG) |
| `build_nape_dial.py` | Nape modules: `nape_pinlock` (print one) and the enclosed PULL dial set: body (ratchet ring), cover (window), lid, dial, key cap, pinion, retainer with M5 nut pocket (`--out-dir`) |
| `build_pylon.py` | Antenna pylon: pegged base with a serrated clevis, faceted blade, lock knob (`--out-dir`) |
| `build_port_parts.py` | Cylinder port spares: plug, coupler, drill guide (`--out-dir`) |
| `build_fit_coupon.py` | Print-first tolerance coupon: hole gauges, port, bayonet boss + stub, ratchet pair |
| `print_check.py` | Audit of every exported STL in print orientation: bed contact, flat overhang / bridge area, 45..70 deg overhang; flags parts exported the wrong way up |
| `assemble_vp0.py` | Builds everything (nape parts per `NAPE_MODULE`) + reference foam / coil / nails / springs / head, writes clearance, mass, collision and snag reports, renders, saves `3D-Models/HelmKit_vp0/vp0_assembly.blend` |

## Regenerate everything

```sh
B=/Applications/Blender.app/Contents/MacOS/Blender   # linux: B=blender
OUT=3D-Models/HelmKit/_generated/vp0
for p in fit_coupon cradle_front rear_band_half crown_arch_half apex_block brow_center brow_lid; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/$p.stl
done
for p in brow_rail brow_tab; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/${p}_L.stl
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/${p}_R.stl --mirror
done
for p in disk nexus nape_dial pylon port_parts; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out-dir $OUT
done
$B --background --python tools/blender/vp0/print_check.py -- $OUT
$B --background --python tools/blender/vp0/assemble_vp0.py -- --out $OUT/renders   # ~10 min with renders
```

Each STL is exported in its print orientation with a `.txt` sidecar (bbox, mass,
manifold check, notes). Output is `.gitignore`d; the `.blend` is tracked.

## Working in the Blender UI

Open `3D-Models/HelmKit_vp0/vp0_assembly.blend`. 1 unit = 1 mm. Collections:
Cradle (with Nape), Disks.L/R (dome, back, nexus, spool, keeper, knob, collar), Crown (arches, couplers, apex), Brow (panel, rails with rings, tabs, lid),
AddOns (pylons), Reference (foam, coil, nails, springs, head; not printed), PrintLayout (hidden). The `README_vp0` text block explains the edit → export
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
- Overlapping holes (the pin-lock's 2.2 mm holes 1.96 mm apart) are fine for the solver; check the physical waist instead (1.0 mm here, so a 2 mm nail stays in its lobe).
