#!/usr/bin/env -S blender --background --python
"""
build_port_parts.py -- vp0.4 port standard parts (--out-dir):

  port_coupler_crown / _rear / _brow.stl   printed 10 mm posts with pin holes 7 mm from each end
                                            (preferred: aluminium 10 x 10 x 1 tube, drilled with the guide)
  coupler_drill_guide.stl   10.2 mm square slot with a 3.2 mm hole at 7 mm: drill tubes and posts identically
  socket_form.stl           10.3 mm square former with 1 deg draft and a knob: cast oversize sockets in metal epoxy
  port_plug_blank.stl       plug + 16 x 16 x 8 block, pinned: add-on starting point
  port_cover.stl            pinned plug with a 1 mm lip for unused sockets
  strap_anchor.stl          pinned plug with a 28 x 4 webbing/rope loop (chin strap)
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


def pin_cross_hole(z):
    return L.add_cyl("pin", (0.0, 0.0, z), C.PIN_DIA / 2.0, C.PORT_SQ + 6.0, axis="X", verts=24)


def coupler_part(name, length):
    c = L.add_box(name, (0.0, 0.0, 0.0), (C.PORT_SQ, C.PORT_SQ, length))
    L.fillet(c, width=0.6)
    for z in (length / 2.0 - C.PORT_PIN_DEPTH, -(length / 2.0 - C.PORT_PIN_DEPTH)):
        L.cut(c, pin_cross_hole(z))
    return c


def plug_with_pin(name, lip):
    p = L.port_plug(name, I, lip=lip)
    L.cut(p, L.add_cyl("pin", (0.0, 0.0, -C.PORT_PIN_DEPTH), C.PIN_DIA / 2.0, C.PORT_SQ + 6.0, axis="X", verts=24))
    return p


def blank():
    b = plug_with_pin("port_plug_blank", (16.0, 2.0))
    L.union(b, L.add_box("block", (0, 0, 2.0 + 4.0 - 0.5), (16.0, 16.0, 9.0)))
    return b


def cover():
    c = plug_with_pin("port_cover", (12.0, 1.0))
    L.fillet(c, width=0.5)
    return c


def strap_anchor():
    s = plug_with_pin("strap_anchor", (16.0, 2.0))
    sw, sh = C.STRAP_SLOT
    L.union(s, L.add_box("loop", (0, 0, 2.0 + 3.0 - 0.5), (sw + 6.0, 10.0, 7.0)))
    L.cut(s, L.add_box("slot", (0, 0, 2.0 + 3.5), (sw, 14.0, sh)))
    L.fillet(s, width=0.6)
    return s


def drill_guide():
    g = L.add_box("coupler_drill_guide", (0, 0, 10.0), (30.0, 22.0, 20.0))
    L.cut(g, L.add_box("slot", (0, 0, 10.0), (34.0, C.PORT_SQ + 0.2, C.PORT_SQ + 0.2)))
    for x in (-15.0 + C.PORT_PIN_DEPTH, 15.0 - C.PORT_PIN_DEPTH):
        L.cut(g, L.add_cyl("hole", (x, 0.0, 10.0), C.PIN_DIA / 2.0, 30.0, axis="Z", verts=24))
    L.fillet(g, width=1.0)
    return g


def socket_form():
    sq = C.PORT_SQ + C.PORT_CLEAR
    f = L.add_box("socket_form", (0, 0, 6.0), (sq, sq, 12.0))
    L.union(f, L.add_cyl("knob", (0, 0, 12.0 + 8.0), 9.0, 16.0, axis="Z", verts=48))
    L.fillet(f, width=0.5)
    return f


def brow_len():
    import build_brow_panel as BP
    return BP.BROW_COUPLER_LEN


PARTS = {
    "port_coupler_crown": (lambda: coupler_part("port_coupler_crown", C.COUPLER_CROWN_LEN), L.ROT_NONE, [f"{C.COUPLER_CROWN_LEN:.1f} mm; print flat or cut tube"]),
    "port_coupler_rear": (lambda: coupler_part("port_coupler_rear", C.COUPLER_REAR_LEN), L.ROT_NONE, [f"{C.COUPLER_REAR_LEN:.1f} mm; print flat or cut tube"]),
    "port_coupler_brow": (lambda: coupler_part("port_coupler_brow", brow_len()), L.ROT_NONE, ["print flat or cut tube"]),
    "coupler_drill_guide": (drill_guide, L.ROT_NONE, ["print flat; clamp a tube in the slot, drill 3.2 through the guide holes"]),
    "socket_form": (socket_form, L.ROT_NONE, ["wrap in PTFE tape, wax, press into an oversize socket filled with metal epoxy, pull after cure"]),
    "port_plug_blank": (blank, L.ROT_X_TO_Z, ["print on its side; modify the block for your add-on"]),
    "port_cover": (cover, L.ROT_NONE, ["print lip down"]),
    "strap_anchor": (strap_anchor, L.ROT_X_TO_Z, ["print on its side; 25 mm webbing or rope"]),
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
