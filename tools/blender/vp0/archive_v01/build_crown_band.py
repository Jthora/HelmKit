#!/usr/bin/env -S blender --background --python
"""
build_crown_band.py -- vp0 crown band: the fixed headphone-style arch.

30 x 6 mm ribbon following a superellipse (n=2.6) from hub to hub,
ending in Ø30 rings on the pivot axis. Ring inboard face serrated
(mates the brow ring), outboard face flat (thumb-nut bears on it).

Print: lying on its side (band width = print height). No supports.
Qty: 1.

Run:
    blender --background --python tools/blender/vp0/build_crown_band.py -- \\
        --out 3D-Models/HelmKit/_generated/vp0/crown_band.stl
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

PRINT_ROT = L.ROT_X_TO_Z
NOTES = [
    "print lying flat on its 6 mm edge (arch in the XY plane); brim recommended; no supports",
    f"hub-to-hub {2*C.CROWN_RING_Y:.1f} mm; centreline apex z {C.CROWN_APEX_Z:.0f}; clearance over vertex {C.CROWN_CLEAR} mm",
]


def make():
    pts = L.superellipse_yz(C.CROWN_RING_Y, C.CROWN_APEX_Z, C.CROWN_SUPER_N)
    ext = [(C.CROWN_W / 2, C.CROWN_W / 2, C.CROWN_T / 2, C.CROWN_T / 2)] * len(pts)
    band = L.ribbon("crown_band", pts, Vector((1.0, 0.0, 0.0)), ext)
    for side in (+1, -1):
        L.union(band, L.ring_paddle("crown_ring", side * C.CROWN_RING_Y, C.CROWN_RING_R, side=side))
        L.pivot_bore(band, side * C.CROWN_RING_Y)
    for side in (+1, -1):   # serrations last (see vp0lib.serrate)
        L.serrate(band, side * C.CROWN_RING_Y, side=side, serr_in=True, serr_out=False)
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
