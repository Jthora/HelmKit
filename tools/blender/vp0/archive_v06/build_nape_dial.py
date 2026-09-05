#!/usr/bin/env -S blender --background --python
"""
build_nape_dial.py -- vp0.6 enclosed PULL dial (--out-dir): body, cover, lid, dial, key, pinion.

Local frame at the nape: u = -Y (wearer's right), v = W (up the band), w = outward.
  lid     w -5.0 .. -2.8   head side, carries the axle head and the foam pad
  body    w -2.8 .. 4.8    closed rack channels, pinion cavity through the outer wall, cover bosses,
                           RATCHET RING on its outer face (w 4.8 .. 5.8)
  pinion  w -1.5 .. 3.5    integral hub to w 8.5 with three drive lugs into the dial
  dial    w  6.0 .. 14.0   Ø44, ratchet teeth on its INNER face (reach down to w 5.0), spring well in the
                           outer face, two thread holes for the key cap
  key     w 14.0 .. 26.5   Ø28 ring screwed to the dial face with two 18 x 3 x 10 ribs: pinch and pull
  cover   w  4.8 .. 28.0   tray with a Ø30 window; the ribs sit 1.5 mm below its face
Spring (3/8 x 3/4 in) sits in the dial's well and pushes the dial INWARD against a washer + M5 nyloc
on the axle: the teeth stay meshed; a blow to the face only meshes them harder. Turning to tighten
clicks over the ramps. Pinch the ribs, pull 1.5 mm, turn to loosen. Axle: M5 x 35, head epoxied to
the lid; the nut sets the preload (15-20 N at 9 mm working length).
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
M = L.frame(BACK, N_OUT, (0.0, -1.0, 0.0))
HU, HV = C.NAPE_HU, C.NAPE_HV
CH, WALL = C.NAPE_CH, C.NAPE_WALL
W1 = C.NAPE_BODY_W1                       # 4.8
UPPER = (C.RACK_PITCH_W - 1.25 - 0.3, HV / 2 - WALL)     # rack strip v range + clearance
DIAL_R = C.NAPE_DIAL_D / 2
D_W0, D_T = C.NAPE_DIAL_W0, C.NAPE_DIAL_T                # 6.0, 8
COV_W0 = C.NAPE_COVER_W0                                 # 25.0
COV_T = 3.0
HUB_R = C.NAPE_HUB_D / 2                                 # 7
AXLE_R = 2.75
RECESS_D = 2.5                                           # dial recess that captures the hub end + lugs
RI, RO = C.NAPE_RATCHET_R
KEY_OD, KEY_ID, KEY_T = C.NAPE_KEY


def box(name, c, d):
    return L.add_box_local(name, M, c, d)


def cyl(name, c, r, depth, verts=48):
    return L.add_cyl_local(name, M, c, r, depth, axis="Z", verts=verts)


def ring(name, w, normal_sign):
    return L.face_ratchet_ring(name, M @ Vector((0.0, 0.0, w)), M.to_3x3() @ Vector((0.0, 0.0, normal_sign)),
                               RI, RO, C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR)


def make_body():
    w0 = -CH
    body = box("nape_body", (0.0, 0.0, (w0 + W1) / 2), (HU, HV, W1 - w0))
    for u, v in C.NAPE_COVER_SCREWS:
        L.union(body, box("boss", (u, v, W1 + 3.0 - 0.5), (7.0, 7.0, 7.0)))
    L.fillet(body, width=0.8)
    lo, hi = UPPER
    ch_c, ch_h = (lo + hi) / 2, hi - lo
    L.cut(body, box("ch_up", ((-HU / 2 - 1.0 + HU / 2 - 7.0) / 2, ch_c, 0.0), (HU - 6.0, ch_h, 2 * CH + 2.0)))
    L.cut(body, box("ch_lo", ((HU / 2 + 1.0 - HU / 2 + 7.0) / 2, -ch_c, 0.0), (HU - 6.0, ch_h, 2 * CH + 2.0)))
    L.cut(body, cyl("pcav", (0.0, 0.0, (W1 + 1.0 - CH - 1.0) / 2), C.NAPE_PINION_CAV_R, W1 + CH + 2.0))
    for u, v in C.NAPE_LID_SCREWS:
        L.cut(body, cyl("ls", (u, v, 0.0), C.M3_TAP_DIA / 2, 2 * CH + WALL + 4.0, verts=16))
    for u, v in C.NAPE_COVER_SCREWS:
        L.cut(body, cyl("cs", (u, v, W1 + 3.0), C.M3_TAP_DIA / 2, 8.0, verts=16))
    L.union(body, ring("ring", W1, +1.0))
    return body


def make_cover(fillet=True):
    depth = COV_W0 + COV_T - W1
    cover = box("nape_cover", (0.0, 0.0, W1 + depth / 2), (HU, HV, depth))
    if fillet:
        L.fillet(cover, width=1.5, segments=3)
    L.cut(cover, box("cav", (0.0, 0.0, W1 + (COV_W0 - W1) / 2 - 1.0), (HU - 2 * WALL, HV - 2 * WALL, COV_W0 - W1 + 2.0)))
    for u, v in C.NAPE_COVER_SCREWS:
        L.cut(cover, cyl("cs", (u, v, COV_W0 + COV_T / 2), C.M3_CLEAR_DIA / 2, COV_T + 2.0, verts=16))
        L.cut(cover, cyl("csh", (u, v, COV_W0 + COV_T - 0.5), 3.1, 3.0, verts=16))
    L.cut(cover, cyl("window", (0.0, 0.0, COV_W0 + COV_T / 2), C.NAPE_WINDOW_D / 2, COV_T + 2.0, verts=64))
    L.cut(cover, cyl("drain", (0.0, -HV / 2 + WALL / 2, W1 + 6.0), 1.5, WALL + 2.0, verts=12))   # drain hole low in the tray wall
    if fillet and L.mesh_stats(cover)["nonmanifold_edges"]:
        print("nape_cover: filleted build not manifold, rebuilding without the fillet")
        L.delete(cover)
        return make_cover(fillet=False)
    return cover


def make_lid():
    lid = box("nape_lid", (0.0, 0.0, -CH - C.NAPE_LID_T / 2), (HU, HV, C.NAPE_LID_T))
    L.fillet(lid, width=0.6)
    for u, v in C.NAPE_LID_SCREWS:
        L.cut(lid, cyl("lh", (u, v, -CH - C.NAPE_LID_T / 2), C.M3_CLEAR_DIA / 2, C.NAPE_LID_T + 2.0, verts=16))
    L.cut(lid, cyl("axle", (0.0, 0.0, -CH - C.NAPE_LID_T / 2), AXLE_R, C.NAPE_LID_T + 2.0, verts=32))
    L.cut(lid, cyl("head", (0.0, 0.0, -CH - C.NAPE_LID_T), 4.6, 2.0, verts=32))
    return lid


def make_pinion():
    """Pinion + hub + three drive lugs into the dial's recess; the axle passes through."""
    Mp = M @ Matrix.Translation((0.0, 0.0, C.NAPE_PINION_W0))
    pin = L.extrude_polygon("nape_pinion", L.involute_gear_poly(C.PINION_N, C.GEAR_MODULE, C.GEAR_PA), C.PINION_W, Mp)
    hub_w0 = C.NAPE_PINION_W0 + C.PINION_W - 0.2
    hub_w1 = D_W0 + RECESS_D
    L.union(pin, cyl("hub", (0.0, 0.0, (hub_w0 + hub_w1) / 2), HUB_R, hub_w1 - hub_w0, verts=64))
    for k in range(3):
        a = 2 * math.pi * k / 3
        L.union(pin, box("lug", ((HUB_R + 1.5) * math.cos(a), (HUB_R + 1.5) * math.sin(a), D_W0 + RECESS_D / 2 - 0.2), (4.0, 3.0, RECESS_D - 0.6)))
    L.cut(pin, cyl("axlebore", (0.0, 0.0, (C.NAPE_PINION_W0 + hub_w1) / 2), AXLE_R, hub_w1 - C.NAPE_PINION_W0 + 2.0, verts=32))
    return pin


