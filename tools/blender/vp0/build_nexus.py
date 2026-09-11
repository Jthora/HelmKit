#!/usr/bin/env -S blender --background --python
"""
build_nexus.py -- vp0.11 NEXUS (--out-dir): flange (hollow stalk, lock-pin hole, cable bore), spool (hub with pawl notches, spacer), disk knob + clip.

Per side, on the disk axis, outboard from the hub node's face (y 100):
  spool      Ø44 x 1 thrust plate on the node face with a web up to the SPACER block (x +/-10, y 100.9..108.9, z 58..68.5) that the
             top bolts pass through and that bears on the flange back; Ø36 x 8.5 hub = the visor ring's bearing, with notches at the six
             visor positions in its outer end for the rail's pawl slider; bolt 0 passes through the hub
  ring       (part of the brow rail) Ø44 / 36.3 x 7 on the hub; wave washer to the flange
  flange     Ø68 x 8 at y 109..117: HOLLOW bayonet stalk (Ø10 bore) with a filleted root and lugs, a radial lock-pin hole at the top,
             three M3 x 30 from OUTSIDE (heads in counterbores under the disk), the Ø5 coil-cable bore, a lanyard hole
  knob       Ø28 knob flush in the dome's apex dish; its shaft runs down the axis into the stalk bore; the eccentric end pushes
             the lock pin into the plate's notch (180 deg turn). A C-clip inside the dome keeps the knob in the disk.
L and R flanges are mirrored STLs; the spool, knob and clip serve both sides.
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
    yc = (C.NEXUS_Y[0] + C.NEXUS_Y[1]) / 2.0 if y is None else y
    return Matrix.Translation((C.CX, side * yc, C.CZ)) @ Matrix.Rotation(-math.radians(angle_deg), 4, "Y")


def ycyl(name, x, z, side, r, y0, y1, verts=24, rot=0.0):
    c = L.add_cyl(name, (x, side * (y0 + y1) / 2.0, z), r, abs(y1 - y0), axis="Y", verts=verts)
    if rot:
        c.matrix_world = Matrix.Translation((x, 0.0, z)) @ Matrix.Rotation(math.radians(rot), 4, "Y") @ Matrix.Translation((-x, 0.0, -z)) @ c.matrix_world
        L.apply_transform(c)
    return c


def sbox(name, x0, x1, y0, y1, z0, z1, side, fillet=None):
    b = L.add_box(name, ((x0 + x1) / 2.0, side * (y0 + y1) / 2.0, (z0 + z1) / 2.0), (x1 - x0, y1 - y0, z1 - z0))
    if fillet:
        L.fillet(b, width=fillet)
    return b


def mirror_if(ob, side):
    if side < 0:
        ob.matrix_world = Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)) @ ob.matrix_world
        L.apply_transform(ob)
        L.recalc_normals(ob)
    return ob


def flange(side=+1):
    y0, y1 = C.NEXUS_Y
    r = C.NEXUS_D / 2.0
    fl = ycyl("nexus", C.CX, C.CZ, side, r, y0, y1, verts=96)
    L.fillet(fl, width=0.8, angle_deg=60.0)
    # hollow stalk with a concave root fillet ring and the bayonet lugs on the outer face
    sd = C.STALK_D
    L.union(fl, ycyl("stalk", C.CX, C.CZ, side, sd / 2.0, y1 - 0.5, y1 + C.STALK_LEN, verts=72, rot=1.3))
    fr = C.STALK_FILLET
    Rc = sd / 2.0 + fr
    prof = [(sd / 2.0 - 0.1, -0.1), (Rc + 0.2, -0.1)]
    for k in range(7):
        phi = math.radians(268.0 - 86.0 * k / 6)
        prof.append((Rc + fr * math.cos(phi), fr + fr * math.sin(phi)))
    prof.append((sd / 2.0 - 0.1, fr))
    fil = L.revolve("stalk_fillet", prof, axis="Y" if side > 0 else "-Y", center=(C.CX, side * y1, C.CZ), segments=60)
    fil.matrix_world = Matrix.Translation((C.CX, 0.0, C.CZ)) @ Matrix.Rotation(math.radians(0.7), 4, "Y") @ Matrix.Translation((-C.CX, 0.0, -C.CZ)) @ fil.matrix_world
    L.apply_transform(fil)
    L.union(fl, fil)
    lw, lr, lh = C.STALK_LUG
    n0, n1 = C.STALK_LUG_N
    for sx in (+1, -1):
        L.union(fl, L.add_box("lug", (C.CX + sx * (sd / 2.0 + lr / 2.0 - 0.3), side * (y1 + (n0 + n1) / 2.0), C.CZ), (lr + 0.6, n1 - n0, lw)))
    # shaft bore down the axis (2 mm into the flange) and the radial lock-pin hole at the top
    L.cut(fl, ycyl("bore", C.CX, C.CZ, side, C.STALK_BORE / 2.0, y1 - 2.0, y1 + C.STALK_LEN + 1.0, verts=48, rot=2.9))
    lk = C.BAYONET_LOCK
    Mp = radial_frame(lk["pin_world_deg"], side, y=y1 + lk["n"])
    L.cut(fl, L.add_cyl_local("pinhole", Mp, ((C.STALK_BORE / 2.0 - 1.0 + sd / 2.0 + 1.0) / 2.0, 0.0, 0.0), (lk["pin_dia"] + 0.2) / 2.0, sd / 2.0 - C.STALK_BORE / 2.0 + 2.0, axis="X", verts=16))
    # bolt holes with head counterbores on the outer face (under the disk plate). v0.14: no spool pocket on the inner face --
    # that face is the print bed and a 0.5 mm recess there fills in; the hub now bears on the flat face and the bolts locate it.
    cd, cdep = C.NEXUS_HEAD_CBORE
    for (x, z) in C.NEXUS_BOLTS:
        L.cut(fl, ycyl("bolt", x, z, side, C.M3_CLEAR_DIA / 2.0, y0 - 1.0, y1 + 1.0, verts=16))
        L.cut(fl, ycyl("head", x, z, side, cd / 2.0, y1 - cdep, y1 + 1.0, verts=24))
    # coil cable bore (straight through plate, flange and node) and the lanyard hole
    cb = C.CABLE_BORE
    L.cut(fl, ycyl("cable", C.CX - cb["dx"], cb["z"], side, cb["dia"] / 2.0, y0 - 1.0, y1 + 1.0, verts=20))
    ly = C.NEXUS_LANYARD
    Ml = radial_frame(ly["angle"], side)
    L.cut(fl, L.add_cyl_local("lanyard", Ml, (ly["r"], 0.0, 0.0), ly["hole"] / 2.0, C.NEXUS_T + 2.0, axis="Y", verts=16))
    return fl


def spool(side=+1):
    """Thrust plate + web as ONE polygon extrusion, then the hub (with the pawl notches) and the top-bolt spacer block."""
    fd, ft, hd, hh = C.NEXUS_SPOOL
    y0 = C.HUB_NODE_OUT_Y
    sp_ = C.SPOOL_SPACER
    xh, top = sp_["x_half"], sp_["z1"]
    R = fd / 2.0
    zc = C.CZ + math.sqrt(R * R - xh * xh)
    a0 = math.degrees(math.atan2(zc - C.CZ, xh))
    outline = [(-xh, top), (xh, top), (xh, zc)]
    n = 96
    for i in range(1, n):
        a = math.radians(a0 - (2 * a0 + 180.0) * i / n)
        outline.append((R * math.cos(a), C.CZ + R * math.sin(a)))
    outline.append((-xh, zc))
    Mp = Matrix.Translation((C.CX, 0.0, 0.0)) @ Matrix.Rotation(-math.pi / 2.0, 4, "X")
    sp = L.extrude_polygon("nexus_spool", [(x, -z) for (x, z) in outline], ft, Mp, z0=y0)
    L.union(sp, ycyl("hub", C.CX, C.CZ, +1, hd / 2.0, y0 + ft - 0.1, y0 + ft + hh, verts=72, rot=1.1))
    blk = sbox("spacer", C.CX - xh, C.CX + xh, y0 + ft - 0.1, sp_["y1"], sp_["z0"], top, +1, fillet=0.8)
    L.union(sp, blk)
    for i, (x, z) in enumerate(C.NEXUS_BOLTS):
        L.cut(sp, ycyl("bolt", x, z, +1, C.M3_CLEAR_DIA / 2.0, y0 - 1.0, (y0 + ft + hh + 1.0) if i == 0 else sp_["y1"] + 1.0, verts=16))
    # pawl notches around the hub's outer end
    hn = C.HUB_NOTCHES
    ny0, ny1 = hn["y"]
    for ang in hn["angles"]:
        Mk = radial_frame(ang + 0.3, +1, y=(ny0 + ny1) / 2.0)
        L.cut(sp, L.add_box_local("notch", Mk, (hd / 2.0 - hn["d"] / 2.0 + 0.5, 0.0, 0.0), (hn["d"] + 1.0, ny1 - ny0, hn["w"])))
    return mirror_if(sp, side)


def disk_knob():
    """Knob + shaft + eccentric as one standing print: knob face at z 0..t, shaft up the axis, eccentric end at the top."""
    kb = C.DISK_KNOB
    kd, kt, sd, ecc, el = kb["d"], kb["t"], kb["shaft_d"], kb["ecc"], kb["ecc_len"]
    n_top = C.DISK_THICK + 0.2                                # knob's outer face (0.2 above the dome apex)
    n_tip = C.BAYONET_LOCK["n"] - 3.0                          # eccentric end 3 mm below the pin hole
    L_shaft = n_top - kt - n_tip                              # from the knob's underside to the tip
    k = L.add_cyl("disk_knob", (0.0, 0.0, kt / 2.0), kd / 2.0, kt, axis="Z", verts=64)
    for i in range(8):
        a = 2 * math.pi * i / 8 + 0.1
        L.cut(k, L.add_cyl("grip", ((kd / 2.0 + 0.5) * math.cos(a), (kd / 2.0 + 0.5) * math.sin(a), kt / 2.0), 2.2, kt + 2.0, axis="Z", verts=16))
    L.union(k, L.add_cyl("shaft", (0.0, 0.0, kt - 0.1 + (L_shaft - el + 0.1) / 2.0), sd / 2.0, L_shaft - el + 0.1, axis="Z", verts=48))
    L.union(k, L.add_cyl("ecc", (ecc, 0.0, kt + L_shaft - el / 2.0 - 0.1), kb["ecc_d"] / 2.0, el + 0.2, axis="Z", verts=40))   # Ø6 offset 1: envelope 8.0 in the 8.2 bore
    gn = C.DISK_THICK + 0.2 - kb["clip_n"]                    # clip groove position along the shaft (from the knob face)
    L.cut(k, L.add_cyl("groove_out", (0.0, 0.0, gn), sd / 2.0 + 1.0, kb["clip"][2] + 0.2, axis="Z", verts=48))
    L.union(k, L.add_cyl("groove_core", (0.0, 0.0, gn), sd / 2.0 - 1.0, kb["clip"][2] + 0.4, axis="Z", verts=40))
    L.cut(k, L.add_box("mark", (kd / 2.0 - 2.0, 0.0, 0.0), (3.0, 1.2, 1.6)))   # index mark on the knob face toward the eccentric side
    return k


def knob_clip():
    od, idia, t = C.DISK_KNOB["clip"]
    c = L.add_cyl("knob_clip", (0.0, 0.0, t / 2.0), od / 2.0, t, axis="Z", verts=48)
    L.cut(c, L.add_cyl("bore", (0.0, 0.0, t / 2.0), (C.DISK_KNOB["shaft_d"] - 2.0 + 0.3) / 2.0, t + 2.0, axis="Z", verts=32))
    L.cut(c, L.add_box("slot", (od / 4.0 + 0.5, 0.0, t / 2.0), (od / 2.0 + 1.0, C.DISK_KNOB["shaft_d"] - 2.0 - 0.4, t + 2.0)))
    return c


PARTS = {
    "nexus_L": (lambda: flange(+1), L.ROT_Y_TO_Z, ["PETG, LEFT. print inner face down, stalk up; no supports (3 mm lug overhangs)", "three M3 x 30 from outside through spool and node into nuts in the node's inner face (thread-lock); lanyard cord through the flange hole to a strap slot; 7.8 mm piece of 3.2 nail, outer end filed round, in the stalk's top hole (grease it: it is loose until the disk is on)"]),
    "nexus_R": (lambda: flange(-1), L.ROT_NEGY_TO_Z, ["PETG, RIGHT (mirrored). print inner face down, stalk up; no supports"]),
    "nexus_spool": (lambda: spool(+1), L.ROT_Y_TO_Z, ["PETG. print plate down, hub and spacer up; no supports", "the visor ring runs on the hub; its pawl drops into the notches at the visor positions; wave washer between ring and nexus flange"]),
    "disk_knob": (disk_knob, L.ROT_NONE, ["PETG. print knob face down, shaft up (brim); the eccentric end is the top", "push through the dome's apex hole from outside, snap the C-clip into the groove from inside, then fit the plate; index mark at the dish notch (bottom) = unlocked, mark up = locked"]),
    "knob_clip": (knob_clip, L.ROT_NONE, ["PETG. print flat; snaps into the shaft groove inside the dome"]),
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
