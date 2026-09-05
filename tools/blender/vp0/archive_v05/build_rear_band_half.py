#!/usr/bin/env -S blender --background --python
"""
build_rear_band_half.py -- vp0.5 rear band half: pinned socket block, rope spine, rack.

36 x 6 chamfered ribbon in a plane tilted 26 deg from a full-height socket
block at the pod (coupler + nail pin + collar) around the occiput to a 66 mm
rack strip (module 1.25) for the enclosed nape dial. Spine groove on the
head-side face for epoxy-soaked rope.
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
         f"socket block: {C.COUPLER_REAR_LEN} mm coupler into the pod rear port, nail pin, thread-wrap collar",
         f"spine groove {C.SPINE_GROOVE[0]} x {C.SPINE_GROOVE[1]} on the head-side face; rack {C.RACK_LEN} mm module {C.GEAR_MODULE}"]
BACK = Vector((C.REAR_BACK_X, 0.0, C.REAR_BACK_Z))
N_OUT = Vector((-math.cos(math.radians(C.REAR_TILT)), 0.0, -math.sin(math.radians(C.REAR_TILT))))
POD_C = Vector((C.CX, C.POD_PORT_Y, C.CZ))


def z_of(x):
    return C.REAR_MOUTH[2] + (x - C.REAR_MOUTH[0]) * math.tan(math.radians(C.REAR_TILT))


def block_mouth_frame():
    return L.frame(POD_C + D * (C.DISH_R + C.REAR_BLOCK_GAP), -D, (0.0, 1.0, 0.0))


def make():
    r_start = C.DISH_R + C.REAR_BLOCK_GAP + C.PORT_BLOCK_LEN - 1.0
    start = POD_C + D * r_start
    wps = [(start.x, start.y)] + list(C.REAR_WAYPOINTS[1:]) + [(C.REAR_BACK_X, 50.0)]
    samp = L.catmull_rom(wps, samples_per_seg=16)
    pts = L.resample_polyline([Vector((x, y, z_of(x))) for (x, y) in samp], 2.0)   # uniform 2 mm stations: no sliver quads
    half = C.REAR_H / 2
    band = L.ribbon("rear_band_half", pts, W, [(half, half, C.REAR_T / 2, C.REAR_T / 2)] * len(pts), chamfer=1.0)
    bc = POD_C + D * (C.DISH_R + C.REAR_BLOCK_GAP + C.PORT_BLOCK_LEN / 2)
    Mb = L.frame(bc, D, (0.0, 1.0, 0.0))
    L.union(band, L.add_box_local("block", Mb, (0.0, 0.0, 0.0), (C.PORT_BLOCK, C.REAR_H + 0.2, C.PORT_BLOCK_LEN)))
    gw, gd = C.SPINE_GROOVE
    gi = L.arc_index_range(pts, 16.0, 6.0)          # clear of the block and of the band's end
    gpts = [pts[i] for i in gi]
    L.cut(band, L.ribbon("spine", gpts, W, [(gw / 2, gw / 2, -(C.REAR_T / 2 - gd), C.REAR_T / 2 + 1.0)] * len(gpts)))
    Mm = block_mouth_frame()
    L.cut(band, L.port_socket_cut(Mm, tag="rb"))
    L.cut(band, *L.port_pin_cutters(Mm, -(C.PORT_BLOCK / 2 + 1.0), C.PORT_BLOCK / 2 + 1.0, tag="rb"))
    L.cut(band, L.collar_cutter(Mm, -C.PORT_BLOCK_LEN / 2.0, C.PORT_BLOCK, tag="rb"))
    # rack strip: u along -Y from y = 50, v along W, w outward
    Mr = L.frame((C.REAR_BACK_X, 50.0, z_of(C.REAR_BACK_X)), N_OUT, (0.0, -1.0, 0.0))
    body_h = half - C.RACK_PITCH_W - 0.2      # rack top 0.2 below the band's chamfered top edge (no coplanar faces)
    poly = L.rack_poly(C.RACK_LEN + 2.0, C.GEAR_MODULE, C.GEAR_PA, body_h)
    poly = [(u - 2.0, C.RACK_PITCH_W - v) for (u, v) in poly]
    L.union(band, L.extrude_polygon("rack", poly, C.REAR_T - 0.1, Mr, z0=-(C.REAR_T - 0.1) / 2))
    return band


def right_half_matrix() -> Matrix:
    return Matrix.Translation(BACK) @ Matrix.Rotation(math.pi, 4, N_OUT) @ Matrix.Translation(-BACK)


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
