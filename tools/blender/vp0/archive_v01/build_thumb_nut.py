#!/usr/bin/env -S blender --background --python
"""
build_thumb_nut.py -- vp0 thumb-nut: captive M5 nut in a scalloped knob.

Ø30 x 14 knob, Ø5.6 bore, hex pocket (8.3 AF x 4.5) open on the
outboard face, 12 scallops. Loosen to fold the rear band / brow plate,
tighten to lock the serrations.

Print: bearing face down. No supports.
Qty: 2.

Run:
    blender --background --python tools/blender/vp0/build_thumb_nut.py -- \\
        --out 3D-Models/HelmKit/_generated/vp0/thumb_nut.stl
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = ["print bearing face down, pocket up; no supports", "hardware: 1x M5 DIN 934 nut pressed into the pocket"]


def make(side: int = +1):
    axis = "Y" if side > 0 else "-Y"
    y0 = side * C.NUT_FACE_Y
    r_b, r_k = C.NUT_BORE / 2, C.NUT_KNOB_D / 2
    knob = L.revolve("thumb_nut", [(r_b, 0.0), (r_k, 0.0), (r_k, C.NUT_KNOB_H), (r_b, C.NUT_KNOB_H)],
                     axis=axis, center=(0.0, y0, 0.0), segments=96)
    d = C.NUT_POCKET_DEPTH
    L.cut(knob, L.add_hex_prism("hexpocket", (0.0, y0 + side * (C.NUT_KNOB_H - d / 2 + 0.5), 0.0),
                                C.M5_NUT_AF + 0.3, d + 1.0, axis="Y"))
    for k in range(C.NUT_SCALLOPS):
        a = 2 * math.pi * k / C.NUT_SCALLOPS
        rr = r_k + 0.8
        L.cut(knob, L.add_cyl("scallop", (rr * math.cos(a), y0 + side * C.NUT_KNOB_H / 2, rr * math.sin(a)),
                              C.NUT_SCALLOP_D / 2, C.NUT_KNOB_H + 2, axis="Y", verts=24))
    return knob


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    L.finalize_and_export(make(+1), args.out, PRINT_ROT, NOTES)


if __name__ == "__main__":
    main()
