#!/usr/bin/env -S blender --background --python
"""
build_psi_stabilizer_panel.py - PCB carrier panel for Psi-Stabilizer-Mk1.

Snap-fit/screw-mounted panel that drops into the IFACE_BAND_STABILIZER
pocket on either Forward or Rear Visor-Band. Carries 2x bifilar 30x30
mm PCBs side-by-side, the nRF52840 + SI5351 + Class-D MCU stack
(mounted between PCBs), and an inboard cable exit grommet for the
RG-178 + USB-C harness.

One STL serves both front + rear pockets (interface is identical;
just installed twice -- one per band).

Run:
    blender --background --python tools/blender/build_psi_stabilizer_panel.py \\
        -- --out 3D-Models/HelmKit/_generated/psi_stabilizer_panel_r1.stl

Datum (panel-local):
    +X = panel long axis (along band tangent)
    +Y = panel short axis (along band height)
    +Z = outward (away from head, faces accent-white cover plate)

Interfaces consumed:
    IFACE_BAND_STABILIZER  (pocket 64x34x4 mm, 2x M3 retention, 4mm grommet)
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
    IFACE_BAND_STABILIZER,
    M3_CLEAR_DIA_MM,
)


PANEL_X, PANEL_Y, PANEL_Z = IFACE_BAND_STABILIZER.pocket_internal_mm  # 64 x 34 x 4
PCB_SIDE = 30.0
PCB_GAP = IFACE_BAND_STABILIZER.pcb_gap_mm
PCB_MAX_T = IFACE_BAND_STABILIZER.pcb_max_thickness_mm
GROMMET_DIA = IFACE_BAND_STABILIZER.cable_exit_grommet_dia_mm
M3_CLR_HOLE_DIA = M3_CLEAR_DIA_MM + 0.2
# Retention screw spacing: along long axis, just outside the 2 PCB footprint
SCREW_PITCH_X = PCB_SIDE + PCB_GAP + 10.0  # 42 mm


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


def _add_cyl(name, center, radius, depth, axis="Z", verts=24):
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


def build_panel() -> bpy.types.Object:
    # Carrier panel: slightly smaller than pocket interior for slip fit
    px = PANEL_X - 0.4
    py = PANEL_Y - 0.4
    pz = PANEL_Z - 0.4
    panel = _add_box("stabilizer_panel", (0.0, 0.0, 0.0), (px, py, pz))
    # 2x PCB recesses on inboard (-Z) face, side-by-side along X
    pcb_x_centers = (-(PCB_SIDE + PCB_GAP) / 2.0, +(PCB_SIDE + PCB_GAP) / 2.0)
    for i, cx in enumerate(pcb_x_centers):
        recess = _add_box(f"pcb_recess_{i}",
                          (cx, 0.0, -pz / 2.0 + PCB_MAX_T / 2.0 - 0.1),
                          (PCB_SIDE + 0.4, PCB_SIDE + 0.4, PCB_MAX_T + 0.4))
        _bool(panel, recess, op="DIFFERENCE")
    # 2x M3 clearance holes for retention into band's M3 heatset
    # (positions: outboard of the 2 PCB recesses, at +/- SCREW_PITCH_X/2)
    for i, cx in enumerate((-SCREW_PITCH_X / 2.0, +SCREW_PITCH_X / 2.0)):
        # Holes near the upper edge so they don't conflict with PCBs
        hole = _add_cyl(f"retention_m3_{i}", (cx, 0.0, 0.0),
                        M3_CLR_HOLE_DIA / 2.0, pz + 1.0, axis="Z")
        _bool(panel, hole, op="DIFFERENCE")
    # Cable exit grommet on inboard face (centered between PCBs)
    grommet = _add_cyl("cable_grommet", (0.0, -py / 2.0, 0.0),
                       GROMMET_DIA / 2.0, py + 1.0, axis="Y")
    _bool(panel, grommet, op="DIFFERENCE")
    return panel


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
    est_mass = (dx * dy * dz) / 1000.0 * 1.27 * 0.4
    out_path.with_suffix(".txt").write_text(
        "psi_stabilizer_panel_r1\n"
        "  (one STL serves FRONT + REAR stabilizers; print 2 copies per helm)\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  est_mass_g (PETG): {est_mass:.1f}\n"
        "  holds:\n"
        f"    - 2x bifilar PCB (30x30 mm) in recesses, gap {PCB_GAP} mm\n"
        f"    - cable exit grommet ({GROMMET_DIA} mm) on inboard face\n"
        "  interfaces_consumed:\n"
        "    - IFACE_BAND_STABILIZER (pocket 64x34x4 mm, 2x M3 retention, 4mm grommet)\n"
        "  fasteners (per panel):\n"
        "    - 2x M3x6 into band M3 heatset\n"
        "  per-side electronics (NOT printed; mounted on PCBs):\n"
        "    - 1x nRF52840 module\n"
        "    - 1x SI5351 clock generator\n"
        "    - Class-D driver for front+rear spiral pair on that side\n"
        "  TODO r2: PCB standoff posts; LED light-pipe on cover side\n"
    )


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    reset_scene()
    obj = build_panel()
    export_stl(obj, args.out)
    write_sidecar(obj, args.out)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
