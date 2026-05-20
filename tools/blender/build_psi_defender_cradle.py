#!/usr/bin/env -S blender --background --python
"""
build_psi_defender_cradle.py - parametric generator for the Defender cradle.

The Defender cradle is the caduceus-coil housing that mates to the
Temple Plate's Option-A standoff arm via a 2-axis pitch+yaw gimbal.
Contains: paired opposite-chirality caduceus coils, coil exit window
on the +Z face (aimed at the head's T-T line for the collinear L+R
operating mode), and the pitch-yoke socket.

Run:
    blender --background --python tools/blender/build_psi_defender_cradle.py \\
        -- --out 3D-Models/HelmKit/_generated/psi_defender_cradle_r1.stl

Datum (cradle-local, neutral aim):
    +X = forward
    +Y = up
    +Z = outward (carries the coil exit window aimed at T-T line)
Cradle origin is the cradle envelope centroid (the point that, in
plate-local coords, equals IFACE_TEMPLE_DEFENDER.pin_local_mm).

Interfaces consumed:
    IFACE_TEMPLE_DEFENDER  (envelope 25x25x20, coil exit 14 mm, pitch + yaw pins)
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

from interfaces import IFACE_TEMPLE_DEFENDER  # type: ignore  # noqa: E402


ENV_X, ENV_Y, ENV_Z = IFACE_TEMPLE_DEFENDER.cradle_envelope_mm  # 25, 25, 20
EXIT_DIA = IFACE_TEMPLE_DEFENDER.coil_exit_window_dia_mm        # 14
WALL_MM = 2.0
PITCH_PIN_DIA = IFACE_TEMPLE_DEFENDER.pitch_pin_dia_mm          # 2
YAW_PIN_DIA = IFACE_TEMPLE_DEFENDER.yaw_pin_dia_mm              # 2
PIN_BORE_DIA = PITCH_PIN_DIA + 0.2

# Pitch yoke clearance slot (the inner cradle pivots about the Y axis
# inside an outer yoke that pivots about the X axis -- 2-axis gimbal).
YOKE_SLOT_W = 12.0  # X width of slot where the inner yoke fits
YOKE_SLOT_H = 12.0  # Y height


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


def build_cradle() -> bpy.types.Object:
    # Outer envelope shell
    shell = _add_box("cradle", (0.0, 0.0, 0.0), (ENV_X, ENV_Y, ENV_Z))
    # Hollow interior for coils
    cavity = _add_box("coil_cavity",
                      (0.0, 0.0, 0.0),
                      (ENV_X - 2 * WALL_MM, ENV_Y - 2 * WALL_MM, ENV_Z - 2 * WALL_MM))
    _bool(shell, cavity, op="DIFFERENCE")
    # Coil exit window on +Z face (14 mm dia)
    exit_win = _add_cyl("coil_exit",
                        (0.0, 0.0, ENV_Z / 2.0),
                        EXIT_DIA / 2.0, WALL_MM + 2.0, axis="Z")
    _bool(shell, exit_win, op="DIFFERENCE")

    # Pitch-pin bore: runs along Y (vertical), through the cradle.
    # The cradle pitches fore/aft about this axis.
    pitch_bore = _add_cyl("pitch_pin_bore",
                          (0.0, 0.0, 0.0),
                          PIN_BORE_DIA / 2.0, ENV_Y + 2.0, axis="Y")
    _bool(shell, pitch_bore, op="DIFFERENCE")

    # Yaw-pin bore: runs along X (fore-aft), perpendicular to pitch.
    # 2-axis gimbal: yaw axis crosses pitch axis at envelope center.
    yaw_bore = _add_cyl("yaw_pin_bore",
                        (0.0, 0.0, 0.0),
                        PIN_BORE_DIA / 2.0, ENV_X + 2.0, axis="X")
    _bool(shell, yaw_bore, op="DIFFERENCE")

    # Pitch-yoke clearance slot: open the -Z face (head-side) so the
    # inner yoke can swing through pitch range. Cut a rectangular slot
    # in the -Z face spanning the yoke envelope.
    yoke_slot = _add_box("pitch_yoke_slot",
                         (0.0, 0.0, -ENV_Z / 2.0 - 0.5),
                         (YOKE_SLOT_W, YOKE_SLOT_H, WALL_MM + 1.0))
    _bool(shell, yoke_slot, op="DIFFERENCE")

    shell.name = "psi_defender_cradle"
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
    est_mass = (dx * dy * dz) / 1000.0 * 1.27 * 0.30
    out_path.with_suffix(".txt").write_text(
        "psi_defender_cradle_r1\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  est_mass_g (PETG): {est_mass:.1f} (cradle SHELL only; coil mass separate)\n"
        f"  envelope_mm: {ENV_X} x {ENV_Y} x {ENV_Z}\n"
        f"  wall_mm: {WALL_MM}\n"
        f"  coil_exit_window_dia_mm: {EXIT_DIA} (on +Z face, aimed at T-T line)\n"
        "  gimbal:\n"
        f"    - pitch axis: along Y (cradle pitches fore/aft), pin {PITCH_PIN_DIA} mm\n"
        f"    - yaw axis:   along X (cradle yaws L/R),         pin {YAW_PIN_DIA} mm\n"
        f"    - aim range:  +/-{IFACE_TEMPLE_DEFENDER.aim_range_pitch_deg[1]} pitch, +/-{IFACE_TEMPLE_DEFENDER.aim_range_yaw_deg[1]} yaw\n"
        "  interfaces_consumed:\n"
        "    - IFACE_TEMPLE_DEFENDER (envelope, coil exit, gimbal pins)\n"
        "  mates_to:\n"
        "    - Temple Plate Option-A standoff pitch yoke (pin at plate-local (+15,+10,+10))\n"
        "  embedded_components:\n"
        "    - 2x caduceus coils (paired opposite-chirality, scalar-shield topology)\n"
        "    - aim-lock M2x4 setscrew into M2 heatset on pitch yoke (cradle side)\n"
        "  ACCEPTANCE GATE: G-Defender-Aim -- coil exit windows L+R collinear within 2 deg\n"
    )


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    reset_scene()
    obj = build_cradle()
    export_stl(obj, args.out)
    write_sidecar(obj, args.out)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
