#!/usr/bin/env -S blender --background --python
"""
print_check.py -- print-orientation audit of every STL in a directory (they are exported
in print orientation, Z up). Per part: footprint, height, bed-contact area, downward-facing
area that is NOT on the bed (bridges / flat overhangs, with the lowest such height) and
45..70 degree overhang area. A part with tiny bed contact or a large flat overhang near
z 0 is exported in the wrong orientation.
Run:  blender --background --python tools/blender/vp0/print_check.py -- [dir]
"""
import sys, glob, os
import bpy, bmesh

D = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 else "3D-Models/HelmKit/_generated/vp0"
bpy.ops.wm.read_factory_settings(use_empty=True)
rows = []
for f in sorted(glob.glob(os.path.join(D, "*.stl"))):
    bpy.ops.wm.stl_import(filepath=f)
    ob = bpy.context.selected_objects[0]
    me = ob.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    z0, z1 = min(zs), max(zs)
    bm = bmesh.new(); bm.from_mesh(me)
    contact = over = over45 = 0.0; over_low = 1e9
    for fc in bm.faces:
        n, a, c = fc.normal, fc.calc_area(), fc.calc_center_median()
        if c.z - z0 < 0.05 and n.z < -0.9:
            contact += a
        elif n.z < -0.94 and a > 0.01:
            over += a; over_low = min(over_low, c.z - z0)
        elif n.z < -0.71:
            over45 += a
    bm.free()
    rows.append((os.path.basename(f), max(xs) - min(xs), max(ys) - min(ys), z1 - z0, contact, over, over45, over_low if over else 0.0))
    bpy.data.objects.remove(ob)
print("part                     footprint x*y   height  bed-contact  flat-overhang(mm2, lowest z)  45-70deg-overhang")
for r in rows:
    flag = "  <-- CHECK" if (r[4] < 60 or (r[5] > 300 and r[7] < 1.0 and r[4] < 300)) else ""
    print(f"{r[0]:24s} {r[1]:6.1f} x {r[2]:6.1f}  {r[3]:6.1f}  {r[4]:8.0f}   {r[5]:8.0f} @ {r[7]:5.1f}   {r[6]:8.0f}{flag}")
