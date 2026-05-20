"""
interfaces.py — single source of truth for HelmKit Mk0.5-β joint geometry.

Mirrors docs/mechanical/mk0.5_topology_beta_architecture.md §12
"Interface contracts (the eight joints) — FROZEN". Every parametric
generator under tools/blender/build_*.py MUST import its joint
dimensions from this module rather than re-typing numbers from the
doc. Changing a number here is the ONLY supported way to revise an
interface, and forces regeneration of every part on both sides of
the joint.

Datum convention (per §12 prose):
    +X = forward (toward brow)
    +Y = up      (toward crown)
    +Z = outward (away from head)

Each Temple Plate has its own local frame with origin at the plate
centroid on the outer face. L and R sides are mirror images about
the head's sagittal plane.

NOTE on axis convention vs envelope scripts (Phase 3):
    The throwaway envelope_*.py scripts use a rotated convention
    (+X=fore-aft, +Y=outboard, +Z=up). Their visual conclusions
    are still valid (all features were rotated consistently) but
    their hard-coded coordinates are NOT canon. interfaces.py
    below uses the doc convention. Generators must follow this
    module, not the envelope scripts.

Units: all linear dims in mm, angles in degrees, masses in grams,
loads in newtons.

Run `python tools/blender/interfaces.py` for a self-check + report.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# ---------------------------------------------------------------------------
# Common fastener constants (M-series, ISO 4762 / DIN 7984 socket-head)
# ---------------------------------------------------------------------------

M2_CLEAR_DIA_MM = 2.4       # close clearance, ISO 273 medium
M3_CLEAR_DIA_MM = 3.4       # close clearance
M3_HEATSET_OD_MM = 5.0      # OD of the M3×5 mm brass heat-set insert body
M3_HEATSET_LEN_MM = 5.0
M2_HEATSET_OD_MM = 3.6      # OD of the M2×4 mm brass heat-set insert body
M2_HEATSET_LEN_MM = 4.0


# ---------------------------------------------------------------------------
# IFACE_YOKE_TEMPLE (Top Yoke arch end ↔ Temple Plate upper edge)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class YokeTempleIface:
    bolt_count: int = 3
    bolt_size: str = "M3"
    pattern: str = "equilateral_triangle"
    pattern_side_mm: float = 12.0
    # Triangle centroid in Temple Plate local frame
    centroid_local_mm: Tuple[float, float, float] = (0.0, 18.0, 0.0)
    bolt_hole_dia_mm: float = M3_CLEAR_DIA_MM
    insert: str = "M3x5_brass_heatset"
    insert_od_mm: float = M3_HEATSET_OD_MM
    insert_depth_mm: float = M3_HEATSET_LEN_MM
    # Mate face normals
    plate_mate_normal: str = "+Y"
    yoke_mate_normal: str = "-Y"
    boss_min_thickness_mm: float = 6.0  # PETG around insert OD
    design_load_N: float = 600.0


IFACE_YOKE_TEMPLE = YokeTempleIface()


# ---------------------------------------------------------------------------
# IFACE_TEMPLE_FWDBAND (Temple Plate L/R ↔ Forward Visor-Band)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TempleVisorBandIface:
    """Generic hinge contract for FwdBand and RearBand (params differ)."""
    pin_dia_mm: float = 3.0
    pin_length_mm: float = 25.0
    pin_material: str = "steel_music_wire"
    # Hinge axis location in Temple Plate local frame
    # (axis is horizontal ear-to-ear, i.e. along world Z)
    axis_local_mm: Tuple[float, float, float] = (8.0, -6.0, 0.0)
    detent_angles_deg: Tuple[float, ...] = (0.0, 30.0, 45.0, 60.0, 90.0)
    detent_mechanism: str = "TPU95A_click_leaf"
    detent_leaf_fastener: str = "M3x6_into_heatset"
    cable_service_loop_mm: float = 25.0
    # Acceptance: detent click holding torque
    detent_holding_torque_Nmm: float = 250.0


IFACE_TEMPLE_FWDBAND = TempleVisorBandIface(
    axis_local_mm=(8.0, -6.0, 0.0),   # +8 fwd, -6 down
)

IFACE_TEMPLE_REARBAND = TempleVisorBandIface(
    axis_local_mm=(-8.0, -6.0, 0.0),  # -8 aft (mirror), -6 down
)


# ---------------------------------------------------------------------------
# IFACE_TEMPLE_PYLON (Temple Plate L/R ↔ Pylon)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TemplePylonIface:
    hinge_type: str = "TPU95A_live_hinge"
    foot_footprint_mm: Tuple[float, float] = (8.0, 12.0)  # (X span, Y span)
    foot_thickness_mm: float = 3.0
    foot_fastener: str = "M2x6_into_M2_heatset"
    foot_fastener_count: int = 2
    # Hinge axis location in Temple Plate local frame:
    # axis is horizontal fore-aft (along world X), at (-5, +10, +4)
    # (5 aft, 10 up, 4 outboard).
    axis_local_mm: Tuple[float, float, float] = (-5.0, 10.0, 4.0)
    fold_direction: str = "backward"
    detent_count: int = 3
    detent_angles_deg: Tuple[float, ...] = (0.0, 45.0, 90.0)
    detent_mechanism: str = "integral_TPU_notches"
    # Fold-flat envelope (clearance budget when fully folded)
    foldflat_max_aft_mm: float = 75.0
    foldflat_max_outboard_mm: float = 15.0
    rf_feed: str = "RG-178_coax"
    rf_service_loop_mm: float = 40.0
    fold_release_threshold_N: float = 30.0


IFACE_TEMPLE_PYLON = TemplePylonIface()


# ---------------------------------------------------------------------------
# IFACE_TEMPLE_DEFENDER (Temple Plate L/R ↔ Defender cradle)
# Updated 2026-05-20 (Phase-3 Option A): standoff arm to clear plate cluster.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TempleDefenderIface:
    gimbal: str = "2_axis_pitch_outer_yaw_inner"
    pitch_pin_dia_mm: float = 2.0
    pitch_pin_length_mm: float = 12.0
    yaw_pin_dia_mm: float = 2.0
    yaw_pin_length_mm: float = 12.0
    pin_material: str = "steel_music_wire"
    # Pitch pin location in Temple Plate local frame.
    # Updated Phase 3: relocated from (0, 0, 6) to (+15, +10, +10) and
    # carried on a standoff arm to clear yoke bolts, pylon foot, and both
    # visor-band hinge bosses.
    pin_local_mm: Tuple[float, float, float] = (15.0, 10.0, 10.0)
    # Standoff arm geometry (cantilever from Temple Plate face to pitch pin)
    standoff_root_local_mm: Tuple[float, float, float] = (5.0, 8.0, 0.0)
    standoff_tip_local_mm: Tuple[float, float, float] = (15.0, 10.0, 10.0)
    standoff_section_mm: Tuple[float, float] = (8.0, 6.0)  # (X x Y cross-sec)
    standoff_material: str = "PETG_integral_to_temple_plate"
    # Aim lock
    aim_lock: str = "M2x4_setscrew_into_M2_heatset_in_pitch_yoke"
    aim_range_pitch_deg: Tuple[float, float] = (-15.0, 15.0)
    aim_range_yaw_deg: Tuple[float, float] = (-15.0, 15.0)
    # Cradle envelope (caduceus coil housing)
    cradle_envelope_mm: Tuple[float, float, float] = (25.0, 25.0, 20.0)
    coil_exit_window_dia_mm: float = 14.0
    # Notes:
    #  - "outward" direction (Z+) carries the coil exit window toward the
    #    head's T-T line; collinear L+R coil alignment is the operating
    #    requirement, not beam pointing.


IFACE_TEMPLE_DEFENDER = TempleDefenderIface()


# ---------------------------------------------------------------------------
# IFACE_TEMPLE_CHEEK (Temple Plate L/R ↔ Chin-yoke webbing)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TempleCheekIface:
    hook_count_per_side: int = 1
    hook_local_mm: Tuple[float, float, float] = (-15.0, -20.0, 0.0)
    webbing_slot_w_mm: float = 26.0   # fits 25 mm webbing
    webbing_slot_h_mm: float = 4.0
    anti_pullout_rib_h_mm: float = 3.0
    anti_pullout_rib_face: str = "inboard"
    load_case_N: float = 150.0
    load_case_angle_below_horizontal_deg: float = 30.0
    load_direction_local: str = "+X (forward) and -Y (down)"


IFACE_TEMPLE_CHEEK = TempleCheekIface()


# ---------------------------------------------------------------------------
# IFACE_BAND_STABILIZER (Visor-Band ↔ Stabilizer panel pocket)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BandStabilizerIface:
    pocket_internal_mm: Tuple[float, float, float] = (64.0, 34.0, 4.0)
    holds: str = "2x_bifilar_PCB_30x30mm_side_by_side"
    pcb_max_thickness_mm: float = 3.2
    pcb_gap_mm: float = 2.0
    retention: str = "2x_M3x6_into_M3_heatset"
    retention_count: int = 2
    cable_exit_face: str = "inboard"
    cable_exit_grommet_dia_mm: float = 4.0
    cover_plate: str = "snap_fit_PETG_accent_white"
    pocket_placement_fwdband: str = "front_center"
    pocket_placement_rearband: str = "back_center"


IFACE_BAND_STABILIZER = BandStabilizerIface()


# ---------------------------------------------------------------------------
# IFACE_BAND_SUBRAIL (Forward Visor-Band lower edge ↔ sensor pods)
# Picatinny canon — carried forward from ring-frame doc §3, unchanged.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BandSubrailIface:
    rail_standard: str = "MIL-STD-1913_Picatinny"
    # Picatinny canonical dims (mm) — verbatim
    tooth_w_mm: float = 5.0
    slot_w_mm: float = 5.55
    pitch_mm: float = 10.55
    top_w_mm: float = 10.2
    bottom_w_mm: float = 19.0
    depth_mm: float = 3.4
    shoulder_angle_deg: float = 45.0
    rail_position: str = "lower_edge_fwdband_outer_face"
    rail_arc_coverage_deg: float = 180.0  # forward arc across the brow
    # Preserved station angles
    station_HP_FL_deg: float = -30.0
    station_HP_FR_deg: float = 30.0
    cable_raceway_face: str = "inboard"


IFACE_BAND_SUBRAIL = BandSubrailIface()


# ---------------------------------------------------------------------------
# IFACE_TEMPLE_SIDEHELM_POD (Temple Plate L/R lower-aft face ↔ sidehelm pod)
# Added 2026-05-20 for compute + battery split.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TempleSidehelmPodIface:
    mount_location_local: str = "lower_aft_face_below_cheek_hook"
    mount_geometry: str = "sliding_dovetail"  # NOT Picatinny
    dovetail_top_w_mm: float = 12.0
    dovetail_bottom_w_mm: float = 18.0
    dovetail_depth_mm: float = 3.4
    dovetail_length_mm: float = 35.0
    adjust_travel_mm: float = 20.0
    lock: str = "M3_thumbscrew_into_M3_heatset"
    pod_envelope_mm: Tuple[float, float, float] = (70.0, 50.0, 40.0)  # L x H x D
    cable_exit: str = "top_into_temple_plate_inboard_cable_hub"
    hp_sl_load_g: float = 110.0  # battery pod loaded mass
    hp_sr_load_g: float = 45.0   # compute pod loaded mass
    lr_imbalance_budget_g: float = 65.0


IFACE_TEMPLE_SIDEHELM_POD = TempleSidehelmPodIface()


# ---------------------------------------------------------------------------
# Registry — convenient iteration for self-check / docs / dispatchers
# ---------------------------------------------------------------------------

ALL_INTERFACES = {
    "IFACE_YOKE_TEMPLE":         IFACE_YOKE_TEMPLE,
    "IFACE_TEMPLE_FWDBAND":      IFACE_TEMPLE_FWDBAND,
    "IFACE_TEMPLE_REARBAND":     IFACE_TEMPLE_REARBAND,
    "IFACE_TEMPLE_PYLON":        IFACE_TEMPLE_PYLON,
    "IFACE_TEMPLE_DEFENDER":     IFACE_TEMPLE_DEFENDER,
    "IFACE_TEMPLE_CHEEK":        IFACE_TEMPLE_CHEEK,
    "IFACE_BAND_STABILIZER":     IFACE_BAND_STABILIZER,
    "IFACE_BAND_SUBRAIL":        IFACE_BAND_SUBRAIL,
    "IFACE_TEMPLE_SIDEHELM_POD": IFACE_TEMPLE_SIDEHELM_POD,
}


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """Assert basic sanity invariants. Raises on failure."""
    # Picatinny canon must not drift
    p = IFACE_BAND_SUBRAIL
    assert p.tooth_w_mm == 5.0,    "Picatinny tooth_w drifted!"
    assert p.slot_w_mm == 5.55,    "Picatinny slot_w drifted!"
    assert p.pitch_mm == 10.55,    "Picatinny pitch drifted!"

    # FwdBand and RearBand axes must mirror in X
    fx = IFACE_TEMPLE_FWDBAND.axis_local_mm[0]
    rx = IFACE_TEMPLE_REARBAND.axis_local_mm[0]
    assert fx == -rx, f"Band axes do not mirror: fwd={fx}, rear={rx}"

    # Defender Phase-3 remediation must hold
    d = IFACE_TEMPLE_DEFENDER
    assert d.pin_local_mm == (15.0, 10.0, 10.0), \
        "Defender pin reverted from Phase-3 Option A position!"
    assert d.standoff_tip_local_mm == d.pin_local_mm, \
        "Standoff arm tip must coincide with pitch pin"

    # Pylon fold direction sanity
    assert IFACE_TEMPLE_PYLON.fold_direction == "backward"

    # Sidehelm balance budget
    s = IFACE_TEMPLE_SIDEHELM_POD
    assert abs(s.hp_sl_load_g - s.hp_sr_load_g) <= s.lr_imbalance_budget_g, \
        "Sidehelm L/R load imbalance exceeds budget"


def _report() -> None:
    print("HelmKit Mk0.5-β interface contracts (§12 frozen):\n")
    for name, iface in ALL_INTERFACES.items():
        print(f"  {name}: {type(iface).__name__}")
    print(f"\n  {len(ALL_INTERFACES)} contracts, all loaded.\n")
    print("Datum convention: +X fwd, +Y up, +Z outward (Temple Plate local).")


if __name__ == "__main__":
    _self_check()
    _report()
    print("OK")
