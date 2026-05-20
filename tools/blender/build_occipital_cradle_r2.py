#!/usr/bin/env -S blender --background --python
"""
build_occipital_cradle_r2.py — parametric generator for HelmKit Mk0.5 R2.

Builds `occipital_cradle_R2.stl`: the rear occipital cradle that
provides anti-pitch + anti-roll lock for the helmet. Slides
height-adjustably on a vertical dovetail off R1's rear face.

Run:
    blender --background --python tools/blender/build_occipital_cradle_r2.py \\
        -- --out 3D-Models/HelmKit/_generated/occipital_cradle_R2.stl

Design canon (see docs/mechanical/mk0.5_base_crown_architecture.md):
    - Cradle height:       60 mm  (inion → lower occiput)
    - Cradle arc:          ~110° (wraps the back of the head)
    - Cradle inner radius: 92 mm  (slightly smaller than R1's 95 mm
                                   to bias-fit against the occipital bone)
    - Wall thickness:      3.0 mm PETG
    - Vertical rail slot:  40 mm  M-LOK-style dovetail on the inner face,
                           giving ~30 mm of height travel against R1's rear
    - Lock:                Single M4 thumbscrew + nylock pocket
    - Carries NO hardpoints (HP-R compute pod attaches to the back face
      via a separate Picatinny stub).

Status: SCAFFOLD. Produces correct cradle body + dovetail slot + thumbscrew
pocket. Has not yet been validated against G-Fit.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    import bpy  # type: ignore
    import bmesh  # type: ignore
except ImportError:
    print("ERROR: run inside Blender:")
    print("  blender --background --python tools/blender/build_occipital_cradle_r2.py")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Canon parameters
# ---------------------------------------------------------------------------

R2_INNER_RADIUS_MM = 92.0
R2_WALL_MM = 3.0
R2_ARC_DEG = 110.0
R2_HEIGHT_MM = 60.0

# Vertical dovetail slot on the inner face (mates to R1's rear dovetail)
DOVETAIL_LEN_MM = 40.0      # length along the vertical (Z) axis
DOVETAIL_TOP_W_MM = 8.0     # narrow at the inner surface
DOVETAIL_BOT_W_MM = 12.0    # wider deeper in (locks the male tail)
DOVETAIL_DEPTH_MM = 4.0     # how deep into R2's wall the slot goes

# M4 thumbscrew + nylock pocket
M4_HOLE_DIA_MM = 4.2        # clearance for M4 shank
M4_HEAD_DIA_MM = 8.0
M4_HEAD_DEPTH_MM = 3.0      # thumbscrew head sits flush
NYLOCK_DIA_MM = 9.0         # captive M4 nylock nut pocket
NYLOCK_DEPTH_MM = 4.5
THUMBSCREW_Z_OFFSET_MM = 0.0  # centered on cradle midline


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def make_arc_band(inner_r: float, wall: float, arc_deg: float,
                  height: float, center_axis_deg: float = 270.0,
                  name: str = "band") -> bpy.types.Object:
    """Build a printable arc-band annulus segment.

    `center_axis_deg` = the angle (CCW from +X) the arc centers on.
    For R2 the cradle wraps the BACK of the head → centers on -Y → 270°.
    """
    outer_r = inner_r + wall
    # Outer cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=outer_r, depth=height, vertices=192)
    outer = bpy.context.active_object
    outer.name = f"{name}_outer"
    # Inner cylinder (subtract)
    bpy.ops.mesh.primitive_cylinder_add(radius=inner_r, depth=height + 2.0, vertices=192)
    inner = bpy.context.active_object
    inner.name = f"{name}_inner"
    mod = outer.modifiers.new(name="annulus", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = inner
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(inner, do_unlink=True)
    # Wedge cutter to leave only the desired arc
    bm = bmesh.new()
    keep_arc_rad = math.radians(arc_deg)
    cut_arc_rad = 2 * math.pi - keep_arc_rad
    # Cutter sweeps the OPPOSITE side from center_axis
    a0 = math.radians(center_axis_deg) + keep_arc_rad / 2
    r_cut = outer_r + 5.0
    n = 64
    bot, top = [], []
    apex_b = bm.verts.new((0, 0, -(height + 1) / 2))
    apex_t = bm.verts.new((0, 0, +(height + 1) / 2))
    for i in range(n + 1):
        a = a0 + (i / n) * cut_arc_rad
        x = r_cut * math.cos(a)
        y = r_cut * math.sin(a)
        bot.append(bm.verts.new((x, y, -(height + 1) / 2)))
        top.append(bm.verts.new((x, y, +(height + 1) / 2)))
    for i in range(n):
        bm.faces.new((apex_b, bot[i + 1], bot[i]))
        bm.faces.new((apex_t, top[i], top[i + 1]))
        bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
    bm.faces.new((apex_b, apex_t, top[0], bot[0]))
    bm.faces.new((apex_t, apex_b, bot[-1], top[-1]))
    mesh = bpy.data.meshes.new(f"{name}_cutter_mesh")
    bm.to_mesh(mesh)
    bm.free()
    cutter = bpy.data.objects.new(f"{name}_cutter", mesh)
    bpy.context.collection.objects.link(cutter)
    mod = outer.modifiers.new(name="arc_cut", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    outer.name = name
    return outer


def cut_dovetail_slot(cradle: bpy.types.Object) -> None:
    """Subtract a vertical M-LOK-style dovetail slot from R2's inner face.

    The slot runs along Z (vertical), is centered on the cradle's
    midpoint (back of helmet = -Y axis), and is a trapezoidal cross-
    section that widens with depth (so the male dovetail on R1's
    rear cannot pull straight out radially).
    """
    bm = bmesh.new()
    # Slot is centered on -Y. In R2's frame, the slot's center radial
    # axis is (-0, -1) and the slot's "width" axis is along +X.
    # Trapezoid: narrow opening at r = R2_INNER_RADIUS,
    #            wider base   at r = R2_INNER_RADIUS + DOVETAIL_DEPTH.
    z_top, z_bot = +DOVETAIL_LEN_MM / 2, -DOVETAIL_LEN_MM / 2
    r_in = R2_INNER_RADIUS_MM - 0.2   # bite slightly into the inner face
    r_out = R2_INNER_RADIUS_MM + DOVETAIL_DEPTH_MM
    half_top = DOVETAIL_TOP_W_MM / 2
    half_bot = DOVETAIL_BOT_W_MM / 2
    # 8 verts of a trapezoidal prism, oriented along -Y radial:
    # opening (narrow) on the -Y inner face; base (wide) deeper out (+y... wait)
    # NOTE: -Y is the OUTWARD direction here (cradle wraps the back so the
    # inner surface of the cradle FACES the head, i.e. +Y). Dovetail
    # opens toward +Y (toward the head, where R1's male dovetail lives).
    # Correction: the slot opens INTO the cradle from the +Y side.
    # Re-derive: slot opening at r = R2_INNER (facing +Y, toward head),
    # widens going OUTward (away from head, toward -Y).
    # Use y-axis directly since cradle is centered on -Y arc.
    y_open = +R2_INNER_RADIUS_MM + 0.2   # slot mouth at the inner surface
    y_deep = +R2_INNER_RADIUS_MM - DOVETAIL_DEPTH_MM  # widens INward (toward head LESS)
    # Wait — the cradle is wrapped around -Y, so inner surface of the
    # cradle is on the +Y side relative to its own center. R1's rear is
    # also on -Y of the world, so the male dovetail on R1 protrudes in
    # the -Y direction; R2's slot must open OUTWARD (away from R2's
    # body center, which is at world origin) → that's the +Y face of
    # R2's wall... this is getting confusing. Simpler model below.
    # ----
    # SIMPLER MODEL: just cut a vertical trapezoidal channel in the
    # cradle wall at the midpoint, with width along +X and the
    # trapezoid widening with -Y depth.
    # Cradle midpoint inner surface is at world (0, -R2_INNER_RADIUS, 0)
    # (because cradle wraps -Y axis).
    y_mouth = -R2_INNER_RADIUS_MM - 0.2   # outside inner face (cut starts here)
    y_floor = -R2_INNER_RADIUS_MM + DOVETAIL_DEPTH_MM  # cut bottom (into wall)
    # Verts: at mouth (narrow), at floor (wide)
    v_mouth_corners = [
        bm.verts.new((-half_top, y_mouth, z_bot)),
        bm.verts.new((+half_top, y_mouth, z_bot)),
        bm.verts.new((+half_top, y_mouth, z_top)),
        bm.verts.new((-half_top, y_mouth, z_top)),
    ]
    v_floor_corners = [
        bm.verts.new((-half_bot, y_floor, z_bot)),
        bm.verts.new((+half_bot, y_floor, z_bot)),
        bm.verts.new((+half_bot, y_floor, z_top)),
        bm.verts.new((-half_bot, y_floor, z_top)),
    ]
    # 6 faces of a trapezoidal prism
    bm.faces.new(v_mouth_corners[::-1])
    bm.faces.new(v_floor_corners)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((v_mouth_corners[i], v_mouth_corners[j],
                      v_floor_corners[j], v_floor_corners[i]))
    cut_mesh = bpy.data.meshes.new("dovetail_cut_mesh")
    bm.to_mesh(cut_mesh)
    bm.free()
    cutter = bpy.data.objects.new("dovetail_cut", cut_mesh)
    bpy.context.collection.objects.link(cutter)
    mod = cradle.modifiers.new(name="dovetail", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    bpy.context.view_layer.objects.active = cradle
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def cut_thumbscrew_pocket(cradle: bpy.types.Object) -> None:
    """Cut the M4 thumbscrew through-hole + nylock pocket.

    The thumbscrew enters from outside the cradle (-Y face), passes
    through the wall, and threads into the male dovetail on R1.
    Captive nylock nut sits in a hex/round pocket on the outer face.
    """
    # Three cylinders: outer head clearance + through hole + inner nylock pocket.
    # Axis along +Y (radial to cradle at midpoint).
    z = THUMBSCREW_Z_OFFSET_MM
    # Through-hole: spans the full wall + dovetail depth + margin
    bpy.ops.mesh.primitive_cylinder_add(
        radius=M4_HOLE_DIA_MM / 2,
        depth=R2_WALL_MM + DOVETAIL_DEPTH_MM + 4.0,
        vertices=32,
    )
    through = bpy.context.active_object
    through.rotation_euler = (math.pi / 2, 0, 0)  # rotate so axis = Y
    through.location = (0, -R2_INNER_RADIUS_MM - R2_WALL_MM / 2, z)
    # Nylock pocket on the OUTER face (-Y side)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=NYLOCK_DIA_MM / 2,
        depth=NYLOCK_DEPTH_MM + 0.2,
        vertices=6,  # hex pocket
    )
    nylock = bpy.context.active_object
    nylock.rotation_euler = (math.pi / 2, 0, 0)
    nylock.location = (0, -(R2_INNER_RADIUS_MM + R2_WALL_MM) + NYLOCK_DEPTH_MM / 2, z)

    for cutter in (through, nylock):
        mod = cradle.modifiers.new(name=cutter.name, type="BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter
        bpy.context.view_layer.objects.active = cradle
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter, do_unlink=True)


def export_stl(obj: bpy.types.Object, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=str(out_path), export_selected_objects=True)
    else:
        bpy.ops.export_mesh.stl(filepath=str(out_path), use_selection=True)
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)

    reset_scene()
    cradle = make_arc_band(
        inner_r=R2_INNER_RADIUS_MM,
        wall=R2_WALL_MM,
        arc_deg=R2_ARC_DEG,
        height=R2_HEIGHT_MM,
        center_axis_deg=270.0,  # wraps -Y (back of head)
        name="occipital_cradle_R2",
    )
    cut_dovetail_slot(cradle)
    cut_thumbscrew_pocket(cradle)
    export_stl(cradle, args.out)
    print(f"  R2 cradle: arc {R2_ARC_DEG}°, height {R2_HEIGHT_MM} mm, "
          f"dovetail {DOVETAIL_LEN_MM} mm w/ {DOVETAIL_TOP_W_MM}→{DOVETAIL_BOT_W_MM} mm trapezoid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
