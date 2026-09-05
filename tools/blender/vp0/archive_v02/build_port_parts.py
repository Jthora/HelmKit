#!/usr/bin/env -S blender --background --python
"""
build_port_parts.py -- vp0.2 port standard add-ons (--out-dir):

  port_coupler.stl     10 x 10 x 30 double-male post (joins crown arch feet to pod top ports). Qty 2.
  port_plug_blank.stl  plug + flange + 16 x 16 x 8 block: the starting point for any add-on.
  port_cover.stl       flange + 3 mm stub for unused sockets.
  strap_anchor.stl     plug with a 28 x 4 webbing loop (chin/nape strap alternative to cheek hooks).
  battery_pack.stl     plug + 18650 sleeve (one cell per pod, rear-upper port).
All print flat / on their side, no supports.
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

I = Matrix.Identity(4)


def coupler():
    c = L.add_box("port_coupler", (0, 0, 0), (C.PORT_SQ, C.PORT_SQ, 2 * C.PORT_PLUG_LEN + 1.0))
    for z in (C.PORT_PLUG_LEN + 0.5 - C.PORT_XBOLT_DEPTH, -(C.PORT_PLUG_LEN + 0.5 - C.PORT_XBOLT_DEPTH)):
        L.cut(c, L.add_cyl("xb", (0, 0, z), C.M3_CLEAR_DIA / 2, C.PORT_SQ + 6, axis="X", verts=24))
    return c


def blank():
    b = L.port_plug("port_plug_blank", I)
    L.union(b, L.add_box("block", (0, 0, C.PORT_FLANGE_T + 4.0), (C.PORT_FLANGE, C.PORT_FLANGE, 8.0)))
    L.cut(b, L.port_plug_xhole(I))
    return b


def cover():
    c = L.add_box("port_cover", (0, 0, C.PORT_FLANGE_T / 2), (C.PORT_FLANGE, C.PORT_FLANGE, C.PORT_FLANGE_T))
    L.union(c, L.add_box("stub", (0, 0, -1.5), (C.PORT_SQ, C.PORT_SQ, 3.2)))
    return c


def strap_anchor():
    s = L.port_plug("strap_anchor", I)
    sw, sh = C.STRAP_SLOT
    L.union(s, L.add_box("loop", (0, 0, C.PORT_FLANGE_T + 3.0), (sw + 6.0, 10.0, 6.0)))
    L.cut(s, L.add_box("slot", (0, 0, C.PORT_FLANGE_T + 3.0), (sw, 14.0, sh)))
    L.cut(s, L.port_plug_xhole(I))
    return s


def battery_pack():
    p = L.port_plug("battery_pack", I)
    L.union(p, L.add_box("sleeve", (0, 0, C.PORT_FLANGE_T + 12.5), (72.0, 25.0, 25.0)))
    L.cut(p, L.add_box("cell", (2.0, 0, C.PORT_FLANGE_T + 12.5), (72.0, 21.0, 21.0)))
    L.cut(p, L.add_cyl("wire", (-34.0, 0, C.PORT_FLANGE_T + 12.5), 3.0, 6.0, axis="X", verts=16))
    L.cut(p, L.add_box("strapslot", (30.0, 0, C.PORT_FLANGE_T + 24.5), (3.0, 30.0, 5.0)))
    L.cut(p, L.port_plug_xhole(I))
    return p


PARTS = {
    "port_coupler": (coupler, L.ROT_NONE, ["print flat; joins crown foot to pod top port; 2x M3 cross-bolts"]),
    "port_plug_blank": (blank, L.ROT_X_TO_Z, ["print on its side; modify the 16x16x8 block for your add-on"]),
    "port_cover": (cover, L.ROT_NONE, ["print flange down"]),
    "strap_anchor": (strap_anchor, L.ROT_X_TO_Z, ["print on its side; 25 mm webbing"]),
    "battery_pack": (battery_pack, L.ROT_Y_TO_Z, ["print on its side (sleeve roof bridges 21 mm); one 18650 per pod; wire exits the closed end"]),
}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(L.argv_after_dashdash())
    for name, (mk, rot, notes) in PARTS.items():
        L.reset_scene()
        L.finalize_and_export(mk(), Path(args.out_dir) / f"{name}.stl", rot, notes)


if __name__ == "__main__":
    main()
