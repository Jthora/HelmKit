"""
canon.py -- single source of truth for the HelmKit vp0 (visual prototype 0)
part set. Every build_*.py in this directory imports from here.

vp0 is the "look the part" set: headphone-style hard bands, two 122.1 mm
semi-parabolic side dishes, a brow plate with a placeholder projector bay,
serrated fold joints at the sides. It is NOT the Mk0.5-beta topology
(tools/blender/*.py, interfaces.py) and consumes none of its interfaces.

Assembly frame ("world"):
    origin  = midpoint between the two ear canals
    +X      = forward (toward the brow)
    +Y      = wearer's LEFT
    +Z      = up
Left-side parts are built at +Y; right side is a mirror across the XZ plane.
Units: mm, degrees, grams.

Wearer measurements (2026-09-04, J. Trana) and the estimates derived from
them are in `HEAD`. Change a number here, regenerate everything.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Wearer
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Head:
    # --- measured ---
    circumference_mm: float = 580.0         # tape over brow + occiput
    ear_to_ear_over_crown_mm: float = 330.0 # from ear-top attachment, over the vertex
    canal_to_crown_arc_mm: float = 200.0    # tape from ear canal over the vertex
    # --- estimated from the above (revise after first fit) ---
    length_mm: float = 200.0     # glabella -> back of skull (circ 580 * ~0.345)
    width_mm: float = 156.0      # max breadth, just above the ears
    vertex_z_mm: float = 135.0   # straight-line ear canal -> vertex
    brow_z_mm: float = 40.0      # eyebrow line above the ear canal
    inion_z_mm: float = 5.0      # external occipital protuberance ("the lump")
    nape_z_mm: float = -35.0     # occipital hollow under the inion; retention target

    # Phantom ellipsoid used for renders + clearance checks.
    # Centre is above the canal because the skull is widest above the ears.
    @property
    def phantom_center_z(self) -> float:
        return 25.0

    @property
    def phantom_semi(self) -> tuple[float, float, float]:
        return (self.length_mm / 2.0, self.width_mm / 2.0,
                self.vertex_z_mm - self.phantom_center_z)

    def half_width_at(self, x: float, z: float) -> float:
        """Half-width of the phantom at (x, z); 0 if outside."""
        a, b, c = self.phantom_semi
        s = 1.0 - (x / a) ** 2 - ((z - self.phantom_center_z) / c) ** 2
        return b * math.sqrt(s) if s > 0 else 0.0


HEAD = Head()


# ---------------------------------------------------------------------------
# Fasteners / print constants
# ---------------------------------------------------------------------------

M5_CLEAR_DIA = 5.4          # pivot bolt clearance (ISO 273 medium)
M5_HEAD_DIA = 8.5           # socket-head cap, ISO 4762
M5_HEAD_H = 5.0
M5_NUT_AF = 8.0             # DIN 934 across flats
M5_NUT_T = 4.0
M3_CLEAR_DIA = 3.4
M3_BUTTON_HEAD_DIA = 5.7
M3_HEATSET_HOLE_DIA = 4.3   # for a 5.0 mm OD brass insert (same insert as interfaces.py)
M3_HEATSET_DEPTH = 7.0
FIT_CLEAR = 0.15            # per-side slip-fit clearance for PETG on the X-MAX3
PETG_DENSITY_G_CM3 = 1.27


# ---------------------------------------------------------------------------
# Side dish + cap ("the disks")
# ---------------------------------------------------------------------------

DISH_OD = 122.1             # user spec: 12.21 cm (~ lambda at 2.45 GHz)
DISH_DEPTH = 16.0           # paraboloid sag from rim to vertex (ear clearance)
DISH_WALL = 3.0
SKIRT_WALL = 2.5
SKIRT_RABBET_WALL = 1.25    # skirt thins to this where the cap seats
CAP_T = 3.5
CAVITY_H = 6.0              # electronics gap between cap inner face and dish vertex
CUSHION_T = 12.0            # compressed foam ear ring
LIP_H = 2.0                 # cushion-locating lip at the rim OD
LIP_W = 1.55
VENT_DIA = 4.0              # hole at the dish vertex (avoids a degenerate apex, doubles as cable pass)

DISH_R = DISH_OD / 2.0                      # 61.05
SKIRT_IN_R = DISH_R - SKIRT_WALL            # 58.55  (bowl rim radius)
RABBET_IN_R = DISH_R - SKIRT_RABBET_WALL    # 59.80
CAP_R = RABBET_IN_R - FIT_CLEAR             # 59.65
DISH_FOCAL = SKIRT_IN_R ** 2 / (4.0 * DISH_DEPTH)   # 53.6 mm (f/D 0.44)

# Dish local axial coordinate n: 0 at the skirt end (cap outer face),
# increasing toward the head.
N_CAP_INNER = CAP_T                          # 3.5
N_VERTEX_UNDER = N_CAP_INNER + CAVITY_H      # 9.5
N_VERTEX = N_VERTEX_UNDER + DISH_WALL        # 12.5
N_RIM = N_VERTEX + DISH_DEPTH                # 28.5  (skirt height)
N_LIP_TOP = N_RIM + LIP_H                    # 30.5

# Hub (integral to cap, on its outer face)
HUB_BOSS_D = 40.0
HUB_BOSS_H = 6.0
M5_HEAD_POCKET_DIA = M5_HEAD_DIA + 0.7
M5_HEAD_POCKET_DEPTH = M5_HEAD_H + 0.5

# Cosmetic
CAP_GROOVE_W = 3.0
CAP_GROOVE_D = 1.0
CAP_GROOVE_R0 = 24.0
CAP_GROOVE_R1 = 54.0
CAP_GROOVE_ANGLES = (45.0, 135.0, 225.0, 315.0)
CAP_RING_GROOVE = (56.5, 58.0)               # r_in, r_out
CAP_SCREW_R = 52.0
CAP_SCREW_ANGLES = tuple(30.0 + 60.0 * k for k in range(6))
CAP_SCREW_CBORE_DIA = 6.5
CAP_SCREW_CBORE_D = 2.0
BOSS_D = 8.0
BOSS_H = 8.0

# ---------------------------------------------------------------------------
# Pivot stack (per side, Y distances from the mid-sagittal plane)
# ---------------------------------------------------------------------------

SERR_TEETH = 24             # 15 deg detents
SERR_H = 1.2                # tooth height; meshed rings sit this far apart
SERR_R_IN = 8.0
SERR_R_OUT = 12.5
SERR_OVERLAP = 0.6          # how far the serration solid sinks into its host (boolean robustness)
RING_T = 6.2                # ring thickness; bands are 6.0 so no ring/band face is coplanar (EXACT-solver hygiene)

RIM_Y = HEAD.width_mm / 2.0 + CUSHION_T          # 90.0   cushion face / dish rim
CAP_OUT_Y = RIM_Y + N_RIM                        # 118.5  cap outer face == skirt end
CAP_IN_Y = CAP_OUT_Y - CAP_T                     # 115.0
HUB_TOP_Y = CAP_OUT_Y + HUB_BOSS_H               # 124.5  serrated

# Stack order from the cap outward. Crown ring is OUTERMOST so the arms
# that fold (rear band, brow plate) swing inside the crown arch.
REAR_RING_Y = HUB_TOP_Y + SERR_H + RING_T / 2.0          # 128.7
BROW_RING_Y = REAR_RING_Y + RING_T + SERR_H              # 135.9
CROWN_RING_Y = BROW_RING_Y + RING_T + SERR_H             # 143.1
NUT_FACE_Y = CROWN_RING_Y + RING_T / 2.0                 # 146.1  (crown ring outer face is flat)

# Ring radii sit 0.2 inside their band's envelope: no tangent faces for the
# solver, and inverted/side prints rest on the band's flat edge, not the ring.
REAR_RING_R = 12.3
BROW_RING_R = 12.3
CROWN_RING_R = 14.8
BROW_STEM_W = 24.0

# ---------------------------------------------------------------------------
# Crown band (fixed arch, headphone style)
# ---------------------------------------------------------------------------

CROWN_W = 30.0              # fore-aft width (== crown ring diameter)
CROWN_T = 6.0
CROWN_CLEAR = 12.0          # inner face over the vertex
CROWN_APEX_Z = HEAD.vertex_z_mm + CROWN_CLEAR + CROWN_T / 2.0   # 150 centreline
CROWN_SUPER_N = 2.6         # superellipse exponent (2 = ellipse; >2 = squarer)

# ---------------------------------------------------------------------------
# Rear band (folds; hooks under the inion)
# ---------------------------------------------------------------------------

REAR_H = 25.0               # band height at the arms (== ring diameter)
REAR_T = 6.0
REAR_TOP_Z = REAR_H / 2.0   # constant top edge -> prints inverted with no supports
REAR_BOT_Z = -REAR_H / 2.0
REAR_DIP_Z = HEAD.nape_z_mm # bottom edge at the back centre
REAR_CLEAR = 8.0            # to the phantom at the back centre (foam pad takes it up)
# (x, y, z_bottom) waypoints for the LEFT half, ring -> back centre.
# Kept outboard of the cap disc (r<59.65 at y=118.5) and the hub boss.
REAR_WAYPOINTS = (
    (0.0,    REAR_RING_Y, REAR_BOT_Z),
    (-22.0,  125.5,       REAR_BOT_Z),
    (-45.0,  122.5,       REAR_BOT_Z),
    (-63.0,  120.0,       REAR_BOT_Z),
    (-85.0,  92.0,        -18.0),
    (-100.0, 55.0,        -30.0),
    (-110.0, 20.0,        REAR_DIP_Z),
    (-111.0, 0.0,         REAR_DIP_Z),
)

# ---------------------------------------------------------------------------
# Brow plate (folds; projector bay placeholder)
# ---------------------------------------------------------------------------

BROW_PLATE_Z0 = HEAD.brow_z_mm          # 40  bottom edge
BROW_PLATE_Z1 = 90.0                    # top edge (constant across arms + plate)
BROW_PLATE_T = 14.0
BROW_PLATE_CLEAR = 10.0
BROW_ARM_Z0 = 72.0                      # arm bottom edge (18 mm strap; keeps the plate reading as a plate)
BROW_ARM_T = 6.0
BROW_PLATE_HALF_Y = 70.0                # plate spans +/- this at its inner face
# Inner-face ellipse of the plate, sized where the head is widest under the
# plate (near its bottom edge) so the whole plate clears by >= BROW_PLATE_CLEAR.
BROW_MID_Z = BROW_PLATE_Z0 + 4.0
BROW_ELL_A = HEAD.phantom_semi[0] * math.sqrt(
    max(0.0, 1.0 - ((BROW_MID_Z - HEAD.phantom_center_z) / HEAD.phantom_semi[2]) ** 2)) + BROW_PLATE_CLEAR
BROW_ELL_B = HEAD.phantom_semi[1] * math.sqrt(
    max(0.0, 1.0 - ((BROW_MID_Z - HEAD.phantom_center_z) / HEAD.phantom_semi[2]) ** 2)) + BROW_PLATE_CLEAR
# (x, y, thickness) arm waypoints, LEFT side, ring -> plate end
BROW_ARM_WAYPOINTS = (
    (0.0,  BROW_RING_Y, BROW_ARM_T),
    (24.0, 134.0,       BROW_ARM_T),
    (46.0, 124.0,       BROW_ARM_T),
    (58.0, 104.0,       8.0),
    (63.0, 88.0,        11.0),
)
BROW_BAY_HALF_Y = 35.0
BROW_BAY_Z = (50.0, 80.0)
BROW_BAY_FRONT_WALL = 2.5
BROW_WINDOW_HALF_Y = 20.0
BROW_WINDOW_Z = (60.0, 70.0)

# ---------------------------------------------------------------------------
# Thumb-nut
# ---------------------------------------------------------------------------

NUT_KNOB_D = 30.0
NUT_KNOB_H = 14.0
NUT_POCKET_DEPTH = M5_NUT_T + 0.5
NUT_SCALLOPS = 12
NUT_SCALLOP_D = 5.0
NUT_BORE = 5.6

# Bolt: head pocket floor at CAP_IN_Y + pocket depth; nut top at NUT_FACE_Y + knob height
BOLT_GRIP_MM = (NUT_FACE_Y + NUT_KNOB_H) - (CAP_IN_Y + M5_HEAD_POCKET_DEPTH)   # ~39.6 -> M5x40 or 45


def report() -> str:
    lines = [
        "vp0 canon",
        f"  head: circ {HEAD.circumference_mm} | width {HEAD.width_mm} | length {HEAD.length_mm} | vertex z {HEAD.vertex_z_mm}",
        f"  dish: OD {DISH_OD} | depth {DISH_DEPTH} | focal {DISH_FOCAL:.1f} (f/D {DISH_FOCAL/DISH_OD:.2f}) | skirt h {N_RIM}",
        f"  cap: R {CAP_R:.2f} (rabbet ID {2*RABBET_IN_R:.1f})",
        f"  Y stack (left): rim {RIM_Y} | cap out {CAP_OUT_Y} | hub top {HUB_TOP_Y} | rear ring {REAR_RING_Y} | brow ring {BROW_RING_Y} | crown ring {CROWN_RING_Y} | nut face {NUT_FACE_Y}",
        f"  overall width incl. knobs: {2*(NUT_FACE_Y+NUT_KNOB_H):.0f} mm",
        f"  crown apex centreline z {CROWN_APEX_Z}",
        f"  brow inner ellipse a={BROW_ELL_A:.1f} b={BROW_ELL_B:.1f} at z={BROW_MID_Z}",
        f"  pivot bolt grip {BOLT_GRIP_MM:.1f} mm -> M5x45 socket head",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
