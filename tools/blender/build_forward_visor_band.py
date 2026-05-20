#!/usr/bin/env -S blender --background --python
"""
build_forward_visor_band.py - parametric generator for the brow-arc band.

Forward Visor-Band: curved band spanning the forehead between L+R Temple
Plates. Hosts the front Psi-Stabilizer pocket (one of two stabilizers,
front-center), the MIL-STD-1913 Picatinny sub-rail along its lower outer
edge (180-deg forward arc), and pin-hinge tabs at each end that mate
into the FwdBand hinge bosses on the Temple Plates.

Run:
    blender --background --python tools/blender/build_forward_visor_band.py \\
        -- --out 3D-Models/HelmKit/_generated/forward_visor_band_r1.stl

Datum (world frame for this part):
    +X = ear-to-ear (band spans +/-X)
    +Y = up
    +Z = forward (band arcs forward of head; +Z is brow-out direction)
The band is a circular arc band centered on the head, arcing forward
across the brow.

Interfaces consumed:
    IFACE_TEMPLE_FWDBAND     (mirror end of the hinge; tabs on band carry
                              3mm steel pin, bore aligned to plate boss)
    IFACE_BAND_STABILIZER    (front-center pocket 64x34x4 mm + 2x M3 heatset)
    IFACE_BAND_SUBRAIL       (Picatinny rail along lower outer edge, 180-deg
                              forward arc; HP-FL=-30, HP-FR=+30 stations)

Status: SCAFFOLD. All IFACE numerics honoured. Picatinny rendered as a
linear strip along the front face (true arc-following Picatinny is a
bigger lift -- noted as a TODO for r2).
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
    IFACE_TEMPLE_FWDBAND,
    IFACE_BAND_STABILIZER,
    IFACE_BAND_SUBRAIL,
    M3_HEATSET_OD_MM,
    M3_HEATSET_LEN_MM,
)


# ---------------------------------------------------------------------------
# Band geometry
# ---------------------------------------------------------------------------

BAND_INNER_R_MM = 95.0     # inner radius (head fit)
BAND_WALL_MM = 4.0         # PETG wall thickness (radial)
BAND_HEIGHT_MM = 38.0      # vertical extent (Y) along forehead
BAND_ARC_DEG = 180.0       # forward semicircle
# Centered on +Z (forward). In our XZ plane arc convention:
#   angle 0   = +X (right ear)
#   angle 90  = +Z (brow)
#   angle 180 = -X (left ear)
# Band covers angle 0 -> 180 (the forward 180 deg).

# Hinge tabs at each end of the band
HINGE_TAB_W_MM = 12.0      # tab width along band length (arc)
HINGE_TAB_H_MM = 14.0      # tab height (Y)
HINGE_TAB_T_MM = 5.0       # tab thickness (radial)
HINGE_PIN_BORE_DIA_MM = IFACE_TEMPLE_FWDBAND.pin_dia_mm + 0.2  # 3.2 slip-fit

# Stabilizer pocket (front-center)
POCKET_W_MM, POCKET_H_MM, POCKET_D_MM = IFACE_BAND_STABILIZER.pocket_internal_mm
# (64 x 34 x 4)
POCKET_M3_PITCH_MM = POCKET_W_MM - 8.0  # 56 mm between retention screws

# Picatinny rail params (verbatim from IFACE_BAND_SUBRAIL)
RAIL = IFACE_BAND_SUBRAIL


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Band body
# ---------------------------------------------------------------------------

def make_arc_band() -> bpy.types.Object:
    """Build the arc band: annulus segment extruded along Y.

    Arc lies in the XZ plane, sweeping from angle 0 (+X, right ear) to
    angle 180 deg (-X, left ear), passing through +Z (brow) at 90 deg.
    Extruded vertically along Y (height = BAND_HEIGHT_MM).
    """
    bm = bmesh.new()
    n = 96
    outer_r = BAND_INNER_R_MM + BAND_WALL_MM
    inner_r = BAND_INNER_R_MM
    arc_rad = math.radians(BAND_ARC_DEG)
    pts_outer = []
    pts_inner = []
    for i in range(n + 1):
        t = (i / n) * arc_rad   # 0 .. pi
        pts_outer.append((outer_r * math.cos(t), outer_r * math.sin(t)))
        pts_inner.append((inner_r * math.cos(t), inner_r * math.sin(t)))
    # Build closed 2D ring: outer 0->pi, then inner pi->0
    ring_2d = []
    for x, z in pts_outer:
        ring_2d.append((x, z))
    for x, z in reversed(pts_inner):
        ring_2d.append((x, z))
    y_lo, y_hi = -BAND_HEIGHT_MM / 2.0, +BAND_HEIGHT_MM / 2.0
    bot = [bm.verts.new((x, y_lo, z)) for (x, z) in ring_2d]
    top = [bm.verts.new((x, y_hi, z)) for (x, z) in ring_2d]
    # Cap faces: quads between outer and inner edges
    n_outer = n + 1
    for i in range(n):
        ob_a, ob_b = bot[i], bot[i + 1]
        ib_a, ib_b = bot[2 * n_outer - 1 - i], bot[2 * n_outer - 2 - i]
        bm.faces.new((ob_a, ob_b, ib_b, ib_a))
        ot_a, ot_b = top[i], top[i + 1]
        it_a, it_b = top[2 * n_outer - 1 - i], top[2 * n_outer - 2 - i]
        bm.faces.new((ot_a, it_a, it_b, ot_b))
    # Side walls along the closed ring
    m = len(ring_2d)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    mesh = bpy.data.meshes.new("fwd_band_mesh")
    bm.to_mesh(mesh)
    bm.free()
    band = bpy.data.objects.new("forward_visor_band", mesh)
    bpy.context.collection.objects.link(band)
    return band


def add_hinge_tabs(band: bpy.types.Object) -> None:
    """Add tabs at each band end with 3 mm pin bores aligned along Z.

    Tab axis (the pin axis) per IFACE is the world Z direction (ear-to-
    ear horizontal in the plate-local frame is the band-Z direction --
    note this maps to band's RADIAL direction at the end). For the
    band, the natural hinge axis is approximately RADIAL at the tab's
    arc position. At the band ends (angle 0 = +X, angle 180 = -X),
    the radial axis is exactly +/- X, which IS the world ear-to-ear
    axis. So the pin bore runs along X at each end. Good.
    """
    for side, ang_deg in (("R", 0.0), ("L", 180.0)):
        t = math.radians(ang_deg)
        r_mid = BAND_INNER_R_MM + BAND_WALL_MM / 2.0
        cx = r_mid * math.cos(t)
        cz = r_mid * math.sin(t)
        # Tab sticks RADIALLY outward from band end, by HINGE_TAB_W/2
        # so it overlaps with the band wall and extends a bit beyond.
        # Use a box of length HINGE_TAB_W along the radial direction.
        tab_offset_r = HINGE_TAB_W_MM / 2.0
        tab_cx = (r_mid + tab_offset_r - HINGE_TAB_W_MM / 2.0) * math.cos(t) + \
                 (HINGE_TAB_W_MM / 2.0) * math.cos(t)
        # Simpler: position tab center at radial r = r_mid (band middle),
        # and extend HINGE_TAB_W along the local tangent (which at angle
        # 0 or 180 is along +/- Z).
        tab_cx = r_mid * math.cos(t)
        tab_cz = r_mid * math.sin(t)
        # Tangent at angle t in XZ plane: (-sin(t), cos(t))
        # At t=0: tangent = (0, 1) -> +Z
        # At t=pi: tangent = (0, -1) -> -Z
        # Offset tab center along tangent by HINGE_TAB_W/2 to "stick out"
        tan_x = -math.sin(t)
        tan_z = math.cos(t)
        tab_cx += tan_x * HINGE_TAB_W_MM / 2.0
        tab_cz += tan_z * HINGE_TAB_W_MM / 2.0
        # Tab dims: along band length (tangent) = HINGE_TAB_W, vertical
        # Y = HINGE_TAB_H, radial thickness = HINGE_TAB_T.
        # We approximate the tab as an axis-aligned box rotated about Y
        # by angle t. Since at t=0 or pi the box is already axis-aligned,
        # this is exact for the band ends.
        # At angle 0: tab spans +Z (tangent), Y, X (radial)
        # At angle pi: tab spans -Z (tangent), Y, X (radial)
        tab = _add_box(f"hinge_tab_{side}",
                       (tab_cx, 0.0, tab_cz),
                       (HINGE_TAB_T_MM, HINGE_TAB_H_MM, HINGE_TAB_W_MM))
        # Note: at angle pi the tab is just on the -X side; same box dims.
        _bool(band, tab, op="UNION")
        # Pin bore: along X (the hinge axis is +/- X at the band ends)
        bore_len = HINGE_TAB_T_MM + BAND_WALL_MM + 4.0
        # Center the bore on the tab's X position; if at t=0 the band
        # extends to +X, bore center sits at tab_cx (slightly past +X
        # face of band).
        bore = _add_cylinder(f"hinge_bore_{side}",
                             (tab_cx, 0.0, tab_cz),
                             HINGE_PIN_BORE_DIA_MM / 2.0, bore_len, axis="X")
        _bool(band, bore, op="DIFFERENCE")


def add_stabilizer_pocket(band: bpy.types.Object) -> None:
    """Front-center pocket (64x34x4 mm) into the OUTER face of the band.

    Located at angle 90 deg (+Z direction, brow center). Pocket opens
    outward (radially out of the band). 2x M3 heatset holes on either
    side of the pocket for the snap-fit cover plate.
    """
    # Pocket center at brow apex
    r_pocket_face = BAND_INNER_R_MM + BAND_WALL_MM + 0.2  # +0.2 to bite outward face
    # Pocket cuts inward by POCKET_D_MM (4 mm)
    # So center the cutter at radial = r_outer - POCKET_D_MM/2
    r_cutter_center = BAND_INNER_R_MM + BAND_WALL_MM - POCKET_D_MM / 2.0 + 0.2
    pocket = _add_box("stabilizer_pocket",
                      (0.0, 0.0, r_cutter_center),
                      (POCKET_W_MM, POCKET_H_MM, POCKET_D_MM + 0.4))
    _bool(band, pocket, op="DIFFERENCE")
    # Cable exit grommet on inboard face (head-facing side)
    grommet_dia = IFACE_BAND_STABILIZER.cable_exit_grommet_dia_mm
    grommet = _add_cylinder("stab_cable_grommet",
                            (0.0, 0.0, BAND_INNER_R_MM + BAND_WALL_MM / 2.0),
                            grommet_dia / 2.0, BAND_WALL_MM + 2.0, axis="Z")
    _bool(band, grommet, op="DIFFERENCE")
    # 2x M3 heatset for cover plate retention (above + below pocket center,
    # along Y axis since pocket is wider in X than Y; cover screws sit
    # in the meat above and below the pocket)
    for i, dy in enumerate((-POCKET_H_MM / 2.0 - 4.0, +POCKET_H_MM / 2.0 + 4.0)):
        hole = _add_cylinder(f"stab_cover_m3_{i}",
                             (0.0, dy, BAND_INNER_R_MM + BAND_WALL_MM - M3_HEATSET_LEN_MM / 2.0),
                             M3_HEATSET_OD_MM / 2.0, M3_HEATSET_LEN_MM + 0.2,
                             axis="Z")
        _bool(band, hole, op="DIFFERENCE")


def add_picatinny_rail_strip(band: bpy.types.Object) -> None:
    """Add a flat Picatinny strip tangent to the band's lower-outer edge.

    Renders the MIL-STD-1913 cross-section as a linear strip placed
    along the brow center (angle 90 deg, +Z), sized to cover the
    HP-FL (-30 deg) to HP-FR (+30 deg) stations plus margin.

    Geometry (verbatim from IFACE_BAND_SUBRAIL):
        bottom_w_mm = 19.0  (base width)
        top_w_mm    = 10.2  (rail top width)
        depth_mm    = 3.4   (height)
        Cross-section is a trapezoid with 45-deg shoulders.

    Picatinny slot/tooth alternation along length:
        tooth_w = 5.0, slot_w = 5.55, pitch = 10.55 mm

    NOTE: Real production part should follow the arc; this scaffold
    uses a flat tangent strip for first-print fit-check. r2 will sweep
    the cross-section along the arc curve.
    """
    # Rail strip length: cover HP-FL to HP-FR stations (60 deg of arc)
    # arc length at r_outer over 60 deg
    r_outer = BAND_INNER_R_MM + BAND_WALL_MM
    rail_arc_rad = math.radians(60.0 + 20.0)  # 80 deg = stations + margin
    rail_length_mm = r_outer * rail_arc_rad
    n_slots = int(rail_length_mm // RAIL.pitch_mm)
    rail_length_mm = n_slots * RAIL.pitch_mm + RAIL.tooth_w_mm  # snap to whole teeth

    # Strip base: trapezoidal prism extruded along X (tangent at brow).
    # Lives at brow center: y at the LOWER edge of band, z just outside
    # band outer face.
    y_rail_top = -BAND_HEIGHT_MM / 2.0 + 0.5   # rail sits just inside band lower
    y_rail_center = y_rail_top - RAIL.depth_mm / 2.0
    z_rail_inner = r_outer - 0.2               # bite into band surface
    z_rail_outer = z_rail_inner + RAIL.depth_mm + 0.1  # rough; trapezoid trimmed

    # Build the trapezoidal prism in bmesh
    bm = bmesh.new()
    x_lo = -rail_length_mm / 2.0
    x_hi = +rail_length_mm / 2.0
    # Cross-section in YZ plane (Y vertical, Z radial-out):
    #   bottom (against band):    width bottom_w along X??? NO.
    # Standard Picatinny: looking at cross-section, bottom is the wide
    # mating face that sits on the firearm receiver; top is the narrower
    # rail with shoulders. "Width" is the SIDE-TO-SIDE dimension of the
    # rail cross-section. The rail's LENGTH runs along its sliding axis.
    # In our setup: rail's length = X (tangent at brow), cross-section
    # is in YZ (height = Y, width = Z? or vice versa). To keep the
    # rail mounted "lower-edge outer face" with its base against the
    # band outer surface (Z-out), and accessories slide along X, the
    # cross-section is:
    #   - base (bottom_w = 19.0) lies along Y (vertical), against +Z face
    #   - top (top_w = 10.2)     lies along Y, on +Z side (outboard)
    #   - depth (3.4)            along Z (radial-out)
    # Hmm -- actually accessory rides on TOP of the rail. The 19/10.2
    # widths are perpendicular to BOTH length AND height. Length=X (
    # slide axis), height = Z (radial-out, also the accessory-clamping
    # axis), width = Y (cross-clamping direction). So:
    #   verts at x_lo: 4 corners of trapezoid in YZ plane
    #     (y = -bot_w/2, z = z_inner)   bottom-left
    #     (y = +bot_w/2, z = z_inner)   bottom-right
    #     (y = +top_w/2, z = z_outer)   top-right
    #     (y = -top_w/2, z = z_outer)   top-left
    # But the rail mounts on the BAND's outer surface, so the base
    # face (wide) should sit ON the band -> base z = z_inner (smaller r),
    # top z = z_outer (larger r). The accessory clamps from the SIDES
    # (Y direction). Good.
    half_bot = RAIL.bottom_w_mm / 2.0
    half_top = RAIL.top_w_mm / 2.0
    z_in = z_rail_inner
    z_out = z_rail_inner + RAIL.depth_mm

    def quad(x_val):
        return [
            bm.verts.new((x_val, -half_bot, z_in)),
            bm.verts.new((x_val, +half_bot, z_in)),
            bm.verts.new((x_val, +half_top, z_out)),
            bm.verts.new((x_val, -half_top, z_out)),
        ]
    v_lo = quad(x_lo)
    v_hi = quad(x_hi)
    bm.faces.new(v_lo[::-1])
    bm.faces.new(v_hi)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((v_lo[i], v_lo[j], v_hi[j], v_hi[i]))
    # Shift everything down to y_rail_center
    for v in bm.verts:
        v.co.y += y_rail_center
    mesh = bpy.data.meshes.new("picatinny_base_mesh")
    bm.to_mesh(mesh)
    bm.free()
    rail = bpy.data.objects.new("picatinny_base", mesh)
    bpy.context.collection.objects.link(rail)
    _bool(band, rail, op="UNION")

    # Cut Picatinny SLOTS across the rail at each pitch interval
    # Slot is a transverse cut: width = slot_w along X, full depth along
    # Z, full width along Y (cuts all the way through cross-section).
    x_start = -rail_length_mm / 2.0 + RAIL.tooth_w_mm
    for i in range(n_slots):
        x_slot_center = x_start + i * RAIL.pitch_mm + RAIL.slot_w_mm / 2.0
        slot = _add_box(f"pic_slot_{i}",
                        (x_slot_center,
                         y_rail_center,
                         (z_in + z_out) / 2.0),
                        (RAIL.slot_w_mm,
                         RAIL.bottom_w_mm + 2.0,
                         RAIL.depth_mm + 0.4))
        _bool(band, slot, op="DIFFERENCE")


# ---------------------------------------------------------------------------
# Export + sidecar
# ---------------------------------------------------------------------------

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
    if not bb:
        return
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    dx, dy, dz = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    petg_density = 1.27
    est_mass = (dx * dy * dz) / 1000.0 * petg_density * 0.15  # arc is mostly air
    side = out_path.with_suffix(".txt")
    side.write_text(
        "forward_visor_band_r1\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  est_mass_g (PETG, ~15pct bbox-fill rough): {est_mass:.1f}\n"
        f"  inner_radius_mm: {BAND_INNER_R_MM}\n"
        f"  wall_mm: {BAND_WALL_MM}\n"
        f"  height_mm: {BAND_HEIGHT_MM}\n"
        f"  arc_deg: {BAND_ARC_DEG}\n"
        "  interfaces_consumed:\n"
        "    - IFACE_TEMPLE_FWDBAND   (2x hinge tabs, 3mm pin bores along +/-X)\n"
        f"    - IFACE_BAND_STABILIZER  (front-center pocket {POCKET_W_MM}x{POCKET_H_MM}x{POCKET_D_MM} mm)\n"
        f"    - IFACE_BAND_SUBRAIL     (Picatinny strip, ~80 deg arc coverage)\n"
        "  picatinny_dims_mm:\n"
        f"    tooth_w={RAIL.tooth_w_mm} slot_w={RAIL.slot_w_mm} pitch={RAIL.pitch_mm}\n"
        f"    top_w={RAIL.top_w_mm}  bottom_w={RAIL.bottom_w_mm}  depth={RAIL.depth_mm}\n"
        "  fasteners (per band):\n"
        "    - 2x 3mm steel pin (hinge to L+R Temple Plate FwdBand bosses)\n"
        "    - 2x M3 heatset   (stabilizer cover plate retention)\n"
        "  TODOs for r2:\n"
        "    - True arc-following Picatinny (sweep cross-section along curve)\n"
        "    - Snap-fit cover plate STL companion part\n"
        "    - Cable raceway internal channel along band underside\n"
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
    add_picatinny_rail_strip(band)
    export_stl(band, args.out)
    write_sidecar(band, args.out)

    print("---- IFACE_BAND_SUBRAIL verbatim ----")
    print(f"  standard:    {RAIL.rail_standard}")
    print(f"  tooth/slot/pitch (mm): {RAIL.tooth_w_mm}/{RAIL.slot_w_mm}/{RAIL.pitch_mm}")
    print(f"  top/bottom/depth (mm): {RAIL.top_w_mm}/{RAIL.bottom_w_mm}/{RAIL.depth_mm}")
    print(f"  stations: HP-FL={RAIL.station_HP_FL_deg} HP-FR={RAIL.station_HP_FR_deg}")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
