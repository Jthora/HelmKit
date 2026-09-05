#!/usr/bin/env -S blender --background --python
"""build_brow_lid.py -- vp0.2 brow panel lid (head side). 156 x 46 x 2 plate, 4 screw holes. Print flat. Qty: 1."""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_brow_panel as BP

PRINT_ROT = L.rot_dir_to(C.BROW_EX, (0.0, 0.0, 1.0))
NOTES = ["print flat; foam forehead pad glues to the outer (head-side) face"]


def make():
    T, W, H, WALL = C.BROW_T, C.BROW_W, C.BROW_H, C.BROW_WALL
    lid = L.add_box_local("brow_lid", BP.MP, (0.2 + C.BROW_LID_T / 2, 0.0, H / 2), (C.BROW_LID_T, W - 2 * WALL, H - 2 * WALL))
    for y, z in BP.LID_SCREWS:
        L.cut(lid, L.add_cyl_local("hole", BP.MP, (1.2, y, z), C.M3_CLEAR_DIA / 2, 6.0, axis="X"))
    return lid


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
