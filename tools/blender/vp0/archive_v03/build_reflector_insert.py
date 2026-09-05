#!/usr/bin/env -S blender --background --python
"""
build_reflector_insert.py -- vp0.2 paraboloid reflector, glued into the pod cup.

2 mm paraboloid (sag 8 mm, f/D 0.88 -- cosmetic for now), Ø4 vent at the
vertex, ring of Ø3 airflow holes at r=40 (inside the cushion ID) so the pod
fans can move air across the temple.

Print: concave UP, supports under the bowl (removable, hidden inside the pod).
Qty: 2. Epoxy into the cup ledge after the hub bracket is fitted.
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

PRINT_ROT = L.ROT_NEGY_TO_Z
NOTES = ["print concave up with supports (tree/organic works well); scuff the rim and epoxy into the cup ledge",
         f"sag {C.REFL_SAG} over r {C.REFL_R:.1f}; focal {C.REFL_FOCAL:.0f} mm"]


def n_top(r):
    return C.N_REFL_VERTEX + C.REFL_SAG * (r / C.REFL_R) ** 2


def make(side: int = +1):
    axis = "-Y" if side > 0 else "Y"
    yc = side * C.CUP_FACE_Y
    rv = C.VENT_DIA / 2
    rs = [rv + (C.REFL_R - rv) * i / 48 for i in range(49)]
    prof = [(r, n_top(r)) for r in rs]
    prof += [(C.REFL_R, C.N_LEDGE), (C.SKIRT_IN_R, C.N_LEDGE)]
    under = [r for r in reversed(rs) if r <= C.SKIRT_IN_R - 1.5]
    prof += [(r, n_top(r) - C.REFL_T) for r in under]
    refl = L.revolve("reflector_insert", prof, axis=axis, center=(C.CX, yc, C.CZ), segments=160)
    if C.REFL_PERF:
        for k in range(C.REFL_PERF_N):
            a = 2 * math.pi * k / C.REFL_PERF_N
            p = Vector((C.CX + C.REFL_PERF_R * math.cos(a), yc - side * n_top(C.REFL_PERF_R), C.CZ + C.REFL_PERF_R * math.sin(a)))
            L.cut(refl, L.add_cyl("perf", p, C.REFL_PERF_D / 2, 8.0, axis="Y", verts=16))
    return refl


if __name__ == "__main__":
    L.std_main(lambda: make(+1), PRINT_ROT, NOTES)
