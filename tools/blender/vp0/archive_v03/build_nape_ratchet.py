#!/usr/bin/env -S blender --background --python
"""
build_nape_ratchet.py -- vp0.2 hard-hat style nape ratchet: body, lid, knob.

Both rear-band racks run through the body in stacked channels; a 10-tooth
module-1.25 pinion between them (integral with the knob and shaft) moves
them in opposite directions. A 24-tooth sawtooth rim on the knob is held by
a leaf pawl standing on the body's outer face: turn the knob CCW (seen from
behind) to tighten, pull the pawl tab outward to release.

Outputs (--out-dir): nape_body.stl (outer face down), nape_lid.stl (flat),
nape_knob.stl (knob face down). Qty: 1 each.
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
M = L.frame(BACK, N_OUT, (0.0, -1.0, 0.0))     # u = -Y (to wearer's right), v = W (up), w = outward
HU, HV, HN = C.NAPE_HOUSING                     # 74, 42, 9.6
CH = C.NAPE_CHANNEL_N / 2                       # 2.8
WALL = C.NAPE_WALL
UPPER = (C.RACK_PITCH_W - 1.25 - 0.3, HV / 2 - WALL)        # 4.7 .. 19  (rack strip v range + clearance)
LID_SCREWS = C.NAPE_LID_SCREWS
PAWL_U = C.NAPE_KNOB_D / 2 + 0.7 + 0.45         # leaf centre line (leaf 0.9 thick)
RATCHET_DIR = C.NAPE_RATCHET_DIR
PAWL_ANCHOR = (PAWL_U + 3.5, -14.0)      # (u, v) of the pawl base screw on the outer face

NOTES_BODY = ["print outer face down (channels up); no supports; the C bumper protects the dial from behind and below",
              "hardware: 4x M3x8 thread-forming (lid)"]
NOTES_LID = ["print flat; foam nape pad glues to the head side"]
NOTES_KNOB = ["print knob face down (pinion up); insert from inside the body before fitting the lid"]


def box(name, c, d):
    return L.add_box_local(name, M, c, d)


def make_body():
    """One box minus channels: no coplanar unions, stays manifold."""
    w0 = CH + WALL
    body = box("nape_body", (0.0, 0.0, (w0 - CH) / 2), (HU, HV, w0 + CH))          # w in [-CH, w0]
    L.fillet(body, width=0.8)   # outer edges only; the channel cuts below stay crisp
    ch_lo, ch_hi = UPPER
    ch_c, ch_h = (ch_lo + ch_hi) / 2, ch_hi - ch_lo
    # upper channel: open through the -u wall (left half's rack enters), closed 7 mm before the +u wall
    L.cut(body, box("ch_up", ((-HU / 2 - 1.0 + (HU / 2 - 7.0)) / 2, ch_c, -CH - 0.6 + CH + 0.6 - 0.6 + 0.0), (HU - 7.0 + 1.0, ch_h, 2 * CH + 1.2)))
    L.cut(body, box("ch_lo", ((HU / 2 + 1.0 + (-HU / 2 + 7.0)) / 2, -ch_c, 0.0), (HU - 7.0 + 1.0, ch_h, 2 * CH + 1.2)))
    L.cut(body, L.add_cyl_local("pcav", M, (0.0, 0.0, 0.0), 8.2, 2 * CH + 1.2, axis="Z", verts=48))
    L.cut(body, L.add_cyl_local("shaft", M, (0.0, 0.0, CH + WALL / 2), C.NAPE_SHAFT_D / 2 + 0.2, WALL + 2, axis="Z", verts=32))
    for u, v in LID_SCREWS:
        L.cut(body, L.add_cyl_local("ls", M, (u, v, 0.0), C.M3_TAP_DIA / 2, 2 * CH + WALL + 2, axis="Z", verts=16))
    L.cut(body, L.add_cyl_local("pawlscrew", M, (PAWL_ANCHOR[0], PAWL_ANCHOR[1], w0 - WALL / 2), C.M3_TAP_DIA / 2, WALL + 2, axis="Z", verts=16))
    # C-shaped bumper around the dial (left side + bottom; pawl side and top stay open)
    r_in, r_out, arc = C.NAPE_BUMPER
    a0, a1 = math.radians(100.0), math.radians(300.0)
    n = 40
    poly = [(r_out * math.cos(a0 + (a1 - a0) * i / n), r_out * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    poly += [(r_in * math.cos(a1 - (a1 - a0) * i / n), r_in * math.sin(a1 - (a1 - a0) * i / n)) for i in range(n + 1)]
    L.union(body, L.extrude_polygon("bumper", poly, C.NAPE_KNOB_H + 1.5 + 0.5, M, z0=w0 - 0.5))
    return body


def make_pawl():
    """Leaf pawl on a base plate, screwed to the body's outer face beside the knob."""
    w0 = CH + WALL
    leaf_t, leaf_h = 0.9, 10.0
    base = box("nape_pawl", (PAWL_ANCHOR[0], PAWL_ANCHOR[1], w0 + 1.0), (12.0, 10.0, 2.0))
    L.union(base, box("leaf", (PAWL_U, -2.0, w0 + 1.5 + (leaf_h + 0.5) / 2), (leaf_t, 24.0, leaf_h + 0.5)))
    L.union(base, box("root", (PAWL_U + 2.0, -13.0, w0 + 1.5 + 2.25), (5.0, 6.0, 4.5)))
    L.union(base, box("tooth", (PAWL_U - 1.2, 6.0, w0 + 2.0 + 5.0), (3.0, 4.0, 4.0)))
    L.union(base, box("tab", (PAWL_U + 3.0, 9.0, w0 + 2.0 + 5.0), (6.0, 4.0, 4.0)))
    L.cut(base, L.add_cyl_local("screw", M, (PAWL_ANCHOR[0], PAWL_ANCHOR[1], w0 + 1.0), C.M3_CLEAR_DIA / 2, 4.0, axis="Z", verts=16))
    return base


