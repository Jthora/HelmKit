#!/usr/bin/env -S blender --background --python
"""
build_nexus.py -- vp0.9 NEXUS (--out-dir): flange with stalk, spool, pin keeper, lock knob, pin collar.

The nexus is the hub on the disk axis between the cradle's hub node and the
disk. Inboard to outboard: node face | spool (Ø44 thrust flange + Ø32 hub) |
visor ring (part of the brow rail) | wave washer | flange Ø60 x 8 (PETG),
bolted through the node with three M3, with an ear straight down: full
thickness to r 58; the disk back plate seats on it and the M3 x 20 lock screw passes through it into the plate's tapped lock
tab sits over (M3 x 12 + knob from the gap side), a lanyard hole, and the Ø20
bayonet stalk. No ports: the crown arch lives on the hub node socket.
Keeper: a U-saddle bolted through the hub node's pin lug; the index nail runs
through its bar, a spring between bar and a glued C-collar keeps it captive.
One STL each serves both sides.
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
    """Local +X = radial direction at `angle_deg` (from +x toward +z); local Y = world Y; local Z = tangential."""
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
    e = L.add_box_local("ear", Me, ((r - 4.0 + ear["r_out"]) / 2.0, 0.0, 0.0), (ear["r_out"] - r + 4.0, C.NEXUS_T, ear["width"]))
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
    # lock screw clearance hole through the ear, lanyard hole through the flange
    lk = C.DISK_LOCK
    L.cut(fl, L.add_cyl_local("lock", Me, (lk["r"], 0.0, 0.0), lk["hole"] / 2.0, C.NEXUS_T + 2.0, axis="Y", verts=16))
    ly = C.NEXUS_LANYARD
    L.cut(fl, L.add_cyl_local("lanyard", Me, (ly["r"], 0.0, ly["offset"]), ly["hole"] / 2.0, C.NEXUS_T + 2.0, axis="Y", verts=16))
    return fl


def spool(side=+1):
    fd, ft, hd, hh = C.NEXUS_SPOOL
    y0 = C.HUB_NODE_OUT_Y
    sp = ycyl("nexus_spool", C.CX, C.CZ, side, fd / 2.0, y0, y0 + ft, verts=96)
    L.union(sp, ycyl("hub", C.CX, C.CZ, side, hd / 2.0, y0 + ft - 0.1, y0 + ft + hh, verts=72, rot=1.7))
    x, z = C.NEXUS_BOLTS[0]
    L.cut(sp, ycyl("bolt", x, z, side, C.M3_CLEAR_DIA / 2.0, y0 - 1.0, y0 + ft + hh + 1.0, verts=16))
    return sp


def keeper(side=+1):
    """U-saddle over the hub node's pin lug: two end plates, a top bar with the pin hole, one M3 along x through the lug."""
    (lx0, lx1), (ly0, ly1), (lz0, lz1) = C.NEXUS_PIN_LUG
    k = C.PIN_KEEPER
    pt, top, bt, bz = k["plate_t"], k["top_z"], k["bar_t"], k["bolt_z"]
    kp = L.add_box("pin_keeper", ((lx0 - pt + lx0) / 2.0, side * (ly0 + ly1) / 2.0, (lz0 + top) / 2.0), (pt, ly1 - ly0, top - lz0))
    L.union(kp, L.add_box("plate2", ((lx1 + lx1 + pt) / 2.0, side * (ly0 + ly1) / 2.0, (lz0 + top) / 2.0), (pt, ly1 - ly0, top - lz0)))
    L.union(kp, L.add_box("bar", ((lx0 + lx1) / 2.0, side * (ly0 + ly1) / 2.0, (top - bt + top) / 2.0), (lx1 - lx0 + 0.2, ly1 - ly0, bt)))
    L.fillet(kp, width=0.6)
    px, py = C.NEXUS_PIN
    L.cut(kp, L.add_cyl("pin", (px, side * py, top - bt / 2.0), 1.8, bt + 2.0, axis="Z", verts=16))
    L.cut(kp, L.add_cyl("bolt", ((lx0 + lx1) / 2.0, side * py, bz), C.M3_CLEAR_DIA / 2.0, lx1 - lx0 + 2 * pt + 2.0, axis="X", verts=16))
    L.cut(kp, L.add_cyl("head", (lx0 - pt + 1.0 - 1.0, side * py, bz), 3.1, 2.0, axis="X", verts=16))
    return kp


def lock_knob():
    kd, kt = C.LOCK_KNOB
    k = L.add_cyl("lock_knob", (0.0, 0.0, kt / 2.0), kd / 2.0, kt, axis="Z", verts=48)
    for i in range(6):
        a = 2 * math.pi * i / 6
        L.cut(k, L.add_cyl("grip", ((kd / 2.0 + 0.3) * math.cos(a), (kd / 2.0 + 0.3) * math.sin(a), kt / 2.0), 1.6, kt + 2.0, axis="Z", verts=12))
    L.cut(k, L.add_cyl("bolt", (0.0, 0.0, kt / 2.0), C.M3_CLEAR_DIA / 2.0, kt + 2.0, axis="Z", verts=16))
    L.cut(k, L.add_cyl("head", (0.0, 0.0, kt - 1.5 + 1.0), 3.1, 5.0, axis="Z", verts=16))
    return k


def pin_collar():
    od, t, slot = C.PIN_COLLAR
    c = L.add_cyl("pin_collar", (0.0, 0.0, t / 2.0), od / 2.0, t, axis="Z", verts=48)
    L.cut(c, L.add_cyl("bore", (0.0, 0.0, t / 2.0), 1.65, t + 2.0, axis="Z", verts=16))
    L.cut(c, L.add_box("slot", (od / 4.0 + 0.5, 0.0, t / 2.0), (od / 2.0 + 1.0, slot, t + 2.0)))
    return c


PARTS = {
    "nexus": (lambda: flange(+1), L.ROT_Y_TO_Z, ["PETG. print inner face down, stalk up; no supports (3 mm lug overhangs)", "three M3 x 30 through the hub node (nylocs, thread-lock); lanyard cord through the ear hole to a strap slot"]),
    "nexus_spool": (lambda: spool(+1), L.ROT_Y_TO_Z, ["print flange down; the visor ring runs on the hub, a wave washer between ring and nexus flange"]),
    "pin_keeper": (lambda: keeper(+1), L.ROT_FLIP, ["print bar down, plates up; one M3 x 25 through the hub node's pin lug; nail + spring + glued C-collar inside"]),
    "lock_knob": (lock_knob, L.ROT_NONE, ["print flat; glue onto the head of the M3 x 20 disk lock screw"]),
    "pin_collar": (pin_collar, L.ROT_NONE, ["print flat; snap onto the index nail 11 mm above the tip and epoxy"]),
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
