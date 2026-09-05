#!/usr/bin/env -S blender --background --python
"""
assemble_vp0.py -- build every vp0.2 part in the assembly frame, run the
engineering reports, render, and save the hand-editable .blend.

Reports written next to the renders:
  clearance.txt   min distance of each part to the head phantom (scaled-radial)
  mass.txt        solid-PETG mass + centroid per part, totals, CG, tipping moments
  collisions.txt  BVH overlap pairs in the worn and folded states

Run:
    blender --background --python tools/blender/vp0/assemble_vp0.py -- \\
        --out 3D-Models/HelmKit/_generated/vp0/renders \\
        [--blend 3D-Models/HelmKit_vp0/vp0_assembly.blend] [--no-head] [--no-render]
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore
import vp0lib as L
import canon as C
import build_pod_cup, build_reflector_insert, build_hub_bracket, build_thumb_knob
import build_crown_arch_half, build_apex_block
import build_brow_panel, build_brow_lid, build_brow_arm
import build_rear_band_half, build_nape_ratchet
import build_cheek_hook, build_port_parts, build_fit_coupon

COLORS = {"graphite": (0.10, 0.10, 0.11, 1.0), "accent": (0.80, 0.16, 0.12, 1.0), "bone": (0.86, 0.84, 0.78, 1.0),
          "steel": (0.55, 0.57, 0.60, 1.0), "skin": (0.72, 0.58, 0.48, 1.0), "bed": (0.30, 0.32, 0.36, 1.0)}
DEFAULT_BLEND = "3D-Models/HelmKit_vp0/vp0_assembly.blend"
PIVOT = Vector((C.CX, 0.0, C.CZ))
FOLD_ANGLES = {"rear": -75.0, "brow": +90.0}     # both swing DOWN (Ry: +x goes to -z for +angle)


# ---------------------------------------------------------------------------
# scene organisation
# ---------------------------------------------------------------------------

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
# build
# ---------------------------------------------------------------------------

def build_assembly(with_head=True):
    P = {}
    for side, tag in ((+1, "L"), (-1, "R")):
        pods = collection(f"Pods.{tag}")
        P[f"cup_{tag}"] = style(build_pod_cup.make(side), f"pod_cup.{tag}", "graphite", pods)
        P[f"refl_{tag}"] = style(build_reflector_insert.make(side), f"reflector.{tag}", "accent", pods)
        P[f"hub_{tag}"] = style(build_hub_bracket.make(side), f"hub_bracket.{tag}", "steel", pods)
        P[f"knob_{tag}"] = style(build_thumb_knob.make(side), f"thumb_knob.{tag}", "bone", pods)
        P[f"coupler_{tag}"] = style(placed(build_port_parts.coupler(), L.pod_port_frame(90.0, side)), f"port_coupler.{tag}", "steel", pods)
        add = collection("AddOns")
        P[f"cheek_{tag}"] = style(build_cheek_hook.make(side), f"cheek_hook.{tag}", "bone", add)
        P[f"batt_{tag}"] = style(placed(build_port_parts.battery_pack(), L.pod_port_frame(135.0, side)), f"battery_pack.{tag}", "graphite", add)
        for ang in (45.0, 240.0):
            P[f"cover{int(ang)}_{tag}"] = style(placed(build_port_parts.cover(), L.pod_port_frame(ang, side)), f"port_cover{int(ang)}.{tag}", "steel", add)
    crown = collection("Crown")
    P["arch_L"] = style(build_crown_arch_half.make(), "crown_arch.L", "graphite", crown)
    P["arch_R"] = style(L.transformed_copy(P["arch_L"], build_crown_arch_half.right_half_matrix(), "crown_arch.R"), "crown_arch.R", "graphite", crown)
    P["apex"] = style(build_apex_block.make(), "apex_block", "steel", crown)
    brow = collection("Brow")
    P["panel"] = style(build_brow_panel.make(), "brow_panel", "bone", brow)
    P["lid"] = style(build_brow_lid.make(), "brow_lid", "bone", brow)
    P["arm_L"] = style(build_brow_arm.make(+1), "brow_arm.L", "graphite", brow)
    P["arm_R"] = style(build_brow_arm.make(-1), "brow_arm.R", "graphite", brow)
    rear = collection("Rear")
    P["rear_L"] = style(build_rear_band_half.make(), "rear_band.L", "graphite", rear)
    P["rear_R"] = style(L.transformed_copy(P["rear_L"], build_rear_band_half.right_half_matrix(), "rear_band.R"), "rear_band.R", "graphite", rear)
    P["nape_body"] = style(build_nape_ratchet.make_body(), "nape_body", "steel", rear)
    P["nape_lid"] = style(build_nape_ratchet.make_lid(), "nape_lid", "steel", rear)
    P["nape_knob"] = style(build_nape_ratchet.make_knob(), "nape_knob", "bone", rear)
    P["nape_pawl"] = style(build_nape_ratchet.make_pawl(), "nape_pawl", "bone", rear)
    if with_head:
        P["head"] = style(L.head_phantom(), "head_phantom", "skin", collection("Phantom"))
    return P


def add_fold_rigs(P):
    rig = collection("Rig")
    rigs = {}
    groups = {"rear": ["rear_L", "rear_R", "nape_body", "nape_lid", "nape_knob", "nape_pawl"],
              "brow": ["panel", "lid", "arm_L", "arm_R"]}
    for key, members in groups.items():
        e = bpy.data.objects.new(f"FOLD_{key}", None)
        e.empty_display_type = "ARROWS"
        e.empty_display_size = 40.0
        e.location = PIVOT
        rig.objects.link(e)
        bpy.context.view_layer.update()          # matrix_world is stale until the depsgraph runs
        for m in members:
            P[m].parent = e
            P[m].matrix_parent_inverse = Matrix.Translation(-PIVOT)   # explicit: children stay where they are
        rigs[key] = e
    bpy.context.view_layer.update()
    return rigs


def fold(rigs, rear_deg, brow_deg):
    rigs["rear"].rotation_euler.y = math.radians(rear_deg)
    rigs["brow"].rotation_euler.y = math.radians(brow_deg)
    bpy.context.view_layer.update()


PRINT_ITEMS = [
    ("fit_coupon", build_fit_coupon.make, lambda: build_fit_coupon.PRINT_ROT, "bone"),
    ("pod_cup", lambda: build_pod_cup.make(+1), lambda: build_pod_cup.PRINT_ROT, "graphite"),
    ("reflector_insert", lambda: build_reflector_insert.make(+1), lambda: build_reflector_insert.PRINT_ROT, "accent"),
    ("hub_bracket", lambda: build_hub_bracket.make(+1), lambda: build_hub_bracket.PRINT_ROT, "steel"),
    ("thumb_knob", lambda: build_thumb_knob.make(+1), lambda: build_thumb_knob.PRINT_ROT, "bone"),
    ("crown_arch_half", build_crown_arch_half.make, lambda: build_crown_arch_half.PRINT_ROT, "graphite"),
    ("apex_block", build_apex_block.make, lambda: build_apex_block.PRINT_ROT, "steel"),
    ("brow_panel", build_brow_panel.make, lambda: build_brow_panel.PRINT_ROT, "bone"),
    ("brow_lid", build_brow_lid.make, lambda: build_brow_lid.PRINT_ROT, "bone"),
    ("brow_arm_L", lambda: build_brow_arm.make(+1), lambda: build_brow_arm.PRINT_ROT, "graphite"),
    ("brow_arm_R", lambda: build_brow_arm.make(-1), lambda: build_brow_arm.PRINT_ROT, "graphite"),
    ("rear_band_half", build_rear_band_half.make, lambda: build_rear_band_half.PRINT_ROT, "graphite"),
    ("nape_body", build_nape_ratchet.make_body, lambda: build_nape_ratchet.PARTS["nape_body"][1], "steel"),
    ("nape_lid", build_nape_ratchet.make_lid, lambda: build_nape_ratchet.PARTS["nape_lid"][1], "steel"),
    ("nape_knob", build_nape_ratchet.make_knob, lambda: build_nape_ratchet.PARTS["nape_knob"][1], "bone"),
    ("nape_pawl", build_nape_ratchet.make_pawl, lambda: build_nape_ratchet.PARTS["nape_pawl"][1], "bone"),
    ("cheek_hook_L", lambda: build_cheek_hook.make(+1), lambda: build_cheek_hook.print_rot(+1), "bone"),
    ("cheek_hook_R", lambda: build_cheek_hook.make(-1), lambda: build_cheek_hook.print_rot(-1), "bone"),
    ("port_coupler", build_port_parts.coupler, lambda: L.ROT_NONE, "steel"),
    ("port_plug_blank", build_port_parts.blank, lambda: L.ROT_X_TO_Z, "steel"),
    ("port_cover", build_port_parts.cover, lambda: L.ROT_NONE, "steel"),
    ("strap_anchor", build_port_parts.strap_anchor, lambda: L.ROT_X_TO_Z, "steel"),
    ("battery_pack", build_port_parts.battery_pack, lambda: L.ROT_Y_TO_Z, "graphite"),
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


README = """HelmKit vp0.2 -- hand-editable assembly
=======================================
Units: 1 Blender unit = 1 mm. Frame: origin between the ear canals, +X forward,
+Y wearer's LEFT, +Z up. Pods are centred on BRAIN_CORE (10, 0, 35).

