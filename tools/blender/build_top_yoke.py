#!/usr/bin/env -S blender --background --python
"""
build_top_yoke.py - parametric generator for HelmKit Mk0.5-beta Top Yoke.

The Top Yoke is the over-parietal headphone-style arch that carries the
primary weight path of the frame, hosts the 1:1 balun at its apex, and
runs the differential dipole feed down each arm via an internal cable
raceway. Each arm terminates in a 3-bolt M3 cluster that bolts to a
Temple Plate (IFACE_YOKE_TEMPLE).

Run:
    blender --background --python tools/blender/build_top_yoke.py \\
        -- --out 3D-Models/HelmKit/_generated/top_yoke_r1.stl

Datum convention (world frame for this part):
    +X = ear-to-ear  (arch spans +/-X)
    +Y = up          (arch rises to +Y at apex)
    +Z = fore-aft    (arch is thin in Z, fore-aft is the "depth" direction)
The Temple Plate local frame (interfaces.py) is REMAPPED onto each arm
end as a rigid transform; the bolt triangle centroid in the plate frame
(0, +18, 0) lands on the mating face of the yoke arm end.

Status: SCAFFOLD. Geometry honours IFACE_YOKE_TEMPLE bolt cluster and
the balun cavity envelope. Has not yet been validated against G-Yoke
or G-Fit.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

# Allow `from interfaces import ...` when run via blender --python
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

try:
    import bpy  # type: ignore
    import bmesh  # type: ignore
except ImportError:
    print("ERROR: run inside Blender:")
    print("  blender --background --python tools/blender/build_top_yoke.py")
    sys.exit(1)

from interfaces import (  # type: ignore  # noqa: E402
    IFACE_YOKE_TEMPLE,
    M3_HEATSET_OD_MM,
    M3_HEATSET_LEN_MM,
)


# ---------------------------------------------------------------------------
# Canon parameters (yoke geometry; iface dims come from interfaces.py)
# ---------------------------------------------------------------------------

# Elliptical arch semi-axes (head-shape derived):
ARCH_SEMI_X_MM = 78.0    # ear-to-ear half-span (arch goes from -78 to +78)
ARCH_SEMI_Y_MM = 96.0    # crown rise above ear plane
ARCH_DEPTH_Z_MM = 22.0   # fore-aft thickness of the arch (front-to-back band)
ARCH_WALL_MM = 4.0       # PETG outer wall thickness

# Internal raceway: hollow channel along the underside of each arm,
# carrying the balanced feed pair from balun (apex) down to arm end.
RACEWAY_W_MM = 6.0       # cross-section width  (along Z, fore-aft)
RACEWAY_H_MM = 4.0       # cross-section height (radially inward)
RACEWAY_INSET_MM = 1.2   # how far the raceway sits inside the inner wall

# Balun cavity at apex (must fit IFACE balun spec <= 25 x 15 x 10 mm)
BALUN_X_MM = 27.0        # interior X (along arch tangent at apex)
BALUN_Y_MM = 12.0        # interior Y (radial-inward at apex)
BALUN_Z_MM = 17.0        # interior Z (fore-aft, parallel to arch depth)
BALUN_LID_W_MM = 30.0    # service lid opening on underside
BALUN_LID_D_MM = 19.0

# Arm-end mating pad: flat face perpendicular to the arch tangent at
# the end where the Temple Plate bolts on. Pad sized to host the M3x3
# bolt triangle plus boss meat (insert OD 5 mm + 6 mm min thickness).
ARM_END_PAD_W_MM = 28.0  # along Z (fore-aft of head at ear)
ARM_END_PAD_H_MM = 24.0  # along arch-radial
ARM_END_PAD_T_MM = 8.0   # thickness of pad outward of nominal arch wall

# Heat-set bosses
BOSS_OD_MM = M3_HEATSET_OD_MM + 2.0 * 3.0  # 5 mm insert + 3 mm wall each side
BOSS_DEPTH_MM = M3_HEATSET_LEN_MM + 2.0    # 5 mm insert + 2 mm bottom


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def _apply_boolean(host: bpy.types.Object, tool: bpy.types.Object,
                   op: str = "DIFFERENCE", solver: str = "EXACT") -> None:
    mod = host.modifiers.new(name=f"bool_{tool.name}", type="BOOLEAN")
    mod.operation = op
    mod.object = tool
    mod.solver = solver
    bpy.context.view_layer.objects.active = host
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def make_elliptical_arch() -> bpy.types.Object:
    """Build the arch body: an extruded elliptical annulus segment.

    Extrusion axis is Z (fore-aft). The XY profile is an elliptical
    annulus, kept only for the upper half (y >= 0) -> headphone arch.
    """
    bm = bmesh.new()
    n = 96
    outer_pts = []
    inner_pts = []
    a_out_x = ARCH_SEMI_X_MM + ARCH_WALL_MM
    a_out_y = ARCH_SEMI_Y_MM + ARCH_WALL_MM
    a_in_x = ARCH_SEMI_X_MM
    a_in_y = ARCH_SEMI_Y_MM
    # Sweep from angle pi (left ear, -X) up over apex to 0 (right ear, +X)
    for i in range(n + 1):
        t = math.pi - (i / n) * math.pi
        outer_pts.append((a_out_x * math.cos(t), a_out_y * math.sin(t)))
        inner_pts.append((a_in_x * math.cos(t), a_in_y * math.sin(t)))
    # Build the 2D arch ring (closed loop): outer L->R, then inner R->L
    ring = []
    for x, y in outer_pts:
        ring.append((x, y))
    for x, y in reversed(inner_pts):
        ring.append((x, y))
    z_lo, z_hi = -ARCH_DEPTH_Z_MM / 2.0, +ARCH_DEPTH_Z_MM / 2.0
    bot_verts = [bm.verts.new((x, y, z_lo)) for (x, y) in ring]
    top_verts = [bm.verts.new((x, y, z_hi)) for (x, y) in ring]
    # Cap faces: triangulate via center fan against centroid would be
    # bad for a thin annulus; instead use a quad strip between outer
    # and inner edges for both caps.
    n_outer = n + 1
    for i in range(n):
        ob_a, ob_b = bot_verts[i], bot_verts[i + 1]
        ib_a, ib_b = bot_verts[2 * n_outer - 1 - i], bot_verts[2 * n_outer - 2 - i]
        bm.faces.new((ob_a, ob_b, ib_b, ib_a))
        ot_a, ot_b = top_verts[i], top_verts[i + 1]
        it_a, it_b = top_verts[2 * n_outer - 1 - i], top_verts[2 * n_outer - 2 - i]
        bm.faces.new((ot_a, it_a, it_b, ot_b))
    # Side walls along the closed ring
    m = len(ring)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new((bot_verts[i], bot_verts[j], top_verts[j], top_verts[i]))

    mesh = bpy.data.meshes.new("top_yoke_arch_mesh")
    bm.to_mesh(mesh)
    bm.free()
    arch = bpy.data.objects.new("top_yoke", mesh)
    bpy.context.collection.objects.link(arch)
    # Pre-clean with a UNION-with-self to neutralize EXACT-solver quirks
    return arch


def cut_internal_raceway(arch: bpy.types.Object) -> None:
    """Cut a small rectangular tunnel along the underside of each arm.

    Modeled as two thin boxes: one along the +X arm, one along the -X
    arm, both following the inner ellipse but Inset slightly.
    Implementation here is a simplified straight tunnel near the
    inner wall (not a true swept channel) - good enough for the print
    bringup; revisit for production with a true curve-sweep.
    """
    for side in (-1, +1):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        cube = bpy.context.active_object
        cube.name = f"raceway_{'L' if side < 0 else 'R'}"
        # Tunnel runs roughly along X from near-apex (x = side*8) out to
        # arm end (x = side*ARCH_SEMI_X_MM). Sits just below the inner
        # arch curve, at a representative average height.
        x0 = side * 8.0
        x1 = side * (ARCH_SEMI_X_MM - 2.0)
        x_mid = 0.5 * (x0 + x1)
        # Average y along the arc between x0 and x1
        # y = ARCH_SEMI_Y * sqrt(1 - (x/ARCH_SEMI_X)^2)
        def arc_y(x: float) -> float:
            u = max(-1.0, min(1.0, x / ARCH_SEMI_X_MM))
            return ARCH_SEMI_Y_MM * math.sqrt(max(0.0, 1.0 - u * u))
        y_mid = 0.5 * (arc_y(x0) + arc_y(x1)) - RACEWAY_INSET_MM - RACEWAY_H_MM / 2.0
        cube.location = (x_mid, y_mid, 0.0)
        cube.scale = (abs(x1 - x0), RACEWAY_H_MM, RACEWAY_W_MM)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        _apply_boolean(arch, cube, op="DIFFERENCE")


def cut_balun_cavity(arch: bpy.types.Object) -> None:
    """Hollow a service cavity at the arch apex for the 1:1 balun.

    Cavity opens downward (toward head) so it can be loaded/serviced
    from beneath; later, a snap-fit lid covers it.
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    cav = bpy.context.active_object
    cav.name = "balun_cavity"
    # Sit just below the apex inner surface; apex is at (0, ARCH_SEMI_Y, 0)
    y_top = ARCH_SEMI_Y_MM - 0.5  # cavity ceiling just inside outer wall
    y_center = y_top - BALUN_Y_MM / 2.0
    cav.location = (0.0, y_center, 0.0)
    cav.scale = (BALUN_X_MM, BALUN_Y_MM, BALUN_Z_MM)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _apply_boolean(arch, cav, op="DIFFERENCE")

    # Also cut a service-lid slot through the bottom (underside) of
    # the cavity so it can be opened.
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    lid = bpy.context.active_object
    lid.name = "balun_lid_slot"
    lid.location = (0.0, y_center - BALUN_Y_MM / 2.0, 0.0)
    lid.scale = (BALUN_LID_W_MM, ARCH_WALL_MM + 1.0, BALUN_LID_D_MM)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _apply_boolean(arch, lid, op="DIFFERENCE")


