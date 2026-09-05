#!/usr/bin/env -S blender --background --python
"""
build_pod_cup.py -- vp0.2 pod cup: the visible Ø122.1 disk, printed face-down.

Flat outer face (cosmetic grooves) + 20.5 mm skirt with a ledge for the glued
reflector insert. Inside: 3 M3 through-holes for the hub bracket, four fan
standoffs (25 mm fan), intake vent slots on the skirt, DC-jack + USB holes.
Outside: five standard port sockets on the rim (45/90/135/240/300 deg).

Print: outer face DOWN (on the bed). No supports (socket roofs bridge 10 mm).
Qty: 2 (identical L/R).
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
    "print outer face down; no supports; 3 walls, 20% gyroid",
    f"ports: {C.POD_PORT_ANGLES} deg (0=forward, 90=up); socket {C.PORT_SQ + C.PORT_CLEAR:.1f} sq x {C.PORT_DEPTH} deep, M3 cross-bolt {C.PORT_XBOLT_DEPTH} mm in",
    "hardware: 3x M3x8 (from inside, into hub bracket nuts); 4x M2x6 fan screws; reflector epoxied into the ledge",
]


def pod_axis_pt(side, n):
    """Point on the pod axis at local axial coordinate n (0 = cup outer face, + toward head)."""
    return Vector((C.CX, side * (C.CUP_FACE_Y - n), C.CZ))


def make(side: int = +1):
    axis = "-Y" if side > 0 else "Y"
    yc = side * C.CUP_FACE_Y
    gi, go = C.CAP_RING_GROOVE
    gd = C.CAP_GROOVE_D
    prof = [(0.0, 0.0), (gi, 0.0), (gi, gd), (go, gd), (go, 0.0), (C.DISH_R, 0.0), (C.DISH_R, C.N_SKIRT_TOP),
            (C.SKIRT_IN_R + C.LEDGE_STEP, C.N_SKIRT_TOP), (C.SKIRT_IN_R + C.LEDGE_STEP, C.N_LEDGE),
            (C.SKIRT_IN_R, C.N_LEDGE), (C.SKIRT_IN_R, C.N_FLOOR_IN), (0.0, C.N_FLOOR_IN)]
    cup = L.revolve("pod_cup", prof, axis=axis, center=(C.CX, yc, C.CZ), segments=160)

    # --- unions: port bosses, fan standoffs
    frames = {ang: L.pod_port_frame(ang, side) for ang in C.POD_PORT_ANGLES}
    for ang, M in frames.items():
        L.union(cup, L.port_boss(f"boss{int(ang)}", M))
    fa = math.radians(C.FAN_CENTER_ANGLE)
    d = Vector((math.cos(fa), 0.0, math.sin(fa)))
    t = Vector((-math.sin(fa), 0.0, math.cos(fa)))
    fc = pod_axis_pt(side, C.N_FLOOR_IN) + d * C.FAN_CENTER_R
    pegs = []
    for sd in (-1, 1):
        for st in (-1, 1):
            pc = fc + d * (sd * C.FAN_PITCH / 2) + t * (st * C.FAN_PITCH / 2) - Vector((0, side * C.FAN_STANDOFF_H / 2, 0))
            pegs.append(pc)
            L.union(cup, L.add_cyl("peg", pc, C.FAN_STANDOFF_D / 2, C.FAN_STANDOFF_H + 0.4, axis="Y", verts=24))

    # --- cuts
    for ang, M in frames.items():
        L.cut(cup, *L.port_cutters(M, tag=str(int(ang))))
    for pc in pegs:
        L.cut(cup, L.add_cyl("peghole", pc - Vector((0, side * 0.5, 0)), C.M2_TAP_DIA / 2, 4.0, axis="Y", verts=16))
    for ang in C.HUB_BOLT_ANGLES:
        a = math.radians(ang)
        p = Vector((C.CX + C.HUB_BOLT_R * math.cos(a), yc - side * C.CUP_FLOOR_T / 2, C.CZ + C.HUB_BOLT_R * math.sin(a)))
        L.cut(cup, L.add_cyl("hubbolt", p, C.M3_CLEAR_DIA / 2, C.CUP_FLOOR_T + 2, axis="Y", verts=24))
    # vent slots through the skirt
    n_mid = (C.N_FLOOR_IN + C.N_LEDGE) / 2
    for k in range(C.VENT_SLOTS):
        ang = C.VENT_ANGLE_0 + (C.VENT_ANGLE_1 - C.VENT_ANGLE_0) * (k + 0.5) / C.VENT_SLOTS
        a = math.radians(ang)
        dv = Vector((math.cos(a), 0.0, math.sin(a)))
        M = L.frame(pod_axis_pt(side, n_mid) + dv * (C.DISH_R - C.SKIRT_WALL / 2), dv, (0.0, side, 0.0))
        L.cut(cup, L.add_box_local("vent", M, (0, 0, 0), (C.VENT_SLOT_L, C.VENT_SLOT_W, C.SKIRT_WALL + 2)))
    # DC jack (180 deg) and USB-C slot (195 deg) through the skirt
    for ang, shape in ((C.JACK_ANGLE, "jack"), (C.USB_ANGLE, "usb")):
        a = math.radians(ang)
        dv = Vector((math.cos(a), 0.0, math.sin(a)))
        M = L.frame(pod_axis_pt(side, n_mid) + dv * (C.DISH_R - C.SKIRT_WALL / 2), dv, (0.0, side, 0.0))
        if shape == "jack":
            L.cut(cup, L.add_cyl_local("jack", M, (0, 0, 0), C.NAPE_JACK_DIA / 2, C.SKIRT_WALL + 2, axis="Z", verts=32))
        else:
            L.cut(cup, L.add_box_local("usb", M, (0, 0, 0), (3.6, 9.2, C.SKIRT_WALL + 2)))
    # cosmetic radial grooves on the outer face
    for ang in C.CAP_GROOVE_ANGLES:
        a = math.radians(ang)
        dv = Vector((math.cos(a), 0.0, math.sin(a)))
        rm = (C.CAP_GROOVE_R0 + C.CAP_GROOVE_R1) / 2
        M = L.frame(Vector((C.CX, yc, C.CZ)) + dv * rm, dv, (0.0, side, 0.0))
        L.cut(cup, L.add_box_local("groove", M, (0, 0, 0), (2 * C.CAP_GROOVE_D, C.CAP_GROOVE_W, C.CAP_GROOVE_R1 - C.CAP_GROOVE_R0)))
    return cup


if __name__ == "__main__":
    L.std_main(lambda: make(+1), PRINT_ROT, NOTES)
