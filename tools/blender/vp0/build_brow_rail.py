#!/usr/bin/env -S blender --background --python
"""
build_brow_rail.py -- vp0.8 brow rail with its nexus ring (left; --mirror for right).

A Ø44 ring (bore 32.3) that runs on the nexus spool between the spool's
thrust flange and a wave washer, with 24 radial Ø3.4 index holes in its rim
(15 deg tilt steps; a spring-loaded nail in the cradle's pin lug locks it),
and a 7 x 20 rail leaving it at 13 deg above forward to the panel's tab,
which it bolts to with two M3 x 12 (fixed reach).
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

NOTES = ["print lying on the inner (ring) face; no supports",
         "runs on the nexus spool; captive index nail in the keeper locks the tilt; two M3 x 12 into the panel tab"]


def rail_frame(angle_deg, side):
    return Matrix.Translation((C.CX, 0.0, C.CZ)) @ Matrix.Rotation(-math.radians(angle_deg), 4, "Y")


def make(side=+1):
    od, idia, t = C.NEXUS_RING
    y0 = C.NEXUS_RING_Y0
    axis = "Y" if side > 0 else "-Y"
    ring = L.revolve("brow_rail", [(idia / 2.0, 0.0), (od / 2.0, 0.0), (od / 2.0, t), (idia / 2.0, t)], axis=axis, center=(C.CX, side * y0, C.CZ), segments=100)
    Mr = rail_frame(C.RAIL_ANGLE, side)
    r0 = C.RAIL_ROOT_R
    yr = side * (y0 + t / 2.0)
    L.union(ring, L.add_box_local("root", Mr, ((od / 2.0 - 2.0 + r0) / 2.0, yr, 0.0), (r0 - od / 2.0 + 2.0, t, C.RAIL_H)))
    yb = side * (C.RAIL_Y0 + C.RAIL_T / 2.0)
    L.union(ring, L.add_box_local("bar", Mr, ((r0 - 0.5 + C.RAIL_S1) / 2.0, yb, 0.0), (C.RAIL_S1 - r0 + 0.5, C.RAIL_T, C.RAIL_H)))
    L.fillet(ring, width=0.6, angle_deg=60.0)
    for s_b in C.RAIL_BOLTS_S:
        L.cut(ring, L.add_cyl_local("bolt", Mr, (s_b, yb, 0.0), C.M3_CLEAR_DIA / 2.0, C.RAIL_T + 4.0, axis="Y", verts=16))
    for k in range(C.NEXUS_RING_HOLES):
        a = 90.0 + 360.0 * k / C.NEXUS_RING_HOLES          # a hole sits under the pin lug at the nominal tilt
        Mk = rail_frame(a, side)
        L.cut(ring, L.add_cyl_local("idx", Mk, ((od / 2.0 + 0.5 + od / 2.0 - 5.5) / 2.0, yr, 0.0), C.M3_CLEAR_DIA / 2.0, 6.0, axis="X", verts=16))
    return ring


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    L.finalize_and_export(make(side), args.out, L.ROT_Y_TO_Z if side > 0 else L.ROT_NEGY_TO_Z, NOTES)
