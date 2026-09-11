#!/usr/bin/env -S blender --background --python
"""
build_nape_dial.py -- nape modules (--out-dir): the print-one PINLOCK block, and the enclosed PULL dial (body, cover, lid, dial, key, pinion, retainer).

Local frame at the nape: u = -Y (wearer's right), v = W (up the band), w = outward.
  lid     w -5.0 .. -2.8   head side, carries the axle head and the foam pad
  body    w -2.8 .. 4.8    closed rack channels, pinion cavity through the outer wall, cover bosses,
                           RATCHET RING on its outer face (w 4.8 .. 5.8)
  pinion  w -1.5 .. 3.5    integral hub to w 8.5 with three drive lugs into the dial
  dial    w  6.0 .. 14.0   Ø44, ratchet teeth on its INNER face (reach down to w 5.0), spring well in the
                           outer face, two thread holes for the key cap
  key     w 14.0 .. 26.5   Ø28 ring screwed to the dial face with two 18 x 3 x 10 ribs: pinch and pull
  cover   w  4.8 .. 21.5   tray with a Ø28 window; the ribs sit below its face
Spring (3/8 x 1/2 in) sits in a seat on the dial's outer face and pushes the dial INWARD against a
printed retainer threaded on the axle: the teeth stay meshed; a blow to the face only meshes them harder. Turning to tighten
clicks over the ramps. Pinch the ribs, pull 1.5 mm, turn to loosen. Axle: M5 x 25, head epoxied to
the lid; the retainer sets the preload (10-15 N at 6.5 mm working length).
v0.7 compact: 52 x 44 x 26.5 (was 80 x 54 x 33); racks 50, travel +/- 7.
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


def ring(name, w, normal_sign, phase_deg=0.0):
    """Face ratchet ring on the nape axis. `phase_deg` rotates it so no tooth vertex lands on a revolve's radial line."""
    ob = L.face_ratchet_ring(name, M @ Vector((0.0, 0.0, w)), M.to_3x3() @ Vector((0.0, 0.0, normal_sign)),
                             RI, RO, C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR)
    if phase_deg:
        ob.matrix_world = M @ Matrix.Rotation(math.radians(phase_deg), 4, "Z") @ M.inverted() @ ob.matrix_world
        L.apply_transform(ob)
    return ob


def make_body():
    w0 = -CH
    body = box("nape_body", (0.0, 0.0, (w0 + W1) / 2), (HU, HV, W1 - w0))
    for u, v in C.NAPE_COVER_SCREWS:
        L.union(body, box("boss", (u, v, W1 + 3.0 - 0.5), (7.0, 7.0, 7.0)))
    L.fillet(body, width=0.8)
    lo, hi = UPPER
    ch_c, ch_h = (lo + hi) / 2, hi - lo
    L.cut(body, box("ch_up", ((-HU / 2 - 1.0 + HU / 2 - 3.0) / 2, ch_c, 0.0), (HU - 2.0, ch_h, 2 * CH + 2.0)))   # open at one end, 3 mm wall at the other
    L.cut(body, box("ch_lo", ((HU / 2 + 1.0 - HU / 2 + 3.0) / 2, -ch_c, 0.0), (HU - 2.0, ch_h, 2 * CH + 2.0)))
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
        lr, lt = C.NAPE_LUG
        L.union(pin, box("lug", (C.NAPE_LUG_R * math.cos(a), C.NAPE_LUG_R * math.sin(a), D_W0 + RECESS_D / 2 - 0.2), (lr, lt, RECESS_D - 0.6)))
    L.cut(pin, cyl("axlebore", (0.0, 0.0, (C.NAPE_PINION_W0 + hub_w1) / 2), AXLE_R, hub_w1 - C.NAPE_PINION_W0 + 2.0, verts=32))
    return pin


