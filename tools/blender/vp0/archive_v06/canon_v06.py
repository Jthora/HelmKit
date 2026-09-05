"""
canon.py -- single source of truth for the HelmKit vp0.6 part set.

vp0.6 (2026-09-04): cradle architecture. The head is held by a hard-hat style
CRADLE (front U + two tilted rear halves + nape dial) with foam blocks; the
pods float 20 mm off the skull on two pinned brackets each and touch nothing.
Brow hinges on the cradle's temple nodes (visor motion, folds flat). Crown
arch feet are hinge plugs (folds flat). Dial is the PULL variant: key ribs on
the face, spring outside, a fall cannot release it. Chin strap on the cradle.
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
CUSHION_T = 0.0               # v0.6: pods touch nothing
POD_RIM_Y = 104.0             # pod rim plane: 7 mm outside the cradle nodes, 26.5 mm off the skull
RIM_Y = POD_RIM_Y                                       # 97.5
POD_THICK = RING_H + DOME_SAG                           # 26
POD_OUT_Y = RIM_Y + POD_THICK                           # 118.5 dome vertex
DOME_FOCAL = RING_IN_R ** 2 / (4.0 * DOME_SAG)
EAR_ROOM_CENTER = (POD_RIM_Y - HEAD.width_mm / 2.0) + RING_H + DOME_SAG - SHELL_T  # 49.5

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
POD_PORT_ANGLES = (BROW_TILT, 90.0, 135.0, 175.0, 250.0, 300.0)
POD_PORT_NAMES = {BROW_TILT: "front (bracket to temple node)", 90.0: "top (crown arch hinge plug)", 135.0: "rear-upper (spare)",
                  175.0: "rear (bracket to mastoid node)", 250.0: "rear-lower (spare)", 300.0: "front-lower (spare)"}
FRONT_PORT_ANGLE = BROW_TILT
REAR_PORT_ANGLE = 175.0

# ---------------------------------------------------------------------------
# Cradle: front U (forehead + sides + temple/mastoid nodes) + rear halves + nape dial
# ---------------------------------------------------------------------------

CRADLE_H = 30.0
CRADLE_T = 5.0
CRADLE_FOAM = 10.0
CRADLE_SIDE_Y = HEAD.width_mm / 2.0 + CRADLE_FOAM + CRADLE_T / 2.0      # 90.0 band centreline at the sides
CRADLE_FRONT_X = HEAD.phantom_semi[0] + CRADLE_FOAM + CRADLE_T / 2.0     # 113.75 band centreline at the forehead
CRADLE_Z = 55.0                          # horizontal hat line: band z 40..70, clears the top of the ear
CRADLE_WAYPOINTS = ((-56.0, CRADLE_SIDE_Y), (-20.0, CRADLE_SIDE_Y), (30.0, CRADLE_SIDE_Y), (66.0, CRADLE_SIDE_Y),
                    (94.0, 62.0), (CRADLE_FRONT_X, 0.0))   # plan, LEFT half, rear node -> forehead; mirrored for the right


def cradle_z(x: float) -> float:
    return CRADLE_Z


TEMPLE_NODE_X = 66.0
REAR_NODE_X = -45.0
NODE_LEN = 26.0                          # along the band
NODE_IN_Y = 84.0                         # node inner face (3.5 inside the band's inner face; 6 mm foam there)
NODE_OUT_Y = 97.0                        # node outer face (7 inside the pod rim plane)
NODE_W = (-15.0, 15.0)                   # temple node W range = the band
REAR_NODE_W = (-33.0, 15.0)              # rear node hangs 18 below the band to meet the rear half and the rear bracket
HINGE_BOLT = "M3 x 25 with nyloc"
HINGE_SERR = dict(r_in=5.0, r_out=8.3, teeth=24, height=0.8, phase_ear=7.9, phase_tongue=0.4)   # odd phases: no vertex lands on a mesh line   # detent rings around every M3 hinge
HINGE_SLOT_W = 6.9                       # 6 mm tongue + one 0.8 serration face + 0.1
BROW_HINGE_X = TEMPLE_NODE_X + NODE_LEN / 2.0 - 9.0       # 70: 9 mm behind the node's front face (disc and ring stay inside the ear)
BROW_HINGE_W = 4.0                       # above the band centreline (z 59); the serration ring stays inside the ear
BROW_DISC_R = 8.5
BROW_SLOT_DEPTH = 18.5                   # from the node's front face; open at the top; floor at W -5
BRACKET_BOLT_W = -11.0                   # front node: M3 + nail at x 56 / 63 on this line
FRONT_BRACKET_HOLES = ((TEMPLE_NODE_X - 10.0, BRACKET_BOLT_W), (TEMPLE_NODE_X - 3.0, BRACKET_BOLT_W))   # (x, W): bolt, nail
REAR_BRACKET_HOLES = ((REAR_NODE_X + 7.0, -11.0), (REAR_NODE_X + 7.0, -23.0))                          # (x, W): bolt, nail
REAR_TENON_W0 = -17.0                    # rear half centreline leaves the rear node here (z 38)
CRADLE_TENON = (5.0, 26.0, 14.0, 8.0)    # y thickness, mouth height, depth, tip half-height (symmetric taper: the right half is the left rotated 180 deg)
TENON_PIN_X = REAR_NODE_X - NODE_LEN / 2.0 + 6.0          # -52: nail through node + tenon along Y
STRAP_SLOT = (14.0, 4.0)                 # W height x along-band width, through the band, centred at W +4.5; pairs 8 mm apart
CRADLE_STRAP_X = (47.0, 39.0)            # slot centres behind the temple node (world x)
REAR_STRAP_S = (24.0, 32.0)              # slot centres along the rear half from the node (arc mm)
CABLE_GROOVE = (2.2, 2.5)                # width x depth, cut into the band's TOP edge, outer half
SPINE_W = -10.5                          # rope spine groove line on the cradle's inner face (below the brow slot floor)
FOAM_BLOCKS = dict(forehead=(70.0, 26.0, 10.0), side=(40.0, 26.0, 10.0), temple=(24.0, 26.0, 6.0), rear=(24.0, 40.0, 6.0))

# ---------------------------------------------------------------------------
# Crown arch
# ---------------------------------------------------------------------------

CROWN_W = 30.0
CROWN_T = 6.0                 # +1 mm over v0.3: room for the spine groove
CROWN_PAD_T = 12.0
HINGE_PLUG_EAR_T = 6.0
HINGE_PLUG_LIP = (16.0, 3.0)
HINGE_PLUG_H = 24.0                      # clevis ears above the lip
CROWN_HINGE_Z = CZ + DISH_R + HINGE_PLUG_LIP[1] + 11.5  # 110.55 hinge bolt axis
CROWN_LEG_Z0 = CZ + DISH_R + HINGE_PLUG_LIP[1] + 0.5   # 99.55: the tongue starts 0.5 above the plug lip
CROWN_BEND_Z = CROWN_LEG_Z0 + 25.5      # straight tongue up to here, then the superellipse
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
BROW_Z0 = HEAD.brow_z_mm - 1.0   # 39: panel bottom at the eyebrow line, 18 mm in front of it
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


BROW_X_IN = CRADLE_FRONT_X + CRADLE_T / 2.0 + 2.0 + (CRADLE_Z + CRADLE_H / 2.0 - BROW_Z0) * math.tan(math.radians(BROW_TILT))   # 125.4: the tilted panel's inner face clears the band's top edge by 2 mm
BROW_X_OUT = BROW_X_IN + BROW_T
_t = math.radians(BROW_TILT)
BROW_EX = (math.cos(_t), 0.0, math.sin(_t))
BROW_EZ = (-math.sin(_t), 0.0, math.cos(_t))
BROW_ORIGIN = (BROW_X_IN, 0.0, BROW_Z0)
BROW_STRUT_LOCAL_Z = (CX - BROW_ORIGIN[0]) * BROW_EZ[0] + (CZ - BROW_ORIGIN[2]) * BROW_EZ[2]
BROW_HINGE = (BROW_HINGE_X, (NODE_IN_Y + NODE_OUT_Y) / 2.0, CRADLE_Z + BROW_HINGE_W)   # (72, 90.5, 65) hinge axis along Y
BROW_TONGUE_T = 6.0
BROW_LID_SCREWS = ((-31.0, 10.0), (31.0, 10.0), (-31.0, BROW_H - 10.0), (31.0, BROW_H - 10.0))
BROW_TENON = (BROW_T - 3.0, BROW_H - 4.0, 15.0)      # x thickness, z height, depth into the centre end
BROW_TENON_PINS = (4.5, 11.0)                       # depths from the centre end face, vertical nails
BROW_TOP_BEAD_R = 4.0        # wide enough to swallow the nail-head counterbores

# ---------------------------------------------------------------------------
# Rear bands + nape plate with clam cleat
# ---------------------------------------------------------------------------

REAR_H = 36.0                 # racks need it
REAR_T = 6.0
REAR_START = (REAR_NODE_X - NODE_LEN / 2.0, CRADLE_SIDE_Y, CRADLE_Z + REAR_TENON_W0)   # (-58, 90, 38) rear node's rear face
REAR_BACK_X = -108.0
REAR_BACK_Z = -20.0                      # band centreline at the nape, under the occipital bump
REAR_TILT = math.degrees(math.atan2(REAR_START[2] - REAR_BACK_Z, REAR_START[0] - REAR_BACK_X))   # ~49 deg: the band slants from behind the ear to the nape
REAR_W = (-math.sin(math.radians(REAR_TILT)), 0.0, math.cos(math.radians(REAR_TILT)))
REAR_MOUTH = REAR_START
REAR_T_IN = (math.cos(math.radians(REAR_TILT)), 0.0, math.sin(math.radians(REAR_TILT)))   # into the node (forward-up)
REAR_WAYPOINTS = (                      # plan (x, y) LEFT half, mastoid node -> rack start at y = 50
    (REAR_START[0], REAR_START[1]),
    (-72.0, 84.0),
    (-86.0, 72.0),
    (-99.0, 59.0),
    (-106.0, 52.5),
)                                       # offset for the band's LOWER edge (11 mm forward, 10 down): the head is widest at ear level
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
NAPE_SPRING_WELL = (11.0, 4.5)                          # dia x depth in the dial's OUTER face (spring sits outside, pushes the dial in)
NAPE_RATCHET_R = (17.0, 21.0)          # ring on the body's outer wall face, teeth on the dial's inner face
NAPE_RATCHET_H = 1.0
NAPE_DIAL_W0 = NAPE_BODY_W1 + NAPE_RATCHET_H + 0.2   # 6.0 dial inner face; its teeth reach down to 5.0, into the body ring (4.8..5.8)
NAPE_RATCHET_TEETH = 24
NAPE_RATCHET_DIR = -1                                   # flip if it clicks when loosening and locks when tightening
NAPE_RELEASE_TRAVEL = 1.5                               # pull the ribs out this far to disengage
NAPE_KEY_RIBS = (18.0, 3.0, 10.0, 9.5)                  # length, width, height, +/- offset v: pinch these through the window and pull
NAPE_NUT_STACK = 6.0                                    # washer + M5 nyloc outside the spring
NAPE_KEY = (28.0, 13.0, 2.5)                            # key cap ring OD, ID, thickness (screwed to the dial face, carries the ribs)
NAPE_KEY_SCREWS = ((11.5, 0.0), (-11.5, 0.0))
NAPE_COVER_W0 = NAPE_DIAL_W0 + NAPE_DIAL_T - NAPE_SPRING_WELL[1] + NAPE_SPRING["working"] + NAPE_NUT_STACK + 0.5   # 25.0 cover inner face
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

COUPLER_LEN = 2 * PORT_PLUG_LEN          # spare double-male post
BRACKET_ARM = (POD_PORT_Y - NODE_OUT_Y, 20.0, 6.0)   # inboard reach, height, thickness of the pod bracket arm
BRACKET_TONGUE = (20.0, 20.0, 6.0)       # plate against the node's outer face, one M3
APEX_FILLET = 3.0
NECK_PIVOT = (-15.0, 0.0, -45.0)


def report() -> str:
    L = [
        "vp0.6 canon",
        f"  head: width {HEAD.width_mm} | length {HEAD.length_mm} | phantom perimeter {HEAD.plan_perimeter():.0f}",
        f"  pod: shell OD {DISH_OD}, ring {RING_H} + dome {DOME_SAG} = {POD_THICK} thick; rim {POD_RIM_Y - HEAD.width_mm/2:.1f} mm off the skull; dome f/D {DOME_FOCAL/DISH_OD:.2f}",
        f"  cradle: band {CRADLE_H}x{CRADLE_T} at z {CRADLE_Z}, foam {CRADLE_FOAM}; sides y {CRADLE_SIDE_Y}, forehead x {CRADLE_FRONT_X:.1f}; temple node x {TEMPLE_NODE_X}, rear node x {REAR_NODE_X} (W {REAR_NODE_W})",
        f"  brow hinge {BROW_HINGE}; rear halves leave the rear nodes at {REAR_START}",
        f"  overall width at the dome vertices: {2*POD_OUT_Y:.0f} mm; band centreline y {POD_PORT_Y}",
        f"  ports {POD_PORT_ANGLES}; pin {PIN_DIA} mm nail in double shear; cast sockets {CAST_SOCKETS}",
        f"  crown: hinge plugs in the top ports, bolt axis z {CROWN_HINGE_Z:.1f}; ribbon {CROWN_W}x{CROWN_T} to apex {CROWN_APEX_Z:.1f}",
        f"  brow: centre {BROW_CENTER_W} at x {BROW_X_IN:.1f}, wings hinged on the temple nodes, tilt {BROW_TILT}",
        f"  rear: halves from the rear nodes, tilt {REAR_TILT:.1f}, nape z {REAR_BACK_Z}; PULL dial Ø{NAPE_DIAL_D}, spring {NAPE_SPRING['note']}, housing w -5..{NAPE_COVER_W0 + 3.0:.1f}",
        f"  brackets: arm reach {BRACKET_ARM[0]:.1f} mm; strap on the cradle; pod ports 135/250/300 free for add-ons",
    ]
    return "\n".join(L)


if __name__ == "__main__":
    print(report())
