#!/usr/bin/env -S blender --background --python
"""
build_rear_visor_band.py - parametric generator for the occipital arc band.

Rear Visor-Band: 180-deg semicircle band on the BACK of the head,
mirror of forward_visor_band but with rear-center Stabilizer pocket
and NO Picatinny sub-rail. Hinges to L+R Temple Plates via the
REARBAND hinge bosses (axis at plate-local (-8, -6, 0)).

Run:
    blender --background --python tools/blender/build_rear_visor_band.py \\
        -- --out 3D-Models/HelmKit/_generated/rear_visor_band_r1.stl

Datum (world frame):
    +X = ear-to-ear   (band spans +/-X)
    +Y = up
    +Z = forward      (rear band wraps -Z, the occiput)

Interfaces consumed:
    IFACE_TEMPLE_REARBAND    (2x hinge tabs at band ends)
    IFACE_BAND_STABILIZER    (rear-center pocket, same 64x34x4 mm spec)
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
except ImportError:
    print("ERROR: run inside Blender")
    sys.exit(1)

from interfaces import (  # type: ignore  # noqa: E402
    IFACE_TEMPLE_REARBAND,
    IFACE_BAND_STABILIZER,
    M3_HEATSET_OD_MM,
    M3_HEATSET_LEN_MM,
)


BAND_INNER_R_MM = 95.0
BAND_WALL_MM = 4.0
BAND_HEIGHT_MM = 38.0
BAND_ARC_DEG = 180.0

HINGE_TAB_W_MM = 12.0
HINGE_TAB_H_MM = 14.0
HINGE_TAB_T_MM = 5.0
HINGE_PIN_BORE_DIA_MM = IFACE_TEMPLE_REARBAND.pin_dia_mm + 0.2

POCKET_W_MM, POCKET_H_MM, POCKET_D_MM = IFACE_BAND_STABILIZER.pocket_internal_mm


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


def _add_cylinder(name, center, radius, depth, axis="Y", verts=48):
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


def make_arc_band() -> bpy.types.Object:
    """Rear semicircle: angle 180..360 in XZ plane (wraps -Z)."""
    bm = bmesh.new()
    n = 96
    outer_r = BAND_INNER_R_MM + BAND_WALL_MM
    inner_r = BAND_INNER_R_MM
    arc_rad = math.radians(BAND_ARC_DEG)
    t0 = math.pi  # start at -X
    pts_outer = []
    pts_inner = []
    for i in range(n + 1):
        t = t0 + (i / n) * arc_rad   # pi .. 2pi
        pts_outer.append((outer_r * math.cos(t), outer_r * math.sin(t)))
        pts_inner.append((inner_r * math.cos(t), inner_r * math.sin(t)))
    ring_2d = list(pts_outer) + list(reversed(pts_inner))
    y_lo, y_hi = -BAND_HEIGHT_MM / 2.0, +BAND_HEIGHT_MM / 2.0
    bot = [bm.verts.new((x, y_lo, z)) for (x, z) in ring_2d]
    top = [bm.verts.new((x, y_hi, z)) for (x, z) in ring_2d]
    n_outer = n + 1
    for i in range(n):
        bm.faces.new((bot[i], bot[i + 1],
                      bot[2 * n_outer - 2 - i], bot[2 * n_outer - 1 - i]))
        bm.faces.new((top[i], top[2 * n_outer - 1 - i],
                      top[2 * n_outer - 2 - i], top[i + 1]))
    m = len(ring_2d)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    mesh = bpy.data.meshes.new("rear_band_mesh")
    bm.to_mesh(mesh)
    bm.free()
    band = bpy.data.objects.new("rear_visor_band", mesh)
    bpy.context.collection.objects.link(band)
    return band


def add_hinge_tabs(band: bpy.types.Object) -> None:
    """Tabs at angle 180 (-X = L) and 360 (+X = R), pin bore along +/-X."""
    for side, ang_deg in (("L", 180.0), ("R", 360.0)):
        t = math.radians(ang_deg)
        r_mid = BAND_INNER_R_MM + BAND_WALL_MM / 2.0
        tab_cx = r_mid * math.cos(t)
        tab_cz = r_mid * math.sin(t)
        tan_x = -math.sin(t)
        tan_z = math.cos(t)
        tab_cx += tan_x * HINGE_TAB_W_MM / 2.0
        tab_cz += tan_z * HINGE_TAB_W_MM / 2.0
        tab = _add_box(f"hinge_tab_{side}",
                       (tab_cx, 0.0, tab_cz),
                       (HINGE_TAB_T_MM, HINGE_TAB_H_MM, HINGE_TAB_W_MM))
        _bool(band, tab, op="UNION")
        bore = _add_cylinder(f"hinge_bore_{side}",
                             (tab_cx, 0.0, tab_cz),
                             HINGE_PIN_BORE_DIA_MM / 2.0,
                             HINGE_TAB_T_MM + BAND_WALL_MM + 4.0,
                             axis="X")
        _bool(band, bore, op="DIFFERENCE")


def add_stabilizer_pocket(band: bpy.types.Object) -> None:
    """Rear-center pocket at angle 270 deg (-Z direction, back of head)."""
    r_outer = BAND_INNER_R_MM + BAND_WALL_MM
    r_cutter_center = r_outer - POCKET_D_MM / 2.0 + 0.2
    pocket = _add_box("stabilizer_pocket",
                      (0.0, 0.0, -r_cutter_center),
                      (POCKET_W_MM, POCKET_H_MM, POCKET_D_MM + 0.4))
    _bool(band, pocket, op="DIFFERENCE")
    grommet_dia = IFACE_BAND_STABILIZER.cable_exit_grommet_dia_mm
    grommet = _add_cylinder("stab_cable_grommet",
                            (0.0, 0.0, -(BAND_INNER_R_MM + BAND_WALL_MM / 2.0)),
                            grommet_dia / 2.0, BAND_WALL_MM + 2.0, axis="Z")
    _bool(band, grommet, op="DIFFERENCE")
    for i, dy in enumerate((-POCKET_H_MM / 2.0 - 4.0, +POCKET_H_MM / 2.0 + 4.0)):
        hole = _add_cylinder(f"stab_cover_m3_{i}",
                             (0.0, dy, -(BAND_INNER_R_MM + BAND_WALL_MM - M3_HEATSET_LEN_MM / 2.0)),
                             M3_HEATSET_OD_MM / 2.0,
                             M3_HEATSET_LEN_MM + 0.2, axis="Z")
        _bool(band, hole, op="DIFFERENCE")


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
    est_mass = (dx * dy * dz) / 1000.0 * 1.27 * 0.15
    side = out_path.with_suffix(".txt")
    side.write_text(
        "rear_visor_band_r1\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  est_mass_g (PETG, ~15pct rough): {est_mass:.1f}\n"
        f"  inner_radius_mm: {BAND_INNER_R_MM}\n"
        f"  wall_mm: {BAND_WALL_MM}\n"
        f"  height_mm: {BAND_HEIGHT_MM}\n"
        f"  arc_deg: {BAND_ARC_DEG} (occipital semicircle, wraps -Z)\n"
        "  interfaces_consumed:\n"
        "    - IFACE_TEMPLE_REARBAND   (2x hinge tabs)\n"
        "    - IFACE_BAND_STABILIZER   (rear-center pocket 64x34x4 mm)\n"
        "  fasteners (per band):\n"
        "    - 2x 3mm steel pin (hinge to L+R Temple Plate RearBand bosses)\n"
        "    - 2x M3 heatset   (stabilizer cover plate retention)\n"
        "  note: NO Picatinny on rear band (forward band carries sub-rail per\n"
        "        IFACE_BAND_SUBRAIL.rail_position = 'lower_edge_fwdband_outer_face')\n"
    )
    print(f"Wrote sidecar {side}")


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    reset_scene()
    band = make_arc_band()
    add_hinge_tabs(band)
    add_stabilizer_pocket(band)
    export_stl(band, args.out)
    write_sidecar(band, args.out)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