def make_dial():
    dial = L.revolve("nape_dial", [(0.0, D_W0), (DIAL_R, D_W0), (DIAL_R, D_W0 + D_T), (0.0, D_W0 + D_T)], axis="Z",
                     center=(0.0, 0.0, 0.0), segments=100)   # 100 segments: no shared radial lines with the 24-tooth ring (120 fails)
    dial.matrix_world = M @ dial.matrix_world
    L.apply_transform(dial)
    # hub recess + lug slots from the inner face; spring well from the outer face; axle bore through
    L.cut(dial, cyl("recess", (0.0, 0.0, D_W0 + RECESS_D / 2 - 1.0), HUB_R + 0.25, RECESS_D + 2.0, verts=64))
    for k in range(3):
        a = 2 * math.pi * k / 3
        lr, lt = C.NAPE_LUG
        L.cut(dial, box("lugslot", (C.NAPE_LUG_R * math.cos(a), C.NAPE_LUG_R * math.sin(a), D_W0 + RECESS_D / 2 - 1.15), (lr + 0.6, lt + 0.6, RECESS_D + 1.7)))
    wd, wdepth = C.NAPE_SPRING_WELL
    L.cut(dial, cyl("well", (0.0, 0.0, D_W0 + D_T - wdepth / 2 + 0.5), wd / 2, wdepth + 1.0, verts=48))
    L.cut(dial, cyl("axle", (0.0, 0.0, D_W0 + D_T / 2), AXLE_R + 0.05, D_T + 2.0, verts=32))
    for u, v in C.NAPE_KEY_SCREWS:
        L.cut(dial, cyl("ks", (u, v, D_W0 + D_T - 2.25 + 0.5), C.M3_TAP_DIA / 2, 5.5, verts=16))   # 4.5 deep: stops 0.5 above the teeth
    # no fillet on the dial: the bevel pass leaves edges the teeth-ring union cannot resolve (it reverted anyway in v0.6)
    L.union(dial, ring("teeth", D_W0, -1.0))
    return dial


def make_retainer():
    """Retainer on the M5 axle tip: a Ø12 washer with an M5 nut in a hex pocket on its outer face (printed threads strip). The nut sets the spring preload."""
    rd, rt, rh = C.NAPE_RETAINER
    w0 = D_W0 + D_T - C.NAPE_SPRING_WELL[1] + C.NAPE_SPRING["working"]
    r = cyl("nape_retainer", (0.0, 0.0, w0 + rt / 2), rd / 2, rt, verts=48)
    L.cut(r, cyl("bore", (0.0, 0.0, w0 + rt / 2), rh / 2, rt + 2.0, verts=24))
    nut = L.add_hex_prism("nut", (0.0, 0.0, 0.0), C.M5_NUT_AF + 0.3, 2 * 3.2)
    nut.matrix_world = M @ Matrix.Translation((0.0, 0.0, w0 + rt)) @ Matrix.Rotation(math.radians(7.0), 4, "Z") @ nut.matrix_world
    L.apply_transform(nut)
    L.cut(r, nut)
    return r


def lobed_poly(centres, r, n_arc=8):
    """Outline of the union of equal circles centred on the u axis (spacing < 2r): a lobed slot, one clean polygon."""
    cs = sorted(centres)
    d = cs[1] - cs[0] if len(cs) > 1 else 0.0
    phi = math.acos(min(1.0, d / (2 * r))) if d < 2 * r else 0.0
    pts = []
    for i, c in enumerate(cs):                    # top arcs, left to right
        a0 = math.pi if i == 0 else math.pi - phi
        a1 = 0.0 if i == len(cs) - 1 else phi
        for k in range(n_arc + 1):
            if (i > 0 and k == 0):
                continue                          # shared waist point already emitted
            a = a0 + (a1 - a0) * k / n_arc
            pts.append((c + r * math.cos(a), r * math.sin(a)))
    for i, c in reversed(list(enumerate(cs))):    # bottom arcs, right to left
        a0 = 0.0 if i == len(cs) - 1 else -phi
        a1 = -math.pi if i == 0 else -(math.pi - phi)
        for k in range(n_arc + 1):
            if k == 0:
                continue                          # (c_last, 0) / waist points already emitted
            a = a0 + (a1 - a0) * k / n_arc
            pts.append((c + r * math.cos(a), r * math.sin(a)))
    return pts[:-1]                               # last point == first (leftmost, angle -pi == pi)


