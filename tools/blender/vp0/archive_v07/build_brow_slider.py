#!/usr/bin/env -S blender --background --python
"""
build_brow_slider.py -- vp0.7 brow slider (left; --mirror for right).

Flange screwed to the centre panel's end face (2x M3) and extended backward as
a foot under the whole arm, which reaches outboard to a sleeve (behind the
panel) that rides the rail; an M3 pin through the sleeve into
one of the rail's holes sets the reach (nut trapped in a slot in the arm).
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

PRINT_ROT = L.ROT_Y_TO_Z   # LEFT part: +Y (outboard) up, so the flange's inner face (-Y) is on the bed
NOTES = ["print flange face down; the sleeve bore bridges 6.6 mm; no supports",
         "2x M3 x 10 into the panel end; reach pin M3 x 20 + knob, nut dropped into the arm's slot"]
T, H, W = C.BROW_T, C.BROW_H, C.BROW_CENTER_W


def make(side=+1):
    MP = BP.MP
    ft = C.SLIDER_FLANGE_T
    fx0 = C.SLIDER_FOOT_X0
    sl = L.add_box_local("brow_slider", MP, ((fx0 + T - 1.0) / 2, side * (W / 2 + ft / 2), H / 2), (T - 1.0 - fx0, ft, H - 4.0))   # flange + foot under the whole arm
    xs = C.RAIL_HOLES_X0
    hy, hz = C.RAIL_Y, C.BROW_HINGE[2]
    sw, wall = C.SLIDER_SLEEVE
    rt, rh = C.RAIL_SECTION
    so_y, so_z = rt + 0.6 + 2 * wall, rh + 0.6 + 2 * wall       # 12.6, 26.6
    y_arm0 = W / 2 + ft - 0.5
    y_arm1 = hy - so_y / 2 + 0.1
    ax0, ax1 = C.SLIDER_ARM_X
    L.fillet(sl, width=0.8)
    # filleted primitives, then union: no global bevel pass over small steps
    arm_rear = L.add_box("arm_rear", (xs, side * (y_arm0 + y_arm1) / 2, hz + 0.05), (sw - 0.2, y_arm1 - y_arm0, so_z - 0.2))
    arm_front = L.add_box("arm_front", ((xs + 2.0 + ax1) / 2, side * (y_arm0 + 0.1 + y_arm1 - 0.1) / 2, hz + 0.05), (ax1 - xs - 2.0, y_arm1 - y_arm0 - 0.2, so_z - 0.4))
    sleeve = L.add_box("sleeve", (xs, side * hy, hz), (sw, so_y, so_z))
    for b in (arm_rear, arm_front, sleeve):
        L.fillet(b, width=0.8)
        L.union(sl, b)
    L.cut(sl, L.add_box("bore", (xs, side * hy, hz), (sw + 2.0, rt + 0.6, rh + 0.6)))
    ty0, ty1, tz0, tz1 = C.SLIDER_TUNNEL                      # lightening tunnel through the arm along x
    L.cut(sl, L.add_box("tunnel", ((ax0 + ax1) / 2, side * (ty0 + ty1) / 2, (tz0 + tz1) / 2), (ax1 - ax0 + 4.0, ty1 - ty0, tz1 - tz0)))
    L.cut(sl, L.add_cyl("pin", (xs, side * (hy + 2.0), hz), C.M3_CLEAR_DIA / 2, so_y + 6.0, axis="Y", verts=16))
    # nut slot in the arm, open at the top, just inboard of the sleeve's inner wall
    ny = hy - so_y / 2 - 1.5
    L.cut(sl, L.add_box("nutslot", (xs, side * ny, hz + 4.0), (5.8, 2.6, 22.0)))
    for z in C.BROW_END_SCREWS:
        L.cut(sl, L.add_cyl_local("fscrew", MP, (T / 2, side * (W / 2 + ft / 2), z), C.M3_CLEAR_DIA / 2, ft + 2.0, axis="Y", verts=16))
        L.cut(sl, L.add_cyl_local("fhead", MP, (T / 2, side * (W / 2 + ft + 1.0 - 1.0 + 0.6), z), 3.1, 3.2, axis="Y", verts=16))
    return sl


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    rot = L.ROT_Y_TO_Z if side > 0 else L.ROT_NEGY_TO_Z
    L.finalize_and_export(make(side), args.out, rot, NOTES)
