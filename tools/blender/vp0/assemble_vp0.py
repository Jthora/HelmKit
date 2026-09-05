#!/usr/bin/env -S blender --background --python
"""
assemble_vp0.py -- build every vp0.9 part in the assembly frame, run the reports,
render, save the hand-editable .blend.

Reports (next to the renders): clearance.txt, mass.txt, collisions.txt, snag.txt
Run:
    blender --background --python tools/blender/vp0/assemble_vp0.py -- \\
        --out 3D-Models/HelmKit/_generated/vp0/renders [--blend path] [--no-head] [--no-render] [--no-layout]
"""
from __future__ import annotations
import math, re, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore
import vp0lib as L
import canon as C
import build_disk, build_nexus, build_crown_arch_half, build_apex_block, build_cradle_front
import build_brow_center, build_brow_rail, build_brow_tab, build_brow_lid, build_rear_band_half, build_nape_dial
import build_pylon, build_port_parts, build_fit_coupon

COLORS = {"graphite": (0.10, 0.10, 0.11, 1.0), "accent": (0.80, 0.16, 0.12, 1.0), "bone": (0.86, 0.84, 0.78, 1.0), "spring": (0.75, 0.75, 0.78, 1.0),
          "steel": (0.55, 0.57, 0.60, 1.0), "skin": (0.72, 0.58, 0.48, 1.0), "bed": (0.30, 0.32, 0.36, 1.0),
          "foam": (0.25, 0.25, 0.27, 1.0), "rope": (0.62, 0.55, 0.40, 1.0)}
DEFAULT_BLEND = "3D-Models/HelmKit_vp0/vp0_assembly.blend"


def material(name):
    m = bpy.data.materials.get(f"vp0_{name}")
    if m:
        return m
    rgba = COLORS[name]
    m = bpy.data.materials.new(f"vp0_{name}")
    m.diffuse_color = rgba
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.6
    return m


def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def move_to(ob, coll):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)


def style(ob, name, color, coll):
    ob.name = name
    ob.color = COLORS[color]
    ob.data.materials.clear()
    ob.data.materials.append(material(color))
    move_to(ob, coll)
    return ob


def layer_coll(name):
    def walk(lc):
        if lc.name == name:
            return lc
        for ch in lc.children:
            r = walk(ch)
            if r:
                return r
    return walk(bpy.context.view_layer.layer_collection)


def placed(ob, M: Matrix):
    ob.matrix_world = M @ ob.matrix_world
    L.apply_transform(ob)
    return ob


# ---------------------------------------------------------------------------

