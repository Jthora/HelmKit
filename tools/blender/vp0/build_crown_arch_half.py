#!/usr/bin/env -S blender --background --python
"""
build_crown_arch_half.py -- vp0.9 crown arch half: socketed foot on the hub node (coupler).

20 x 7 ribbon (chamfered section) from a foot block with an 8.3 socket over the
hub node's socket (a 30 mm coupler, M3 cross-bolt each end), straight up 20 mm,
then a superellipse to a straight, level top (v0.18): half width wherever the other half lies beside it, ridges
and a clamp slot centred on the apex. Two cross-bolts out and the arch lifts off for packing.
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
    # v0.18 (2026-11-10): the superellipse now ENDS at y = CROWN_FLAT_Y, and the half runs straight and level at the apex height
    # from there to y = -CROWN_OVERLAP. Before, the curve ran on to y = 0, the bar began there, and the other half stayed full width
    # until 12 mm from the centre: the two halves overlapped by ~1800 mm3 as designed and could never both be fitted. The assembly's
    # collision report listed arch-against-arch as "expected" contact, which is how it went unseen until a part snapped.
    yf = C.CROWN_FLAT_Y
    for i in range(121):
        t = (math.pi / 2) * i / 120
        pts.append(Vector((C.CX, yf + (a - yf) * math.cos(t) ** (2 / n), zb + (zA - zb) * math.sin(t) ** (2 / n))))
    k = 1
    while yf - 2.0 * k > -C.CROWN_OVERLAP - 1e-6:
        pts.append(Vector((C.CX, yf - 2.0 * k, zA)))
        k += 1
    return pts


def make():
    pts = centreline()
    ext = []
    for p in pts:
        f = min(1.0, max(0.0, (p.y - (C.CROWN_OVERLAP + 1.0)) / 3.0))   # half width wherever the other half's bar lies beside it
        ext.append((C.CROWN_W / 2, C.CROWN_W / 2 * f, C.CROWN_T / 2, C.CROWN_T / 2))
    arch = L.ribbon("crown_arch_half", pts, Vector((1.0, 0.0, 0.0)), ext, chamfer=1.0)
    # ridges on the bar's mating face, then the slot through both (before the foot and the spine: solver order matters)
    Mr = L.frame((C.CX, 0.0, C.CROWN_APEX_Z - C.CROWN_T / 2 + 1.1), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
    # two ridge plates, one each side of the clamp slot's y-range (a plate through the slot would be cut to 0.2 mm stubs)
    # v0.18: the clamp slot is centred on the apex (y = 0), where the apex block's M4 is, so the bolt passes through BOTH bars'
    # slots (before, the slots sat at +/-20 and the bolt met neither); ridges either side of it, over the whole side-by-side run
    ys0, ys1 = -C.CROWN_SLOT_L / 2 - 0.5, C.CROWN_SLOT_L / 2 + 0.5
    for u0, u1 in ((-C.CROWN_OVERLAP + 1.0, ys0), (ys1, C.CROWN_OVERLAP - 1.0)):
        poly = L.ridge_plate_poly(u0, u1, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 0.5, C.CROWN_SERR_PITCH / 4)
        L.union(arch, L.extrude_polygon("ridges", poly, C.CROWN_T - 2.2, Mr))
    L.cut(arch, L.add_box("slot", (C.CX + C.CROWN_BAR_W / 2, 0.0, C.CROWN_APEX_Z), (C.CROWN_BAR_W + 4, C.CROWN_SLOT_L, C.CROWN_SLOT_W)))
    # foot block (ridges first, then the foot: solver order) with an 8.3 socket over the hub node's socket; a coupler joins them
    fx, fy, fz = C.CROWN_FOOT
    foot = L.add_box("foot", (C.CX, C.HUB_SOCKET[1], C.CROWN_LEG_Z0 - fz / 2 + 0.8), (fx, fy, fz + 1.6))
    L.fillet(foot, width=1.0)
    L.union(arch, foot)
    z_mouth = C.CROWN_LEG_Z0 - fz
    L.cut(arch, L.add_cyl("socket", (C.CX, C.HUB_SOCKET[1], z_mouth + C.CYL_DEPTH / 2 - 0.5), C.CROWN_FOOT_SOCKET_D / 2, C.CYL_DEPTH + 1.0, axis="Z", verts=48))   # prints horizontal: 0.2 more than the vertical cradle sockets
    L.cut(arch, L.add_teardrop("cross", (C.CX, C.HUB_SOCKET[1], C.CROWN_CROSS_Z), C.M3_CLEAR_DIA / 2, fy + 4.0, (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), verts=24))   # arch prints on edge: -X is up
    L.bed_plane(arch, PRINT_ROT, 0.25)   # Track P: 190 mm2 of the bed face sat 0.2 up; one bed plane
    return arch


def right_half_matrix() -> Matrix:
    return Matrix.Translation((C.CX, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-C.CX, 0, 0))


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