def make_lid():
    lid = box("nape_lid", (0.0, 0.0, -CH - WALL / 2), (HU, HV, WALL))
    for u, v in LID_SCREWS:
        L.cut(lid, L.add_cyl_local("lh", M, (u, v, -CH - WALL / 2), C.M3_CLEAR_DIA / 2, WALL + 2, axis="Z", verts=16))
    L.fillet(lid, width=0.6)
    return lid


def make_knob():
    w_knob0 = CH + WALL + 0.3
    knob = L.extrude_polygon("nape_knob", L.sawtooth_poly(C.NAPE_RATCHET_TEETH, C.NAPE_KNOB_D / 2 - 1.5, C.NAPE_KNOB_D / 2, 0.15, RATCHET_DIR),
                             C.NAPE_KNOB_H, M, z0=w_knob0)
    L.union(knob, L.add_cyl_local("shaft", M, (0.0, 0.0, (C.PINION_W / 2 - 0.2 + w_knob0 + 0.5) / 2),
                                  C.NAPE_SHAFT_D / 2, w_knob0 + 0.5 - (C.PINION_W / 2 - 0.2), axis="Z", verts=48))
    L.union(knob, L.extrude_polygon("pinion", L.involute_gear_poly(C.PINION_N, C.GEAR_MODULE, C.GEAR_PA), C.PINION_W, M, z0=-C.PINION_W / 2))
    return knob


PARTS = {"nape_body": (make_body, L.rot_dir_to(N_OUT, (0, 0, -1)), NOTES_BODY),
         "nape_lid": (make_lid, L.rot_dir_to(N_OUT, (0, 0, 1)), NOTES_LID),
         "nape_knob": (make_knob, L.rot_dir_to(N_OUT, (0, 0, -1)), NOTES_KNOB),
         "nape_pawl": (make_pawl, L.rot_dir_to(N_OUT, (0, 0, 1)), ["print base plate down; the 0.9 mm leaf is the weakest part of the set: print slow, 100% infill, or in TPU 95A"])}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(L.argv_after_dashdash())
    for name, (mk, rot, notes) in PARTS.items():
        L.reset_scene()
        L.finalize_and_export(mk(), Path(args.out_dir) / f"{name}.stl", rot, notes)


if __name__ == "__main__":
    main()
