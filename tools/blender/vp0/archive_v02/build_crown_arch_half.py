#!/usr/bin/env -S blender --background --python
"""
build_crown_arch_half.py -- vp0.2 crown arch, one of two identical halves.

30 x 5 ribbon rising from a 30 x 16 x 18 foot block (downward port socket; a
port coupler joins it to the pod's top port) over the crown, narrowing to a
15 mm overlap bar past the sagittal plane. The bar carries transverse
ridges on its mating face and a 26 mm slot: the two bars sit side by side
in the apex block, clamped by one M4 bolt, giving +/-13 mm width adjustment.

Print: lying flat, ridged face UP. No supports (foot socket roof bridges 10 mm).
Qty: 2 (same STL; the right half is the left rotated 180 deg about vertical).
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

PRINT_ROT = L.ROT_NEGX_TO_Z
NOTES = ["print lying flat with the ridged bar face up; brim; no supports",
         f"span adjust +/-{C.CROWN_SLOT_L/2:.0f} mm via the apex M4 clamp; ridge pitch {C.CROWN_SERR_PITCH} mm"]


def centreline():
    a, z0, zA, n = C.POD_TOP_PORT_Y, C.CROWN_LEG_Z0, C.CROWN_APEX_Z, C.CROWN_SUPER_N
    pts = []
    for i in range(121):
        t = (math.pi / 2) * i / 120
        pts.append(Vector((C.CX, a * math.cos(t) ** (2 / n), z0 + (zA - z0) * math.sin(t) ** (2 / n))))
    for i in range(1, 21):
        pts.append(Vector((C.CX, -C.CROWN_OVERLAP * i / 20, zA)))
    return pts


def make():
    pts = centreline()
    ext = []
    for p in pts:
        y = p.y
        f = min(1.0, max(0.0, (y - 2.0) / 10.0))      # 1 = full width, 0 = bar offset to +X
        ext.append((C.CROWN_W / 2, C.CROWN_W / 2 * f, C.CROWN_T / 2, C.CROWN_T / 2))
    arch = L.ribbon("crown_arch_half", pts, Vector((1.0, 0.0, 0.0)), ext)
    fx, fy, fz = C.CROWN_FOOT
    foot_c = Vector((C.CX, C.POD_TOP_PORT_Y, C.CROWN_LEG_Z0 - fz / 2 + 0.5))
    L.union(arch, L.add_box("foot", foot_c, (fx, fy, fz + 1.0)))
    # ridges on the bar's -X face (mating face), last union before cuts on the bar
    Mr = L.frame((C.CX, 0.0, C.CROWN_APEX_Z - C.CROWN_T / 2 + 0.1), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))   # u=Y, v=-X
    poly = L.ridge_plate_poly(-C.CROWN_OVERLAP + 1.0, -1.0, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 0.5, C.CROWN_SERR_PITCH / 4)
    L.union(arch, L.extrude_polygon("ridges", poly, C.CROWN_T - 0.2, Mr))
    # slot through the bar along X
    L.cut(arch, L.add_box("slot", (C.CX + C.CROWN_BAR_W / 2, -C.CROWN_OVERLAP / 2, C.CROWN_APEX_Z), (C.CROWN_BAR_W + 4, C.CROWN_SLOT_L, C.CROWN_SLOT_W)))
    # foot socket (opens downward)
    Mf = L.frame((C.CX, C.POD_TOP_PORT_Y, C.CROWN_LEG_Z0 - fz), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0))
    L.cut(arch, *L.port_cutters(Mf, tag="foot", header=False, xbolt_len=C.CROWN_W + 4.0))
    return arch


def right_half_matrix() -> Matrix:
    return Matrix.Translation((C.CX, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-C.CX, 0, 0))


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
