#!/usr/bin/env -S blender --background --python
"""
assemble_vp0.py -- build every vp0.3 part in the assembly frame, run the reports,
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
import build_pod_shell, build_crown_arch_half, build_apex_block
import build_brow_center, build_brow_wing, build_brow_lid, build_rear_band_half, build_nape_dial
import build_port_parts, build_fit_coupon

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


def coupler_at(name, length, Mmouth):
    """Coupler centred so one plug sits in the pod socket and the other reaches the far socket."""
    c = L.coupler(name, length)
    return placed(c, Mmouth @ Matrix.Translation((0.0, 0.0, length / 2.0 - C.PORT_PLUG_LEN)))


# ---------------------------------------------------------------------------

def build_assembly(with_head=True):
    P, R = {}, {}      # P = printed parts, R = reference (foam, head, spring)
    for side, tag in ((+1, "L"), (-1, "R")):
        pods = collection(f"Pods.{tag}")
        P[f"pod_{tag}"] = style(build_pod_shell.make(side), f"pod_shell.{tag}", "graphite", pods)
        links = collection("Couplers")
        P[f"cpl_crown_{tag}"] = style(coupler_at("c", C.COUPLER_CROWN_LEN, L.pod_port_frame(90.0, side)), f"coupler_crown.{tag}", "steel", links)
        P[f"cpl_rear_{tag}"] = style(coupler_at("c", C.COUPLER_REAR_LEN, L.pod_port_frame(C.REAR_PORT_ANGLE, side)), f"coupler_rear.{tag}", "steel", links)
        add = collection("AddOns")
        P[f"strap_{tag}"] = style(placed(build_port_parts.strap_anchor(), L.pod_port_frame(300.0, side)), f"strap_anchor.{tag}", "steel", add)
        for ang in (135.0, 250.0):
            P[f"cover{int(ang)}_{tag}"] = style(placed(build_port_parts.cover(), L.pod_port_frame(ang, side)), f"port_cover{int(ang)}.{tag}", "steel", add)
    crown = collection("Crown")
    P["arch_L"] = style(build_crown_arch_half.make(), "crown_arch.L", "graphite", crown)
    P["arch_R"] = style(L.transformed_copy(P["arch_L"], build_crown_arch_half.right_half_matrix(), "crown_arch.R"), "crown_arch.R", "graphite", crown)
    P["apex"] = style(build_apex_block.make(), "apex_block", "steel", crown)
    brow = collection("Brow")
    P["panel"] = style(build_brow_center.make(), "brow_center", "bone", brow)
    P["lid"] = style(build_brow_lid.make(), "brow_lid", "bone", brow)
    P["wing_L"] = style(build_brow_wing.make(+1), "brow_wing.L", "bone", brow)
    P["wing_R"] = style(build_brow_wing.make(-1), "brow_wing.R", "bone", brow)
    rear = collection("Rear")
    P["rear_L"] = style(build_rear_band_half.make(), "rear_band.L", "graphite", rear)
    P["rear_R"] = style(L.transformed_copy(P["rear_L"], build_rear_band_half.right_half_matrix(), "rear_band.R"), "rear_band.R", "graphite", rear)
    P["nape_body"] = style(build_nape_dial.make_body(), "nape_body", "steel", rear)
    P["nape_cover"] = style(build_nape_dial.make_cover(), "nape_cover", "steel", rear)
    P["nape_lid"] = style(build_nape_dial.make_lid(), "nape_lid", "steel", rear)
    P["nape_dial"] = style(build_nape_dial.make_dial(), "nape_dial", "bone", rear)
    P["nape_pinion"] = style(build_nape_dial.make_pinion(), "nape_pinion", "bone", rear)

    ref = collection("Reference")
    if with_head:
        R["head"] = style(L.head_phantom(), "head_phantom", "skin", ref)
    for side, tag in ((+1, "L"), (-1, "R")):
        axis = "-Y" if side > 0 else "Y"
        R[f"cushion_{tag}"] = style(L.foam_ring("cushion", (C.CX, side * C.RIM_Y, C.CZ), C.DISH_R, C.CUSHION_ID / 2, C.CUSHION_T, axis=axis), f"ear_cushion.{tag}", "foam", ref)
        px, py = -86.0, side * 82.0
        z = build_rear_band_half.z_of(px)
        Mp = L.frame((px, py, z), (0.0, side, 0.0), (1.0, 0.0, 0.0))
        pw, ph_, pt = C.REAR_SIDE_PAD
        R[f"rearpad_{tag}"] = style(L.add_box_local("rearpad", Mp, (0.0, 0.0, -pt / 2 - C.REAR_T / 2), (pw, ph_, pt)), f"rear_side_pad.{tag}", "foam", ref)
    sx, sy, sz = C.APEX_SLEEVE
    apex_bottom = C.CROWN_APEX_Z - (C.CROWN_T + 0.4) / 2 - C.APEX_FLOOR_T
    pw, pl, pt = C.CROWN_PAD
    R["crownpad"] = style(L.add_box("crownpad", (C.CX, 0.0, apex_bottom - pt / 2), (pw, pl, pt)), "crown_pad", "foam", ref)
    bw, bh, bt = C.BROW_PAD
    R["browpad"] = style(L.add_box_local("browpad", build_brow_center.MP, (0.2 - bt / 2, 0.0, C.BROW_H / 2), (bt, bw, bh)), "brow_pad", "foam", ref)
    Mn = build_nape_dial.M
    nw, nh, nt = C.NAPE_PAD
    R["napepad"] = style(L.add_box_local("napepad", Mn, (0.0, 0.0, -C.NAPE_CH - C.NAPE_LID_T - nt / 2), (nw, nh, nt)), "nape_pad", "foam", ref)
    sp = C.NAPE_SPRING
    R["spring"] = style(L.add_cyl_local("spring", Mn, (0.0, 0.0, C.NAPE_BODY_W1 + sp["working"] / 2), sp["od"] / 2, sp["working"], axis="Z", verts=24), "nape_spring", "spring", ref)
    return P, R


PRINT_ITEMS = [
    ("fit_coupon", build_fit_coupon.make, lambda: build_fit_coupon.PRINT_ROT, "bone"),
    ("pod_shell", lambda: build_pod_shell.make(+1), lambda: build_pod_shell.PRINT_ROT, "graphite"),
    ("crown_arch_half", build_crown_arch_half.make, lambda: build_crown_arch_half.PRINT_ROT, "graphite"),
    ("apex_block", build_apex_block.make, lambda: build_apex_block.PRINT_ROT, "steel"),
    ("brow_center", build_brow_center.make, lambda: build_brow_center.PRINT_ROT, "bone"),
    ("brow_wing_L", lambda: build_brow_wing.make(+1), lambda: build_brow_wing.PRINT_ROT, "bone"),
    ("brow_wing_R", lambda: build_brow_wing.make(-1), lambda: build_brow_wing.PRINT_ROT, "bone"),
    ("brow_lid", build_brow_lid.make, lambda: build_brow_lid.PRINT_ROT, "bone"),
    ("rear_band_half", build_rear_band_half.make, lambda: build_rear_band_half.PRINT_ROT, "graphite"),
    ("nape_body", build_nape_dial.make_body, lambda: build_nape_dial.PARTS["nape_body"][1], "steel"),
    ("nape_cover", build_nape_dial.make_cover, lambda: build_nape_dial.PARTS["nape_cover"][1], "steel"),
    ("nape_lid", build_nape_dial.make_lid, lambda: build_nape_dial.PARTS["nape_lid"][1], "steel"),
    ("nape_dial", build_nape_dial.make_dial, lambda: build_nape_dial.PARTS["nape_dial"][1], "bone"),
    ("nape_pinion", build_nape_dial.make_pinion, lambda: build_nape_dial.PARTS["nape_pinion"][1], "bone"),
    ("port_coupler_crown", build_port_parts.PARTS["port_coupler_crown"][0], lambda: L.ROT_NONE, "steel"),
    ("port_coupler_rear", build_port_parts.PARTS["port_coupler_rear"][0], lambda: L.ROT_NONE, "steel"),
    ("coupler_drill_guide", build_port_parts.drill_guide, lambda: L.ROT_NONE, "steel"),
    ("socket_form", build_port_parts.socket_form, lambda: L.ROT_NONE, "steel"),
    ("port_plug_blank", build_port_parts.blank, lambda: L.ROT_X_TO_Z, "steel"),
    ("port_cover", build_port_parts.cover, lambda: L.ROT_NONE, "steel"),
    ("strap_anchor", build_port_parts.strap_anchor, lambda: L.ROT_X_TO_Z, "steel"),
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


README = """HelmKit vp0.5 -- hand-editable assembly
=======================================
Units: 1 Blender unit = 1 mm. Frame: origin between the ear canals, +X forward,
+Y wearer's LEFT, +Z up. Pods are centred on BRAIN_CORE (10, 0, 35).

