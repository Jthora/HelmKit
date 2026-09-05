#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon.py -- vp0.3 fit coupon: print this FIRST.

Plate with every hole/pocket in the set, a flush socket block + loose plug
(port fit, lock screw), a 30 mm rack strip + loose pinion (nape gear mesh),
and a ridge plate (apex clamp). Print flat, no supports. Qty: 1.
Holes along the long edge: M3 3.4 + cbore | M3 tap 2.5 | M4 4.4 | hex M3 | hex M4 | M2 tap 1.7
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
from mathutils import Matrix, Vector  # type: ignore

PRINT_ROT = L.ROT_NONE
NOTES = ["print flat; check every fit before printing anything large; adjust canon.py clearances if needed"]


def make():
    plate = L.add_box("fit_coupon", (0.0, 0.0, 3.0), (100.0, 40.0, 6.0))
    xs = [-40, -24, -8, 8, 24, 40]
    y = 12.0
    L.cut(plate, L.add_cyl("h_m3", (xs[0], y, 3.0), C.M3_CLEAR_DIA / 2, 10.0, verts=32))
    L.cut(plate, L.add_cyl("h_cb", (xs[0], y, 6.0), 3.1, 4.0, verts=32))
    L.cut(plate, L.add_cyl("h_tap", (xs[1], y, 3.0), C.M3_TAP_DIA / 2, 10.0, verts=16))
    L.cut(plate, L.add_cyl("h_m4", (xs[2], y, 3.0), C.M4_CLEAR_DIA / 2, 10.0, verts=32))
    L.cut(plate, L.add_hex_prism("h_hex3", (xs[3], y, 6.0), C.M3_NUT_AF + 0.3, 2 * (C.M3_NUT_T + 0.3)))
    L.cut(plate, L.add_hex_prism("h_hex4", (xs[4], y, 6.0), C.M4_NUT_AF + 0.3, 2 * (C.M4_NUT_T + 0.3)))
    L.cut(plate, L.add_cyl("h_m2", (xs[5], y, 3.0), C.M2_TAP_DIA / 2, 10.0, verts=16))
    # socket block standing on the plate, socket opening +Z, screw along X
    Mp = L.frame((25.0, -8.0, 6.0 + C.PORT_BLOCK_LEN), (0, 0, 1), (1, 0, 0))
    L.union(plate, L.add_box("sockblock", (25.0, -8.0, 6.0 + C.PORT_BLOCK_LEN / 2 - 0.5), (C.PORT_BLOCK, C.PORT_BLOCK, C.PORT_BLOCK_LEN + 1.0)))
    # rack strip on the back edge, teeth pointing -Y
    Mrk = L.frame((-15.0, -20.0, 6.0), (0, 0, -1), (1, 0, 0))
    L.union(plate, L.extrude_polygon("rack", L.rack_poly(30.0, C.GEAR_MODULE, C.GEAR_PA, 4.0), 6.0, Mrk, z0=-1.0))
    L.cut(plate, L.port_socket_cut(Mp, tag="c"))
    L.cut(plate, *L.port_screw_cutters(Mp, -1.0, C.PORT_BLOCK / 2 + 1.0, tag="c"))
    # loose parts
    plug = L.port_plug("plug", L.frame((70.0, -14.0, C.PORT_PLUG_LEN), (0, 0, 1), (1, 0, 0)), lip=(12.0, 1.0))
    L.cut(plug, L.port_plug_thread_hole(L.frame((70.0, -14.0, C.PORT_PLUG_LEN), (0, 0, 1), (1, 0, 0))))
    pinion = L.extrude_polygon("pinion", L.involute_gear_poly(C.PINION_N, C.GEAR_MODULE, C.GEAR_PA), C.PINION_W, Matrix.Translation((-75.0, 12.0, 0.0)))
    L.cut(pinion, L.add_cyl("pb", (-75.0, 12.0, 2.5), 2.0, 10.0, verts=16))
    ridge = L.extrude_polygon("ridge", L.ridge_plate_poly(0.0, 30.0, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 3.0, C.CROWN_SERR_PITCH / 4), 10.0, Matrix.Translation((-90.0, -20.0, 0.0)))
    for o in (plug, pinion, ridge):
        L.union(plate, o)
    return plate


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
