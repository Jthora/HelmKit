#!/usr/bin/env -S blender --background --python
"""
assemble_vp0.py -- build every vp0.11 part in the assembly frame, run the reports,
render, save the hand-editable .blend.

Reports (next to the renders): clearance.txt (head + ear phantoms), mass.txt, collisions.txt (worn pose, plus the
parked visor and the cable runs as check-only objects), snag.txt
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
import build_brow_center, build_brow_rail, build_brow_link, build_visor_slider, build_brow_lid, build_rear_band_half, build_nape_dial, build_spine_covers
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

def rot_about_z(x0):
    """180 deg about the vertical axis through (x0, 0): how a left print is physically reused on the right."""
    return Matrix.Translation((x0, 0.0, 0.0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-x0, 0.0, 0.0))


def rot_about_disk_axis(deg):
    return Matrix.Translation((C.CX, 0.0, C.CZ)) @ Matrix.Rotation(-math.radians(deg), 4, "Y") @ Matrix.Translation((-C.CX, 0.0, -C.CZ))


EAR = dict(center_x=-8.5, center_z=4.5, semi=(17.0, 10.0, 33.0), proud=9.0)   # pinna phantom: 33 long, 65 tall, sticks out 19 mm


def ear_center(side):
    """Ellipsoid centre: 9 mm outboard of the head surface at the pinna's centre (bisection on the phantom's implicit)."""
    lo, hi = 0.0, 120.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if C.HEAD.implicit(EAR["center_x"], mid, EAR["center_z"]) < 1.0:
            lo = mid
        else:
            hi = mid
    return Vector((EAR["center_x"], side * (lo + EAR["proud"]), EAR["center_z"]))


def ear_phantom(side):
    c = ear_center(side)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=48, ring_count=24, location=c)
    ob = bpy.context.active_object
    ob.scale = EAR["semi"]
    L.apply_transform(ob)
    return ob


def ear_standoff(p, side):
    c = ear_center(side)
    a, b, cc = EAR["semi"]
    F = ((p.x - c.x) / a) ** 2 + ((p.y - c.y) / b) ** 2 + ((p.z - c.z) / cc) ** 2
    r = (p - c).length
    return r - r / math.sqrt(max(F, 1e-12))


def cable(name, waypoints, dia=4.0):
    pts = L.resample_polyline([Vector(w) for w in L.catmull_rom(waypoints, samples_per_seg=8)], 2.0)
    h = dia / 2.0
    return L.ribbon(name, pts, Vector((0.0, 0.0, 1.0)), [(h, h, h, h)] * len(pts), chamfer=dia * 0.29)


def cable_runs(side):
    """Reference cable routes (Ø4 = a stripped ethernet pair with slack): coil feed straight through the plate / flange / node bores at
    (CX - 15, z 59.5) then inside the band under the foam, down the rear half to the nape and out; LED feed out through the band bore just ahead of the node
    at (36, z 55), up under the rail root into the rail's underside groove, along the link, into the panel."""
    s = side
    cb = C.CABLE_BORE
    xc, xl, zb = C.CX - cb["dx"], C.CX + cb["dx"], cb["z"]
    y_in = C.NODE_IN_Y - 1.5
    coil = [(xc, s * (C.DISK_IN_Y + 8.0), zb), (xc, s * (C.NODE_IN_Y - 2.0), zb), (xc, s * y_in, zb - 6.0), (-14.0, s * y_in, 50.0), (-28.0, s * y_in, 50.0),
            (-45.0, s * y_in, 45.0), (-62.0, s * 84.0, 30.0), (-80.0, s * 73.0, 8.0), (-98.0, s * 54.0, -12.0), (-106.0, s * 38.0, -22.0), (-109.0, s * 20.0, -27.0),
            (-110.0, 0.0, -42.0), (-110.0, 0.0, -80.0)]
    a = math.radians(C.RAIL_ANGLE)
    y_ch = s * (C.RAIL_Y0 + C.RAIL_T - 0.6 - C.RAIL_CHANNEL[1] / 2.0)
    t_ch = -C.RAIL_H / 2.0 - 1.0 + (C.RAIL_CHANNEL[0] + 1.0) / 2.0
    def rail_pt(sd, t, y=None):
        return (C.CX + sd * math.cos(a) - t * math.sin(a), y if y is not None else y_ch, C.CZ + sd * math.sin(a) + t * math.cos(a))
    Mb = build_brow_link.link_frame(side)
    def link_pt(u):
        v = Mb @ Vector((u, 0.0, t_ch))
        return (v.x, v.y, v.z)
    lx, lz = cb["led_x"], cb["led_z"]
    y_bo = C.CRADLE_SIDE_Y + C.CRADLE_T / 2.0
    led = [(lx, s * (y_bo - 12.0), lz - 4.0), (lx, s * (y_bo + 1.0), lz), (lx + 6.0, s * (y_bo + 2.5), lz - 15.0), (lx + 11.0, s * (y_bo + 4.5), lz - 27.0),
           (lx + 14.0, s * 103.5, lz - 28.0), rail_pt(42.0, t_ch - 2.0), rail_pt(48.0, t_ch), rail_pt(60.0, t_ch), rail_pt(70.0, t_ch), rail_pt(82.0, t_ch - 1.5),
           link_pt(6.0), link_pt(C.BROW_LINK_LEN * 0.5), link_pt(C.BROW_LINK_LEN - 2.0), link_pt(C.BROW_LINK_LEN + 5.0)]
    return cable(f"cable_coil.{'L' if s > 0 else 'R'}", coil), cable(f"cable_led.{'L' if s > 0 else 'R'}", led)


