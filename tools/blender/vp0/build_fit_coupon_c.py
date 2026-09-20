#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon_c.py -- Track P fit coupon C: the nape ratchet, on its own.

Coupon A carries a ratchet ring and a loose disc, but on the printed plate the pair cannot actually be
engaged (bench result 2026-09-16), so the one-way click has never been tested. Coupon C is that test and
nothing else:

  base   a square plate (easy to hold still) carrying the nape BODY's ratchet ring and a centring spigot
         that stands in for the pinion the real dial turns on
  dial   a loose disc the size of the real one (NAPE_DIAL_D x NAPE_DIAL_T) with the matching tooth ring
         and a flatted rim for grip

Both tooth rings print facing UP, so neither is an overhang; the dial is flipped onto the spigot to use it.
The one number this coupon decides is NAPE_RATCHET_DIR. Print flat, no supports. Qty: 1.
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
from mathutils import Matrix  # type: ignore

PRINT_ROT = L.ROT_NONE

BASE = (56.0, 56.0, 4.0)      # square: held still in one hand while the other turns the dial
SPIGOT_D = 8.0                # centring post; the pinion's job in the real module
SPIGOT_H = 8.0                # taller than the dial so it stays on axis through the whole turn
SPIGOT_SINK = 1.0             # the spigot starts 1 mm INSIDE the base: a union face coplanar with the
                              # plate's top leaves non-manifold edges (the lesson from the nape base's
                              # umbilical window, README "print-readiness lessons")
BORE_CLEAR = 0.5              # coupon A showed a 0.3 clearance prints SNUG, and this one has to rotate
DIAL_X = 50.0                 # the loose dial, printed beside the base
GRIP_FLATS = 8                # flats, not scallops: a circular cutter is internally tangent to the rim at its
FLAT_R = C.NAPE_RATCHET_R[1] + 0.5   # innermost point and the boolean leaves zero-length slivers there (12
                              # non-manifold edges, 2026-09-16). A plane cutting a cylinder is always clean.
                              # 15.5 from centre, 1.0 clear of the tooth ring: the rim becomes a regular octagon

NOTES = ["print flat, no supports; both toothed rings print facing UP so neither is an overhang",
         "to test: flip the dial over onto the base's spigot so the two tooth rings face each other, press down and turn",
         "it must click freely one way and lock solid the other; if it clicks when LOOSENING and locks when TIGHTENING, flip NAPE_RATCHET_DIR in canon.py",
         "the dial is the real one's size (34 dia x 5); the bore is 0.5 clear on the spigot so it turns freely"]


def make():
    base = L.add_box("fit_coupon_c", (0.0, 0.0, BASE[2] / 2), BASE)
    # the nape body's ratchet ring, teeth up on the base's top face
    L.union(base, L.face_ratchet_ring("ring_body", (0.0, 0.0, BASE[2]), (0, 0, 1),
                                      C.NAPE_RATCHET_R[0], C.NAPE_RATCHET_R[1],
                                      C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR))
    # centring spigot
    L.union(base, L.add_cyl("spigot", (0.0, 0.0, BASE[2] + (SPIGOT_H - SPIGOT_SINK) / 2),
                            SPIGOT_D / 2, SPIGOT_H + SPIGOT_SINK, verts=48))

    # the loose dial: an annulus the size of the real one, tooth ring on its printed-up face
    bore_r = (SPIGOT_D + BORE_CLEAR) / 2
    dial_r = C.NAPE_DIAL_D / 2
    dial = L.revolve("dial", [(bore_r, 0.0), (dial_r, 0.0), (dial_r, C.NAPE_DIAL_T), (bore_r, C.NAPE_DIAL_T)],
                     axis="Z", center=(DIAL_X, 0.0, 0.0), segments=96)
    L.union(dial, L.face_ratchet_ring("ring_dial", (DIAL_X, 0.0, C.NAPE_DIAL_T), (0, 0, 1),
                                      C.NAPE_RATCHET_R[0], C.NAPE_RATCHET_R[1],
                                      C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR))
    # grip flats: each is one plane well clear of the tooth ring, and the box is wider than the chord it
    # cuts, so only its inner face ever touches the dial
    for k in range(GRIP_FLATS):
        M = Matrix.Translation((DIAL_X, 0.0, C.NAPE_DIAL_T / 2)) @ Matrix.Rotation(2.0 * math.pi * k / GRIP_FLATS, 4, 'Z')
        L.cut(dial, L.add_box_local(f"flat{k}", M, (FLAT_R + 6.0, 0.0, 0.0), (12.0, 24.0, C.NAPE_DIAL_T + 4.0)))

    L.union(base, dial)
    return base


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
