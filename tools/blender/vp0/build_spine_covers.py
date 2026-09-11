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
    hw = (w - C.SPINE["cover_clear"]) / 2
    return L.ribbon(name, CF.offset_outboard(run_ch, offset_out), CF.UP, [(hw, hw, t / 2, t / 2)] * len(run_ch))


def cover_front(run=None):
    run = run or cradle_runs()[1]
    return strip("cover_front", CF.channel_pts(run), C.CRADLE_T / 2 - C.SPINE["cover_t"] / 2, C.SPINE["w"], C.SPINE["cover_t"])


def cover_side(run=None):
    run = run or cradle_runs()[0]
    return strip("cover_side", CF.channel_pts(run), C.CRADLE_T / 2 - C.SPINE["cover_t"] / 2, C.SPINE["w"], C.SPINE["cover_t"])


def cover_rear():
    run = RB.spine_run(RB.centre_pts())
    pts = RB.spine_pts(run, C.REAR_T / 2 - C.SPINE["rear_cover_t"] / 2)
    hw = (C.SPINE["w"] - C.SPINE["cover_clear"]) / 2
    return L.ribbon("cover_rear", pts, RB.W, [(hw, hw, C.SPINE["rear_cover_t"] / 2, C.SPINE["rear_cover_t"] / 2)] * len(pts))


def cover_rear_in():
    """1 mm cover strip for the rear half's inner harness channel (v0.15)."""
    rc = C.REAR_CABLE
    pts = RB.centre_pts()
    run = [p for p in pts if p.x < RB.START.x - rc["s0"] - 1.0 and p.y > rc["y_end"] + 1.0]
    sgn = RB.outward_sign(run)
    out = []
    for i, p in enumerate(run):
        a = run[max(i - 1, 0)]; b = run[min(i + 1, len(run) - 1)]
        Tv = (b - a).normalized()
        N = Tv.cross(RB.W).normalized() * sgn
        out.append(p + RB.W * rc["v"] - N * (C.REAR_T / 2 - rc["cover_t"] / 2))
    hw = (rc["w"] - C.SPINE["cover_clear"]) / 2
    return L.ribbon("cover_rear_in", out, RB.W, [(hw, hw, rc["cover_t"] / 2, rc["cover_t"] / 2)] * len(out))


def cover_bottom(side=+1):
    """v0.17: 1 mm strip closing the band's bottom-face cable channel (the cable rides above it)."""
    cc = C.CABLE_CHANNEL
    pts = CF.centreline()
    s_end = CF.s_at_x(pts, cc["x_end"] - cc["overrun"] + 1.0, side)
    s_a, s_b = (s_end, -cc["s_start"] + 1.0) if side > 0 else (cc["s_start"] - 1.0, s_end)
    run = CF.arc_span(pts, s_a, s_b, x_min=30.0)
    t = C.SPINE["bottom_cover_t"]
    # printed FLAT (constant z) and bent into the channel: a 1 mm PETG strip follows the 12 mm rise easily; the assembly places it on the true path
    pts_c = [Vector((p.x, p.y, C.CRADLE_Z)) for p in run]
    hw = (cc["w"] - C.SPINE["cover_clear"]) / 2
    return L.ribbon("cover_bottom", pts_c, CF.UP, [(t / 2, t / 2, hw, hw)] * len(pts_c))


def cover_bottom_placed(side=+1):
    """The strip on its real path (for the assembly only)."""
    cc = C.CABLE_CHANNEL
    pts = CF.centreline()
    s_end = CF.s_at_x(pts, cc["x_end"] - cc["overrun"] + 1.0, side)
    s_a, s_b = (s_end, -cc["s_start"] + 1.0) if side > 0 else (cc["s_start"] - 1.0, s_end)
    run = CF.arc_span(pts, s_a, s_b, x_min=30.0)
    t = C.SPINE["bottom_cover_t"]
    pts_c = [Vector((p.x, p.y, CF.band_bottom(p.x) + t / 2)) for p in run]
    hw = (cc["w"] - C.SPINE["cover_clear"]) / 2
    return L.ribbon("cover_bottom", pts_c, CF.UP, [(t / 2, t / 2, hw, hw)] * len(pts_c))


PARTS = {
    "cover_front": (cover_front, L.ROT_NONE, ["print standing on its long edge, brim; PETG or PLA", "lay the 2 mm rope in the channel, fill with steel epoxy, press the strip in flush, wipe"]),
    "cover_side": (cover_side, L.ROT_NONE, ["print standing on its long edge; short span between the rear and hub nodes"]),
    "cover_rear": (cover_rear, L.rot_dir_to(RB.W, (0.0, 0.0, 1.0)), ["print standing on its long edge, brim; two identical (the right half is the left print turned over, so its cover is too)"]),
    "cover_bottom": (lambda: cover_bottom(+1), L.ROT_NONE, ["v0.17: 1 mm strip glued into the band's bottom-face cable channel over the cables; x2 (one flipped for the right side)"]),
    "cover_rear_in": (cover_rear_in, L.rot_dir_to(RB.W, (0.0, 0.0, 1.0)), ["v0.15: 1 mm strip over the rear half's inner harness channel, glued in over the cables; two identical"]),
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
