#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon_f.py -- Track P fit coupon F: the bayonet CAM, corrected, on a ladder.

Coupon E (2026-09-19) proved the canon cam is upside down. BAYONET_CAM = (4.5, 3.8) puts the groove floor 0.34 mm
INTO the lug's path 20 deg past the notch and 0.2 mm clear of it at the stop, so the joint jams where it must be
free and rattles where it must be tight, and no stub could turn. The groove ceiling (7.8) never touches the lug
top (7.0) because the flange stops the plate 0.8 mm before it could, so it is gone: the groove is open to the sky
and the boss wall stops just above the lugs. No cap, no lock notch. This coupon tests the turn and nothing else.

  bosses  four, on Ø42 collars, pips on the rim count the ladder step. The floor RISES from 3.5 at the entry notch
          to the stop height, which is the ladder: 3.9 / 4.0 / 4.1 / 4.2 against a lug bottom at 4.0, i.e. 0.1
          loose, dead on, 0.1 preload, 0.2 preload. The tight end is the one that matters; it is measured here.
  stubs   two, full-size lugs, hollow. A (one pip): the lug's outer bottom edge chamfered 45 deg x 1.2, so the
          shelf under it is 1.8 mm instead of 3.0. B: plain, as the nexus stalk is drawn today. The nexus prints
          stalk-up with the same 3 mm shelf under each lug, so whatever sags here sags there.

Test: for each boss, push a stub up from underneath, lugs on the slots, until its flange meets the collar. Turn to
the stop. Report per boss and per stub: free / effort / jams, and at the stop: rattles / snug / tight.

Print flat, no supports. Qty: 1.
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
PT = 3.2                            # collar thickness: below every floor on the ladder, so no cut lands on its top face
COLLAR_D = 42.0
WALL_H = 7.5                        # the boss wall: lug top 7.0 + 0.5, no ceiling
ENTRY = 3.5                         # floor at the notch: 0.5 under the lug bottom, drops in free
STOP_LADDER = [3.9, 4.0, 4.1, 4.2]  # floor at the stop
CHAMFER = 1.2                       # stub A: 45 deg off the lug's outer bottom edge
STUB_BASE_D, STUB_BASE_T = 26.0, 2.5
PITCH = 26.0
STUB_Y = -(PITCH + COLLAR_D / 2.0 + 8.0 + STUB_BASE_D / 2.0)

NOTES = ["print flat, no supports, 8 mm brim",
         f"four bosses: floor rises from {ENTRY} at the notch to the stop height, pips on the rim: 1 = {STOP_LADDER[0]}, 2 = {STOP_LADDER[1]}, 3 = {STOP_LADDER[2]}, 4 = {STOP_LADDER[3]} (lug bottom is 4.0)",
         "stub A (one pip on its flange) has the lug's outer bottom edge chamfered; stub B is plain, as the nexus is drawn today",
         "to test: push a stub UP through a boss from the collar's underside, lugs on the two slots, until the flange meets the collar. Turn about 107 deg to the stop",
         "report for every boss x stub: turns free / with effort / jams, and at the stop: rattles / snug / tight. The highest floor that still turns is the answer"]


def _pips(host, cx, cy, n, r, z_top, a0=270.0, rp=1.2):
    for k in range(n):
        a = math.radians(a0 - 15.0 * (k - (n - 1) / 2.0))
        L.union(host, L.add_cyl(f"pip{n}{k}", (cx + r * math.cos(a), cy + r * math.sin(a), z_top - 0.25), rp, 1.5, axis="Z", verts=16))


def _boss(host, cx, cy, stop):
    M = Matrix.Translation((cx, cy, 0.0))          # local 0 = the collar's bed face, as the disk plate prints
    L.union(host, build_disk.bayonet_boss(M, C.DISK_PLATE_T - 0.1, h=WALL_H))
    build_disk.bayonet_cuts(host, M, mouth=False, z_below=1.0, cam=(ENTRY, stop), open_top=True, lock=False, bore_clear=0.3, notch_clear=0.3, reverse_block=False, lug_reach=3.0)


