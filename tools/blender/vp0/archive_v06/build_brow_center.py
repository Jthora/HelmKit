#!/usr/bin/env -S blender --background --python
"""
build_brow_center.py -- vp0.5 brow centre panel: 100 x 50 x 15 shell with a top bead.

LED bay open to the head side (lid), LED window in the bottom face, solid
ends with a tenon pocket for each wing-spar, two vertical nail holes per
tenon. Leans back 13 deg. Print: standing on its bottom face. Qty: 1.
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

MP = L.frame(C.BROW_ORIGIN, C.BROW_EZ, C.BROW_EX)          # local x outward, y = +Y, z up (tilted)
PRINT_ROT = L.rot_dir_to(C.BROW_EZ, (0, 0, 1))
T, H, W = C.BROW_T, C.BROW_H, C.BROW_CENTER_W
LID_RECESS = 2.2
NOTES = ["print standing on the bottom face; brim; tenon pockets bridge 12 mm; no supports",
         "wings: tenon in, two nails from the top bead through each tenon, epoxy the joint",
         "hardware: 4x M3x8 thread-forming (lid); 4 nails ~3 mm x 60 mm; 60x44x12 foam pad on the lid"]


def make():
    panel = L.add_box_local("brow_center", MP, (T / 2, 0.0, H / 2), (T, W, H))
    L.union(panel, L.add_cyl_local("bead", MP, (T / 2, 0.0, H), C.BROW_TOP_BEAD_R, W - 0.4, axis="Y", verts=32))   # ends 0.2 inside: no coplanar caps
    cav_x0, cav_x1 = LID_RECESS, T - C.BROW_WALL
    L.cut(panel, L.add_box_local("cavity", MP, ((cav_x0 + cav_x1) / 2, 0.0, H / 2), (cav_x1 - cav_x0, C.BROW_CAV_W, H - 8.0)))
    L.cut(panel, L.add_box_local("recess", MP, (LID_RECESS / 2 - 1.0, 0.0, H / 2), (LID_RECESS + 2.0, C.BROW_CAV_W + 8.0, H - 2 * C.BROW_WALL + 0.4)))
    ww, wt = C.BROW_LED_WINDOW
    L.cut(panel, L.add_box_local("ledwin", MP, (T / 2, 0.0, 1.5), (wt, ww, 7.0)))
    for y, z in C.BROW_LID_SCREWS:
        L.cut(panel, L.add_cyl_local("lidscrew", MP, (4.0, y, z), C.M3_TAP_DIA / 2, 12.0, axis="X", verts=16))
    tx, tz, td = C.BROW_TENON
    for side in (+1, -1):
        L.cut(panel, L.add_box_local("tenon_pocket", MP, (T / 2, side * (W / 2 - td / 2 + 1.0), (tz + 2.0) / 2 - 1.0),
                                     (tx + 0.3, td + 2.0, tz + 2.3)))
        for d in C.BROW_TENON_PINS:
            L.cut(panel, L.add_cyl_local("tenonhead", MP, (T / 2, side * (W / 2 - d), H + 4.4), C.PIN_HEAD_DIA / 2, 8.0, axis="Z", verts=36))   # floor 0.4 above the panel top, well inside the bead
            L.cut(panel, L.add_cyl_local("tenonpin", MP, (T / 2, side * (W / 2 - d), H / 2), C.PIN_DIA / 2, H + 10.0, axis="Z", verts=24))
    L.fillet(panel, width=1.0)    # last
    return panel


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
