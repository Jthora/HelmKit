#!/usr/bin/env -S blender --background --python
"""
assemble_vp0.py -- build every vp0 part in the assembly frame and save a
hand-editable .blend (plus renders + clearance report).

The .blend is organised for working in the Blender UI:
  Collections : Pods.L / Pods.R / Bands / Phantom / PrintLayout (hidden) / Rig
  Fold rigs   : rotate empties FOLD_rear / FOLD_brow about Y to fold the helm
  Materials   : graphite / accent / bone / skin, viewport + Principled colours
  Units       : 1 Blender unit = 1 mm (scene scale 0.001), viewport clip 20 m
  Text block  : README_vp0 (how the file is laid out, how to regenerate)

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
import build_side_cap, build_side_dish, build_crown_band, build_rear_band, build_brow_plate, build_thumb_nut, build_fit_coupon

COLORS = {
    "graphite": (0.10, 0.10, 0.11, 1.0),
    "accent": (0.80, 0.16, 0.12, 1.0),
    "bone": (0.86, 0.84, 0.78, 1.0),
    "skin": (0.72, 0.58, 0.48, 1.0),
    "bed": (0.30, 0.32, 0.36, 1.0),
}
DEFAULT_BLEND = "3D-Models/HelmKit_vp0/vp0_assembly.blend"


# ---------------------------------------------------------------------------
# Scene organisation helpers
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


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_assembly(with_head=True):
    parts = {}
    for side, tag in ((+1, "L"), (-1, "R")):
        pods = collection(f"Pods.{tag}")
        parts[f"cap_{tag}"] = style(build_side_cap.make(side), f"side_cap.{tag}", "graphite", pods)
        parts[f"dish_{tag}"] = style(build_side_dish.make(side), f"side_dish.{tag}", "accent", pods)
        parts[f"nut_{tag}"] = style(build_thumb_nut.make(side), f"thumb_nut.{tag}", "bone", pods)
    bands = collection("Bands")
    parts["crown"] = style(build_crown_band.make(), "crown_band", "graphite", bands)
    parts["rear"] = style(build_rear_band.make(), "rear_band", "graphite", bands)
    parts["brow"] = style(build_brow_plate.make(), "brow_plate", "bone", bands)
    if with_head:
        parts["head"] = style(L.head_phantom(), "head_phantom", "skin", collection("Phantom"))
    return parts


def add_fold_rigs(parts):
    """Empties on the ear axis; rotate their Y to fold the rear band / brow plate."""
    rig = collection("Rig")
    rigs = {}
    for key, label in (("rear", "FOLD_rear"), ("brow", "FOLD_brow")):
        e = bpy.data.objects.new(label, None)
        e.empty_display_type = "ARROWS"
        e.empty_display_size = 40.0
        e.rotation_mode = "XYZ"
        rig.objects.link(e)
        parts[key].parent = e
        rigs[key] = e
    return rigs


def fold(rigs, rear_deg, brow_deg):
    rigs["rear"].rotation_euler.y = math.radians(rear_deg)
    rigs["brow"].rotation_euler.y = math.radians(brow_deg)
    bpy.context.view_layer.update()


def add_print_layout():
    """Every part in its print orientation on its own 325x325 bed, off to the side, hidden."""
    coll = collection("PrintLayout")
    items = [
        ("fit_coupon", lambda: build_fit_coupon.make(), build_fit_coupon.PRINT_ROT, "bone"),
        ("side_cap", lambda: build_side_cap.make(+1), build_side_cap.PRINT_ROT, "graphite"),
        ("side_dish", lambda: build_side_dish.make(+1), build_side_dish.PRINT_ROT, "accent"),
        ("thumb_nut", lambda: build_thumb_nut.make(+1), build_thumb_nut.PRINT_ROT, "bone"),
        ("crown_band", build_crown_band.make, build_crown_band.PRINT_ROT, "graphite"),
        ("rear_band", build_rear_band.make, build_rear_band.PRINT_ROT, "graphite"),
        ("brow_plate", build_brow_plate.make, build_brow_plate.PRINT_ROT, "bone"),
    ]
    bed = 325.0
    pitch = bed + 60.0
    for i, (name, make, rot, color) in enumerate(items):
        ob = make()
        L.clean(ob)
        L.to_print_frame(ob, rot)
        col, row = i % 4, i // 4
        origin = Vector((col * pitch - 1.5 * pitch, -800.0 - row * pitch, 0.0))
        ob.location = origin
        style(ob, f"print_{name}", color, coll)
        bpy.ops.mesh.primitive_plane_add(size=bed, location=origin - Vector((0, 0, 0.05)))
        plane = bpy.context.active_object
        style(plane, f"bed_{name}", "bed", coll)
    lc = layer_coll("PrintLayout")
    if lc:
        lc.hide_viewport = True
    coll.hide_render = True
    return coll


README = """HelmKit vp0 -- hand-editable assembly
=====================================