def build_assembly(with_head=True):
    P, R = {}, {}      # P = printed parts, R = reference (foam, head, springs, nails, coil)
    add = collection("AddOns")
    for side, tag in ((+1, "L"), (-1, "R")):
        disks = collection(f"Disks.{tag}")
        P[f"dome_{tag}"] = style(build_disk.dome(side), f"disk_dome.{tag}", "graphite", disks)
        P[f"back_{tag}"] = style(build_disk.back(side), f"disk_back.{tag}", "graphite", disks)
        P[f"nexus_{tag}"] = style(build_nexus.flange(side), f"nexus.{tag}", "steel", disks)
        P[f"spool_{tag}"] = style(build_nexus.spool(side), f"nexus_spool.{tag}", "steel", disks)
        P[f"keeper_{tag}"] = style(build_nexus.keeper(side), f"pin_keeper.{tag}", "steel", disks)
        lk = C.DISK_LOCK
        a = math.radians(lk["angle"])
        Mk = Matrix.Translation((C.CX + lk["r"] * math.cos(a), side * C.NEXUS_Y[0], C.CZ + lk["r"] * math.sin(a))) @ Matrix.Rotation(side * math.pi / 2, 4, "X")
        P[f"knob_{tag}"] = style(placed(build_nexus.lock_knob(), Mk), f"lock_knob.{tag}", "bone", disks)
        px, py = C.NEXUS_PIN
        P[f"collar_{tag}"] = style(placed(build_nexus.pin_collar(), Matrix.Translation((px, side * py, C.NEXUS_PIN_LUG[2][1] + 0.3))), f"pin_collar.{tag}", "bone", disks)
        P[f"pylon_{tag}"] = style(build_pylon.base(side), f"pylon_base.{tag}", "steel", add)
        P[f"pylonb_{tag}"] = style(build_pylon.blade(side), f"pylon_blade.{tag}", "graphite", add)
        P[f"pylonk_{tag}"] = style(build_pylon.knob(side), f"pylon_knob.{tag}", "bone", add)
    cradle = collection("Cradle")
    P["cradle"] = style(build_cradle_front.make(), "cradle_front", "accent", cradle)
    P["rear_L"] = style(build_rear_band_half.make(), "rear_band.L", "accent", cradle)
    P["rear_R"] = style(L.transformed_copy(P["rear_L"], build_rear_band_half.right_half_matrix(), "rear_band.R"), "rear_band.R", "accent", cradle)
    nape = collection("Nape", cradle)
    if C.NAPE_MODULE == "pinlock":
        P["nape_pinlock"] = style(build_nape_dial.make_pinlock(), "nape_pinlock", "steel", nape)
    else:
        for nm, mk in (("body", build_nape_dial.make_body), ("cover", build_nape_dial.make_cover), ("lid", build_nape_dial.make_lid), ("dial", build_nape_dial.make_dial),
                       ("key", build_nape_dial.make_key), ("pinion", build_nape_dial.make_pinion), ("retainer", build_nape_dial.make_retainer)):
            P[f"nape_{nm}"] = style(mk(), f"nape_{nm}", "steel" if nm in ("body", "cover", "lid") else "bone", nape)
    crown = collection("Crown")
    P["arch_L"] = style(build_crown_arch_half.make(), "crown_arch.L", "graphite", crown)
    P["arch_R"] = style(L.transformed_copy(P["arch_L"], build_crown_arch_half.right_half_matrix(), "crown_arch.R"), "crown_arch.R", "graphite", crown)
    P["apex"] = style(build_apex_block.make(), "apex_block", "steel", crown)
    for side, tag in ((+1, "L"), (-1, "R")):     # couplers: hub node socket <-> arch foot socket
        P[f"coupler_{tag}"] = style(placed(build_port_parts.coupler(), Matrix.Translation((C.HUB_SOCKET[0], side * C.HUB_SOCKET[1], C.CRADLE_Z + C.HUB_NODE_W[1] - C.CYL_DEPTH))),
                                    f"port_coupler.{tag}", "steel", crown)
    brow = collection("Brow")
    P["panel"] = style(build_brow_center.make(), "brow_center", "bone", brow)
    P["lid"] = style(build_brow_lid.make(), "brow_lid", "bone", brow)
    P["rail_L"] = style(build_brow_rail.make(+1), "brow_rail.L", "steel", brow)
    P["rail_R"] = style(build_brow_rail.make(-1), "brow_rail.R", "steel", brow)
    P["tab_L"] = style(build_brow_tab.make(+1), "brow_tab.L", "bone", brow)
    P["tab_R"] = style(build_brow_tab.make(-1), "brow_tab.R", "bone", brow)

    ref = collection("Reference")
    if with_head:
        R["head"] = style(L.head_phantom(), "head_phantom", "skin", ref)
    fb = C.FOAM_BLOCKS
    w, h, t = fb["forehead"]
    R["foam_front"] = style(L.add_box("foam", (C.CRADLE_FRONT_X - C.CRADLE_T / 2 - t / 2, 0.0, C.CRADLE_Z), (t, w, h)), "foam_forehead", "foam", ref)
    for side, tag in ((+1, "L"), (-1, "R")):
        w, h, t = fb["side"]
        R[f"foam_side_{tag}"] = style(L.add_box("foam", (40.0, side * (C.CRADLE_SIDE_Y - C.CRADLE_T / 2 - t / 2), C.CRADLE_Z), (w, t, h)), f"foam_side.{tag}", "foam", ref)
        w, h, t = fb["temple"]
        R[f"foam_hub_{tag}"] = style(L.add_box("foam", (C.HUB_NODE[0], side * (C.NODE_IN_Y - t / 2), C.CRADLE_Z + 2.5), (w, t, 20.0)), f"foam_hub.{tag}", "foam", ref)
        w, h, t = fb["rear"]
        r0, r1 = C.REAR_NODE_W
        R[f"foam_rear_{tag}"] = style(L.add_box("foam", (C.REAR_NODE_X, side * (C.NODE_IN_Y - t / 2), C.CRADLE_Z + (r0 + r1) / 2 + 2.0), (w, t, h)), f"foam_rear.{tag}", "foam", ref)
        cd, ct = C.DISK_CAVITY
        n0 = C.DISK_PLATE_T + 1.0
        R[f"coil_{tag}"] = style(L.foam_ring("coil", (C.CX, side * (C.DISK_IN_Y + n0), C.CZ), cd / 2, 18.0, ct - 2.0, axis="Y" if side > 0 else "-Y"), f"coil_apparatus.{tag}", "rope", ref)
    for side, tag in ((+1, "L"), (-1, "R")):    # captive index nails (tip in a ring hole, collar on the lug, spring under the keeper bar) -- reference
        px, py = C.NEXUS_PIN
        z_tip = C.CZ + 17.5
        R[f"pin_{tag}"] = style(L.add_cyl("pin", (px, side * py, z_tip + 20.0), 1.6, 40.0, axis="Z", verts=12), f"index_nail.{tag}", "spring", ref)
        z_c = C.NEXUS_PIN_LUG[2][1] + 0.3 + C.PIN_COLLAR[1]
        z_b = C.PIN_KEEPER["top_z"] - C.PIN_KEEPER["bar_t"]
        R[f"spring_{tag}"] = style(L.add_cyl("spring", (px, side * py, (z_c + z_b) / 2), C.PIN_SPRING["id"] / 2 + 1.0, z_b - z_c, axis="Z", verts=16), f"index_spring.{tag}", "spring", ref)
    pw, pl, pt = C.CROWN_PAD
    apex_bottom = C.CROWN_APEX_Z - (C.CROWN_T + 0.4) / 2 - C.APEX_FLOOR_T
    R["crownpad"] = style(L.add_box("crownpad", (C.CX, 0.0, apex_bottom - pt / 2), (pw, pl, pt)), "crown_pad", "foam", ref)
    Mn = build_nape_dial.M
    nw, nh, nt = C.NAPE_PAD
    if C.NAPE_MODULE == "pinlock":
        R["napepad"] = style(L.add_box_local("napepad", Mn, (0.0, 0.0, -C.NAPE_PINLOCK_T / 2 - nt / 2), (nw, nh, nt)), "nape_pad", "foam", ref)
        R["napenail"] = style(L.add_cyl_local("napenail", Mn, (C.NAPE_PINLOCK_HOLES[0], 3.0, 0.0), C.NAPE_PINLOCK_PIN["dia"] / 2, C.NAPE_HV + 6.0, axis="Y", verts=12), "nape_nail", "spring", ref)
    else:
        R["napepad"] = style(L.add_box_local("napepad", Mn, (0.0, 0.0, -C.NAPE_CH - C.NAPE_LID_T - nt / 2), (nw, nh, nt)), "nape_pad", "foam", ref)
        sp = C.NAPE_SPRING
        w_floor = C.NAPE_DIAL_W0 + C.NAPE_DIAL_T - C.NAPE_SPRING_WELL[1]
        R["spring"] = style(L.add_cyl_local("spring", Mn, (0.0, 0.0, w_floor + sp["working"] / 2), sp["od"] / 2, sp["working"], axis="Z", verts=24), "nape_spring", "spring", ref)
    return P, R


