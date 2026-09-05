#!/usr/bin/env -S blender --background --python
"""
build_hub_bracket.py -- vp0.2 pivot hub, bolted to the pod cup face.

Ø44 x 5 disc + Ø26 x 3 serrated boss. M5 socket-head pocket on the underside
(bolt head hidden between bracket and cup), three M3 nut pockets on the top
face (bolts come from inside the cup). Separate from the cup so the cup can
print face-down and so the joint can be swapped for a different design.

Print: boss up. No supports. Qty: 2.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
from mathutils import Vector  # type: ignore

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = ["print boss up; no supports", "hardware: 1x M5x30 socket head (pocket underneath), 3x M3 nuts in the top pockets"]


def make(side: int = +1):
    axis = "Y" if side > 0 else "-Y"
    yc = side * C.CUP_FACE_Y
    rb, rp = C.M5_CLEAR_DIA / 2, C.M5_HEAD_POCKET_DIA / 2
    prof = [(rb, C.M5_HEAD_POCKET_DEPTH), (rp, C.M5_HEAD_POCKET_DEPTH), (rp, 0.0), (C.HUB_BRACKET_D / 2, 0.0),
            (C.HUB_BRACKET_D / 2, C.HUB_DISC_T), (C.HUB_BOSS_D / 2, C.HUB_DISC_T), (C.HUB_BOSS_D / 2, C.HUB_T), (rb, C.HUB_T)]
    hub = L.revolve("hub_bracket", prof, axis=axis, center=(C.CX, yc, C.CZ), segments=128)
    for ang in C.HUB_BOLT_ANGLES:
        a = math.radians(ang)
        x, z = C.CX + C.HUB_BOLT_R * math.cos(a), C.CZ + C.HUB_BOLT_R * math.sin(a)
        L.cut(hub, L.add_cyl("bolt", (x, yc + side * C.HUB_DISC_T / 2, z), C.M3_CLEAR_DIA / 2, C.HUB_DISC_T + 2, axis="Y", verts=24))
        L.cut(hub, L.add_hex_prism("nut", (x, yc + side * (C.HUB_DISC_T - C.HUB_NUT_POCKET_DEPTH / 2 + 0.5), z),
                                   C.M3_NUT_AF + 0.3, C.HUB_NUT_POCKET_DEPTH + 1.0, axis="Y"))
    L.union(hub, L.serration_solid("hub_serr", (C.CX, yc + side * C.HUB_T, C.CZ), (0.0, side, 0.0)))
    return hub


if __name__ == "__main__":
    L.std_main(lambda: make(+1), PRINT_ROT, NOTES)
