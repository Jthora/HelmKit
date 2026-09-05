# `tools/blender/vp0/` — HelmKit visual prototype (clean-slate part set)

Current revision: **vp0.4** (2026-09-04). Spec, print order and BOM:
[`docs/mechanical/vp0_visual_prototype.md`](../../../docs/mechanical/vp0_visual_prototype.md).
Earlier revisions are archived in `archive_v01/`, `archive_v02/` and `archive_v03/`.

## Files

| File | Role |
|---|---|
| `canon.py` | Every number: wearer measurements, pod, port standard, crown, brow, rear band, ratchet, foam. `python3 canon.py` prints a summary. |
| `vp0lib.py` | Mesh helpers: revolve, chamfered ribbon sweep, centripetal Catmull-Rom, CDT-triangulated polygon extrusion, involute gear / rack / sawtooth / ridge profiles, flush-port sockets and couplers, fillet pass, EXACT booleans, BVH overlap, mass properties, print-orientation export. |
| `build_pod_shell.py` | Paraboloid shell, dome out, five pinned flush sockets in the rim ring (×2) |
| `build_crown_arch_half.py` | Arch half with rim-seated pinned foot and rope spine groove (×2, same STL) |
| `build_apex_block.py` | Apex sleeve with M4 clamp |
| `build_brow_panel.py`, `build_brow_lid.py` | Centre + swept wings, lid |
| `build_rear_band_half.py` | Band half with pinned socket block, spine groove and rope eye (×2, same STL) |
| `build_nape_plate.py` | Nape plate with rope channel and printed clam cleat |
| `build_port_parts.py` | Pinned couplers (crown / rear / brow), drill guide, socket casting form, plug blank, cover, strap anchor (`--out-dir`) |
| `build_fit_coupon.py` | Print-first tolerance coupon |
| `assemble_vp0.py` | Builds everything + reference foam / cells / head, writes clearance, mass, collision and snag reports, renders, saves `3D-Models/HelmKit_vp0/vp0_assembly.blend` |

## Regenerate everything

```sh
B=/Applications/Blender.app/Contents/MacOS/Blender   # linux: B=blender
OUT=3D-Models/HelmKit/_generated/vp0
for p in fit_coupon pod_shell crown_arch_half apex_block brow_panel brow_lid rear_band_half nape_plate; do
  $B --background --python tools/blender/vp0/build_$p.py -- --out $OUT/$p.stl
done
$B --background --python tools/blender/vp0/build_port_parts.py -- --out-dir $OUT
$B --background --python tools/blender/vp0/assemble_vp0.py -- --out $OUT/renders   # ~10 min with renders
```

Each STL is exported in its print orientation with a `.txt` sidecar (bbox, mass,
manifold check, notes). Output is `.gitignore`d; the `.blend` is tracked.

## Working in the Blender UI

Open `3D-Models/HelmKit_vp0/vp0_assembly.blend`. 1 unit = 1 mm. Collections:
Pods.L/R, Couplers, Crown, Brow, Rear, AddOns, Reference (foam, rope, head; not
printed), PrintLayout (hidden). The `README_vp0` text block explains the edit → export
workflow. Re-running `assemble_vp0.py` overwrites the file.

## Boolean and print hygiene (Blender 5.0 EXACT solver)

- Revolves, never cylinder primitives, for anything a serration or ridge is unioned onto.
- Polygon extrusions triangulate their caps with a constrained Delaunay (ear clipping emits zero-area triangles on collinear outlines such as rack roots).
- No two bodies share a face plane or a tangent line: offsets of 0.1 mm everywhere it matters.
- Ribbons use centripetal Catmull-Rom (uniform loops back on itself at uneven waypoints) and a chamfered section.
- `fillet()` runs the bevel modifier and reverts itself if the result is not manifold; call it after every cut, never before one. Ribbons get their rounding from `chamfer=` instead.
- Ridge and serration valleys sit 0.1 mm below their host face; a vertex exactly on a face is a non-manifold edge waiting to happen.
- `finalize_and_export` warns on any non-manifold edge; treat that as a failed build.