NAPE_ITEMS = ([("nape_pinlock", build_nape_dial.make_pinlock, lambda: build_nape_dial.PARTS["nape_pinlock"][1], "steel")] if C.NAPE_MODULE == "pinlock" else
              [(f"nape_{n}", getattr(build_nape_dial, f"make_{n}"), (lambda n=n: build_nape_dial.PARTS[f"nape_{n}"][1]), "steel" if n in ("body", "cover", "lid") else "bone")
               for n in ("body", "cover", "lid", "dial", "key", "pinion", "retainer")])
PRINT_ITEMS = [
    ("fit_coupon", build_fit_coupon.make, lambda: build_fit_coupon.PRINT_ROT, "bone"),
    ("cradle_front", build_cradle_front.make, lambda: build_cradle_front.PRINT_ROT, "accent"),
    ("rear_band_half", build_rear_band_half.make, lambda: build_rear_band_half.PRINT_ROT, "accent"),
    ("disk_dome", lambda: build_disk.dome(+1), lambda: build_disk.PARTS["disk_dome"][1], "graphite"),
    ("disk_back", lambda: build_disk.back(+1), lambda: build_disk.PARTS["disk_back"][1], "graphite"),
    ("nexus", lambda: build_nexus.flange(+1), lambda: build_nexus.PARTS["nexus"][1], "steel"),
    ("nexus_spool", lambda: build_nexus.spool(+1), lambda: build_nexus.PARTS["nexus_spool"][1], "steel"),
    ("pin_keeper", lambda: build_nexus.keeper(+1), lambda: build_nexus.PARTS["pin_keeper"][1], "steel"),
    ("lock_knob", build_nexus.lock_knob, lambda: build_nexus.PARTS["lock_knob"][1], "bone"),
    ("pin_collar", build_nexus.pin_collar, lambda: build_nexus.PARTS["pin_collar"][1], "bone"),
    ("crown_arch_half", build_crown_arch_half.make, lambda: build_crown_arch_half.PRINT_ROT, "graphite"),
    ("apex_block", build_apex_block.make, lambda: build_apex_block.PRINT_ROT, "steel"),
    ("port_coupler", build_port_parts.coupler, lambda: L.ROT_NONE, "steel"),
    ("port_drill_guide", build_port_parts.drill_guide, lambda: L.ROT_NONE, "steel"),
    ("brow_center", build_brow_center.make, lambda: build_brow_center.PRINT_ROT, "bone"),
    ("brow_rail_L", lambda: build_brow_rail.make(+1), lambda: L.ROT_Y_TO_Z, "steel"),
    ("brow_rail_R", lambda: build_brow_rail.make(-1), lambda: L.ROT_NEGY_TO_Z, "steel"),
    ("brow_tab_L", lambda: build_brow_tab.make(+1), lambda: L.ROT_Y_TO_Z, "bone"),
    ("brow_tab_R", lambda: build_brow_tab.make(-1), lambda: L.ROT_NEGY_TO_Z, "bone"),
    ("brow_lid", build_brow_lid.make, lambda: build_brow_lid.PRINT_ROT, "bone"),
    *NAPE_ITEMS,
    ("pylon_base", lambda: build_pylon.base(+1), lambda: build_pylon.PARTS["pylon_base"][1], "steel"),
    ("pylon_blade", lambda: build_pylon.blade(+1, 0.0), lambda: build_pylon.PARTS["pylon_blade"][1], "graphite"),
    ("pylon_knob", lambda: build_pylon.knob(+1), lambda: build_pylon.PARTS["pylon_knob"][1], "bone"),
]


