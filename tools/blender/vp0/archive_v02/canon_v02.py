"""
canon.py -- single source of truth for the HelmKit vp0.2 part set.

vp0.2 (2026-09-04): brain-core-centred thin pods with a face-down cup and a
glued reflector insert, bolt-on hub bracket, standard 10 mm port sockets for
modular add-ons, flat rectangular brow panel with an LED bay, separate brow
arms, split crown arch with an apex slider, tilted rear band with a
rack-and-pinion nape ratchet and battery bay, cheek hooks / strap anchors as
port add-ons.

Assembly frame ("world"):
    origin  = midpoint between the two ear canals (Frankfort plane)
    +X      = forward (toward the brow)
    +Y      = wearer's LEFT
    +Z      = up
Left-side parts are built at +Y; right side is a mirror across the XZ plane.
Units: mm, degrees, grams.

Run `python3 canon.py` for a summary.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Wearer (measured 2026-09-04)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Head:
    circumference_mm: float = 580.0
    width_mm: float = 155.0          # straight-line, above the ears (measured)
    length_mm: float = 202.5         # glabella -> opisthocranion (measured)
    ear_to_ear_over_crown_mm: float = 330.0
    canal_to_crown_arc_mm: float = 200.0
    vertex_z_mm: float = 135.0       # est. straight-line ear canal -> vertex
    brow_z_mm: float = 40.0          # eyebrow line
    hairline_z_mm: float = 95.0      # est.
    inion_z_mm: float = 5.0          # external occipital protuberance
    nape_z_mm: float = -35.0         # occipital hollow (retention hook target)
    zygomatic_z_mm: float = -5.0     # cheekbone arch, just below the canal
    bizygomatic_mm: float = 140.0    # cheekbone-to-cheekbone (est.)
    plan_exp: float = 2.45           # superellipse exponent in plan; >2 fattens temples/occiput
    phantom_center_z: float = 25.0

    @property
    def phantom_semi(self) -> tuple[float, float, float]:
        return (self.length_mm / 2.0, self.width_mm / 2.0, self.vertex_z_mm - self.phantom_center_z)

    def implicit(self, x: float, y: float, z: float) -> float:
        """Superellipsoid F(p): F<1 inside, F=1 on the surface. Homogeneous of degree 2."""
        a, b, c = self.phantom_semi
        n = self.plan_exp
        plan = (abs(x / a) ** n + abs(y / b) ** n) ** (2.0 / n)
        return plan + ((z - self.phantom_center_z) / c) ** 2

    def plan_perimeter(self) -> float:
        a, b, n = self.length_mm / 2.0, self.width_mm / 2.0, self.plan_exp
        pts = []
        for i in range(721):
            t = 2 * math.pi * i / 720
            c, s = math.cos(t), math.sin(t)
            pts.append((a * math.copysign(abs(c) ** (2 / n), c), b * math.copysign(abs(s) ** (2 / n), s)))
        return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(720))


HEAD = Head()

# The pod axis passes through here (brain-core centring), perpendicular to the
# sagittal plane. Roughly the centroid of the cerebrum: a little forward of and
# well above the ear canals.
BRAIN_CORE = (10.0, 0.0, 35.0)
CX, CZ = BRAIN_CORE[0], BRAIN_CORE[2]

# ---------------------------------------------------------------------------
# Fasteners / print constants
# ---------------------------------------------------------------------------

M5_CLEAR_DIA = 5.4
M5_HEAD_DIA = 8.5
M5_HEAD_H = 5.0
M5_NUT_AF = 8.0
M5_NUT_T = 4.0
M4_CLEAR_DIA = 4.4
M4_HEAD_DIA = 7.0
M4_NUT_AF = 7.0
M4_NUT_T = 3.2
M3_CLEAR_DIA = 3.4
M3_TAP_DIA = 2.5            # thread-forming M3 straight into PETG (low-load lids only)
M3_NUT_AF = 5.5
M3_NUT_T = 2.4
M3_HEATSET_HOLE_DIA = 4.3   # 5.0 OD brass insert
M3_HEATSET_DEPTH = 6.0
M3_BOSS_OD = 10.5           # >= 2x insert OD
M2_TAP_DIA = 1.7            # fan screws
FIT_CLEAR = 0.15
PETG_DENSITY_G_CM3 = 1.27

# ---------------------------------------------------------------------------
# Pod: face-down cup + glued reflector insert + bolt-on hub bracket
# ---------------------------------------------------------------------------

DISH_OD = 122.1
DISH_R = DISH_OD / 2.0                  # 61.05
SKIRT_WALL = 2.5
CUP_FLOOR_T = 2.5
REFL_SAG = 8.0                          # paraboloid sag (cosmetic for now)
REFL_T = 2.0
REFL_LIP_H = 0.5                        # skirt rim stands this proud of the reflector
LEDGE_STEP = 1.0                        # skirt thins by this to make the reflector seat
CUSHION_T = 15.0                        # compressed foam ring (gives the ear its room)
CAVITY_MIN = 7.5                        # floor inner face -> reflector underside at the vertex
SKIRT_IN_R = DISH_R - SKIRT_WALL        # 58.55
REFL_R = SKIRT_IN_R + LEDGE_STEP - FIT_CLEAR    # 59.40: seats in the ledge (ID 59.55)
VENT_DIA = 4.0
REFL_PERF = True                        # ring of airflow holes near the reflector rim
REFL_PERF_N = 30
REFL_PERF_R = 40.0                      # inside the cushion ID
REFL_PERF_D = 3.0

# Pod local axial coordinate n: 0 at the cup OUTER face, increasing toward the head.
N_FLOOR_IN = CUP_FLOOR_T                                # 2.5
N_REFL_UNDER = N_FLOOR_IN + CAVITY_MIN                  # 10.0  reflector underside at vertex
N_REFL_VERTEX = N_REFL_UNDER + REFL_T                   # 12.0
N_REFL_RIM = N_REFL_VERTEX + REFL_SAG                   # 20.0  reflector top at its rim
N_LEDGE = N_REFL_RIM - REFL_T                           # 18.0  ledge the reflector rim sits on
N_SKIRT_TOP = N_REFL_RIM + REFL_LIP_H                   # 20.5  skirt height
REFL_FOCAL = SKIRT_IN_R ** 2 / (4.0 * REFL_SAG)         # ~107 mm (f/D 0.88)

RIM_Y = HEAD.width_mm / 2.0 + CUSHION_T                 # 92.5
CUP_FACE_Y = RIM_Y + N_SKIRT_TOP                        # 113.0  cup outer face

# Cosmetic grooves on the cup face (echo of the segmented red disc)
CAP_GROOVE_W = 3.0
CAP_GROOVE_D = 0.8
CAP_GROOVE_R0 = 26.0
CAP_GROOVE_R1 = 50.0
CAP_GROOVE_ANGLES = (45.0, 135.0, 225.0, 315.0)
CAP_RING_GROOVE = (53.0, 54.5)

# Hub bracket (bolts to the cup face from inside the cup; carries the pivot)
HUB_BRACKET_D = 44.0
HUB_DISC_T = 5.0                        # heat-set depth lives here
HUB_BOSS_D = 26.0
HUB_BOSS_H = 3.0
HUB_T = HUB_DISC_T + HUB_BOSS_H         # 8.0 total protrusion from the cup face
HUB_BOLT_R = 17.0
HUB_BOLT_ANGLES = (90.0, 210.0, 330.0)
HUB_NUT_POCKET_DEPTH = M3_NUT_T + 0.3   # M3 nuts captured in the bracket top; bolts come from inside the cup
M5_HEAD_POCKET_DIA = M5_HEAD_DIA + 0.7
M5_HEAD_POCKET_DEPTH = M5_HEAD_H + 0.5  # from the bracket underside; leaves 2.5 mm ceiling
HUB_TOP_Y = CUP_FACE_Y + HUB_T          # 121.0  serrated

# Fan / cooling provisions inside the cup (placeholder for "tiny fans")
FAN_SIZE = 25.0
FAN_PITCH = 20.0
FAN_STANDOFF_H = 5.0
FAN_STANDOFF_D = 5.0
FAN_CENTER_R = 28.0                     # from the pod centre
FAN_CENTER_ANGLE = 200.0                # rear-lower quadrant
VENT_SLOTS = 8                          # skirt intake slots
VENT_SLOT_W = 3.0
VENT_SLOT_L = 10.0
VENT_ANGLE_0, VENT_ANGLE_1 = 150.0, 228.0
JACK_ANGLE, USB_ANGLE = 270.0, 285.0   # bottom of the pod; cable hangs down

# ---------------------------------------------------------------------------
# Port standard (modular add-on sockets)
# ---------------------------------------------------------------------------

PORT_SQ = 10.0                          # post side
PORT_CLEAR = 0.3                        # socket = 10.3
PORT_DEPTH = 15.0
PORT_BOSS = 16.0                        # socket boss outer square
PORT_BOSS_H = 18.0                      # boss height above the surface it stands on
PORT_XBOLT_DIA = M3_CLEAR_DIA           # cross-bolt through boss + post
PORT_XBOLT_DEPTH = 8.0                  # from the socket mouth
PORT_HDR_POCKET = (10.4, 2.8, 6.0)      # 4-pin 2.54 mm header pocket in the socket floor (W x T x depth)
PORT_PLUG_LEN = PORT_DEPTH - 0.5
PORT_PLUG_CHAMFER = 1.0
PORT_FLANGE = 16.0
PORT_FLANGE_T = 3.0
# Pod ports: angle in the pod's XZ plane, 0 = forward, 90 = up. Radial sockets.
POD_PORT_ANGLES = (45.0, 90.0, 135.0, 240.0, 300.0)
POD_PORT_NAMES = {45.0: "front-upper", 90.0: "top (crown arch)", 135.0: "rear-upper",
                  240.0: "rear-lower (pylons)", 300.0: "front-lower (cheek hook / strap)"}
PORT_BOSS_SINK = 1.0                    # boss sinks this far into its host for a robust union

# ---------------------------------------------------------------------------
# Pivot stack (per side, Y from the mid-sagittal plane), on the pod axis
# ---------------------------------------------------------------------------

SERR_TEETH = 24
SERR_H = 1.0
SERR_R_IN = 7.5
SERR_R_OUT = 12.0
SERR_OVERLAP = 0.6
RING_T = 5.2                            # rings; bands are BAND_T so faces never coincide
BAND_T = 5.0
REAR_RING_Y = HUB_TOP_Y + SERR_H + RING_T / 2.0          # 124.6
BROW_RING_Y = REAR_RING_Y + RING_T + SERR_H              # 130.8
NUT_FACE_Y = BROW_RING_Y + RING_T / 2.0                  # 133.4
REAR_RING_R = 12.3
BROW_RING_R = 12.3

# Thumb knob (low profile)
KNOB_D = 34.0
KNOB_H = 8.0
KNOB_POCKET_DEPTH = M5_NUT_T + 0.5
KNOB_SCALLOPS = 14
KNOB_SCALLOP_D = 5.0
KNOB_BORE = 5.6
BOLT_GRIP_MM = (NUT_FACE_Y + KNOB_H) - (CUP_FACE_Y + M5_HEAD_POCKET_DEPTH)   # ~23 -> M5x30

# ---------------------------------------------------------------------------
# Crown arch: two identical halves plugged into the pods' top ports, joined
# by a slotted/serrated overlap inside the apex block (width adjustment).
# ---------------------------------------------------------------------------

CROWN_W = 30.0
CROWN_T = BAND_T
CROWN_PAD_T = 12.0
CROWN_APEX_Z = HEAD.vertex_z_mm + CROWN_PAD_T + 2.0 + 2.0 + 0.2 + CROWN_T / 2.0     # 153.7 centreline (pad + sleeve floor + clearance)
POD_PORT_Y = CUP_FACE_Y - PORT_BOSS / 2.0             # 105.0  boss flush with the cup face (prints on the bed)
POD_TOP_PORT_Y = POD_PORT_Y
POD_TOP_PORT_TOP_Z = CZ + DISH_R + PORT_BOSS_H         # 114.05  boss top surface
CROWN_FOOT = (CROWN_W, 16.0, 18.0)      # X x Y x Z block with a downward port socket; a coupler joins it to the pod
CROWN_LEG_Z0 = POD_TOP_PORT_TOP_Z + CROWN_FOOT[2]      # 132.05  ribbon starts on top of the foot block
CROWN_SUPER_N = 2.6
CROWN_OVERLAP = 40.0                    # each half extends this far past the sagittal plane
CROWN_BAR_W = CROWN_W / 2.0             # overlap bars sit side by side in X
CROWN_SLOT_L = 26.0                     # adjustment +/- 13 mm span
CROWN_SLOT_W = M4_CLEAR_DIA
CROWN_SERR_PITCH = 2.0
CROWN_SERR_H = 0.6
APEX_SLEEVE = (40.0, 64.0, 10.4)        # X x Y x Z outer (2 mm floor, 3 mm roof)
APEX_FLOOR_T = 2.0
APEX_CHANNEL = (CROWN_W + 0.6, 2 * CROWN_T + 2 * CROWN_SERR_H + 0.4)   # X x Z inner

# ---------------------------------------------------------------------------
# Brow panel (flat, rectangular, LED bay) + separate arms
# ---------------------------------------------------------------------------

BROW_W = 160.0
BROW_H = 50.0
BROW_T = 12.0
BROW_WALL = 2.0
BROW_Z0 = HEAD.brow_z_mm + 2.0          # 42 bottom edge
BROW_Z1 = BROW_Z0 + BROW_H              # 92 top edge (covers to the hairline)
BROW_CLEAR = 10.0
BROW_LID_T = 2.0
BROW_LID_SCREWS = ((-70.0, BROW_Z0 + 8.0), (70.0, BROW_Z0 + 8.0), (-70.0, BROW_Z1 - 8.0), (70.0, BROW_Z1 - 8.0))
BROW_LED_WINDOW = (120.0, 6.0)          # slot in the bottom face (LED array shines down onto the face)
BROW_TILT = 13.0                        # panel + arms lean back by this (top further back), following the forehead
BROW_ARM_T = BAND_T
BROW_ARM_H = 25.0                       # constant height along the tilted "up" (== ring dia + margin)
BROW_TAB_Y = (58.0, 84.0)               # tab runs along the panel front face over this |y| range
# Panel-local frame: origin at the inner-bottom edge centre, x = outward normal, y = +Y, z = panel "up".
_ph, _c, _s = None, math.cos(math.radians(BROW_TILT)), math.sin(math.radians(BROW_TILT))
BROW_EX = (_c, 0.0, _s)
BROW_EZ = (-_s, 0.0, _c)
BROW_PORTS_Y = (-60.0, 60.0)            # top-edge sockets


def _forehead_x(z: float) -> float:
    a, _, c = HEAD.phantom_semi
    s = 1.0 - ((z - HEAD.phantom_center_z) / c) ** 2
    return a * math.sqrt(max(0.0, s))


BROW_X_IN = _forehead_x(BROW_Z0 + 6.0) + BROW_CLEAR      # inner-bottom edge x; the tilted face then tracks the forehead
BROW_X_OUT = BROW_X_IN + BROW_T * _c                     # outer face x at the bottom edge (for reference)
BROW_ORIGIN = (BROW_X_IN, 0.0, BROW_Z0)
# Arm centreline in XZ: the line through the hub with direction BROW_EX (perpendicular to the panel).
# Tab centreline sits BROW_ARM_T/2 outside the panel's outer face; its panel-local height follows.
BROW_ARM_ZL = (CX - BROW_X_IN) * (-_s) + (CZ - BROW_Z0) * _c      # panel-local z of the arm centreline (~15)
BROW_ARM_BOLTS = ((66.0, BROW_ARM_ZL - 6.5), (66.0, BROW_ARM_ZL + 6.5))   # (|y|, panel-local z) through the front wall

# ---------------------------------------------------------------------------
# Rear band: tilted plane (leans back to follow the occiput), constant height,
# splits at the nape into two racks driven by one pinion (hard-hat ratchet).
# ---------------------------------------------------------------------------

REAR_H = 36.0                           # constant; the racks need the height
REAR_T = BAND_T
REAR_BACK_X = -108.0                    # chord of the straight rack section (centreline)
REAR_BACK_Z = HEAD.nape_z_mm + 12.5     # -22.5 centreline at the back
REAR_TILT = math.degrees(math.atan2(CZ - REAR_BACK_Z, CX - REAR_BACK_X))   # ~26 deg
REAR_W = (-math.sin(math.radians(REAR_TILT)), 0.0, math.cos(math.radians(REAR_TILT)))   # band "up"
RACK_LEN = 66.0
RACK_Y_START = 42.0                     # rack begins here (|y|) and runs across the centre
# plan waypoints for the LEFT half, ring -> start of the straight rack (x, y)
REAR_WAYPOINTS = (
    (CX,     REAR_RING_Y),
    (-15.0,  123.0),
    (-45.0,  120.5),
    (-66.0,  116.5),
    (-88.0,  95.0),
    (-102.0, 66.0),
    (REAR_BACK_X + 0.5, 54.0),
)
GEAR_MODULE = 1.25
GEAR_PA = 20.0
PINION_N = 10
PINION_PITCH_R = GEAR_MODULE * PINION_N / 2.0           # 6.25
PINION_W = REAR_T                                       # 5.0
RACK_PITCH_W = PINION_PITCH_R                           # racks' pitch lines at +/- this (band-local W)
NAPE_HOUSING = (74.0, REAR_H + 6.0, 9.6)                # Y x W x N outer
NAPE_CHANNEL_N = REAR_T + 0.6
NAPE_WALL = 2.0
NAPE_SHAFT_D = 8.0
NAPE_KNOB_D = 34.0
NAPE_KNOB_H = 8.0
NAPE_RATCHET_TEETH = 24
NAPE_RATCHET_DIR = -1                   # flip if the knob locks in the tightening direction
NAPE_LID_SCREWS = ((-34.0, -17.0), (34.0, 17.0), (-22.0, 0.0), (22.0, 0.0))   # (u, v): closed corners + rib ends
# Battery / nape pack above the ratchet (2x 18650 flat pack 65 x 37 x 19)
NAPE_PACK = True
NAPE_PACK_INNER = (70.0, 40.0, 21.0)    # Y x W x N
NAPE_PACK_WALL = 1.6
NAPE_JACK_DIA = 8.0                     # panel-mount DC barrel jack (12 V aux in)

# ---------------------------------------------------------------------------
# Cheek hook (port add-on, front-lower port) and strap anchor
# ---------------------------------------------------------------------------

CHEEK_PAD = (30.0, 20.0, 3.0)           # X x Z x T plate; foam glued on the face side
CHEEK_PAD_Y_IN = HEAD.bizygomatic_mm / 2.0 - 2.0   # 68: pad inner face, hooks just under the arch
CHEEK_BAR = (12.0, BAND_T)              # bar height x thickness
STRAP_SLOT = (28.0, 4.0)                # 25 mm webbing

# ---------------------------------------------------------------------------
# Mass / balance references
# ---------------------------------------------------------------------------

NECK_PIVOT = (-15.0, 0.0, -45.0)        # approx atlanto-occipital joint, for tipping moments


def report() -> str:
    L = [
        "vp0.2 canon",
        f"  head: circ {HEAD.circumference_mm} | width {HEAD.width_mm} | length {HEAD.length_mm} | plan exp {HEAD.plan_exp} -> phantom perimeter {HEAD.plan_perimeter():.0f} mm",
        f"  brain core {BRAIN_CORE}; pods centred there",
        f"  pod: OD {DISH_OD} | skirt h {N_SKIRT_TOP} | reflector sag {REFL_SAG} (f/D {REFL_FOCAL/DISH_OD:.2f}) | cushion {CUSHION_T}",
        f"  Y stack (left): rim {RIM_Y} | cup face {CUP_FACE_Y} | hub top {HUB_TOP_Y} | rear ring {REAR_RING_Y:.1f} | brow ring {BROW_RING_Y:.1f} | knob face {NUT_FACE_Y:.1f}",
        f"  overall width incl. knobs: {2*(NUT_FACE_Y+KNOB_H):.0f} mm; protrusion past cup face {NUT_FACE_Y+KNOB_H-CUP_FACE_Y:.0f} mm",
        f"  pivot bolt grip {BOLT_GRIP_MM:.1f} mm -> M5x30 socket head",
        f"  crown: leg from z {CROWN_LEG_Z0:.1f} at y {POD_TOP_PORT_Y:.1f} to apex centreline z {CROWN_APEX_Z:.1f}; ports at {POD_PORT_ANGLES}",
        f"  brow: {BROW_W}x{BROW_H}x{BROW_T} at x {BROW_X_IN:.1f}..{BROW_X_OUT:.1f}, z {BROW_Z0}..{BROW_Z1}",
        f"  rear: tilt {REAR_TILT:.1f} deg, back chord x {REAR_BACK_X}, centreline z {REAR_BACK_Z}; pinion m{GEAR_MODULE} N{PINION_N}",
        f"  ports: {len(POD_PORT_ANGLES)} per pod + 2 brow + 1 apex = {2*len(POD_PORT_ANGLES)+3}",
    ]
    return "\n".join(L)


if __name__ == "__main__":
    print(report())