Collections
  Pods.L / Pods.R  pod_shell: paraboloid shell, dome outside, six flush pinned sockets (20 mm deep) in the rim ring
  Couplers         four rounded 10 mm posts (print, or aluminium tube drilled with the guide)
  Crown            crown_arch.L/.R (same part, rope spine groove), apex_block
  Brow             brow_center (LED bay, top bead), brow_wing.L/.R (tenon + wing + integral spar + post), brow_lid
  Rear             rear_band.L/.R (same part, spine groove, rack), nape_body / cover / lid / dial / pinion
  AddOns           strap anchors (front-lower), covers (rear-upper, rear-lower)
  Reference        NOT printed: head, ear cushions, crown / brow / nape / rear pads, the nape spring
  PrintLayout      hidden; every printed part in print orientation on a 325x325 bed

Nape dial: press the face in and turn to loosen; turn to tighten. Spring 3/8 x 3/4 in.
Every socket: nail through both walls and the post, head counterbored and epoxied.
Bands: epoxy-soaked rope in the spine grooves. Blocks: thread-and-epoxy collar wraps.

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
        so = [standoff(ob.matrix_world @ v.co) for v in ob.data.vertices]
        lines.append(f"  {ob.name:20s} min {min(so):7.1f}   max {max(so):6.1f}   verts inside: {sum(1 for d in so if d < 0)}")
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
    lines.append(f"  TOTAL printed {tot_m:.0f} g solid; ~{tot_m*0.75:.0f} g as printed (+ ~45 g foam, ~20 g nails/rope/epoxy)")
    lines.append(f"  CG ({cg.x:.1f}, {cg.y:.1f}, {cg.z:.1f})  [brain core at {C.BRAIN_CORE}]")
    lines.append(f"  pitch moment about the ear axis: {tot_m*g*cg.x/1000:+.3f} N*m (+ = nose-down)")
    nx, ny, nz = C.NECK_PIVOT
    lines.append(f"  pitch moment about the neck pivot {C.NECK_PIVOT}: {tot_m*g*(cg.x-nx)/1000:+.3f} N*m")
    return "\n".join(lines)


def collision_report(P, label):
    bpy.context.view_layer.update()
    names = list(P)
    bvh = {n: L.bvh_of(P[n]) for n in names}
    expected = {("pod", "cpl"), ("cpl", "arch"), ("cpl", "rear"), ("pod", "strap"), ("pod", "cover"), ("arch", "arch"),
                ("arch", "apex"), ("panel", "lid"), ("panel", "wing"), ("pod", "wing"), ("rear", "nape"), ("nape", "nape"), ("pod", "arch")}
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
    for k, lab in (("arch_L", "crown arch"), ("rear_L", "rear band"), ("panel", "brow centre"), ("wing_L", "brow wing")):
        so = [standoff(P[k].matrix_world @ v.co) for v in P[k].data.vertices]
        lines.append(f"    {lab:12s} min {min(so):5.1f}  median {sorted(so)[len(so)//2]:5.1f}  max {max(so):5.1f}")
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
