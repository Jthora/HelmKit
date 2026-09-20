#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon_g.py -- Track P fit coupon G: the bayonet with PRINTER-SIZED clearances, every bearing face on a layer.

Coupon F (2026-09-20) failed on every combination: the lugs bound within 15 deg of leaving the notch. Two causes,
both mine. (1) Every bearing surface on F sat exactly on a slice plane (floors at 3.9 and 4.1, the flange top at
2.5, the lug bottom at 6.5): at 0.2 mm layers the slicer samples each layer at its mid-height, so each of those
landed a tenth high or low at random, and a ladder in 0.1 steps was a ladder the printer cannot resolve. (2) The
lug's underside is a 3 mm shelf that sags 0.1 to 0.3, so the printed lug bottom sat around 3.6 to 3.8 above the
flange, not 4.0, and met the floor at once. Clearances of a tenth on a process that scatters by a tenth or two.

This coupon:
  every horizontal bearing face is a multiple of 0.2 from the bed: collar top 3.0, entry floor 3.2, stop floors
  3.4 / 3.6 / 3.8, wall top 7.6, stub flange 2.4, lug bottom 6.4, lug top 9.4. Deterministic.
  bosses  three, floor rising from 3.2 at the notch to 3.4 / 3.6 / 3.8 at the stop: 0.6 / 0.4 / 0.2 of clearance
          under a lug at 4.0. Pips count the step. Open groove, no cap, no lock notch. The elephant-foot relief
          cone at the bore (as the real plate has) is ON, so the stub's flange seats on the collar and not on the
          first layer's squash.
  stubs   two, hollow, both with the lug's outer bottom edge chamfered 45 x 1.0. A (one pip): lug reach 2.6, so
          the groove wall clears it by 1.0 not 0.6. B (two pips): canon reach 3.0.

Preload is NOT a printed dimension any more. The joint runs 0.2 to 0.6 loose by design and the play is taken up
by a wave washer or an O-ring between the nexus flange and the disk plate; that is the next canon change if G turns.

Test: push a stub up from underneath, lugs on the slots, flange against the collar. Turn to the stop. Report per
boss and per stub: free / effort / jams; at the stop: rattles / snug / tight. The tightest floor that still turns
freely is the number.

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

LAYER = 0.2
PRINT_ROT = L.ROT_NONE
PT = 3.0                            # collar: 15 layers, and below every floor so no cut lands on its top face
COLLAR_D = 42.0
WALL_H = 7.6                        # 38 layers: lug top 7.0 + 0.6, no ceiling
ENTRY = 3.2                         # 16 layers: 0.8 under the lug on entry
STOP_LADDER = [3.4, 3.6, 3.8]       # 17 / 18 / 19 layers: 0.6 / 0.4 / 0.2 under a lug at 4.0
CHAMFER = 1.0
STUB_BASE_D, STUB_BASE_T = 26.0, 2.4    # 12 layers, so the lug band lands at 6.4 .. 9.4 (32 .. 47 layers)
STUB_REACH = [2.6, 3.0]             # A, B: radial reach of the lug (canon 3.0)
PITCH = 46.0
STUB_Y = -(COLLAR_D / 2.0 + 8.0 + STUB_BASE_D / 2.0)

for _z in (PT, WALL_H, ENTRY, *STOP_LADDER, STUB_BASE_T, STUB_BASE_T + C.STALK_LUG_N[0], STUB_BASE_T + C.STALK_LUG_N[1]):
    assert abs(_z / LAYER - round(_z / LAYER)) < 1e-6, f"{_z} is not on a {LAYER} layer boundary"

NOTES = ["print flat, no supports, 8 mm brim, 0.20 mm layers (every bearing face is drawn on a layer boundary for THIS height)",
         f"three bosses: floor rises from {ENTRY} at the notch to the stop height, pips on the rim: 1 = {STOP_LADDER[0]}, 2 = {STOP_LADDER[1]}, 3 = {STOP_LADDER[2]} (lug bottom is 4.0: clearance 0.6 / 0.4 / 0.2)",
         f"stub A (one pip): lug reach {STUB_REACH[0]}; stub B (two pips): canon reach {STUB_REACH[1]}. Both chamfered under the lug",
         "to test: push a stub UP through a boss from the collar's underside, lugs on the two slots, until the flange meets the collar. Turn about 107 deg to the stop",
         "report for every boss x stub: turns free / with effort / jams, and at the stop: rattles / snug / tight. The tightest floor that turns freely is the number; the play is for a washer, not a dimension"]


