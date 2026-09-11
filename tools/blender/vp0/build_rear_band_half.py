#!/usr/bin/env -S blender --background --python
"""
build_rear_band_half.py -- vp0.6 rear band half: tenon into the rear node, rope spine, rack.

30 x 5 chamfered ribbon in a plane tilted ~49 deg (from behind the ear down to
the nape) leaving the cradle's rear node through a tapered tenon (nail through
node and tenon, epoxy), around the occiput to a 50 mm rack strip (module 1.25)
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
         "strap slot pair 24 / 32 mm behind the node: rear leg of the chin strap"]
BACK = Vector((C.REAR_BACK_X, 0.0, C.REAR_BACK_Z))
N_OUT = Vector((-math.cos(math.radians(C.REAR_TILT)), 0.0, -math.sin(math.radians(C.REAR_TILT))))
START = Vector(C.REAR_START)
INSIDE = 8.0                       # the ribbon starts this far inside the node, then is trimmed to the node's rear face


def z_of(x):
    return START.z + (x - START.x) * math.tan(math.radians(C.REAR_TILT))


def centre_pts():
    s0 = START + T_IN * INSIDE
    wps = [(s0.x, s0.y), (START.x - 8.0, START.y - 0.5)] + list(C.REAR_WAYPOINTS[1:]) + [(C.REAR_BACK_X, C.RACK_Y0)]
    samp = L.catmull_rom(wps, samples_per_seg=16)
    return L.resample_polyline([Vector((x, y, z_of(x))) for (x, y) in samp], 2.0)


def spine_run(pts):
    """Exposed span of the rear half: from 2 mm behind the node's rear face to 8 mm short of the rack."""
    return [p for p in pts if p.x < START.x - 2.0 and p.y > C.RACK_Y0 + 8.0]


def outward_sign(run):
    Tv = (run[1] - run[0]).normalized()
    return 1.0 if Tv.cross(W).dot(N_OUT) > 0 else -1.0


def spine_pts(run, offset_out):
    """Run shifted down the band by 6 (channel centre at v -6) and outward by `offset_out`."""
    sgn = outward_sign(run)
    out = []
    for i, p in enumerate(run):
        a = run[max(i - 1, 0)]; b = run[min(i + 1, len(run) - 1)]
        Tv = (b - a).normalized()
        N = Tv.cross(W).normalized() * sgn
        out.append(p + W * ((C.SPINE["rear_v"][0] + C.SPINE["rear_v"][1]) / 2) + N * offset_out)
    return out


def make():
    pts = centre_pts()
    half = C.REAR_H / 2
    band = L.ribbon("rear_band_half", pts, W, [(half, half, C.REAR_T / 2, C.REAR_T / 2)] * len(pts), chamfer=1.0)
    # spine channel in the outer face (3 deep, 4 tall at v -8..-4) over the exposed span; the cover strip is a separate print
    run = spine_run(pts)
    sgn = outward_sign(run)
    d = C.SPINE["rear_d"]
    n_out, n_in = C.REAR_T / 2 + 1.0, d - C.REAR_T / 2
    ext = (n_out, n_in) if sgn > 0 else (n_in, n_out)
    L.cut(band, L.ribbon("spinech", spine_pts(run, 0.0), W, [(C.SPINE["w"] / 2, C.SPINE["w"] / 2, ext[0], ext[1])] * len(run)))
    # strap slots through the band behind the node (first: the solver likes them on the plain ribbon)
    sh, sw = C.STRAP_SLOT
    for s in C.REAR_STRAP_S:
        i = L.arc_index_range(pts, INSIDE + s, 0.0)[0]
        Tv = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        Ms = L.frame(pts[i] + Tv * 0.45, W, Tv)          # off the 2 mm station grid: no cutter face on a ribbon ring
        L.cut(band, L.add_box_local("strap", Ms, (0.0, 0.0, 4.5), (sw + 0.3, C.REAR_T + 2.0, sh)))
    # trim to the node's rear face, then add the tapered tenon (4.8 thick: 0.1 inside the band faces)
    r0, r1 = C.REAR_NODE_W
    L.cut(band, L.add_box("nodebox", (C.REAR_NODE_X, CF.NODE_Y, C.CRADLE_Z + (r0 + r1) / 2), (C.NODE_LEN, CF.NODE_T + 4.0, r1 - r0 + 4.0)))
    L.union(band, L.extrude_polygon("tenon", CF.tenon_poly(0.0, +1), C.CRADLE_TENON[0] - 0.2, CF.tenon_frame(+1), z0=-(C.CRADLE_TENON[0] - 0.2) / 2))
    pz = START.z + 6.0 * T_IN.z
    L.cut(band, L.add_cyl("tpin", (C.TENON_PIN_X, START.y, pz), C.PIN_DIA / 2 + 0.1, 12.0, axis="Y", verts=24))
    # rack strip: u along -Y from y = 50, v along W, w outward
    Mr = L.frame((C.REAR_BACK_X, C.RACK_Y0, z_of(C.REAR_BACK_X)), N_OUT, (0.0, -1.0, 0.0))
    body_h = half - C.RACK_PITCH_W - 0.2
    poly = L.rack_poly(C.RACK_LEN + 2.0, C.GEAR_MODULE, C.GEAR_PA, body_h)
    poly = [(u - C.RACK_SHIFT, C.RACK_PITCH_W - v) for (u, v) in poly]   # phase: a tooth space on y = 0 at the nominal fit
    L.union(band, L.extrude_polygon("rack", poly, C.REAR_T - 0.1, Mr, z0=-(C.REAR_T - 0.1) / 2))
    return band


def right_half_matrix() -> Matrix:
    return Matrix.Translation(BACK) @ Matrix.Rotation(math.pi, 4, N_OUT) @ Matrix.Translation(-BACK)


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
