"""
canon.py -- single source of truth for the HelmKit vp0.9 part set.

vp0.9 (2026-09-05): robustness + lean pass on v0.8.
  * Captive index pins (nail + glued C-collar + spring under an integral keeper
    gallows on the hub node), M3 thumbscrew disk lock into a tapped nexus ear,
    lanyard hole, M5-nut nape retainer, nexus in PETG.
  * Crown arch back on the hub node sockets (couplers); the nexus has no ports.
  * Visor reach fixed: the rails bolt to L-tabs on the panel ends; no sliders.
  * No detent bump in the bayonet (the lock screw holds), no rope grooves.
  * Nape for print one: a 10 mm PIN-LOCK body (one nail through both racks'
    tooth gaps); the compact dial stays as an upgrade on the same rear halves.
vp0.8 (2026-09-05): the NEXUS. One hub per side on the disk axis between the
cradle's hub node and the disk: a Ø60 flange bolted through the node (three
M3), a Ø32 spacer it clamps, the visor RING running on that spacer (the visor
rails pivot about the disk centre, locked by a spring-loaded index pin in 24
radial holes), the bayonet stalk for the disk (which now seats on the flange
face and is anti-rotation locked by a nail through the plate into an ear),
and three flat 4 x 20 tongue ports (front, top = crown arch, back). Temple
nodes, hinge lugs, yokes and the microphone are gone; pylons stay on the
rear nodes. The band carries a 3 mm doubler around the hub node.
vp0.7 (2026-09-05): centre-mounted enclosed disks, cradle carries everything.
  * Disks are ENCLOSED lenses (dome shell + screwed back plate) with a cavity
    for the bifilar coil apparatus, hung at their CENTRE on a printed
    quarter-turn bayonet stalk from a yoke on the cradle's hub node. No rim
    ports, no metal on the coil axis.
  * Crown arch feet are round pegs in the hub nodes (removable, no hinge).
  * Cylinder port standard on the cradle: 8 mm peg, 8.3 socket, 15 deep,
    M3 cross-bolt (or nail) at 7 mm. Sockets: hub tops (arch), rear tops
    (antenna pylons), temple bottoms (microphone boom / plug).
  * Brow: 160 mm centre panel on two RAILS hinged on external serrated lugs at
    the temple nodes (wave washer + nyloc: 15 deg notches, hard stops) with a
    pin-in-hole reach adjustment every 5 mm (0..45 mm).
  * Antenna pylons: faceted 140 mm blades on serrated knob-locked hinges.
  * Cables run on the inside of the band under the foam; no cable groove.
vp0.6 (2026-09-04): cradle architecture, floating pods on pinned brackets, pull dial.
vp0.5 (2026-09-04): protected knob, integral brow spars, deeper rounded ports.
vp0.4 (2026-09-04): reinforcement pass (dome-out shells, nail pins, rope spines).

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
M5_CLEAR_DIA = 5.4
M5_NUT_AF = 8.0
M5_NUT_T = 4.0
FIT_CLEAR = 0.15
FILLET_MM = 1.0
FILLET_SEGMENTS = 2

PIN_DIA = 3.2                 # nail shank ~3.0 mm slip fit (measure yours; epoxy fills the rest)
PIN_HEAD_DIA = 6.5            # counterbore for the nail head
PIN_HEAD_DEPTH = 2.0
ROPE_DIA = 3.5                # 2-4 mm rope / twine
SPINE_GROOVE = (ROPE_DIA + 0.4, 2.8)     # width x depth of the rope-and-epoxy spine groove (crown arch, rear halves)

# ---------------------------------------------------------------------------
# Cylinder port standard (cradle sockets for add-ons)
# ---------------------------------------------------------------------------

CYL_PEG_D = 8.0               # printed peg (a 3.2 mm nail down its core + epoxy makes it a composite)
CYL_SOCKET_D = 8.3
CYL_DEPTH = 15.0
CYL_PIN_Z = 7.0               # cross-bolt axis from the socket mouth (M3 through, or a nail)
CYL_PEG_LEN = CYL_DEPTH - 0.5

# ---------------------------------------------------------------------------
# Disk: enclosed lens on a central bayonet stalk
# ---------------------------------------------------------------------------

DISK_OD = 122.1               # physics: free-space wavelength at 2.455 GHz (the deferred 2.45 GHz Defender band, confirmed 2026-09-11), do not change
DISK_R = DISK_OD / 2.0
DISK_SHELL_T = 2.5
DISK_SAG = 10.0               # dome rise above the rim
DISK_PLATE_T = 2.0            # back plate (head side): clamped at six bosses and the bayonet boss
DISK_CAVITY = (110.0, 12.0)   # dia x depth for the coil apparatus (assumed; measure yours)
DISK_RIM_WALL = 3.0
DISK_N_RIM = DISK_PLATE_T + DISK_CAVITY[1] + DISK_SHELL_T     # 17.5: dome outer surface at the rim (n from the back face)
DISK_THICK = DISK_N_RIM + DISK_SAG                            # 27.5 at the vertex
DISK_IN_Y = 117.0             # back plate's head-side face SEATS on the nexus flange (= NEXUS_Y[1], asserted below): 40 mm off the skull
DISK_OUT_Y = DISK_IN_Y + DISK_THICK                           # 134.5 vertex
DISK_SCREWS = 6               # M3 x 8 into bosses at r 55.5, through the back plate
DISK_SCREW_R = 55.5
CABLE_BORE = dict(dia=5.0, dx=15.0, z=CZ + 24.5, led_x=36.0, led_z=CZ + 20.0)   # coil feed: one straight Ø5 bore along y at (CX - 15, z 59.5) through plate, flange and node into the band's inside;
#   LED feed: a Ø5 bore through the band just ahead of the hub node at (36, z 55); the cable then runs up under the rail root into the rail's underside groove (behind the disk from the side)
DISK_FOCAL = (DISK_R - DISK_RIM_WALL) ** 2 / (4.0 * DISK_SAG)
# bayonet: stalk from the yoke enters the back plate; lugs turn 90 deg into a groove inside a boss on the cavity side
STALK_D = 20.0
STALK_LUG = (6.0, 3.0, 3.0)   # tangential width, radial reach, height
STALK_LEN = 14.0              # beyond the nexus flange's outer face: 2 plate + 12 into the boss (the lock pin sits at n 10.8, 1.5 mm of tip above its hole)
STALK_BORE = 8.2              # axial bore for the knob shaft (Ø7.6), 2 mm into the flange; v0.14: 8.2 not 10 so the shaft is guided where the eccentric works
STALK_LUG_N = (4.0, 7.0)      # lug band measured from the disk back face (n)
BAYONET_BOSS = (34.0, 14.5)   # dia x height on the cavity side of the back plate: groove to 7.7, lock notch 9.0..12.6, 1.9 mm top
BAYONET_GROOVE = (13.6, 4.0, 7.8)   # groove outer radius, nominal floor n0, ceiling n1 (measured from the plate's head face); v0.14: +0.1 for the printed ceiling's sag over the 3.3 mm annular overhang (1.2 mm wall to the lock notch floor)
BAYONET_CAM = (4.5, 3.8)      # groove floor at the entry notch / at the stop: the turn cams the plate 0.2 mm onto the flange face (printed lugs at n 4..7)
BAYONET_STOP = dict(bump_deg=129.0, bump_w=3.0, flat_end=135.0)   # v0.16: stop bump centre (plate deg past the entry notch) and the end of the flat n_stop floor; the 6 mm lug spans 30 deg at r 11.5 and the bump 14 deg, so the lug centre stops at 108 deg = 107 deg of travel (was a notional 98 that the lug could not reach)
DISK_CABLE_SLOT_W = 5.0       # v0.16: the plate's cable exit is an arc SLOT at the bore radius spanning the lock travel, so the lead stays in the flange bore while the plate turns
BAYONET_LOCK = dict(pin_world_deg=90.0, pin_dia=3.2, pin_len=7.8, n=10.8, notch=(3.6, 2.5), notch_n=(9.0, 12.6))   # centre-knob disk lock: a 7.2 mm piece of 3.2 nail in a radial hole in the hollow stalk (top) is pushed 2 mm out into a notch in the boss bore by the knob shaft's eccentric; the notch sits 98 deg past the pin in the plate frame (locked pose)
DISK_KNOB = dict(d=28.0, t=5.0, dish=(32.0, 5.0), shaft_d=7.6, ecc=1.0, ecc_d=6.0, ecc_len=6.0, clip_n=16.0, clip=(14.0, 8.0, 2.0), apex_boss=(36.0, 7.0), hole=9.0)
#   v0.14: the eccentric is a Ø6 cylinder offset 1.0 (envelope 8.0 in the 8.2 bore): cam low r 2.0 / high r 4.0 against a 7.8 mm pin whose
#   retracted inner end sits at r 2.2 -> 1.8 mm into the 2.5 notch; file the pin's outer end round so the notch wall can push it back in
DISK_PRINT_FLAT = 0.15        # v0.14: the dome prints ON EDGE; a 0.15 mm flat on the rim (6 mm chord) is its first layer
DISK_UNLOCK_MARK = (2.0, 3.0) # notch (width, depth) in the dish rim at the bottom: knob index mark here = unlocked
#   knob flush in a dish at the dome apex; its Ø7.6 shaft runs down the axis through the coil's free centre into the stalk's Ø10 bore; the eccentric end
#   works the lock pin; a C-clip on the shaft inside the apex boss keeps it in the dome. Turn 180 deg = lock / unlock. No metal on the axis.

# ---------------------------------------------------------------------------
# Cradle: front U (forehead + sides, temple / hub / rear nodes) + rear halves + nape dial
# ---------------------------------------------------------------------------

CRADLE_H = 30.0
CRADLE_T = 7.0                           # 7: room for the 4 x 4 spine channel on the outer face (rope + steel epoxy, flush cover)
CRADLE_FOAM = 10.0
CRADLE_SIDE_Y = HEAD.width_mm / 2.0 + CRADLE_FOAM + CRADLE_T / 2.0      # 90.0 band centreline at the sides
CRADLE_FRONT_X = HEAD.phantom_semi[0] + CRADLE_FOAM + CRADLE_T / 2.0     # 113.75 band centreline at the forehead
CRADLE_Z = 55.0                          # horizontal hat line: band z 40..70, clears the top of the ear
CRADLE_WAYPOINTS = ((-56.0, CRADLE_SIDE_Y), (-20.0, CRADLE_SIDE_Y), (30.0, CRADLE_SIDE_Y), (66.0, CRADLE_SIDE_Y),
                    (94.0, 62.0), (CRADLE_FRONT_X, 0.0))   # plan, LEFT half, rear node -> forehead; mirrored for the right


def cradle_z(x: float) -> float:
    return CRADLE_Z


NODE_IN_Y = 84.0                         # node inner face (3.5 inside the band's inner face; 6 mm foam there)
NODE_OUT_Y = 97.0                        # hub / rear node outer face
HUB_NODE = (10.0, 40.0)                  # centre x, length: x -10..30: bolt pair at CX +/- 7, cable bores at CX +/- 15, 2.5 mm end walls
HUB_NODE_OUT_Y = 100.0                   # hub node 16 thick: the nexus stack (spool, ring) then passes ~8 mm outside the upper pinna
HUB_NODE_W = (-12.0, 15.0)               # bottom at z 43, ~6 mm above the top of the ear (ear phantom in the assembly)
REAR_NODE = (-45.0, 26.0)                # x -58..-32
REAR_NODE_W = (-33.0, 15.0)              # hangs 18 below the band to take the rear half's tenon
NODE_LEN = 26.0
REAR_NODE_X = REAR_NODE[0]
CRADLE_DOUBLER = ((-33.0, 53.0), (CRADLE_SIDE_Y + CRADLE_T / 2.0, CRADLE_SIDE_Y + CRADLE_T / 2.0 + 3.0), (50.0, 70.0))   # x, y, z: band 8 thick around the hub node (disk-hit bending)
# sockets (cylinder standard) in the nodes
HUB_SOCKET = (HUB_NODE[0], (NODE_IN_Y + HUB_NODE_OUT_Y) / 2.0)      # (10, 92) from the top face down: crown arch coupler
REAR_SOCKET = (REAR_NODE[0], (NODE_IN_Y + NODE_OUT_Y) / 2.0)        # (-45, 90.5) from the top face down: pylon peg
HUB_CROSS_Z = CRADLE_Z + HUB_NODE_W[1] - CYL_PIN_Z   # 63: spare-port cross-bolt
# ---- NEXUS: hub on the disk axis (CX, y, CZ) between the hub node and the disk ----
NEXUS_D = 68.0                           # flange diameter: 2.6 mm of rim outside the top bolt heads' counterbores
NEXUS_T = 8.0                            # flange thickness
NEXUS_Y = (HUB_NODE_OUT_Y + 9.0, HUB_NODE_OUT_Y + 9.0 + NEXUS_T)   # flange y 109..117 (spool plate 1 + ring 7 + washer 1); the disk back plate seats on its outer face
assert abs(DISK_IN_Y - NEXUS_Y[1]) < 1e-9
NEXUS_BOLTS = ((CX, CZ + 14.5), (CX - 7.0, CZ + 26.0), (CX + 7.0, CZ + 26.0))   # (x, z): M3 x 30 from OUTSIDE (head in a flange counterbore under the disk) through flange, spool hub / tower and node to a nut in the node's inner-face hex pocket; the top pair clears the arch socket by 1.1
NEXUS_HEAD_CBORE = (6.0, 3.5)            # head counterbore dia x depth on the flange's outer face
NEXUS_NUT_POCKET = (5.7, 2.4)            # hex pocket across-flats (M3 nut 5.5) x depth into the node's inner face: nothing proud under the foam
NEXUS_SPOOL = (44.0, 1.0, 36.0, 8.0)     # thrust plate dia x thickness (y 100..101) + hub dia x height (y 101..109, bearing on the flange face): the visor ring's bearing and the bolt-0 spacer. v0.14: no flange pocket (a 0.5 mm bed-side recess does not print)
NEXUS_RING = (44.0, 36.3, 7.0)           # visor ring OD, ID, thickness (y 101.05..108.05) on the spool hub; wave washer in the remaining 0.95; 7 mm bearing for the 118 mm lever
NEXUS_RING_Y0 = HUB_NODE_OUT_Y + 1.05
SPOOL_SPACER = dict(x_half=10.0, z0=CZ + 23.0, z1=CZ + 33.5, y1=HUB_NODE_OUT_Y + 8.9)   # block on the spool plate above the ring: the top bolts pass through it, it bears on the flange back
HUB_NOTCHES = dict(angles=(-17.0, -2.0, 13.0, 28.0, 43.0, 58.0), w=2.8, d=2.0, y=(HUB_NODE_OUT_Y + 3.0, HUB_NODE_OUT_Y + 7.0))   # v0.14: notches span the pawl's y (slot 103.25..106.45); they started at 104 before and the tip could not seat   # pawl notches in the hub's OD at the visor positions only (the pawl rides on the rail); none near bolt 0 at 90 deg
VISOR_PAWL = dict(slot=(3.2, 3.6), y0=HUB_NODE_OUT_Y + 3.25, r_in=16.0, r_spring=36.0, r_out=41.5, stem=(2.0, 1.4), tab_s=(38.0, 41.0), tab_h=15.0,
                  slider=(2.6, 3.0), tip_w=2.4, tip_r=(16.2, 18.5), body_r=26.0, spring="Ø3 x 10 compression, 9 mm working (or the printed-flexure slider)")
#   spring-loaded pawl slider in a tunnel along the rail axis inside the ring/gusset: tip into a hub notch, thumb tab out of the rail's top edge at r 36.5..39.5
STALK_FILLET = 1.2                                       # concave fillet ring at the stalk root (the stalk is the disk fuse; no sharp corner there)
NEXUS_LANYARD = dict(r=30.0, hole=4.0, angle=150.0)     # Ø4 hole through the flange up-back, for a cord loop to a strap slot
NEXUS_MATERIAL = "PETG"
# captive index pin: nail through a keeper gallows on the hub node, spring between the keeper and a glued C-collar
# visor: rails pivot about the disk axis on the nexus ring
RAIL_ANGLE = 13.0                        # nominal rail direction from the axis, deg above +x (= BROW_TILT, so the slider sleeve is axis-aligned)
RAIL_ROOT_R = 32.0                       # (legacy) the rail is now ring + gusset + bar, all 7 thick
RAIL_T = 7.0                             # rail thickness beyond the root; the root is the ring's 4.5
RAIL_Y0 = NEXUS_RING_Y0 + 0.05           # rail inner face: flush with the ring's inner face (prints flat on it)
RAIL_H = 20.0
# RAIL_S1 / RAIL_BOLTS_S (rail tip, tab bolts) are derived from the panel position below
VISOR_PARK_DEG = 43.0                    # parked visor = two 15-deg steps up (the third step sweeps the rail bar through the spool spacer); the assembly checks this pose
RAIL_GUSSET = (13.0, 40.0)               # rail root gusset: half-height at the ring's rim, radius where it has narrowed to the bar's 10
REAR_TENON_W0 = -17.0                    # rear half centreline leaves the rear node here (z 38)
CRADLE_TENON = (5.0, 26.0, 14.0, 3.0)    # y thickness, mouth height, depth, tip LOWER half-height: the W+ face (the band's top edge, on the bed) is straight, only the W- face tapers (v0.14: a symmetric taper was a 70-deg overhang)
TENON_PIN_X = REAR_NODE_X - NODE_LEN / 2.0 + 6.0          # -52: nail through node + tenon along Y
STRAP_SLOT = (14.0, 4.0)                 # W height x along-band width, through the band, centred at W +4.5; pairs 8 mm apart
CRADLE_STRAP_X = (49.0, 57.0)            # slot centres in front of the hub node (world x); slots sit below the spine channel (z 47.5..61.5)
REAR_STRAP_S = (24.0, 32.0)              # slot centres along the rear half from the node (arc mm)
CRADLE_FRONT_RISE = 12.0                 # the band's LOWER edge rises this much at the forehead (top edge stays at z 70): band bottom 12 mm above the eyebrow line


def cradle_rise(x: float) -> float:
    """Lower-edge rise of the cradle band at station x: 0 behind x 60, smooth to CRADLE_FRONT_RISE at the forehead."""
    t = (x - 60.0) / (CRADLE_FRONT_X - 60.0)
    t = min(1.0, max(0.0, t))
    return CRADLE_FRONT_RISE * t * t * (3.0 - 2.0 * t)


SPINE = dict(w=4.0, d=4.0, z=(CRADLE_Z + 8.0, CRADLE_Z + 12.0), cover_t=1.5, rope=2.0, rear_v=(-8.0, -4.0), rear_d=3.0, rear_cover_t=1.0, cover_clear=0.3)   # cover strips 0.3 narrower than the channel (curved strip in a curved channel)
#   rope-and-steel-epoxy spine: 4 x 4 channel in the band's outer face (z 63..67) between the nodes and around the front, 3 deep on the rear halves;
#   2 mm rope potted in metal-filled epoxy, flush printed cover strips glued in wet. The nodes themselves are solid blocks; each free span is bonded over its length.
# --- v0.12: pad frames (printed sensor carriers under the foam), the combat-trim sensor bar, headgear fit rule ---
PAD_FRAME = dict(plate_t=2.0, gap=0.1, screw="M3 x 8 countersunk (DIN 965) thread-forming from the head side, flush under the foam", countersink=(5.6, 1.1))   # 90-deg countersink for the DIN 965 M3 head (5.6 max): Ø5.6 at the face, 1.1 deep
PAD_FRONT = dict(half_arc=45.0, h=17.6, z=61.0, foam_t=8.0, screws_s=(-36.0, 36.0), screw_z=58.0,
                 windows=((0.0, "ppg"), (-25.0, "eda"), (25.0, "eda")),           # arc offsets of the carrier windows (s > 0 = right); flat carriers on an R~73 arc converge inboard, keep 4 mm at the plate
                 carrier_ppg=(26.0, 17.6, 21.6, 15.0, 4.0), carrier_eda=(16.0, 17.6, 12.0, 13.0, 0.8),   # (flange w, flange h, pocket w, pocket h, pocket depth)
                 flange_t=1.4, plug_inset=2.0, wall=1.3, chamfer=0.3)
#   carriers: a plug fills the plate window (epoxied), the flange sits on the head-side face, a tower rises to 1 mm under the foam
#   surface with the sensor pocket opening toward the skin; MAX30102 module in the centre, conductive-fabric EDA patches at +/-25
PAD_HUB = dict(x=(-9.0, 29.0), z=(44.0, 69.0), foam_t=4.0, screws=((-5.0, 48.0), (25.0, 65.0)), wall=1.2,   # screws 4 mm in from the edges so the countersinks stay inside the plate
               bct=(16.4, 14.0, 2.0, 19.5, 54.0),        # bone-conduction seat: pillar dia, transducer dia, recess, at (x, z); placeholder until the Mk1 transducer is chosen
               cable=(5.4, CX - 15.0, CZ + 24.5),        # coil-feed hole in line with the node bore
               cross=(7.5, HUB_SOCKET[0], HUB_CROSS_Z),  # clearance over the hub socket's cross-bolt: an M3 nut is 6.35 across corners
               bolt_relief=(4.6, 0.8))                   # Ø4.6 x 0.8 recesses on the band-side face over the nexus bolt tips (M3 x 30 ends 0.5 past the node face; 1.2 mm land to the cross hole)
PAD_REAR = dict(x=(-57.0, -33.0), z=(42.0, 68.0), foam_t=4.0, screws=((-53.0, 63.5), (-37.0, 63.5)), wall=1.3,   # plate down to z 42 (the node face runs to 23); screws above the tenon slot (z 25..51), countersinks inside the plate
                temp=(13.0, 10.0, 2.5, REAR_NODE_X, 50.0),                         # MAX30205 pocket w x h x depth at (x, z), occipital skin
                cross=(7.5, REAR_NODE_X, CRADLE_Z + REAR_NODE_W[1] - CYL_PIN_Z))   # clearance over the rear socket's cross-bolt (nut across corners 6.35)
SENSOR_BAR = dict(half_arc=50.0, n=24.0, w=20.0, z=58.0, standoff=0.8, wall=2.0, floor=4.0, chamfer=1.0, cavity_arc=34.0,
                  window=(18.0, 7.3, 17.3), recess=(25.4, 6.1, 18.5, 1.5), carrier=(25.0, 6.3, 18.3, 1.5),   # (half arc, normal from the band centreline .., depth)
                  camera=(0.0, 8.6), thermopile=(-11.0, 9.6), thermopile_tilt=15.0, ir_leds=((8.5, 5.2), (15.0, 5.2)), carrier_screws_s=(-21.5, 21.5),
                  exit=(30.0, 3.5, 5.3, 10.0), led_groove=(46.0, 20.0, 25.3, 2.2),            # cable exit: vertical Ø3.5 slot at arc +/-30 down the back wall, centred IN the wall (normal = CRADLE_T/2 + standoff + wall/2 = 5.3), out of the bar's bottom under the band edge
                  pins_s=(-42.0, 42.0), pin=(4.0, 5.0, 10.5), pin_fit=(0.1, 0.3), screw_z=58.5)   # pin_fit: (band socket, bar socket) clearance: snug in the band, loose in the bar      # pins clear the front pad taps at +/-36 (cut from the other face) and sit 2.3 above the bottom cable channel, 2.3 under the spine channel
#   curved hollow bar hugging the band's outer front face in combat trim: 24 x 20 section (z 48..68), 1 mm chamfers, 2 mm walls, 4 mm floor with a
#   window + flush recess for the sensor CARRIER (camera head, MLX90614 thermopile, two IR LEDs) screwed from below; LED pacer lane on the
#   underside along the front edge; two printed Ø4 pins (the shear fuse) + one M3 x 8 into the band's outer face; cable holes in the floor
CABLE_CHANNEL = dict(w=3.0, d=3.4, s_start=27.0, x_end=36.0, overrun=3.0, groove_w=4.0, mouth=(8.0, 8.0), groove_z=CZ + 20.0, cable_d=2.5)
#   v0.13 combat cable path: 3 x 3.4 channel in the band's BOTTOM face from arc +/-27 (3 mm short of the bar's exit holes at +/-30) around the corner
#   to x 33, then a 4 x 3.4 groove (8 x 8 mouth at its foot for the bend) up the outer face at x 36 into the LED bore (36, 55) and inside. Invisible from outside, prints as
#   an open groove on the inverted cradle. Present in both trims (same cradle print).
HEADGEAR = dict(thickness=25.0, z_min=-10.0, face=(70.0, 55.0))   # padded shell over the head phantom (face opening: up to z 70, +/- 55 wide); combat-trim parts must stay inside it
COMBAT_MAX_STANDOFF = 20.0        # sparring rule: nothing beyond this off the skull in combat trim except the sensor bar
FOAM_BLOCKS = dict(forehead=(90.0, 16.0, 10.0), side=(40.0, 26.0, 10.0), temple=(24.0, 26.0, 6.0), rear=(24.0, 40.0, 6.0))

# ---------------------------------------------------------------------------
# Crown arch (pegged into the hub nodes)
# ---------------------------------------------------------------------------

CROWN_W = 20.0                # narrower and thicker than v0.6; crown hits bend the arch in its own plane
CROWN_T = 7.0                 # 0.5 clear of the disk back face and the flange's inner plane
CROWN_PAD_T = 12.0
CROWN_LEG_Y = HUB_SOCKET[1]              # 92: leg centreline over the hub node's socket
CROWN_FOOT = (19.6, 13.0, 18.0)          # x (0.2 inside the ribbon width), y (centred on the socket), z: foot block with an 8.3 socket, joined to the hub socket by a coupler
CROWN_LEG_Z0 = CRADLE_Z + HUB_NODE_W[1] + CROWN_FOOT[2]    # 88: ribbon starts on top of the foot block
CROWN_BEND_Z = CROWN_LEG_Z0 + 20.0
CROWN_CROSS_Z = CRADLE_Z + HUB_NODE_W[1] + CYL_PIN_Z   # 77: cross-bolt through the foot socket and the coupler
SOCKET_MOUTH_STEP = (9.5, 0.6)          # dia x depth relief at socket mouths that print on the bed (elephant foot)
CROWN_FOOT_SOCKET_D = CYL_SOCKET_D + 0.2   # the arch foot's socket prints HORIZONTAL (arch on edge) and comes out oval: 0.2 more than the vertical cradle sockets
APEX_FLOOR_T = 2.0
APEX_SLEEVE = (34.0, 64.0, CROWN_T + 0.4 + 2.0 + 3.0)   # 13.4: channel + floor + 3 mm top
CROWN_APEX_Z = HEAD.vertex_z_mm + CROWN_PAD_T + APEX_FLOOR_T + 0.2 + CROWN_T / 2.0   # 152.2
CROWN_SUPER_N = 2.6
CROWN_OVERLAP = 40.0
CROWN_BAR_W = CROWN_W / 2.0
CROWN_SLOT_L = 26.0
CROWN_SLOT_W = M4_CLEAR_DIA
CROWN_SERR_PITCH = 2.0
CROWN_SERR_H = 0.6
CROWN_PAD = (40.0, 60.0, CROWN_PAD_T)

# ---------------------------------------------------------------------------
# Brow: centre panel on two hinged rails
# ---------------------------------------------------------------------------

BROW_TILT = 13.0
BROW_CENTER_W = 160.0
BROW_H = 50.0
BROW_T = 15.0
BROW_WALL = 2.0
BROW_Z0 = HEAD.brow_z_mm - 1.0   # 39: panel bottom at the eyebrow line
BROW_Z1 = BROW_Z0 + BROW_H
BROW_LID_T = 2.0
BROW_LED_WINDOW = (110.0, 6.0)
BROW_CAV_W = 116.0             # 22 mm solid ends carry the link pockets (12 deep at 55 deg) with 3.5 mm to the cavity
BROW_X_IN = CRADLE_FRONT_X + CRADLE_T / 2.0 + 2.0 + (CRADLE_Z + CRADLE_H / 2.0 - BROW_Z0) * math.tan(math.radians(BROW_TILT))   # 125.4
BROW_X_OUT = BROW_X_IN + BROW_T
_t = math.radians(BROW_TILT)
BROW_EX = (math.cos(_t), 0.0, math.sin(_t))
BROW_EZ = (-math.sin(_t), 0.0, math.cos(_t))
BROW_ORIGIN = (BROW_X_IN, 0.0, BROW_Z0)
BROW_LID_SCREWS = ((-40.0, 6.0), (40.0, 6.0), (-40.0, BROW_H - 6.0), (40.0, BROW_H - 6.0))   # faceplate screws into the top and bottom walls (cavity z 9..41)
BROW_CAV_H = BROW_H - 18.0     # 32: 9 mm top and bottom walls carry the faceplate screws
BROW_FACEPLATE_H = BROW_H - 6.0  # 44: the faceplate leaves 3 mm lips top and bottom
BROW_TOP_BEAD_R = 4.0
RAIL_S1 = 90.0                           # the rail ends here (x ~98); the LINK takes over: half-lap on the rail's inner half, then a bend inboard behind the panel
RAIL_LAP = (74.0, 90.0)                  # half-lap: the rail's inner half (y 101.1..104.6) is removed here, the link's lap fills it
RAIL_BOLTS_S = (77.0, 85.0)              # two M3 x 10 through the lap (heads counterbored on the rail's outer face) into the link
BROW_LINK = dict(angle=53.0, lap_t=3.5, pocket_depth=10.0, screws_d=(6.0,), screw_cbore=(6.2, 3.0))   # one M3 x 16 from the panel's underside; the pocket walls carry the bending   # bend angle inboard (plan), lap thickness, depth into the panel's back-face pocket, screw depths along the pocket
_bx = CX + RAIL_S1 * math.cos(_t); _bz = CZ + RAIL_S1 * math.sin(_t)
_xl = (_bx - BROW_X_IN) * math.cos(_t) + (_bz - BROW_Z0) * math.sin(_t)           # bend point in panel coordinates (negative: behind the back face)
BROW_LINK_LEN = -_xl / math.cos(math.radians(BROW_LINK["angle"]))                # bend point to the panel's back face along the link
BROW_POCKET_Y = RAIL_Y0 + RAIL_T / 2.0 - BROW_LINK_LEN * math.sin(math.radians(BROW_LINK["angle"]))   # |y| where the link enters the panel's back face
BROW_POCKET_Z = (CX - BROW_X_IN) * (-math.sin(_t)) + (CZ - BROW_Z0) * math.cos(_t)                    # panel-local z of the rail axis (the pocket centre)
RAIL_CHANNEL = (2.5, 2.5, 40.0, 72.0)    # LED cable groove in the rail's underside: tangential depth, y width, s range (bar only, ends before the lap); the link's bar carries it on

# serrated detent hinge (pylons): 24 teeth, 0.8 mm, wave washer + nyloc
HINGE_SERR = dict(r_in=5.0, r_out=8.3, teeth=24, height=0.8, phase_ear=7.9, phase_tongue=0.4)
HINGE_GAP = 6.9
HINGE_BOLT = "M3 x 30, wave washer + nyloc"

# ---------------------------------------------------------------------------
# Antenna pylons (rear node sockets)
# ---------------------------------------------------------------------------

PYLON_BASE = (18.0, 16.0, 8.0)          # block x, y, z on the rear node's top
PYLON_EAR_T = 6.0
PYLON_EAR_H = 21.0                      # 1 mm above the serration ring: the inverted print stands on the ear tops
PYLON_HINGE_Z = CRADLE_Z + REAR_NODE_W[1] + PYLON_BASE[2] + 12.0   # 90
PYLON_LEN = 140.0
PYLON_ROOT = (28.0, 6.0)                # blade root section (x, y) while inside the clevis
PYLON_SECTION = (28.0, 14.0)            # blade section after the flare
PYLON_TIP = (12.0, 6.0)
PYLON_FLARE = 22.0                      # distance from the hinge where the blade thickens
PYLON_ANGLE = 30.0                      # deg back from vertical, deployed
PYLON_WIRE_D = 3.0
PYLON_WALL = None                       # v0.14: the blade is modelled SOLID; the slicer's 10-15 % infill replaces the 2.4 mm hollow (a 23 mm bridge along the whole blade). Set 2.4 to hollow it again
PYLON_KNOB = (24.0, 8.0)                # dia, thickness of the printed lock knob (M3 nut pocket)
# ---------------------------------------------------------------------------
# Rear halves + enclosed pull dial
# ---------------------------------------------------------------------------

REAR_H = 36.0
REAR_T = 6.0
REAR_START = (REAR_NODE_X - NODE_LEN / 2.0, CRADLE_SIDE_Y, CRADLE_Z + REAR_TENON_W0)   # (-58, 90, 38) rear node's rear face
REAR_BACK_X = -112.0                     # 4 mm further back than v0.6: the compact housing's lower edge sits on the occipital bulge
REAR_BACK_Z = -20.0
REAR_TILT = math.degrees(math.atan2(REAR_START[2] - REAR_BACK_Z, REAR_START[0] - REAR_BACK_X))   # ~49 deg
REAR_W = (-math.sin(math.radians(REAR_TILT)), 0.0, math.cos(math.radians(REAR_TILT)))
REAR_MOUTH = REAR_START
REAR_T_IN = (math.cos(math.radians(REAR_TILT)), 0.0, math.sin(math.radians(REAR_TILT)))
REAR_WAYPOINTS = (
    (REAR_START[0], REAR_START[1]),
    (-72.0, 84.0),
    (-86.0, 72.0),
    (-101.0, 59.0),
    (-109.0, 52.5),
    (-112.0, 44.0),
)                                       # the band then runs straight along the nape to the rack start at |y| = RACK_Y0
RACK_LEN = 54.0                                         # racks reach ~16 past the centre so two pin-lock nails always find teeth (was 50)
RACK_Y0 = 35.0                                          # rack strip starts here (|y|); nominal fit
NAPE_TRAVEL = 7.0                                       # +/- mm at the nape (14 mm of circumference)
GEAR_MODULE = 1.25
GEAR_PA = 20.0
PINION_N = 10
PINION_PITCH_R = GEAR_MODULE * PINION_N / 2.0           # 6.25
PINION_W = 5.0
RACK_PITCH_W = PINION_PITCH_R
_p = math.pi * GEAR_MODULE
_n = int(RACK_LEN // _p)
RACK_SHIFT = (1.0 + (RACK_LEN - _n * _p) / 2.0 + _p - RACK_Y0) % _p   # 2.78: rack outline shifted so a tooth SPACE is centred on y = 0 at the nominal fit (pinion tooth / pinlock nail there)
# Enclosed dial (nape local frame: u = -Y, v = W up, w = outward; band mid-plane at w = 0)
NAPE_MODULE = "core"                                    # print one: 'core' (v0.15: the pin-lock block with the electronics junction bay behind it), 'pinlock' (block only), 'dial' = the compact pull dial
NAPE_PINLOCK_HOLES = (0.0, 0.5 * _p, _p, 1.5 * _p)      # u of the four vertical pin holes: whole-pitch settings use 0 and p, half-pitch ones p/2 and 3p/2 -> two nails, two teeth per rack
NAPE_PINLOCK_PIN = dict(dia=2.0, hole=2.2, hole_bottom=2.1, cbore=(5.0, 1.0), nail="2 x 50 nail or 2 mm rod")   # tooth space 2.1 at the pitch line; the holes overlap into a 4-lobe slot (1.0 waists); snug in the bottom wall, head flush in a counterbore
NAPE_HU, NAPE_HV = 60.0, 44.0                           # width = rack tip at the tightest (23) + end wall + margin; height = racks 36 + walls
NAPE_WALL = 2.5
NAPE_CH = 2.8                                           # channel half-thickness (racks are +/-2.5)
NAPE_LID_T = 2.2                                        # head-side lid: w -5.0 .. -2.8
NAPE_BODY_W1 = NAPE_CH + 2.0                            # 4.8 outer channel wall face
NAPE_PINLOCK_T = 2 * (NAPE_CH + 0.5) + 4.0              # 10.6: rack tunnels 6.6 tall (as in the dial body) with 2 mm skins
NAPE_PINION_W0 = -1.5                                   # pinion rests at w -1.5 .. 3.5 (moves inward on release)
NAPE_PINION_CAV_R = 8.2
NAPE_HUB_D = 14.0
NAPE_DIAL_D = 34.0                                      # was 44: the ribs are the grip, not the rim
NAPE_DIAL_T = 5.0
NAPE_SPRING = dict(od=9.5, free=12.7, working=6.5, wire=0.6, note="3/8 x 1/2 in compression spring (3/8 x 3/4 fits: housing grows 2.5 mm)")
NAPE_SPRING_WELL = (10.5, 1.5)                          # dia x depth seat in the dial's OUTER face (spring sits outside, pushes the dial in)
NAPE_RATCHET_R = (10.5, 14.5)          # ring on the body's outer wall face, teeth on the dial's inner face (2.3 outside the pinion cavity, 0.7 outside the lug slots)
NAPE_LUG_R = 8.0                                        # pinion drive lugs: centre radius
NAPE_LUG = (2.6, 3.0)                                   # radial x tangential
NAPE_RATCHET_H = 1.0
NAPE_DIAL_W0 = NAPE_BODY_W1 + NAPE_RATCHET_H + 0.2   # 6.0 dial inner face; its teeth reach down to 5.0, into the body ring (4.8..5.8)
NAPE_RATCHET_TEETH = 24
NAPE_RATCHET_DIR = -1                                   # flip if it clicks when loosening and locks when tightening
NAPE_RELEASE_TRAVEL = 1.5                               # pull the ribs out this far to disengage
NAPE_KEY_RIBS = (10.0, 3.0, 5.0, 8.5)                   # length (along v), width, height, +/- offset u: pinch these through the window and pull
NAPE_NUT_STACK = 4.0                                    # Ø12 x 4 retainer with an embedded M5 nut (sets the preload)
NAPE_KEY = (24.0, 12.0, 2.0)                            # key cap ring OD, ID, thickness (screwed to the dial face, carries the ribs)
NAPE_KEY_SCREWS = ((0.0, 9.0), (0.0, -9.0))             # at 90/270 deg: clear of the pinion lug slots at 0/120/240
NAPE_RETAINER = (12.0, 4.0, M5_CLEAR_DIA)               # dia, thickness, bore; an M5 nut sits in a hex pocket (3.2 deep) on its outer face (printed threads strip)
NAPE_COVER_W0 = NAPE_DIAL_W0 + NAPE_DIAL_T - NAPE_SPRING_WELL[1] + NAPE_SPRING["working"] + NAPE_NUT_STACK + 0.5   # 25.0 cover inner face
NAPE_COVER_T = 2.5
NAPE_WINDOW_D = 28.0
NAPE_AXLE = "M5 x 25 bolt: head epoxied to the lid; printed retainer threaded on the tip sets the spring preload"
NAPE_LID_SCREWS = ((-20.0, 0.0), (20.0, 0.0), (0.0, 18.0), (0.0, -18.0))
NAPE_COVER_SCREWS = ((-22.0, -18.0), (22.0, -18.0), (-22.0, 18.0), (22.0, 18.0))
NAPE_PAD = (48.0, 40.0, 10.0)

# ---------------------------------------------------------------------------
# v0.15 electronics integration: nape core base, core pods (nape / slab), belt pack, coil former, harness channels
# ---------------------------------------------------------------------------
# One helm, three ways to power it: belt pack only (base + cap, umbilical into the base), helm only (base + nape pod, or two slab
# pods on the rear sockets), or both (pod + umbilical). The base is the pin-lock block with a junction bay behind it: every helm
# cable ends on a small junction board there; a jumper goes to the pod, the umbilical goes down to the belt.
NAPE_CORE = dict(bay_d=12.0, wall=2.0, web_hole=4.0, web_u=22.0,                 # bay depth behind the pin-lock block; Ø4 harness holes through the block's web at u +/-22
                 pod_screws=((-20.0, 12.0), (20.0, 12.0)), boss=(6.0, 4.0),       # M3 taps in bosses on the bay's outer wall for the pod / cap
                 window=(16.0, 8.0, -14.0),                                     # jumper window through the outer wall: w x h at v
                 conn=(16.0, 10.0), umbilical=(8.0, 3.0),                       # umbilical connector window in the bottom (v-) wall; strain-relief hole dia and zip-tie slot
                 junction=(30.0, 20.0, 4.0), cap_t=2.0)                        # junction perfboard w x h on 3 mm standoffs; cap thickness (belt-only)
POD_NAPE = dict(inner=(58.0, 50.0, 20.0), wall=2.0, lid_t=2.0, rebate=1.0, lip=1.4, fillet=0.6, boss=6.0,       # u x v x w cavity: 1000 mAh LiPo (50 x 34 x 6) on the floor, Heltec on it (foam between), IMU / GSR / amp in the 16 mm +v strip
                rails=None, oled=("lid", 26.0, 14.0, -11.0), usb=(10.0, 7.0, 12.0),           # OLED window (face, w, h, u); USB window w x h at depth
                buttons=(12.4, 7.6, (-18.0, 0.0, 18.0), 11.0), slide=(9.5, 4.5),                # 12 mm tact switches: pocket, plunger hole, u positions on the +v wall at depth; slide-switch slot
                cable_window=("back", 16.0, 8.0, -14.0), mount=((-20.0, 12.0), (20.0, 12.0)))
POD_SLAB = dict(inner=(58.0, 18.0, 36.0), wall=2.0, lid_t=2.0, rebate=1.0, lip=1.4, fillet=0.6, boss=6.0,       # thin slab standing on a rear-node socket: Heltec on edge, or the LiPo + small boards
               rails=None, oled=("-v", 26.0, 14.0, -11.0, 0.7), usb=(10.0, 7.0, 15.0),
               buttons=(12.4, 7.6, (-18.0, 0.0, 18.0), 10.0), slide=(9.5, 4.5),
               cable_window=("-u", 12.0, 6.0, 6.0), mount=((-20.0, 0.0), (20.0, 0.0)))
SOCKET_FOOT = dict(plate=(50.0, 20.0, 4.0), taps=((-20.0, 0.0), (20.0, 0.0)))               # the pod's mounting holes onto an 8 mm peg (port standard) for a rear-node socket
BUTTON_CAP = dict(d=(10.0, 14.0), h=4.0, bore=(3.6, 2.0))                                   # small / large (tally) caps pressed onto the 3.5 mm tact plunger
BELT_PACK = dict(inner=(100.0, 65.0, 35.0), wall=2.5, lid_t=2.5, rebate=1.0, lip=1.8, fillet=0.8, boss=7.0, belt=(45.0, 4.5, 26.0),   # Heltec + 2x18650 + coil driver; belt slots w x h at +/-y
                 umbilical=(8.0, 3.0), usb=(10.0, 7.0, 14.0))
COIL_FORMER = dict(od=109.4, id=40.0, t=3.5, r0=22.0, r1=50.0, pitch=1.9, groove=(1.1, 0.8), back_groove=(1.4, 1.0),   # 0.8 mm ribs between turns, an 0.8 deep furrow (the pair stands proud, glued)
                   boss_hole=7.6, pin_hole=1.2)                                               # pancake former in the disk cavity: bifilar pair (2 x 24 AWG) in one spiral groove; 6 boss holes; the back grooves drop all four ends into the plate's cable hole
REAR_CABLE = dict(w=3.0, d=2.5, v=-13.0, s0=12.0, y_end=RACK_Y0 + 8.0, cover_t=1.0)   # v0.16: BELOW the strap slots (v -2.5..11.5) and the rack; the flipped right half carries it at +13           # harness channel on the rear halves' INNER face at v +9.5, from 10 mm behind the node to 8 mm short of the rack. The RIGHT half is the left print flipped over (its rack takes the lower tunnel), so on the right the channel sits at v -9.5 and the +W x-shift of a tilted band would carry a nearer start into the node: hence s0 10
NODE_CABLE_GROOVE = dict(w=3.0, d=2.5, z_L=CRADLE_Z + REAR_TENON_W0 - 9.0, z_R=CRADLE_Z + REAR_TENON_W0 + 10.0, y=(NODE_IN_Y, CRADLE_SIDE_Y - 2.4))   # groove across each rear node's rear face (y 84 -> 87.6): left at z 47.5 (above the tenon nail's counterbore), right at z 30 (the flipped half's channel is low); the foam-layer harness steps out to the rear half's inner face
ELECTRONICS_G = dict(heltec=12.0, lipo_1000=20.0, imu=3.0, gsr=6.0, amp=4.0, junction=5.0, wiring=15.0, transducer=8.0)   # reference masses for the balance report

REAR_SIDE_PAD = (50.0, 30.0, 12.0)

APEX_FILLET = 3.0
NECK_PIVOT = (-15.0, 0.0, -45.0)


def report() -> str:
    L = [
        "vp0.9 canon",
        f"  head: width {HEAD.width_mm} | length {HEAD.length_mm} | phantom perimeter {HEAD.plan_perimeter():.0f}",
        f"  disk: OD {DISK_OD}, {DISK_THICK} thick at the vertex, cavity {DISK_CAVITY}, back face {DISK_IN_Y - HEAD.width_mm/2:.1f} mm off the skull; dome f/D {DISK_FOCAL/DISK_OD:.2f}",
        f"  overall width at the vertices: {2*DISK_OUT_Y:.0f} mm; stalk {STALK_D} bayonet at the brain core",
        f"  cradle: band {CRADLE_H}x{CRADLE_T} at z {CRADLE_Z}, doubler {CRADLE_DOUBLER[0]}; hub node x {HUB_NODE} (y {NODE_IN_Y}..{HUB_NODE_OUT_Y}), rear node x {REAR_NODE}",
        f"  nexus ({NEXUS_MATERIAL}): flange Ø{NEXUS_D} x {NEXUS_T} at y {NEXUS_Y}, spool {NEXUS_SPOOL}, visor ring {NEXUS_RING}, {len(HUB_NOTCHES['angles'])} hub notches + rail pawl slider; centre-knob disk lock",
        f"  ports: {CYL_PEG_D} mm pegs in {CYL_SOCKET_D} sockets {CYL_DEPTH} deep at the hub top (crown arch coupler) and rear top (pylon)",
        f"  brow: panel {BROW_CENTER_W} at x {BROW_X_IN:.1f}, rails pivot on the disk axis at {RAIL_ANGLE} deg, fixed reach, tilt in 15 deg pin notches, park {VISOR_PARK_DEG} deg",
        f"  crown: couplers into the hub sockets, ribbon {CROWN_W}x{CROWN_T} from z {CROWN_LEG_Z0} to apex {CROWN_APEX_Z:.1f}",
        f"  pylons: {PYLON_LEN} mm blades on the rear nodes, hinge z {PYLON_HINGE_Z}, {PYLON_ANGLE} deg back",
        f"  rear: halves tilt {REAR_TILT:.1f}, nape z {REAR_BACK_Z}; nape module '{NAPE_MODULE}' (pinlock housing 10 mm deep; dial w -5..{NAPE_COVER_W0 + 3.0:.1f})",
    ]
    return "\n".join(L)


if __name__ == "__main__":
    print(report())
