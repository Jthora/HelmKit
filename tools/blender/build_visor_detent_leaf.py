#!/usr/bin/env -S blender --background --python
"""
build_visor_detent_leaf.py - TPU 95A click-leaf for Visor-Band hinges.

Small TPU leaf that bolts to the Temple Plate's visor_band_hinge boss
and presses against the band's hinge cylinder. Provides tactile click
detents at 0/15/30/45/60 deg and holds the band at any stop with
~250 N.mm torque. One leaf per band per side (4 leaves per helm:
L+R front, L+R rear).

Run:
    blender --background --python tools/blender/build_visor_detent_leaf.py \\
        -- --out 3D-Models/HelmKit/_generated/visor_detent_leaf_r1.stl

Datum (leaf-local):
    +X = root-to-tip
    +Y = leaf width
    +Z = up (thru-hole axis)

Interfaces consumed:
    IFACE_TEMPLE_FWDBAND / IFACE_TEMPLE_REARBAND  (detent mechanism)
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

from interfaces import M3_CLEAR_DIA_MM  # type: ignore  # noqa: E402


LEAF_LEN_MM = 25.0   # service-loop length, X
LEAF_W_MM = 8.0      # Y
LEAF_T_MM = 1.6      # Z (thin enough to flex)
ROOT_PAD_X_MM = 8.0  # thicker pad at root for the M3 screw
ROOT_PAD_T_MM = 3.0
TIP_BUMP_DIA_MM = 3.0  # rounded bump at tip presses into the cylinder notches
TIP_BUMP_T_MM = 1.0    # bump proud of leaf top face
M3_CLR_HOLE_DIA = M3_CLEAR_DIA_MM + 0.2


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


def _add_cyl(name, center, radius, depth, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    o.location = center
    return o


def build_leaf() -> bpy.types.Object:
    # Root pad (thicker)
    pad = _add_box("root_pad",
                   (ROOT_PAD_X_MM / 2.0, 0.0, ROOT_PAD_T_MM / 2.0),
                   (ROOT_PAD_X_MM, LEAF_W_MM, ROOT_PAD_T_MM))
    # Thin leaf extending +X past the pad
    leaf = _add_box("leaf",
                    (ROOT_PAD_X_MM + (LEAF_LEN_MM - ROOT_PAD_X_MM) / 2.0,
                     0.0, LEAF_T_MM / 2.0),
                    (LEAF_LEN_MM - ROOT_PAD_X_MM, LEAF_W_MM, LEAF_T_MM))
    _bool(pad, leaf, op="UNION")
    # Tip bump (rounded contact point against cylinder notches)
    bump = _add_cyl("tip_bump",
                    (LEAF_LEN_MM - 2.0, 0.0, LEAF_T_MM + TIP_BUMP_T_MM / 2.0),
                    TIP_BUMP_DIA_MM / 2.0, TIP_BUMP_T_MM + 0.1)
    _bool(pad, bump, op="UNION")
    # M3 clearance hole through root pad
    hole = _add_cyl("root_m3", (ROOT_PAD_X_MM / 2.0, 0.0, ROOT_PAD_T_MM / 2.0),
                    M3_CLR_HOLE_DIA / 2.0, ROOT_PAD_T_MM + 1.0)
    _bool(pad, hole, op="DIFFERENCE")
    pad.name = "visor_detent_leaf"
    return pad


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
    out_path.with_suffix(".txt").write_text(
        "visor_detent_leaf_r1\n"
        "  MATERIAL: TPU 95A\n"
        "  (one STL; print 4 copies per helm -- L+R front + L+R rear)\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  leaf_length_mm: {LEAF_LEN_MM} (service loop length per IFACE)\n"
        f"  leaf_thickness_mm: {LEAF_T_MM} (flexes)\n"
        f"  root_pad_mm: {ROOT_PAD_X_MM} x {LEAF_W_MM} x {ROOT_PAD_T_MM}\n"
        f"  tip_bump_dia_mm: {TIP_BUMP_DIA_MM}\n"
        "  detent target: 250 N.mm holding torque\n"
        "  interfaces_consumed:\n"
        "    - IFACE_TEMPLE_FWDBAND / IFACE_TEMPLE_REARBAND (detent_mechanism)\n"
        "  fasteners (per leaf):\n"
        "    - 1x M3x6 into Temple Plate visor_band_hinge boss M3 heatset\n"
        "  detent_angles_deg: 0 / 15 / 30 / 45 / 60 (matching notches on band cylinder)\n"
    )


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    reset_scene()
    obj = build_leaf()
    export_stl(obj, args.out)
    write_sidecar(obj, args.out)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
