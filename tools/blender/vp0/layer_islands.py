#!/usr/bin/env -S blender --background --python
"""
layer_islands.py -- the slicer's "floating regions" check, done the slicer's way (Track P, 2026-09-25).

print_deep.py reasons from faces: a feature that begins in mid air next to something solid reads as a cantilever
there and never trips its ISLAND flag. QIDI Studio / Orca reason per LAYER: any region of a layer whose polygon has
no overlap with the layer below is a floating region, and the object gets the warning "has floating regions".

This slices the print-oriented STL at every layer (mid-layer, as the slicer samples), builds each layer's closed
section loops, and reports every MATERIAL loop (even nesting depth; odd ones are holes, which the slicer never treats as regions)
that neither contains a vertex of the layer below nor has a vertex inside a loop of the layer below: the region
starts in the air. For each: the layer height, where it is, how big, and how
many layers it persists before it joins something.

Run:  blender --background --python tools/blender/vp0/layer_islands.py -- part.stl [--layer 0.2] [--first 0.2]
"""
import sys, os, math
import bpy, bmesh
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PATH = argv[0]
LH = float(argv[argv.index("--layer") + 1]) if "--layer" in argv else 0.2
FIRST = float(argv[argv.index("--first") + 1]) if "--first" in argv else 0.2

bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
bpy.ops.wm.stl_import(filepath=os.path.abspath(PATH))
ob = bpy.context.selected_objects[0]
base = bmesh.new(); base.from_mesh(ob.data); base.transform(ob.matrix_world)
zs = [v.co.z for v in base.verts]; zmin, zmax = min(zs), max(zs)


def section_loops(z):
    bm = base.copy()
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0.0, 0.0, z), plane_no=(0.0, 0.0, 1.0), clear_outer=True, clear_inner=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    # chain the cut edges into closed loops
    adj = {}
    for e in edges:
        a, b = e.verts
        adj.setdefault(a.index, []).append(b.index); adj.setdefault(b.index, []).append(a.index)
    co = {v.index: (v.co.x, v.co.y) for e in edges for v in e.verts}
    seen, loops = set(), []
    for start in adj:
        if start in seen: continue
        loop, cur, prev = [], start, None
        while cur is not None and cur not in seen:
            seen.add(cur); loop.append(co[cur])
            nxt = [n for n in adj[cur] if n != prev and n not in seen]
            prev, cur = cur, (nxt[0] if nxt else None)
        if len(loop) >= 3: loops.append(loop)
    bm.free()
    return loops


def inside(pt, poly):
    x, y = pt; n = len(poly); c = False
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            c = not c
    return c


def area(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2.0


def supported(loop, prev_loops):
    if not prev_loops: return False
    for p in loop:
        if any(inside(p, q) for q in prev_loops): return True
    for q in prev_loops:
        if any(inside(p, loop) for p in q): return True
    return False


levels, z, prev = [], zmin + FIRST / 2.0, []
while z < zmax:
    levels.append(z); z += LH
def material_loops(loops):
    """Loops nested an even number of times are material outlines; odd ones are holes (void), which the slicer never
    treats as regions. Nesting is counted by testing one vertex of each loop against every other loop."""
    out = []
    for i, a in enumerate(loops):
        depth = sum(1 for j, b in enumerate(loops) if j != i and inside(a[0], b))
        if depth % 2 == 0:
            out.append(a)
    return out


found = {}
for li, z in enumerate(levels):
    loops = section_loops(z)
    for loop in material_loops(loops):
        if li == 0 or supported(loop, prev):
            continue
        xs = [p[0] for p in loop]; ys = [p[1] for p in loop]
        key = (round(sum(xs) / len(xs)), round(sum(ys) / len(ys)))
        rec = found.setdefault(key, dict(z0=z - zmin, n=0, w=max(xs) - min(xs), d=max(ys) - min(ys), a=area(loop), x=sum(xs) / len(xs), y=sum(ys) / len(ys)))
        rec["n"] += 1
    prev = loops

print(f"{os.path.basename(PATH)}: {len(levels)} layers of {LH} from {zmin:.2f} to {zmax:.2f}; floating regions: {len(found)}")
for k, r in sorted(found.items(), key=lambda kv: kv[1]["z0"]):
    print(f"   starts {r['z0']:6.2f} mm up at x {r['x']:7.1f} y {r['y']:7.1f}: {r['w']:.1f} x {r['d']:.1f} mm, {r['a']:.2f} mm2, floating for {r['n']} layer(s)")