def add_arm_end_pad_and_bosses(arch: bpy.types.Object, side: int) -> None:
    """Add a flat mounting pad at one arm end + 3x M3 heat-set bosses.

    `side` = -1 (left, -X) or +1 (right, +X).
    The pad sits perpendicular to the arch tangent at the arm end,
    i.e. flat in the YZ plane (normal = +X for right, -X for left).
    Bolt triangle is equilateral, side = IFACE pattern_side_mm, centered
    on the pad center. Plate-local +Y maps to world +Y (down the arm).
    """
    side_name = "R" if side > 0 else "L"
    # Arm end is at x = side*ARCH_SEMI_X. Pad sits OUTBOARD of that
    # by ARM_END_PAD_T_MM/2 so it presents a clean mating face at
    # x = side*(ARCH_SEMI_X + ARM_END_PAD_T).
    x_pad_center = side * (ARCH_SEMI_X_MM + ARM_END_PAD_T_MM / 2.0)
    # Arm-end is at ear plane (y = 0), so pad center sits a touch
    # above ear plane to clear the ear; lift by half its height.
    y_pad_center = ARM_END_PAD_H_MM / 2.0 - 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    pad = bpy.context.active_object
    pad.name = f"arm_pad_{side_name}"
    pad.location = (x_pad_center, y_pad_center, 0.0)
    pad.scale = (ARM_END_PAD_T_MM, ARM_END_PAD_H_MM, ARM_END_PAD_W_MM)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Union the pad into the arch
    mod = arch.modifiers.new(name=f"pad_{side_name}", type="BOOLEAN")
    mod.operation = "UNION"
    mod.object = pad
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = arch
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(pad, do_unlink=True)

    # 3 M3 heat-set bosses arranged as equilateral triangle on the
    # outboard face of the pad. Triangle lies in the YZ plane.
    s = IFACE_YOKE_TEMPLE.pattern_side_mm
    # Equilateral triangle centered at (y_pad_center, 0) in YZ:
    # vertex 1 up, vertices 2 & 3 lower-left / lower-right.
    R_circ = s / math.sqrt(3.0)  # circumradius
    triangle_pts_yz = [
        (y_pad_center + R_circ, 0.0),
        (y_pad_center - R_circ / 2.0, -s / 2.0),
        (y_pad_center - R_circ / 2.0, +s / 2.0),
    ]
    # Bosses are cylinders along +/-X (outboard); cut blind holes that
    # accept the heat-set inserts.
    pad_outer_x = side * (ARCH_SEMI_X_MM + ARM_END_PAD_T_MM)
    for (y, z) in triangle_pts_yz:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=M3_HEATSET_OD_MM / 2.0,
            depth=BOSS_DEPTH_MM + 0.2,
            vertices=32,
        )
        hole = bpy.context.active_object
        hole.name = f"insert_{side_name}_y{y:+.1f}_z{z:+.1f}"
        hole.rotation_euler = (0.0, math.pi / 2.0, 0.0)  # axis along X
        # Center the hole so it eats from the outboard face inward
        hole.location = (
            pad_outer_x - side * (BOSS_DEPTH_MM / 2.0),
            y, z,
        )
        _apply_boolean(arch, hole, op="DIFFERENCE")


