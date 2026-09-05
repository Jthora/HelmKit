#!/usr/bin/env -S blender --background --python
"""
build_rear_band.py -- vp0 rear band: folding occipital band with nape hook.

25 x 6 mm ribbon from hub to hub around the back of the head. Constant
top edge (z=+12.5); the bottom edge drops to z=-35 at the back centre so
the band hooks under the inion (anti-lift retention). Ø25 rings on the
pivot axis, serrated both faces.

Print: INVERTED (top edge on the bed). No supports.
Qty: 1.

Run:
    blender --background --python tools/blender/vp0/build_rear_band.py -- \\
        --out 3D-Models/HelmKit/_generated/vp0/rear_band.stl
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
from mathutils import Vector  # type: ignore

PRINT_ROT = L.ROT_FLIP
NOTES = [
    "print inverted (flat top edge on the bed); no supports",
    f"nape hook bottom edge z {C.REAR_DIP_Z}; back-centre clearance to phantom ~{C.REAR_CLEAR} mm (foam pad)",
]


def waypoints():
    left = list(C.REAR_WAYPOINTS)
    right = [(x, -y, zb) for (x, y, zb) in reversed(left[:-1])]
    return left + right


def make():
    wps = waypoints()
    samp = L.catmull_rom(wps, samples_per_seg=14)
    pts = [Vector((x, y, 0.0)) for (x, y, zb) in samp]
    ext = [(C.REAR_TOP_Z, -zb, C.REAR_T / 2, C.REAR_T / 2) for (x, y, zb) in samp]
    band = L.ribbon("rear_band", pts, Vector((0.0, 0.0, 1.0)), ext)
    for side in (+1, -1):
        L.union(band, L.ring_paddle("rear_ring", side * C.REAR_RING_Y, C.REAR_RING_R, side=side))
        L.pivot_bore(band, side * C.REAR_RING_Y)
    for side in (+1, -1):   # serrations last (see vp0lib.serrate)
        L.serrate(band, side * C.REAR_RING_Y, side=side, serr_in=True, serr_out=True)
    return band


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    L.finalize_and_export(make(), args.out, PRINT_ROT, NOTES)


if __name__ == "__main__":
    main()