Collections
  Pods.L / Pods.R  pod_cup, reflector, hub_bracket, thumb_knob, port_coupler
  Crown            crown_arch.L/.R (identical part), apex_block
  Brow             brow_panel, brow_lid, brow_arm.L/.R
  Rear             rear_band.L/.R (identical part), nape_body/lid/knob/pawl
  AddOns           cheek_hook.L/.R, battery_pack.L/.R (rear-upper ports), port covers
  Phantom          head_phantom (superellipsoid from the measured head) -- hide with the eye icon
  Rig              FOLD_rear / FOLD_brow empties at the pivot; rotate their Y to fold
                   (rear -75, brow +90 = both swing DOWN for storage)
  PrintLayout      hidden; every part in its print orientation on a 325x325 bed

Port standard: 10 mm square post, 15 mm socket, M3 cross-bolt 8 mm in, 4-pin
header pocket in the floor. Sockets: 5 per pod (45/90/135/240/300 deg), 2 on
the brow panel top edge, 1 on the apex block, 1 under each crown arch foot.

Editing: numbers -> tools/blender/vp0/canon.py then re-run assemble_vp0.py
(overwrites this file). Shapes -> edit here, rotate to print orientation
(see PrintLayout), File > Export > STL with Selection Only.
Reports: renders/clearance.txt, mass.txt, collisions.txt.
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

