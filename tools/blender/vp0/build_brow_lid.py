#!/usr/bin/env -S blender --background --python
"""build_brow_lid.py -- vp0.11 brow FACEPLATE (front), 4 screws into the top and bottom walls. Print flat. Qty: 1."""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_brow_center as BP

PRINT_ROT = L.rot_dir_to(C.BROW_EX, (0, 0, 1))
NOTES = ["print flat (outer face down for a clean finish); the LED strip sits behind it; 4x M3 x 8 thread-forming"]


def make():
    x0 = C.BROW_T - BP.LID_RECESS + 0.2
    lid = L.add_box_local("brow_lid", BP.MP, (x0 + C.BROW_LID_T / 2, 0.0, C.BROW_H / 2),
                          (C.BROW_LID_T, C.BROW_CAV_W + 8.0 - 0.4, C.BROW_FACEPLATE_H - 0.4))
    for y, z in C.BROW_LID_SCREWS:
        L.cut(lid, L.add_cyl_local("hole", BP.MP, (x0 + C.BROW_LID_T / 2, y, z), C.M3_CLEAR_DIA / 2, 6.0, axis="X", verts=16))
    L.fillet(lid, width=0.6)
    return lid


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
