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
    # the former turns with the plate: its exit must sit over the bore in the LOCKED pose, one lock travel further round
    return math.hypot(q.x, q.y), math.atan2(q.y, q.x) + math.radians(BD.lock_travel_deg())


def spool(side=+1, n_offset=0.0):
    """v0.17 spool former: one flange (Ø109.4 x 1.2) with a Ø40/44 x 3 hub ring, six boss holes, a solder-pad boss and a Ø3 lead
    pass-through over the plate's arc slot (locked-pose angle). The bifilar pair is scramble-wound onto the flange around the hub and
    glued; a second identical spool stacks on the first (its flange rests on the hub and the winding) for the counter-wound sham.
    n_offset stacks it: 0 for the first, flange_t + hub height for the second."""
    M = BD.axis_frame(side)
    ft = CF["flange_t"]
    hid, hod, hh = CF["hub"]
    n0 = N0 + 0.2 + n_offset                      # +0.2 for the foil lining under the first spool
    body = L.add_cyl_local("coil_spool", M, (0.0, 0.0, n0 + ft / 2), CF["od"] / 2, ft, axis="Z", verts=160)
    L.union(body, L.add_cyl_local("hub", M, (0.0, 0.0, n0 + ft + hh / 2 - 0.05), hod / 2, hh + 0.1, axis="Z", verts=96))
    L.cut(body, L.add_cyl_local("centre", M, (0.0, 0.0, n0 + (ft + hh) / 2), hid / 2, ft + hh + 2.0, axis="Z", verts=96))
    for k in range(C.DISK_SCREWS):
        a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
        L.cut(body, L.add_cyl_local("bosshole", M, (C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a), n0 + ft / 2), CF["boss_hole"] / 2, ft + 2.0, axis="Z", verts=24))
    r_exit, a_exit = exit_polar(M)
    Mr = M @ Matrix.Rotation(a_exit, 4, "Z")
    pw, pd, ph = CF["pad"]
    r_pad = CF["r1"] + 0.5 + pw / 2
    L.union(body, L.add_box_local("pad", Mr, (r_pad, 0.0, n0 + ft + ph / 2 - 0.05), (pw, pd, ph + 0.1)))       # solder pad boss outside the winding, inside the cavity wall (r 50.5..54.5)
    L.cut(body, L.add_box_local("padslot", Mr, (r_pad, 0.0, n0 + (ft + ph) / 2), (1.0, 2.5, ft + ph + 2.0)))   # tie-off slot for the wire pair side by side (1.25 walls in the 3.5 boss)
    L.cut(body, L.add_cyl_local("lead", Mr, (r_exit, 0.0, n0 + ft / 2), CF["pass_hole"] / 2, ft + 2.0, axis="Z", verts=16))   # over the plate's slot (locked pose)
    bw, bd = CF["spool_groove"]
    L.cut(body, L.add_box_local("radial", Mr, ((r_exit - 1.5 + r_pad + 1.0) / 2, 0.0, n0 - 0.5 + bd / 2), (r_pad + 1.0 - r_exit + 1.5, bw, bd + 1.0)))   # back groove: tie hole -> lead hole (0.8 deep in the 1.6 flange; ends 1.5 inside the flange edge)
    L.cut(body, L.add_box_local("arrow", Mr, (r_exit + 5.0, 2.6, n0 + ft), (4.0, 1.2, 1.2)))   # beside the back groove (y +-0.7), not over it
    return body


def bay_spool():
    """v0.17: the visor-bay coil spool (built flat in its own frame: x = width, y = height, z = up from the flange)."""
    B = C.BAY_COIL
    w, h, ft = B["w"], B["h"], B["flange_t"]
    cw, ch, chh = B["core"]
    sp = L.add_box("bay_spool", (0.0, 0.0, ft / 2), (w, h, ft))
    core = L.extrude_polygon("core", L.rounded_rect_poly(cw, ch, ch / 2 - 0.1), chh + 0.1, Matrix.Translation((0.0, 0.0, ft - 0.05)))
    L.union(sp, core)
    pw, pd, ph = B["pad"]
    L.union(sp, L.add_box("pad", (w / 2 - pw / 2, -h / 2 + pd / 2, ft + ph / 2 - 0.05), (pw, pd, ph + 0.1)))
    L.cut(sp, L.add_cyl("lead", (w / 2 - pw - 2.0, -h / 2 + 3.0, ft / 2), B["lead_hole"] / 2, ft + 2.0, axis="Z", verts=16))
    L.fillet(sp, width=0.5)
    return sp


def former(side=+1):
    if CF.get("style") == "spool":
        return spool(side)
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
    "coil_former": (lambda: former(+1), L.ROT_Y_TO_Z, ["print flat, flange down, hub up (x2 per disk: the second is the counter-wound sham layer); PLA",
                                                       "scramble-wind the bifilar pair around the hub onto the flange, a drop of CA every few turns, ends to the solder pad; leads down the pass hole and the back groove into the plate's arc slot; clock the arrow at the plate's slot end; foam ring on top"]),
    "bay_spool": (bay_spool, L.ROT_NONE, ["print flat; the front-axis coil for the visor bay: wind around the core, ends to the pad, lead through the hole into the panel's cable hole"]),
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