def clearance_report(P):
    bpy.context.view_layer.update()
    lines = ["head-phantom clearance (scaled-radial, mm); negative = inside the phantom"]
    for name, ob in P.items():
        if name == "head":
            continue
        worst, inside = 1e9, 0
        cz = C.HEAD.phantom_center_z
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            F = C.HEAD.implicit(p.x, p.y, p.z)
            s = math.sqrt(max(F, 1e-12))
            r = math.sqrt(p.x ** 2 + p.y ** 2 + (p.z - cz) ** 2)
            d = r - r / s
            if d < 0:
                inside += 1
            worst = min(worst, d)
        lines.append(f"  {ob.name:18s} {worst:7.1f} mm   verts inside: {inside}")
    return "\n".join(lines)


def mass_report(P):
    bpy.context.view_layer.update()
    rows, tot_m, tot_c = [], 0.0, Vector((0.0, 0.0, 0.0))
    for name, ob in P.items():
        if name == "head":
            continue
        V, c = L.mass_props(ob)
        m = abs(V) / 1000.0 * C.PETG_DENSITY_G_CM3
        rows.append((ob.name, m, c))
        tot_m += m
        tot_c += c * m
    cg = tot_c / tot_m if tot_m else Vector((0, 0, 0))
    g = 9.81e-3
    lines = ["solid-PETG mass per part (as-printed with 20% infill ~ 0.7-0.8x for thick parts)"]
    for n, m, c in sorted(rows, key=lambda r: -r[1]):
        lines.append(f"  {n:18s} {m:6.0f} g   centroid ({c.x:6.1f}, {c.y:6.1f}, {c.z:6.1f})")
    lines.append(f"  TOTAL (no hardware, no foam, no cells) {tot_m:.0f} g solid; ~{tot_m*0.75:.0f} g as printed")
    lines.append(f"  CG ({cg.x:.1f}, {cg.y:.1f}, {cg.z:.1f})  [ear canals at origin, brain core at {C.BRAIN_CORE}]")
    lines.append(f"  pitch moment about the ear axis: {tot_m*g*cg.x/1000:+.3f} N*m (+ = nose-down)")
    nx, ny, nz = C.NECK_PIVOT
    lines.append(f"  pitch moment about the neck pivot {C.NECK_PIVOT}: {tot_m*g*(cg.x-nx)/1000:+.3f} N*m")
    lines.append(f"  height of CG above the ear axis: {cg.z:.0f} mm (lower = less roll inertia on the neck)")
    return "\n".join(lines)


