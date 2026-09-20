#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon_h.py -- Track P fit coupon H: the bayonet that can only turn the right way, on a follower that can climb.

Coupon G (2026-09-20) turned, and what it measured was four faults at once:
  1. From each notch the lug could turn the WRONG way, 29 deg across the flat tail of the other sector's entry floor
     to the back of its stop bump, and stop there as if locked. Jordan's "short side". A block now fills that tail.
  2. The Ø20 stalk in a bore drawn at 20.6 (prints ~20.25) is a friction fit: it held the flange up and read as
     "snug" with the lug floating 0.8 above the floor, and turned stiff or not at all from collar to collar. Bore
     clearance 0.5 on radius here (Ø21.0).
  3. The full-reach lug (3.0) would not enter some slots at all: 0.6 of radial slot clearance prints as ~0.2.
     Slot clearance 1.0 here; both stubs reach 2.6.
  4. The ramp never climbed, and the reason was the fifth fault, not droop: the stubs' pips stood on the flange's
     TOP face, the face that seats on the collar, 0.5 mm proud, just outside the relief cone. Every stub sat 0.5
     off the collar and its lug at 3.5 instead of 4.0, below every riser. Jordan caught it. The marks are now on the
     stalk's free end, where nothing touches them, and this coupon's ladder assumes a lug back near 4.0.
  5. Even so, at 0.2 mm layers the cam is a staircase and a square-edged lug can catch a riser at its own height.
     Stub A has 45-deg LEAD-IN chamfers on both tangential bottom edges so it rides up instead of hitting, and a
     deeper outer chamfer (1.4) leaves a 1.2 mm shelf that droops less. Stub B has the outer chamfer only: the control.

  bosses  three, every bearing face on a 0.2 layer: entry floor 3.2, stop floors 3.2 (FLAT, the control: no cam at
          all, so if this turns and the others do not the ramp is the problem) / 3.6 / 3.8. Pips count the step.
          Reverse block behind each slot, open groove, wall 7.6, elephant-foot relief on.
  stubs   two, hollow, reach 2.6, flange 2.4, lug 6.4..9.4, pips on the stalk's end. A (one pip): lead-in
          chamfers. B (two pips): none. The flange's top face carries NOTHING.

Turn direction: looking down on a collar with the pips toward you, the lug leaves the slot ANTICLOCKWISE up the
ramp; the block stops the other way within a few degrees. Print flat, no supports. Qty: 1.
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
STOP_LADDER = [3.2, 3.6, 3.8]       # 16 (FLAT control) / 18 / 19 layers: 0.8 / 0.4 / 0.2 under a lug at 4.0
CHAMFER = 1.4                       # outer bottom edge: leaves a 1.2 mm shelf on a 2.6 reach
LEAD = 0.6                          # stub A only: 45-deg lead-in on both tangential bottom edges
BORE_CLEAR, NOTCH_CLEAR = 0.5, 0.7        # slot to r 13.7 (pinned as printed: 0.7 beyond the 3.0 canon reach of the day; 1.1 beyond the 2.6 lug)
STUB_BASE_D, STUB_BASE_T = 26.0, 2.4    # 12 layers, so the lug band lands at 6.4 .. 9.4 (32 .. 47 layers)
STUB_REACH = [2.6, 2.6]             # both: canon 3.0 would not enter
STUB_LEAD = [True, False]           # A has the lead-in chamfers, B is the control
PITCH = 46.0
STUB_Y = -(COLLAR_D / 2.0 + 8.0 + STUB_BASE_D / 2.0)

for _z in (PT, WALL_H, ENTRY, *STOP_LADDER, STUB_BASE_T, STUB_BASE_T + C.STALK_LUG_N[0], STUB_BASE_T + C.STALK_LUG_N[1]):
    assert abs(_z / LAYER - round(_z / LAYER)) < 1e-6, f"{_z} is not on a {LAYER} layer boundary"

