#!/usr/bin/env -S blender --background --python
"""
build_nape_plate.py -- vp0.4 nape plate with a printed clam cleat.

74 x 36 x 6 plate in the rear band plane between the two rope eyes, foam
pad on the head side, a rope channel through it and a no-moving-parts clam
cleat on the outer face. Rope: knot at the right eye, through the plate
channel, through the left eye, back into the cleat. Pull the tail to
tighten, lift it out of the V to release.
Print: outer face up. Qty: 1.
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

BACK = Vector((C.REAR_BACK_X, 0.0, C.REAR_BACK_Z))
N_OUT = Vector((-math.cos(math.radians(C.REAR_TILT)), 0.0, -math.sin(math.radians(C.REAR_TILT))))
M = L.frame(BACK, N_OUT, (0.0, -1.0, 0.0))      # u = -Y (to the wearer's right), v = W (up), w = outward
PRINT_ROT = L.rot_dir_to(N_OUT, (0.0, 0.0, 1.0))
NOTES = ["print outer face (cleat) up; no supports; the rope channel bridges 4 mm",
         f"rope {C.ROPE_DIA} mm: knot at the right eye, through the channel, through the left eye, back into the cleat"]


def make():
    pu, pv, pw = C.NAPE_PLATE
    plate = L.add_box_local("nape_plate", M, (0.0, 0.0, 0.0), (pu, pv, pw))
    L.fillet(plate, width=0.8)
    L.union(plate, L.clam_cleat("cleat", M, base_z=pw / 2.0 - 0.5))
    # rope channel through the plate along u at the band mid-plane
    L.cut(plate, L.add_cyl_local("channel", M, (0.0, 0.0, 0.0), C.LOOP_HOLE_DIA / 2, pu + 4.0, axis="X", verts=24))
    # tail keeper notch at the +u end of the outer face
    L.cut(plate, L.add_box_local("keeper", M, (pu / 2 - 4.0, 9.0, pw / 2 + 1.0), (2.2, 8.0, 4.0)))
    return plate


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
