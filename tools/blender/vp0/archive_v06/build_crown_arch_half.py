#!/usr/bin/env -S blender --background --python
"""
build_crown_arch_half.py -- vp0.6 crown arch half: hinged tongue foot, rope spine.

30 x 6 ribbon (chamfered section): a straight 25 mm tongue (M3 hole, serrated
outer face) that sits between the ears of the hinge plug in the pod's top
port, then a superellipse over the crown to the 15 mm overlap bar (ridges +
slot for the apex clamp). Loosen the two hinge bolts and the arch folds down
beside the pods. A 3.9 x 2.8 groove on the head-side face takes a rope soaked
in epoxy.
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
         f"foot: tongue between the hinge plug's ears, {C.HINGE_BOLT} at z {C.CROWN_HINGE_Z:.1f}; serrations face outboard"]


def centreline():
    a, z0, zb, zA, n = C.POD_TOP_PORT_Y, C.CROWN_LEG_Z0, C.CROWN_BEND_Z, C.CROWN_APEX_Z, C.CROWN_SUPER_N
    pts = [Vector((C.CX, a, z0 + (zb - z0) * i / 12)) for i in range(12)]
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
    gw, gd = C.SPINE_GROOVE
    gi = [i for i, p in enumerate(pts) if 16.0 < p.y < C.POD_TOP_PORT_Y - 10.0]
    gpts = [pts[i] for i in gi]
    gext = [(gw / 2, gw / 2, -(C.CROWN_T / 2 - gd), C.CROWN_T / 2 + 1.0)] * len(gpts)
    L.cut(arch, L.ribbon("spine", gpts, Vector((1.0, 0.0, 0.0)), gext))
    # ridges on the bar's mating face, then the slot through both
    Mr = L.frame((C.CX, 0.0, C.CROWN_APEX_Z - C.CROWN_T / 2 + 1.1), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
    poly = L.ridge_plate_poly(-C.CROWN_OVERLAP + 1.0, -1.0, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 0.5, C.CROWN_SERR_PITCH / 4)
    L.union(arch, L.extrude_polygon("ridges", poly, C.CROWN_T - 2.2, Mr))
    L.cut(arch, L.add_box("slot", (C.CX + C.CROWN_BAR_W / 2, -C.CROWN_OVERLAP / 2, C.CROWN_APEX_Z), (C.CROWN_BAR_W + 4, C.CROWN_SLOT_L, C.CROWN_SLOT_W)))
    # hinge: bolt hole along Y through the tongue, serrations on the outboard face
    hp = (C.CX, C.POD_TOP_PORT_Y, C.CROWN_HINGE_Z)
    L.cut(arch, L.add_cyl("bolt", hp, C.M3_CLEAR_DIA / 2, C.CROWN_T + 4.0, axis="Y", verts=24))
    sr = C.HINGE_SERR
    L.union(arch, L.serration_solid("serr", (C.CX, C.POD_TOP_PORT_Y + C.CROWN_T / 2, C.CROWN_HINGE_Z), (0.0, 1.0, 0.0),
                                    r_in=sr["r_in"], r_out=sr["r_out"], teeth=sr["teeth"], height=sr["height"], phase_deg=sr["phase_tongue"]))
    return arch


def right_half_matrix() -> Matrix:
    return Matrix.Translation((C.CX, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-C.CX, 0, 0))


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
