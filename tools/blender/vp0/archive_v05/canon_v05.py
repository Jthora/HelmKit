"""
canon.py -- single source of truth for the HelmKit vp0.5 part set.

vp0.5 (2026-09-04): protected knob, integral brow spars, deeper rounded ports.
  * Nape: an ENCLOSED dial. Racks run in closed channels; the dial and pinion
    are one part on an M5 axle; a face ratchet on the cover holds it, a 3/8 x
    3/4 in compression spring loads it; press the dial face and turn to loosen.
    Only a recessed face shows through a ringed window.
  * Brow: centre panel + two wing-spar parts. The wing root is a pinned tenon
    in the centre; the spar tapers into the pod's front port post. No struts.
  * Ports: 20 mm deep, 1 mm internal corner radius, six per pod. Foam ID 80.
vp0.4 (2026-09-04): reinforcement pass on vp0.3 for a PLA prototype that
gets hit.
  * Pods are pure paraboloid SHELLS, concave toward the head, dome outside,
    no cavity (the pods carry no electronics). Five flush sockets live in a
    16 mm rim ring under the foam.
  * Every socket is locked by a NAIL in double shear (through both walls and
    the coupler), head counterbored and epoxied. Screws fit the same hole.
  * Couplers: aluminium 10 mm square tube, or printed with an axial channel
    for a nail-and-epoxy core. A drill guide and a socket casting form ship
    with the set.
  * Bands carry a rope-and-epoxy spine in a groove on the head-side face.
    Socket blocks carry a shallow collar groove for a thread-and-epoxy wrap.
  * Nape: the ratchet is gone. Two shorter rear bands end in rope eyes; a
    rope runs through a nape plate with a printed clam cleat (no moving
    parts). A second rope loop through every block ties the helm together.

Assembly frame: origin between the ear canals, +X forward, +Y wearer's LEFT,
+Z up. Left parts built at +Y; right = mirror across XZ. Units mm / deg / g.
Run `python3 canon.py` for a summary.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


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
# Materials, fasteners, reinforcement stock
# ---------------------------------------------------------------------------

MATERIAL = "PLA (prototype); PA12-CF or PC for the hit-rated build"
DENSITY_G_CM3 = 1.24          # PLA
M4_CLEAR_DIA = 4.4
M4_HEAD_DIA = 7.0
M4_NUT_AF = 7.0
M4_NUT_T = 3.2
M3_CLEAR_DIA = 3.4
M3_TAP_DIA = 2.5
FIT_CLEAR = 0.15
FILLET_MM = 1.0
FILLET_SEGMENTS = 2

PIN_DIA = 3.2                 # nail shank ~3.0 mm slip fit (measure yours; epoxy fills the rest)
PIN_HEAD_DIA = 6.5            # counterbore for the nail head
PIN_HEAD_DEPTH = 2.0
ROPE_DIA = 3.5                # 2-4 mm rope / twine
SPINE_GROOVE = (ROPE_DIA + 0.4, 2.8)     # width x depth of the rope-and-epoxy spine groove on bands
COLLAR_GROOVE = (6.0, 0.6)    # width x depth of the thread-wrap collar around socket blocks
CAST_SOCKETS = False          # True: sockets 1 mm oversize with ribs, to be cast in metal epoxy around the form
CAST_OVERSIZE = 1.0
COUPLER_TUBE = "10 x 10 x 1 mm aluminium square tube (preferred) or printed PLA with a nail-and-epoxy core"

# ---------------------------------------------------------------------------
# Pod: paraboloid shell, dome outside, rim ring with flush sockets
# ---------------------------------------------------------------------------

DISH_OD = 122.1               # physics: wavelength-linked, do not change
DISH_R = DISH_OD / 2.0
RING_H = 16.0                 # rim ring height (sockets live here, under the foam)
RING_WALL = 4.0
RING_IN_R = DISH_R - RING_WALL          # 57.05
SHELL_T = 3.0
DOME_SAG = 10.0               # dome rise above the ring's outer edge
CUSHION_T = 15.0
CUSHION_ID = 80.0             # ear still clears; hides the 20 mm socket tunnels
RIM_Y = HEAD.width_mm / 2.0 + CUSHION_T                 # 92.5  cushion face
POD_THICK = RING_H + DOME_SAG                           # 26
POD_OUT_Y = RIM_Y + POD_THICK                           # 118.5 dome vertex
DOME_FOCAL = RING_IN_R ** 2 / (4.0 * DOME_SAG)
EAR_ROOM_CENTER = CUSHION_T + RING_H + DOME_SAG - SHELL_T  # 38

# ---------------------------------------------------------------------------
# Port standard (flush sockets, pinned)
# ---------------------------------------------------------------------------

PORT_SQ = 10.0
PORT_CLEAR = 0.3
PORT_DEPTH = 20.0             # v0.5: deeper engagement halves socket-wall load
PORT_PLUG_LEN = PORT_DEPTH - 0.5
PORT_PIN_DEPTH = 7.0          # pin axis, measured from the socket mouth
PORT_TUNNEL_WALL = 2.0
PORT_BLOCK = PORT_SQ + PORT_CLEAR + 2 * 2.65    # 15.6
PORT_BLOCK_LEN = PORT_DEPTH + 3.0               # 23
PORT_CORNER_R = 1.0           # internal corner radius of every socket, matching post edge fillet
SHEAR_PIN_DIA = 1.8           # breakaway option on add-on plugs: toothpick / 1.5 mm nail
SOCKET_N0 = (RING_H - (PORT_SQ + PORT_CLEAR)) / 2.0     # 2.85 (socket centred in the ring height)
SOCKET_N1 = SOCKET_N0 + PORT_SQ + PORT_CLEAR            # 13.15
POD_PORT_Y = RIM_Y + RING_H / 2.0                       # 100.5  every band/strut centreline
BROW_TILT = 13.0
POD_PORT_ANGLES = (BROW_TILT, 90.0, 135.0, 206.0, 250.0, 300.0)
POD_PORT_NAMES = {BROW_TILT: "front (brow wing spar)", 90.0: "top (crown arch)", 135.0: "rear-upper (spare)",
                  206.0: "rear (rear band)", 250.0: "rear-lower (spare)", 300.0: "front-lower (strap anchor)"}
FRONT_PORT_ANGLE = BROW_TILT
REAR_PORT_ANGLE = 206.0

# ---------------------------------------------------------------------------
# Crown arch
# ---------------------------------------------------------------------------

CROWN_W = 30.0
CROWN_T = 6.0                 # +1 mm over v0.3: room for the spine groove
CROWN_PAD_T = 12.0
CROWN_FOOT = (CROWN_W, 16.0, PORT_BLOCK_LEN)
CROWN_LEG_Z0 = CZ + DISH_R + CROWN_FOOT[2]      # 111.05
APEX_FLOOR_T = 2.0
APEX_SLEEVE = (40.0, 64.0, 11.4)
CROWN_APEX_Z = HEAD.vertex_z_mm + CROWN_PAD_T + APEX_FLOOR_T + 0.2 + CROWN_T / 2.0   # 152.2
CROWN_SUPER_N = 2.6
CROWN_OVERLAP = 40.0
CROWN_BAR_W = CROWN_W / 2.0
CROWN_SLOT_L = 26.0
CROWN_SLOT_W = M4_CLEAR_DIA
CROWN_SERR_PITCH = 2.0
CROWN_SERR_H = 0.6
POD_TOP_PORT_Y = POD_PORT_Y
CROWN_PAD = (40.0, 60.0, CROWN_PAD_T)

# ---------------------------------------------------------------------------
# Brow panel
# ---------------------------------------------------------------------------

BROW_CENTER_W = 100.0
BROW_WING_ANGLE = 20.0
BROW_H = 50.0
BROW_T = 15.0
BROW_WALL = 2.0
BROW_Z0 = HEAD.brow_z_mm + 2.0
BROW_Z1 = BROW_Z0 + BROW_H
BROW_CLEAR = 10.0
BROW_LID_T = 2.0
BROW_LED_WINDOW = (50.0, 6.0)
BROW_CAV_W = 56.0              # centre ends stay solid for the wing tenons
BROW_PAD = (60.0, 44.0, 12.0)


def _forehead_x(z: float) -> float:
    a, _, c = HEAD.phantom_semi
    s = 1.0 - ((z - HEAD.phantom_center_z) / c) ** 2
    return a * math.sqrt(max(0.0, s))


BROW_X_IN = max(_forehead_x(z) for z in (BROW_Z0, BROW_Z0 + 10, BROW_Z0 + 25, BROW_Z1)) + BROW_CLEAR
BROW_X_OUT = BROW_X_IN + BROW_T
_t = math.radians(BROW_TILT)
BROW_EX = (math.cos(_t), 0.0, math.sin(_t))
BROW_EZ = (-math.sin(_t), 0.0, math.cos(_t))
BROW_ORIGIN = (BROW_X_IN, 0.0, BROW_Z0)
BROW_STRUT_LOCAL_Z = (CX - BROW_ORIGIN[0]) * BROW_EZ[0] + (CZ - BROW_ORIGIN[2]) * BROW_EZ[2]
BROW_WING_LEN = (POD_PORT_Y - BROW_CENTER_W / 2.0) / math.cos(math.radians(BROW_WING_ANGLE))
BROW_LID_SCREWS = ((-31.0, 10.0), (31.0, 10.0), (-31.0, BROW_H - 10.0), (31.0, BROW_H - 10.0))
BROW_TENON = (BROW_T - 3.0, BROW_H - 4.0, 15.0)      # x thickness, z height, depth into the centre end
BROW_TENON_PINS = (4.5, 11.0)                       # depths from the centre end face, vertical nails
BROW_SPAR = (25.0, 12.0)                            # z height x y thickness of the wing spar before the post
BROW_TOP_BEAD_R = 4.0        # wide enough to swallow the nail-head counterbores

# ---------------------------------------------------------------------------
# Rear bands + nape plate with clam cleat
# ---------------------------------------------------------------------------

REAR_H = 36.0                 # racks need it
REAR_T = 6.0
REAR_BLOCK_GAP = 5.0
_a = math.radians(REAR_PORT_ANGLE)
REAR_D = (math.cos(_a), 0.0, math.sin(_a))
REAR_TILT = REAR_PORT_ANGLE - 180.0
REAR_W = (-math.sin(math.radians(REAR_TILT)), 0.0, math.cos(math.radians(REAR_TILT)))
REAR_MOUTH = (CX + DISH_R * REAR_D[0], POD_PORT_Y, CZ + DISH_R * REAR_D[2])
_r0 = DISH_R + REAR_BLOCK_GAP + PORT_BLOCK_LEN
REAR_START = (CX + _r0 * REAR_D[0], POD_PORT_Y, CZ + _r0 * REAR_D[2])
REAR_BACK_X = -108.0
REAR_BACK_Z = HEAD.nape_z_mm + 12.5
REAR_WAYPOINTS = (                      # plan (x, y) LEFT half, start -> rack start at y = 50
    (REAR_START[0], REAR_START[1]),
    (-78.0, 90.0),
    (-93.0, 72.0),
    (-103.0, 58.0),
    (-107.5, 54.0),
)
RACK_LEN = 66.0
GEAR_MODULE = 1.25
GEAR_PA = 20.0
PINION_N = 10
PINION_PITCH_R = GEAR_MODULE * PINION_N / 2.0           # 6.25
PINION_W = 5.0
RACK_PITCH_W = PINION_PITCH_R
# Enclosed dial (nape local frame: u = -Y, v = W up, w = outward; band mid-plane at w = 0)
NAPE_HU, NAPE_HV = 80.0, 54.0
NAPE_WALL = 2.5
NAPE_CH = 2.8                                           # channel half-thickness (racks are +/-2.5)
NAPE_LID_T = 2.2                                        # head-side lid: w -5.0 .. -2.8
NAPE_BODY_W1 = NAPE_CH + 2.0                            # 4.8 outer channel wall face
NAPE_PINION_W0 = -1.5                                   # pinion rests at w -1.5 .. 3.5 (moves inward on release)
NAPE_PINION_CAV_R = 8.2
NAPE_HUB_D = 14.0
NAPE_DIAL_D = 44.0
NAPE_DIAL_T = 8.0
NAPE_SPRING = dict(od=9.5, free=19.0, working=9.0, wire=0.8, note="3/8 x 3/4 in compression spring")
NAPE_SPRING_WELL = (11.0, 6.0)                          # dia x depth in the dial's inner face
NAPE_DIAL_W0 = NAPE_BODY_W1 + (NAPE_SPRING["working"] - NAPE_SPRING_WELL[1])   # 7.8 dial inner face
NAPE_RATCHET_R = (17.0, 21.0)          # outside the window, inside the dial rim
NAPE_RATCHET_H = 1.0
NAPE_RATCHET_TEETH = 24
NAPE_RATCHET_DIR = -1                                   # flip if it clicks when loosening and locks when tightening
NAPE_RELEASE_TRAVEL = 1.5
NAPE_COVER_W0 = NAPE_DIAL_W0 + NAPE_DIAL_T + NAPE_RATCHET_H + 0.2   # 17.0 cover inner face
NAPE_COVER_T = 2.5
NAPE_WINDOW_D = 30.0
NAPE_AXLE = "M5 x 35 bolt (or 5 mm rod): head epoxied to the lid, nyloc nut loose in the dial face pocket"
NAPE_LID_SCREWS = ((-34.0, -17.0), (34.0, 17.0), (-22.0, 0.0), (22.0, 0.0))
NAPE_COVER_SCREWS = ((-34.0, -22.0), (34.0, -22.0), (-34.0, 22.0), (34.0, 22.0))
NAPE_PAD = (74.0, 42.0, 10.0)
REAR_SIDE_PAD = (50.0, 30.0, 12.0)

# ---------------------------------------------------------------------------
# Add-ons, retention loop
# ---------------------------------------------------------------------------

STRAP_SLOT = (28.0, 4.0)
COUPLER_CROWN_LEN = 2 * PORT_PLUG_LEN
COUPLER_REAR_LEN = REAR_BLOCK_GAP + 2 * PORT_PLUG_LEN
APEX_FILLET = 3.0
NECK_PIVOT = (-15.0, 0.0, -45.0)


def report() -> str:
    L = [
        "vp0.5 canon",
        f"  head: width {HEAD.width_mm} | length {HEAD.length_mm} | phantom perimeter {HEAD.plan_perimeter():.0f}",
        f"  pod: shell OD {DISH_OD}, ring {RING_H} + dome {DOME_SAG} = {POD_THICK} thick; ear room at centre {EAR_ROOM_CENTER}; dome f/D {DOME_FOCAL/DISH_OD:.2f}",
        f"  overall width at the dome vertices: {2*POD_OUT_Y:.0f} mm; band centreline y {POD_PORT_Y}",
        f"  ports {POD_PORT_ANGLES}; pin {PIN_DIA} mm nail in double shear; cast sockets {CAST_SOCKETS}",
        f"  crown: ribbon {CROWN_W}x{CROWN_T} from z {CROWN_LEG_Z0:.1f} to apex {CROWN_APEX_Z:.1f}; spine groove {SPINE_GROOVE}",
        f"  brow: centre {BROW_CENTER_W} + wings {BROW_WING_LEN:.1f} @ {BROW_WING_ANGLE}, tilt {BROW_TILT}",
        f"  rear: port {REAR_PORT_ANGLE}, bands {REAR_H}x{REAR_T}, racks m{GEAR_MODULE}; enclosed dial Ø{NAPE_DIAL_D}, spring {NAPE_SPRING['note']}, housing w -5..{NAPE_COVER_W0 + 3.0:.1f}",
        f"  couplers: crown {COUPLER_CROWN_LEN}, rear {COUPLER_REAR_LEN}; brow spars integral; {COUPLER_TUBE}",
    ]
    return "\n".join(L)


if __name__ == "__main__":
    print(report())
