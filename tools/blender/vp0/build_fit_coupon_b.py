#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon_b.py -- vp0.17 second fit coupon: the fits the first coupon does not test. Print flat, no supports. Qty: 1.

  block A  standing 30 x 12 x 22 with a row of HORIZONTAL holes (Ø2.5, 3.4 round, 3.4 teardrop, 4.1, 5.0) at 12 mm up, and a
           sideways M3 hex nut pocket 2.7 deep in its end face: the cradle's inner-face pockets and every Y-axis hole print like this
  hub      Ø36 x 8 stub + a loose Ø44 / 36.3 x 7 ring beside it: the visor ring on the spool hub
  stalk    Ø20 x 14 stub with the Ø8.2 bore and the radial Ø3.4 lock-pin hole at n 10.8: drop a 7.8 mm nail piece in, push it out with a rod
  pins     Ø4.1 and Ø4.3 sockets 6 deep for a printed Ø4 pin (print bar_pin from build_sensor_bar)
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

PRINT_ROT = L.ROT_NONE
NOTES = ["print flat; M3 nut must press into the sideways pocket; a 3.4 nail slips through the teardrop 3.4 but binds in the round 3.4 if your printer sags",
         "the ring must turn freely on the hub; the 7.8 mm nail piece must sit in the stalk hole and move 1.8 mm when pushed from the bore",
         "a printed Ø4 pin: snug in 4.1, free in 4.3",
         "a 2 mm nail: must enter the 2.1 (snug) and 2.2 (clear) vertical holes near the pin sockets; if not, the pin-lock gets a 2.0 mm drill pass"]


def make():
    plate = L.add_box("fit_coupon_b", (0.0, 0.0, 2.0), (110.0, 60.0, 4.0))
    # block A with horizontal holes and a sideways nut pocket
    bx, by = -30.0, 12.0
    L.union(plate, L.add_box("blockA", (bx, by, 4.0 + 12.0 - 0.5), (46.0, 12.0, 24.0 + 1.0)))   # 46 long: the nut pocket in the +x end face clears the last hole; 24 tall: 2.7 over the pocket
    holes = ((-16.0, C.M3_TAP_DIA / 2, False), (-8.0, C.M3_CLEAR_DIA / 2, False), (0.0, C.M3_CLEAR_DIA / 2, True), (8.0, 2.05, True), (16.0, 2.5, True))
    for dx, r, td in holes:
        if td:
            L.cut(plate, L.add_teardrop("h", (bx + dx, by, 4.0 + 12.0), r, 16.0, (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), verts=20))
        else:
            L.cut(plate, L.add_cyl("h", (bx + dx, by, 4.0 + 12.0), r, 16.0, axis="Y", verts=20))
    af, dp = C.NEXUS_NUT_POCKET
    L.cut(plate, L.add_hex_prism("nutp", (bx + 23.0 - dp / 2 + 0.5, by, 4.0 + 18.0), af, dp + 1.0, axis="X"))   # sideways pocket in the +x end face
    # hub stub + loose ring
    od, idia, t = C.NEXUS_RING
    hub_d = C.NEXUS_SPOOL[2]
    L.union(plate, L.add_cyl("hub", (20.0, 12.0, 4.0 + 4.0 - 0.5), hub_d / 2, 8.0 + 1.0, axis="Z", verts=96))
    ring = L.revolve("ring", [(idia / 2, 0.0), (od / 2, 0.0), (od / 2, t), (idia / 2, t)], axis="Z", center=(0.0, -30.0 - od / 2 - 3.0, 0.0), segments=100)   # a loose island beside the plate
    # stalk stub with bore and lock-pin hole
    sx, sy = -20.0, -16.0
    L.union(plate, L.add_cyl("stalk", (sx, sy, 4.0 + C.STALK_LEN / 2 - 0.5), C.STALK_D / 2, C.STALK_LEN + 1.0, axis="Z", verts=72))
    L.cut(plate, L.add_cyl("bore", (sx, sy, 4.0 + C.STALK_LEN / 2 + 1.0), C.STALK_BORE / 2, C.STALK_LEN + 2.0, axis="Z", verts=48))
    lk = C.BAYONET_LOCK
    r_a, r_b = C.STALK_BORE / 2 - 1.0, C.STALK_D / 2 + 1.0
    L.cut(plate, L.add_cyl("pinhole", (sx, sy + (r_a + r_b) / 2, 4.0 + lk["n"]), (lk["pin_dia"] + 0.2) / 2, r_b - r_a, axis="Y", verts=16))   # round, as on the nexus
    # pin sockets
    pd = C.SENSOR_BAR["pin"][0]
    for dx, clr in ((44.0, C.SENSOR_BAR["pin_fit"][0]), (50.0, C.SENSOR_BAR["pin_fit"][1])):
        L.cut(plate, L.add_cyl("psock", (dx, -18.0, 4.0 - 3.0 + 0.5), (pd + clr) / 2, 6.0 + 1.0, axis="Z", verts=24))
    # Track P: the nape pin-lock's 2 mm nail holes, vertical, snug and clearance sizes (the one fit no coupon covered)
    npin = C.NAPE_PINLOCK_PIN
    for dx, d in ((36.0, npin["hole_bottom"]), (40.0, npin["hole"])):
        L.cut(plate, L.add_cyl("nailhole", (dx, -26.0, 2.0), d / 2, 4.0 + 2.0, axis="Z", verts=16))
    L.union(plate, ring)
    return plate


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
