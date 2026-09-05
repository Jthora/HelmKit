#!/usr/bin/env -S blender --background --python
"""
build_cradle_front.py -- vp0.8 cradle front U: forehead band, side bars, hub + rear nodes.

30 x 5 chamfered ribbon in the horizontal plane z = 55 (band z 40..70, above
the ears) from the left rear node around the forehead to the right rear node,
with a 3 mm doubler on the outer face around each hub node (a disk hit puts
about 6 N.m into that node). Nodes:
  hub node   on the disk axis: three M3 through-holes for the NEXUS (heads
             under the foam), a pin lug above the visor ring for the index nail,
             8.3 socket from the top (spare port)
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
    t, mouth_h, depth, tip = C.CRADLE_TENON
    h = mouth_h / 2 + clear
    return [(-1.0, -h), (depth + clear, -(tip + clear)), (depth + clear, tip + clear), (-1.0, h)]


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


def make():
    pts = centreline()
    band = L.ribbon("cradle_front", pts, UP, [(H2 - 0.1, H2, T2, T2)] * len(pts), chamfer=1.0)
    Z = C.CRADLE_Z
    # strap slots first, on the plain ribbon (the solver dislikes them after the node unions)
    sh, sw = C.STRAP_SLOT
    for side in (+1, -1):
        for x in C.CRADLE_STRAP_X:
            L.cut(band, L.add_box("strap", (x + 0.45, side * (C.CRADLE_SIDE_Y + 1.5), Z + 4.5), (sw + 0.3, C.CRADLE_T + 6.0, sh)))
    for side in (+1, -1):
        (dx0, dx1), (dy0, dy1), (dz0, dz1) = C.CRADLE_DOUBLER
        L.union(band, sbox("doubler", dx0, dx1, dy0 - 0.2, dy1, dz0, dz1 - 0.2, side, fillet=1.0))
        hx, hl = C.HUB_NODE
        w0, w1 = C.HUB_NODE_W
        L.union(band, sbox("hnode", hx - hl / 2, hx + hl / 2, C.NODE_IN_Y, C.HUB_NODE_OUT_Y, Z + w0, Z + w1, side, fillet=1.0))
        rx, rl = C.REAR_NODE
        w0, w1 = C.REAR_NODE_W
        L.union(band, sbox("rnode", rx - rl / 2, rx + rl / 2, C.NODE_IN_Y, C.NODE_OUT_Y, Z + w0, Z + w1, side, fillet=1.0))
        (lx0, lx1), (ly0, ly1), (lz0, lz1) = C.NEXUS_PIN_LUG
        L.union(band, sbox("pinlug", lx0, lx1, ly0 - 0.5, ly1, lz0, lz1 - 0.2, side, fillet=0.8))
    # nexus bolt holes for both sides first, one combined cutter per side (the solver is order-sensitive here)
    for side in (+1, -1):
        tool = None
        for i, (x, z) in enumerate(C.NEXUS_BOLTS):
            c = ycyl("nbolt", x, z, side, C.M3_CLEAR_DIA / 2, C.NODE_IN_Y - 2.0, C.HUB_NODE_OUT_Y + 2.0)
            if i > 0:     # the bottom bolt sits 3.5 mm above the node's edge: its head stays proud under the foam
                L.union(c, ycyl("nhead", x, z, side, 3.3, C.NODE_IN_Y - 1.0, C.NODE_IN_Y + 2.2))
            if tool is None:
                tool = c
            else:
                L.union(tool, c)
        L.cut(band, tool)
    md, mdep = C.SOCKET_MOUTH_STEP
    for side in (+1, -1):
        # nexus bolts through the hub node, heads counterbored under the foam
        # index pin hole down through the lug
        px, py = C.NEXUS_PIN
        (lx0, lx1), (ly0, ly1), (lz0, lz1) = C.NEXUS_PIN_LUG
        L.cut(band, zcyl("pin", px, py, side, C.M3_CLEAR_DIA / 2, lz0 - 1.0, lz1 + 1.0, verts=16))
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
