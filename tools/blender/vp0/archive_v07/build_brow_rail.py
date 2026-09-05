#!/usr/bin/env -S blender --background --python
"""
build_brow_rail.py -- vp0.7 brow rail (left; --mirror for right).

6 x 20 bar from a rounded serrated knuckle (hinged between the temple node's
lugs, M3 x 40 with a wave washer: 15 deg tilt notches) forward to x 183, with
ten Ø3.4 reach holes every 5 mm for the slider's pin. Flip the brow up over
the crown: the rail stops on the node's top.
Print: lying on a side face. Qty: 1 L + 1 R.
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

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = ["print lying on a side face; no supports", "hinge: M3 x 40 through the temple lugs with a wave washer; reach pin: M3 x 20 with a knob"]


def make(side=+1):
    hx, hy, hz = C.BROW_HINGE
    t, h = C.RAIL_SECTION
    r = h / 2
    poly = []
    for i in range(25):
        a = math.radians(90.0 + 180.0 * i / 24)
        poly.append((hx + r * math.cos(a), hz + r * math.sin(a)))
    poly += [(C.RAIL_X1, hz - r), (C.RAIL_X1, hz + r)]
    M = L.frame((0.0, side * hy + t / 2, 0.0), (0.0, -1.0, 0.0), (1.0, 0.0, 0.0))   # u = x, v = +z on both sides; extrudes 6 mm toward -Y from the outer face
    rail = L.extrude_polygon("brow_rail", poly, t, M)
    L.fillet(rail, width=0.8)
    L.cut(rail, L.add_cyl("bolt", (hx, side * hy, hz), C.M3_CLEAR_DIA / 2, t + 4.0, axis="Y", verts=24))
    for k in range(C.RAIL_HOLES_N):
        L.cut(rail, L.add_cyl("reach", (C.RAIL_HOLES_X0 + k * C.RAIL_HOLE_PITCH, side * hy, hz), C.M3_CLEAR_DIA / 2, t + 4.0, axis="Y", verts=16))
    sr = C.HINGE_SERR
    L.union(rail, L.serration_solid("serr", (hx, side * (hy + t / 2), hz), (0.0, side, 0.0),
                                    r_in=sr["r_in"], r_out=sr["r_out"], teeth=sr["teeth"], height=sr["height"], phase_deg=sr["phase_tongue"]))
    return rail


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    L.finalize_and_export(make(side), args.out, L.ROT_Y_TO_Z if side > 0 else L.ROT_NEGY_TO_Z, NOTES)
