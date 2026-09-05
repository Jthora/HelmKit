#!/usr/bin/env -S blender --background --python
"""
build_cradle_front.py -- vp0.7 cradle front U: forehead band, side bars, temple / hub / rear nodes.

30 x 5 chamfered ribbon in the horizontal plane z = 55 (band z 40..70, above
the ears) from the left rear node around the forehead to the right rear node.
Solid nodes on the band:
  temple node  external serrated lugs for the brow rail hinge (M3 x 40, wave
               washer), 8.3 socket from the bottom face (microphone boom)
  hub node     8.3 socket from the top (crown arch peg, M3 cross-bolt), yoke
               bolt holes (disk hanger on its outer face)
  rear node    tapered tenon socket for the rear half (nail), 8.3 socket from
               the top (antenna pylon)
Strap slot pairs behind the temple nodes. Cables run on the inside of the
band under the foam blocks.
Print: upside down (top edge and node tops on the bed), PETG. Qty: 1.
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
NOTES = ["print upside down (top edge, node tops and lug tops on the bed); PETG; no supports",
         f"brow rail hinge: {C.HINGE_BOLT} along Y through node and lugs, head under the temple foam",
         f"sockets: {C.CYL_SOCKET_D} mm x {C.CYL_DEPTH}; hub top = crown arch peg, rear top = pylon, temple bottom = mic boom; M3 cross-bolt or nail at {C.CYL_PIN_Z} mm",
         f"rear halves: tenon into the rear node, {C.PIN_DIA} mm nail through node and tenon along Y, epoxy",
         "foam: forehead 70x26x10, sides 40x26x10, 6 mm under the nodes; cables under the foam"]
H2, T2 = C.CRADLE_H / 2, C.CRADLE_T / 2
NODE_Y = (C.NODE_IN_Y + C.NODE_OUT_Y) / 2
NODE_T = C.NODE_OUT_Y - C.NODE_IN_Y
HUB_Y = (C.NODE_IN_Y + C.HUB_NODE_OUT_Y) / 2
HUB_T = C.HUB_NODE_OUT_Y - C.NODE_IN_Y


def centreline():
    left = list(C.CRADLE_WAYPOINTS)
    right = [(x, -y) for (x, y) in reversed(left[:-1])]
    samp = L.catmull_rom(left + right, samples_per_seg=16)
    return L.resample_polyline([Vector((x, y, C.CRADLE_Z)) for (x, y) in samp], 2.0)


def tenon_frame(side):
    o = Vector((C.REAR_START[0], side * C.REAR_START[1], C.REAR_START[2]))
    return L.frame(o, (0.0, -side, 0.0), C.REAR_T_IN)


def tenon_poly(clear=0.0, side=+1):
    t, mouth_h, depth, tip = C.CRADLE_TENON
    h = mouth_h / 2 + clear
    return [(-1.0, -h), (depth + clear, -(tip + clear)), (depth + clear, tip + clear), (-1.0, h)]


def sbox(name, x0, x1, y0, y1, z0, z1, side, fillet=None):
    b = L.add_box(name, ((x0 + x1) / 2, side * (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0))
    if fillet:
        L.fillet(b, width=fillet)
    return b


def ycyl(name, x, z, side, r, y0, y1, verts=24):
    return L.add_cyl(name, (x, side * (y0 + y1) / 2, z), r, y1 - y0, axis="Y", verts=verts)


def zcyl(name, x, y, side, r, z0, z1, verts=32):
    return L.add_cyl(name, (x, side * y, (z0 + z1) / 2), r, z1 - z0, axis="Z", verts=verts)


def make():
    pts = centreline()
    band = L.ribbon("cradle_front", pts, UP, [(H2 - 0.1, H2, T2, T2)] * len(pts), chamfer=1.0)
    Z = C.CRADLE_Z
    for side in (+1, -1):
        tx, tl = C.TEMPLE_NODE
        w0, w1 = C.TEMPLE_NODE_W
        L.union(band, sbox("tnode", tx - tl / 2, tx + tl / 2, C.NODE_IN_Y, C.NODE_OUT_Y, Z + w0 - 0.2, Z + w1, side, fillet=1.0))
        hx, hl = C.HUB_NODE
        w0, w1 = C.HUB_NODE_W
        L.union(band, sbox("hnode", hx - hl / 2, hx + hl / 2, C.NODE_IN_Y, C.HUB_NODE_OUT_Y, Z + w0, Z + w1, side, fillet=1.0))
        rx, rl = C.REAR_NODE
        w0, w1 = C.REAR_NODE_W
        L.union(band, sbox("rnode", rx - rl / 2, rx + rl / 2, C.NODE_IN_Y, C.NODE_OUT_Y, Z + w0, Z + w1, side, fillet=1.0))
        # brow hinge lugs on the temple node's outer face
        (lx0, lx1), (lz0, lz1) = C.LUG_X, C.LUG_Z
        L.union(band, sbox("lug_in", lx0, lx1, C.LUG_IN_Y[0], C.LUG_IN_Y[1], lz0, lz1, side, fillet=0.8))
        L.union(band, sbox("lug_out", lx0, lx1, C.LUG_OUT_Y[0], C.LUG_OUT_Y[1], lz0, lz1, side, fillet=0.8))
        (bx0, bx1), (bz0, bz1) = C.LUG_BASE
        L.union(band, sbox("lug_base", bx0, bx1, C.LUG_IN_Y[0], C.LUG_OUT_Y[1], bz0, bz1 + 0.5, side, fillet=0.8))
    for side in (+1, -1):
        # hinge bolt through node + lugs, head counterbored under the foam
        bx, by, bz = C.BROW_HINGE
        L.cut(band, ycyl("hbolt", bx, bz, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.LUG_OUT_Y[1] + 2.0))
        L.cut(band, ycyl("hhead", bx, bz, side, 3.3, C.NODE_IN_Y - 1.0, C.NODE_IN_Y + 2.2))
        # sockets: hub top, rear top, temple bottom; cross holes along Y
        md, mdep = C.SOCKET_MOUTH_STEP
        sx, sy = C.HUB_SOCKET
        L.cut(band, zcyl("hsock", sx, sy, side, C.CYL_SOCKET_D / 2, Z + C.HUB_NODE_W[1] - C.CYL_DEPTH, Z + C.HUB_NODE_W[1] + 1.0))
        L.cut(band, zcyl("hmouth", sx, sy, side, md / 2, Z + C.HUB_NODE_W[1] - mdep, Z + C.HUB_NODE_W[1] + 1.0, verts=40))
        L.cut(band, ycyl("hcross", sx, C.HUB_CROSS_Z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0))
        sx, sy = C.REAR_SOCKET
        L.cut(band, zcyl("rsock", sx, sy, side, C.CYL_SOCKET_D / 2, Z + C.REAR_NODE_W[1] - C.CYL_DEPTH, Z + C.REAR_NODE_W[1] + 1.0))
        L.cut(band, zcyl("rmouth", sx, sy, side, md / 2, Z + C.REAR_NODE_W[1] - mdep, Z + C.REAR_NODE_W[1] + 1.0, verts=40))
        L.cut(band, ycyl("rcross", sx, Z + C.REAR_NODE_W[1] - C.CYL_PIN_Z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.NODE_OUT_Y + 2.0))
        sx, sy = C.TEMPLE_SOCKET
        L.cut(band, zcyl("tsock", sx, sy, side, C.CYL_SOCKET_D / 2, Z + C.TEMPLE_NODE_W[0] - 1.2, Z + C.TEMPLE_NODE_W[0] + C.CYL_DEPTH))
        L.cut(band, ycyl("tcross", sx, Z + C.TEMPLE_NODE_W[0] + C.CYL_PIN_Z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.NODE_OUT_Y + 2.0))
        # yoke bolts + nail through the hub node, heads under the foam
        for (x, z) in C.YOKE_BOLTS:
            L.cut(band, ycyl("ybolt", x, z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0))
            L.cut(band, ycyl("yhead", x, z, side, 3.3, C.NODE_IN_Y - 1.0, C.NODE_IN_Y + 2.2))
        nx, nz = C.YOKE_NAIL
        L.cut(band, ycyl("ynail", nx, nz, side, C.PIN_DIA / 2 + 0.1, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0))
        L.cut(band, ycyl("ynhead", nx, nz, side, C.PIN_HEAD_DIA / 2, C.NODE_IN_Y - 1.0, C.NODE_IN_Y + C.PIN_HEAD_DEPTH))
        # rear-half tenon slot + nail
        t = C.CRADLE_TENON[0] + 0.4
        L.cut(band, L.extrude_polygon("tslot", tenon_poly(0.2, side), t, tenon_frame(side), z0=-t / 2))
        pz = C.REAR_START[2] + 6.0 * C.REAR_T_IN[2]
        L.cut(band, ycyl("tpin", C.TENON_PIN_X, pz, side, C.PIN_DIA / 2 + 0.1, C.NODE_IN_Y - 2.0, C.NODE_OUT_Y + 2.0))
        L.cut(band, ycyl("tpinhead", C.TENON_PIN_X, pz, side, C.PIN_HEAD_DIA / 2, C.NODE_IN_Y - 1.0, C.NODE_IN_Y + C.PIN_HEAD_DEPTH))
        # strap slots behind the temple node
        sh, sw = C.STRAP_SLOT
        for x in C.CRADLE_STRAP_X:
            L.cut(band, L.add_box("strap", (x + 0.45, side * C.CRADLE_SIDE_Y, Z + 4.5), (sw + 0.3, C.CRADLE_T + 2.0, sh)))
    for side in (+1, -1):
        bx, by, bz = C.BROW_HINGE
        sr = C.HINGE_SERR
        L.union(band, L.serration_solid("serr", (bx, side * C.LUG_OUT_Y[0], bz), (0.0, -side, 0.0),
                                        r_in=sr["r_in"], r_out=sr["r_out"], teeth=sr["teeth"], height=sr["height"], phase_deg=sr["phase_ear"]))
    return band


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
