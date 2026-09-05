"""
canon.py -- single source of truth for the HelmKit vp0.3 part set.

vp0.3 (2026-09-04): snag/robustness pass on vp0.2.
  * No pivot stack. Bands and struts plug into FLUSH port sockets sunk into the
    pod skirt; collapsing = unplugging. Side width drops from 283 to 232 mm.
  * Every high-load joint is a socket-coupler-socket pair; couplers can be
    printed or cut from 10 mm aluminium square tube.
  * Brow panel: flat centre + 20 deg swept wings, connected by two straight
    struts from the pods' front ports. Crown arch feet sit on the pod rim.
  * Rear band starts at the pod's rear port, hugs the occiput, same nape ratchet
    with a bumper around the dial.
  * Foam pads are modelled (ear rings, crown, brow, nape, rear sides) so the
    open loops a branch could enter are closed.
  * Pouch cells live inside the pods. Cheek hooks dropped; strap anchors default.
  * Fillet pass on every printed part.

Assembly frame: origin between the ear canals, +X forward, +Y wearer's LEFT,
+Z up. Left parts built at +Y; right = mirror across XZ. Units mm / deg / g.
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
    width_mm: float = 155.0
    length_mm: float = 202.5
    ear_to_ear_over_crown_mm: float = 330.0
    canal_to_crown_arc_mm: float = 200.0
    vertex_z_mm: float = 135.0
    brow_z_mm: float = 40.0
    hairline_z_mm: float = 95.0
    inion_z_mm: float = 5.0
    nape_z_mm: float = -35.0
    plan_exp: float = 2.45
    phantom_center_z: float = 25.0

    @property
    def phantom_semi(self) -> tuple[float, float, float]:
        return (self.length_mm / 2.0, self.width_mm / 2.0, self.vertex_z_mm - self.phantom_center_z)

    def implicit(self, x: float, y: float, z: float) -> float:
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
BRAIN_CORE = (10.0, 0.0, 35.0)
CX, CZ = BRAIN_CORE[0], BRAIN_CORE[2]

# ---------------------------------------------------------------------------
# Fasteners / print constants
# ---------------------------------------------------------------------------

M4_CLEAR_DIA = 4.4
M4_HEAD_DIA = 7.0
M4_NUT_AF = 7.0
M4_NUT_T = 3.2
M3_CLEAR_DIA = 3.4
M3_TAP_DIA = 2.5            # thread-forming M3 straight into PETG
M3_CSK_DIA = 6.5            # 90 deg countersink for flat-head M3
M3_NUT_AF = 5.5
M3_NUT_T = 2.4
M2_TAP_DIA = 1.7
FIT_CLEAR = 0.15
PETG_DENSITY_G_CM3 = 1.27
FILLET_MM = 1.0             # bevel pass on printed parts
FILLET_SEGMENTS = 2

# ---------------------------------------------------------------------------
# Pod: face-down cup + glued reflector, flush sockets in the skirt
# ---------------------------------------------------------------------------

DISH_OD = 122.1
DISH_R = DISH_OD / 2.0
SKIRT_WALL = 2.5
CUP_FLOOR_T = 2.5
REFL_SAG = 8.0
REFL_T = 2.0
REFL_LIP_H = 0.5
LEDGE_STEP = 1.0
CUSHION_T = 15.0
CAVITY_MIN = 10.5                       # floor inner face -> reflector underside at the vertex (pouch cell + socket tunnels)
SKIRT_IN_R = DISH_R - SKIRT_WALL        # 58.55
REFL_R = SKIRT_IN_R + LEDGE_STEP - FIT_CLEAR    # 59.40
VENT_DIA = 4.0
REFL_PERF = True
REFL_PERF_N = 30
REFL_PERF_R = 40.0
REFL_PERF_D = 3.0

N_FLOOR_IN = CUP_FLOOR_T                                # 2.5
N_REFL_UNDER = N_FLOOR_IN + CAVITY_MIN                  # 13.0
N_REFL_VERTEX = N_REFL_UNDER + REFL_T                   # 15.0
N_REFL_RIM = N_REFL_VERTEX + REFL_SAG                   # 23.0
N_LEDGE = N_REFL_RIM - REFL_T                           # 21.0
N_SKIRT_TOP = N_REFL_RIM + REFL_LIP_H                   # 23.5
REFL_FOCAL = SKIRT_IN_R ** 2 / (4.0 * REFL_SAG)

RIM_Y = HEAD.width_mm / 2.0 + CUSHION_T                 # 92.5
CUP_FACE_Y = RIM_Y + N_SKIRT_TOP                        # 116.0

CAP_GROOVE_W = 3.0
CAP_GROOVE_D = 0.8
CAP_GROOVE_R0 = 26.0
CAP_GROOVE_R1 = 50.0
CAP_GROOVE_ANGLES = (45.0, 135.0, 225.0, 315.0)
CAP_RING_GROOVE = (53.0, 54.5)

FAN_PITCH = 20.0
FAN_STANDOFF_H = 5.0
FAN_STANDOFF_D = 5.0
FAN_CENTER_R = 28.0
FAN_CENTER_ANGLE = 240.0
VENT_SLOTS = 8
VENT_SLOT_W = 3.0
VENT_SLOT_L = 10.0
VENT_ANGLE_0, VENT_ANGLE_1 = 150.0, 190.0
JACK_ANGLE, USB_ANGLE = 262.0, 277.0
NAPE_JACK_DIA = 8.0
POUCH_CELL = (60.0, 40.0, 8.0)          # reference LiPo pouch inside each pod (not printed)

# ---------------------------------------------------------------------------
# Port standard (flush sockets)
# ---------------------------------------------------------------------------

PORT_SQ = 10.0
PORT_CLEAR = 0.3
PORT_DEPTH = 12.0
PORT_PLUG_LEN = PORT_DEPTH - 0.5        # 11.5
PORT_SCREW_DEPTH = 7.0                  # locking screw, measured from the socket mouth
PORT_TUNNEL_WALL = 2.0                  # wall around a socket sunk into a body
PORT_BLOCK = PORT_SQ + PORT_CLEAR + 2 * 2.65    # 15.6 -> block section around a socket on a band
PORT_BLOCK_LEN = PORT_DEPTH + 3.0       # 15.0
# In the pod: the socket sits in the skirt band between the floor and the reflector.
SOCKET_N0 = N_FLOOR_IN + 1.5                    # 4.0  socket bottom (toward the cup face)
SOCKET_N1 = SOCKET_N0 + PORT_SQ + PORT_CLEAR    # 14.3
POD_PORT_Y = CUP_FACE_Y - (SOCKET_N0 + SOCKET_N1) / 2.0    # 106.85  every band/strut centreline
POD_PORT_SCREW_R = DISH_R - PORT_SCREW_DEPTH    # 54.05 screw from the outer face into the plug

BROW_TILT = 13.0                        # panel leans back; the front port aims along the panel normal
POD_PORT_ANGLES = (BROW_TILT, 90.0, 135.0, 206.0, 300.0)
POD_PORT_NAMES = {BROW_TILT: "front (brow strut)", 90.0: "top (crown arch)", 135.0: "rear-upper (spare, pylons)",
                  206.0: "rear (rear band)", 300.0: "front-lower (strap anchor)"}
FRONT_PORT_ANGLE = BROW_TILT
REAR_PORT_ANGLE = 206.0
COUPLER_TUBE = "10 x 10 x 1 mm aluminium square tube, or printed PETG"

# ---------------------------------------------------------------------------
# Crown arch: feet on the pod rims (top ports), apex sleeve with width adjust
# ---------------------------------------------------------------------------

CROWN_W = 30.0
CROWN_T = 5.0
CROWN_PAD_T = 12.0
CROWN_FOOT = (CROWN_W, 16.0, PORT_BLOCK_LEN)    # X x Y x Z, concave seat on the rim
CROWN_LEG_Z0 = CZ + DISH_R + CROWN_FOOT[2]      # 111.05
APEX_FLOOR_T = 2.0
APEX_SLEEVE = (40.0, 64.0, 10.4)
CROWN_APEX_Z = HEAD.vertex_z_mm + CROWN_PAD_T + APEX_FLOOR_T + 0.2 + CROWN_T / 2.0   # 151.7
CROWN_SUPER_N = 2.6
CROWN_OVERLAP = 40.0
CROWN_BAR_W = CROWN_W / 2.0
CROWN_SLOT_L = 26.0
CROWN_SLOT_W = M4_CLEAR_DIA
CROWN_SERR_PITCH = 2.0
CROWN_SERR_H = 0.6
POD_TOP_PORT_Y = POD_PORT_Y
CROWN_PAD = (40.0, 60.0, CROWN_PAD_T)   # foam under the apex sleeve

# ---------------------------------------------------------------------------
# Brow panel: flat centre + swept wings, struts from the front ports
# ---------------------------------------------------------------------------

BROW_CENTER_W = 100.0
BROW_WING_ANGLE = 20.0                  # wings sweep back
BROW_H = 50.0
BROW_T = 12.0
BROW_WALL = 2.0
BROW_Z0 = HEAD.brow_z_mm + 2.0          # 42
BROW_Z1 = BROW_Z0 + BROW_H              # 92
BROW_CLEAR = 10.0
BROW_LID_T = 2.0
BROW_LED_WINDOW = (80.0, 6.0)
BROW_CAV_W = 92.0
BROW_PAD = (96.0, 44.0, 12.0)           # foam on the lid, closes the forehead gap


def _forehead_x(z: float) -> float:
    a, _, c = HEAD.phantom_semi
    s = 1.0 - ((z - HEAD.phantom_center_z) / c) ** 2
    return a * math.sqrt(max(0.0, s))


BROW_X_IN = max(_forehead_x(z) for z in (BROW_Z0, BROW_Z0 + 10, BROW_Z0 + 25, BROW_Z1)) + BROW_CLEAR   # 110
BROW_X_OUT = BROW_X_IN + BROW_T
# Panel local frame: origin at the inner-bottom edge centre, ex = outward normal, ez = up (both tilted)
_t = math.radians(BROW_TILT)
BROW_EX = (math.cos(_t), 0.0, math.sin(_t))
BROW_EZ = (-math.sin(_t), 0.0, math.cos(_t))
BROW_ORIGIN = (BROW_X_IN, 0.0, BROW_Z0)
# Struts run along BROW_EX from the pod front port; in panel coordinates they sit at this local z:
BROW_STRUT_LOCAL_Z = (CX - BROW_ORIGIN[0]) * BROW_EZ[0] + (CZ - BROW_ORIGIN[2]) * BROW_EZ[2]   # ~15.7
BROW_WING_LEN = (POD_PORT_Y - BROW_CENTER_W / 2.0) / math.cos(math.radians(BROW_WING_ANGLE))   # 60.5: wing end meets the strut line
BROW_LID_SCREWS = ((-42.0, BROW_Z0 - BROW_Z0 + 10.0), (42.0, 10.0), (-42.0, BROW_H - 10.0), (42.0, BROW_H - 10.0))  # (local y, local z)

# ---------------------------------------------------------------------------
# Rear band: from the rear port, hugging the occiput, nape ratchet
# ---------------------------------------------------------------------------

REAR_H = 36.0
REAR_T = 5.0
REAR_BLOCK_GAP = 5.0                    # socket block mouth stands this far off the pod rim
_a = math.radians(REAR_PORT_ANGLE)
REAR_D = (math.cos(_a), 0.0, math.sin(_a))                    # port radial direction (back, 26 deg down)
REAR_TILT = REAR_PORT_ANGLE - 180.0                            # 26: band plane slope, contains the port axis
REAR_W = (-math.sin(math.radians(REAR_TILT)), 0.0, math.cos(math.radians(REAR_TILT)))
REAR_MOUTH = (CX + DISH_R * REAR_D[0], POD_PORT_Y, CZ + DISH_R * REAR_D[2])                   # (-44.8, 106.85, 8.3)
_r0 = DISH_R + REAR_BLOCK_GAP + PORT_BLOCK_LEN                                                 # 81.05 band starts here
REAR_START = (CX + _r0 * REAR_D[0], POD_PORT_Y, CZ + _r0 * REAR_D[2])                          # (-62.8, 106.85, -0.5)
REAR_BACK_X = -108.0
REAR_BACK_Z = HEAD.nape_z_mm + 12.5     # -22.5 (consistent with the 26 deg plane through the mouth)
REAR_WAYPOINTS = (                      # plan (x, y) LEFT half, start -> rack
    (REAR_START[0], REAR_START[1]),
    (-75.0, 96.0),
    (-90.0, 78.0),
    (-101.0, 62.0),
    (-107.0, 54.0),
)
RACK_LEN = 66.0
GEAR_MODULE = 1.25
GEAR_PA = 20.0
PINION_N = 10
PINION_PITCH_R = GEAR_MODULE * PINION_N / 2.0
PINION_W = REAR_T
RACK_PITCH_W = PINION_PITCH_R
NAPE_HOUSING = (74.0, REAR_H + 6.0, 9.6)
NAPE_CHANNEL_N = REAR_T + 0.6
NAPE_WALL = 2.0
NAPE_SHAFT_D = 8.0
NAPE_KNOB_D = 34.0
NAPE_KNOB_H = 8.0
NAPE_RATCHET_TEETH = 24
NAPE_RATCHET_DIR = -1
NAPE_LID_SCREWS = ((-34.0, -17.0), (34.0, 17.0), (-22.0, 0.0), (22.0, 0.0))
NAPE_BUMPER = (19.5, 22.5, 200.0)       # r_in, r_out, arc degrees of the C bumper around the dial (open at the top)
NAPE_PAD = (74.0, 42.0, 10.0)
REAR_SIDE_PAD = (50.0, 30.0, 12.0)      # foam strips on the band's inner face beside the occiput

# ---------------------------------------------------------------------------
# Add-ons
# ---------------------------------------------------------------------------

STRAP_SLOT = (28.0, 4.0)
COUPLER_CROWN_LEN = 2 * PORT_PLUG_LEN                       # 23
COUPLER_REAR_LEN = REAR_BLOCK_GAP + 2 * PORT_PLUG_LEN       # 28
NECK_PIVOT = (-15.0, 0.0, -45.0)


def report() -> str:
    L = [
        "vp0.3 canon",
        f"  head: width {HEAD.width_mm} | length {HEAD.length_mm} | phantom perimeter {HEAD.plan_perimeter():.0f}",
        f"  pod: OD {DISH_OD} | skirt h {N_SKIRT_TOP} | socket n {SOCKET_N0}..{SOCKET_N1} | band centreline y {POD_PORT_Y:.2f}",
        f"  overall width (pod faces): {2*CUP_FACE_Y:.0f} mm",
        f"  ports: {POD_PORT_ANGLES}",
        f"  crown: feet on rim, ribbon from z {CROWN_LEG_Z0:.1f} to apex {CROWN_APEX_Z:.1f}",
        f"  brow: centre {BROW_CENTER_W} + wings {BROW_WING_LEN:.1f} @ {BROW_WING_ANGLE} deg, tilt {BROW_TILT}; strut at local z {BROW_STRUT_LOCAL_Z:.1f}",
        f"  rear: port {REAR_PORT_ANGLE} -> start {tuple(round(v,1) for v in REAR_START)}; tilt {REAR_TILT}; nape ({REAR_BACK_X}, 0, {REAR_BACK_Z})",
        f"  couplers: crown {COUPLER_CROWN_LEN}, rear {COUPLER_REAR_LEN}, brow computed in build_brow_panel",
    ]
    return "\n".join(L)


if __name__ == "__main__":
    print(report())
