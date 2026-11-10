#!/usr/bin/env -S blender --background --python
"""
build_first_layers.py -- a first-layer test for a big, low-contact part (Track P, 2026-09-25).

Takes a part's generated, print-oriented STL and keeps only its bottom `--height` mm (default 0.6: three layers),
exactly as it will meet the plate. Printed with the same project settings, brim included, it shows in minutes whether
the whole footprint sticks, the far arm tips above all, instead of finding out an hour into an eight-hour print. The
cradle's fourth attempt failed on its first layer: the skirt and brim peeled at an arm tip and the nozzle dragged them.

Run:  blender --background --python tools/blender/vp0/build_first_layers.py -- cradle_front [--height 0.6]
      (reads and writes 3D-Models/HelmKit/_generated/vp0/<part>.stl -> <part>_first_layers.stl)
"""
import sys, os
from pathlib import Path
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import bpy  # type: ignore
import vp0lib as L

argv = L.argv_after_dashdash()
PART = argv[0]
H = float(argv[argv.index("--height") + 1]) if "--height" in argv else 0.6
GEN = _HERE.parents[2] / "3D-Models/HelmKit/_generated/vp0"
L.reset_scene()
bpy.ops.wm.stl_import(filepath=str(GEN / f"{PART}.stl"))
ob = bpy.context.selected_objects[0]
ob.name = f"{PART}_first_layers"
L.apply_transform(ob)
zmin = min(v.co.z for v in ob.data.vertices)
# a part with a sacrificial frame is many overlapping closed shells; the exact boolean cannot cut them as one, so each
# shell is trimmed on its own and the pieces are joined again
L.select_only(ob)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
kept = []
for sh in list(bpy.context.selected_objects):
    if min((sh.matrix_world @ v.co).z for v in sh.data.vertices) > zmin + H - 1e-6:
        L.delete(sh); continue
    L.cut(sh, L.add_box("above", (0.0, 0.0, zmin + H + 200.0), (1000.0, 1000.0, 400.0)))
    kept.append(sh)
bpy.ops.object.select_all(action="DESELECT")
for sh in kept:
    sh.select_set(True)
bpy.context.view_layer.objects.active = kept[0]
bpy.ops.object.join()
ob = kept[0]
ob.name = f"{PART}_first_layers"
L.finalize_and_export(ob, GEN / f"{PART}_first_layers.stl", L.ROT_NONE,
                      [f"the bottom {H} mm of {PART} as it meets the plate: print it with {PART}'s settings, brim and all",
                       "pass: every line is flat and fused, the brim is stuck all round, the arm tips and the node junctions most of all; nothing lifts when you run a fingernail along an edge",
                       "fail at one spot only: clean the plate there (dish soap and water, then dry) and re-level; fail everywhere: the Z offset is high"])