def _stub(name, sx, sy, chamfer):
    lw, lr, lh = C.STALK_LUG[0], 3.0, C.STALK_LUG[2]   # pinned: the 3.0 reach this coupon printed with (canon is 2.6 since coupon H)
    n0, n1 = C.STALK_LUG_N
    stub = L.add_cyl(name, (sx, sy, STUB_BASE_T / 2.0), STUB_BASE_D / 2.0, STUB_BASE_T, axis="Z", verts=60)
    top = STUB_BASE_T + C.STALK_LEN
    L.union(stub, L.add_cyl(name + "_stalk", (sx, sy, (STUB_BASE_T + top) / 2.0), C.STALK_D / 2.0, top - STUB_BASE_T, axis="Z", verts=72))
    r_in, r_out = C.STALK_D / 2.0 - 0.3, C.STALK_D / 2.0 + lr
    z0, z1 = STUB_BASE_T + n0, STUB_BASE_T + n1
    if chamfer:
        # the lug as a revolved profile with the outer bottom corner cut at 45 deg, then trimmed to its tangential width.
        # Inner radius deep inside the stalk (8.5, as the boss revolve does) and 60 segments turned 2.3 deg: at 9.7 with the
        # stalk's own 72 angles, the union left slivers where the trim planes crossed the shared vertex lines.
        prof = [(8.5, z0), (r_out - CHAMFER, z0), (r_out, z0 + CHAMFER), (r_out, z1), (8.5, z1)]
        ring = L.revolve(name + "_lugring", prof, axis="Z", center=(sx, sy, 0.0), segments=60)
        ring.matrix_world = Matrix.Translation((sx, sy, 0.0)) @ Matrix.Rotation(math.radians(2.3), 4, "Z") @ Matrix.Translation((-sx, -sy, 0.0)) @ ring.matrix_world
        L.apply_transform(ring)
        for s2 in (+1, -1):
            L.cut(ring, L.add_box(name + f"_trim{s2}", (sx, sy + s2 * (lw / 2.0 + 50.0), (z0 + z1) / 2.0), (60.0, 100.0, 20.0)))
        L.union(stub, ring)
    else:
        for s2 in (+1, -1):
            L.union(stub, L.add_box(name + f"_lug{s2}", (sx + s2 * (r_in + r_out) / 2.0, sy, (z0 + z1) / 2.0), (r_out - r_in, lw, z1 - z0)))
    L.cut(stub, L.add_cyl(name + "_bore", (sx, sy, top - C.STALK_LEN / 2.0 + 1.0), C.STALK_BORE / 2.0, C.STALK_LEN + 2.0, axis="Z", verts=48))
    return stub


def make():
    host = None
    for i, stop in enumerate(STOP_LADDER):
        cx, cy = (-PITCH if i % 2 == 0 else PITCH), (PITCH if i < 2 else -PITCH)
        collar = L.add_cyl("fit_coupon_f" if host is None else f"collar{i}", (cx, cy, PT / 2.0), COLLAR_D / 2.0, PT, axis="Z", verts=96)
        _boss(collar, cx, cy, stop)
        _pips(collar, cx, cy, i + 1, COLLAR_D / 2.0 - 2.3, PT)
        if host is None:
            host = collar
        else:
            L.union(host, collar)
    a = _stub("stubA", -16.0, STUB_Y, chamfer=True)
    _pips(a, -16.0, STUB_Y, 1, 11.5, STUB_BASE_T, rp=0.9)     # clear of the stalk (10) and the flange edge (13): a pip tangent to the stalk left a sliver
    L.union(host, a)
    L.union(host, _stub("stubB", 16.0, STUB_Y, chamfer=False))
    return host


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
