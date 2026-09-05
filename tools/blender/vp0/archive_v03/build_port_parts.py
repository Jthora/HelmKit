#!/usr/bin/env -S blender --background --python
"""
build_port_parts.py -- vp0.3 port standard parts (--out-dir):

  port_coupler_crown.stl   23 mm double-male post: pod top port <-> crown foot. Qty 2.
  port_coupler_rear.stl    28 mm: pod rear port <-> rear band block. Qty 2.
  port_coupler_brow.stl    ~39 mm: pod front port <-> brow wing socket. Qty 2.
  port_plug_blank.stl      post + 16x16x8 block: starting point for add-ons (pylons, sensors).
  port_cover.stl           post with a 1 mm lip for unused sockets (screw-locked like everything else).
  strap_anchor.stl         post with a 28x4 webbing loop (chin / nape strap). Qty 2 default.
  battery_sleeve.stl       optional external 18650 sleeve (cells normally live inside the pods).
All couplers may be replaced by 10 x 10 x 1 mm aluminium square tube cut to length, drilled 2.5 mm at 7 mm from each end.
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


def coupler_part(name, length):
    c = L.coupler(name, length)
    L.fillet(c, width=0.6)
    return c


def blank():
    b = L.port_plug("port_plug_blank", I, lip=(16.0, 2.0))
    L.union(b, L.add_box("block", (0, 0, 2.0 + 4.0 - 0.5), (16.0, 16.0, 9.0)))
    L.cut(b, L.port_plug_thread_hole(I))
    return b


def cover():
    c = L.port_plug("port_cover", I, lip=(12.0, 1.0))
    L.cut(c, L.port_plug_thread_hole(I))
    L.fillet(c, width=0.5)
    return c


def strap_anchor():
    s = L.port_plug("strap_anchor", I, lip=(16.0, 2.0))
    sw, sh = C.STRAP_SLOT
    L.union(s, L.add_box("loop", (0, 0, 2.0 + 3.0 - 0.5), (sw + 6.0, 10.0, 7.0)))
    L.cut(s, L.add_box("slot", (0, 0, 2.0 + 3.5), (sw, 14.0, sh)))
    L.cut(s, L.port_plug_thread_hole(I))
    L.fillet(s, width=0.6)
    return s


def battery_sleeve():
    p = L.port_plug("battery_sleeve", I, lip=(16.0, 2.0))
    L.union(p, L.add_box("sleeve", (0, 0, 2.0 + 12.5 - 0.5), (72.0, 25.0, 26.0)))
    L.cut(p, L.add_box("cell", (2.0, 0, 2.0 + 12.5), (72.0, 21.0, 21.0)))
    L.cut(p, L.add_cyl("wire", (-34.0, 0, 2.0 + 12.5), 3.0, 6.0, axis="X", verts=16))
    L.cut(p, L.add_box("strapslot", (30.0, 0, 2.0 + 25.0), (3.0, 30.0, 5.0)))
    L.cut(p, L.port_plug_thread_hole(I))
    return p


def brow_len():
    import build_brow_panel as BP
    return BP.BROW_COUPLER_LEN


PARTS = {
    "port_coupler_crown": (lambda: coupler_part("port_coupler_crown", C.COUPLER_CROWN_LEN), L.ROT_NONE, [f"{C.COUPLER_CROWN_LEN:.1f} mm; print flat or cut from tube"]),
    "port_coupler_rear": (lambda: coupler_part("port_coupler_rear", C.COUPLER_REAR_LEN), L.ROT_NONE, [f"{C.COUPLER_REAR_LEN:.1f} mm; print flat or cut from tube"]),
    "port_coupler_brow": (lambda: coupler_part("port_coupler_brow", brow_len()), L.ROT_NONE, ["print flat or cut from tube"]),
    "port_plug_blank": (blank, L.ROT_X_TO_Z, ["print on its side; modify the block for your add-on"]),
    "port_cover": (cover, L.ROT_NONE, ["print lip down"]),
    "strap_anchor": (strap_anchor, L.ROT_X_TO_Z, ["print on its side; 25 mm webbing"]),
    "battery_sleeve": (battery_sleeve, L.ROT_Y_TO_Z, ["optional external cell sleeve; print on its side"]),
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