def build_assembly(with_head=True):
    P, R, Q = {}, {}, {}      # P = printed parts, R = reference (foam, head, springs, nails, coil), Q = check-only poses / routes
    add = collection("AddOns")
    for side, tag in ((+1, "L"), (-1, "R")):
        disks = collection(f"Disks.{tag}")
        P[f"dome_{tag}"] = style(build_disk.dome(side), f"disk_dome.{tag}", "graphite", disks)
        P[f"back_{tag}"] = style(build_disk.back(side), f"disk_back.{tag}", "graphite", disks)
        P[f"nexus_{tag}"] = style(build_nexus.flange(side), f"nexus.{tag}", "steel", disks)
        P[f"spool_{tag}"] = style(build_nexus.spool(side), f"nexus_spool.{tag}", "steel", disks)
        kb = C.DISK_KNOB
        Mk = Matrix.Translation((C.CX, side * (C.DISK_IN_Y + C.DISK_THICK + 0.2), C.CZ)) @ Matrix.Rotation(side * math.pi / 2, 4, "X")   # knob face outboard, shaft down the axis
        P[f"dknob_{tag}"] = style(placed(build_nexus.disk_knob(), Mk), f"disk_knob.{tag}", "bone", disks)
        Mc = Matrix.Translation((C.CX, side * (C.DISK_IN_Y + kb["clip_n"] - kb["clip"][2] / 2), C.CZ)) @ Matrix.Rotation(-side * math.pi / 2, 4, "X")
        P[f"clip_{tag}"] = style(placed(build_nexus.knob_clip(), Mc), f"knob_clip.{tag}", "bone", disks)
    # pylons: the right side is the LEFT print turned 180 deg about the vertical axis through its socket (what you actually do)
    P["pylon_L"] = style(build_pylon.base(+1), "pylon_base.L", "steel", add)
    P["pylonb_L"] = style(build_pylon.blade(+1), "pylon_blade.L", "graphite", add)
    P["pylonk_L"] = style(build_pylon.knob(+1), "pylon_knob.L", "bone", add)
    Mz = rot_about_z(C.REAR_SOCKET[0])
    for k, nm in (("pylon", "pylon_base"), ("pylonb", "pylon_blade"), ("pylonk", "pylon_knob")):
        P[f"{k}_R"] = style(L.transformed_copy(P[f"{k}_L"], Mz, f"{nm}.R"), f"{nm}.R", "steel" if k == "pylon" else ("graphite" if k == "pylonb" else "bone"), add)
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
    P["link_L"] = style(build_brow_link.make(+1), "brow_link.L", "bone", brow)
    P["link_R"] = style(build_brow_link.make(-1), "brow_link.R", "bone", brow)
    P["slider_L"] = style(build_visor_slider.make(+1), "visor_slider.L", "accent", brow)
    P["slider_R"] = style(build_visor_slider.make(-1), "visor_slider.R", "accent", brow)
    # spine cover strips: left ones built, right ones mirrored
    left, front_left, right = build_spine_covers.cradle_runs()
    P["cover_f_L"] = style(build_spine_covers.cover_front(front_left), "cover_front.L", "accent", cradle)
    P["cover_s_L"] = style(build_spine_covers.cover_side(left), "cover_side.L", "accent", cradle)
    P["cover_r_L"] = style(build_spine_covers.cover_rear(), "cover_rear.L", "accent", cradle)
    Mmir = Matrix.Diagonal((1.0, -1.0, 1.0, 1.0))
    for k, nm in (("cover_f", "cover_front"), ("cover_s", "cover_side")):
        ob = L.transformed_copy(P[f"{k}_L"], Mmir, f"{nm}.R"); L.recalc_normals(ob)
        P[f"{k}_R"] = style(ob, f"{nm}.R", "accent", cradle)
    P["cover_r_R"] = style(L.transformed_copy(P["cover_r_L"], build_rear_band_half.right_half_matrix(), "cover_rear.R"), "cover_rear.R", "accent", cradle)

    checks = collection("Checks")            # not printed, not in the mass: the parked visor pose and the cable runs
    Mp = rot_about_disk_axis(C.VISOR_PARK_DEG - C.RAIL_ANGLE)
    for tag in ("L", "R"):
        Q[f"railp_{tag}"] = style(L.transformed_copy(P[f"rail_{tag}"], Mp, f"brow_rail_parked.{tag}"), f"brow_rail_parked.{tag}", "bed", checks)
    for side, tag in ((+1, "L"), (-1, "R")):
        coil, led = cable_runs(side)
        Q[f"cablec_{tag}"] = style(coil, coil.name, "rope", checks)
        Q[f"cablel_{tag}"] = style(led, led.name, "rope", checks)

    ref = collection("Reference")
    if with_head:
        R["head"] = style(L.head_phantom(), "head_phantom", "skin", ref)
        for side, tag in ((+1, "L"), (-1, "R")):
            R[f"ear_{tag}"] = style(ear_phantom(side), f"ear_phantom.{tag}", "skin", ref)
    fb = C.FOAM_BLOCKS
    w, h, t = fb["forehead"]
    zf = C.CRADLE_Z + C.cradle_rise(C.CRADLE_FRONT_X) / 2.0
    R["foam_front"] = style(L.add_box("foam", (C.CRADLE_FRONT_X - C.CRADLE_T / 2 - t / 2, 0.0, zf), (t, w, h)), "foam_forehead", "foam", ref)
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
    for side, tag in ((+1, "L"), (-1, "R")):    # lock pins (7.2 mm of 3.2 nail in the stalk top), pawl springs, rope in the spine channels -- reference
        lk = C.BAYONET_LOCK
        R[f"lockpin_{tag}"] = style(L.add_cyl("lockpin", (C.CX, side * (C.DISK_IN_Y + lk["n"]), C.CZ + (4.8 + 12.0) / 2), lk["pin_dia"] / 2, lk["pin_len"], axis="Z", verts=12), f"lock_pin.{tag}", "spring", ref)
        vp = C.VISOR_PAWL
        Mr = build_brow_rail.rail_frame(C.RAIL_ANGLE, side)
        R[f"pspring_{tag}"] = style(L.add_cyl_local("pspring", Mr, ((vp["body_r"] + 1.0 + vp["r_spring"]) / 2, side * (vp["y0"] + vp["slot"][0] / 2), 0.0), 1.5, vp["r_spring"] - vp["body_r"] - 1.0, axis="X", verts=12), f"pawl_spring.{tag}", "spring", ref)
    left, front_left, right = build_spine_covers.cradle_runs()
    for nm, run in (("rope_side.L", left), ("rope_front", [p for p in build_cradle_front.spine_runs(build_cradle_front.centreline())[1]]), ("rope_side.R", right)):
        pts_r = build_cradle_front.offset_outboard(build_cradle_front.channel_pts(run), 1.0)
        R[nm] = style(L.ribbon("rope", pts_r, Vector((0.0, 0.0, 1.0)), [(1.0, 1.0, 1.0, 1.0)] * len(pts_r), chamfer=0.4), nm, "rope", ref)
    pw, pl, pt = C.CROWN_PAD
    apex_bottom = C.CROWN_APEX_Z - (C.CROWN_T + 0.4) / 2 - C.APEX_FLOOR_T
    R["crownpad"] = style(L.add_box("crownpad", (C.CX, 0.0, apex_bottom - pt / 2), (pw, pl, pt)), "crown_pad", "foam", ref)
    Mn = build_nape_dial.M
    nw, nh, nt = C.NAPE_PAD
    if C.NAPE_MODULE == "pinlock":
        R["napepad"] = style(L.add_box_local("napepad", Mn, (0.0, 0.0, -C.NAPE_PINLOCK_T / 2 - nt / 2), (nw, nh, nt)), "nape_pad", "foam", ref)
        for i, u in enumerate(C.NAPE_PINLOCK_HOLES[:3:2]):
            R[f"napenail{i}"] = style(L.add_cyl_local("napenail", Mn, (u, 0.0, 0.0), C.NAPE_PINLOCK_PIN["dia"] / 2, C.NAPE_HV - 1.0, axis="Y", verts=12), f"nape_nail.{i}", "spring", ref)
    else:
        R["napepad"] = style(L.add_box_local("napepad", Mn, (0.0, 0.0, -C.NAPE_CH - C.NAPE_LID_T - nt / 2), (nw, nh, nt)), "nape_pad", "foam", ref)
        sp = C.NAPE_SPRING
        w_floor = C.NAPE_DIAL_W0 + C.NAPE_DIAL_T - C.NAPE_SPRING_WELL[1]
        R["spring"] = style(L.add_cyl_local("spring", Mn, (0.0, 0.0, w_floor + sp["working"] / 2), sp["od"] / 2, sp["working"], axis="Z", verts=24), "nape_spring", "spring", ref)
    return P, R, Q


