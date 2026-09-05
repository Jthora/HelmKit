#!/usr/bin/env -S blender --background --python
"""
build_cheek_hook.py -- vp0.2 cheek hook add-on (front-lower port), left; --mirror for right.

Standard port plug + flange, a 12 x 5 bar running inward under the pod rim,
ending in a 30 x 20 pad plate that tucks just under the zygomatic arch (foam on
the face side). Chin-strap-free anti-lift: speculative, fit to be confirmed.

Print: flange on the bed, post up, pad disc standing on edge. Qty: 1 L + 1 R.
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
from mathutils import Matrix, Vector  # type: ignore

PORT_ANGLE = 300.0
NOTES = ["print flange down, post up; the pad plate stands on its long edge", "--mirror for the right hook; foam pad on the disc face"]


def local_frame(side=+1) -> Matrix:
    Mp = L.pod_port_frame(PORT_ANGLE, side)
    d = Vector((Mp[0][2], Mp[1][2], Mp[2][2]))          # outward radial
    origin = Vector((Mp[0][3], Mp[1][3], Mp[2][3]))
    return L.frame(origin, -d, (0.0, -side, 0.0))        # z = into socket, x = inward? (x hint = -Y side)


def make(side: int = +1):
    M = local_frame(side)
    # in this frame: z into the socket, x = inward (toward the face), y = z cross x
    hook = L.add_box_local("cheek_hook", M, (0.0, 0.0, -C.PORT_FLANGE_T / 2), (C.PORT_FLANGE, C.PORT_FLANGE, C.PORT_FLANGE_T))
    L.union(hook, L.add_box_local("post", M, (0.0, 0.0, (C.PORT_PLUG_LEN - 1.0) / 2), (C.PORT_SQ, C.PORT_SQ, C.PORT_PLUG_LEN + 1.0)))   # sinks 1 mm into the flange
    bar_len = (C.POD_PORT_Y - C.PORT_FLANGE / 2) - (C.CHEEK_PAD_Y_IN + C.CHEEK_PAD[2])
    bh, bt = C.CHEEK_BAR
    L.union(hook, L.add_box_local("bar", M, (C.PORT_FLANGE / 2 + bar_len / 2, 0.0, bh / 2 - C.PORT_FLANGE_T + 0.1), (bar_len + 1.0, bt, bh)))   # 0.1 up: no coplanar bottoms
    pw, ph, pt = C.CHEEK_PAD
    L.union(hook, L.add_box_local("pad", M, (C.PORT_FLANGE / 2 + bar_len + pt / 2, 0.0, ph / 2 - C.PORT_FLANGE_T), (pt, pw, ph)))   # pad on the bed plane; bar 0.1 up (solver hygiene)
    L.cut(hook, L.add_cyl_local("xbolt", M, (0.0, 0.0, C.PORT_XBOLT_DEPTH), C.M3_CLEAR_DIA / 2, C.PORT_SQ + 4, axis="X", verts=24))
    return hook


def print_rot(side=+1) -> Matrix:
    return local_frame(side).inverted()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    L.finalize_and_export(make(side), args.out, print_rot(side), NOTES)
