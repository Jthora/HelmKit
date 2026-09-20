#!/usr/bin/env -S blender --background --python
"""
print_deep.py -- what a part actually asks of the printer (Track P, 2026-09-20, v2).

print_check and print_matrix measure areas. This classifies them. For every steep downward face (within 45 deg
of straight down) that is not on the bed it asks two things: how far is the drop to whatever is beneath it, and
is there material beside it at that height? Four horizontal rays decide the kind:

  BRIDGE       material on two opposite sides within 20 mm: the nozzle spans a gap. Fine to ~15 mm in PLA,
               sags past that, and a bridge over a hole is normal geometry, not a defect.
  CANTILEVER   material on one side only: a ledge or a shelf that starts in mid air and hangs off a wall.
               The drop says whether a 1 mm ledge (prints, with droop) or a 20 mm cliff (support or redesign).
  ISLAND       nothing beside it and nothing under it: the first layer of a feature that begins in the air.

The bed face is reported as area within one layer of the lowest point and as a fraction of the footprint
(flat% compares it with HORIZONTAL faces up to 1 mm higher; chamfers and fillets on the bed edge are ignored), and
the part's height over that contact is the tipping lever the brim has to fight.

Flags: LEVELS (over 100 mm2 of horizontal bed-region face 0.05 to 0.5 mm above the lowest: the bed face is in
more than one plane, and the first slice plane at 0.1 will cut through it, the ragged-first-layer symptom),
PERCH (contact under 12 % of the footprint on a part over 20 mm tall), CANTILEVER (over 100 mm2 hanging
with a drop over 2 mm), CLIFF (a cantilever drop over 8 mm: support territory), LONGBRIDGE (a bridge over
20 mm), ISLAND (over 10 mm2 starting in the air), NOTFLAT (under half the bed face in the first layer).

Run:  blender --background --python tools/blender/vp0/print_deep.py -- [dir] [--md out.md] [--only part]
"""
import sys, glob, os, math
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
D = argv[0] if argv and not argv[0].startswith("--") else "3D-Models/HelmKit/_generated/vp0"
MD = argv[argv.index("--md") + 1] if "--md" in argv else None
ONLY = argv[argv.index("--only") + 1] if "--only" in argv else None

FLAT_EPS = 0.2                          # one layer: area within this of the lowest point is "on the bed"
STEEP = math.cos(math.radians(45.0))    # a downward face within 45 deg of straight down
LEDGE = 2.0                             # a drop under this is a ledge the print carries with droop
CLIFF = 8.0                             # a drop over this needs support or a redesign
REACH = 20.0                            # how far sideways to look for a neighbour at the face's height
UP, DOWN = Vector((0, 0, 1)), Vector((0, 0, -1))
SIDES = [Vector((1, 0, 0)), Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, -1, 0))]


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)


