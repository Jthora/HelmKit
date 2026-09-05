#!/usr/bin/env -S blender --background --python
"""
build_crown_arch_half.py -- vp0.4 crown arch half: rim-seated foot, pinned, rope spine.

30 x 6 ribbon (chamfered section) from a foot with a concave rim seat and a
pinned socket, over the crown to the 15 mm overlap bar (ridges + slot for the
apex clamp). A 3.9 x 2.8 groove on the head-side face takes a rope soaked in
epoxy: the band keeps 1 kN of tensile continuity after a crack.
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
         f"spine groove {C.SPINE_GROOVE[0]} x {C.SPINE_GROOVE[1]} on the head-side face: lay epoxy-soaked rope, press flush",
         f"foot: {C.COUPLER_CROWN_LEN} mm coupler into the pod top port, nail pin through both foot faces, thread-wrap collar"]


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
    arch = L.ribbon("crown_arch_half", pts, Vector((1.0, 0.0, 0.0)), ext, chamfer=1.0)
    fx, fy, fz = C.CROWN_FOOT
    L.union(arch, L.add_box("foot", (C.CX, C.POD_TOP_PORT_Y, C.CROWN_LEG_Z0 - fz / 2 + 0.5), (fx, fy, fz + 1.0)))
    L.cut(arch, L.add_cyl("seat", (C.CX, C.POD_TOP_PORT_Y, C.CZ), C.DISH_R, fy + 4.0, axis="Y", verts=160))
    # spine groove on the head-side face (-N) between the foot and the bar
    gw, gd = C.SPINE_GROOVE
    gi = [i for i, p in enumerate(pts) if 16.0 < p.y < C.POD_TOP_PORT_Y - 10.0]   # clear of the foot and the bar ramp
    gpts = [pts[i] for i in gi]
    gext = [(gw / 2, gw / 2, -(C.CROWN_T / 2 - gd), C.CROWN_T / 2 + 1.0)] * len(gpts)
    L.cut(arch, L.ribbon("spine", gpts, Vector((1.0, 0.0, 0.0)), gext))
    Mf = foot_mouth_frame()
    L.cut(arch, L.port_socket_cut(Mf, tag="foot"))
    L.cut(arch, *L.port_pin_cutters(Mf, -(fy / 2 + 1.0), fy / 2 + 1.0, tag="foot"))
    L.cut(arch, L.collar_cutter(Mf, -fz / 2.0, fy, tag="foot"))
    # ridges on the bar's mating face (chamfered ribbon: no bevel pass needed), then the slot through both
    Mr = L.frame((C.CX, 0.0, C.CROWN_APEX_Z - C.CROWN_T / 2 + 1.1), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))   # inside the chamfered corners
    poly = L.ridge_plate_poly(-C.CROWN_OVERLAP + 1.0, -1.0, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 0.5, C.CROWN_SERR_PITCH / 4)
    L.union(arch, L.extrude_polygon("ridges", poly, C.CROWN_T - 2.2, Mr))
    L.cut(arch, L.add_box("slot", (C.CX + C.CROWN_BAR_W / 2, -C.CROWN_OVERLAP / 2, C.CROWN_APEX_Z), (C.CROWN_BAR_W + 4, C.CROWN_SLOT_L, C.CROWN_SLOT_W)))
    return arch


def right_half_matrix() -> Matrix:
    return Matrix.Translation((C.CX, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-C.CX, 0, 0))


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
