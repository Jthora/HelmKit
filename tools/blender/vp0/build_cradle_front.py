#!/usr/bin/env -S blender --background --python
"""
build_cradle_front.py -- vp0.8 cradle front U: forehead band, side bars, hub + rear nodes.

30 x 5 chamfered ribbon in the horizontal plane z = 55 (band z 40..70, above
the ears) from the left rear node around the forehead to the right rear node,
with a 3 mm doubler on the outer face around each hub node (a disk hit puts
about 6 N.m into that node). Nodes:
  hub node   on the disk axis: three M3 through-holes for the NEXUS (heads
             under the foam), a pin lug above the visor ring (the keeper saddle
             bolts through it), 8.3 socket from the top (crown arch coupler)
  rear node  tapered tenon socket for the rear half (nail), 8.3 socket from the
             top (antenna pylon)
Strap slot pairs behind the hub nodes. Cables run on the inside under the foam.
Print: upside down (top edge, node tops and lug tops on the bed), PETG. Qty: 1.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import bpy  # type: ignore
import vp0lib as L
import canon as C
from mathutils import Matrix, Vector  # type: ignore

UP = Vector((0.0, 0.0, 1.0))
PRINT_ROT = L.ROT_FLIP
NOTES = ["print upside down (top edge, node tops and pin lugs on the bed); PETG; brim; no supports",
         "nexus: three M3 x 30 through each hub node, heads under the foam; index nail 3.2 x 30 + spring in the pin lug",
         f"sockets: {C.CYL_SOCKET_BED_D} mm x {C.CYL_DEPTH} (bed-face size, d1 v2); hub top = spare (plug), rear top = pylon; M3 cross-bolt or nail at {C.CYL_PIN_Z} mm",
         f"rear halves: tenon into the rear node, {C.PIN_DIA} mm nail through node and tenon along Y, epoxy",
         "foam: forehead 70x26x10, sides 40x26x10, 6 mm under the nodes; cables under the foam"]
H2, T2 = C.CRADLE_H / 2, C.CRADLE_T / 2
NODE_Y = (C.NODE_IN_Y + C.NODE_OUT_Y) / 2
NODE_T = C.NODE_OUT_Y - C.NODE_IN_Y


def centreline():
    left = list(C.CRADLE_WAYPOINTS)
    right = [(x, -y) for (x, y) in reversed(left[:-1])]
    samp = L.catmull_rom(left + right, samples_per_seg=16)
    return L.resample_polyline([Vector((x, y, C.CRADLE_Z)) for (x, y) in samp], 2.0)


def tenon_frame(side):
    o = Vector((C.REAR_START[0], side * C.REAR_START[1], C.REAR_START[2]))
    return L.frame(o, (0.0, -side, 0.0), C.REAR_T_IN)


def tenon_poly(clear=0.0, side=+1):
    """Tenon outline in (along T, along W). The W+ face (the band's top edge: on the bed in both prints) is straight; only the
    W- face tapers, from the mouth half-height to the tip's lower half-height, so neither print has an overhang under the tenon."""
    t, mouth_h, depth, tip_lo = C.CRADLE_TENON
    h = mouth_h / 2 + clear
    return [(-1.0, -h), (depth + clear, -(tip_lo + clear)), (depth + clear, h), (-1.0, h)]


def sbox(name, x0, x1, y0, y1, z0, z1, side, fillet=None):
    b = L.add_box(name, ((x0 + x1) / 2, side * (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0))
    if fillet:
        L.fillet(b, width=fillet)
    return b


PRINT_UP = (0.0, 0.0, -1.0)          # the cradle prints inverted: every Y-axis hole is horizontal, its roof points world -Z


def ycyl(name, x, z, side, r, y0, y1, verts=24, rot=0.0, td=False):
    """Cylinder along Y; `rot` turns its vertex ring so no vertex sits exactly on a cut plane's tangent line.
    td=True: a teardrop toward the print's up (v0.17) for holes that print horizontal."""
    if td:
        return L.add_teardrop(name, (x, side * (y0 + y1) / 2, z), r, y1 - y0, (0.0, 1.0, 0.0), PRINT_UP, verts=verts)
    M = Matrix.Translation((x, side * (y0 + y1) / 2, z)) @ Matrix.Rotation(math.radians(rot), 4, "Y")
    return L.add_cyl_local(name, M, (0.0, 0.0, 0.0), r, y1 - y0, axis="Y", verts=verts)


def zcyl(name, x, y, side, r, z0, z1, verts=32):
    return L.add_cyl(name, (x, side * y, (z0 + z1) / 2), r, z1 - z0, axis="Z", verts=verts)


def spine_runs(pts, into=0.0):
    """Free spans of the band between the nodes: left rear-to-hub, the front arc, right hub-to-rear (world x limits with 0.5 clearance).
    `into` > 0 extends each span that far INTO the solid nodes (Track P fasteners plan: the channel ends 3 mm inside the node, so the
    rope is potted into the block instead of stopping 2 mm short of where a crack would start). The cover strips use the default."""
    hx, hl = C.HUB_NODE
    rx, rl = C.REAR_NODE
    x_hub0, x_hub1 = hx - hl / 2 - 0.5 + into, hx + hl / 2 + 0.5   # the FRONT run does not enter the hub nodes: with its floor-deep wedge the entry left a 5.4 mm lip cantilevered off each node face (QIDI 'floating cantilever', 2026-09-25)
    x_rear1 = rx + rl / 2 + 0.5 - into
    left = [p for p in pts if p.y > 0 and x_rear1 <= p.x <= x_hub0]
    front = [p for p in pts if p.x >= x_hub1]
    right = [p for p in pts if p.y < 0 and x_rear1 <= p.x <= x_hub0]
    spine_runs.front_ref = front
    return [r for r in (left, front, right) if len(r) >= 3]


spine_runs.front_ref = None


def spine_stations(pts):
    """World points on the band centreline where the sensor bar fastens (two pins, one tap): the spine run is a closed
    tunnel there (Track P)."""
    run = front_run(pts, C.PAD_FRONT["half_arc"] + 10.0)
    out = []
    for s_ in tuple(C.SENSOR_BAR["pins_s"]) + (0.0,):
        p, Tv, N = arc_point(run, s_)
        out.append((Vector((p.x, p.y, 0.0)), Vector((Tv.x, Tv.y, 0.0)).normalized()))
    return out


def channel_pts(run):
    zc = (C.SPINE["z"][0] + C.SPINE["z"][1]) / 2 - C.CRADLE_Z
    return [Vector((p.x, p.y, p.z + zc)) for p in run]


def offset_outboard(run, d):
    """Points shifted outboard (away from the head) by d, using the local tangent and UP (N = T x UP points inboard)."""
    out = []
    for i, p in enumerate(run):
        a = run[max(i - 1, 0)]; b = run[min(i + 1, len(run) - 1)]
        Tv = (b - a).normalized()
        N = Tv.cross(UP).normalized()
        out.append(p - N * d)
    return out


def _front_poly(pts, x_min=60.0):
    """Front arc of a left -> right polyline (x > x_min), its cumulative arc length and the exact arc length of the y = 0 crossing."""
    front = [p for p in pts if p.x > x_min]
    acc = [0.0]
    for i in range(1, len(front)):
        acc.append(acc[-1] + (front[i] - front[i - 1]).length)
    s0 = None
    for i in range(len(front) - 1):
        ya, yb = front[i].y, front[i + 1].y
        if (ya >= 0.0 > yb) or (ya > 0.0 >= yb):
            t = ya / (ya - yb)
            s0 = acc[i] + t * (acc[i + 1] - acc[i])
            break
    if s0 is None:
        s0 = acc[min(range(len(front)), key=lambda i: abs(front[i].y))]
    return front, acc, s0


def _interp(front, acc, s):
    s = min(max(s, acc[0]), acc[-1])
    for i in range(len(acc) - 1):
        if acc[i] <= s <= acc[i + 1]:
            t = (s - acc[i]) / (acc[i + 1] - acc[i]) if acc[i + 1] > acc[i] else 0.0
            return front[i].lerp(front[i + 1], t)
    return front[-1].copy()


def front_run(pts, half_arc, step=2.0):
    """The front arc of the centreline within +/- half_arc of arc length from the y = 0 crossing, exact ends, ordered left -> right."""
    front, acc, s0 = _front_poly(pts)
    n = max(2, int(math.ceil(2.0 * half_arc / step)))
    return [_interp(front, acc, s0 - half_arc + 2.0 * half_arc * k / n) for k in range(n + 1)]


def arc_span(pts, s_a, s_b, step=2.0, x_min=60.0):
    """Exact points between arc positions s_a < s_b (relative to the y = 0 crossing, s > 0 toward -y), left -> right."""
    front, acc, s0 = _front_poly(pts, x_min)
    n = max(2, int(math.ceil((s_b - s_a) / step)))
    return [_interp(front, acc, s0 + s_a + (s_b - s_a) * k / n) for k in range(n + 1)]


def s_at_x(pts, x, side, x_min=30.0):
    """Arc position (relative to the y = 0 crossing) where the band centreline crosses world x on the given side (+1 left / -1 right)."""
    front, acc, s0 = _front_poly(pts, x_min)
    best = None
    for i in range(len(front) - 1):
        a, b = front[i], front[i + 1]
        if (a.y * side > 0 or b.y * side > 0) and ((a.x - x) * (b.x - x) <= 0.0) and a.x != b.x:
            t = (x - a.x) / (b.x - a.x)
            s = acc[i] + t * (acc[i + 1] - acc[i]) - s0
            if best is None or abs(s) > abs(best):      # the crossing farthest from the front (the side span, not a front wiggle)
                best = s
    return best


def band_bottom(x):
    return C.CRADLE_Z - C.CRADLE_H / 2 + C.cradle_rise(x)


def cable_channel_cuts(pts):
    """v0.13: the two combat cable channels in the band's bottom face (arc +/-s_start .. x_end) and the grooves up the outer face at x_end."""
    cc = C.CABLE_CHANNEL
    cuts = []
    for side in (+1, -1):
        s_end = s_at_x(pts, cc["x_end"] - cc["overrun"], side)          # the channel runs a little past the groove for the bend
        s_a, s_b = (s_end, -cc["s_start"]) if side > 0 else (cc["s_start"], s_end)
        run = arc_span(pts, s_a, s_b, x_min=30.0)
        pts_c = [Vector((p.x, p.y, band_bottom(p.x) + cc["d"] / 2 - 0.5)) for p in run]
        cuts.append(L.ribbon("cchan", pts_c, UP, [(cc["d"] / 2 + 0.5, cc["d"] / 2 + 0.5, cc["w"] / 2, cc["w"] / 2)] * len(pts_c)))
        # groove up the outer face at x_end, with a wider mouth at its foot so the cable can bend out of the channel
        p, Tv, N = arc_point(pts, s_at_x(pts, cc["x_end"], side), x_min=30.0)
        M = L.frame(Vector((p.x, p.y, 0.0)), N, Tv)
        z0, z1 = band_bottom(p.x) - 1.0, cc["groove_z"] + 1.0
        n_c = -(T2 - cc["d"] / 2 + 0.5)
        cuts.append(L.add_box_local("cgroove", M, (0.0, (z0 + z1) / 2, n_c), (cc["groove_w"], z1 - z0, cc["d"] + 1.0)))
        mw, mh = cc["mouth"]
        x_bias = -side * 1.5                                             # toward the channel side (the forehead is at larger x = left -> right ... local x runs left -> right)
        cuts.append(L.add_box_local("cmouth", M, (x_bias if side < 0 else -x_bias, (z0 + z0 + mh) / 2, n_c + 0.5), (mw, mh, cc["d"] + 2.0)))   # 1 mm further inboard than the groove: room for the bend
    return cuts


def arc_point(pts, s, x_min=60.0):
    """Exact point, tangent (left -> right) and inboard normal at arc distance s from the y = 0 crossing (s > 0 toward -y).
    x_min widens the polyline (30 reaches the side spans up to the hub nodes; the default 60 is the forehead arc)."""
    front, acc, s0 = _front_poly(pts, x_min)
    p = _interp(front, acc, s0 + s)
    Tv = (_interp(front, acc, s0 + s + 0.5) - _interp(front, acc, s0 + s - 0.5)).normalized()
    N = Tv.cross(UP).normalized()
    return p, Tv, N


def normal_cyl(name, p, N, r, d0, d1, verts=16, td=None):
    """Cylinder along the inboard normal N through p, from inboard offset d0 to d1 (negative = outboard).
    td = a world up vector: a teardrop toward it (v0.17) for holes that print horizontal."""
    if td is not None:
        return L.add_teardrop(name, Vector(p) + Vector(N) * ((d0 + d1) / 2), r, abs(d1 - d0), N, td, verts=verts)
    M = L.frame(p, N, (0.0, 0.0, 1.0))
    return L.add_cyl_local(name, M, (0.0, 0.0, (d0 + d1) / 2), r, abs(d1 - d0), axis="Z", verts=verts)


def make():
    pts = centreline()
    band = L.ribbon("cradle_front", pts, UP, [(H2 - 0.1, H2 - C.cradle_rise(p.x), T2, T2) for p in pts], chamfer=1.0)   # lower edge rises at the forehead, top edge stays planar (inverted print)
    Z = C.CRADLE_Z
    # strap slots first, on the plain ribbon (the solver dislikes them after the node unions)
    sh, sw = C.STRAP_SLOT
    for side in (+1, -1):
        for x in C.CRADLE_STRAP_X:
            # in the band's own frame at that station (tangent along, UP, normal through), so the slot is square to the band
            # and the chamfer frustums sit on its two faces; 0.45 along the tangent keeps the cutter off the 2 mm station grid
            i, pc = min(((i, p) for i, p in enumerate(pts) if side * p.y > 0), key=lambda ip: abs(ip[1].x - x))
            Tv = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            Ms = L.frame(Vector((pc.x, pc.y, Z - 0.5)) + Tv * 0.45, UP, Tv)
            L.cut(band, L.add_box_local("strap", Ms, (0.0, 0.0, 0.0), (sw + 0.3, C.CRADLE_T + 6.0, sh)))
            L.slot_chamfer(band, Ms, sw + 0.3, sh, C.CRADLE_T, C.STRAP_SLOT_CHAMFER)
    for side in (+1, -1):
        hx, hl = C.HUB_NODE
        w0, w1 = C.HUB_NODE_W
        L.union(band, sbox("hnode", hx - hl / 2, hx + hl / 2, C.NODE_IN_Y, C.HUB_NODE_OUT_Y, Z + w0, Z + w1, side, fillet=1.0))
        rx, rl = C.REAR_NODE
        w0, w1 = C.REAR_NODE_W
        L.union(band, sbox("rnode", rx - rl / 2, rx + rl / 2, C.NODE_IN_Y, C.NODE_OUT_Y, Z + w0, Z + w1, side, fillet=1.0))
    # spine channels: 4 x 4 grooves in the outer face at z 63..67 on every free span between the nodes (potted rope + flush cover)
    # Track P: the cradle prints upside down, so the groove's lower wall would be a 4 mm ledge printed in the air;
    # the section carries a 45-degree wedge below the groove (inside the band) that turns it into a printable overhang.
    spine_sec = L.groove_section(face=-T2, floor=C.SPINE["d"] - T2, over=-(T2 + 1.0), wh=C.SPINE["w"] / 2, depth=C.SPINE["d"])
    # the sensor bar's two pin sockets and centre tap sit right under the front run: there the groove is a closed
    # tunnel for 8 mm (a 1.5 mm printed skin on the outer face; its print-ceiling is a 2.5 mm bridge, no wedge needed)
    # so the wedge cannot cut into the sockets; 4 mm transitions either side. The cover strips skip these stations.
    stations = spine_stations(pts)
    for run in spine_runs(pts, into=C.SPINE_INTO_NODE):
        cpts = channel_pts(run)
        if run is not spine_runs.front_ref:
            L.cut(band, L.ribbon("spinech", cpts, UP, None, section=spine_sec))
            continue
        secs = []
        for p in cpts:
            d = min(((p.x - q.x) ** 2 + (p.y - q.y) ** 2) ** 0.5 for q, _ in stations)
            f = min(max((d - C.SPINE["tunnel_half"]) / C.SPINE["tunnel_ramp"], 0.0), 1.0)      # 0 inside the tunnel, 1 in the open groove
            # inside the tunnel the section is the 4 x 4 rectangle plus a 0.2 mm token wedge (its floor side stays 1.25 mm
            # above the pin sockets); it grows to the full 45-degree wedge over the ramp
            # the skin ends square (a step between two stations) rather than tapering to a knife edge over the ramp
            over = -(T2 - C.SPINE["skin"]) if d < C.SPINE["tunnel_half"] else -(T2 + 1.0)
            secs.append(L.groove_section(face=-T2, floor=C.SPINE["d"] - T2, over=over,
                                         wh=C.SPINE["w"] / 2, depth=0.2, mouth_deep=True))   # square groove on the front run, its 0.2 slope toward the mouth so the ceiling starts at the body (2026-09-25): a floor-deep wedge starts its roof as a lip along the whole front arc (QIDI "floating cantilever", 85 mm by its own rule) and a mouth-deep one flares into the sensor-bar sockets. Square, the ceiling is a 4 mm ledge held along its full length   # the front run keeps the floor-deep wedge: a mouth-deep one flares into the sensor-bar sockets (234 non-manifold edges, tried twice 2026-09-25)
        L.cut(band, L.ribbon("spinech", cpts, UP, None, section=secs))
    # cable bores along y through the hub nodes: coil feed at CX - 15 (in line with the flange bore), LED feed at CX + 15
    cb = C.CABLE_BORE
    for side in (+1, -1):
        L.cut(band, ycyl("cbore", C.CX - cb["dx"], cb["z"], side, cb["dia"] / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0, verts=20, td=True))
        L.cut(band, ycyl("lbore", cb["led_x"], cb["led_z"], side, cb["dia"] / 2, C.CRADLE_SIDE_Y - C.CRADLE_T / 2 - 2.0,  C.CRADLE_SIDE_Y + C.CRADLE_T / 2 + 2.0, verts=20, td=True))
    # v0.13 combat cable channels (bottom face + outer-face grooves at x 36), before the node unions like the strap slots
    for cutter in cable_channel_cuts(pts):
        L.cut(band, cutter)
    # v0.12 mounting features: pad-frame taps on the inner faces, sensor-bar pin sockets + tap on the outer front face
    run = front_run(pts, C.PAD_FRONT["half_arc"] + 10.0)
    for s_ in C.PAD_FRONT["screws_s"]:
        p, Tv, N = arc_point(run, s_)
        p = Vector((p.x, p.y, C.PAD_FRONT["screw_z"]))
        L.cut(band, normal_cyl("ftap", p, N, C.M3_TAP_DIA / 2, T2 - 5.5, T2 + 1.0))
    sb = C.SENSOR_BAR
    for s_ in sb["pins_s"]:
        p, Tv, N = arc_point(run, s_)
        p = Vector((p.x, p.y, sb["screw_z"]))
        L.cut(band, normal_cyl("bpin", p, N, (sb["pin"][0] + sb["pin_fit"][0]) / 2, -T2 - 1.0, -T2 + sb["pin"][1] + 0.5, verts=20, td=PRINT_UP))
    p, Tv, N = arc_point(run, 0.0)
    L.cut(band, normal_cyl("btap", Vector((p.x, p.y, sb["screw_z"])), N, C.M3_TAP_DIA / 2, -T2 - 1.0, -T2 + 5.0))
    for side in (+1, -1):
        for (x, z) in C.PAD_HUB["screws"] + C.PAD_REAR["screws"]:
            L.cut(band, ycyl("ptap", x, z, side, C.M3_TAP_DIA / 2, C.NODE_IN_Y - 1.0, C.NODE_IN_Y + 5.0, verts=12))
    # nexus bolt holes for both sides first, one combined cutter per side (the solver is order-sensitive here):
    # M3 clearance through the node + hex nut pocket on the INNER face (the nut sits flush under the foam)
    af, pdep = C.NEXUS_NUT_POCKET
    for side in (+1, -1):
        tool = None
        for (x, z) in C.NEXUS_BOLTS:
            c = ycyl("nbolt", x, z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0, td=True)
            nut = L.add_hex_prism("nut", (x, side * C.NODE_IN_Y, z), af, 2 * pdep, axis="Y")
            nut.matrix_world = Matrix.Translation((x, 0.0, z)) @ Matrix.Rotation(math.radians(7.0), 4, "Y") @ Matrix.Translation((-x, 0.0, -z)) @ nut.matrix_world
            L.apply_transform(nut)
            L.union(c, nut)
            tool = c if tool is None else (L.union(tool, c) or tool)
        L.cut(band, tool)
    md, mdep = C.SOCKET_MOUTH_STEP
    for side in (+1, -1):
        # sockets: hub top (spare), rear top (pylon); cross holes along Y; mouth relief on the bed faces
        sx, sy = C.HUB_SOCKET
        L.cut(band, zcyl("hsock", sx, sy, side, C.CYL_SOCKET_BED_D / 2, Z + C.HUB_NODE_W[1] - C.CYL_DEPTH, Z + C.HUB_NODE_W[1] + 1.0))
        L.cut(band, zcyl("hmouth", sx, sy, side, md / 2, Z + C.HUB_NODE_W[1] - mdep, Z + C.HUB_NODE_W[1] + 1.0, verts=40))
        L.cut(band, ycyl("hcross", sx, C.HUB_CROSS_Z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0, td=True))
        sx, sy = C.REAR_SOCKET
        L.cut(band, zcyl("rsock", sx, sy, side, C.CYL_SOCKET_BED_D / 2, Z + C.REAR_NODE_W[1] - C.CYL_DEPTH, Z + C.REAR_NODE_W[1] + 1.0))
        L.cut(band, zcyl("rmouth", sx, sy, side, md / 2, Z + C.REAR_NODE_W[1] - mdep, Z + C.REAR_NODE_W[1] + 1.0, verts=40))
        L.cut(band, ycyl("rcross", sx, Z + C.REAR_NODE_W[1] - C.CYL_PIN_Z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.NODE_OUT_Y + 2.0, td=True))
        # v0.15: harness groove across the node's rear face (y NODE_IN_Y -> the rear half's inner face) at z 45
        ng = C.NODE_CABLE_GROOVE
        gy0, gy1 = ng["y"]
        gz = ng["z_L"] if side > 0 else ng["z_R"]
        # Track P: rectangle plus a wedge below it (the groove's lower wall would face down in the upside-down print)
        xo, xfl = rx - rl / 2 - 1.0, rx - rl / 2 + ng["d"]
        # The wedge's deep point is at the MOUTH, not the floor (2026-09-25). With the slope deepest at the floor, the groove's
        # print-upper wall rose inward from the face, and its first layer was a 0.15 mm sliver on the face plane over the open
        # mouth: QIDI Studio's "floating regions" warning on the cradle, found by layer_islands.py. Deepest at the mouth, the
        # roof rises from the floor toward the face and every layer of it grows out of the node's body. The mouth is 3.5 taller.
        gpoly = [(xfl, gz + ng["w"] / 2), (xo, gz + ng["w"] / 2), (xo, gz - ng["w"] / 2 - (xfl - xo)), (xfl, gz - ng["w"] / 2)]
        ylo, yhi = sorted((side * (gy0 - 1.0), side * gy1))
        Mg = Matrix.Rotation(math.radians(90.0), 4, "X")          # local y -> world z, local z -> world -y
        L.cut(band, L.extrude_polygon("hgroove", gpoly, yhi - ylo, Mg, z0=-yhi))
        # rear-half tenon slot + nail
        t = C.CRADLE_TENON[0] + 0.4
        # v0.18 (2026-11-10): the slot is the tenon swept straight back out past the node's face. Cut only to the tenon's own shape,
        # its lower half began up to 9 mm INSIDE the node (the tenon goes in at 47 deg, the face is vertical): the tenon fitted in its
        # final place but had no path to it (simulated insertion: 120-350 mm3 of solid in the way, from every direction tried).
        _, mouth_h, depth, tip_lo = C.CRADLE_TENON
        h, c = mouth_h / 2 + 0.2, 0.2
        slot = [(-16.0, -h), (-1.0, -h), (depth + c, -(tip_lo + c)), (depth + c, h), (-16.0, h)]
        L.cut(band, L.extrude_polygon("tslot", slot, t, tenon_frame(side), z0=-t / 2))
        pz = C.REAR_START[2] + 6.0 * C.REAR_T_IN[2]
        L.cut(band, ycyl("tpin", C.TENON_PIN_X, pz, side, C.PIN_DIA / 2 + 0.1, C.NODE_IN_Y - 2.0, C.NODE_OUT_Y + 2.0, td=True))
        L.cut(band, ycyl("tpinhead", C.TENON_PIN_X, pz, side, C.PIN_HEAD_DIA / 2, C.NODE_IN_Y - 1.0, C.NODE_IN_Y + C.PIN_HEAD_DEPTH, td=True))
        # v0.17: chamfer the hub node's lower inner edge over the ear
        ch = C.HUB_NODE_EAR_CHAMFER
        hx_, hl_ = C.HUB_NODE
        Mc = Matrix.Translation((hx_, side * C.NODE_IN_Y, Z + C.HUB_NODE_W[0])) @ Matrix.Rotation(math.radians(45.0), 4, "X")
        L.cut(band, L.add_box_local("earchamfer", Mc, (0.0, 0.0, 0.0), (hl_ + 4.0, ch * math.sqrt(2.0), ch * math.sqrt(2.0))))
    L.bed_plane(band, PRINT_ROT, 0.15)   # Track P: the band's top edge sat 0.1 above the node tops (H2 - 0.1); one bed plane
    return band


# ---------------------------------------------------------------------------------------------------------------------
# Sacrificial print frame (Track P, 2026-09-25). The cradle is a 176 x 200 U of 7 mm ribbon standing 48 mm on its edge
# with heavy nodes at the arm tips; four prints failed at the arm tips (settings, then the first layer). This is printed
# scaffolding, cut off afterwards: a 1.2 mm base frame along both faces of the band (0.4 mm gap), a tie bar straight across
# the open end of the U joining the two arm tips, vertical bracing fins standing on the frame along both faces, and small
# necks joining it all to the part every ~15 mm. Cut the necks (knife or scissors), lift the frame away. The necks stay
# clear of the spine channel and its flare, the strap slots, the cable-channel groove and the sensor-bar sockets.
# It is added only by the print export below; make() stays clean for the assembly and the fit checks.
FRAME_T, FRAME_W, FRAME_GAP = 1.2, 12.0, 0.4
FIN_H, FIN_T, NECK_W = 20.0, 1.2, 1.5
FIN_NECK_DEPTHS = (12.0, 18.0)         # below the bed plane in world z (up in the print): under the spine flare (world 59..67)


def print_frame(band):
    """Built as SEPARATE closed solids (strips, tie bar, necks, fins) that overlap the band and each other, joined into one
    mesh without booleans: the slicer merges overlapping solids per layer. Unioned, the pieces tore the boolean (400-1400
    non-manifold edges). Every piece stops exactly at the bed plane, coplanar with the part's bed face, which is harmless
    between separate solids."""
    pts = centreline()
    zb = max((band.matrix_world @ v.co).z for v in band.data.vertices)      # the bed plane, in world z
    Z = C.CRADLE_Z
    t2, g = C.CRADLE_T / 2.0, FRAME_GAP
    w_top, w_bot = zb - Z, zb - FRAME_T - Z                                 # slab from zb - FRAME_T to zb, in the ribbon's W
    pieces = []
    nodes = [(C.HUB_NODE, C.HUB_NODE_OUT_Y), (C.REAR_NODE, C.NODE_OUT_Y)]
    def node_at(p, margin=3.0):
        for (cx, ln), out_y in nodes:
            if abs(p.y) > 60 and cx - ln / 2 - margin < p.x < cx + ln / 2 + margin:
                return out_y
        return None
    # two strips (outer and inner face), each an explicit per-station section that steps out past a node's faces
    for sgn in (+1, -1):
        secs = []
        for p in pts:
            out_y = node_at(p)
            if out_y is None:
                a = t2 + g
            else:                                                           # past the node's face: outer (out_y) or inner (NODE_IN_Y)
                a = (out_y - abs(p.y)) + g if sgn > 0 else (abs(p.y) - C.NODE_IN_Y) + g
            b = a + FRAME_W
            n0, n1 = (a, b) if sgn > 0 else (-b, -a)
            secs.append([(n0, w_bot), (n1, w_bot), (n1, w_top), (n0, w_top)])
        pieces.append(L.ribbon("pstrip", pts, UP, None, section=secs))
    zc = zb - FRAME_T / 2.0
    xr = C.REAR_NODE[0] - C.REAR_NODE[1] / 2.0                              # the arm tips' rear faces (-58)
    yb = C.HUB_NODE_OUT_Y + g + FRAME_W
    pieces.append(L.add_box("ptie", (xr - g - 6.0, 0.0, zc), (12.0, 2 * yb, FRAME_T)))
    for side in (+1, -1):                                                   # tie arms back along both faces of the rear node
        for ya, yb_ in ((C.NODE_OUT_Y + g, C.NODE_OUT_Y + g + FRAME_W), (C.NODE_IN_Y - g - FRAME_W, C.NODE_IN_Y - g)):
            y0, y1 = sorted((side * ya, side * yb_))
            pieces.append(L.add_box("ptiearm", (xr - g - 6.0 + 16.0, (y0 + y1) / 2.0, zc), (32.0, y1 - y0, FRAME_T)))
        for yy in (C.NODE_IN_Y + 3.0, C.NODE_OUT_Y - 3.0):                  # necks from the tie bar to the node's rear face
            pieces.append(L.add_box("pneck", (xr - g / 2.0, side * yy, zc), (g + 1.6, NECK_W, FRAME_T)))
    cum = [0.0]
    for a_, b_ in zip(pts, pts[1:]):
        cum.append(cum[-1] + (b_ - a_).length)
    stations = spine_stations(pts)
    def clear_of_features(p):
        if any(((p.x - q.x) ** 2 + (p.y - q.y) ** 2) ** 0.5 < 8.0 for q, _ in stations):
            return False
        return not (40.0 < p.x < 66.0 or 30.0 < p.x < 42.0)                 # strap slots; cable-channel groove + mouth
    def tn(i):
        Tv = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        return Tv, Tv.cross(UP).normalized()
    # necks every ~15 mm along the free band, both faces: from 1.2 inside the band face (past its 1 mm chamfer) to the strip
    s_next = 5.0
    for i, p in enumerate(pts):
        if cum[i] < s_next or node_at(p, 1.0) is not None:
            continue
        s_next = cum[i] + 15.0
        Tv, N = tn(i)
        for sgn in (+1, -1):
            M = L.frame(Vector((p.x, p.y, zc)), UP, N * sgn)
            pieces.append(L.add_box_local("pneck", M, (t2 - 1.2 + (g + 1.2 + 1.0) / 2.0, 0.0, 0.0), (g + 1.2 + 1.0, NECK_W, FRAME_T)))
    # bracing fins every ~30 mm where the band is free, both faces, standing on the strips; two necks each to the band
    s_next = 12.0
    for i, p in enumerate(pts):
        if cum[i] < s_next or not clear_of_features(p) or node_at(p) is not None:
            continue
        s_next = cum[i] + 30.0
        Tv, N = tn(i)
        for sgn in (+1, -1):
            n0, n1 = t2 + g, t2 + g + FRAME_W
            M = L.frame(Vector((p.x, p.y, zb)), Tv * sgn, N * sgn)          # local x = out from the face, local y = world DOWN
            pieces.append(L.extrude_polygon("pfin", [(n0, 0.0), (n1, 0.0), (n0, FIN_H)], FIN_T, M, z0=-FIN_T / 2.0))
            for dz in FIN_NECK_DEPTHS:
                pieces.append(L.add_box_local("pfneck", M, ((t2 - 1.2 + n0 + 0.3) / 2.0, dz, 0.0), (n0 + 0.3 - (t2 - 1.2), 1.2, FIN_T)))
    # join: one mesh, many overlapping closed shells
    for ob in pieces:
        L.apply_transform(ob)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in pieces:
        ob.select_set(True)
    band.select_set(True)
    bpy.context.view_layer.objects.active = band
    bpy.ops.object.join()
    return band


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--frame", action="store_true", help="add the sacrificial print frame (opt-in since 2026-09-29: Jordan found it overkill; the first layers were the problem)")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    ob = make()
    notes = list(NOTES)
    if args.frame:
        print_frame(ob)
        notes.insert(0, "PRINTS WITH A SACRIFICIAL FRAME: a 1.2 mm base frame along both faces, a tie bar across the open end of the U and "
                        "20 mm bracing fins, joined to the band by small necks. After printing, cut the necks with a knife or flush "
                        "cutters, lift the frame away, and pare the neck stubs flush")
    L.finalize_and_export(ob, args.out, PRINT_ROT, notes)
