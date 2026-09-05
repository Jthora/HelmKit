#!/usr/bin/env -S blender --background --python
"""
build_brow_arm.py -- vp0.2 brow arm: hub ring to panel tab (left; --mirror for right).

25 x 5 strut in a plane tilted BROW_TILT deg (rises from the hub toward the
panel, parallel to the panel's normal), serrated Ø24.6 ring at the hub, tab
lying on the panel's front face with two M3 bolts.

Print: on its planar bottom edge (tilted plane on the bed). No supports.
Qty: 1 L + 1 R.
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

EX, EZ = Vector(C.BROW_EX), Vector(C.BROW_EZ)
ORG = Vector(C.BROW_ORIGIN)
HUB = Vector((C.CX, 0.0, C.CZ))
PRINT_ROT = L.rot_dir_to(EZ, (0.0, 0.0, 1.0))
NOTES = ["print on the flat (tilted-plane) bottom edge; no supports", "--mirror for the right arm"]


def z_of(x):
    """Centreline height: the line through the hub with direction BROW_EX."""
    return C.CZ + (x - C.CX) * math.tan(math.radians(C.BROW_TILT))


def tab_x():
    """World x of the tab centreline (BROW_ARM_T/2 outside the panel's outer face), at the centreline height."""
    t = (ORG - HUB).dot(EX) + C.BROW_T + C.BROW_ARM_T / 2
    return (HUB + EX * t).x


def make(side: int = +1):
    y = side * C.BROW_RING_Y
    xt = tab_x()
    y0, y1 = C.BROW_TAB_Y
    wps = [(C.CX, y), (52.0, side * 128.0), (92.0, side * 112.0), (112.0, side * 94.0), (xt, side * y1), (xt, side * y0)]
    samp = L.catmull_rom(wps, samples_per_seg=12)
    pts = [Vector((x, yy, z_of(x))) for (x, yy) in samp]
    half = C.BROW_ARM_H / 2
    arm = L.ribbon("brow_arm", pts, EZ, [(half, half, C.BROW_ARM_T / 2, C.BROW_ARM_T / 2)] * len(pts))
    L.union(arm, L.ring_paddle("ring", (C.CX, y, C.CZ), C.BROW_RING_R, side=side))
    L.pivot_bore(arm, (C.CX, y, C.CZ))
    MP = L.frame(C.BROW_ORIGIN, C.BROW_EZ, C.BROW_EX)
    for by, bz in C.BROW_ARM_BOLTS:
        L.cut(arm, L.add_cyl_local("tabbolt", MP, (C.BROW_T + C.BROW_ARM_T / 2, side * by, bz), C.M3_CLEAR_DIA / 2, C.BROW_ARM_T + 4, axis="X"))
    L.serrate(arm, (C.CX, y, C.CZ), side=side, serr_in=True, serr_out=True)
    return arm


if __name__ == "__main__":
    L.std_main(lambda: make(+1), PRINT_ROT, NOTES, mirror_ok=True)