Units: 1 Blender unit = 1 mm. Frame: origin between the ear canals,
+X forward, +Y wearer's LEFT, +Z up.

Collections
  Pods.L / Pods.R   side_cap, side_dish, thumb_nut per side
  Bands             crown_band (fixed), rear_band + brow_plate (fold)
  Phantom           head_phantom -- ellipsoid from the measured head; hide it (eye icon)
  Rig               FOLD_rear / FOLD_brow empties. Rotate their Y (N panel > Item)
                    to fold: rear ~ +100 deg, brow ~ -80 deg. Parts are parented to them.
  PrintLayout       hidden. Every part in its PRINT orientation on a 325x325 bed
                    (QIDI X-MAX3). Un-hide to check orientation / supports.

Editing workflow
  * Numbers change  -> edit tools/blender/vp0/canon.py, re-run assemble_vp0.py
                       (this file is overwritten) and the build_*.py exporters.
  * Shape change    -> edit the mesh here, then File > Export > STL with
                       "Selection Only" and "Apply Modifiers" for that part.
                       Rotate to print orientation first (see PrintLayout for
                       the intended orientation of each part).
  * Keep your edited copy under a new name if you want the generator output
    and your hand edits to coexist.

Regenerate everything: see tools/blender/vp0/README.md
Spec / print plan / BOM: docs/mechanical/vp0_visual_prototype.md
"""


def add_readme():
    t = bpy.data.texts.get("README_vp0") or bpy.data.texts.new("README_vp0")
    t.clear()
    t.write(README)
    return t


def tune_ui():
    """Viewport defaults baked into the file: material colours, cavity, far clip."""
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
                    sp.overlay.grid_scale = 1.0


# ---------------------------------------------------------------------------
# Render + report
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
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


VIEWS = {
    "front34": (700.0, 620.0, 420.0),
    "front": (1050.0, 0.0, 120.0),
    "side": (0.0, 1050.0, 120.0),
    "back34": (-700.0, -620.0, 420.0),
    "top": (1.0, 0.0, 1050.0),
}


def render_views(scene, cam, out_dir: Path, prefix: str, views=VIEWS):
    for name, loc in views.items():
        aim(cam, loc)
        scene.render.filepath = str(out_dir / f"{prefix}_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", scene.render.filepath)


def clearance_report(parts):
    """Min radial clearance of every part to the head phantom (ellipsoid), in mm.
    Negative = the part intersects the phantom. Approximate: scaled-radial."""
    a, b, c = C.HEAD.phantom_semi
    cz = C.HEAD.phantom_center_z
    lines = []
    for name, ob in parts.items():
        if name == "head":
            continue
        worst, inside = 1e9, 0
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            x, y, z = p.x, p.y, p.z - cz
            s = math.sqrt((x / a) ** 2 + (y / b) ** 2 + (z / c) ** 2)
            if s < 1e-6:
                continue
            r = math.sqrt(x * x + y * y + z * z)
            d = r - r / s
            if d < 0:
                inside += 1
            worst = min(worst, d)
        lines.append(f"  {ob.name:14s} min clearance {worst:7.1f} mm   verts inside phantom: {inside}")
    txt = "head-phantom clearance (scaled-radial, mm):\n" + "\n".join(lines)
    print(txt)
    return txt


# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--blend", default=DEFAULT_BLEND)
    ap.add_argument("--no-head", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    L.reset_scene()
    scene = bpy.context.scene
    parts = build_assembly(with_head=not args.no_head)
    rigs = add_fold_rigs(parts)
    add_print_layout()
    add_readme()
    cam = setup_render(scene)
    (out / "clearance.txt").write_text(clearance_report(parts) + "\n")

    if not args.no_render:
        render_views(scene, cam, out, "worn")
        if "head" in parts:
            parts["head"].hide_render = True
        fold(rigs, 100.0, -80.0)
        render_views(scene, cam, out, "folded", views={"front34": VIEWS["front34"], "side": VIEWS["side"]})
        fold(rigs, 0.0, 0.0)
        if "head" in parts:
            parts["head"].hide_render = False

    aim(cam, VIEWS["front34"])
    tune_ui()
    if args.blend:
        bp = Path(args.blend).resolve()
        bp.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(bp), compress=True)
        print("saved", bp)


if __name__ == "__main__":
    main()
