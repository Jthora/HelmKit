#!/usr/bin/env -S blender --background --python
"""
build_belt_pack.py -- vp0.15 belt pack (--out-dir): the off-helm box for the belt-only and both options.

A 105 x 70 x 40 box (100 x 65 x 35 inside) with a rebated lid on four M3 corner bosses, two belt slots through the back for a
45 mm belt, an Ø8 umbilical hole in one end with a zip-tie slot pair inside, and a USB window. Holds the Heltec (belt-only), a
2 x 18650 holder or a LiPo, the coil driver and a buck converter. Nothing in it is helm-specific: the umbilical's other end is
the nape core base's connector.
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C

BP = C.BELT_PACK


def make_box():
    iu, iv, iw = BP["inner"]
    wall, lt, reb, b = BP["wall"], BP["lid_t"], BP["rebate"], BP["boss"]
    ou, ov = iu + 2 * wall, iv + 2 * wall
    H = wall + iw
    box = L.add_box("belt_pack", (0.0, 0.0, H / 2), (ou, ov, H))
    L.fillet(box, width=BP["fillet"])
    L.cut(box, L.add_box("cav", (0.0, 0.0, wall + iw / 2 + 0.5), (iu, iv, iw + 1.0)))
    lip = BP["lip"]
    L.cut(box, L.add_box("rebate", (0.0, 0.0, H - reb / 2 + 0.5), (ou - 2 * lip, ov - 2 * lip, reb + 1.0)))
    for sx in (+1, -1):
        for sy in (+1, -1):
            cx, cy = sx * (iu / 2 - b / 2 + 0.3), sy * (iv / 2 - b / 2 + 0.3)
            L.union(box, L.add_box("boss", (cx, cy, wall + (iw - reb) / 2 - 0.05), (b, b, iw - reb + 0.1)))
            L.cut(box, L.add_cyl("ltap", (cx, cy, H - 5.0), C.M3_TAP_DIA / 2, 10.0, axis="Z", verts=12))
    # belt slots through the back (floor): two, at +/- y, sized for a 45 mm belt
    bw, bh, by = BP["belt"]
    for sy in (+1, -1):
        L.cut(box, L.add_box("belt", (0.0, sy * by, wall / 2), (bw, bh, wall + 2.0)))
    # umbilical hole in the +x end wall with a zip-tie slot pair either side inside
    ud, uz = BP["umbilical"]
    L.cut(box, L.add_cyl("umb", (iu / 2 + wall / 2, 0.0, wall + 12.0), ud / 2, wall + 2.0, axis="X", verts=24))
    for sy in (+1, -1):
        L.cut(box, L.add_box("zip", (iu / 2 - 6.0, sy * (ud / 2 + 3.0), wall / 2), (uz, 2.0, wall + 2.0)))
    uw, uh, ud_ = BP["usb"]
    L.cut(box, L.add_box("usb", (-iu / 2 - wall / 2, 0.0, wall + ud_), (wall + 2.0, uw, uh)))
    return box


def make_lid():
    iu, iv, iw = BP["inner"]
    wall, lt, reb, b = BP["wall"], BP["lid_t"], BP["rebate"], BP["boss"]
    ou, ov = iu + 2 * wall, iv + 2 * wall
    H = wall + iw
    lid = L.add_box("belt_pack_lid", (0.0, 0.0, H + lt / 2), (ou, ov, lt))
    lip = BP["lip"]
    L.union(lid, L.add_box("tongue", (0.0, 0.0, H - reb / 2 + 0.05), (ou - 2 * lip - 0.3, ov - 2 * lip - 0.3, reb + 0.1)))
    L.fillet(lid, width=0.8)
    for sx in (+1, -1):
        for sy in (+1, -1):
            cx, cy = sx * (iu / 2 - b / 2 + 0.3), sy * (iv / 2 - b / 2 + 0.3)
            L.cut(lid, L.add_cyl("lscrew", (cx, cy, H + lt / 2), C.M3_CLEAR_DIA / 2, lt + reb + 2.0, axis="Z", verts=16))
            L.cut(lid, L.add_cyl("lcsk", (cx, cy, H + lt + 0.5 - 0.6), 2.9, 1.2, axis="Z", verts=16))
    return lid


PARTS = {
    "belt_pack": (make_box, L.ROT_NONE, ["print open side up; no supports; belt through the two back slots; umbilical in the end hole with a zip tie across the inside slots"]),
    "belt_pack_lid": (make_lid, L.ROT_FLIP, ["print outer face down; four countersunk M3 x 8"]),
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
