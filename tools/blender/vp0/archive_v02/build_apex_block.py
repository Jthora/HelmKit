#!/usr/bin/env -S blender --background --python
"""
build_apex_block.py -- vp0.2 crown apex sleeve: joins the two arch halves.

40 x 64 x 10.4 sleeve with a 30.6 x 5.4 through-channel for the two overlap
bars, an M4 clamp bolt across X (nut pocket on the -X face), a foam crown
pad on the underside and a standard port socket on top.

Print: standing on end (channel vertical). No supports. Qty: 1.
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
from mathutils import Vector  # type: ignore

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = ["print standing on its end; no supports", "hardware: 1x M4x50 + nut (clamp); 12 mm foam pad glued underneath"]


def make():
    sx, sy, sz = C.APEX_SLEEVE
    cw, ch = C.CROWN_W + 0.6, C.CROWN_T + 0.4
    zA = C.CROWN_APEX_Z
    zc = zA - ch / 2 - C.APEX_FLOOR_T + sz / 2
    blk = L.add_box("apex_block", (C.CX, 0.0, zc), (sx, sy, sz))
    Mp = L.frame((C.CX, 0.0, zc + sz / 2 + C.PORT_BOSS_H), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
    L.union(blk, L.port_boss("apex_boss", Mp))
    L.cut(blk, L.add_box("channel", (C.CX, 0.0, zA), (cw, sy + 4, ch)))
    L.cut(blk, L.add_cyl("m4", (C.CX, 0.0, zA), C.M4_CLEAR_DIA / 2, sx + 4, axis="X", verts=32))
    L.cut(blk, L.add_hex_prism("m4nut", (C.CX - sx / 2 + C.M4_NUT_T / 2 - 0.5, 0.0, zA), C.M4_NUT_AF + 0.3, C.M4_NUT_T + 1.0, axis="X"))
    L.cut(blk, *L.port_cutters(Mp, tag="apex", header=False))
    return blk


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
