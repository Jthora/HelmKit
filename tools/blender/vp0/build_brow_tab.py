#!/usr/bin/env -S blender --background --python
"""
build_brow_tab.py -- vp0.9 brow tab (left; --mirror for right).

L-bracket on each end of the centre panel: a flange screwed to the panel's
end face (2x M3 x 10) and an arm reaching outboard to the rail's inner face
with two M3 tap holes; the rail bolts onto it. Fixed reach.
Print: flange down. Qty: 1 L + 1 R.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_brow_center as BP
from mathutils import Matrix, Vector  # type: ignore

NOTES = ["print flange face down; no supports", "2x M3 x 10 into the panel end; the rail bolts to the arm with 2x M3 x 12 into the tap holes"]
T, H, W = C.BROW_T, C.BROW_H, C.BROW_CENTER_W


def rail_point_local(s, MP):
    a = math.radians(C.RAIL_ANGLE)
    return MP.inverted() @ Vector((C.CX + s * math.cos(a), 0.0, C.CZ + s * math.sin(a)))


def make(side=+1):
    MP = BP.MP
    ft = C.BROW_TAB["flange_t"]
    tab = L.add_box_local("brow_tab", MP, (T / 2.0, side * (W / 2.0 + ft / 2.0), H / 2.0), (T - 2.0, ft, H - 4.0))
    L.fillet(tab, width=0.8)
    p0, p1 = rail_point_local(C.RAIL_BOLTS_S[0], MP), rail_point_local(C.RAIL_BOLTS_S[1], MP)
    zc = (p0.z + p1.z) / 2.0
    y_arm0, y_arm1 = W / 2.0 + ft - 0.5, C.RAIL_Y0
    arm = L.add_box_local("arm", MP, (T / 2.0, side * (y_arm0 + y_arm1) / 2.0, zc), (T - 1.0, y_arm1 - y_arm0, C.RAIL_H))
    L.fillet(arm, width=0.8)
    L.union(tab, arm)
    for p in (p0, p1):
        L.cut(tab, L.add_cyl_local("tap", MP, (p.x, side * (y_arm1 - 3.0), p.z), C.M3_TAP_DIA / 2.0, 8.0, axis="Y", verts=16))
    for z in C.BROW_END_SCREWS:
        L.cut(tab, L.add_cyl_local("fscrew", MP, (T / 2.0, side * (W / 2.0 + ft / 2.0), z), C.M3_CLEAR_DIA / 2.0, ft + 2.0, axis="Y", verts=16))
        L.cut(tab, L.add_cyl_local("fhead", MP, (T / 2.0, side * (W / 2.0 + ft + 0.6), z), 3.1, 3.2, axis="Y", verts=16))
    return tab


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    L.finalize_and_export(make(side), args.out, L.ROT_Y_TO_Z if side > 0 else L.ROT_NEGY_TO_Z, NOTES)