def add_print_layout():
    coll = collection("PrintLayout")
    bed, pitch, cols = 325.0, 385.0, 6
    for i, (name, mk, rot, color) in enumerate(PRINT_ITEMS):
        ob = mk()
        L.clean(ob)
        L.to_print_frame(ob, rot())
        col, row = i % cols, i // cols
        origin = Vector((col * pitch - (cols - 1) * pitch / 2, -900.0 - row * pitch, 0.0))
        ob.location = origin
        style(ob, f"print_{name}", color, coll)
        bpy.ops.mesh.primitive_plane_add(size=bed, location=origin - Vector((0, 0, 0.05)))
        style(bpy.context.active_object, f"bed_{name}", "bed", coll)
    lc = layer_coll("PrintLayout")
    if lc:
        lc.hide_viewport = True
    coll.hide_render = True


README = """HelmKit vp0.9 -- hand-editable assembly
=======================================
Units: 1 Blender unit = 1 mm. Frame: origin between the ear canals, +X forward,
+Y wearer's LEFT, +Z up. Disks are centred on BRAIN_CORE (10, 0, 35) and hang
at their centre from the CRADLE, which holds the head.

Collections
  Cradle           cradle_front (forehead + sides, hub / rear nodes, one PETG print), rear_band.L/.R
                   (tenon into the rear nodes, racks), Nape: nape_pinlock (print one) or the pull dial set
  Disks.L / Disks.R  disk_dome + disk_back (enclosed lens, six M3, coil cavity, tapped lock tab), nexus (Ø60 PETG flange bolted
                   through the hub node: bayonet stalk, lock ear, lanyard hole), nexus_spool (visor ring bearing),
                   pin_keeper (captive index nail), lock_knob (on the M3 lock screw), pin_collar
  Crown            crown_arch.L/.R (socket feet on the hub nodes via port_coupler.L/.R), apex_block
  Brow             brow_center (160 wide, LED bay), brow_rail.L/.R (ring on the nexus spool: pivot on the disk axis, 24 index holes),
                   brow_tab.L/.R (panel end to rail, two M3), brow_lid
  AddOns           pylon_base / blade / knob (rear node sockets)
  Reference        NOT printed: head, foam blocks, coil apparatus, index nails + springs, nape nail, crown / nape pads
  PrintLayout      hidden; every printed part in print orientation on a 325x325 bed

Disks: seat on the nexus flange with the lugs in the notches, quarter turn to the stop, M3 x 20 lock screw (knob) from the head side through the ear into the plate's tapped boss.
Brow: pull the index nail head above the keeper, tilt in 15 deg steps about the disk centre (one step down = eye level,
60 deg up = parked), let the spring drop it back. Reach is fixed (two M3 per side, rail to tab).
Pylons: serrated hinge, hand knob locks it. Crown arch: cross-bolts out of the couplers, lift off.
Nape (pinlock): slide the racks through, drop the 2 mm nail through the hole whose tooth spaces line up (whole / half pitch).
Cables run on the inside of the band under the foam. Chin strap: slot pairs behind the hub nodes and on the rear halves.

Editing: numbers -> tools/blender/vp0/canon.py, re-run assemble_vp0.py (overwrites
this file). Shapes -> edit here, rotate to print orientation, Export STL, Selection Only.
Reports: renders/clearance.txt, mass.txt, collisions.txt, snag.txt
Spec: docs/mechanical/vp0_visual_prototype.md
"""