# ---------------------------------------------------------------------------
# Export + sidecar
# ---------------------------------------------------------------------------

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


def write_sidecar(obj: bpy.types.Object, out_path: Path) -> None:
    """Write a .txt next to the STL with bbox, mass estimate, ifaces."""
    bb = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not bb:
        return
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    dx, dy, dz = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    # PETG density 1.27 g/cc; this approx assumes ~25% infill on bbox
    # (very rough; real slicer is authoritative).
    petg_density_g_per_cc = 1.27
    bbox_vol_cc = (dx * dy * dz) / 1000.0
    est_mass_g = bbox_vol_cc * petg_density_g_per_cc * 0.25
    side_path = out_path.with_suffix(".txt")
    side_path.write_text(
        f"top_yoke_r1\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  bbox_vol_cc: {bbox_vol_cc:.1f}\n"
        f"  est_mass_g (PETG, 25%% bbox-infill rough): {est_mass_g:.1f}\n"
        f"  interfaces_consumed:\n"
        f"    - IFACE_YOKE_TEMPLE (x2, one per arm end)\n"
        f"  fasteners: 6x M3 heat-set inserts (3 per side)\n"
        f"  balun_cavity_mm: {BALUN_X_MM} x {BALUN_Y_MM} x {BALUN_Z_MM} (interior)\n"
        f"  raceway_section_mm: {RACEWAY_W_MM} x {RACEWAY_H_MM} (per arm)\n"
    )
    print(f"Wrote sidecar {side_path}")


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)

    reset_scene()
    arch = make_elliptical_arch()
    cut_internal_raceway(arch)
    cut_balun_cavity(arch)
    add_arm_end_pad_and_bosses(arch, side=-1)
    add_arm_end_pad_and_bosses(arch, side=+1)
    export_stl(arch, args.out)
    write_sidecar(arch, args.out)

    print("---- IFACE_YOKE_TEMPLE consumed ----")
    print(f"  bolts: {IFACE_YOKE_TEMPLE.bolt_count}x {IFACE_YOKE_TEMPLE.bolt_size}")
    print(f"  pattern: {IFACE_YOKE_TEMPLE.pattern} side={IFACE_YOKE_TEMPLE.pattern_side_mm} mm")
    print(f"  insert: {IFACE_YOKE_TEMPLE.insert}")
    print(f"  design_load_N: {IFACE_YOKE_TEMPLE.design_load_N}")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
