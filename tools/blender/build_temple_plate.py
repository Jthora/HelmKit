#!/usr/bin/env -S blender --background --python
"""
build_temple_plate.py - parametric generator for HelmKit Mk0.5-beta Temple Plate.

The Temple Plate is the structural confluence of the helm: 4 independent
co-located pivots, the cheek-hook for the chin yoke, the yoke bolt cluster,
and the sidehelm pod sliding-dovetail mount. One STL serves L and R (the
plate-local frame is mirror-symmetric per IFACE conventions; the L/R
distinction is purely world placement).

Run:
    blender --background --python tools/blender/build_temple_plate.py \\
        -- --out 3D-Models/HelmKit/_generated/temple_plate_r1.stl

Datum convention (plate-local, per interfaces.py / sec 12):
    +X = forward (toward brow)
    +Y = up      (toward crown)
    +Z = outward (away from head, ear-to-ear axis in world)
Origin = centroid of outer face.

Interfaces consumed:
    IFACE_YOKE_TEMPLE        (3x M3 cluster at upper edge centroid)
    IFACE_TEMPLE_FWDBAND     (hinge boss + pin hole at (+8, -6, 0))
    IFACE_TEMPLE_REARBAND    (hinge boss + pin hole at (-8, -6, 0))
    IFACE_TEMPLE_PYLON       (live-hinge foot pad + 2x M2 heatset at (-5,+10,+4))
    IFACE_TEMPLE_DEFENDER    (Option-A standoff arm + 2-axis pitch pin at (+15,+10,+10))
    IFACE_TEMPLE_CHEEK       (cheek hook + webbing slot at (-15, -20, 0))
    IFACE_TEMPLE_SIDEHELM_POD (sliding dovetail female slot at lower-aft face)

Status: SCAFFOLD. Honours every IFACE numeric contract. Visual quality
intentionally rough (boxy bosses, no fillets); intended for fit-checks
+ first physical print, not final aesthetics. G-Fit / G-Defender-Aim /
G-Pull / G-Pod gates pending physical validation.
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
    print("ERROR: run inside Blender:")
    print("  blender --background --python tools/blender/build_temple_plate.py")
    sys.exit(1)

from interfaces import (  # type: ignore  # noqa: E402
    IFACE_YOKE_TEMPLE,
    IFACE_TEMPLE_FWDBAND,
    IFACE_TEMPLE_REARBAND,
    IFACE_TEMPLE_PYLON,
    IFACE_TEMPLE_DEFENDER,
    IFACE_TEMPLE_CHEEK,
    IFACE_TEMPLE_SIDEHELM_POD,
    M2_CLEAR_DIA_MM,
    M2_HEATSET_OD_MM,
    M2_HEATSET_LEN_MM,
    M3_HEATSET_OD_MM,
    M3_HEATSET_LEN_MM,
)


# ---------------------------------------------------------------------------
# Plate body parameters (chosen to host all interface features with margin)
# ---------------------------------------------------------------------------

PLATE_X_MIN = -30.0       # aft edge
PLATE_X_MAX = +35.0       # forward edge
PLATE_Y_MIN = -28.0       # bottom edge (below cheek hook)
PLATE_Y_MAX = +25.0       # top edge (above yoke cluster)
PLATE_WALL_MM = 4.0       # 3 mm shell + 1 mm ribs (sec 5 row)
PLATE_RIB_THK_MM = 1.0    # ribs on inner face at pivots/bolts (rendered as
                          # extra thickness around feature bosses; not
                          # broken out as separate ribs in this scaffold).

# Hinge boss dimensions for visor-band pins (FwdBand + RearBand)
HINGE_BOSS_DIA_MM = 10.0  # outer dia of cylindrical boss around 3 mm pin
HINGE_BOSS_LEN_MM = 8.0   # length along plate-local Z (outward)
HINGE_PIN_BORE_DIA_MM = IFACE_TEMPLE_FWDBAND.pin_dia_mm + 0.2  # slip-fit

# Pylon live-hinge foot pad
PYLON_FOOT_X_MM = IFACE_TEMPLE_PYLON.foot_footprint_mm[0]   # 8
PYLON_FOOT_Y_MM = IFACE_TEMPLE_PYLON.foot_footprint_mm[1]   # 12
PYLON_FOOT_THK_MM = IFACE_TEMPLE_PYLON.foot_thickness_mm    # 3
PYLON_M2_BORE_DIA_MM = M2_HEATSET_OD_MM                     # 3.6
PYLON_M2_BORE_DEPTH_MM = M2_HEATSET_LEN_MM + 1.0            # 5

# Cheek hook
CHEEK_TAB_X_MM = 14.0     # length along +/-X (slot fits inside)
CHEEK_TAB_Y_MM = 10.0     # height along Y
CHEEK_TAB_Z_MM = 4.0      # thickness outward
CHEEK_SLOT_W_MM = IFACE_TEMPLE_CHEEK.webbing_slot_w_mm     # 26 -> exceeds tab,
                                                            # so make tab wider
CHEEK_SLOT_H_MM = IFACE_TEMPLE_CHEEK.webbing_slot_h_mm     # 4
CHEEK_TAB_X_MM = max(CHEEK_TAB_X_MM, CHEEK_SLOT_W_MM + 4.0)  # leave 2 mm rim

# Defender standoff arm (Phase-3 Option A)
DEF_ROOT = IFACE_TEMPLE_DEFENDER.standoff_root_local_mm   # (5, 8, 0)
DEF_TIP = IFACE_TEMPLE_DEFENDER.standoff_tip_local_mm     # (15, 10, 10)
DEF_SEC_X, DEF_SEC_Y = IFACE_TEMPLE_DEFENDER.standoff_section_mm  # (8, 6)
DEF_PIN = IFACE_TEMPLE_DEFENDER.pin_local_mm              # (15, 10, 10)
DEF_PIN_BORE_DIA_MM = IFACE_TEMPLE_DEFENDER.pitch_pin_dia_mm + 0.2  # 2.2

# Sidehelm dovetail (female slot, runs along X on the lower-aft face)
SH_DT_TOP_W = IFACE_TEMPLE_SIDEHELM_POD.dovetail_top_w_mm        # 12 (opening)
SH_DT_BOT_W = IFACE_TEMPLE_SIDEHELM_POD.dovetail_bottom_w_mm     # 18 (deeper)
SH_DT_DEPTH = IFACE_TEMPLE_SIDEHELM_POD.dovetail_depth_mm        # 3.4
SH_DT_LEN = IFACE_TEMPLE_SIDEHELM_POD.dovetail_length_mm         # 35
SH_DT_CENTER_X = -8.0    # along plate-local X (centered slightly aft)
SH_DT_CENTER_Y = -26.0   # along lower edge of plate (just above plate bottom)


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def _bool(host: bpy.types.Object, tool: bpy.types.Object,
          op: str = "DIFFERENCE", solver: str = "EXACT") -> None:
    mod = host.modifiers.new(name=f"b_{tool.name[:24]}", type="BOOLEAN")
    mod.operation = op
    mod.object = tool
    mod.solver = solver
    bpy.context.view_layer.objects.active = host
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def _add_box(name: str, center, dims) -> bpy.types.Object:
    cx, cy, cz = center
    dx, dy, dz = dims
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    o = bpy.context.active_object
    o.name = name
    o.location = (cx, cy, cz)
    o.scale = (dx, dy, dz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return o


def _add_cylinder(name: str, center, radius: float, depth: float,
                  axis: str = "Z", verts: int = 48) -> bpy.types.Object:
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
# Body construction
# ---------------------------------------------------------------------------

def build_plate_body() -> bpy.types.Object:
    """Base slab spanning the plate-local rectangle, PLATE_WALL_MM thick (Z)."""
    cx = (PLATE_X_MIN + PLATE_X_MAX) / 2.0
    cy = (PLATE_Y_MIN + PLATE_Y_MAX) / 2.0
    dx = PLATE_X_MAX - PLATE_X_MIN
    dy = PLATE_Y_MAX - PLATE_Y_MIN
    plate = _add_box("temple_plate", (cx, cy, PLATE_WALL_MM / 2.0),
                     (dx, dy, PLATE_WALL_MM))
    return plate


def add_yoke_cluster(plate: bpy.types.Object) -> None:
    """3x M3 heatset bosses + holes at IFACE_YOKE_TEMPLE centroid."""
    cx, cy, _ = IFACE_YOKE_TEMPLE.centroid_local_mm  # (0, 18, 0)
    s = IFACE_YOKE_TEMPLE.pattern_side_mm
    R_circ = s / math.sqrt(3.0)
    # Triangle in plate's XY plane, one vertex up (+Y), two lower
    pts = [
        (cx,                cy + R_circ),
        (cx - s / 2.0,      cy - R_circ / 2.0),
        (cx + s / 2.0,      cy - R_circ / 2.0),
    ]
    # Add a unified rib pad under the cluster for extra thickness (1 mm rib)
    rib = _add_box("yoke_rib", (cx, cy, PLATE_WALL_MM + PLATE_RIB_THK_MM / 2.0),
                   (s + 6.0, s + 6.0, PLATE_RIB_THK_MM))
    _bool(plate, rib, op="UNION")
    # Bosses + holes
    boss_dia = M3_HEATSET_OD_MM + 4.0  # 5 mm insert + 2 mm wall each side
    boss_h = M3_HEATSET_LEN_MM + 1.0   # 6 mm
    for i, (x, y) in enumerate(pts):
        boss = _add_cylinder(f"yoke_boss_{i}",
                             (x, y, PLATE_WALL_MM + boss_h / 2.0),
                             boss_dia / 2.0, boss_h, axis="Z")
        _bool(plate, boss, op="UNION")
        hole = _add_cylinder(f"yoke_hole_{i}",
                             (x, y, PLATE_WALL_MM + boss_h - (M3_HEATSET_LEN_MM + 0.2) / 2.0),
                             M3_HEATSET_OD_MM / 2.0, M3_HEATSET_LEN_MM + 0.2, axis="Z")
        _bool(plate, hole, op="DIFFERENCE")


def add_visor_band_hinges(plate: bpy.types.Object) -> None:
    """Cylindrical hinge bosses for FwdBand and RearBand pins.

    Axis is along plate-local Z (ear-to-ear horizontal in world). Boss
    sticks out +Z (outward); pin bore runs the full length.
    """
    for iface, name in (
        (IFACE_TEMPLE_FWDBAND, "fwdband"),
        (IFACE_TEMPLE_REARBAND, "rearband"),
    ):
        x, y, _ = iface.axis_local_mm  # (+/-8, -6, 0)
        # Boss center is offset outward in +Z so it stands proud of plate
        z_center = PLATE_WALL_MM + HINGE_BOSS_LEN_MM / 2.0
        boss = _add_cylinder(f"{name}_boss", (x, y, z_center),
                             HINGE_BOSS_DIA_MM / 2.0, HINGE_BOSS_LEN_MM,
                             axis="Z")
        _bool(plate, boss, op="UNION")
        # Through-bore for the pin (slip fit)
        bore_depth = HINGE_BOSS_LEN_MM + PLATE_WALL_MM + 2.0
        bore = _add_cylinder(f"{name}_bore", (x, y, bore_depth / 2.0 - 1.0),
                             HINGE_PIN_BORE_DIA_MM / 2.0, bore_depth, axis="Z")
        _bool(plate, bore, op="DIFFERENCE")


def add_pylon_foot(plate: bpy.types.Object) -> None:
    """Flat foot pad with 2x M2 heatset holes at IFACE_TEMPLE_PYLON axis."""
    x, y, z = IFACE_TEMPLE_PYLON.axis_local_mm  # (-5, +10, +4)
    # Foot pad is a thin slab on the outer face (+Z), positioned so its
    # outer surface sits at plate-local Z = z (4 mm outboard of plate face)
    pad_z_center = PLATE_WALL_MM + (z - PLATE_WALL_MM) / 2.0 if z > PLATE_WALL_MM \
        else PLATE_WALL_MM + PYLON_FOOT_THK_MM / 2.0
    pad_thk = max(PYLON_FOOT_THK_MM, z - PLATE_WALL_MM)
    pad = _add_box("pylon_foot",
                   (x, y, PLATE_WALL_MM + pad_thk / 2.0),
                   (PYLON_FOOT_X_MM + 4.0, PYLON_FOOT_Y_MM + 4.0, pad_thk))
    _bool(plate, pad, op="UNION")
    # 2x M2 heatset bores spaced along Y (12 mm footprint -> 8 mm pitch)
    hole_pitch = PYLON_FOOT_Y_MM - 4.0  # 8
    for i, dy in enumerate((-hole_pitch / 2.0, +hole_pitch / 2.0)):
        hole = _add_cylinder(f"pylon_m2_{i}",
                             (x, y + dy, PLATE_WALL_MM + pad_thk - PYLON_M2_BORE_DEPTH_MM / 2.0),
                             PYLON_M2_BORE_DIA_MM / 2.0, PYLON_M2_BORE_DEPTH_MM,
                             axis="Z")
        _bool(plate, hole, op="DIFFERENCE")


def add_defender_standoff_and_cradle(plate: bpy.types.Object) -> None:
    """Phase-3 Option A: cantilever arm from plate to Defender pitch pin.

    Arm root: DEF_ROOT (5, 8, 0)  - sits on plate outer face
    Arm tip:  DEF_TIP  (15, 10, 10) - pitch pin centerline
    Section:  8 x 6 mm (X x Y)
    Cradle is rendered as the pitch-pin yoke -- a chunky boss with the
    pin bore through it. The actual coil cradle is a separate part
    (build_psi_defender_cradle.py), but we represent its envelope here
    as a visual hint and as the bore axis.
    """
    rx, ry, rz = DEF_ROOT
    tx, ty, tz = DEF_TIP
    # Bounding box that contains both root and tip
    arm_x_min = min(rx, tx) - DEF_SEC_X / 2.0 + (DEF_SEC_X / 2.0)
    arm_x_max = max(rx, tx) + (DEF_SEC_X / 2.0)
    arm_y_min = min(ry, ty) - (DEF_SEC_Y / 2.0)
    arm_y_max = max(ry, ty) + (DEF_SEC_Y / 2.0)
    arm_z_min = min(rz, tz)
    arm_z_max = max(rz, tz) + DEF_SEC_Y / 2.0  # ensure tip end is solid
    cx = (arm_x_min + arm_x_max) / 2.0
    cy = (arm_y_min + arm_y_max) / 2.0
    cz = (arm_z_min + arm_z_max) / 2.0
    dx = arm_x_max - arm_x_min
    dy = arm_y_max - arm_y_min
    dz = max(arm_z_max - arm_z_min, DEF_SEC_Y)
    arm = _add_box("defender_standoff", (cx, cy, cz), (dx, dy, dz))
    _bool(plate, arm, op="UNION")
    # Pitch-pin yoke: a small block centered on tip with the pin bore.
    yoke_dim = 10.0  # 10 mm cube around the pin
    pin_yoke = _add_box("pitch_yoke", (tx, ty, tz),
                        (yoke_dim, yoke_dim, yoke_dim))
    _bool(plate, pin_yoke, op="UNION")
    # Pin bore through the yoke along plate-local Y (vertical) -- the
    # pitch axis is the up-down axis so the cradle pitches fore/aft.
    bore_len = yoke_dim + 4.0
    bore = _add_cylinder("def_pin_bore", (tx, ty, tz),
                         DEF_PIN_BORE_DIA_MM / 2.0, bore_len, axis="Y")
    _bool(plate, bore, op="DIFFERENCE")


def add_cheek_hook(plate: bpy.types.Object) -> None:
    """Webbing-slot hook integral to lower edge at IFACE_TEMPLE_CHEEK location."""
    x, y, _ = IFACE_TEMPLE_CHEEK.hook_local_mm  # (-15, -20, 0)
    # Downward tab extending below plate, with rectangular through-slot
    # for 25 mm webbing (+/- a couple mm). Tab outer face is flush with
    # plate inner face; webbing rides on the outboard face of the tab.
    tab_center_y = y - CHEEK_TAB_Y_MM / 2.0  # below hook reference point
    tab_center_z = -CHEEK_TAB_Z_MM / 2.0     # tab on the INBOARD side (-Z)
    tab = _add_box("cheek_tab",
                   (x, tab_center_y, tab_center_z),
                   (CHEEK_TAB_X_MM, CHEEK_TAB_Y_MM, CHEEK_TAB_Z_MM))
    _bool(plate, tab, op="UNION")
    # Webbing slot cut through tab along Z
    slot = _add_box("cheek_slot",
                    (x, tab_center_y, tab_center_z),
                    (CHEEK_SLOT_W_MM, CHEEK_SLOT_H_MM, CHEEK_TAB_Z_MM + 2.0))
    _bool(plate, slot, op="DIFFERENCE")
    # Anti-pullout rib on the inboard face of the slot
    rib_h = IFACE_TEMPLE_CHEEK.anti_pullout_rib_h_mm
    rib = _add_box("cheek_rib",
                   (x, tab_center_y + CHEEK_SLOT_H_MM / 2.0 + rib_h / 2.0,
                    tab_center_z - CHEEK_TAB_Z_MM / 2.0 - rib_h / 2.0),
                   (CHEEK_SLOT_W_MM + 4.0, rib_h, rib_h))
    _bool(plate, rib, op="UNION")


def add_sidehelm_dovetail(plate: bpy.types.Object) -> None:
    """Female sliding dovetail along lower-aft face for sidehelm pod mount.

    Slot runs along plate-local X (length SH_DT_LEN), opens toward -Y
    (downward), and widens with depth (top_w narrower at opening, bot_w
    wider deeper inside). Cut from the underside of the plate; depth
    SH_DT_DEPTH (3.4 mm) eats into the plate slab from -Y.
    """
    # The plate slab is only 4 mm thick (Z); a dovetail can't be cut
    # straight DOWN into a 4 mm wall without breaking through. So we
    # add a thicker lower-aft boss first that the dovetail goes into.
    boss_y_center = SH_DT_CENTER_Y + (SH_DT_DEPTH + 2.0) / 2.0
    boss_h = SH_DT_DEPTH + 4.0   # 7.4 mm tall: room for slot + 4 mm meat
    boss_z_thk = PLATE_WALL_MM + 4.0   # 8 mm thick outward to host slot
    boss = _add_box("sidehelm_dt_boss",
                    (SH_DT_CENTER_X, SH_DT_CENTER_Y + boss_h / 2.0,
                     boss_z_thk / 2.0),
                    (SH_DT_LEN + 6.0, boss_h, boss_z_thk))
    _bool(plate, boss, op="UNION")

    # Trapezoidal slot: opens at -Y face (top of slot near boss bottom),
    # widens going +Y (deeper into the boss).
    y_open = SH_DT_CENTER_Y - 0.5            # slot mouth just below boss bottom
    y_deep = SH_DT_CENTER_Y + SH_DT_DEPTH    # slot floor
    z_center = boss_z_thk / 2.0
    z_lo = z_center - SH_DT_LEN / 2.0
    z_hi = z_center + SH_DT_LEN / 2.0
    # 8 verts of a trapezoidal prism (length along X actually; let me re-
    # derive: slot length runs along X (the SLIDING direction), and
    # trapezoid widens in the Y direction with depth Y).
    # Trapezoid lies in YX plane, extruded along Z (slot is a channel
    # whose CROSS-section is the trapezoid). Hmm -- a sliding dovetail
    # cut into a face: the slot's length axis = sliding direction (X),
    # and the trapezoid cross-section lies in the YZ plane.
    # Cross-section: opening width SH_DT_TOP_W along Z, mouth at -Y;
    # deep width SH_DT_BOT_W along Z, at +Y depth.
    bm = bmesh.new()
    x_lo = SH_DT_CENTER_X - SH_DT_LEN / 2.0
    x_hi = SH_DT_CENTER_X + SH_DT_LEN / 2.0
    # 4 cross-section verts at x_lo end:
    z_top_half_open = SH_DT_TOP_W / 2.0
    z_top_half_deep = SH_DT_BOT_W / 2.0
    v_lo = [
        bm.verts.new((x_lo, y_open, boss_z_thk / 2.0 - z_top_half_open)),
        bm.verts.new((x_lo, y_open, boss_z_thk / 2.0 + z_top_half_open)),
        bm.verts.new((x_lo, y_deep, boss_z_thk / 2.0 + z_top_half_deep)),
        bm.verts.new((x_lo, y_deep, boss_z_thk / 2.0 - z_top_half_deep)),
    ]
    v_hi = [
        bm.verts.new((x_hi, y_open, boss_z_thk / 2.0 - z_top_half_open)),
        bm.verts.new((x_hi, y_open, boss_z_thk / 2.0 + z_top_half_open)),
        bm.verts.new((x_hi, y_deep, boss_z_thk / 2.0 + z_top_half_deep)),
        bm.verts.new((x_hi, y_deep, boss_z_thk / 2.0 - z_top_half_deep)),
    ]
    bm.faces.new(v_lo[::-1])
    bm.faces.new(v_hi)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((v_lo[i], v_lo[j], v_hi[j], v_hi[i]))
    mesh = bpy.data.meshes.new("sh_dt_slot_mesh")
    bm.to_mesh(mesh)
    bm.free()
    cutter = bpy.data.objects.new("sh_dt_slot", mesh)
    bpy.context.collection.objects.link(cutter)
    _bool(plate, cutter, op="DIFFERENCE")

    # Thumbscrew lock hole through the boss (M3 clearance through wall,
    # heatset on the OPPOSITE face). Placed at one end of the slot.
    ts_x = SH_DT_CENTER_X + SH_DT_LEN / 2.0 - 5.0
    ts_y = SH_DT_CENTER_Y + SH_DT_DEPTH + 2.0
    # Through-hole along Z
    ts_bore = _add_cylinder("sh_dt_thumbscrew_bore",
                            (ts_x, ts_y, boss_z_thk / 2.0),
                            M3_HEATSET_OD_MM / 2.0,
                            boss_z_thk + 2.0, axis="Z")
    _bool(plate, ts_bore, op="DIFFERENCE")


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
    bb = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not bb:
        return
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    dx, dy, dz = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    petg_density = 1.27
    est_mass = (dx * dy * dz) / 1000.0 * petg_density * 0.20  # 20% bbox-infill rough
    side_path = out_path.with_suffix(".txt")
    side_path.write_text(
        "temple_plate_r1\n"
        "  (one STL serves L+R via mirrored world placement)\n"
        f"  bbox_mm: {dx:.1f} x {dy:.1f} x {dz:.1f}\n"
        f"  est_mass_g (PETG, 20pct bbox-infill rough): {est_mass:.1f}\n"
        "  interfaces_consumed:\n"
        "    - IFACE_YOKE_TEMPLE\n"
        "    - IFACE_TEMPLE_FWDBAND\n"
        "    - IFACE_TEMPLE_REARBAND\n"
        "    - IFACE_TEMPLE_PYLON\n"
        "    - IFACE_TEMPLE_DEFENDER (Option-A standoff arm)\n"
        "    - IFACE_TEMPLE_CHEEK\n"
        "    - IFACE_TEMPLE_SIDEHELM_POD\n"
        "  fasteners (per plate):\n"
        "    - 3x M3 heatset (yoke cluster)\n"
        "    - 2x M2 heatset (pylon foot)\n"
        "    - 1x M3 heatset (sidehelm dovetail thumbscrew)\n"
        "    - 2x 3mm steel pin (FwdBand + RearBand hinges)\n"
        "    - 2x 2mm steel pin (Defender pitch + yaw, hosted in cradle subpart)\n"
        "  key_feature_locations_plate_local_mm:\n"
        f"    yoke_centroid:   {IFACE_YOKE_TEMPLE.centroid_local_mm}\n"
        f"    fwdband_axis:    {IFACE_TEMPLE_FWDBAND.axis_local_mm}\n"
        f"    rearband_axis:   {IFACE_TEMPLE_REARBAND.axis_local_mm}\n"
        f"    pylon_axis:      {IFACE_TEMPLE_PYLON.axis_local_mm}\n"
        f"    defender_pin:    {IFACE_TEMPLE_DEFENDER.pin_local_mm}\n"
        f"    cheek_hook:      {IFACE_TEMPLE_CHEEK.hook_local_mm}\n"
    )
    print(f"Wrote sidecar {side_path}")


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)

    reset_scene()
    plate = build_plate_body()
    add_yoke_cluster(plate)
    add_visor_band_hinges(plate)
    add_pylon_foot(plate)
    add_defender_standoff_and_cradle(plate)
    add_cheek_hook(plate)
    add_sidehelm_dovetail(plate)
    export_stl(plate, args.out)
    write_sidecar(plate, args.out)

    print("---- Temple Plate interfaces consumed ----")
    for nm, axis in (
        ("YOKE_TEMPLE.centroid", IFACE_YOKE_TEMPLE.centroid_local_mm),
        ("FWDBAND.axis", IFACE_TEMPLE_FWDBAND.axis_local_mm),
        ("REARBAND.axis", IFACE_TEMPLE_REARBAND.axis_local_mm),
        ("PYLON.axis", IFACE_TEMPLE_PYLON.axis_local_mm),
        ("DEFENDER.pin", IFACE_TEMPLE_DEFENDER.pin_local_mm),
        ("DEFENDER.standoff_root", IFACE_TEMPLE_DEFENDER.standoff_root_local_mm),
        ("CHEEK.hook", IFACE_TEMPLE_CHEEK.hook_local_mm),
    ):
        print(f"  {nm:30s} = {axis}")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
