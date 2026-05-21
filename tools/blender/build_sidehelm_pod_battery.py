#!/usr/bin/env -S blender --background --python
"""
build_sidehelm_pod_battery.py - HP-SL battery pod for the Mk0.5-beta helm.

Sliding-dovetail pod on the LEFT temple. Houses 1x 18650 or pouch
LiPo (~110 g loaded). Mates to Temple Plate sidehelm dovetail slot
via male dovetail on the inboard (+X-toward-head) face.

Run:
    blender --background --python tools/blender/build_sidehelm_pod_battery.py \\
        -- --out 3D-Models/HelmKit/_generated/sidehelm_pod_battery_r1.stl

Datum (pod-local):
    +X = head-ward  (inboard face carries the male dovetail rail)
    +Y = up
    +Z = forward

Pod envelope:
    70 x 50 x 40 mm (length X = depth fore/aft, width Y = vertical,
    height Z = -- but rotated to match plate). For build clarity we
    orient the pod with its long 70 mm axis along the head fore/aft
    line: X=mounting depth (40), Y=height (50), Z=length (70).

Dovetail (mates to IFACE_TEMPLE_SIDEHELM_POD female slot on plate):
    top width 12, bottom width 18, depth 3.4, length 35 (along +Z).

Interfaces consumed:
    IFACE_TEMPLE_SIDEHELM_POD
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

try:
    import bpy  # type: ignore
    import bmesh  # type: ignore
    from mathutils import Vector  # type: ignore
except ImportError:
    print("ERROR: run inside Blender")
    sys.exit(1)

from interfaces import (  # type: ignore  # noqa: E402
    IFACE_TEMPLE_SIDEHELM_POD,
    M3_CLEAR_DIA_MM,
)


# Pod outer envelope -- choose orientation: X depth, Y height, Z length
POD_X = 40.0
POD_Y = 50.0
POD_Z = 70.0
WALL = 2.5

DT_TOP_W = IFACE_TEMPLE_SIDEHELM_POD.dovetail_top_w_mm     # 12
DT_BOT_W = IFACE_TEMPLE_SIDEHELM_POD.dovetail_bottom_w_mm  # 18
DT_DEPTH = IFACE_TEMPLE_SIDEHELM_POD.dovetail_depth_mm     # 3.4
DT_LEN = IFACE_TEMPLE_SIDEHELM_POD.dovetail_length_mm      # 35

M3_CLR = M3_CLEAR_DIA_MM + 0.2

# Battery cell cradle interior: 18650 cell is ~18 x 65 mm; carve a cradle
CELL_DIA = 18.5
CELL_LEN = 66.0


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def _bool(host, tool, op="DIFFERENCE"):
    mod = host.modifiers.new(name=f"b_{tool.name[:20]}", type="BOOLEAN")
    mod.operation = op
    mod.object = tool
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = host
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def _add_box(name, center, dims):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    o = bpy.context.active_object
    o.name = name
    o.location = center
    o.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return o


def _add_cyl(name, center, radius, depth, axis="Z", verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    if axis == "X":
        o.rotation_euler = (0.0, math.pi / 2.0, 0.0)
    elif axis == "Y":
        o.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    o.location = center
    return o


def _add_male_dovetail(name, center, top_w, bot_w, depth, length):
    """Build a male dovetail prism (trapezoid cross-section, swept along Z).
    Trapezoid in the XY plane: bottom (head-side) wider than top (outer).
    Centered at `center`; rises +X from the inboard face by `depth`.
    """
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    # Cross-section (in local frame, before translation): rectangle on
    # plate side (x=0) widening into pod by depth. We'll model the
    # trapezoid as 4 points in XY then extrude along Z.
    # Trapezoid: bottom (at x=0, into pod surface) is BOT_W wide;
    # top (at x=depth, sticking out further) is TOP_W wide.
    # Sweep along Z (length axis).
    p1 = bm.verts.new((0.0, -bot_w / 2.0, -length / 2.0))
    p2 = bm.verts.new((0.0, +bot_w / 2.0, -length / 2.0))
    p3 = bm.verts.new((depth, +top_w / 2.0, -length / 2.0))
    p4 = bm.verts.new((depth, -top_w / 2.0, -length / 2.0))
    bm.faces.new((p1, p2, p3, p4))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    # Extrude the face along Z by `length`
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0.0, 0.0, length)}
    )
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    o.location = Vector(center)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    return o


def build_pod() -> bpy.types.Object:
    # Outer pod shell, centered at origin
    shell = _add_box("pod", (0.0, 0.0, 0.0), (POD_X, POD_Y, POD_Z))
    # Hollow interior
    cavity = _add_box("cavity",
                      (-WALL / 2.0, 0.0, 0.0),
                      (POD_X - 2 * WALL, POD_Y - 2 * WALL, POD_Z - 2 * WALL))
    _bool(shell, cavity, op="DIFFERENCE")
    # Male dovetail rail rises in +X from inboard face (+X side faces head)
    # Inboard face is at x = +POD_X/2; rail base sits flush at that face.
    rail = _add_male_dovetail("male_dt",
                              (POD_X / 2.0, 0.0, 0.0),
                              DT_TOP_W, DT_BOT_W, DT_DEPTH, DT_LEN)
    _bool(shell, rail, op="UNION")
    # 18650 cell cradle: cylindrical recess along Z axis inside cavity
    cradle = _add_cyl("cell_cradle",
                      (0.0, -POD_Y / 2.0 + WALL + CELL_DIA / 2.0 + 1.0, 0.0),
                      CELL_DIA / 2.0, CELL_LEN, axis="Z")
    _bool(shell, cradle, op="DIFFERENCE")
    # USB-C / power exit hole on -Z (rear) face
    usb = _add_box("usb_exit",
                   (0.0, 0.0, -POD_Z / 2.0),
                   (10.0, 4.5, WALL + 1.0))
    _bool(shell, usb, op="DIFFERENCE")
    # M3 thumbscrew lock slot at fore end of dovetail
    lock = _add_cyl("thumbscrew",
                    (POD_X / 2.0 + DT_DEPTH - 1.0, 0.0, DT_LEN / 2.0 - 4.0),
                    M3_CLR / 2.0, 8.0, axis="X")
    _bool(shell, lock, op="DIFFERENCE")
    shell.name = "sidehelm_pod_battery"
    return shell


def export_stl(obj, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=str(out_path), export_selected_objects=True)
    else:
        bpy.ops.export_mesh.stl(filepath=str(out_path), use_selection=True)
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


def write_sidecar(obj, out_path: Path) -> None:
    bb = [obj.matrix_world @ v.co for v in obj.data.vertices]
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    dx, dy, dz = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    est_mass_shell = (dx * dy * dz) / 1000.0 * 1.27 * 0.25
    out_path.with_suffix(".txt").write_text(
        "sidehelm_pod_battery_r1 (HP-SL, LEFT temple)\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  est_shell_mass_g (PETG): {est_mass_shell:.1f}\n"
        "  loaded_mass_target_g: 110 (shell + cell + harness)\n"
        f"  envelope_mm: {POD_X} x {POD_Y} x {POD_Z}\n"
        f"  wall_mm: {WALL}\n"
        "  male_dovetail (mates IFACE_TEMPLE_SIDEHELM_POD female slot):\n"
        f"    top_w={DT_TOP_W}  bot_w={DT_BOT_W}  depth={DT_DEPTH}  length={DT_LEN}\n"
        f"  cell_cradle: 18650 ({CELL_DIA} dia x {CELL_LEN} mm) along Z\n"
        "  USB-C exit slot on -Z (rear) face\n"
        "  M3 thumbscrew lock through dovetail fore end\n"
        "  interfaces_consumed:\n"
        "    - IFACE_TEMPLE_SIDEHELM_POD (dovetail spec)\n"
        "  imbalance_budget: |HP-SL - HP-SR| <= 65 g\n"
    )


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    reset_scene()
    obj = build_pod()
    export_stl(obj, args.out)
    write_sidecar(obj, args.out)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
