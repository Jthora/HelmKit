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
import vp0lib as L
import canon as C
from mathutils import Matrix, Vector  # type: ignore

UP = Vector((0.0, 0.0, 1.0))
PRINT_ROT = L.ROT_FLIP
NOTES = ["print upside down (top edge, node tops and pin lugs on the bed); PETG; brim; no supports",
         "nexus: three M3 x 30 through each hub node, heads under the foam; index nail 3.2 x 30 + spring in the pin lug",
         f"sockets: {C.CYL_SOCKET_D} mm x {C.CYL_DEPTH}; hub top = spare (plug), rear top = pylon; M3 cross-bolt or nail at {C.CYL_PIN_Z} mm",
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


def ycyl(name, x, z, side, r, y0, y1, verts=24, rot=0.0):
    """Cylinder along Y; `rot` turns its vertex ring so no vertex sits exactly on a cut plane's tangent line."""
    M = Matrix.Translation((x, side * (y0 + y1) / 2, z)) @ Matrix.Rotation(math.radians(rot), 4, "Y")
    return L.add_cyl_local(name, M, (0.0, 0.0, 0.0), r, y1 - y0, axis="Y", verts=verts)


def zcyl(name, x, y, side, r, z0, z1, verts=32):
    return L.add_cyl(name, (x, side * y, (z0 + z1) / 2), r, z1 - z0, axis="Z", verts=verts)


def spine_runs(pts):
    """Free spans of the band between the nodes: left rear-to-hub, the front arc, right hub-to-rear (world x limits with 0.5 clearance)."""
    hx, hl = C.HUB_NODE
    rx, rl = C.REAR_NODE
    x_hub0, x_hub1 = hx - hl / 2 - 0.5, hx + hl / 2 + 0.5
    x_rear1 = rx + rl / 2 + 0.5
    left = [p for p in pts if p.y > 0 and x_rear1 <= p.x <= x_hub0]
    front = [p for p in pts if p.x >= x_hub1]
    right = [p for p in pts if p.y < 0 and x_rear1 <= p.x <= x_hub0]
    return [r for r in (left, front, right) if len(r) >= 3]


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


def normal_cyl(name, p, N, r, d0, d1, verts=16):
    """Cylinder along the inboard normal N through p, from inboard offset d0 to d1 (negative = outboard)."""
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
            L.cut(band, L.add_box("strap", (x + 0.45, side * (C.CRADLE_SIDE_Y + 1.5), Z - 0.5), (sw + 0.3, C.CRADLE_T + 6.0, sh)))
    for side in (+1, -1):
        hx, hl = C.HUB_NODE
        w0, w1 = C.HUB_NODE_W
        L.union(band, sbox("hnode", hx - hl / 2, hx + hl / 2, C.NODE_IN_Y, C.HUB_NODE_OUT_Y, Z + w0, Z + w1, side, fillet=1.0))
        rx, rl = C.REAR_NODE
        w0, w1 = C.REAR_NODE_W
        L.union(band, sbox("rnode", rx - rl / 2, rx + rl / 2, C.NODE_IN_Y, C.NODE_OUT_Y, Z + w0, Z + w1, side, fillet=1.0))
    # spine channels: 4 x 4 grooves in the outer face at z 63..67 on every free span between the nodes (potted rope + flush cover)
    for run in spine_runs(pts):
        L.cut(band, L.ribbon("spinech", channel_pts(run), UP, [(C.SPINE["w"] / 2, C.SPINE["w"] / 2, C.SPINE["d"] - T2, T2 + 1.0)] * len(run)))
    # cable bores along y through the hub nodes: coil feed at CX - 15 (in line with the flange bore), LED feed at CX + 15
    cb = C.CABLE_BORE
    for side in (+1, -1):
        L.cut(band, ycyl("cbore", C.CX - cb["dx"], cb["z"], side, cb["dia"] / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0, verts=20))
        L.cut(band, ycyl("lbore", cb["led_x"], cb["led_z"], side, cb["dia"] / 2, C.CRADLE_SIDE_Y - C.CRADLE_T / 2 - 2.0, C.CRADLE_SIDE_Y + C.CRADLE_T / 2 + 2.0, verts=20))
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
        L.cut(band, normal_cyl("bpin", p, N, (sb["pin"][0] + sb["pin_fit"][0]) / 2, -T2 - 1.0, -T2 + sb["pin"][1] + 0.5, verts=20))
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
            c = ycyl("nbolt", x, z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0)
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
        L.cut(band, zcyl("hsock", sx, sy, side, C.CYL_SOCKET_D / 2, Z + C.HUB_NODE_W[1] - C.CYL_DEPTH, Z + C.HUB_NODE_W[1] + 1.0))
        L.cut(band, zcyl("hmouth", sx, sy, side, md / 2, Z + C.HUB_NODE_W[1] - mdep, Z + C.HUB_NODE_W[1] + 1.0, verts=40))
        L.cut(band, ycyl("hcross", sx, C.HUB_CROSS_Z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0))
        sx, sy = C.REAR_SOCKET
        L.cut(band, zcyl("rsock", sx, sy, side, C.CYL_SOCKET_D / 2, Z + C.REAR_NODE_W[1] - C.CYL_DEPTH, Z + C.REAR_NODE_W[1] + 1.0))
        L.cut(band, zcyl("rmouth", sx, sy, side, md / 2, Z + C.REAR_NODE_W[1] - mdep, Z + C.REAR_NODE_W[1] + 1.0, verts=40))
        L.cut(band, ycyl("rcross", sx, Z + C.REAR_NODE_W[1] - C.CYL_PIN_Z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.NODE_OUT_Y + 2.0))
        # rear-half tenon slot + nail
        t = C.CRADLE_TENON[0] + 0.4
        L.cut(band, L.extrude_polygon("tslot", tenon_poly(0.2, side), t, tenon_frame(side), z0=-t / 2))
        pz = C.REAR_START[2] + 6.0 * C.REAR_T_IN[2]
        L.cut(band, ycyl("tpin", C.TENON_PIN_X, pz, side, C.PIN_DIA / 2 + 0.1, C.NODE_IN_Y - 2.0, C.NODE_OUT_Y + 2.0, rot=7.5))
        L.cut(band, ycyl("tpinhead", C.TENON_PIN_X, pz, side, C.PIN_HEAD_DIA / 2, C.NODE_IN_Y - 1.0, C.NODE_IN_Y + C.PIN_HEAD_DEPTH, rot=7.5))
    return band


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
