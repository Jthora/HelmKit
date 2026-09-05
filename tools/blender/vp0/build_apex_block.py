#!/usr/bin/env -S blender --background --python
"""build_apex_block.py -- vp0.3 crown apex sleeve: joins the two arch halves. M4 clamp across X (counterbored
head, captive nut), foam crown pad glued underneath, no port on top. Print standing on end. Qty: 1."""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = ["print standing on its end; no supports", "hardware: 1x M4x50 + nut; 12 mm foam pad underneath"]


def make():
    sx, sy, sz = C.APEX_SLEEVE
    cw, ch = C.CROWN_W + 0.6, C.CROWN_T + 0.4
    zA = C.CROWN_APEX_Z
    zc = zA - ch / 2 - C.APEX_FLOOR_T + sz / 2
    blk = L.add_box("apex_block", (C.CX, 0.0, zc), (sx, sy, sz))
    L.cut(blk, L.add_box("channel", (C.CX, 0.0, zA), (cw, sy + 4, ch)))
    L.cut(blk, L.add_cyl("m4", (C.CX, 0.0, zA), C.M4_CLEAR_DIA / 2, sx + 4, axis="X", verts=32))
    L.cut(blk, L.add_cyl("m4head", (C.CX + sx / 2 - 1.5, 0.0, zA), C.M4_HEAD_DIA / 2 + 0.4, 4.0, axis="X", verts=32))
    L.cut(blk, L.add_hex_prism("m4nut", (C.CX - sx / 2 + C.M4_NUT_T / 2 - 0.5, 0.0, zA), C.M4_NUT_AF + 0.3, C.M4_NUT_T + 1.0, axis="X"))
    L.fillet(blk)
    return blk


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