def make_dial():
    dial = L.revolve("nape_dial", [(0.0, D_W0), (DIAL_R, D_W0), (DIAL_R, D_W0 + D_T), (0.0, D_W0 + D_T)], axis="Z",
                     center=(0.0, 0.0, 0.0), segments=120)
    dial.matrix_world = M @ dial.matrix_world
    L.apply_transform(dial)
    # hub recess + lug slots from the inner face; spring well from the outer face; axle bore through
    L.cut(dial, cyl("recess", (0.0, 0.0, D_W0 + RECESS_D / 2 - 1.0), HUB_R + 0.25, RECESS_D + 2.0, verts=64))
    for k in range(3):
        a = 2 * math.pi * k / 3
        L.cut(dial, box("lugslot", ((HUB_R + 1.5) * math.cos(a), (HUB_R + 1.5) * math.sin(a), D_W0 + RECESS_D / 2 - 1.15), (4.6, 3.6, RECESS_D + 1.7)))
    wd, wdepth = C.NAPE_SPRING_WELL
    L.cut(dial, cyl("well", (0.0, 0.0, D_W0 + D_T - wdepth / 2 + 0.5), wd / 2, wdepth + 1.0, verts=48))
    L.cut(dial, cyl("axle", (0.0, 0.0, D_W0 + D_T / 2), AXLE_R + 0.05, D_T + 2.0, verts=32))
    for u, v in C.NAPE_KEY_SCREWS:
        L.cut(dial, cyl("ks", (u, v, D_W0 + D_T - 3.0 + 0.5), C.M3_TAP_DIA / 2, 7.0, verts=16))
    L.fillet(dial, width=0.8)
    L.union(dial, ring("teeth", D_W0, -1.0))
    return dial