def make_pinlock():
    """Print-one nape module: a one-piece block with two rack tunnels (each open at its own end) and four vertical Ø2.2 holes
    on the mid-plane at u = 0, p/2, p, 3p/2. Two 2 mm nails dropped through the top wall pass both racks' tooth spaces
    (whole-pitch settings use 0 and p, half-pitch ones p/2 and 3p/2): two teeth per rack, 3.9 mm steps of circumference.
    Heads sit flush in counterbores; the bottom wall is a snug 2.1 so the nails stay put; a lanyard hole takes their thread."""
    T = C.NAPE_PINLOCK_T
    ch = CH + 0.5
    pin = C.NAPE_PINLOCK_PIN
    pl = box("nape_pinlock", (0.0, 0.0, 0.0), (HU, HV, T))
    L.fillet(pl, width=0.8)
    lo, hi = UPPER
    ch_c, ch_h = (lo + hi) / 2, hi - lo
    L.cut(pl, box("ch_up", ((-HU / 2 - 1.0 + HU / 2 - 3.0) / 2, ch_c, 0.0), (HU - 2.0, ch_h, 2 * ch)))    # left rack enters from -u (+Y)
    L.cut(pl, box("ch_lo", ((HU / 2 + 1.0 - HU / 2 + 3.0) / 2, -ch_c, 0.0), (HU - 2.0, ch_h, 2 * ch)))    # right rack enters from +u
    v_bot_in = -HV / 2 + WALL                     # inner face of the bottom wall (inside the lower tunnel)
    cb_d, cb_h = pin["cbore"]
    Mv = M @ Matrix.Rotation(-math.pi / 2.0, 4, "X")            # local z -> +v, local x -> u
    us = list(C.NAPE_PINLOCK_HOLES)
    L.cut(pl, L.extrude_polygon("pins", lobed_poly(us, pin["hole"] / 2), HV / 2 + 1.0 - (v_bot_in + 0.5), Mv, z0=v_bot_in + 0.5))
    L.cut(pl, L.extrude_polygon("pinsb", lobed_poly(us, pin["hole_bottom"] / 2), v_bot_in + 0.3 + HV / 2 + 1.0, Mv, z0=-HV / 2 - 1.0))
    L.cut(pl, L.extrude_polygon("cbores", lobed_poly(us, cb_d / 2), cb_h + 1.0, Mv, z0=HV / 2 - cb_h))
    L.cut(pl, cyl("lanyard", (-HU / 2 + 4.0, 0.0, 0.0), 1.1, T + 2.0, verts=12))
    return pl


def make_key():
    """Key cap: Ø28 ring on the dial's outer face with two pull ribs; the spring passes through the middle."""
    w0 = D_W0 + D_T
    key = cyl("nape_key", (0.0, 0.0, w0 + KEY_T / 2), KEY_OD / 2, KEY_T, verts=64)
    rl, rw, rh, rv = C.NAPE_KEY_RIBS
    for sv in (+1, -1):
        L.union(key, box("rib", (sv * rv, 0.0, w0 + KEY_T + rh / 2 - 0.5), (rw, rl, rh + 1.0)))   # ribs along v at u = +/- rv, screws at v = +/- 9 between them
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
    "nape_retainer": (make_retainer, L.rot_dir_to(N_OUT, (0, 0, 1)), ["print flat, nut pocket up; press an M5 nut in, run it down the axle against the spring to the chosen preload, thread-lock"]),
    "nape_pinlock": (make_pinlock, L.rot_dir_to(M.to_3x3() @ Vector((0.0, 1.0, 0.0)), (0, 0, 1)), ["print standing on its bottom end (nail holes vertical and round; 6.6 mm tunnel bridges); brim", "slide both racks in, drop the two 2 mm nails through the pair of holes whose tooth spaces line up (0 + p, or p/2 + 3p/2); heads flush; tie both to the lanyard hole"]),
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
