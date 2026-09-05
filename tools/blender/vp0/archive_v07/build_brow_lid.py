#!/usr/bin/env -S blender --background --python
"""build_brow_lid.py -- vp0.3 brow lid (head side), 4 screws, foam pad glues to it. Print flat. Qty: 1."""
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
NOTES = ["print flat; foam forehead pad glues to the head-side face"]


def make():
    lid = L.add_box_local("brow_lid", BP.MP, (0.2 + C.BROW_LID_T / 2, 0.0, C.BROW_H / 2),
                          (C.BROW_LID_T, C.BROW_CAV_W + 8.0 - 0.4, C.BROW_H - 2 * C.BROW_WALL))
    for y, z in C.BROW_LID_SCREWS:
        L.cut(lid, L.add_cyl_local("hole", BP.MP, (1.2, y, z), C.M3_CLEAR_DIA / 2, 6.0, axis="X", verts=16))
    L.fillet(lid, width=0.6)
    return lid


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
