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

# v0.18 (2026-11-10): an OPEN-TOPPED U channel. The closed 64 mm sleeve gave the two 10 mm arch bars 0.6 mm of play
# across the pair and 0.4 through their 7 mm thickness, which the printer closes (openings print ~0.3 small, bars ~0.15
# large), and the bars' interlocking ridges had to ride over each other for 40 mm while being shoved in: an arch part snapped
# at the first assembly. Now the bars are LAID IN from above with a snug drop-in fit across them and set to span by sliding in
# the open channel; the M4 through both walls and both bars' slots clamps them together and is what keeps them in. Printed
# flat on its 34 x 64 underside, 9.4 mm tall: no bridge, no overhang, the steadiest print in the set. The 12 mm foam pad
# glues to that underside.
PRINT_ROT = L.ROT_NONE
APEX_PLAY = 1.6          # across the bar pair: 0.6 for their interleaved ridges (each face's teeth stand 0.6) + 1.0 of fit. Printed,
                         # the channel comes out ~0.3 small and the two bars ~0.3 large, leaving ~0.4: a hand fit, and less than the
                         # 0.6 the teeth need to jump out of mesh. The walls are too stiff to clamp a gap closed; the open top sands
NOTES = ["print flat on the underside (the foam-pad face), channel opening upward; no supports; 8 mm brim",
         "assembly: lay both arch bars into the channel from above with their ridged faces together, slide to set the span, then the M4 x 50 through both walls and both bars' slots, nut dropped into the pocket; tighten until the ridges lock; 12 mm foam pad underneath"]


def make():
    sx, sy, _ = C.APEX_SLEEVE
    cw, ch = C.CROWN_W + APEX_PLAY, C.CROWN_T + 0.4
    zA = C.CROWN_APEX_Z
    z0 = zA - ch / 2 - C.APEX_FLOOR_T                        # underside (the foam-pad face)
    z1 = zA + ch / 2                                          # wall tops: flush with the bars' top faces + 0.2
    blk = L.add_box("apex_block", (C.CX, 0.0, (z0 + z1) / 2), (sx, sy, z1 - z0))
    L.cut(blk, L.add_box("channel", (C.CX, 0.0, zA + 5.0), (cw, sy + 4, ch + 10.0)))      # open at the top
    L.cut(blk, L.add_teardrop("m4", (C.CX, 0.0, zA), C.M4_CLEAR_DIA / 2, sx + 4, (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), verts=32))
    L.cut(blk, L.add_teardrop("m4head", (C.CX + sx / 2 - 1.5, 0.0, zA), C.M4_HEAD_DIA / 2 + 0.4, 4.0, (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), verts=32))
    L.cut(blk, L.add_hex_prism("m4nut", (C.CX - sx / 2 + C.M4_NUT_T / 2 - 0.5, 0.0, zA), C.M4_NUT_AF + 0.3, C.M4_NUT_T + 1.0, axis="X"))
    L.fillet(blk, width=C.APEX_FILLET, segments=4)
    return blk


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
