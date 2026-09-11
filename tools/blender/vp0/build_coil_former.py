#!/usr/bin/env -S blender --background --python
"""
build_coil_former.py -- vp0.15 pancake coil former (--out-dir): the winding body for the Stabilizer's bifilar pancake in the disk cavity.

docs/psionic_engineering/stabilizer_derivation.md: 4-terminal bifilar pancake, ID 40 / OD ~104, 16-17 turn-pairs of 24 AWG.
A Ø109.4 x 3.5 disc that sits on the back plate's cavity side, captured by the six dome screw bosses through its holes and
cleared by the Ø34 bayonet boss through its Ø40 centre. Its outer face carries one Archimedean spiral groove (1.15 wide, 1.3 deep:
the two 24 AWG wires of the bifilar pair lie side by side in it) from r 21 to r 50 at 1.8 mm pitch. Both ends of the spiral drop
through the disc; on the back face a radial groove along the exit direction and an arc groove at r 51.5 bring all four wire ends
over the plate's cable hole: the wires drop straight from the back grooves into it (no hole through the windings). Clock the former
so its arrow points at the plate's hole; the six boss holes then fix it.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_disk as BD
from mathutils import Matrix, Vector  # type: ignore

CF = C.COIL_FORMER
N0 = C.DISK_PLATE_T + 0.05                     # former back face (on the plate's cavity side)


def exit_polar(M):
    """(r, angle) of the plate's cable hole in the disk's local frame."""
    cb = C.CABLE_BORE
    p_world = Vector((C.CX - cb["dx"], 0.0, cb["z"]))
    # M's origin is (CX, side*DISK_IN_Y, CZ); take the local x/y of the world point (ignoring the axis component)
    Minv = M.inverted()
    q = Minv @ Vector((p_world.x, M.translation.y, p_world.z))
    return math.hypot(q.x, q.y), math.atan2(q.y, q.x)


def former(side=+1):
    M = BD.axis_frame(side)
    t = CF["t"]
    body = L.add_cyl_local("coil_former", M, (0.0, 0.0, N0 + t / 2), CF["od"] / 2, t, axis="Z", verts=160)
    L.cut(body, L.add_cyl_local("centre", M, (0.0, 0.0, N0 + t / 2), CF["id"] / 2, t + 2.0, axis="Z", verts=96))
    for k in range(C.DISK_SCREWS):
        a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
        L.cut(body, L.add_cyl_local("bosshole", M, (C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a), N0 + t / 2), CF["boss_hole"] / 2, t + 2.0, axis="Z", verts=24))
    r_exit, a_exit = exit_polar(M)
    # spiral groove on the outer face, starting at the exit angle
    r0, r1, pitch = CF["r0"], CF["r1"], CF["pitch"]
    gw, gd = CF["groove"]
    n_turns = (r1 - r0) / pitch
    pts = []
    th = 0.0
    while th <= 2 * math.pi * n_turns:
        r = r0 + pitch * th / (2 * math.pi)
        pts.append(M @ Vector((r * math.cos(a_exit + th), r * math.sin(a_exit + th), N0 + t)))
        th += 2.0 / r                           # ~2 mm steps
    wide = M.to_3x3() @ Vector((0.0, 0.0, 1.0))
    L.cut(body, L.ribbon("spiral", pts, wide, [(1.0, gd, gw / 2, gw / 2)] * len(pts)))
    a_end = a_exit + 2 * math.pi * n_turns
    # through-holes at both spiral ends, the exit hole, back-face grooves: radial along a_exit (r0 -> r1 + 1.5) and an arc at r1 + 1.5
    # the wire pair drops through a 1.0 x 2.0 slot along the furrow at each end (narrower than the furrow: no sliver walls)
    for r, a in ((r0, a_exit), (r1, a_end)):
        Ms = M @ Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((r, 0.0, 0.0))
        L.cut(body, L.add_box_local("pin", Ms, (0.0, 0.0, N0 + t / 2), (1.0, 2.0, t + 2.0)))
    bw, bd = CF["back_groove"]
    ra = r1 - 1.0                            # the arc groove sits just inside the outer pin hole, 2 mm clear of the boss holes at r 51.7
    Mr = M @ Matrix.Rotation(a_exit, 4, "Z")
    L.cut(body, L.add_box_local("radial", Mr, ((r0 - 1.0 + ra + 0.7) / 2, 0.0, N0 - 0.5 + bd / 2), (ra + 0.7 - r0 + 1.0, bw, bd + 1.0)))
    arc = []
    a = a_end
    while a > a_exit + 2 * math.pi * math.floor(n_turns):
        arc.append(M @ Vector((ra * math.cos(a), ra * math.sin(a), N0)))
        a -= 2.0 / ra
    arc.append(M @ Vector((ra * math.cos(a_exit + 2 * math.pi * math.floor(n_turns)), ra * math.sin(a_exit + 2 * math.pi * math.floor(n_turns)), N0)))
    if len(arc) >= 2:
        L.cut(body, L.ribbon("arc", arc, wide, [(bd, 1.0, bw / 2, bw / 2)] * len(arc)))
    # index arrow (a small triangle pocket) on the outer face pointing at the exit
    L.cut(body, L.add_box_local("arrow", Mr, (r_exit + 5.0, 0.0, N0 + t), (4.0, 1.2, 1.2)))
    return body


PARTS = {
    "coil_former": (lambda: former(+1), L.ROT_Y_TO_Z, ["print flat, spiral face up (x2, same part for both disks); PLA is fine, the coil dissipates under a watt at the experimental currents",
                                                       "wind the bifilar pair (two 24 AWG wires side by side) from the inner pin hole outward in the spiral, drop both ends through the pin holes, run them in the back grooves to the exit hole; clock the arrow over the plate's cable hole"]),
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
