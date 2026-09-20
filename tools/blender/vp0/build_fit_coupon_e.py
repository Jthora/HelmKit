#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon_e.py -- Track P fit coupon E: the SPLIT bayonet boss.

The one-piece boss cannot print. Its groove is retained by a 3.3 mm wide annular roof hanging in mid air,
which came out badly on coupon A and nearly wrecked the plate. This coupon tests the fix: cut the boss
horizontally at the groove ceiling and make the roof a separate ring that is bonded on afterwards.

  base   the tile carrying the boss wall up to the groove ceiling. The groove is open upward, so every
         surface faces the sky and there is no overhang anywhere. The two entry slots run from the BED
         face up past the groove floor, because the lug has to climb through the wall from underneath.
  cap    the piece that was cut off: a ring, bore 20.6, outside 34, carrying the groove ceiling and the
         lock notch. Prints flat on the bed, no overhang.
  stubs  three, with lugs 0.0 / 0.3 / 0.6 mm under size, hollow as the real stalk is.

Both halves are produced by building the EXISTING boss geometry and slicing it with a plane at the groove
ceiling, so the groove, the cam ramp, the stop bumps and the lock notch are bit-for-bit what the disk has.
Nothing is re-derived and nothing can drift.

Assembly needs no keying: the stalk itself centres the cap, since a 20 mm stalk in a 20.6 bore leaves three
tenths. Drop the stalk in through the slots, turn it to the stop, slide the cap down the stalk onto the
land and bond it. The land is about 330 mm2, which is far more epoxy than the joint can ever need.

Print flat, no supports. Qty: 1.
"""
from __future__ import annotations
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
PT = 4.0
BASE_D = 46.0                      # just a collar round the Ø34 boss: the old 100 x 60 tile was ballast
STUB_BASE_D = 26.0                 # a handle, nothing more
STUB_BASE_T = 2.5
SPLIT = C.BAYONET_GROOVE[2]        # the groove ceiling: 7.8 from the head face
BOSS_X, BOSS_Y = 0.0, 0.0
CAP_X, CAP_Y = 0.0, -50.0
LUG_STEPS = [0.0, 0.3, 0.6]

NOTES = ["print flat, no supports, 8 mm brim",
         f"the boss is split at the groove ceiling ({SPLIT} from the face). The BASE has the groove open upward and no overhang; the CAP is the ring that was cut off",
         "to test: push a stub UP through the bore from the tile's underside with its two lugs lined up on the two slots, until its flange meets the tile. Then turn it about 107 deg to the stop, tightening over the last third",
         "then slide the cap down over the stalk onto the land and check it sits flat and concentric. The stalk centres it; no keying is needed. In the real part that joint is epoxied",
         "the three stubs have lugs 0.0 / 0.3 / 0.6 mm under size: report which turns"]


def _base_boss(host, M):
    """The standard boss and cuts on `host`, then everything above the groove ceiling removed."""
    L.union(host, build_disk.bayonet_boss(M, C.DISK_PLATE_T - 0.1, h=14.5))
    build_disk.bayonet_cuts(host, M, mouth=False, z_below=1.0, **build_disk.LEGACY)
    z = M.translation.z + SPLIT
    L.cut(host, L.add_box("chop_hi", (M.translation.x, M.translation.y, z + 200.0), (400.0, 400.0, 400.0)))
    return host


def _cap_boss(M):
    """The same boss, with everything BELOW the groove ceiling removed: the ring that was cut off."""
    cap = build_disk.bayonet_boss(M, C.DISK_PLATE_T - 0.1, h=14.5)
    build_disk.bayonet_cuts(cap, M, mouth=False, z_below=1.0, **build_disk.LEGACY)
    z = M.translation.z + SPLIT
    L.cut(cap, L.add_box("chop_lo", (M.translation.x, M.translation.y, z - 200.0), (400.0, 400.0, 400.0)))
    return cap


def make():
    base = L.add_cyl("fit_coupon_e", (BOSS_X, BOSS_Y, PT / 2.0), BASE_D / 2.0, PT, axis="Z", verts=96)
    # local 0 = the disc's BED face, exactly as the disk back plate prints: the stalk enters from underneath
    _base_boss(base, Matrix.Translation((BOSS_X, BOSS_Y, 0.0)))

    # the cap: the same boss sliced the other way, then dropped to the bed so it prints as a flat ring
    cap = _cap_boss(Matrix.Translation((CAP_X, CAP_Y, 0.0)))
    cap.location = (0.0, 0.0, -SPLIT)
    L.apply_transform(cap)
    L.union(base, cap)

    lw, lr, lh = C.STALK_LUG[0], 3.0, C.STALK_LUG[2]   # pinned: the 3.0 reach this coupon printed with (canon is 2.6 since coupon H)
    n0, n1 = C.STALK_LUG_N
    for i, step in enumerate(LUG_STEPS):
        sx, sy = -30.0 + i * 30.0, -95.0
        stub = L.add_cyl(f"sbase{i}", (sx, sy, STUB_BASE_T / 2.0), STUB_BASE_D / 2.0, STUB_BASE_T, axis="Z", verts=60)
        top = STUB_BASE_T + C.STALK_LEN
        L.union(stub, L.add_cyl(f"sstalk{i}", (sx, sy, (STUB_BASE_T + top) / 2.0), C.STALK_D / 2.0,
                                top - STUB_BASE_T, axis="Z", verts=72))
        for s2 in (+1, -1):
            L.union(stub, L.add_box(f"slug{i}_{s2}", (sx + s2 * (C.STALK_D / 2.0 + (lr - step) / 2.0 - 0.15), sy,
                                                      STUB_BASE_T + (n0 + n1) / 2.0), (lr - step + 0.3, lw - step, n1 - n0)))
        # hollow, as the real stalk is: a Ø8.2 bore for the knob shaft. Lighter and more representative.
        L.cut(stub, L.add_cyl(f"sbore{i}", (sx, sy, top - C.STALK_LEN / 2.0 + 1.0), C.STALK_BORE / 2.0,
                              C.STALK_LEN + 2.0, axis="Z", verts=48))
        L.union(base, stub)
    return base


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