NOTES = ["print flat, no supports, 8 mm brim, 0.20 mm layers (every bearing face is drawn on a layer boundary for THIS height)",
         "TURN DIRECTION: pips toward you, looking down, the lug leaves the slot ANTICLOCKWISE up the ramp; a block stops the other way within a few degrees (coupon G's 'short side' was the wrong way)",
         f"three bosses, pips on the rim: 1 = FLAT floor {STOP_LADDER[0]} (no cam: the control), 2 = rises to {STOP_LADDER[1]}, 3 = rises to {STOP_LADDER[2]}. Bore Ø21.0, slot clearance 1.0",
         "stub A (one pip on the stalk's end): lead-in chamfers on the lug's leading edges, so it climbs the ramp's layer steps; stub B (two pips): none, the control. Both reach 2.6. The flange face is clean: nothing stands it off the collar",
         "to test: push a stub UP through a boss from the collar's underside, lugs on the two slots, until the flange meets the collar. Turn about 107 deg to the stop",
         "report for every boss x stub: turns free / with effort / jams, and at the stop: rattles / snug / tight. The tightest floor that turns freely is the number; the play is for a washer, not a dimension"]


def _pips(host, cx, cy, n, r, z_top, a0=270.0, rp=1.2):
    for k in range(n):
        a = math.radians(a0 - 15.0 * (k - (n - 1) / 2.0))
        L.union(host, L.add_cyl(f"pip{n}{k}", (cx + r * math.cos(a), cy + r * math.sin(a), z_top - 0.25), rp, 1.5, axis="Z", verts=16))


def _boss(host, cx, cy, stop):
    M = Matrix.Translation((cx, cy, 0.0))          # local 0 = the collar's bed face, as the disk plate prints
    L.union(host, build_disk.bayonet_boss(M, C.DISK_PLATE_T - 0.1, h=WALL_H))
    build_disk.bayonet_cuts(host, M, mouth=True, z_below=1.0, cam=(ENTRY, stop), open_top=True, lock=False,
                            bore_clear=BORE_CLEAR, notch_clear=NOTCH_CLEAR, reverse_block=True, lug_reach=3.0)


def _stub(name, sx, sy, reach, lead):
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
    if lead:
        # 45-deg lead-in on the lug's two tangential bottom edges: a diamond prism along the lug's radial run, its centre on the
        # edge, takes a triangle of leg LEAD off the corner. Starts at r 9.6 so it clears the stalk's surface (9.54 at y = 3).
        for s2 in (+1, -1):
            for sgn in (+1, -1):
                xc = sx + s2 * (9.6 + r_out + 0.5) / 2.0
                Mlead = Matrix.Translation((xc, sy + sgn * lw / 2.0, z0)) @ Matrix.Rotation(math.radians(45.0), 4, "X")
                L.cut(stub, L.add_box_local(name + f"_lead{s2}{sgn}", Mlead, (0.0, 0.0, 0.0), (r_out + 0.5 - 9.6, LEAD * math.sqrt(2.0), LEAD * math.sqrt(2.0))))
    L.cut(stub, L.add_cyl(name + "_bore", (sx, sy, top - C.STALK_LEN / 2.0 + 1.0), C.STALK_BORE / 2.0, C.STALK_LEN + 2.0, axis="Z", verts=48))
    return stub


def make():
    host = None
    for i, stop in enumerate(STOP_LADDER):
        cx, cy = (i - 1) * PITCH, 0.0
        collar = L.add_cyl("fit_coupon_h" if host is None else f"collar{i}", (cx, cy, PT / 2.0), COLLAR_D / 2.0, PT, axis="Z", verts=96)
        _boss(collar, cx, cy, stop)
        _pips(collar, cx, cy, i + 1, COLLAR_D / 2.0 - 2.3, PT)
        if host is None:
            host = collar
        else:
            L.union(host, collar)
    for i, reach in enumerate(STUB_REACH):
        sx = -16.0 + 32.0 * i
        stub = _stub(f"stub{i}", sx, STUB_Y, reach, STUB_LEAD[i])
        # marks on the stalk's FREE END, never on the flange's top face: that face seats on the collar, and on coupons F and G a
        # 0.5 mm pip there stood every stub 0.5 off the collar and put its lug at 3.5 instead of 4.0 (Jordan caught it, 2026-09-20)
        _pips(stub, sx, STUB_Y, i + 1, 7.0, STUB_BASE_T + C.STALK_LEN, rp=0.9)
        L.union(host, stub)
    return host


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
