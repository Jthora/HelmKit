#!/usr/bin/env -S blender --background --python
"""
build_brow_link.py -- vp0.11 brow link (left; --mirror for right).

Joins the brow rail to the centre panel out of sight: a 3.5 mm lap that fills the rail's inner half over s 75..90
(two M3 tapped along y), then a 7 x 20 bar bending 53 deg inboard behind the panel into a pocket in the panel's back
face (12 deep, two M3 tapped from below). LED cable groove along its underside continues the rail's.
Print: standing on the bar's bottom edge (the panel's thickness direction up), so the bend is in-layer. Qty: 1 L + 1 R.
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

PRINT_ROT = L.rot_dir_to(C.BROW_EZ, (0.0, 0.0, 1.0))
NOTES = ["print standing on the bottom edge (brim); no supports; the bend is in-plane",
         "lap into the rail's inner half (2x M3 x 10 from the rail's outer face), bar into the panel's back pocket (2x M3 x 16 from the panel's underside)"]


def link_frame(side):
    """Origin at the bend point on the rail axis; local X along the bar (inboard-forward), local Z tangential (= panel z)."""
    Mr = BR.rail_frame(C.RAIL_ANGLE, side)
    return Mr @ Matrix.Translation((C.RAIL_S1, side * (C.RAIL_Y0 + C.RAIL_T / 2.0), 0.0)) @ Matrix.Rotation(-side * math.radians(C.BROW_LINK["angle"]), 4, "Z")


def make(side=+1):
    Mr = BR.rail_frame(C.RAIL_ANGLE, side)
    lap0, lap1 = C.RAIL_LAP
    lt = C.BROW_LINK["lap_t"]
    link = L.add_box_local("brow_link", Mr, ((lap0 + lap1) / 2.0, side * (C.RAIL_Y0 + 0.1 + (lt - 0.1) / 2.0), 0.0), (lap1 - lap0, lt - 0.1, C.RAIL_H - 0.2))   # 0.1 inside the bar's faces (inner face too): no coplanar union
    L.fillet(link, width=0.8)                                   # same rounding as the bar: their edges merge instead of leaving slivers
    Mb = link_frame(side)
    Lb = C.BROW_LINK_LEN + C.BROW_LINK["pocket_depth"]
    bar = L.add_box_local("bar", Mb, (Lb / 2.0, 0.0, 0.0), (Lb, C.RAIL_T, C.RAIL_H))
    L.fillet(bar, width=0.8)
    L.union(link, bar)
    for s_b in C.RAIL_BOLTS_S:                                   # taps for the rail bolts, through the lap
        L.cut(link, L.add_cyl_local("tap", Mr, (s_b, side * (C.RAIL_Y0 + lt / 2.0), 0.0), C.M3_TAP_DIA / 2.0, lt + 2.0, axis="Y", verts=16))
    hh = C.RAIL_H / 2.0
    for d in C.BROW_LINK["screws_d"]:                            # taps from the bar's underside, inside the panel pocket
        L.cut(link, L.add_cyl_local("ptap", Mb, (C.BROW_LINK_LEN + d, 0.0, -hh - 1.0 + 5.0), C.M3_TAP_DIA / 2.0, 10.0, axis="Z", verts=16))
    cd, cw = C.RAIL_CHANNEL[0], C.RAIL_CHANNEL[1]
    L.cut(link, L.add_box_local("cablech", Mb, ((4.0 + C.BROW_LINK_LEN - 1.0) / 2.0, 0.0, -hh - 1.0 + (cd + 1.0) / 2.0), (C.BROW_LINK_LEN - 1.0 - 4.0, cw, cd + 1.0)))   # bar only, from 4 mm past the bend to the panel face
    return link


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    L.finalize_and_export(make(side), args.out, PRINT_ROT, NOTES)
