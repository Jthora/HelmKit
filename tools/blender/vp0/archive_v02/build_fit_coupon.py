#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon.py -- vp0.2 fit coupon: print this FIRST.

Plate with every hole/pocket in the set, a serration pad + loose serrated
puck (pivot detents), a port socket boss + loose plug (0.3 mm socket fit and
cross-bolt), a 30 mm rack strip + loose pinion (nape gear mesh), and a
ridge-plate pair (apex clamp). Print flat, no supports. Qty: 1.

Holes along the long edge, left to right: M5 5.4 | knob bore 5.6 | M3 3.4 +
cbore | M3 heat-set 4.3 | M3 tap 2.5 | hex M3 | hex M4 | hex M5.
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
    xs = [-42, -30, -18, -6, 6, 18, 30, 42]
    y = 12.0
    L.cut(plate, L.add_cyl("h_m5", (xs[0], y, 3.0), C.M5_CLEAR_DIA / 2, 10.0, verts=48))
    L.cut(plate, L.add_cyl("h_bore", (xs[1], y, 3.0), C.KNOB_BORE / 2, 10.0, verts=48))
    L.cut(plate, L.add_cyl("h_m3", (xs[2], y, 3.0), C.M3_CLEAR_DIA / 2, 10.0, verts=32))
    L.cut(plate, L.add_cyl("h_cb", (xs[2], y, 6.0), 6.5 / 2, 4.0, verts=32))
    L.cut(plate, L.add_cyl("h_hs", (xs[3], y, 6.0), C.M3_HEATSET_HOLE_DIA / 2, 10.0, verts=32))
    L.cut(plate, L.add_cyl("h_tap", (xs[4], y, 3.0), C.M3_TAP_DIA / 2, 10.0, verts=16))
    L.cut(plate, L.add_hex_prism("h_hex3", (xs[5], y, 6.0), C.M3_NUT_AF + 0.3, 2 * (C.M3_NUT_T + 0.3)))
    L.cut(plate, L.add_hex_prism("h_hex4", (xs[6], y, 6.0), C.M4_NUT_AF + 0.3, 2 * (C.M4_NUT_T + 0.3)))
    L.cut(plate, L.add_hex_prism("h_hex5", (xs[7], y, 6.0), C.M5_NUT_AF + 0.3, 2 * C.KNOB_POCKET_DEPTH))
    # serration pad (bottom-left) + pivot bore
    L.cut(plate, L.add_cyl("pad_bore", (-35.0, -8.0, 3.0), C.M5_CLEAR_DIA / 2, 20.0, verts=48))
    # port socket boss standing on the plate (bottom-right)
    Mp = L.frame((25.0, -8.0, 6.0 + C.PORT_BOSS_H), (0, 0, 1), (1, 0, 0))
    L.union(plate, L.port_boss("boss", Mp))
    # rack strip along the plate's back edge (teeth pointing +Y)
    Mrk = L.frame((-15.0, -20.0, 5.0), (0, 0, 1), (1, 0, 0))     # teeth point +Y? no: local y = +Y, so flip below
    Mrk = L.frame((-15.0, -20.0, 5.0), (0, 0, 1), (-1, 0, 0))    # local y = Z x (-X) = -Y : teeth point outward (-Y)
    L.union(plate, L.extrude_polygon("rack", L.rack_poly(30.0, C.GEAR_MODULE, C.GEAR_PA, 4.0), 6.0, Mrk, z0=0.0))   # z 5..11, sunk 1 mm
    L.cut(plate, *L.port_cutters(Mp, tag="c"))
    # loose parts beside the plate
    puck = L.revolve("puck", [(C.M5_CLEAR_DIA / 2, 0.0), (12.3, 0.0), (12.3, C.RING_T), (C.M5_CLEAR_DIA / 2, C.RING_T)],
                     axis="Z", center=(70.0, 12.0, 0.0), segments=96)
    plug = L.port_plug("plug", L.frame((70.0, -14.0, C.PORT_PLUG_LEN), (0, 0, 1), (1, 0, 0)))
    L.cut(plug, L.port_plug_xhole(L.frame((70.0, -14.0, C.PORT_PLUG_LEN), (0, 0, 1), (1, 0, 0))))
    pinion = L.extrude_polygon("pinion", L.involute_gear_poly(C.PINION_N, C.GEAR_MODULE, C.GEAR_PA), C.PINION_W,
                               Matrix.Translation((-75.0, 12.0, 0.0)))
    L.cut(pinion, L.add_cyl("pb", (-75.0, 12.0, 2.5), 2.0, 10.0, verts=16))
    ridge = L.extrude_polygon("ridge", L.ridge_plate_poly(0.0, 30.0, C.CROWN_SERR_PITCH, C.CROWN_SERR_H, 3.0, C.CROWN_SERR_PITCH / 4),
                              10.0, Matrix.Translation((-90.0, -20.0, 0.0)))
    for o in (puck, plug, pinion, ridge):
        L.union(plate, o)
    # serrations last
    L.union(plate, L.serration_solid("pad", (-35.0, -8.0, 6.0), (0, 0, 1)))
    L.union(plate, L.serration_solid("puck_serr", (70.0, 12.0, C.RING_T), (0, 0, 1)))
    return plate


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
