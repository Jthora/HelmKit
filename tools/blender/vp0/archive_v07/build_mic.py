#!/usr/bin/env -S blender --background --python
"""
build_mic.py -- vp0.7 microphone boom (--out-dir): boom block + capsule cup.

boom  8 mm peg up into the temple node's bottom socket (M3 cross-bolt), a
      block under the node with a Ø6.4 bore angled 35 deg forward-down for a
      gooseneck or a stiff cable run to the mouth. Fits either side.
cup   Ø13 cup for a 9.7 mm electret capsule with a Ø6.4 socket for the boom.
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

SX, SY = C.TEMPLE_SOCKET
Z_BOT = C.CRADLE_Z + C.TEMPLE_NODE_W[0]     # 40 node bottom


def bore_frame(side=+1):
    a = math.radians(C.MIC_BORE_ANGLE)
    bx, by, bz = C.MIC_BLOCK
    return L.frame((SX, side * SY, Z_BOT - bz / 2), (math.sin(a), 0.0, -math.cos(a)), (1.0, 0.0, 0.0))


def boom(side=+1):
    bx, by, bz = C.MIC_BLOCK
    part = L.add_box("mic_boom", (SX, side * SY, Z_BOT - bz / 2 - 0.5), (bx, by, bz + 1.0))
    L.fillet(part, width=1.0)
    L.union(part, L.add_cyl("peg", (SX, side * SY, Z_BOT + C.CYL_PEG_LEN / 2 - 0.5), C.CYL_PEG_D / 2, C.CYL_PEG_LEN + 1.0, axis="Z", verts=48))
    L.cut(part, L.add_cyl("cross", (SX, side * SY, Z_BOT + C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2, C.CYL_PEG_D + 4.0, axis="Y", verts=24))
    L.cut(part, L.add_cyl_local("bore", bore_frame(side), (0.0, 0.0, 6.0), C.MIC_BORE_D / 2, 14.0, axis="Z", verts=24))
    L.cut(part, L.add_cyl_local("grub", bore_frame(side), (0.0, 0.0, 4.0), C.M3_TAP_DIA / 2, by + 4.0, axis="Y", verts=12))   # M3 grub to clamp the neck
    return part


def cup():
    od, idia, depth = C.MIC_CUP
    c = L.add_cyl("mic_cup", (0.0, 0.0, (depth + 6.0) / 2), od / 2, depth + 6.0, axis="Z", verts=48)
    L.fillet(c, width=0.8)
    L.cut(c, L.add_cyl("pocket", (0.0, 0.0, 6.0 + depth / 2 + 1.0), idia / 2, depth + 2.0, axis="Z", verts=48))
    L.cut(c, L.add_cyl("socket", (0.0, 0.0, 3.0 - 1.0), C.MIC_BORE_D / 2, 8.0, axis="Z", verts=24))
    L.cut(c, L.add_cyl("grub", (0.0, 0.0, 3.5), C.M3_TAP_DIA / 2, od + 2.0, axis="X", verts=12))
    return c


PARTS = {
    "mic_boom": (lambda: boom(+1), L.ROT_NONE, ["print peg up (block on the bed); no supports", "M3 grub clamps the gooseneck; fits either temple socket"]),
    "mic_cup": (cup, L.ROT_NONE, ["print open end up; capsule 9.7 mm; M3 grub on the neck"]),
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