def make_key():
    """Key cap: Ø28 ring on the dial's outer face with two pull ribs; the spring passes through the middle."""
    w0 = D_W0 + D_T
    key = cyl("nape_key", (0.0, 0.0, w0 + KEY_T / 2), KEY_OD / 2, KEY_T, verts=64)
    rl, rw, rh, rv = C.NAPE_KEY_RIBS
    for sv in (+1, -1):
        L.union(key, box("rib", (0.0, sv * rv, w0 + KEY_T + rh / 2 - 0.5), (rl, rw, rh + 1.0)))
    L.fillet(key, width=0.6)
    L.cut(key, cyl("hole", (0.0, 0.0, w0 + KEY_T / 2), KEY_ID / 2, KEY_T + 2.0, verts=48))
    for u, v in C.NAPE_KEY_SCREWS:
        L.cut(key, cyl("ks", (u, v, w0 + KEY_T / 2), C.M3_CLEAR_DIA / 2, KEY_T + 2.0, verts=16))
        L.cut(key, cyl("ksh", (u, v, w0 + KEY_T + 0.5), 3.1, 3.0, verts=16))
    return key


PARTS = {
    "nape_body": (make_body, L.rot_dir_to(N_OUT, (0, 0, 1)), ["print outer face up (channels down, 14 mm bridges); the ratchet ring prints upward; no supports"]),
    "nape_cover": (make_cover, L.rot_dir_to(N_OUT, (0, 0, -1)), ["print window face down; no supports"]),
    "nape_lid": (make_lid, L.rot_dir_to(N_OUT, (0, 0, -1)), ["print head-side face up; foam pad glues over the axle head"]),
    "nape_dial": (make_dial, L.rot_dir_to(N_OUT, (0, 0, -1)), ["print outer face down (well and key screw holes down), teeth up; no supports"]),
    "nape_key": (make_key, L.rot_dir_to(N_OUT, (0, 0, 1)), ["print ring down, ribs up; two M3 x 6 into the dial face"]),
    "nape_pinion": (make_pinion, L.rot_dir_to(N_OUT, (0, 0, 1)), ["print pinion down, lugs up; no supports"]),
}


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
