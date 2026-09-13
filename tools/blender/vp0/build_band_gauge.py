#!/usr/bin/env -S blender --background --python
"""
build_band_gauge.py -- vp0.17 head-fit gauges (--out-dir): thin horizontal slices of the cradle and the rear halves.

Print this before the cradle. It is the bottom 3 mm of the band, 7 mm wide, following the cradle's centreline
with its lower edge on the band's real bottom edge (forehead rise included): the head width, the temple contact
and the ear clearance can be checked on the wearer's head in a print of minutes instead of the cradle's eight hours.

Pass rule: the gauge sits level on the head with its inner face touching at the temples and its lower edge 4 mm
or more above the ear tops. The rear halves twist below this height and have no gauge; their fit is checked at
the cradle wear test.
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_cradle_front as BCF

from mathutils import Vector  # type: ignore

GAUGE_H = 3.0                  # fifteen 0.2 mm layers when printed flat


def front_gauge():
    """The bottom 3 mm of the band as a plain ribbon along the cradle centreline, 7 mm wide (the band's thickness),
    its lower edge on the band's real bottom edge everywhere (the forehead rise included). No nodes, no grooves,
    no bores: nothing to leave slivers or coplanar cuts, and nothing the head-fit question needs."""
    pts = BCF.centreline()
    path = [Vector((p.x, p.y, BCF.band_bottom(p.x) + GAUGE_H / 2)) for p in pts]
    half_t = C.CRADLE_T / 2
    ob = L.ribbon("band_gauge_front", path, BCF.UP, [(GAUGE_H / 2, GAUGE_H / 2, half_t, half_t)] * len(path))
    return ob


PARTS = {
    "band_gauge_front": (front_gauge, L.ROT_NONE, ["print flat, 0.2 mm layers, SUPPORTS ON (build-plate only): the ribbon rises 12 mm at the forehead and its underside needs them; the head-fit gauge for the cradle, about 1.5 h against the cradle's eight",
                                                   "pass: level on the head, inner face touching at the temples, lower edge >= 4 mm above the ear tops",
                                                   "the rear halves twist below this height, so they have no gauge: their fit is the cradle wear test"]),
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