def add_readme():
    t = bpy.data.texts.get("README_vp0") or bpy.data.texts.new("README_vp0")
    t.clear()
    t.write(README)


def tune_ui():
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type != "VIEW_3D":
                continue
            for sp in area.spaces:
                if sp.type == "VIEW_3D":
                    sp.clip_start = 1.0
                    sp.clip_end = 20000.0
                    sp.shading.color_type = "MATERIAL"
                    sp.shading.show_cavity = True


# ---------------------------------------------------------------------------
# reports
# ---------------------------------------------------------------------------

def standoff(p):
    cz = C.HEAD.phantom_center_z
    F = C.HEAD.implicit(p.x, p.y, p.z)
    s = math.sqrt(max(F, 1e-12))
    r = math.sqrt(p.x ** 2 + p.y ** 2 + (p.z - cz) ** 2)
    return r - r / s


def clearance_report(P):
    bpy.context.view_layer.update()
    lines = ["head-phantom clearance (scaled-radial, mm); negative = inside the phantom"]
    for name, ob in P.items():
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        so = [standoff(p) for p in pts]
        i = min(range(len(so)), key=lambda j: so[j])
        lines.append(f"  {ob.name:20s} min {min(so):7.1f} at ({pts[i].x:5.0f},{pts[i].y:5.0f},{pts[i].z:5.0f})   max {max(so):6.1f}   verts inside: {sum(1 for d in so if d < 0)}")
    return "\n".join(lines)


