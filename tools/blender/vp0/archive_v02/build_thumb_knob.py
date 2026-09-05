#!/usr/bin/env -S blender --background --python
"""
build_thumb_knob.py -- vp0.2 low-profile pivot knob with a captive M5 nut.

Ø34 x 8, 14 scallops, hex pocket open outboard. Print bearing face down. Qty: 2.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = ["print bearing face down; no supports", "hardware: 1x M5 nut pressed into the pocket"]


def make(side: int = +1):
    axis = "Y" if side > 0 else "-Y"
    yc = side * C.NUT_FACE_Y
    rb, rk = C.KNOB_BORE / 2, C.KNOB_D / 2
    knob = L.revolve("thumb_knob", [(rb, 0.0), (rk, 0.0), (rk, C.KNOB_H), (rb, C.KNOB_H)], axis=axis,
                     center=(C.CX, yc, C.CZ), segments=96)
    d = C.KNOB_POCKET_DEPTH
    L.cut(knob, L.add_hex_prism("hex", (C.CX, yc + side * (C.KNOB_H - d / 2 + 0.5), C.CZ), C.M5_NUT_AF + 0.3, d + 1.0, axis="Y"))
    for k in range(C.KNOB_SCALLOPS):
        a = 2 * math.pi * k / C.KNOB_SCALLOPS
        rr = rk + 0.8
        L.cut(knob, L.add_cyl("scallop", (C.CX + rr * math.cos(a), yc + side * C.KNOB_H / 2, C.CZ + rr * math.sin(a)),
                              C.KNOB_SCALLOP_D / 2, C.KNOB_H + 2, axis="Y", verts=24))
    return knob


if __name__ == "__main__":
    L.std_main(lambda: make(+1), PRINT_ROT, NOTES)
