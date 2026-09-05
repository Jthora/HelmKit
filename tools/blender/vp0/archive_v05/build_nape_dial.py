#!/usr/bin/env -S blender --background --python
"""
build_nape_dial.py -- vp0.5 enclosed nape dial (--out-dir): body, cover, lid, dial, pinion.

Local frame at the nape: u = -Y (wearer's right), v = W (up the band), w = outward.
  lid     w -5.0 .. -2.8   head side, carries the axle head and the foam pad
  body    w -2.8 .. 4.8    closed rack channels, pinion cavity through the outer wall, cover bosses
  pinion  w -1.5 .. 3.5    integral tube hub to w 10.8 with three drive lugs into the dial
  dial    w  7.8 .. 15.8   Ø40, face ratchet teeth on the outer face, spring well inside
  cover   w  4.8 .. 20.0   tray with the mating ratchet ring on its inner face and a Ø34 window
Spring (3/8 x 3/4 in compression) sits on the body face inside the hub tube and pushes the dial
outward into the cover's teeth. Turning to tighten clicks over the ramps; press the dial face
in 1.5 mm and turn to loosen. Axle: M5 x 20 bolt, head epoxied to the lid, tip free in the well.
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
D_W0, D_T = C.NAPE_DIAL_W0, C.NAPE_DIAL_T                # 7.8, 8
COV_W0 = C.NAPE_COVER_W0                                 # 17.0
COV_T = 3.0
HUB_R, HUB_RI = C.NAPE_HUB_D / 2, C.NAPE_SPRING_WELL[0] / 2   # 7, 5.5
AXLE_R = 2.75
RECESS_D = 3.0                                           # dial recess that captures the hub end + lugs
RI, RO = C.NAPE_RATCHET_R


def box(name, c, d):
    return L.add_box_local(name, M, c, d)


def cyl(name, c, r, depth, verts=48):
    return L.add_cyl_local(name, M, c, r, depth, axis="Z", verts=verts)


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
    L.cut(body, cyl("springseat", (0.0, 0.0, W1), HUB_RI + 0.3, 2.0, verts=32))
    for u, v in C.NAPE_LID_SCREWS:
        L.cut(body, cyl("ls", (u, v, 0.0), C.M3_TAP_DIA / 2, 2 * CH + WALL + 4.0, verts=16))
    for u, v in C.NAPE_COVER_SCREWS:
        L.cut(body, cyl("cs", (u, v, W1 + 3.0), C.M3_TAP_DIA / 2, 8.0, verts=16))
    return body


def make_cover(fillet=True):
    depth = COV_W0 + COV_T - W1
    cover = box("nape_cover", (0.0, 0.0, W1 + depth / 2), (HU, HV, depth))
    if fillet:
        L.fillet(cover, width=1.5, segments=3)      # outer edges only, before any cut
    L.cut(cover, box("cav", (0.0, 0.0, W1 + (COV_W0 - W1) / 2 - 1.0), (HU - 2 * WALL, HV - 2 * WALL, COV_W0 - W1 + 2.0)))
    for u, v in C.NAPE_COVER_SCREWS:
        L.cut(cover, cyl("cs", (u, v, COV_W0 + COV_T / 2), C.M3_CLEAR_DIA / 2, COV_T + 2.0, verts=16))
        L.cut(cover, cyl("csh", (u, v, COV_W0 + COV_T - 0.5), 3.1, 3.0, verts=16))
    L.cut(cover, cyl("window", (0.0, 0.0, COV_W0 + COV_T / 2), C.NAPE_WINDOW_D / 2, COV_T + 2.0, verts=64))
    L.union(cover, L.face_ratchet_ring("ring", M @ Vector((0.0, 0.0, COV_W0)), M.to_3x3() @ Vector((0.0, 0.0, -1.0)),
                                       RI, RO, C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR))
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
    """Pinion + tube hub + three drive lugs; the spring passes through the tube."""
    Mp = M @ Matrix.Translation((0.0, 0.0, C.NAPE_PINION_W0))
    pin = L.extrude_polygon("nape_pinion", L.involute_gear_poly(C.PINION_N, C.GEAR_MODULE, C.GEAR_PA), C.PINION_W, Mp)
    hub_w0 = C.NAPE_PINION_W0 + C.PINION_W - 0.2
    hub_w1 = D_W0 + RECESS_D
    L.union(pin, L.add_cyl_local("hubtube", M, (0.0, 0.0, (hub_w0 + hub_w1) / 2), HUB_R, hub_w1 - hub_w0, axis="Z", verts=64))
    for k in range(3):
        a = 2 * math.pi * k / 3
        L.union(pin, box("lug", ((HUB_R + 1.5) * math.cos(a), (HUB_R + 1.5) * math.sin(a), D_W0 + RECESS_D / 2 - 0.2), (4.0, 3.0, RECESS_D - 0.6)))
    L.cut(pin, cyl("bore", (0.0, 0.0, (C.NAPE_PINION_W0 + hub_w1) / 2), HUB_RI, hub_w1 - C.NAPE_PINION_W0 + 2.0, verts=48))
    L.cut(pin, cyl("axlebore", (0.0, 0.0, C.NAPE_PINION_W0 + C.PINION_W / 2), AXLE_R, C.PINION_W + 2.0, verts=32))
    return pin


def make_dial():
    dial = L.revolve("nape_dial", [(0.0, D_W0), (DIAL_R, D_W0), (DIAL_R, D_W0 + D_T), (0.0, D_W0 + D_T)], axis="Z",
                     center=(0.0, 0.0, 0.0), segments=96)
    dial.matrix_world = M @ dial.matrix_world
    L.apply_transform(dial)
    # hub recess + lug slots + spring well from the inner face
    L.cut(dial, cyl("recess", (0.0, 0.0, D_W0 + RECESS_D / 2 - 1.0), HUB_R + 0.25, RECESS_D + 2.0, verts=64))
    for k in range(3):
        a = 2 * math.pi * k / 3
        L.cut(dial, box("lugslot", ((HUB_R + 1.5) * math.cos(a), (HUB_R + 1.5) * math.sin(a), D_W0 + RECESS_D / 2 - 1.15), (4.6, 3.6, RECESS_D + 1.7)))   # top 0.3 below the recess floor
    wd, wdepth = C.NAPE_SPRING_WELL
    L.cut(dial, cyl("well", (0.0, 0.0, D_W0 + RECESS_D + (wdepth - RECESS_D) / 2 - 0.5), wd / 2, wdepth - RECESS_D + 1.0, verts=48))
    # grip grooves on the outer face inside the ratchet ring
    for k in range(12):
        a = 2 * math.pi * k / 12
        Mg = M @ Matrix.Translation((0.0, 0.0, D_W0 + D_T)) @ Matrix.Rotation(a, 4, "Z")
        L.cut(dial, L.add_box_local("grip", Mg, ((RI - 2.0) / 2 + 2.0, 0.0, 0.0), (RI - 4.0, 1.4, 1.6)))
    L.fillet(dial, width=1.0)
    L.union(dial, L.face_ratchet_ring("teeth", M @ Vector((0.0, 0.0, D_W0 + D_T)), M.to_3x3() @ Vector((0.0, 0.0, 1.0)),
                                      RI, RO, C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR))
    return dial


PARTS = {
    "nape_body": (make_body, L.rot_dir_to(N_OUT, (0, 0, 1)), ["print outer face up (channels down, 14 mm bridges); no supports"]),
    "nape_cover": (make_cover, L.rot_dir_to(N_OUT, (0, 0, -1)), ["print window face down; the ratchet ring prints upward inside the tray"]),
    "nape_lid": (make_lid, L.rot_dir_to(N_OUT, (0, 0, -1)), ["print head-side face up; foam pad glues over the axle head"]),
    "nape_dial": (make_dial, L.rot_dir_to(N_OUT, (0, 0, 1)), ["print inner face down, teeth up; no supports"]),
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
