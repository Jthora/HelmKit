#!/usr/bin/env -S blender --background --python
"""
build_fit_coupon.py -- vp0.4 fit coupon: print this FIRST.

Plate with: a pinned socket block + loose pinned plug (port fit, nail fit),
a clam cleat (rope jam test), a spine groove and a collar groove sample,
M3 / M4 / hex holes, and the M4 nut pocket. Print flat, no supports. Qty: 1.
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
NOTES = ["print flat; nail must press into the 3.2 holes with light hammer taps and not split the block;",
         "rope must jam in the cleat when pulled from the narrow end and lift out freely; adjust PIN_DIA / CLEAT in canon.py"]


def make():
    plate = L.add_box("fit_coupon", (0.0, 0.0, 3.0), (110.0, 44.0, 6.0))
    xs = [-48, -36, -24, -12]
    y = 14.0
    L.cut(plate, L.add_cyl("h_m3", (xs[0], y, 3.0), C.M3_CLEAR_DIA / 2, 10.0, verts=32))
    L.cut(plate, L.add_cyl("h_pin", (xs[1], y, 3.0), C.PIN_DIA / 2, 10.0, verts=24))
    L.cut(plate, L.add_cyl("h_m4", (xs[2], y, 3.0), C.M4_CLEAR_DIA / 2, 10.0, verts=32))
    L.cut(plate, L.add_hex_prism("h_hex4", (xs[3], y, 6.0), C.M4_NUT_AF + 0.3, 2 * (C.M4_NUT_T + 0.3)))
    # pinned socket block standing on the plate (socket opens +Z, pin along X)
    Mp = L.frame((-30.0, -10.0, 6.0 + C.PORT_BLOCK_LEN), (0, 0, 1), (1, 0, 0))
    L.union(plate, L.add_box("sockblock", (-30.0, -10.0, 6.0 + C.PORT_BLOCK_LEN / 2 - 0.5), (C.PORT_BLOCK, C.PORT_BLOCK, C.PORT_BLOCK_LEN + 1.0)))
    # cleat on the plate (rope along X)
    Mc = L.frame((25.0, -6.0, 6.0), (0, 0, 1), (1, 0, 0))
    L.union(plate, L.clam_cleat("cleat", Mc, base_z=-0.5))
    # spine groove sample along the front edge, collar groove sample around the socket block
    gw, gd = C.SPINE_GROOVE
    L.cut(plate, L.add_box("spine", (5.0, 18.0, 6.0), (40.0, gw, 2 * gd)))
    L.cut(plate, L.port_socket_cut(Mp, tag="c"))
    L.cut(plate, *L.port_pin_cutters(Mp, -(C.PORT_BLOCK / 2 + 1.0), C.PORT_BLOCK / 2 + 1.0, tag="c"))
    L.cut(plate, L.collar_cutter(Mp, -C.PORT_BLOCK_LEN / 2.0, C.PORT_BLOCK, tag="c"))
    # loose pinned plug beside the plate
    Mpl = L.frame((70.0, 0.0, C.PORT_PLUG_LEN), (0, 0, 1), (1, 0, 0))
    plug = L.port_plug("plug", Mpl, lip=(12.0, 1.0))
    L.cut(plug, L.add_cyl_local("pin", Mpl, (0.0, 0.0, -C.PORT_PIN_DEPTH), C.PIN_DIA / 2, C.PORT_SQ + 6.0, axis="X", verts=24))
    L.union(plate, plug)
    return plate


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
