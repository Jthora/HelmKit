#!/usr/bin/env -S blender --background --python
"""
build_rear_band_half.py -- vp0.3 rear band half: socket block at the pod, rack at the nape.

36 x 5 ribbon in a plane tilted 26 deg, starting from a full-height socket
block that a 28 mm coupler joins to the pod's rear port, hugging the occiput
to a 66 mm rack strip for the nape ratchet. Filleted before the rack goes on.
Print: top edge down (rack teeth up). Qty: 2 (same STL; right = rotated 180 deg
about the outward normal at the nape).
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
D = Vector(C.REAR_D)
PRINT_ROT = L.rot_dir_to(W, (0.0, 0.0, -1.0))
NOTES = ["print with the planar top edge on the bed (rack teeth up); no supports",
         f"socket block takes a {C.COUPLER_REAR_LEN} mm coupler into the pod rear port; lock screw M3 from the outboard face"]
BACK = Vector((C.REAR_BACK_X, 0.0, C.REAR_BACK_Z))
N_OUT = Vector((-math.cos(math.radians(C.REAR_TILT)), 0.0, -math.sin(math.radians(C.REAR_TILT))))
POD_C = Vector((C.CX, C.POD_PORT_Y, C.CZ))


def z_of(x):
    return C.REAR_MOUTH[2] + (x - C.REAR_MOUTH[0]) * math.tan(math.radians(C.REAR_TILT))


def block_mouth_frame():
    mouth = POD_C + D * (C.DISH_R + C.REAR_BLOCK_GAP)
    return L.frame(mouth, -D, (0.0, 1.0, 0.0))


def make():
    r_start = C.DISH_R + C.REAR_BLOCK_GAP + C.PORT_BLOCK_LEN - 1.0
    start = POD_C + D * r_start
    wps = [(start.x, start.y)] + list(C.REAR_WAYPOINTS[1:]) + [(C.REAR_BACK_X, 50.0)]
    samp = L.catmull_rom(wps, samples_per_seg=12)
    pts = [Vector((x, y, z_of(x))) for (x, y) in samp]
    half = C.REAR_H / 2
    band = L.ribbon("rear_band_half", pts, W, [(half, half, C.REAR_T / 2, C.REAR_T / 2)] * len(pts), chamfer=1.0)
    # socket block at the pod end
    bc = POD_C + D * (C.DISH_R + C.REAR_BLOCK_GAP + C.PORT_BLOCK_LEN / 2)
    Mb = L.frame(bc, D, (0.0, 1.0, 0.0))
    L.union(band, L.add_box_local("block", Mb, (0.0, 0.0, 0.0), (C.PORT_BLOCK, C.REAR_H, C.PORT_BLOCK_LEN)))
    Mm = block_mouth_frame()
    L.cut(band, L.port_socket_cut(Mm, tag="rb"))
    L.cut(band, *L.port_screw_cutters(Mm, -1.0, C.PORT_BLOCK / 2 + 1.0, tag="rb"))
    L.fillet(band, width=0.8)   # block edges; the ribbon is chamfered by construction
    # rack strip
    Mr = L.frame((C.REAR_BACK_X, 50.0, z_of(C.REAR_BACK_X)), N_OUT, (0.0, -1.0, 0.0))
    body_h = half - C.RACK_PITCH_W
    poly = L.rack_poly(C.RACK_LEN + 2.0, C.GEAR_MODULE, C.GEAR_PA, body_h)
    poly = [(u - 2.0, C.RACK_PITCH_W - v) for (u, v) in poly]
    L.union(band, L.extrude_polygon("rack", poly, C.REAR_T - 0.1, Mr, z0=-(C.REAR_T - 0.1) / 2))
    return band


def right_half_matrix() -> Matrix:
    return Matrix.Translation(BACK) @ Matrix.Rotation(math.pi, 4, N_OUT) @ Matrix.Translation(-BACK)


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