def audit(path):
    reset()
    bpy.ops.wm.stl_import(filepath=path)
    ob = bpy.context.selected_objects[0]
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    bvh = BVHTree.FromBMesh(bm)
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    zmin, zmax = min(zs), max(zs)
    w, d, h = max(xs) - min(xs), max(ys) - min(ys), zmax - zmin

    bed = bed_near = 0.0
    levels = {}                         # horizontal bed-region faces by exact height: a two-level bed face is a slicer trap
    kinds = {"bridge": 0.0, "cant": 0.0, "island": 0.0}
    bridge_span = 0.0
    cant_drop = 0.0
    cant_pts = []
    for f in bm.faces:
        n = f.normal
        if n.z >= -0.1:
            continue
        a = f.calc_area()
        top = max(v.co.z for v in f.verts)
        if top <= zmin + 0.5 and -n.z > 0.95:
            lv = round((top - zmin) * 20) / 20
            levels[lv] = levels.get(lv, 0.0) + a
        if top <= zmin + FLAT_EPS:
            bed += a
            continue
        if top <= zmin + 1.0 and -n.z > 0.95:
            bed_near += a                    # horizontal only: a chamfer or fillet on the bed edge is not a bed face
        if -n.z < STEEP:
            continue
        c = f.calc_center_median()
        below = bvh.ray_cast(Vector((c.x, c.y, c.z - 0.05)), DOWN, (c.z - zmin) + 1.0)
        drop = (c.z - below[0].z) if below[0] is not None else (c.z - zmin)
        if drop <= 0.3:
            continue                                    # sits on something: not hanging
        o = Vector((c.x, c.y, c.z - 0.3))
        side = [bvh.ray_cast(o, s, REACH) for s in SIDES]
        dist = [(s[3] if s[0] is not None else None) for s in side]
        if (dist[0] is not None and dist[1] is not None) or (dist[2] is not None and dist[3] is not None):
            kinds["bridge"] += a
            # the bridge runs the SHORT way: on a curved cavity the long axis can read 36 where the roof spans 20
            pairs = [dist[0] + dist[1] if dist[0] is not None and dist[1] is not None else None,
                     dist[2] + dist[3] if dist[2] is not None and dist[3] is not None else None]
            sp = min(x for x in pairs if x is not None)
            bridge_span = max(bridge_span, sp)
        elif any(x is not None for x in dist):
            kinds["cant"] += a
            cant_drop = max(cant_drop, drop)
            cant_pts.append((c.x, c.y, c.z - zmin, drop, a))
        else:
            kinds["island"] += a

    flat_frac = bed / (bed + bed_near) if (bed + bed_near) > 1e-9 else 1.0
    contact = bed / (w * d) if w * d > 1e-9 else 1.0
    where = ""
    if cant_pts:
        big = [p for p in cant_pts if p[3] > LEDGE]
        if big:
            cx = [p[0] for p in big]; cy = [p[1] for p in big]; cz = [p[2] for p in big]
            where = f"x {min(cx):.0f}..{max(cx):.0f} y {min(cy):.0f}..{max(cy):.0f} at z {min(cz):.0f}..{max(cz):.0f}"
    cant_big = sum(p[4] for p in cant_pts if p[3] > LEDGE)

    lv_txt = " ".join(f"{k:.2f}:{v:.0f}" for k, v in sorted(levels.items()) if v > 20)
    two_level = sum(v for k, v in levels.items() if 0.08 <= k <= 0.5 and v > 20)   # under half a layer is inside layer 1 and prints

    flags = []
    if two_level > 100:
        flags.append("LEVELS")
    if contact < 0.12 and h > 20:
        flags.append("PERCH")
    if cant_big > 100:
        flags.append("CANTILEVER")
    if cant_drop > CLIFF and cant_big > 30:
        flags.append("CLIFF")
    if bridge_span > 20:
        flags.append("LONGBRIDGE")
    if kinds["island"] > 10:
        flags.append("ISLAND")
    if flat_frac < 0.5:
        flags.append("NOTFLAT")
    return dict(part=os.path.basename(path)[:-4], w=w, d=d, h=h, bed=bed, contact=contact, flat=flat_frac,
                levels=lv_txt, bridge=kinds["bridge"], span=bridge_span, cant=cant_big, drop=cant_drop, where=where,
                island=kinds["island"], flags=" ".join(flags) or "ok")


files = sorted(glob.glob(os.path.join(D, "*.stl")))
if ONLY:
    files = [f for f in files if ONLY in os.path.basename(f)]
rows = [audit(f) for f in files]

hdr = "| part | size | bed | contact | bed levels (mm:mm²) | bridges (max span) | cantilever >2 mm (max drop) | where | island | flags |"
sep = "|---|---|---|---|---|---|---|---|---|---|"
out = [hdr, sep]
for r in sorted(rows, key=lambda r: (r["flags"] == "ok", -(r["cant"] + (5000 if "PERCH" in r["flags"] else 0)), r["part"])):
    out.append(f"| {r['part']} | {r['w']:.0f}x{r['d']:.0f}x{r['h']:.0f} | {r['bed']:.0f} mm² | {100*r['contact']:.0f} % | "
               f"{r['levels']} | {r['bridge']:.0f} mm² ({r['span']:.0f}) | {r['cant']:.0f} mm² ({r['drop']:.1f}) | "
               f"{r['where']} | {r['island']:.0f} | {r['flags']} |")
print("\n".join(out))
print(f"\n{len(rows)} parts, {sum(1 for r in rows if r['flags'] != 'ok')} flagged")
if MD:
    open(MD, "w").write("\n".join(out) + "\n")
