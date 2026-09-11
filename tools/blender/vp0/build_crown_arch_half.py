#!/usr/bin/env -S blender --background --python
"""
build_crown_arch_half.py -- vp0.9 crown arch half: socketed foot on the hub node (coupler).

20 x 7 ribbon (chamfered section) from a foot block with an 8.3 socket over the
hub node's socket (a 30 mm coupler, M3 cross-bolt each end), straight up 20 mm,
then a superellipse over the crown to the 15 mm overlap bar (ridges + slot
for the apex clamp). Two cross-bolts out and the arch lifts off for packing.
A 3.9 x 2.8 groove on the head-side face takes a rope soaked in epoxy.
Print: lying flat, ridged face up. Qty: 2 (same STL, rotated 180 deg).
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
NOTES = ["print on edge (arch plane on the bed), ridged bar face up; brim; no supports",
         f"foot: 8.3 socket; port_coupler (or 8 mm rod) joins it to the hub node, M3 cross-bolts at z {C.HUB_CROSS_Z:.0f} and {C.CROWN_CROSS_Z:.0f}"]


def centreline():
    a, z0, zb, zA, n = C.CROWN_LEG_Y, C.CROWN_LEG_Z0, C.CROWN_BEND_Z, C.CROWN_APEX_Z, C.CROWN_SUPER_N
    pts = [Vector((C.CX, a, z0 + (zb - z0) * i / 10)) for i in range(10)]
    for i in range(121):
        t = (math.pi / 2) * i / 120
        pts.append(Vector((C.CX, a * math.cos(t) ** (2 / n), zb + (zA - zb) * math.sin(t) ** (2 / n))))
    for i in range(1, 21):
        pts.append(Vector((C.CX, -C.CROWN_OVERLAP * i / 20, zA)))
    return pts


def make():
    pts = centreline()
    ext = []
    for p in pts:
        f = min(1.0, max(0.0, (p.y - 2.0) / 10.0))
        ext.append((C.CROWN_W / 2, C.CROWN_W / 2 * f, C.CROWN_T / 2, C.CROWN_T / 2))
    arch = L.ribbon("crown_arch_half", pts, Vector((1.0, 0.0, 0.0)), ext, chamfer=1.0)
    # ridges on the bar's mating face, then the slot through both (before the foot and the spine: solver order matters)
    Mr = L.frame((C.CX, 0.0, C.CROWN_APEX_Z - C.CROWN_T / 2 + 1.1), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
    # two ridge plates, one each side of the clamp slot's y-range (a plate through the slot would be cut to 0.2 mm stubs)
    ys0, ys1 = -C.CROWN_OVERLAP / 2 - C.CROWN_SLOT_L / 2 - 0.5, -C.CROWN_OVERLAP / 2 + C.CROWN_SLOT_L / 2 + 0.5
    for u0, u1 in ((-C.CROWN_OVERLAP + 1.0, ys0), (ys1, -1.0)):
        poly = L.ridge_plate_poly(u0, u1, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 0.5, C.CROWN_SERR_PITCH / 4)
        L.union(arch, L.extrude_polygon("ridges", poly, C.CROWN_T - 2.2, Mr))
    L.cut(arch, L.add_box("slot", (C.CX + C.CROWN_BAR_W / 2, -C.CROWN_OVERLAP / 2, C.CROWN_APEX_Z), (C.CROWN_BAR_W + 4, C.CROWN_SLOT_L, C.CROWN_SLOT_W)))
    # foot block (ridges first, then the foot: solver order) with an 8.3 socket over the hub node's socket; a coupler joins them
    fx, fy, fz = C.CROWN_FOOT
    foot = L.add_box("foot", (C.CX, C.HUB_SOCKET[1], C.CROWN_LEG_Z0 - fz / 2 + 0.8), (fx, fy, fz + 1.6))
    L.fillet(foot, width=1.0)
    L.union(arch, foot)
    z_mouth = C.CROWN_LEG_Z0 - fz
    L.cut(arch, L.add_cyl("socket", (C.CX, C.HUB_SOCKET[1], z_mouth + C.CYL_DEPTH / 2 - 0.5), C.CYL_SOCKET_D / 2, C.CYL_DEPTH + 1.0, axis="Z", verts=48))
    L.cut(arch, L.add_cyl("cross", (C.CX, C.HUB_SOCKET[1], C.CROWN_CROSS_Z), C.M3_CLEAR_DIA / 2, fy + 4.0, axis="Y", verts=24))
    return arch


def right_half_matrix() -> Matrix:
    return Matrix.Translation((C.CX, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-C.CX, 0, 0))


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
