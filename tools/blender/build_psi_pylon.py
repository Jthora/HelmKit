#!/usr/bin/env -S blender --background --python
"""
build_psi_pylon.py - parametric generator for the Psi-Pylon dipole arm.

Each Pylon is one leg of the head-spanning differential dipole. PETG
prism with embedded brass dipole leg, hinged to the Temple Plate via
a TPU live-hinge (build_pylon_live_hinge.py). The Pylon foot bolts
into the Temple Plate's pylon_foot pad via 2x M2 heatset screws.

Run:
    blender --background --python tools/blender/build_psi_pylon.py \\
        -- --out 3D-Models/HelmKit/_generated/psi_pylon_r1.stl

Datum (Pylon-local, deployed position 0 deg fold):
    +X = root-to-tip  (long axis; root at X=0, tip at X=+60)
    +Y = up
    +Z = outboard

Interfaces consumed:
    IFACE_TEMPLE_PYLON   (8x12 foot footprint, 2x M2 holes, RG-178 service loop)
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
    M2_HEATSET_OD_MM,
    M2_HEATSET_LEN_MM,
)


# ---------------------------------------------------------------------------
# Pylon geometry (per envelope_pylon_fold scaffold: 60 x 6 x 4 mm prism)
# ---------------------------------------------------------------------------

PYLON_LEN_MM = 60.0       # root-to-tip
PYLON_W_MM = 6.0          # Y (vertical)
PYLON_T_MM = 4.0          # Z (outboard thickness)

FOOT_X_MM = IFACE_TEMPLE_PYLON.foot_footprint_mm[0]  # 8
FOOT_Y_MM = IFACE_TEMPLE_PYLON.foot_footprint_mm[1]  # 12
FOOT_T_MM = IFACE_TEMPLE_PYLON.foot_thickness_mm     # 3
FOOT_M2_PITCH_MM = FOOT_Y_MM - 4.0                   # 8 mm

# Embedded dipole leg slot: 1.5 mm wide channel running the length
DIPOLE_SLOT_W_MM = 1.6
DIPOLE_SLOT_D_MM = 2.0    # slot depth from outboard face

# RG-178 coax service loop pocket at root (40 mm loop, but coiled in
# a small pocket -- render as a 12 mm dia x 5 mm deep cavity in foot)
COAX_LOOP_DIA_MM = 12.0
COAX_LOOP_D_MM = 5.0


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def _bool(host, tool, op="DIFFERENCE", solver="EXACT"):
    mod = host.modifiers.new(name=f"b_{tool.name[:20]}", type="BOOLEAN")
    mod.operation = op
    mod.object = tool
    mod.solver = solver
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


def _add_cylinder(name, center, radius, depth, axis="Z", verts=32):
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


def build_pylon() -> bpy.types.Object:
    # Pylon prism: root at X=0, tip at X=+PYLON_LEN
    body = _add_box("psi_pylon",
                    (PYLON_LEN_MM / 2.0, 0.0, PYLON_T_MM / 2.0),
                    (PYLON_LEN_MM, PYLON_W_MM, PYLON_T_MM))
    # Foot pad: extends in -X (off the root) and is wider than prism
    foot = _add_box("foot",
                    (-FOOT_X_MM / 2.0, 0.0, FOOT_T_MM / 2.0),
                    (FOOT_X_MM, FOOT_Y_MM, FOOT_T_MM))
    _bool(body, foot, op="UNION")
    # 2x M2 heatset holes in foot
    for i, dy in enumerate((-FOOT_M2_PITCH_MM / 2.0, +FOOT_M2_PITCH_MM / 2.0)):
        hole = _add_cylinder(f"foot_m2_{i}",
                             (-FOOT_X_MM / 2.0, dy,
                              FOOT_T_MM - M2_HEATSET_LEN_MM / 2.0),
                             M2_HEATSET_OD_MM / 2.0,
                             M2_HEATSET_LEN_MM + 0.2, axis="Z")
        _bool(body, hole, op="DIFFERENCE")
    # Coax service loop pocket on inboard face of foot
    loop = _add_cylinder("coax_loop_pocket",
                         (-FOOT_X_MM / 2.0, 0.0, -COAX_LOOP_D_MM / 2.0 + 0.5),
                         COAX_LOOP_DIA_MM / 2.0, COAX_LOOP_D_MM + 0.5,
                         axis="Z")
    _bool(body, loop, op="DIFFERENCE")
    # Dipole-leg slot down the length on outboard face
    slot = _add_box("dipole_slot",
                    (PYLON_LEN_MM / 2.0, 0.0,
                     PYLON_T_MM - DIPOLE_SLOT_D_MM / 2.0 + 0.1),
                    (PYLON_LEN_MM - 2.0, DIPOLE_SLOT_W_MM, DIPOLE_SLOT_D_MM + 0.2))
    _bool(body, slot, op="DIFFERENCE")
    return body


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
    est_mass = (dx * dy * dz) / 1000.0 * 1.27 * 0.35
    out_path.with_suffix(".txt").write_text(
        "psi_pylon_r1\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  est_mass_g (PETG, ~35pct rough): {est_mass:.1f}\n"
        f"  prism: {PYLON_LEN_MM} x {PYLON_W_MM} x {PYLON_T_MM} mm\n"
        f"  foot:  {FOOT_X_MM} x {FOOT_Y_MM} x {FOOT_T_MM} mm\n"
        "  interfaces_consumed:\n"
        "    - IFACE_TEMPLE_PYLON  (foot, 2x M2 heatset, fold backward, RG-178)\n"
        "  fasteners (per pylon):\n"
        "    - 2x M2x6 (foot to Temple Plate pylon_foot pad)\n"
        "  embedded_components:\n"
        f"    - brass dipole leg ({PYLON_LEN_MM - 2.0} mm long, in {DIPOLE_SLOT_W_MM}x{DIPOLE_SLOT_D_MM} mm slot)\n"
        f"    - RG-178 coax service loop ({COAX_LOOP_DIA_MM} mm dia x {COAX_LOOP_D_MM} mm deep pocket)\n"
        "  note: TPU live-hinge is SEPARATE printed part (build_pylon_live_hinge.py).\n"
    )


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    reset_scene()
    obj = build_pylon()
    export_stl(obj, args.out)
    write_sidecar(obj, args.out)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