NAPE_ITEMS = ([("nape_pinlock", build_nape_dial.make_pinlock, lambda: build_nape_dial.PARTS["nape_pinlock"][1], "steel")] if C.NAPE_MODULE == "pinlock" else
              [(f"nape_{n}", getattr(build_nape_dial, f"make_{n}"), (lambda n=n: build_nape_dial.PARTS[f"nape_{n}"][1]), "steel" if n in ("body", "cover", "lid") else "bone")
               for n in ("body", "cover", "lid", "dial", "key", "pinion", "retainer")])
PRINT_ITEMS = [
    ("fit_coupon", build_fit_coupon.make, lambda: build_fit_coupon.PRINT_ROT, "bone"),
    ("cradle_front", build_cradle_front.make, lambda: build_cradle_front.PRINT_ROT, "accent"),
    ("rear_band_half", build_rear_band_half.make, lambda: build_rear_band_half.PRINT_ROT, "accent"),
    ("disk_dome", lambda: build_disk.dome(+1), lambda: build_disk.PARTS["disk_dome"][1], "graphite"),
    ("disk_back_L", lambda: build_disk.back(+1), lambda: build_disk.PARTS["disk_back_L"][1], "graphite"),
    ("disk_back_R", lambda: build_disk.back(-1), lambda: build_disk.PARTS["disk_back_R"][1], "graphite"),
    ("nexus_L", lambda: build_nexus.flange(+1), lambda: build_nexus.PARTS["nexus_L"][1], "steel"),
    ("nexus_R", lambda: build_nexus.flange(-1), lambda: build_nexus.PARTS["nexus_R"][1], "steel"),
    ("nexus_spool", lambda: build_nexus.spool(+1), lambda: build_nexus.PARTS["nexus_spool"][1], "steel"),
    ("disk_knob", build_nexus.disk_knob, lambda: build_nexus.PARTS["disk_knob"][1], "bone"),
    ("knob_clip", build_nexus.knob_clip, lambda: build_nexus.PARTS["knob_clip"][1], "bone"),
    ("cover_front", build_spine_covers.cover_front, lambda: build_spine_covers.PARTS["cover_front"][1], "accent"),
    ("cover_side", build_spine_covers.cover_side, lambda: build_spine_covers.PARTS["cover_side"][1], "accent"),
    ("cover_rear", build_spine_covers.cover_rear, lambda: build_spine_covers.PARTS["cover_rear"][1], "accent"),
    ("crown_arch_half", build_crown_arch_half.make, lambda: build_crown_arch_half.PRINT_ROT, "graphite"),
    ("apex_block", build_apex_block.make, lambda: build_apex_block.PRINT_ROT, "steel"),
    ("port_coupler", build_port_parts.coupler, lambda: L.ROT_NONE, "steel"),
    ("port_drill_guide", build_port_parts.drill_guide, lambda: L.ROT_NONE, "steel"),
    ("brow_center", build_brow_center.make, lambda: build_brow_center.PRINT_ROT, "bone"),
    ("brow_rail_L", lambda: build_brow_rail.make(+1), lambda: L.ROT_Y_TO_Z, "steel"),
    ("brow_rail_R", lambda: build_brow_rail.make(-1), lambda: L.ROT_NEGY_TO_Z, "steel"),
    ("brow_link_L", lambda: build_brow_link.make(+1), lambda: build_brow_link.PRINT_ROT, "bone"),
    ("brow_link_R", lambda: build_brow_link.make(-1), lambda: build_brow_link.PRINT_ROT, "bone"),
    ("visor_slider", lambda: build_visor_slider.make(+1), lambda: build_visor_slider.PRINT_ROT, "accent"),
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


README = """HelmKit vp0.11 -- hand-editable assembly
========================================
Units: 1 Blender unit = 1 mm. Frame: origin between the ear canals, +X forward,
+Y wearer's LEFT, +Z up. Disks are centred on BRAIN_CORE (10, 0, 35) and hang
at their centre from the CRADLE, which holds the head.

Collections
  Cradle           cradle_front (7 mm PETG band, lower edge rises at the forehead, SPINE channels in the outer face with flush cover
                   strips over a potted rope), rear_band.L/.R (tenon into the rear nodes, spine channel, racks), covers, Nape: nape_pinlock
  Disks.L / Disks.R  disk_dome (knob dish at the apex) + disk_back (cam bayonet groove, lock notch, cable hole; L/R mirrored), nexus (Ø68
                   PETG flange: hollow stalk with the lock-pin hole, coil-cable bore, lanyard hole; L/R mirrored), nexus_spool (ring
                   bearing with 24 pawl notches, top-bolt spacer), disk_knob (shaft + eccentric down the axis), knob_clip
  Crown            crown_arch.L/.R (socket feet on the hub nodes via port_coupler.L/.R), apex_block
  Brow             brow_center (link pockets in its back face), brow_rail.L/.R (Ø44 ring on the hub, pawl tunnel, half-lap), brow_link.L/.R
                   (lap onto the rail, 55 deg bend inboard into the panel's back), visor_slider.L/.R (pawl, thumb tab), brow_lid
  AddOns           pylon_base / blade / knob (rear node sockets); the right set is the left print turned about its socket
  Checks           NOT printed: the rails in the PARKED pose (43 deg) and the cable runs (coil feed through the bores and inside the band;
                   LED feed out of the band ahead of the node, under the rail root into its underside groove); they take part in the collision report
  Reference        NOT printed: head + ear phantoms, foam, coil apparatus, lock pins, pawl springs, spine rope, nape nails, pads
  PrintLayout      hidden; every printed part in print orientation on a 325x325 bed

Disks: lugs into the notches, quarter turn to the stop (the cam groove pulls the plate tight), turn the centre knob half a turn:
its eccentric pushes the stalk pin into the plate's notch. Half a turn back releases.
Visor: thumb on the tab at the rail root, pull 2 mm, swing, let go: the pawl drops into the next hub notch (15 deg). Two steps up = parked.
Brow: the links bend inboard behind the panel; nothing shows from the front. Reach = link length.
Spine: 2 mm rope in the outer-face channels, potted in steel epoxy, cover strips pressed in flush. Cables: stripped ethernet pairs,
coil feed straight through plate / flange / node into the band's inside; LED feed out of the band ahead of the node, in the rail and link undersides.
Nape (pinlock): slide the racks through, drop the two 2 mm nails through the hole pair whose tooth spaces line up.
Nexus bolts: M3 x 30 from OUTSIDE (disk off), nuts sit in hex pockets on the node's inner face under the foam.

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
    ear_rows = []
    for name, ob in P.items():
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        so = [standoff(p) for p in pts]
        i = min(range(len(so)), key=lambda j: so[j])
        lines.append(f"  {ob.name:20s} min {min(so):7.1f} at ({pts[i].x:5.0f},{pts[i].y:5.0f},{pts[i].z:5.0f})   max {max(so):6.1f}   verts inside: {sum(1 for d in so if d < 0)}")
        for side in (+1, -1):
            eo = [ear_standoff(p, side) for p in pts]
            j = min(range(len(eo)), key=lambda k: eo[k])
            if eo[j] < 15.0:
                ear_rows.append((eo[j], ob.name, pts[j]))
    lines.append(f"ear-phantom clearance (pinna ellipsoid {EAR['semi']} at x {EAR['center_x']}, z {EAR['center_z']}, {EAR['proud']} mm proud); parts within 15 mm, negative = touching the ear:")
    for d, n, p in sorted(ear_rows):
        lines.append(f"  {n:20s} {d:6.1f} at ({p.x:5.0f},{p.y:5.0f},{p.z:5.0f}){'   <-- CHECK' if d < 5.0 else ''}")
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


def collision_report(P, label, Q=None):
    bpy.context.view_layer.update()
    P = dict(P, **(Q or {}))
    names = list(P)
    bvh = {n: L.bvh_of(P[n]) for n in names}
    expected = {("dome", "back"), ("back", "nexus"), ("nexus", "spool"), ("cradle", "spool"), ("cradle", "nexus"), ("spool", "rail"),
                ("nexus", "rail"), ("cradle", "rail"), ("spool", "slider"), ("rail", "slider"), ("nexus", "slider"), ("railp", "slider"),
                ("dknob", "dome"), ("dknob", "nexus"), ("dknob", "back"), ("clip", "dknob"), ("clip", "dome"),
                ("cradle", "arch"), ("arch", "arch"), ("arch", "apex"), ("cradle", "coupler"), ("arch", "coupler"),
                ("rail", "link"), ("panel", "link"), ("panel", "lid"), ("cradle", "rear"), ("cover", "cradle"), ("cover", "rear"),
                ("rear", "nape"), ("nape", "nape"), ("cradle", "pylon"), ("pylon", "pylonb"), ("pylon", "pylonk"),
                ("pylonb", "pylonk"),
                ("railp", "rail"), ("railp", "spool"), ("railp", "link"), ("railp", "cablel"),
                ("cablel", "rail"), ("cablel", "link"), ("cablel", "panel"), ("cablel", "cradle"), ("cablel", "nexus"), ("cablel", "spool"),
                ("cablec", "back"), ("cablec", "nexus"), ("cablec", "cradle"), ("cablec", "rear"), ("cablec", "nape"), ("cablec", "cablec")}
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
    P, R, Q = build_assembly(with_head=not args.no_head)
    cam = setup_render(scene)
    for fname, fn in (("clearance.txt", lambda: clearance_report(P)), ("mass.txt", lambda: mass_report(P)),
                      ("collisions.txt", lambda: collision_report(P, "worn + parked visor + cables", Q)), ("snag.txt", lambda: snag_report(P, R))):
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
