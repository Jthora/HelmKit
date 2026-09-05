#!/usr/bin/env -S blender --background --python
"""
build_rear_band_half.py -- vp0.4 rear band half: pinned socket block, rope spine, rope eye.

30 x 6 chamfered ribbon in a plane tilted 26 deg from a full-height socket
block at the pod (coupler + nail pin + collar) around the occiput to a rope
eye block beside the nape. A 3.9 x 2.8 spine groove on the head-side face
takes epoxy-soaked rope. No rack: the nape rope and clam cleat do the tension.
Print: top edge down. Qty: 2 (same STL; right = rotated 180 deg about the
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
D = Vector(C.REAR_D)
PRINT_ROT = L.rot_dir_to(W, (0.0, 0.0, -1.0))
NOTES = ["print with the planar top edge on the bed; no supports",
         f"socket block: {C.COUPLER_REAR_LEN} mm coupler into the pod rear port, nail pin, thread-wrap collar",
         f"spine groove {C.SPINE_GROOVE[0]} x {C.SPINE_GROOVE[1]} on the head-side face; rope eye Ø{C.LOOP_HOLE_DIA} at the nape end"]
BACK = Vector((C.REAR_BACK_X, 0.0, C.REAR_BACK_Z))
N_OUT = Vector((-math.cos(math.radians(C.REAR_TILT)), 0.0, -math.sin(math.radians(C.REAR_TILT))))
POD_C = Vector((C.CX, C.POD_PORT_Y, C.CZ))


def z_of(x):
    return C.REAR_MOUTH[2] + (x - C.REAR_MOUTH[0]) * math.tan(math.radians(C.REAR_TILT))


def block_mouth_frame():
    return L.frame(POD_C + D * (C.DISH_R + C.REAR_BLOCK_GAP), -D, (0.0, 1.0, 0.0))


def eye_centre():
    ex, ey, eb = C.EYE_BLOCK
    return Vector((C.REAR_BACK_X, C.REAR_EYE_Y, z_of(C.REAR_BACK_X)))


def make():
    r_start = C.DISH_R + C.REAR_BLOCK_GAP + C.PORT_BLOCK_LEN - 1.0
    start = POD_C + D * r_start
    ex, ey, eb = C.EYE_BLOCK
    y_end = C.REAR_EYE_Y + eb / 2 - 1.0     # ribbon penetrates the eye block by 1 mm
    wps = [(start.x, start.y)] + list(C.REAR_WAYPOINTS[1:]) + [(C.REAR_BACK_X, y_end)]
    samp = L.catmull_rom(wps, samples_per_seg=12)
    pts = [Vector((x, y, z_of(x))) for (x, y) in samp]
    half = C.REAR_H / 2
    band = L.ribbon("rear_band_half", pts, W, [(half, half, C.REAR_T / 2, C.REAR_T / 2)] * len(pts), chamfer=1.0)
    # socket block at the pod end
    bc = POD_C + D * (C.DISH_R + C.REAR_BLOCK_GAP + C.PORT_BLOCK_LEN / 2)
    Mb = L.frame(bc, D, (0.0, 1.0, 0.0))
    L.union(band, L.add_box_local("block", Mb, (0.0, 0.0, 0.0), (C.PORT_BLOCK, C.REAR_H + 0.2, C.PORT_BLOCK_LEN)))
    # rope eye block at the nape end (band tangent there is -Y)
    ec = eye_centre()
    Me = L.frame(ec, (0.0, -1.0, 0.0), N_OUT)          # local z along the band (-Y), x outward
    L.union(band, L.add_box_local("eye", Me, (0.0, 0.0, 0.0), (ex, ey + 0.2, eb)))
    # spine groove on the head-side face (-N) between the blocks
    gw, gd = C.SPINE_GROOVE
    gi = [i for i, p in enumerate(pts) if 10 < i < len(pts) - 8]
    gpts = [pts[i] for i in gi]
    gext = [(gw / 2, gw / 2, -(C.REAR_T / 2 - gd), C.REAR_T / 2 + 1.0)] * len(gpts)
    L.cut(band, L.ribbon("spine", gpts, W, gext))
    Mm = block_mouth_frame()
    L.cut(band, L.port_socket_cut(Mm, tag="rb"))
    L.cut(band, *L.port_pin_cutters(Mm, -(C.PORT_BLOCK / 2 + 1.0), C.PORT_BLOCK / 2 + 1.0, tag="rb"))
    L.cut(band, L.collar_cutter(Mm, -C.PORT_BLOCK_LEN / 2.0, C.PORT_BLOCK, tag="rb"))
    L.cut(band, L.add_cyl_local("eyehole", Me, (0.0, 0.0, 0.0), C.LOOP_HOLE_DIA / 2, eb + 4.0, axis="Z", verts=24))
    L.fillet(band, width=0.8)    # last: cuts on a filleted mesh leave slivers
    return band


def right_half_matrix() -> Matrix:
    return Matrix.Translation(BACK) @ Matrix.Rotation(math.pi, 4, N_OUT) @ Matrix.Translation(-BACK)


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
