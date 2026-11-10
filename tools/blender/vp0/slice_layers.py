#!/usr/bin/env -S blender --background --python
"""
slice_layers.py -- slice a print-oriented STL at every 0.2 mm layer (mid-layer, as the slicer samples) and write each
layer's closed outlines to JSON, for qidi_support_check.py. Outlines are chained by POSITION (the bisect can split one
point into two indices) and only closed loops are kept; the count of open chains is printed, and any is a mesh defect.

Run:  blender --background --python tools/blender/vp0/slice_layers.py -- part.stl out.json [--layer 0.16]
"""
import bpy, bmesh, sys, os, json
argv = sys.argv[sys.argv.index("--") + 1:]
PATH, OUTJ = argv[0], argv[1]
LH = float(argv[argv.index('--layer') + 1]) if '--layer' in argv else 0.2   # the dome prints at 0.16
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
bpy.ops.wm.stl_import(filepath=os.path.abspath(PATH))
ob = bpy.context.selected_objects[0]
whole = bmesh.new(); whole.from_mesh(ob.data); whole.transform(ob.matrix_world)
# separate closed shells (a part plus its sacrificial frame are overlapping solids): each is sliced on its own, and a
# layer's material is the UNION of its shells' even-odd regions
whole.verts.ensure_lookup_table()
seen, shells = set(), []
for v in whole.verts:
    if v.index in seen: continue
    st, comp = [v], []
    while st:
        x = st.pop()
        if x.index in seen: continue
        seen.add(x.index); comp.append(x.index); st += [e.other_vert(x) for e in x.link_edges if e.other_vert(x).index not in seen]
    shells.append(set(comp))
def shell_mesh(ids):
    bm = whole.copy(); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in range(len(bm.verts)) if i not in ids], context="VERTS")
    return bm
bases = [shell_mesh(ids) for ids in shells] if len(shells) > 1 else [whole]
base = whole
spans = [(min(v.co.z for v in b.verts), max(v.co.z for v in b.verts)) for b in bases]
zs = [v.co.z for v in base.verts]; zmin, zmax = min(zs), max(zs)
layers, z, OPEN = [], zmin + LH / 2 + 0.0013, []   # +0.0013: a flat face at exactly a mid-layer height put the cutting plane IN the face and dropped its outline (nape base, 2026-09-26)
while z < zmax:
    shells_loops = []
    for base_, (s0z, s1z) in zip(bases, spans):
     if not (s0z < z < s1z): continue
     bm = base_.copy(); geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
     res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, z), plane_no=(0, 0, 1), clear_outer=True, clear_inner=True)
     edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
     key = lambda v: (round(v.co.x, 4), round(v.co.y, 4))      # chain by POSITION: the bisect can split one point into two indices
     adj = {}
     for e in edges:
         a, b = key(e.verts[0]), key(e.verts[1])
         if a == b: continue
         adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
     seen, loops, openc = set(), [], 0
     for s0 in adj:
         if s0 in seen: continue
         loop, cur, prev = [s0], s0, None; seen.add(s0); closed = False
         while True:
             nx = [n for n in adj[cur] if n != prev]
             if not nx: break
             if s0 in nx and len(loop) > 2: closed = True; break
             nx = [n for n in nx if n not in seen]
             if not nx: break
             prev, cur = cur, nx[0]; seen.add(cur); loop.append(cur)
         if closed and len(loop) >= 3: loops.append(loop)
         else: openc += 1
     OPEN.append((z - zmin, openc))
     shells_loops.append(loops); bm.free()
    layers.append({"z": z - zmin, "shells": shells_loops, "lh": LH}); z += LH
json.dump(layers, open(OUTJ, "w"))
print("dumped", len(layers), "open chains:", sum(o for _, o in OPEN), "on layers", [round(z, 1) for z, o in OPEN if o][:12])