def collision_report(P, label, skip_head=False):
    bpy.context.view_layer.update()
    names = [n for n in P if not (skip_head and n == "head")]
    bvh = {n: L.bvh_of(P[n]) for n in names}
    expected = {("hub", "rear"), ("hub", "arm"), ("rear", "arm"), ("rear", "knob"), ("arm", "knob"),
                ("rear", "nape"), ("nape", "nape"), ("arch", "apex"), ("panel", "lid"), ("panel", "arm"),
                ("cup", "refl"), ("cup", "hub"), ("cup", "coupler"), ("arch", "coupler"), ("cup", "batt"),
                ("cup", "cover"), ("cup", "cheek"), ("cup", "arch"), ("arch", "arch")}
    lines = [f"collisions [{label}] (BVH face-overlap pairs; 'expected' = designed contact/interlock)"]
    hits = 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pairs = bvh[a].overlap(bvh[b])
            n = len(pairs)
            if n:
                ka, kb = a.split("_")[0].rstrip("0123456789"), b.split("_")[0].rstrip("0123456789")
                exp = (ka, kb) in expected or (kb, ka) in expected
                where = ""
                if not exp:
                    c = Vector((0.0, 0.0, 0.0))
                    for fa, fb in pairs[:50]:
                        c += P[a].matrix_world @ P[a].data.polygons[fa].center
                    c /= min(len(pairs), 50)
                    where = f" near ({c.x:.0f}, {c.y:.0f}, {c.z:.0f})"
                lines.append(f"  {P[a].name:18s} x {P[b].name:18s} {n:5d} faces {'(expected)' if exp else '<-- CHECK' + where}")
                hits += 0 if exp else 1
    lines.append(f"  unexpected overlaps: {hits}")
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
    P = build_assembly(with_head=not args.no_head)
    rigs = add_fold_rigs(P)
    cam = setup_render(scene)

    rep = clearance_report(P)
    (out / "clearance.txt").write_text(rep + "\n")
    print(rep)
    rep = mass_report(P)
    (out / "mass.txt").write_text(rep + "\n")
    print(rep)
    col = collision_report(P, "worn")
    fold(rigs, FOLD_ANGLES["rear"], FOLD_ANGLES["brow"])
    col += "\n" + collision_report(P, f"folded rear {FOLD_ANGLES['rear']} / brow {FOLD_ANGLES['brow']}", skip_head=True)
    fold(rigs, 0.0, 0.0)
    (out / "collisions.txt").write_text(col + "\n")
    print(col)

    if not args.no_render:
        render_views(scene, cam, out, "worn")
        if "head" in P:
            P["head"].hide_render = True
        fold(rigs, FOLD_ANGLES["rear"], FOLD_ANGLES["brow"])
        render_views(scene, cam, out, "folded", views={"front34": VIEWS["front34"], "side": VIEWS["side"]})
        fold(rigs, 0.0, 0.0)
        if "head" in P:
            P["head"].hide_render = False
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
