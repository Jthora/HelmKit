#!/usr/bin/env -S blender --background --python
"""
print_matrix.py -- per-part printability matrix for every STL in a directory (Track P, deep run P8).

Extends print_check.py from one line per part to the computable columns of the printability roster in
docs/mechanical/vp0_printability_matrix.md, for the QIDI X-Max 3's 325 x 325 x 315 plate at 0.4 / 0.2:

  G1  bed envelope           footprint <= 315 x 315 with the skirt / brim margin, height <= 310
  G2  bed contact            contact area, its share of the footprint bounding box, number of contact islands,
                             holes / recesses opening on the bed face (elephant's foot closes them)
  G3  stability              height over the smaller footprint dimension (brim over 3, slow over 5)
  G4  overhangs              area between 45 and 60 deg and between 60 and 70 deg from vertical
  G5  flat overhangs         downward faces off the bed, clustered: count, largest cluster's extent (a span
                             to bridge or a cantilever to support) and the lowest one's height
  G7  thinnest wall          inward ray cast from every face
  G8  small islands          smallest bed-contact island (a thin standing pin or a tab that will not stick)

Joins the slicer summary (part, seconds, filament m, mm3) when /tmp/claude-501/slice/summary.tsv exists and
prints one markdown table row per part.
Run:  blender --background --python tools/blender/vp0/print_matrix.py -- [dir] [--md out.md]
"""
import sys, glob, os, math, json
import bpy, bmesh
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
D = argv[0] if argv and not argv[0].startswith("--") else "3D-Models/HelmKit/_generated/vp0"
MD = argv[argv.index("--md") + 1] if "--md" in argv else None
BED = (315.0, 315.0, 310.0)

