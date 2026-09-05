#!/usr/bin/env -S blender --background --python
"""
build_yoke.py -- vp0.7 disk yoke (left; --mirror for right): plate + bayonet stalk.

6 mm plate on the hub node's outer face (two M3 through the node, heads under
the foam, nuts in pockets; one nail) reaching down to the brain-core height,
with the Ø20 bayonet stalk at the disk centre: two lugs turn a quarter turn
into the back plate's groove. Pocket on the inner face for the arch peg's
cross-bolt nut. The stalk is the fuse: it breaks before the cradle does.
Print: lying on the inner face, stalk up. Qty: 1 L + 1 R.
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
NOTES = ["print lying on the inner face, stalk up; no supports (3 mm lug overhangs)",
         "two M3 x 25 through the hub node (heads under the foam), one nail; disk bayonets onto the stalk"]


def make(side=+1):
    y0, y1 = C.YOKE_Y
    x0, x1 = C.YOKE_X
    z0, z1 = C.YOKE_Z
    yoke = L.add_box("disk_yoke", ((x0 + x1) / 2, side * (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0))
    L.fillet(yoke, width=1.0)
    Ms = L.frame((C.CX, side * (y1 - 0.5), C.CZ), (0.0, side, 0.0), (1.0, 0.0, 0.0))
    L.union(yoke, L.add_cyl_local("stalk", Ms, (0.0, 0.0, (C.STALK_LEN + 0.5) / 2), C.STALK_D / 2, C.STALK_LEN + 0.5, axis="Z", verts=72))
    lw, lr, lh = C.STALK_LUG
    n0, n1 = C.STALK_LUG_N
    for sx in (+1, -1):
        L.union(yoke, L.add_box_local("lug", Ms, (sx * (C.STALK_D / 2 + lr / 2 - 0.3), 0.0, 1.0 + (n0 + n1) / 2), (lr + 0.6, lw, n1 - n0)))
    for (x, z) in C.YOKE_BOLTS:
        L.cut(yoke, L.add_cyl("bolt", (x, side * (y0 + y1) / 2, z), C.M3_CLEAR_DIA / 2, y1 - y0 + 2.0, axis="Y", verts=24))
        L.cut(yoke, L.add_cyl("nutp", (x, side * (y1 - 1.5 + 1.0), z), 3.5, 5.0, axis="Y", verts=24))
    nx, nz = C.YOKE_NAIL
    L.cut(yoke, L.add_cyl("nail", (nx, side * (y0 + y1) / 2, nz), C.PIN_DIA / 2 + 0.1, y1 - y0 + 2.0, axis="Y", verts=24))
    L.cut(yoke, L.add_cyl("crossnut", (C.HUB_SOCKET[0], side * (y0 + 1.75 - 1.0), C.HUB_CROSS_Z), 3.5, 5.5, axis="Y", verts=24))
    return yoke


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    L.finalize_and_export(make(side), args.out, L.ROT_Y_TO_Z if side > 0 else L.ROT_NEGY_TO_Z, NOTES)
