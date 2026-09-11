#!/usr/bin/env -S blender --background --python
"""
build_port_parts.py -- vp0.7 cylinder port standard parts (--out-dir):

  port_plug.stl          8 mm peg + 12 mm cap: closes an unused cradle socket
  port_coupler.stl       double-male 8 mm peg, 30 mm, cross holes 7 mm each side of the joint (crown arch feet, stacked add-ons)
  port_drill_guide.stl   block with an 8.3 hole and a 3.4 cross hole at 7 mm: drill rods and pegs identically
Every peg: Ø8, 14.5 long, cross hole at 7 mm from the mouth for an M3 or a nail.
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C


def peg(name, z0, length):
    p = L.add_cyl(name, (0.0, 0.0, z0 + length / 2), C.CYL_PEG_D / 2, length, axis="Z", verts=48)
    return p


def plug():
    p = peg("port_plug", 3.0 - 0.5, C.CYL_PEG_LEN + 0.5)
    cap = L.add_box("cap", (0.0, 0.0, 1.5), (12.0, 12.0, 3.0))
    L.fillet(cap, width=1.0)
    L.union(p, cap)
    L.cut(p, L.add_cyl("cross", (0.0, 0.0, 3.0 + C.CYL_PEG_LEN - C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2, C.CYL_PEG_D + 4.0, axis="X", verts=24))
    return p


def plug_flush():
    """Combat-trim socket plug: same peg, 1 mm cap (nail through the cross hole retains it; lever it out with the nail)."""
    p = peg("port_plug_flush", 1.3 - 0.5, C.CYL_PEG_LEN + 0.5)
    cap = L.add_box("cap", (0.0, 0.0, 0.65), (12.0, 12.0, 1.3))
    L.fillet(cap, width=0.4)
    L.union(p, cap)
    L.cut(p, L.add_cyl("cross", (0.0, 0.0, 1.3 + C.CYL_PEG_LEN - C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2, C.CYL_PEG_D + 4.0, axis="X", verts=24))
    return p


def coupler():
    length = 2 * C.CYL_PEG_LEN + 1.0
    p = peg("port_coupler", 0.0, length)
    for z in (length / 2 + C.CYL_PIN_Z, length / 2 - C.CYL_PIN_Z):     # 7 mm each side of the joint plane
        L.cut(p, L.add_cyl("cross", (0.0, 0.0, z), C.M3_CLEAR_DIA / 2, C.CYL_PEG_D + 4.0, axis="X", verts=24))
    return p


def drill_guide():
    g = L.add_box("port_drill_guide", (0.0, 0.0, 10.0), (24.0, 20.0, 20.0))
    L.fillet(g, width=1.0)
    L.cut(g, L.add_cyl("hole", (0.0, 0.0, 10.0), C.CYL_SOCKET_D / 2, 24.0, axis="Z", verts=48))
    L.cut(g, L.add_cyl("cross", (0.0, 0.0, 20.0 - C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2, 30.0, axis="X", verts=24))
    return g


PARTS = {
    "port_plug": (plug, L.ROT_NONE, ["print cap down; closes an unused cradle socket"]),
    "port_plug_flush": (plug_flush, L.ROT_NONE, ["print cap down, x4 for the combat trim: 1 mm cap, nail through the cross hole"]),
    "port_coupler": (coupler, L.ROT_NONE, ["print standing; stacks an add-on peg on a cradle socket"]),
    "port_drill_guide": (drill_guide, L.ROT_NONE, ["drill 8 mm aluminium rod or printed pegs for the cross-bolt"]),
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