slicer = {}
try:
    for line in open("/tmp/claude-501/slice/summary.tsv"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 4 and p[0] != "SLICE_ALL_DONE":
            slicer[p[0]] = (float(p[1]), float(p[2]), float(p[3]))
except OSError:
    pass


def clusters(faces):
    """Connected components of a face set (shared vertices)."""
    faces = set(faces)
    seen, out = set(), []
    for f in faces:
        if f in seen:
            continue
        comp, stack = [], [f]
        seen.add(f)
        while stack:
            g = stack.pop()
            comp.append(g)
            for v in g.verts:
                for h in v.link_faces:
                    if h in faces and h not in seen:
                        seen.add(h); stack.append(h)
        out.append(comp)
    return out


def extent(faces):
    xs = [v.co.x for f in faces for v in f.verts]; ys = [v.co.y for f in faces for v in f.verts]
    return max(max(xs) - min(xs), max(ys) - min(ys)) if xs else 0.0


def boundary_loops(faces):
    """Number of boundary edge loops of a face set: loops - islands = holes."""
    faces = set(faces)
    bedges = [e for f in faces for e in f.edges if sum(1 for g in e.link_faces if g in faces) == 1]
    bedges = list(set(bedges))
    seen, loops = set(), 0
    adj = {}
    for e in bedges:
        for v in e.verts:
            adj.setdefault(v, []).append(e)
    for e in bedges:
        if e in seen:
            continue
        loops += 1
        stack = [e]; seen.add(e)
        while stack:
            g = stack.pop()
            for v in g.verts:
                for h in adj.get(v, []):
                    if h not in seen:
                        seen.add(h); stack.append(h)
    return loops


bpy.ops.wm.read_factory_settings(use_empty=True)
rows = []
for f in sorted(glob.glob(os.path.join(D, "*.stl"))):
    name = os.path.basename(f)[:-4]
    bpy.ops.wm.stl_import(filepath=f)
    ob = bpy.context.selected_objects[0]
    me = ob.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    z0, z1 = min(zs), max(zs)
    fx, fy, h = max(xs) - min(xs), max(ys) - min(ys), z1 - z0
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    contact_f, flat_f = [], []
    contact = over45 = over60 = 0.0
    for fc in bm.faces:
        n, a, c = fc.normal, fc.calc_area(), fc.calc_center_median()
        if c.z - z0 < 0.05 and n.z < -0.9:
            contact += a; contact_f.append(fc)
        elif n.z < -0.94 and a > 0.01 and c.z - z0 >= 0.3:
            flat_f.append(fc)
        elif n.z < -0.9 and c.z - z0 < 0.3:
            pass                              # a modelling offset under the first layer: the slicer swallows it
        elif n.z < -0.71:
            if n.z < -0.866: over60 += a      # 60..70 deg from vertical
            else:            over45 += a      # 45..60
    c_isl = clusters(contact_f)
    c_holes = max(0, boundary_loops(contact_f) - len(c_isl)) if contact_f else 0
    c_min_isl = min((sum(fc.calc_area() for fc in comp) for comp in c_isl), default=0.0)
    f_isl = clusters(flat_f)
    f_area = sum(fc.calc_area() for fc in flat_f)
    f_span = max((extent(comp) for comp in f_isl), default=0.0)
    f_low = min((fc.calc_center_median().z - z0 for fc in flat_f), default=0.0)
    bvh = BVHTree.FromBMesh(bm)
    wall, wall_at = 1e9, None
    for fc in bm.faces:
        if fc.calc_area() < 0.05:
            continue
        n, c = fc.normal, fc.calc_center_median()
        hit = bvh.ray_cast(c - n * 0.03, -n, 60.0)
        if hit[0] is None or hit[1].dot(-n) < 0.5:
            continue
        d = (hit[0] - c).length
        if 0.15 < d < wall:
            wall, wall_at = d, c
    bm.free()
    fits = fx <= BED[0] and fy <= BED[1] and h <= BED[2]
    aspect = h / max(min(fx, fy), 0.1)
    ratio = contact / max(fx * fy, 0.1)
    sl = slicer.get(name)
    rows.append(dict(part=name, fx=fx, fy=fy, h=h, fits=fits, contact=contact, ratio=ratio, islands=len(c_isl), bed_holes=c_holes,
                     min_island=c_min_isl, aspect=aspect, over45=over45, over60=over60, flat_n=len(f_isl), flat_area=f_area,
                     flat_span=f_span, flat_low=f_low, wall=wall, wall_at=[round(v, 1) for v in wall_at] if wall_at else None,
                     t_s=sl[0] if sl else None, fil_m=sl[1] if sl else None, g=(sl[2] * 1.24 / 1000) if sl else None))
    bpy.data.objects.remove(ob)


def flags(r):
    f = []
    if not r["fits"]: f.append("BED")
    if r["ratio"] < 0.2 and r["h"] > 20: f.append("brim")
    if r["aspect"] > 5: f.append("tall")
    if r["islands"] > 1 and r["min_island"] < 20: f.append("small-island")
    if r["bed_holes"]: f.append(f"bed-holes:{r['bed_holes']}")
    if r["over60"] > 50: f.append("overhang60")
    elif r["over45"] > 200: f.append("overhang45")
    if r["flat_span"] > 25: f.append(f"span:{r['flat_span']:.0f}")
    elif r["flat_span"] > 10 and r["flat_low"] > 0.3: f.append(f"bridge:{r['flat_span']:.0f}")
    if r["wall"] < 1.2: f.append(f"thin:{r['wall']:.2f}")
    return " ".join(f) or "ok"


hdr = "| part | footprint | h | contact % (islands, bed holes) | h/min | 45-60 / 60-70 mm² | flat overhang: n, span, low z | min wall | time | g | flags |"
lines = [hdr, "|" + "---|" * 11]
for r in rows:
    t = f"{int(r['t_s'] // 3600)}h{int(r['t_s'] % 3600 // 60):02d}" if r["t_s"] else "-"
    g = f"{r['g']:.0f}" if r["g"] is not None else "-"
    lines.append(f"| {r['part']} | {r['fx']:.0f} × {r['fy']:.0f} | {r['h']:.0f} | {100 * r['ratio']:.0f} ({r['islands']}, {r['bed_holes']}) | {r['aspect']:.1f} | "
                 f"{r['over45']:.0f} / {r['over60']:.0f} | {r['flat_n']}, {r['flat_span']:.0f}, {r['flat_low']:.1f} | {r['wall']:.2f} | {t} | {g} | {flags(r)} |")
out = "\n".join(lines)
print(out)
if MD:
    with open(MD, "w") as fh:
        fh.write(out + "\n")
    with open(MD.replace(".md", ".json"), "w") as fh:
        json.dump(rows, fh, indent=1)