def mass_report(P):
    bpy.context.view_layer.update()
    rows, tot_m, tot_c = [], 0.0, Vector((0.0, 0.0, 0.0))
    for name, ob in P.items():
        V, c = L.mass_props(ob)
        m = abs(V) / 1000.0 * C.DENSITY_G_CM3
        rows.append((ob.name, m, c))
        tot_m += m
        tot_c += c * m
    cg = tot_c / tot_m if tot_m else Vector((0, 0, 0))
    g = 9.81e-3
    lines = [f"solid {C.MATERIAL.split()[0]} mass per printed part (as-printed with 20% infill ~ 0.75x for thick parts)"]
    for n, m, c in sorted(rows, key=lambda r: -r[1]):
        lines.append(f"  {n:20s} {m:6.0f} g   centroid ({c.x:6.1f}, {c.y:6.1f}, {c.z:6.1f})")
    lines.append(f"  TOTAL printed {tot_m:.0f} g solid; ~{tot_m*0.75:.0f} g as printed (+ ~40 g foam, ~40 g bolts/nails/rope/epoxy)")
    lines.append(f"  CG ({cg.x:.1f}, {cg.y:.1f}, {cg.z:.1f})  [brain core at {C.BRAIN_CORE}]")
    lines.append(f"  pitch moment about the ear axis: {tot_m*g*cg.x/1000:+.3f} N*m (+ = nose-down)")
    nx, ny, nz = C.NECK_PIVOT
    lines.append(f"  pitch moment about the neck pivot {C.NECK_PIVOT}: {tot_m*g*(cg.x-nx)/1000:+.3f} N*m")
    return "\n".join(lines)


def collision_report(P, label):
    bpy.context.view_layer.update()
    names = list(P)
    bvh = {n: L.bvh_of(P[n]) for n in names}
    expected = {("dome", "back"), ("back", "nexus"), ("nexus", "spool"), ("cradle", "spool"), ("cradle", "nexus"), ("spool", "rail"),
                ("nexus", "rail"), ("cradle", "rail"), ("cradle", "keeper"), ("nexus", "knob"), ("back", "knob"), ("cradle", "collar"), ("keeper", "collar"),
                ("cradle", "arch"), ("arch", "arch"), ("arch", "apex"), ("cradle", "coupler"), ("arch", "coupler"),
                ("rail", "tab"), ("panel", "tab"), ("panel", "lid"), ("cradle", "rear"),
                ("rear", "nape"), ("nape", "nape"), ("cradle", "pylon"), ("pylon", "pylonb"), ("pylon", "pylonk"),
                ("pylonb", "pylonk")}
    lines = [f"collisions [{label}] (BVH face-overlap pairs; 'expected' = designed contact)"]
    hits = 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pairs = bvh[a].overlap(bvh[b])
            if pairs:
                ka, kb = re.sub(r"\d+", "", a.split("_")[0]), re.sub(r"\d+", "", b.split("_")[0])
                exp = (ka, kb) in expected or (kb, ka) in expected
                c = Vector((0.0, 0.0, 0.0))
                for fa, fb in pairs[:50]:
                    c += P[a].matrix_world @ P[a].data.polygons[fa].center
                c /= min(len(pairs), 50)
                lines.append(f"  {P[a].name:20s} x {P[b].name:20s} {len(pairs):5d} faces {'(expected)' if exp else '<-- CHECK'} near ({c.x:.0f}, {c.y:.0f}, {c.z:.0f})")
                hits += 0 if exp else 1
    lines.append(f"  unexpected overlaps: {hits}")
    return "\n".join(lines)


