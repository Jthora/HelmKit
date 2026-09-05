#!/usr/bin/env -S blender --background --python
"""
build_rear_band_half.py -- vp0.6 rear band half: tenon into the rear node, rope spine, rack.

30 x 5 chamfered ribbon in a plane tilted ~49 deg (from behind the ear down to
the nape) leaving the cradle's rear node through a tapered tenon (nail through
node and tenon, epoxy), around the occiput to a 66 mm rack strip (module 1.25)
for the enclosed pull dial. Spine groove on the head-side face, cable groove in
the top edge, strap slot pair behind the node.
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
import build_cradle_front as CF
from mathutils import Matrix, Vector  # type: ignore

W = Vector(C.REAR_W)
T_IN = Vector(C.REAR_T_IN)
PRINT_ROT = L.rot_dir_to(W, (0.0, 0.0, -1.0))
NOTES = ["print with the planar top edge on the bed (rack teeth up); PETG; no supports",
         f"tenon into the cradle's rear node: {C.PIN_DIA} mm nail along Y through node and tenon, epoxy",
         f"spine groove {C.SPINE_GROOVE[0]} x {C.SPINE_GROOVE[1]} on the head-side face; rack {C.RACK_LEN} mm module {C.GEAR_MODULE}",
         "strap slot pair 24 / 32 mm behind the node: rear leg of the chin strap"]
BACK = Vector((C.REAR_BACK_X, 0.0, C.REAR_BACK_Z))
N_OUT = Vector((-math.cos(math.radians(C.REAR_TILT)), 0.0, -math.sin(math.radians(C.REAR_TILT))))
START = Vector(C.REAR_START)
INSIDE = 8.0                       # the ribbon starts this far inside the node, then is trimmed to the node's rear face


def z_of(x):
    return START.z + (x - START.x) * math.tan(math.radians(C.REAR_TILT))


def make():
    s0 = START + T_IN * INSIDE
    wps = [(s0.x, s0.y), (START.x - 8.0, START.y - 0.5)] + list(C.REAR_WAYPOINTS[1:]) + [(C.REAR_BACK_X, 50.0)]
    samp = L.catmull_rom(wps, samples_per_seg=16)
    pts = L.resample_polyline([Vector((x, y, z_of(x))) for (x, y) in samp], 2.0)
    half = C.REAR_H / 2
    band = L.ribbon("rear_band_half", pts, W, [(half, half, C.REAR_T / 2, C.REAR_T / 2)] * len(pts), chamfer=1.0)
    # trim to the node's rear face, then add the tapered tenon (4.8 thick: 0.1 inside the band faces)
    r0, r1 = C.REAR_NODE_W
    L.cut(band, L.add_box("nodebox", (C.REAR_NODE_X, CF.NODE_Y, C.CRADLE_Z + (r0 + r1) / 2), (C.NODE_LEN, CF.NODE_T + 4.0, r1 - r0 + 4.0)))
    L.union(band, L.extrude_polygon("tenon", CF.tenon_poly(0.0, +1), C.CRADLE_TENON[0] - 0.2, CF.tenon_frame(+1), z0=-(C.CRADLE_TENON[0] - 0.2) / 2))
    pz = START.z + 6.0 * T_IN.z
    L.cut(band, L.add_cyl("tpin", (C.TENON_PIN_X, START.y, pz), C.PIN_DIA / 2 + 0.1, 12.0, axis="Y", verts=24))
    # spine groove on the head-side face, clear of the node and the rack; cable groove in the top edge
    gw, gd = C.SPINE_GROOVE
    gi = L.arc_index_range(pts, INSIDE + 12.0, 6.0)
    gpts = [pts[i] for i in gi]
    L.cut(band, L.ribbon("spine", gpts, W, [(gw / 2, gw / 2, -(C.REAR_T / 2 - gd), C.REAR_T / 2 + 1.0)] * len(gpts)))
    cw, cd = C.CABLE_GROOVE
    ci = L.arc_index_range(pts, INSIDE + 2.0, 0.0)
    cpts = [pts[i] + W * (half - cd / 2) for i in ci]
    L.cut(band, L.ribbon("cable", cpts, W, [(cd / 2 + 1.0, cd / 2, 1.3, 0.9)] * len(cpts)))
    # strap slots through the band behind the node
    sh, sw = C.STRAP_SLOT
    for s in C.REAR_STRAP_S:
        i = L.arc_index_range(pts, INSIDE + s, 0.0)[0]
        Tv = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        Ms = L.frame(pts[i] + Tv * 0.45, W, Tv)          # off the 2 mm station grid: no cutter face on a ribbon ring
        L.cut(band, L.add_box_local("strap", Ms, (0.0, 0.0, 4.5), (sw + 0.3, C.REAR_T + 2.0, sh)))
    # rack strip: u along -Y from y = 50, v along W, w outward
    Mr = L.frame((C.REAR_BACK_X, 50.0, z_of(C.REAR_BACK_X)), N_OUT, (0.0, -1.0, 0.0))
    body_h = half - C.RACK_PITCH_W - 0.2
    poly = L.rack_poly(C.RACK_LEN + 2.0, C.GEAR_MODULE, C.GEAR_PA, body_h)
    poly = [(u - 2.0, C.RACK_PITCH_W - v) for (u, v) in poly]
    L.union(band, L.extrude_polygon("rack", poly, C.REAR_T - 0.1, Mr, z0=-(C.REAR_T - 0.1) / 2))
    return band


def right_half_matrix() -> Matrix:
    return Matrix.Translation(BACK) @ Matrix.Rotation(math.pi, 4, N_OUT) @ Matrix.Translation(-BACK)


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
