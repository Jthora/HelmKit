#!/usr/bin/env -S blender --background --python
"""
build_side_dish.py -- vp0 side dish: Ø122.1 semi-parabolic reflector + skirt.

Paraboloid bowl (sag 16 mm, f/D 0.44) concave toward the head, 3 mm
wall, inside a Ø122.1 cylindrical skirt. The skirt end is rabbeted for
the side cap; six M3 heat-set bosses sit inside the skirt at that end.
A 2 mm lip at the rim locates the foam ear cushion. Ø4 vent at the vertex.

Print: skirt end (cap end) DOWN, bowl concave up. The bowl's underside
needs supports inside the skirt (hidden in the electronics cavity);
the head-facing reflector surface prints clean.
Qty: 2 (identical L/R).

Run:
    blender --background --python tools/blender/vp0/build_side_dish.py -- \\
        --out 3D-Models/HelmKit/_generated/vp0/side_dish.stl
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

PRINT_ROT = L.ROT_NEGY_TO_Z
NOTES = [
    "print skirt end down, bowl concave up; supports ON, build-plate only (they grow inside the skirt under the bowl)",
    f"paraboloid: sag {C.DISH_DEPTH} over rim r {C.SKIRT_IN_R:.2f}; focal {C.DISH_FOCAL:.1f} mm; focus is {C.DISH_FOCAL - C.DISH_DEPTH:.1f} mm inboard of the rim plane",
    "hardware: 6x M3 heat-set (5.0 OD) in the bosses; foam ring OD 122 / ID ~88 / 12 mm glued to rim",
]


def bowl_n(r: float) -> float:
    return C.N_VERTEX + C.DISH_DEPTH * (r / C.SKIRT_IN_R) ** 2


def make(side: int = +1):
    axis = "-Y" if side > 0 else "Y"          # n increases toward the head
    y0 = side * C.CAP_OUT_Y
    rv = C.VENT_DIA / 2
    rs = [C.SKIRT_IN_R - (C.SKIRT_IN_R - rv) * i / 40 for i in range(41)]
    prof = [
        (C.DISH_R, 0.0),
        (C.DISH_R, C.N_LIP_TOP),
        (C.DISH_R - C.LIP_W, C.N_LIP_TOP),
        (C.DISH_R - C.LIP_W, C.N_RIM),
    ]
    prof += [(r, bowl_n(r)) for r in rs]                       # concave face, rim -> vent
    prof += [(r, bowl_n(r) - C.DISH_WALL) for r in reversed(rs)]  # underside, vent -> rim
    prof += [
        (C.SKIRT_IN_R, C.N_CAP_INNER),
        (C.RABBET_IN_R, C.N_CAP_INNER),
        (C.RABBET_IN_R, 0.0),
    ]
    dish = L.revolve("side_dish", prof, axis=axis, center=(0.0, y0, 0.0), segments=160)

    # heat-set bosses at the cap end, inside the skirt, webbed to the wall
    n_c = C.N_CAP_INNER + C.BOSS_H / 2
    y_c = side * (C.CAP_OUT_Y - n_c)
    for ang in C.CAP_SCREW_ANGLES:
        a = math.radians(ang)
        x, z = C.CAP_SCREW_R * math.cos(a), C.CAP_SCREW_R * math.sin(a)
        L.union(dish, L.add_cyl("boss", (x, y_c, z), C.BOSS_D / 2, C.BOSS_H, axis="Y", verts=32))
        web_r0, web_r1 = C.CAP_SCREW_R, C.SKIRT_IN_R + 1.0
        w = L.add_box("web", ((web_r0 + web_r1) / 2, y_c, 0.0), (web_r1 - web_r0, C.BOSS_H, C.BOSS_D))
        w.matrix_world = Matrix.Rotation(-a, 4, "Y") @ w.matrix_world   # Ry(-a) maps +X to (cos a, 0, sin a)
        L.apply_transform(w)
        L.union(dish, w)
    # trim anything that poked outside the skirt OD (web boxes), then drill
    L.cut(dish, L.revolve("trim", [(C.DISH_R, -1.0), (C.DISH_R + 20, -1.0), (C.DISH_R + 20, C.N_LIP_TOP + 1), (C.DISH_R, C.N_LIP_TOP + 1)],
                          axis=axis, center=(0.0, y0, 0.0), segments=160))
    for ang in C.CAP_SCREW_ANGLES:
        a = math.radians(ang)
        x, z = C.CAP_SCREW_R * math.cos(a), C.CAP_SCREW_R * math.sin(a)
        n_h = C.N_CAP_INNER + C.M3_HEATSET_DEPTH / 2 - 0.5
        L.cut(dish, L.add_cyl("heatset", (x, side * (C.CAP_OUT_Y - n_h), z), C.M3_HEATSET_HOLE_DIA / 2,
                              C.M3_HEATSET_DEPTH + 1.0, axis="Y", verts=32))
    return dish


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    L.finalize_and_export(make(+1), args.out, PRINT_ROT, NOTES)


if __name__ == "__main__":
    main()
