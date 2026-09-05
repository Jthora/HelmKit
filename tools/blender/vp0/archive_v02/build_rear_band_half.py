#!/usr/bin/env -S blender --background --python
"""
build_rear_band_half.py -- vp0.2 rear band half with integral rack.

36 x 5 ribbon in a plane tilted 26 deg (leans back to follow the occiput)
from the serrated hub ring around the back of the head, ending in a 70 mm
straight rack strip (module 1.25) that runs through the nape ratchet.

Print: top edge DOWN (rack teeth point up). No supports.
Qty: 2 (same STL; the right half is the left rotated 180 deg about the
outward normal at the nape).
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

W = Vector(C.REAR_W)
PRINT_ROT = L.rot_dir_to(W, (0.0, 0.0, -1.0))
NOTES = ["print with the (planar) top edge on the bed so the rack teeth point up; no supports",
         f"tilt {C.REAR_TILT:.1f} deg; rack {C.RACK_LEN} mm, module {C.GEAR_MODULE}"]

BACK = Vector((C.REAR_BACK_X, 0.0, C.REAR_BACK_Z))
N_OUT = Vector((-math.cos(math.radians(C.REAR_TILT)), 0.0, -math.sin(math.radians(C.REAR_TILT))))


def z_of(x):
    return C.CZ - (C.CX - x) * math.tan(math.radians(C.REAR_TILT))


def make():
    wps = list(C.REAR_WAYPOINTS) + [(C.REAR_BACK_X, 50.0)]
    samp = L.catmull_rom(wps, samples_per_seg=12)
    pts = [Vector((x, y, z_of(x))) for (x, y) in samp]
    half = C.REAR_H / 2
    ext = [(half, half, C.REAR_T / 2, C.REAR_T / 2)] * len(pts)
    band = L.ribbon("rear_band_half", pts, W, ext)
    # rack strip: local u along -Y from y=50, v along W, w outward
    Mr = L.frame((C.REAR_BACK_X, 50.0, z_of(C.REAR_BACK_X)), N_OUT, (0.0, -1.0, 0.0))
    body_h = half - C.RACK_PITCH_W
    poly = L.rack_poly(C.RACK_LEN + 2.0, C.GEAR_MODULE, C.GEAR_PA, body_h)
    poly = [(u - 2.0, C.RACK_PITCH_W - v) for (u, v) in poly]
    L.union(band, L.extrude_polygon("rack", poly, C.REAR_T - 0.1, Mr, z0=-(C.REAR_T - 0.1) / 2))   # 0.05 inset: no coplanar faces
    L.union(band, L.ring_paddle("ring", (C.CX, C.REAR_RING_Y, C.CZ), C.REAR_RING_R, side=+1))
    L.pivot_bore(band, (C.CX, C.REAR_RING_Y, C.CZ))
    L.serrate(band, (C.CX, C.REAR_RING_Y, C.CZ), side=+1, serr_in=True, serr_out=True)
    return band


def right_half_matrix() -> Matrix:
    return Matrix.Translation(BACK) @ Matrix.Rotation(math.pi, 4, N_OUT) @ Matrix.Translation(-BACK)


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
