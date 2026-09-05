#!/usr/bin/env -S blender --background --python
"""
build_brow_slider.py -- vp0.8 brow slider (left; --mirror for right).

Flange screwed to the centre panel's end face (2x M3), extended backward as a
foot, carrying a short arm outboard to a sleeve that rides the 7 x 20 rail
(which runs along the panel's own tilt, so everything is one frame). An M3
pin through the sleeve into a rail hole sets the reach; its nut sits in a slot
in the arm. Print: flange down. Qty: 1 L + 1 R.
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

NOTES = ["print flange face down; the sleeve bore bridges 7.6 mm; no supports",
         "2x M3 x 10 into the panel end; reach pin M3 x 20 + knob, nut dropped into the arm's slot"]
T, H, W = C.BROW_T, C.BROW_H, C.BROW_CENTER_W


def make(side=+1):
    MP = BP.MP
    a = math.radians(C.RAIL_ANGLE)
    p_rail = Vector((C.CX + C.RAIL_S0 * math.cos(a), 0.0, C.CZ + C.RAIL_S0 * math.sin(a)))
    pl = MP.inverted() @ p_rail                      # sleeve centre in panel coordinates (x along the rail)
    y_rail = C.RAIL_Y0 + C.RAIL_T / 2.0               # 101.6
    sw, wall = C.SLIDER_SLEEVE
    so_y, so_z = C.RAIL_T + 0.6 + 2 * wall, C.RAIL_H + 0.6 + 2 * wall      # 13.6, 26.6
    ft, fx0 = C.SLIDER_FLANGE_T, C.SLIDER_FOOT_X0
    sl = L.add_box_local("brow_slider", MP, ((fx0 + T - 1.0) / 2.0, side * (W / 2.0 + ft / 2.0), H / 2.0), (T - 1.0 - fx0, ft, H - 4.0))
    L.fillet(sl, width=0.8)
    y_arm0, y_arm1 = W / 2.0 + ft - 0.5, y_rail - so_y / 2.0 + 0.1
    arm = L.add_box_local("arm", MP, (pl.x, side * (y_arm0 + y_arm1) / 2.0, pl.z), (sw - 0.2, y_arm1 - y_arm0, so_z - 0.2))
    sleeve = L.add_box_local("sleeve", MP, (pl.x, side * y_rail, pl.z), (sw, so_y, so_z))
    for b in (arm, sleeve):
        L.fillet(b, width=0.8)
        L.union(sl, b)
    L.cut(sl, L.add_box_local("bore", MP, (pl.x, side * y_rail, pl.z), (sw + 2.0, C.RAIL_T + 0.6, C.RAIL_H + 0.6)))
    L.cut(sl, L.add_cyl_local("pin", MP, (pl.x, side * (y_rail + 2.0), pl.z), C.M3_CLEAR_DIA / 2.0, so_y + 6.0, axis="Y", verts=16))
    ny = y_rail - so_y / 2.0 - 1.5
    L.cut(sl, L.add_box_local("nutslot", MP, (pl.x, side * ny, pl.z + 4.0), (5.8, 2.6, 22.0)))
    for z in C.BROW_END_SCREWS:
        L.cut(sl, L.add_cyl_local("fscrew", MP, (T / 2.0, side * (W / 2.0 + ft / 2.0), z), C.M3_CLEAR_DIA / 2.0, ft + 2.0, axis="Y", verts=16))
        L.cut(sl, L.add_cyl_local("fhead", MP, (T / 2.0, side * (W / 2.0 + ft + 0.6), z), 3.1, 3.2, axis="Y", verts=16))
    return sl


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    L.finalize_and_export(make(side), args.out, L.ROT_Y_TO_Z if side > 0 else L.ROT_NEGY_TO_Z, NOTES)
