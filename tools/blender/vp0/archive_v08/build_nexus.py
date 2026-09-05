#!/usr/bin/env -S blender --background --python
"""
build_nexus.py -- vp0.8 NEXUS (--out-dir): flange with stalk, spool, flat plug.

The nexus is the hub on the disk axis between the cradle's hub node and the
disk. Inboard to outboard: node face | spool (Ø44 thrust flange + Ø32 hub) |
visor ring (part of the brow rail) | wave washer | flange Ø60 x 8, bolted
through the node with three M3, carrying three flat 4 x 20 tongue ports
(front, top = crown arch, back), an ear straight down with the disk lock-pin
hole, and the Ø20 bayonet stalk the disk back plate seats over.
One STL each serves both sides (the right is the left turned 180 deg about
the vertical through the disk centre).
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


def radial_frame(angle_deg, side=+1, y=None):
    """Local +X = radial direction at `angle_deg` (from +x toward +z) in the x-z plane; local Y = world Y; origin on the disk axis."""
    yc = side * ((C.NEXUS_Y[0] + C.NEXUS_Y[1]) / 2.0 if y is None else y)
    return Matrix.Translation((C.CX, yc, C.CZ)) @ Matrix.Rotation(-math.radians(angle_deg), 4, "Y")


def ycyl(name, x, z, side, r, y0, y1, verts=24, rot=0.0):
    M = Matrix.Translation((x, side * (y0 + y1) / 2.0, z)) @ Matrix.Rotation(math.radians(rot), 4, "Y")
    return L.add_cyl_local(name, M, (0.0, 0.0, 0.0), r, y1 - y0, axis="Y", verts=verts)


def flange(side=+1):
    y0, y1 = C.NEXUS_Y
    r = C.NEXUS_D / 2.0
    fl = ycyl("nexus", C.CX, C.CZ, side, r, y0, y1, verts=96)
    ear = C.NEXUS_EAR
    Me = radial_frame(ear["angle"], side)
    e = L.add_box_local("ear", Me, ((r - 4.0 + ear["r_out"]) / 2.0, 0.0, 0.0), (ear["r_out"] - r + 4.0, C.NEXUS_T, ear["width"]))   # local Y = flange thickness, local Z = tangential
    L.fillet(e, width=1.0)
    L.union(fl, e)
    L.fillet(fl, width=0.8, angle_deg=60.0)
    # stalk + bayonet lugs on the outer face
    sd = C.STALK_D
    L.union(fl, ycyl("stalk", C.CX, C.CZ, side, sd / 2.0, y1 - 0.5, y1 + C.STALK_LEN, verts=72, rot=1.3))
    lw, lr, lh = C.STALK_LUG
    n0, n1 = C.STALK_LUG_N
    for sx in (+1, -1):
        L.union(fl, L.add_box("lug", (C.CX + sx * (sd / 2.0 + lr / 2.0 - 0.3), side * (y1 + (n0 + n1) / 2.0), C.CZ), (lr + 0.6, n1 - n0, lw)))
    # spool pocket on the inner face, bolt holes with nut pockets on the outer face
    hub_d = C.NEXUS_SPOOL[2]
    L.cut(fl, ycyl("spoolp", C.CX, C.CZ, side, hub_d / 2.0 + 0.2, y0 - 1.0, y0 + 0.5, verts=64, rot=2.1))
    for (x, z) in C.NEXUS_BOLTS:
        L.cut(fl, ycyl("bolt", x, z, side, C.M3_CLEAR_DIA / 2.0, y0 - 1.0, y1 + 1.0, verts=16))
        L.cut(fl, L.add_hex_prism("nut", (x, side * (y1 - 1.5 + 1.0), z), 5.7, 5.0, axis="Y"))
    # flat ports: radial slots with an M3 tap cross-hole
    st, sw, sdp = C.NEXUS_SLOT
    for a in C.NEXUS_SLOT_ANGLES:
        Ms = radial_frame(a, side)
        L.cut(fl, L.add_box_local("slot", Ms, ((r - sdp + r + 1.0) / 2.0, 0.0, 0.0), (sdp + 1.0, st, sw)))
        L.cut(fl, L.add_cyl_local("tap", Ms, (C.NEXUS_SLOT_BOLT_R, 0.0, 0.0), C.M3_TAP_DIA / 2.0, C.NEXUS_T + 2.0, axis="Y", verts=16))
    # disk lock-pin hole through the ear
    lk = C.DISK_LOCK
    Ml = radial_frame(lk["angle"], side)
    L.cut(fl, L.add_cyl_local("lock", Ml, (lk["r"], 0.0, 0.0), lk["hole"] / 2.0, C.NEXUS_T + 2.0, axis="Y", verts=16))
    return fl


def spool(side=+1):
    fd, ft, hd, hh = C.NEXUS_SPOOL
    y0 = C.HUB_NODE_OUT_Y
    sp = ycyl("nexus_spool", C.CX, C.CZ, side, fd / 2.0, y0, y0 + ft, verts=96)
    L.union(sp, ycyl("hub", C.CX, C.CZ, side, hd / 2.0, y0 + ft - 0.1, y0 + ft + hh, verts=72, rot=1.7))
    x, z = C.NEXUS_BOLTS[0]
    L.cut(sp, ycyl("bolt", x, z, side, C.M3_CLEAR_DIA / 2.0, y0 - 1.0, y0 + ft + hh + 1.0, verts=16))
    return sp


def flat_plug(side=+1, angle=0.0):
    """Tongue + cap that closes an unused flat port."""
    tt, tw, tl = C.NEXUS_TONGUE
    r = C.NEXUS_D / 2.0
    Ms = radial_frame(angle, side)
    pl = L.add_box_local("nexus_plug", Ms, ((r - tl + r + 0.5) / 2.0, 0.0, 0.0), (tl + 0.5, tt, tw))
    cap = L.add_box_local("cap", Ms, (r + 1.5, 0.0, 0.0), (3.0, tt + 2.0, tw + 4.0))
    L.fillet(cap, width=0.8)
    L.union(pl, cap)
    L.cut(pl, L.add_cyl_local("cross", Ms, (C.NEXUS_SLOT_BOLT_R, 0.0, 0.0), C.M3_CLEAR_DIA / 2.0, tt + 4.0, axis="Y", verts=16))
    return pl


PARTS = {
    "nexus": (lambda: flange(+1), L.ROT_Y_TO_Z, ["print inner face down, stalk up; no supports (3 mm lug overhangs)", "three M3 x 30 through the hub node; nylon M3 if you want the disk axis metal-free"]),
    "nexus_spool": (lambda: spool(+1), L.ROT_Y_TO_Z, ["print flange down; the visor ring runs on the hub, a wave washer between ring and nexus flange"]),
    "nexus_plug": (lambda: flat_plug(+1, 90.0), L.ROT_FLIP, ["print cap down (tongue up); closes an unused flat port (front / back)"]),
}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(L.argv_after_dashdash())
    for name, (mk, rot, notes) in PARTS.items():
        L.reset_scene()
        L.finalize_and_export(mk(), Path(args.out_dir) / f"{name}.stl", rot, notes)


if __name__ == "__main__":
    main()
