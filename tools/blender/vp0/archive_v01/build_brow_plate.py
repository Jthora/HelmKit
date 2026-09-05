#!/usr/bin/env -S blender --background --python
"""
build_brow_plate.py -- vp0 brow plate: folding forehead plate + projector bay.

One continuous ribbon: 6 mm arms from each hub ring, thickening to a
14 mm x 50 mm plate across the brow (inner face 10 mm off the phantom
at z=65). Constant top edge z=90. A 70 x 30 mm bay is cut into the
plate from the head side (2.5 mm front wall) as the projector
placeholder, with a 40 x 10 window through the front wall. Vertical
stems drop from the arms to Ø25 rings on the pivot axis.

Print: INVERTED (top edge on the bed). No supports.
Qty: 1.

Run:
    blender --background --python tools/blender/vp0/build_brow_plate.py -- \\
        --out 3D-Models/HelmKit/_generated/vp0/brow_plate.stl
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

PRINT_ROT = L.ROT_FLIP
NOTES = [
    "print inverted (flat top edge z=90 on the bed); no supports; bay roof bridges 12 mm",
    f"plate inner face ellipse a={C.BROW_ELL_A:.1f} b={C.BROW_ELL_B:.1f} at z={C.BROW_MID_Z:.0f}; bay {2*C.BROW_BAY_HALF_Y:.0f} x {C.BROW_BAY_Z[1]-C.BROW_BAY_Z[0]:.0f} x ~{C.BROW_PLATE_T - C.BROW_BAY_FRONT_WALL:.1f} mm open to the head side",
]


def plate_centreline(half_y: float, thick: float, n: int = 36):
    """(x, y, t, z_bot) samples along the plate from +y to -y, centreline = inner face + t/2 along the outward normal."""
    a, b = C.BROW_ELL_A, C.BROW_ELL_B
    t_end = math.asin(min(1.0, half_y / b))
    out = []
    for i in range(n + 1):
        t = t_end - 2 * t_end * i / n
        xi, yi = a * math.cos(t), b * math.sin(t)
        nx, ny = math.cos(t) / a, math.sin(t) / b
        nn = math.hypot(nx, ny)
        nx, ny = nx / nn, ny / nn
        out.append((xi + nx * thick / 2, yi + ny * thick / 2, thick, C.BROW_PLATE_Z0))
    return out


def waypoints():
    left = [(x, y, t, C.BROW_ARM_Z0) for (x, y, t) in C.BROW_ARM_WAYPOINTS]
    plate = plate_centreline(C.BROW_PLATE_HALF_Y, C.BROW_PLATE_T)
    right = [(x, -y, t, zb) for (x, y, t, zb) in reversed(left)]
    return left + plate + right


def make():
    wps = waypoints()
    samp = L.catmull_rom(wps, samples_per_seg=6)
    pts = [Vector((x, y, 0.0)) for (x, y, t, zb) in samp]
    ext = [(C.BROW_PLATE_Z1, -zb, t / 2, t / 2) for (x, y, t, zb) in samp]
    plate = L.ribbon("brow_plate", pts, Vector((0.0, 0.0, 1.0)), ext)

    # projector bay: same centreline, open toward the head (N = inward for this traversal)
    bay_wps = plate_centreline(C.BROW_BAY_HALF_Y, C.BROW_PLATE_T, n=24)
    bay_pts = [Vector((x, y, 0.0)) for (x, y, t, zb) in bay_wps]
    z0, z1 = C.BROW_BAY_Z
    bay_ext = [(z1, -z0, 30.0, C.BROW_PLATE_T / 2 - C.BROW_BAY_FRONT_WALL)] * len(bay_pts)
    L.cut(plate, L.ribbon("bay", bay_pts, Vector((0.0, 0.0, 1.0)), bay_ext))
    # window through the front wall
    w0, w1 = C.BROW_WINDOW_Z
    L.cut(plate, L.add_box("window", (C.BROW_ELL_A + C.BROW_PLATE_T / 2, 0.0, (w0 + w1) / 2),
                           (40.0, 2 * C.BROW_WINDOW_HALF_Y, w1 - w0)))

    for side in (+1, -1):
        y = side * C.BROW_RING_Y
        stem = L.ribbon("stem", [Vector((0.0, y, 0.0)), Vector((0.0, y, C.BROW_ARM_Z0 + 6.0))],
                        Vector((1.0, 0.0, 0.0)),
                        [(C.BROW_STEM_W / 2, C.BROW_STEM_W / 2, C.BROW_ARM_T / 2, C.BROW_ARM_T / 2)] * 2)
        L.union(plate, stem)
        L.union(plate, L.ring_paddle("brow_ring", y, C.BROW_RING_R, side=side))
        L.pivot_bore(plate, y)
    for side in (+1, -1):   # serrations last (see vp0lib.serrate)
        L.serrate(plate, side * C.BROW_RING_Y, side=side, serr_in=True, serr_out=True)
    return plate


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    L.finalize_and_export(make(), args.out, PRINT_ROT, NOTES)


if __name__ == "__main__":
    main()
