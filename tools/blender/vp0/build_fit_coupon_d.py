#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon_d.py -- Track P fit coupon D: the BRACKETING coupons (--out-dir emits TWO plates).

Coupons A and B each gave one data point per fit, so every miss cost another four-hour print. D gives a
LADDER for every fit that failed, so one print brackets the answer instead of iterating.

WHY TWO PLATES (2026-09-17). The first coupon D was a single 236 x 150 plate and it was dragged off the bed a
few layers in, three times. The cause was SIZE: 35,400 mm2 against coupon B's proven 6,600. So NO single island
here is larger than coupon B, because warping scales with one connected island, not with the bounding box.
(Cooling was suspected and cleared: the stock PLA preset has printed reliably on this machine for a long time,
coupons A and B included. If a large part warps later, roster A17's three-layer fan-off is the first lever.)

  d1  the CRADLE GATE: everything that blocks the eight-hour print. Two small plates, one carrying the hole
      ladders and the horizontal round-vs-teardrop pairs, the other the Ø8 sockets opening UP and on the BED
      face, plus the loose peg on a sacrificial foot.
  d2  the MECHANISMS, needed later in the gated order: the bayonet boss with three under-size stubs, the Ø36
      hub with three ring bores, and coupon C's ratchet pair.

Everything prints flat, no supports. Qty: 1 each.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_disk
from mathutils import Matrix  # type: ignore

PRINT_ROT = L.ROT_NONE
PT = 4.0                      # plate thickness
TILE = (110.0, 55.0)          # every plate is at or under coupon B's proven footprint
LADDER_DX = 10.0

PINLOCK   = [1.6, 1.7, 1.8, 1.9]     # nape pin-lock for the 16 ga nail (1.59): nominal 1.7 snug / 1.8 clear (v2, 2026-09-20)
UPIN      = [1.8, 1.9]               # U-pin pairs: two holes one rack pitch apart under a merged 9 x 5 x 1 slot
PLUNGER_D = 3.2                      # a printed pin, standing on a foot: does printed slide in printed 3.4?
M3_TAP    = [2.5, 2.7, 2.9]
M3_CLEAR  = [3.4, 3.6, 3.8]
M4_CLEAR  = [4.4, 4.6, 4.8]
PIN_SOCK  = [4.1, 4.3, 4.5, 4.7]     # sensor-bar pins: blind, so they sit in a raised pad
HORIZ     = [(2.7, False), (2.7, True), (2.9, False), (2.9, True), (3.1, False), (3.1, True), (3.4, False), (3.4, True)]   # 12 ga tenon nail (2.68) slip; 3.4 = the plunger's keeper
SOCK_UP   = [8.3, 8.5, 8.7]
SOCK_BED  = [8.3, 8.5, 8.7, 8.9]
LUG_STEPS = [0.0, 0.3, 0.6]          # taken off each stub's lug width AND radial reach
RING_STEPS = [36.3, 36.7, 37.1]      # ring bores tried on the Ø36.0 hub

D1_NOTES = ["print flat, no supports, 8 mm brim; every ladder runs SMALL to LARGE, left to right. v2 (2026-09-20): the pin ladders are sized to the nails in the box, 12 ga (2.68) and 16 ga (1.59)",
            "pin-lock row (top left, 1.6 / 1.7 / 1.8 / 1.9): the 16 ga nail should press into 1.7 and drop through 1.8. Right of the M4 row: two U-pin pairs (1.8, 1.9): bend a 16 ga nail into a U with legs one rack pitch (3.9 mm) apart, drop it in, pull it out",
            "horizontal row (2.7 / 2.9 / 3.1 / 3.4, each round then teardrop): the 12 ga nail should slide through 3.1; note where the round binds and the teardrop passes. The printed Ø3.2 pin (loose, next to the peg) must slide in the 3.4 holes here and in the vertical 3.4 of the M3 row",
            "second plate, between the socket rows: a strap-slot pair 12 mm apart with chamfered edges. If you have 12 mm webbing, thread it through both",
            "ladders: find the FIRST size that takes its gauge cleanly. The step above nominal is what the slicer owes us, and HALF of it is the xy_hole_compensation value (that setting is a radial offset)",
            "horizontal row: 3.4 and 3.6, each round then teardrop. If the teardrop passes where the round binds, teardrops are doing their job",
            "the second plate's Ø8 sockets: three open UPWARD, four open on the BED face (turn it over). The bed-face row is the cradle's own condition, so find the first that takes the peg WITHOUT force",
            "the peg prints vertical on a sacrificial foot: snap or cut the foot off before testing"]
D2_NOTES = ["print flat, no supports, 8 mm brim",
            "bayonet: the three stubs have lugs 0.0 / 0.3 / 0.6 mm under size. CLOCK the lugs to the two slots in the boss mouth, drop straight in, then turn about 107 deg to the stop, tightening over the last third",
            "rings: bores 36.3 / 36.7 / 37.1 on the Ø36.0 hub; the right one turns freely with no rock",
            "ratchet: flip the loose Ø44 disc onto the spigot, press down and turn. It must click one way and lock the other, else flip NAPE_RATCHET_DIR in canon.py. The disc is oversize on purpose, for grip; only its tooth ring is under test"]


def _tile(name, cx, cy):
    return L.add_box(name, (cx, cy, PT / 2.0), (TILE[0], TILE[1], PT))


def _ladder(plate, cx, cy, dias, through=True):
    for i, d in enumerate(dias):
        x = cx + i * LADDER_DX
        if through:
            L.cut(plate, L.add_cyl(f"lad{cx:.0f}_{cy:.0f}_{i}", (x, cy, PT / 2.0), d / 2.0, PT + 2.0, axis="Z", verts=32))
        else:   # blind from the top of a raised pad: 6 deep, as the sensor bar's sockets are
            L.cut(plate, L.add_cyl(f"blind{cx:.0f}_{i}", (x, cy, PT + 8.0 - 3.0 + 0.5), d / 2.0, 6.0, axis="Z", verts=32))


def make_d1():
    """Plate 1: hole ladders, U-pin pairs, horizontal pairs.  Plate 2: the Ø8 socket rows and a strap-slot pair.  Loose: the peg, a plunger pin."""
    a = _tile("fit_coupon_d1", 0.0, 0.0)
    _ladder(a, -46.0, 16.0, PINLOCK)
    _ladder(a,  -2.0, 16.0, M3_TAP)
    _ladder(a,  30.0, 16.0, M3_CLEAR)
    _ladder(a, -46.0,  0.0, M4_CLEAR)
    # the sensor-bar sockets are BLIND, so they need material under them: a raised pad
    L.union(a, L.add_box("padsock", (-1.0, 0.0, PT + 4.0 - 0.5), (46.0, 14.0, 8.0 + 1.0)))
    _ladder(a, -16.0, 0.0, PIN_SOCK, through=False)
    # U-pin pairs: two vertical holes one rack pitch apart, the two counterbores merged into one slot for the U's bridge
    pitch = math.pi * C.GEAR_MODULE
    sl, sw_, sd = C.NAPE_PINLOCK_PIN["slot"]
    for k, d in enumerate(UPIN):
        cx = 32.0 + k * 13.0
        L.cut(a, L.add_box(f"uslot{k}", (cx + pitch / 2.0, 0.0, PT - sd / 2.0 + 0.5), (sl, sw_, sd + 1.0)))
        for j in (0, 1):
            L.cut(a, L.add_cyl(f"upin{k}{j}", (cx + j * pitch, 0.0, PT / 2.0), d / 2.0, PT + 2.0, axis="Z", verts=20))
    # horizontal holes through a standing block, round vs teardrop
    L.union(a, L.add_box("hblock", (0.0, -16.0, PT + 9.0 - 0.5), (100.0, 14.0, 18.0 + 1.0)))
    for i, (d, td) in enumerate(HORIZ):
        x = -42.0 + i * 12.0
        if td:
            L.cut(a, L.add_teardrop(f"ht{i}", (x, -16.0, PT + 9.0), d / 2.0, 20.0, (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), verts=20))
        else:
            L.cut(a, L.add_cyl(f"hr{i}", (x, -16.0, PT + 9.0), d / 2.0, 20.0, axis="Y", verts=20))

    b = _tile("sockets", 0.0, -80.0)
    for i, d in enumerate(SOCK_UP):
        cx = -36.0 + i * 24.0
        L.union(b, L.add_box(f"subox{i}", (cx, -62.0, PT + 9.0 - 0.5), (16.0, 16.0, 18.0 + 1.0)))
        L.cut(b, L.add_cyl(f"sup{i}", (cx, -62.0, PT + 18.0 - C.CYL_DEPTH / 2.0 + 0.5), d / 2.0, C.CYL_DEPTH + 1.0, axis="Z", verts=48))
    for i, d in enumerate(SOCK_BED):
        cx = -36.0 + i * 24.0
        L.union(b, L.add_box(f"sbbox{i}", (cx, -98.0, PT + 6.0 - 0.5), (16.0, 16.0, 12.0 + 1.0)))
        L.cut(b, L.add_cyl(f"sbed{i}", (cx, -98.0, C.CYL_DEPTH / 2.0 - 1.0), d / 2.0, C.CYL_DEPTH, axis="Z", verts=48))
    # a strap-slot pair between the socket rows: 14 x 4 slots, STRAP_SLOT_PITCH apart, every edge chamfered
    sh, sw = C.STRAP_SLOT
    for k in (-1, +1):
        Ms = L.frame((40.0, -80.0 + k * C.STRAP_SLOT_PITCH / 2.0, PT / 2.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))   # local X = width (along y), local Z = height (along x)
        L.cut(b, L.add_box_local(f"strap{k}", Ms, (0.0, 0.0, 0.0), (sw + 0.3, PT + 2.0, sh)))
        L.slot_chamfer(b, Ms, sw + 0.3, sh, PT, C.STRAP_SLOT_CHAMFER)
    L.union(a, b)

    peg = L.add_cyl("pegfoot", (0.0, -130.0, 0.75), 10.0, 1.5, axis="Z", verts=48)
    L.union(peg, L.add_cyl("peg", (0.0, -130.0, 1.5 + C.CYL_PEG_LEN / 2.0), C.CYL_PEG_D / 2.0, C.CYL_PEG_LEN, axis="Z", verts=48))
    L.cut(peg, L.add_cyl("pegpin", (0.0, -130.0, 1.5 + C.CYL_PEG_LEN - C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2.0, C.CYL_PEG_D + 6.0, axis="X", verts=24))
    L.union(a, peg)
    # the plunger pin: Ø3.2 x 20, standing on a Ø6 foot (a round shank for the fit test; the real plunger's orientation is a Phase 3 question)
    pin = L.add_cyl("pinfoot", (22.0, -130.0, 0.75), 3.0, 1.5, axis="Z", verts=32)
    L.union(pin, L.add_cyl("pin", (22.0, -130.0, 1.5 + 10.0), PLUNGER_D / 2.0, 20.0, axis="Z", verts=32))
    L.union(a, pin)
    return a


def make_d2():
    """Plate: bayonet boss, Ø36 hub, ratchet ring.  Loose: three stubs, three rings, the dial."""
    # two tiles side by side: the boss + hub need 34 and 36 of diameter, and the ratchet ring's teeth reach
    # 14.5 from its centre. All three on one 110-wide tile put the ring's teeth 3.5 mm PAST the plate edge,
    # which left 12 non-manifold edges (2026-09-17). A feature must sit wholly inside its tile.
    a = _tile("fit_coupon_d2", -60.0, 0.0)
    Mb = Matrix.Translation((-86.0, 0.0, 0.0))    # local 0 = the slab's BED face: the stub enters from underneath
    L.union(a, build_disk.bayonet_boss(Mb, C.DISK_PLATE_T - 0.1, h=14.5))
    build_disk.bayonet_cuts(a, Mb, mouth=False, z_below=1.0, **build_disk.LEGACY)
    L.union(a, L.add_cyl("hub", (-38.0, 0.0, PT + 4.0 - 0.5), C.NEXUS_SPOOL[2] / 2.0, 8.0 + 1.0, axis="Z", verts=96))
    b = _tile("ratchet_tile", 60.0, 0.0)
    L.union(b, L.face_ratchet_ring("ring_body", (60.0, 0.0, PT), (0, 0, 1), C.NAPE_RATCHET_R[0], C.NAPE_RATCHET_R[1],
                                   C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR))
    L.union(b, L.add_cyl("spigot", (60.0, 0.0, PT + 3.5), 4.0, 9.0, axis="Z", verts=48))
    L.union(a, b)

    lw, lr, lh = C.STALK_LUG[0], 3.0, C.STALK_LUG[2]   # pinned: the 3.0 reach this coupon printed with (canon is 2.6 since coupon H)
    n0, n1 = C.STALK_LUG_N
    for i, step in enumerate(LUG_STEPS):
        sx, sy = -60.0 + i * 36.0, -50.0
        stub = L.add_cyl(f"sbase{i}", (sx, sy, 1.5), 15.0, 3.0, axis="Z", verts=60)
        L.union(stub, L.add_cyl(f"sstalk{i}", (sx, sy, (2.5 + 3.0 + C.STALK_LEN) / 2.0), C.STALK_D / 2.0, 3.0 + C.STALK_LEN - 2.5, axis="Z", verts=72))
        for s in (+1, -1):
            L.union(stub, L.add_box(f"slug{i}_{s}", (sx + s * (C.STALK_D / 2.0 + (lr - step) / 2.0 - 0.15), sy, 3.0 + (n0 + n1) / 2.0),
                                    (lr - step + 0.3, lw - step, n1 - n0)))
        L.union(a, stub)

    od, _, t = C.NEXUS_RING
    for i, bore in enumerate(RING_STEPS):
        rx = -70.0 + i * 48.0
        L.union(a, L.revolve(f"ring{i}", [(bore / 2.0, 0.0), (od / 2.0, 0.0), (od / 2.0, t), (bore / 2.0, t)],
                             axis="Z", center=(rx, -95.0, 0.0), segments=100))

    # The dial is a PLAIN Ø44 disc here, deliberately bigger than the real Ø34 and with no grip flats.
    # Eight flat cuts emptied this dial silently in this scene (2026-09-17) while the identical construction
    # survives in coupon C, so the grip is not worth another boolean. Only the TOOTH RING is under test, and
    # its geometry is untouched; the extra diameter just gives more to hold while turning it.
    dx, dy = 74.0, -95.0
    dial = L.revolve("dial", [(4.25, 0.0), (22.0, 0.0), (22.0, C.NAPE_DIAL_T), (4.25, C.NAPE_DIAL_T)],
                     axis="Z", center=(dx, dy, 0.0), segments=96)
    L.union(dial, L.face_ratchet_ring("ring_dial", (dx, dy, C.NAPE_DIAL_T), (0, 0, 1), C.NAPE_RATCHET_R[0], C.NAPE_RATCHET_R[1],
                                      C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR))
    L.union(a, dial)
    return a


PARTS = {"fit_coupon_d1": (make_d1, PRINT_ROT, D1_NOTES),
         "fit_coupon_d2": (make_d2, PRINT_ROT, D2_NOTES)}


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
