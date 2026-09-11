#!/usr/bin/env -S blender --background --python
"""
build_visor_slider.py -- vp0.11 visor pawl slider (one STL serves both sides).

Lives in the tunnel along the brow rail's axis: a 2.6 x 3.0 bar whose tip drops into one of the 24 notches in the
spool hub, a 1.4 mm stem carrying a Ø3 x 10 compression spring against the tunnel's step at r 36, and a thumb tab
rising through the rail's top edge at r 36.5..39.5. Pull the tab 2.2 mm, swing the visor, let go. PETG.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_brow_rail as BR
from mathutils import Matrix, Vector  # type: ignore

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = ["PETG. print flat (2.6 mm), tab in-plane; no supports", "slide into the rail tunnel from the bore end with the Ø3 x 10 spring on the stem, then fit the rail on the hub; it is the visor's fuse"]


def make(side=+1):
    vp = C.VISOR_PAWL
    Mr = BR.rail_frame(C.RAIL_ANGLE, side)
    st, sh = vp["slider"]
    yc = side * (vp["y0"] + vp["slot"][0] / 2.0)
    tip0, tip1 = vp["tip_r"]
    body1 = vp["body_r"]
    sl = L.add_box_local("visor_slider", Mr, ((tip1 + 0.5 + body1) / 2.0, yc, 0.0), (body1 - tip1 - 0.5, st, sh))
    L.union(sl, L.add_box_local("tip", Mr, ((tip0 + tip1 + 1.0) / 2.0, yc, 0.0), (tip1 + 1.0 - tip0, st, vp["tip_w"])))   # narrower tip: hub lands stay 1.4 mm
    _, stem_w = vp["stem"]
    L.union(sl, L.add_box_local("stem", Mr, ((body1 - 0.1 + vp["r_out"] - 1.0) / 2.0, yc, 0.0), (vp["r_out"] - 1.0 - body1 + 0.1, st, stem_w)))
    ts0, ts1 = vp["tab_s"]
    L.union(sl, L.add_box_local("tab", Mr, ((ts0 + ts1) / 2.0, yc, vp["tab_h"] / 2.0 - 0.1), (ts1 - ts0 - 0.4, st, vp["tab_h"])))
    L.fillet(sl, width=0.4)
    return sl


if __name__ == "__main__":
    L.std_main(lambda: make(+1), PRINT_ROT, NOTES)