def _pips(host, cx, cy, n, r, z_top, a0=270.0, rp=1.2):
    for k in range(n):
        a = math.radians(a0 - 15.0 * (k - (n - 1) / 2.0))
        L.union(host, L.add_cyl(f"pip{n}{k}", (cx + r * math.cos(a), cy + r * math.sin(a), z_top - 0.25), rp, 1.5, axis="Z", verts=16))


def _boss(host, cx, cy, stop):
    M = Matrix.Translation((cx, cy, 0.0))          # local 0 = the collar's bed face, as the disk plate prints
    L.union(host, build_disk.bayonet_boss(M, C.DISK_PLATE_T - 0.1, h=WALL_H))
    build_disk.bayonet_cuts(host, M, mouth=True, z_below=1.0, cam=(ENTRY, stop), open_top=True, lock=False, bore_clear=0.3, notch_clear=0.3, reverse_block=False, lug_reach=3.0)


def _stub(name, sx, sy, reach):
    lw, lr, lh = C.STALK_LUG
    n0, n1 = C.STALK_LUG_N
    stub = L.add_cyl(name, (sx, sy, STUB_BASE_T / 2.0), STUB_BASE_D / 2.0, STUB_BASE_T, axis="Z", verts=60)
    top = STUB_BASE_T + C.STALK_LEN
    L.union(stub, L.add_cyl(name + "_stalk", (sx, sy, (STUB_BASE_T + top) / 2.0), C.STALK_D / 2.0, top - STUB_BASE_T, axis="Z", verts=72))
    r_out = C.STALK_D / 2.0 + reach
    z0, z1 = STUB_BASE_T + n0, STUB_BASE_T + n1
    # the lug as a revolved profile, outer bottom corner at 45 deg, inner radius deep inside the stalk, 60 segments turned
    # 2.3 deg (coupon F: a ring at 9.7 sharing the stalk's 72 angles left slivers on the trim planes)
    prof = [(8.5, z0), (r_out - CHAMFER, z0), (r_out, z0 + CHAMFER), (r_out, z1), (8.5, z1)]
    ring = L.revolve(name + "_lugring", prof, axis="Z", center=(sx, sy, 0.0), segments=60)
    ring.matrix_world = Matrix.Translation((sx, sy, 0.0)) @ Matrix.Rotation(math.radians(2.3), 4, "Z") @ Matrix.Translation((-sx, -sy, 0.0)) @ ring.matrix_world
    L.apply_transform(ring)
    for s2 in (+1, -1):
        L.cut(ring, L.add_box(name + f"_trim{s2}", (sx, sy + s2 * (lw / 2.0 + 50.0), (z0 + z1) / 2.0), (60.0, 100.0, 20.0)))
    L.union(stub, ring)
    L.cut(stub, L.add_cyl(name + "_bore", (sx, sy, top - C.STALK_LEN / 2.0 + 1.0), C.STALK_BORE / 2.0, C.STALK_LEN + 2.0, axis="Z", verts=48))
    return stub


def make():
    host = None
    for i, stop in enumerate(STOP_LADDER):
        cx, cy = (i - 1) * PITCH, 0.0
        collar = L.add_cyl("fit_coupon_g" if host is None else f"collar{i}", (cx, cy, PT / 2.0), COLLAR_D / 2.0, PT, axis="Z", verts=96)
        _boss(collar, cx, cy, stop)
        _pips(collar, cx, cy, i + 1, COLLAR_D / 2.0 - 2.3, PT)
        if host is None:
            host = collar
        else:
            L.union(host, collar)
    for i, reach in enumerate(STUB_REACH):
        sx = -16.0 + 32.0 * i
        stub = _stub(f"stub{i}", sx, STUB_Y, reach)
        _pips(stub, sx, STUB_Y, i + 1, 11.5, STUB_BASE_T, rp=0.9)
        L.union(host, stub)
    return host


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