def snag_report(P, R):
    bpy.context.view_layer.update()
    lines = ["snag scan: max standoff from the head per printed part, and the outermost points"]
    ext = {"front(+x)": (None, -1e9), "back(-x)": (None, 1e9), "top(+z)": (None, -1e9), "side(|y|)": (None, -1e9)}
    rows = []
    for name, ob in P.items():
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        so = [standoff(p) for p in pts]
        i = max(range(len(so)), key=lambda k: so[k])
        rows.append((ob.name, so[i], pts[i]))
        for p in pts:
            if p.x > ext["front(+x)"][1]: ext["front(+x)"] = (ob.name, p.x)
            if p.x < ext["back(-x)"][1]: ext["back(-x)"] = (ob.name, p.x)
            if p.z > ext["top(+z)"][1]: ext["top(+z)"] = (ob.name, p.z)
            if abs(p.y) > ext["side(|y|)"][1]: ext["side(|y|)"] = (ob.name, abs(p.y))
    for n, mx, pm in sorted(rows, key=lambda r: -r[1]):
        lines.append(f"  {n:20s} {mx:6.1f} mm at ({pm.x:5.0f},{pm.y:5.0f},{pm.z:5.0f})")
    a, b, c = C.HEAD.phantom_semi
    lines.append(f"  extremes (head: front {a:.0f}, back {-a:.0f}, top {C.HEAD.vertex_z_mm:.0f}, side {b:.1f}):")
    for k, (n, v) in ext.items():
        lines.append(f"    {k:11s} {v:7.1f}  {n}")
    lines.append("  loops (gap between band and head; pads listed in Reference close these):")
    for k, lab in (("cradle", "cradle U"), ("rear_L", "rear band"), ("arch_L", "crown arch"), ("panel", "brow centre"), ("rail_L", "brow rail"), ("back_L", "disk back"), ("nexus_L", "nexus")):
        pts = [P[k].matrix_world @ v.co for v in P[k].data.vertices]
        so = [standoff(p) for p in pts]
        i = min(range(len(so)), key=lambda j: so[j])
        lines.append(f"    {lab:12s} min {min(so):5.1f} at ({pts[i].x:.0f},{pts[i].y:.0f},{pts[i].z:.0f})  median {sorted(so)[len(so)//2]:5.1f}  max {max(so):5.1f}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------

def setup_render(scene, res=(1600, 1200)):
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_shadows = True
    sh.show_object_outline = True
    scene.display.render_aa = "8"
    scene.render.resolution_x, scene.render.resolution_y = res
    w = bpy.data.worlds.new("W")
    w.color = (0.92, 0.92, 0.93)
    scene.world = w
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 50
    cam_data.clip_end = 20000
    cam = bpy.data.objects.new("cam", cam_data)
    collection("Rig").objects.link(cam)
    scene.camera = cam
    return cam


def aim(cam, loc, target=(0.0, 0.0, 40.0)):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


VIEWS = {"front34": (700.0, 620.0, 420.0), "front": (1050.0, 0.0, 120.0), "side": (0.0, 1050.0, 120.0),
         "back34": (-700.0, -620.0, 420.0), "top": (1.0, 0.0, 1050.0), "back": (-1050.0, 0.0, 60.0)}


def render_views(scene, cam, out_dir, prefix, views=VIEWS):
    for name, loc in views.items():
        aim(cam, loc)
        scene.render.filepath = str(out_dir / f"{prefix}_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", scene.render.filepath)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--blend", default=DEFAULT_BLEND)
    ap.add_argument("--no-head", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-layout", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    L.reset_scene()
    scene = bpy.context.scene
    P, R = build_assembly(with_head=not args.no_head)
    cam = setup_render(scene)
    for fname, fn in (("clearance.txt", lambda: clearance_report(P)), ("mass.txt", lambda: mass_report(P)),
                      ("collisions.txt", lambda: collision_report(P, "worn")), ("snag.txt", lambda: snag_report(P, R))):
        rep = fn()
        (out / fname).write_text(rep + "\n")
        print(rep)
    if not args.no_render:
        render_views(scene, cam, out, "worn")
        for k in ("head",):
            if k in R:
                R[k].hide_render = True
        render_views(scene, cam, out, "nohead", views={"front34": VIEWS["front34"], "side": VIEWS["side"]})
        for k in ("head",):
            if k in R:
                R[k].hide_render = False
    if not args.no_layout:
        add_print_layout()
    add_readme()
    aim(cam, VIEWS["front34"])
    tune_ui()
    if args.blend:
        bp = Path(args.blend).resolve()
        bp.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(bp), compress=True)
        print("saved", bp)


if __name__ == "__main__":
    main()
