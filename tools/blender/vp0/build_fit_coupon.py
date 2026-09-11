#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon.py -- vp0.9 fit coupon: print this FIRST.

Plate with: the cylinder port (socket block + loose peg, nail fit), the disk BAYONET (boss on the
plate + loose stub: quarter turn to the stop), the nape ratchet ring pair (dial click test),
hole gauges (M3 clear, 3.2 nail press, M4 clear, M4 nut pocket; 3.4 nail slip, 2.2 pinlock nail,
2.5 M3 self-tap). Print flat, no supports. Qty: 1.
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
from mathutils import Matrix, Vector  # type: ignore

PRINT_ROT = L.ROT_NONE
NOTES = ["print flat; the 3.2 nail must press into the 3.2 hole with light taps and slip through the 3.4 hole; a 2 mm nail slips through the 2.2 hole; an M3 self-taps into the 2.5 hole",
         "the 8 mm peg must slide into the 8.3 socket and take an M3 cross-bolt; the bayonet stub must drop into the boss and turn about 107 deg to the stop without force, tightening over the last third",
         "the loose ratchet disc must click over the plate ring one way and lock the other; adjust PIN_DIA / NAPE_RATCHET_DIR / BAYONET_* in canon.py"]


def make():
    plate = L.add_box("fit_coupon", (0.0, 0.0, 3.0), (110.0, 48.0, 6.0))
    # hole gauges: row 1 (y 16) M3 clear, 3.2 press, M4 clear, M4 nut; row 2 (y -17) 3.4 slip, 2.2 pinlock, 2.5 tap
    for x, r in ((-50.0, C.M3_CLEAR_DIA / 2), (-42.0, C.PIN_DIA / 2), (-34.0, C.M4_CLEAR_DIA / 2)):
        L.cut(plate, L.add_cyl("gauge", (x, 16.0, 3.0), r, 10.0, verts=32))
    L.cut(plate, L.add_hex_prism("h_hex4", (-26.0, 16.0, 6.0), C.M4_NUT_AF + 0.3, 2 * (C.M4_NUT_T + 0.3)))
    for x, r in ((-12.0, 1.7), (-4.0, C.NAPE_PINLOCK_PIN["hole"] / 2), (4.0, C.M3_TAP_DIA / 2)):
        L.cut(plate, L.add_cyl("gauge2", (x, -17.0, 3.0), r, 10.0, verts=24))
    # cylinder socket block standing on the plate (socket opens +Z, cross hole along X)
    L.union(plate, L.add_box("sockblock", (-30.0, -10.0, 6.0 + 9.0 - 0.5), (16.0, 16.0, 18.0 + 1.0)))
    L.cut(plate, L.add_cyl("csock", (-30.0, -10.0, 6.0 + 18.0 - C.CYL_DEPTH / 2 + 0.5), C.CYL_SOCKET_D / 2, C.CYL_DEPTH + 1.0, axis="Z", verts=48))
    L.cut(plate, L.add_cyl("ccross", (-30.0, -10.0, 6.0 + 18.0 - C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2, 24.0, axis="X", verts=24))
    # bayonet boss on the plate: same revolve and cutters as the disk back (local z 0 = 2 mm below the plate top, like the disk's head face)
    Mb = Matrix.Translation((-2.0, 6.0, 6.0 - C.DISK_PLATE_T))
    L.union(plate, build_disk.bayonet_boss(Mb, C.DISK_PLATE_T - 0.1))
    build_disk.bayonet_cuts(plate, Mb, mouth=False, z_below=6.0 - C.DISK_PLATE_T + 1.0)
    # face-ratchet test: ring on the plate + a loose ring disc to click against it
    L.union(plate, L.face_ratchet_ring("ratchet", (32.0, 0.0, 6.0), (0, 0, 1), C.NAPE_RATCHET_R[0], C.NAPE_RATCHET_R[1],
                                       C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR))
    disc = L.revolve("disc", [(2.75, 0.0), (22.0, 0.0), (22.0, 4.0), (2.75, 4.0)], axis="Z", center=(85.0, 0.0, 0.0), segments=100)
    L.union(disc, L.face_ratchet_ring("ratchet2", (85.0, 0.0, 4.0), (0, 0, 1), C.NAPE_RATCHET_R[0], C.NAPE_RATCHET_R[1],
                                      C.NAPE_RATCHET_TEETH, C.NAPE_RATCHET_H, direction=C.NAPE_RATCHET_DIR))
    # loose peg beside the plate
    plug = L.add_cyl("plug", (-72.0, 0.0, C.CYL_PEG_LEN / 2), C.CYL_PEG_D / 2, C.CYL_PEG_LEN, axis="Z", verts=48)
    L.cut(plug, L.add_cyl("pin", (-72.0, 0.0, C.CYL_PEG_LEN - C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2, C.CYL_PEG_D + 6.0, axis="X", verts=24))
    # loose bayonet stub: the nexus stalk (Ø20, two 6 x 3 x 3 lugs at 4..7 above the flange face) on a Ø30 x 3 base
    sx, sy = 85.0, 50.0
    stub = L.add_cyl("stub_base", (sx, sy, 1.5), 15.0, 3.0, axis="Z", verts=60)
    L.union(stub, L.add_cyl("stalk", (sx, sy, (2.5 + 3.0 + C.STALK_LEN) / 2), C.STALK_D / 2, 3.0 + C.STALK_LEN - 2.5, axis="Z", verts=72))
    lw, lr, lh = C.STALK_LUG
    n0, n1 = C.STALK_LUG_N
    for s in (+1, -1):
        L.union(stub, L.add_box("lug", (sx + s * (C.STALK_D / 2 + lr / 2 - 0.15), sy, 3.0 + (n0 + n1) / 2), (lr + 0.3, lw, n1 - n0)))
    for o in (plug, disc, stub):
        L.union(plate, o)
    return plate


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
