#!/usr/bin/env -S blender --background --python
"""
envelope_temple_stackup.py — Phase-3 collision-check geometry.

Single Temple Plate (L side) with ALL features placed as solid
primitive bosses/pads at their §12 canon coordinates. Purpose:
visually confirm 4 pivots + 3-bolt yoke cluster + cheek hook +
sidehelm-pod dovetail all fit on one plate without overlap.

Throwaway primitives — boxes, cylinders, cones only. No
booleans between features (we WANT to see overlaps as visible
intersections).

Run:
    /Applications/Blender.app/Contents/MacOS/Blender --background \\
        --python tools/blender/envelope_temple_stackup.py -- \\
        --out 3D-Models/HelmKit/_envelopes/temple_stackup.stl

Source-of-truth: docs/mechanical/mk0.5_topology_beta_architecture.md
§12 IFACE_TEMPLE_FWDBAND/REARBAND/PYLON/DEFENDER/CHEEK/SIDEHELM_POD.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    import bpy  # type: ignore
except ImportError:
    print("ERROR: run inside Blender (--python ...).")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Canon (§12 interface contracts — all in Temple Plate local frame)
# ---------------------------------------------------------------------------

# Temple Plate slab
PLATE_W_MM = 60.0    # fore-aft (X)
PLATE_H_MM = 50.0    # up-down (Z)
PLATE_T_MM = 4.0     # outboard (Y) wall thickness

# IFACE_YOKE_TEMPLE: 3× M3 equilateral triangle, side 12 mm,
# clustered at the UPPER edge of the plate
YOKE_BOLT_TRIANGLE_SIDE_MM = 12.0
YOKE_CLUSTER_X_MM = 0.0   # centered fore-aft (will revisit if Yoke arm-end forward)
YOKE_CLUSTER_Z_MM = +PLATE_H_MM / 2 - 8.0  # 8 mm down from top edge
YOKE_BOSS_DIA_MM = 6.0
YOKE_BOSS_HEIGHT_MM = 5.0

# IFACE_TEMPLE_FWDBAND: hinge pin axis at local (+8, -6, 0)
FWDBAND_AXIS_X_MM = +8.0
FWDBAND_AXIS_Z_MM = -6.0
FWDBAND_BOSS_DIA_MM = 8.0
FWDBAND_BOSS_LEN_MM = 6.0  # tab proud of plate

# IFACE_TEMPLE_REARBAND: hinge pin axis at local (-8, -6, 0)
REARBAND_AXIS_X_MM = -8.0
REARBAND_AXIS_Z_MM = -6.0
REARBAND_BOSS_DIA_MM = 8.0
REARBAND_BOSS_LEN_MM = 6.0

# IFACE_TEMPLE_PYLON: live-hinge foot at local (-5, +10, +4)
# Foot footprint 8 × 12 mm. (+10 = proud of plate outboard face by 10 mm,
# but here we show the FOOT FOOTPRINT on the plate face, not the proud
# part — that's the pylon body.)
PYLON_FOOT_X_MM = -5.0
PYLON_FOOT_Z_MM = +4.0
PYLON_FOOT_W_MM = 8.0   # along X
PYLON_FOOT_L_MM = 12.0  # along Z
PYLON_FOOT_T_MM = 3.0   # TPU foot thickness proud of plate

# IFACE_TEMPLE_DEFENDER: gimbal pin at local (0, 0, +6) — pitch pin
# horizontal fore-aft. Cradle envelope 25 × 25 × 20 mm.
DEFENDER_PIN_X_MM = 0.0
DEFENDER_PIN_Z_MM = +6.0
DEFENDER_CRADLE_W_MM = 25.0
DEFENDER_CRADLE_H_MM = 25.0
DEFENDER_CRADLE_PROUD_MM = 20.0  # outboard from plate

# IFACE_TEMPLE_CHEEK: hook at local (-15, -20, 0)
CHEEK_HOOK_X_MM = -15.0
CHEEK_HOOK_Z_MM = -20.0
CHEEK_HOOK_W_MM = 26.0  # webbing slot wide
CHEEK_HOOK_H_MM = 4.0
CHEEK_HOOK_PROUD_MM = 8.0  # hook geometry proud of plate inboard side

# IFACE_TEMPLE_SIDEHELM_POD: sliding dovetail, lower-aft face below cheek
# hook. Length 35 mm vertical.
SIDEHELM_DOVETAIL_X_MM = -20.0  # aft of cheek hook
SIDEHELM_DOVETAIL_Z_MM = -10.0  # straddles plate's lower-aft area
SIDEHELM_DOVETAIL_TOP_W_MM = 12.0
SIDEHELM_DOVETAIL_BOT_W_MM = 18.0
SIDEHELM_DOVETAIL_LEN_MM = 35.0
SIDEHELM_DOVETAIL_DEPTH_MM = 3.4


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def make_box(name: str, size_xyz: tuple, loc_xyz: tuple) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc_xyz)
    obj = bpy.context.active_object
    obj.scale = size_xyz
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def make_cylinder(name: str, radius: float, depth: float,
                  loc_xyz: tuple, axis: str = "Z") -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        location=loc_xyz, vertices=32)
    obj = bpy.context.active_object
    obj.name = name
    if axis == "X":
        obj.rotation_euler = (0, math.pi / 2, 0)
    elif axis == "Y":
        obj.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return obj


def export_all(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
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

    # Temple Plate slab itself (outboard face = +Y; all features
    # placed in outboard direction)
    make_box(
        "temple_plate_slab",
        size_xyz=(PLATE_W_MM, PLATE_T_MM, PLATE_H_MM),
        loc_xyz=(0, 0, 0),
    )

    # ---- IFACE_YOKE_TEMPLE: 3-bolt triangle bosses (3× M3) ----
    # Equilateral triangle, side 12 mm, centered on (YOKE_CLUSTER_X, YOKE_CLUSTER_Z)
    s = YOKE_BOLT_TRIANGLE_SIDE_MM
    # Apex up
    centroid_to_apex = s / math.sqrt(3)
    bolt_positions = [
        (YOKE_CLUSTER_X_MM, YOKE_CLUSTER_Z_MM + centroid_to_apex),
        (YOKE_CLUSTER_X_MM - s / 2, YOKE_CLUSTER_Z_MM - centroid_to_apex / 2),
        (YOKE_CLUSTER_X_MM + s / 2, YOKE_CLUSTER_Z_MM - centroid_to_apex / 2),
    ]
    for i, (x, z) in enumerate(bolt_positions):
        make_cylinder(
            f"yoke_bolt_boss_{i}",
            radius=YOKE_BOSS_DIA_MM / 2,
            depth=YOKE_BOSS_HEIGHT_MM,
            loc_xyz=(x, PLATE_T_MM / 2 + YOKE_BOSS_HEIGHT_MM / 2, z),
            axis="Y",
        )

    # ---- IFACE_TEMPLE_FWDBAND: hinge pin boss (cylinder along Y) ----
    make_cylinder(
        "fwdband_hinge_boss",
        radius=FWDBAND_BOSS_DIA_MM / 2,
        depth=FWDBAND_BOSS_LEN_MM,
        loc_xyz=(FWDBAND_AXIS_X_MM, PLATE_T_MM / 2 + FWDBAND_BOSS_LEN_MM / 2,
                 FWDBAND_AXIS_Z_MM),
        axis="Y",
    )

    # ---- IFACE_TEMPLE_REARBAND: hinge pin boss ----
    make_cylinder(
        "rearband_hinge_boss",
        radius=REARBAND_BOSS_DIA_MM / 2,
        depth=REARBAND_BOSS_LEN_MM,
        loc_xyz=(REARBAND_AXIS_X_MM, PLATE_T_MM / 2 + REARBAND_BOSS_LEN_MM / 2,
                 REARBAND_AXIS_Z_MM),
        axis="Y",
    )

    # ---- IFACE_TEMPLE_PYLON: live-hinge foot footprint pad ----
    make_box(
        "pylon_foot_pad",
        size_xyz=(PYLON_FOOT_W_MM, PYLON_FOOT_T_MM, PYLON_FOOT_L_MM),
        loc_xyz=(PYLON_FOOT_X_MM, PLATE_T_MM / 2 + PYLON_FOOT_T_MM / 2,
                 PYLON_FOOT_Z_MM),
    )

    # ---- IFACE_TEMPLE_DEFENDER: cradle envelope box + pitch pin ----
    make_box(
        "defender_cradle_envelope",
        size_xyz=(DEFENDER_CRADLE_W_MM, DEFENDER_CRADLE_PROUD_MM,
                  DEFENDER_CRADLE_H_MM),
        loc_xyz=(DEFENDER_PIN_X_MM,
                 PLATE_T_MM / 2 + DEFENDER_CRADLE_PROUD_MM / 2,
                 DEFENDER_PIN_Z_MM),
    )
    # Pitch pin (2 mm, along X axis, through cradle)
    make_cylinder(
        "defender_pitch_pin",
        radius=1.0,
        depth=DEFENDER_CRADLE_W_MM + 4.0,
        loc_xyz=(DEFENDER_PIN_X_MM,
                 PLATE_T_MM / 2 + DEFENDER_CRADLE_PROUD_MM / 2,
                 DEFENDER_PIN_Z_MM),
        axis="X",
    )

    # ---- IFACE_TEMPLE_CHEEK: hook (on INBOARD face, -Y direction) ----
    make_box(
        "cheek_hook",
        size_xyz=(CHEEK_HOOK_W_MM, CHEEK_HOOK_PROUD_MM, CHEEK_HOOK_H_MM),
        loc_xyz=(CHEEK_HOOK_X_MM,
                 -(PLATE_T_MM / 2 + CHEEK_HOOK_PROUD_MM / 2),
                 CHEEK_HOOK_Z_MM),
    )

    # ---- IFACE_TEMPLE_SIDEHELM_POD: sliding dovetail trapezoidal prism ----
    # Shown as a tapered cuboid for visual check. (Real dovetail is a slot
    # cut INTO the plate; here we just show it as a positive feature pad
    # so it's visible in the STL.) Use box for the bottom-width footprint.
    make_box(
        "sidehelm_dovetail_envelope",
        size_xyz=(SIDEHELM_DOVETAIL_BOT_W_MM, SIDEHELM_DOVETAIL_DEPTH_MM,
                  SIDEHELM_DOVETAIL_LEN_MM),
        loc_xyz=(SIDEHELM_DOVETAIL_X_MM,
                 PLATE_T_MM / 2 + SIDEHELM_DOVETAIL_DEPTH_MM / 2,
                 SIDEHELM_DOVETAIL_Z_MM),
    )

    export_all(args.out)
    print(f"  Temple Plate stack-up: 4 pivots + 3-bolt yoke + cheek hook + dovetail")
    print(f"  Plate slab: {PLATE_W_MM:.0f}(X) × {PLATE_T_MM:.1f}(Y) × {PLATE_H_MM:.0f}(Z) mm")
    print(f"  Yoke cluster centroid: ({YOKE_CLUSTER_X_MM:+.1f}, {YOKE_CLUSTER_Z_MM:+.1f})")
    print(f"  FwdBand axis:  ({FWDBAND_AXIS_X_MM:+.1f}, {FWDBAND_AXIS_Z_MM:+.1f})")
    print(f"  RearBand axis: ({REARBAND_AXIS_X_MM:+.1f}, {REARBAND_AXIS_Z_MM:+.1f})")
    print(f"  Pylon foot:    ({PYLON_FOOT_X_MM:+.1f}, {PYLON_FOOT_Z_MM:+.1f})")
    print(f"  Defender pin:  ({DEFENDER_PIN_X_MM:+.1f}, {DEFENDER_PIN_Z_MM:+.1f})")
    print(f"  Cheek hook:    ({CHEEK_HOOK_X_MM:+.1f}, {CHEEK_HOOK_Z_MM:+.1f})")
    print(f"  Dovetail ctr:  ({SIDEHELM_DOVETAIL_X_MM:+.1f}, {SIDEHELM_DOVETAIL_Z_MM:+.1f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
