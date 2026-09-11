#!/usr/bin/env -S blender --background --python
"""
build_spine_covers.py -- vp0.11 flush cover strips for the spine channels (--out-dir).

  cover_front  left half of the front arc (print 2, one mirrored: flip it over)
  cover_side   the short span between the rear and hub nodes (print 2)
  cover_rear   the rear half's span (print 2, one mirrored)
Each strip fills the outer 1.5 mm (1.0 on the rear halves) of a channel over a 2 mm rope potted in steel epoxy.
Print standing on the long edge (the strips are curved in plan); brim.
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_cradle_front as CF
import build_rear_band_half as RB
from mathutils import Matrix, Vector  # type: ignore


def cradle_runs():
    pts = CF.centreline()
    runs = CF.spine_runs(pts)
    left, front, right = runs[0], runs[1], runs[2]
    front_left = [p for p in front if p.y >= -0.01]
    return left, front_left, right


def strip(name, run_ch, offset_out, w, t):
    return L.ribbon(name, CF.offset_outboard(run_ch, offset_out), CF.UP, [(w / 2 - 0.05, w / 2 - 0.05, t / 2, t / 2)] * len(run_ch))


def cover_front(run=None):
    run = run or cradle_runs()[1]
    return strip("cover_front", CF.channel_pts(run), C.CRADLE_T / 2 - C.SPINE["cover_t"] / 2, C.SPINE["w"], C.SPINE["cover_t"])


def cover_side(run=None):
    run = run or cradle_runs()[0]
    return strip("cover_side", CF.channel_pts(run), C.CRADLE_T / 2 - C.SPINE["cover_t"] / 2, C.SPINE["w"], C.SPINE["cover_t"])


def cover_rear():
    run = RB.spine_run(RB.centre_pts())
    pts = RB.spine_pts(run, C.REAR_T / 2 - C.SPINE["rear_cover_t"] / 2)
    return L.ribbon("cover_rear", pts, RB.W, [(C.SPINE["w"] / 2 - 0.05, C.SPINE["w"] / 2 - 0.05, C.SPINE["rear_cover_t"] / 2, C.SPINE["rear_cover_t"] / 2)] * len(pts))


PARTS = {
    "cover_front": (cover_front, L.ROT_NONE, ["print standing on its long edge, brim; PETG or PLA", "lay the 2 mm rope in the channel, fill with steel epoxy, press the strip in flush, wipe"]),
    "cover_side": (cover_side, L.ROT_NONE, ["print standing on its long edge; short span between the rear and hub nodes"]),
    "cover_rear": (cover_rear, L.rot_dir_to(RB.W, (0.0, 0.0, 1.0)), ["print standing on its long edge, brim; one mirrored for the right half"]),
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
