#!/usr/bin/env -S blender --background --python
"""
build_side_cap.py -- vp0 side cap: the visible outer "disk" face.

Flat Ø119.3 disc that seats in the side dish's skirt rabbet, with the
integral pivot hub (Ø40 x 6 boss, serrated top, M5 socket-head pocket
on the inner face), four radial cosmetic grooves, one ring groove and
six M3 counterbored screw holes into the dish bosses.

Print: outer face UP (inner face on the bed). No supports.
Qty: 2 (identical L/R -- the pattern is mirror-symmetric).

Run:
    blender --background --python tools/blender/vp0/build_side_cap.py -- \\
        --out 3D-Models/HelmKit/_generated/vp0/side_cap.stl
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

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = [
    "print outer face up; no supports; 0.2 mm layers; 4 walls",
    f"seats in dish rabbet ID {2*C.RABBET_IN_R:.1f} (cap OD {2*C.CAP_R:.1f}, {C.FIT_CLEAR} mm/side)",
    "hardware: 1x M5x45 socket head (head in pocket, inner side), 6x M3x8 button head",
]


def make(side: int = +1):
    axis = "Y" if side > 0 else "-Y"
    n_top = C.CAP_T + C.HUB_BOSS_H
    gi, go = C.CAP_RING_GROOVE
    gd = C.CAP_T - C.CAP_GROOVE_D
    prof = [
        (C.M5_CLEAR_DIA / 2, C.M5_HEAD_POCKET_DEPTH),
        (C.M5_HEAD_POCKET_DIA / 2, C.M5_HEAD_POCKET_DEPTH),
        (C.M5_HEAD_POCKET_DIA / 2, 0.0),
        (C.CAP_R, 0.0),
        (C.CAP_R, C.CAP_T),
        (go, C.CAP_T), (go, gd), (gi, gd), (gi, C.CAP_T),      # ring groove, in-profile
        (C.HUB_BOSS_D / 2, C.CAP_T),
        (C.HUB_BOSS_D / 2, n_top),
        (C.M5_CLEAR_DIA / 2, n_top),
    ]
    y0 = side * C.CAP_IN_Y
    cap = L.revolve("side_cap", prof, axis=axis, center=(0.0, y0, 0.0))

    y_face = side * C.CAP_OUT_Y
    # Boolean order matters for the EXACT solver: holes first, cosmetics, serration last.
    for ang in C.CAP_SCREW_ANGLES:
        x, z = C.CAP_SCREW_R * math.cos(math.radians(ang)), C.CAP_SCREW_R * math.sin(math.radians(ang))
        L.cut(cap, L.add_cyl("screw", (x, y0 + side * C.CAP_T / 2, z), C.M3_CLEAR_DIA / 2, C.CAP_T + 2, axis="Y", verts=32))
        L.cut(cap, L.add_cyl("cbore", (x, y_face, z), C.CAP_SCREW_CBORE_DIA / 2, 2 * C.CAP_SCREW_CBORE_D, axis="Y", verts=32))
    # radial grooves
    r0, r1 = C.CAP_GROOVE_R0, C.CAP_GROOVE_R1
    for ang in C.CAP_GROOVE_ANGLES:
        g = L.add_box("groove", ((r0 + r1) / 2, y_face, 0.0), (r1 - r0, 2 * C.CAP_GROOVE_D, C.CAP_GROOVE_W))
        g.matrix_world = Matrix.Rotation(math.radians(ang), 4, "Y") @ g.matrix_world
        L.apply_transform(g)
        L.cut(cap, g)
    # serration last (see vp0lib.serrate)
    L.union(cap, L.serration_solid("hub_serr", (0.0, side * C.HUB_TOP_Y, 0.0), (0.0, side, 0.0)))
    return cap


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    L.finalize_and_export(make(+1), args.out, PRINT_ROT, NOTES)


if __name__ == "__main__":
    main()
