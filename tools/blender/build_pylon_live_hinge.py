#!/usr/bin/env -S blender --background --python
"""
build_pylon_live_hinge.py - parametric generator for the Pylon TPU live-hinge.

The live-hinge is a thin TPU 95A web that joins the Temple Plate's
pylon_foot pad to the Pylon's foot pad, providing 0-90 deg fold motion
with integral detent notches. FIRST TPU PRINT in the project; clears
gate G-Pylon when it survives 100 fold cycles without crack initiation.

Run:
    blender --background --python tools/blender/build_pylon_live_hinge.py \\
        -- --out 3D-Models/HelmKit/_generated/pylon_live_hinge_r1.stl

Datum (hinge-local, undeployed flat-print position):
    +X = root-to-tip across the hinge axis (plate side at X=0, pylon side at X=foot+hinge+foot)
    +Y = along hinge axis
    +Z = up (print direction)

Geometry:
    - Plate-side foot (PETG-matching footprint 8x12) with 2x M2 clearance holes
    - Hinge web: thin TPU strip, 12 mm wide (Y), 4 mm long (X), 0.8 mm thick (Z)
      with V-grooves on top face at 45 and 90 deg detent positions
    - Pylon-side foot (matching 8x12) with 2x M2 clearance holes

Print orientation: FLAT on bed (Z up). TPU 95A, 0.2 mm layer, 100pct
infill in the web region, walls = 3 perimeters.

Interfaces consumed:
    IFACE_TEMPLE_PYLON   (foot footprint, fastener pattern, detent angles)
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
except ImportError:
    print("ERROR: run inside Blender")
    sys.exit(1)

from interfaces import (  # type: ignore  # noqa: E402
    IFACE_TEMPLE_PYLON,
    M2_CLEAR_DIA_MM,
)


FOOT_X_MM = IFACE_TEMPLE_PYLON.foot_footprint_mm[0]  # 8
FOOT_Y_MM = IFACE_TEMPLE_PYLON.foot_footprint_mm[1]  # 12
FOOT_T_MM = 1.5  # thin TPU foot, sandwiched between Temple Plate pad + Pylon foot

HINGE_LEN_MM = 4.0   # web length along X (the fold axis is perpendicular = Y)
HINGE_W_MM = FOOT_Y_MM  # 12 mm wide (same as foot)
HINGE_T_MM = 0.8     # web thickness (thin enough to fold)

FOOT_M2_PITCH_MM = FOOT_Y_MM - 4.0  # 8 mm
M2_CLEAR_HOLE_DIA_MM = M2_CLEAR_DIA_MM + 0.2  # 2.6 mm

# Detent V-grooves: cut into top face at 1/4 and 1/2 of hinge length
# to bias the fold at 45 and 90 deg.
DETENT_W_MM = 0.6
DETENT_D_MM = 0.4  # half the web thickness


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


def _add_cylinder(name, center, radius, depth, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    o.location = center
    return o


def build_hinge() -> bpy.types.Object:
    # Plate-side foot (X from 0 to FOOT_X)
    plate_foot = _add_box("plate_foot",
                          (FOOT_X_MM / 2.0, 0.0, FOOT_T_MM / 2.0),
                          (FOOT_X_MM, FOOT_Y_MM, FOOT_T_MM))
    # Hinge web (X from FOOT_X to FOOT_X + HINGE_LEN)
    web = _add_box("web",
                   (FOOT_X_MM + HINGE_LEN_MM / 2.0, 0.0, HINGE_T_MM / 2.0),
                   (HINGE_LEN_MM, HINGE_W_MM, HINGE_T_MM))
    _bool(plate_foot, web, op="UNION")
    # Pylon-side foot
    pylon_foot = _add_box("pylon_foot",
                          (FOOT_X_MM + HINGE_LEN_MM + FOOT_X_MM / 2.0, 0.0,
                           FOOT_T_MM / 2.0),
                          (FOOT_X_MM, FOOT_Y_MM, FOOT_T_MM))
    _bool(plate_foot, pylon_foot, op="UNION")

    # 2x M2 clearance holes through PLATE-SIDE foot
    for i, dy in enumerate((-FOOT_M2_PITCH_MM / 2.0, +FOOT_M2_PITCH_MM / 2.0)):
        hole = _add_cylinder(f"plate_clr_{i}",
                             (FOOT_X_MM / 2.0, dy, FOOT_T_MM / 2.0),
                             M2_CLEAR_HOLE_DIA_MM / 2.0,
                             FOOT_T_MM + 1.0)
        _bool(plate_foot, hole, op="DIFFERENCE")
    # 2x M2 clearance holes through PYLON-SIDE foot
    for i, dy in enumerate((-FOOT_M2_PITCH_MM / 2.0, +FOOT_M2_PITCH_MM / 2.0)):
        hole = _add_cylinder(f"pylon_clr_{i}",
                             (FOOT_X_MM + HINGE_LEN_MM + FOOT_X_MM / 2.0,
                              dy, FOOT_T_MM / 2.0),
                             M2_CLEAR_HOLE_DIA_MM / 2.0,
                             FOOT_T_MM + 1.0)
        _bool(plate_foot, hole, op="DIFFERENCE")

    # Detent V-grooves cut into TOP face of web at 1/3 and 2/3 along web length.
    # Two grooves bias the fold to land on 45 and 90 deg detents.
    for i, frac in enumerate((1.0 / 3.0, 2.0 / 3.0)):
        x_groove = FOOT_X_MM + HINGE_LEN_MM * frac
        groove = _add_box(f"detent_{i}",
                          (x_groove, 0.0, HINGE_T_MM - DETENT_D_MM / 2.0 + 0.05),
                          (DETENT_W_MM, HINGE_W_MM + 0.4, DETENT_D_MM + 0.1))
        _bool(plate_foot, groove, op="DIFFERENCE")

    plate_foot.name = "pylon_live_hinge"
    return plate_foot


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
    tpu_density = 1.21
    est_mass = (dx * dy * dz) / 1000.0 * tpu_density * 0.6  # mostly solid
    out_path.with_suffix(".txt").write_text(
        "pylon_live_hinge_r1\n"
        "  MATERIAL: TPU 95A (NOT PETG) -- FIRST TPU PRINT IN PROJECT\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  est_mass_g (TPU): {est_mass:.1f}\n"
        f"  foot_each_side: {FOOT_X_MM} x {FOOT_Y_MM} x {FOOT_T_MM} mm\n"
        f"  web: {HINGE_LEN_MM} x {HINGE_W_MM} x {HINGE_T_MM} mm\n"
        f"  detent V-grooves: 2x ({DETENT_W_MM} x {DETENT_D_MM} mm) at 1/3 + 2/3 web length\n"
        "  print_orientation: flat on bed, web spans Y axis on bed\n"
        "  print_settings: 0.2 mm layer, 100pct infill, 3 walls, slow speed\n"
        "  interfaces_consumed:\n"
        "    - IFACE_TEMPLE_PYLON (foot footprint, M2 holes, detent angles 0/45/90)\n"
        "  fasteners (per hinge):\n"
        "    - 2x M2x6 thru plate foot into Temple Plate M2 heatset\n"
        "    - 2x M2x6 thru pylon foot into Psi-Pylon M2 heatset\n"
        "  ACCEPTANCE GATE: G-Pylon -- 100 fold cycles 0<->90 deg no crack init\n"
    )


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    reset_scene()
    obj = build_hinge()
    export_stl(obj, args.out)
    write_sidecar(obj, args.out)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
