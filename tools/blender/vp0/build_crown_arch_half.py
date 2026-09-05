#!/usr/bin/env -S blender --background --python
"""
build_crown_arch_half.py -- vp0.3 crown arch half: foot sits on the pod rim.

30 x 5 ribbon from a 30 x 16 x 15 foot (concave seat on the Ø122 rim, socket
underneath for a coupler into the pod's top port) over the crown to a 15 mm
overlap bar with transverse ridges and a 26 mm slot (apex clamp). Filleted.
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
NOTES = ["print lying flat, ridged bar face up; brim; no supports",
         f"foot socket: coupler {C.COUPLER_CROWN_LEN} mm into the pod top port; lock screw M3 from the +Y face"]


def centreline():
    a, z0, zA, n = C.POD_TOP_PORT_Y, C.CROWN_LEG_Z0, C.CROWN_APEX_Z, C.CROWN_SUPER_N
    pts = []
    for i in range(121):
        t = (math.pi / 2) * i / 120
        pts.append(Vector((C.CX, a * math.cos(t) ** (2 / n), z0 + (zA - z0) * math.sin(t) ** (2 / n))))
    for i in range(1, 21):
        pts.append(Vector((C.CX, -C.CROWN_OVERLAP * i / 20, zA)))
    return pts


def foot_mouth_frame():
    return L.frame((C.CX, C.POD_TOP_PORT_Y, C.CZ + C.DISH_R), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0))


def make():
    pts = centreline()
    ext = []
    for p in pts:
        f = min(1.0, max(0.0, (p.y - 2.0) / 10.0))
        ext.append((C.CROWN_W / 2, C.CROWN_W / 2 * f, C.CROWN_T / 2, C.CROWN_T / 2))
    arch = L.ribbon("crown_arch_half", pts, Vector((1.0, 0.0, 0.0)), ext)
    fx, fy, fz = C.CROWN_FOOT
    L.union(arch, L.add_box("foot", (C.CX, C.POD_TOP_PORT_Y, C.CROWN_LEG_Z0 - fz / 2 + 0.5), (fx, fy, fz + 1.0)))
    # concave seat on the rim
    L.cut(arch, L.add_cyl("seat", (C.CX, C.POD_TOP_PORT_Y, C.CZ), C.DISH_R, fy + 4.0, axis="Y", verts=160))
    Mf = foot_mouth_frame()
    L.cut(arch, L.port_socket_cut(Mf, tag="foot"))
    L.cut(arch, *L.port_screw_cutters(Mf, -1.0, fy / 2 + 1.0, tag="foot"))
    L.cut(arch, L.add_box("slot", (C.CX + C.CROWN_BAR_W / 2, -C.CROWN_OVERLAP / 2, C.CROWN_APEX_Z), (C.CROWN_BAR_W + 4, C.CROWN_SLOT_L, C.CROWN_SLOT_W)))
    L.fillet(arch)
    Mr = L.frame((C.CX, 0.0, C.CROWN_APEX_Z - C.CROWN_T / 2 + 0.1), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
    poly = L.ridge_plate_poly(-C.CROWN_OVERLAP + 1.0, -1.0, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 0.5, C.CROWN_SERR_PITCH / 4)
    L.union(arch, L.extrude_polygon("ridges", poly, C.CROWN_T - 0.2, Mr))
    return arch


def right_half_matrix() -> Matrix:
    return Matrix.Translation((C.CX, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-C.CX, 0, 0))


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
