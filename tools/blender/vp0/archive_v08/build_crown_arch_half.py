#!/usr/bin/env -S blender --background --python
"""
build_crown_arch_half.py -- vp0.8 crown arch half: tongue into the nexus, rope spine.

20 x 7 ribbon (chamfered section) from a 4 x 20 tongue in the nexus flange's
top flat port (M3 cross-bolt), straight up 20 mm,
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
         f"spine groove {C.SPINE_GROOVE[0]} x {C.SPINE_GROOVE[1]} on the head-side face: lay epoxy-soaked rope, press flush",
         f"foot: 4 x 20 tongue into the nexus top slot, M3 cross-bolt at z {C.CROWN_CROSS_Z:.0f}"]


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
    poly = L.ridge_plate_poly(-C.CROWN_OVERLAP + 1.0, -1.0, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 0.5, C.CROWN_SERR_PITCH / 4)
    L.union(arch, L.extrude_polygon("ridges", poly, C.CROWN_T - 2.2, Mr))
    L.cut(arch, L.add_box("slot", (C.CX + C.CROWN_BAR_W / 2, -C.CROWN_OVERLAP / 2, C.CROWN_APEX_Z), (C.CROWN_BAR_W + 4, C.CROWN_SLOT_L, C.CROWN_SLOT_W)))
    # foot: 4 x 20 tongue into the nexus flange's top slot, M3 cross-bolt
    tt, tw, tl = C.NEXUS_TONGUE
    r0, r1 = C.CROWN_TONGUE_R
    tongue = L.add_box("tongue", (C.CX, C.CROWN_LEG_Y, (C.CZ + r0 + 0.5 + C.CROWN_LEG_Z0 + 0.5) / 2), (tw, tt, C.CROWN_LEG_Z0 + 0.5 - (C.CZ + r0 + 0.5)))
    L.fillet(tongue, width=0.8)
    L.union(arch, tongue)
    L.cut(arch, L.add_cyl("cross", (C.CX, C.CROWN_LEG_Y, C.CROWN_CROSS_Z), C.M3_CLEAR_DIA / 2, C.CROWN_T + 4.0, axis="Y", verts=24))
    gw, gd = C.SPINE_GROOVE
    gi = [i for i, p in enumerate(pts) if 16.0 < p.y < C.CROWN_LEG_Y - 6.0]
    gpts = [pts[i] for i in gi]
    gext = [(gw / 2, gw / 2, -(C.CROWN_T / 2 - gd), C.CROWN_T / 2 + 1.0)] * len(gpts)
    L.cut(arch, L.ribbon("spine", gpts, Vector((1.0, 0.0, 0.0)), gext))
    return arch


def right_half_matrix() -> Matrix:
    return Matrix.Translation((C.CX, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-C.CX, 0, 0))


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
