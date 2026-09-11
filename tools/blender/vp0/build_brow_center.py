#!/usr/bin/env -S blender --background --python
"""
build_brow_center.py -- vp0.7 brow centre panel: 160 x 50 x 15 shell with a top bead.

LED bay open to the head side (lid), LED window in the bottom face, solid
ends with two M3 tap holes each for the slider flanges. Leans back 13 deg.
Print: standing on its bottom face. Qty: 1.
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
NOTES = ["print standing on the bottom face; brim; no supports; faceplate recess on the front, link pockets in the back face",
         "sliders: two M3 x 10 thread-forming into each end face; lid: 4x M3 x 8"]


def make():
    panel = L.add_box_local("brow_center", MP, (T / 2, 0.0, H / 2), (T, W, H))
    L.union(panel, L.add_cyl_local("bead", MP, (T / 2, 0.0, H), C.BROW_TOP_BEAD_R, W - 0.4, axis="Y", verts=32))   # ends 0.2 inside: no coplanar caps
    # cavity opens to the FRONT: the faceplate (brow_lid) sits in a recess in the front face; the back face stays solid for the link pockets
    cav_x0, cav_x1 = C.BROW_WALL, T - LID_RECESS
    L.cut(panel, L.add_box_local("cavity", MP, ((cav_x0 + cav_x1) / 2, 0.0, H / 2), (cav_x1 - cav_x0, C.BROW_CAV_W, C.BROW_CAV_H)))
    L.cut(panel, L.add_box_local("recess", MP, (T - LID_RECESS / 2 + 1.0, 0.0, H / 2), (LID_RECESS + 2.0, C.BROW_CAV_W + 8.0, C.BROW_FACEPLATE_H + 0.4)))
    ww, wt = C.BROW_LED_WINDOW
    L.cut(panel, L.add_box_local("ledwin", MP, (T / 2 - 1.0, 0.0, (H - C.BROW_CAV_H) / 2 - 1.0), (wt, ww, (H - C.BROW_CAV_H) / 2 + 1.0)))
    for y, z in C.BROW_LID_SCREWS:
        L.cut(panel, L.add_cyl_local("lidscrew", MP, (T - 6.0, y, z), C.M3_TAP_DIA / 2, 12.0, axis="X", verts=16))
    # link pockets in the back face, 55 deg inboard, with screw clearance from the underside and a cable hole into the cavity
    pd = C.BROW_LINK["pocket_depth"]
    for side in (+1, -1):
        Mk = MP @ Matrix.Translation((0.0, side * C.BROW_POCKET_Y, C.BROW_POCKET_Z)) @ Matrix.Rotation(-side * math.radians(C.BROW_LINK["angle"]), 4, "Z")
        L.cut(panel, L.add_box_local("pocket", Mk, ((pd - 1.0) / 2, 0.0, 0.0), (pd + 1.0, C.RAIL_T + 0.3, C.RAIL_H + 0.3)))
        # mouth relief: a straight 1.5 mm recess around the pocket's opening so the 35-deg lip is not a knife edge
        mw = (C.RAIL_T + 0.3) / math.cos(math.radians(C.BROW_LINK["angle"])) + 2.0
        L.cut(panel, L.add_box_local("mouth", MP, (0.25, side * (C.BROW_POCKET_Y - 1.0), C.BROW_POCKET_Z), (2.5, mw, C.RAIL_H - 0.6)))   # shorter than the pocket: its top and bottom lie inside the pocket void, no shared planes, no ledge
        zb = -C.BROW_POCKET_Z - 1.0                                  # panel underside in pocket coordinates
        zt = -(C.RAIL_H + 0.3) / 2 + 0.5
        for d in C.BROW_LINK["screws_d"]:
            L.cut(panel, L.add_cyl_local("pscrew", Mk, (d, 0.0, (zb + zt) / 2), C.M3_CLEAR_DIA / 2, zt - zb, axis="Z", verts=16))
        L.cut(panel, L.add_cyl_local("pcable", MP, (6.5, side * (C.BROW_CAV_W / 2 + 2.5), C.BROW_POCKET_Z - 4.0), 2.0, 9.0, axis="Y", verts=16))   # from the pocket's end straight into the cavity
    L.fillet(panel, width=1.0)    # last
    return panel


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
