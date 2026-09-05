#!/usr/bin/env -S blender --background --python
"""
build_brow_wing.py -- vp0.6 brow wing hinged on the cradle's temple node (left; --mirror for right).

Tenon (pinned into the centre panel) -> wing swept back ~41 deg with the top
bead -> knuckle block -> 6 mm tongue with a serrated hinge disc that sits in the
temple node's open-top slot (M3 along Y). The brow floats 18 mm in front of the
forehead, tilts against the detent and flips up over the crown.
Print: standing on the bottom face; small support under the hinge disc. Qty: 1 L + 1 R.
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

MP = L.frame(C.BROW_ORIGIN, C.BROW_EZ, C.BROW_EX)
PRINT_ROT = L.rot_dir_to(C.BROW_EZ, (0, 0, 1))
T, H, W = C.BROW_T, C.BROW_H, C.BROW_CENTER_W
NOTES = ["print standing on the bottom face; support only under the hinge disc",
         "--mirror for the right wing; tongue into the temple node slot (M3 + nyloc), tenon pins into the centre panel"]
KNUCKLE_LEN = 10.0


def hinge_local(side):
    hx, hy, hz = C.BROW_HINGE
    return MP.inverted() @ Vector((hx, side * hy, hz))


def make(side: int = +1):
    tx, tz, td = C.BROW_TENON
    wing = L.add_box_local("brow_wing", MP, (T / 2, side * (W / 2 - td / 2 + 0.25), tz / 2), (tx, td + 0.5, tz))
    h = hinge_local(side)
    x_end = h.x + 7.5                                      # body ends ~1.6 mm in front of the node's front face
    y_end = abs(h.y) - 2.5
    ang = math.atan2(y_end - W / 2, T / 2 - x_end)
    length = math.hypot(y_end - W / 2, T / 2 - x_end)
    Mw = MP @ Matrix.Translation((T / 2, side * W / 2, H / 2)) @ Matrix.Rotation(side * ang, 4, "Z")
    L.union(wing, L.add_box_local("body", Mw, (0.0, side * (length / 2 - 0.25), 0.0), (T, length + 0.5, H)))
    L.union(wing, L.add_cyl_local("bead", Mw, (0.0, side * (length / 2 - 0.25), H / 2), C.BROW_TOP_BEAD_R, length - 0.3, axis="Y", verts=32))
    L.cut(wing, L.add_box_local("hollow", Mw, (0.0, side * (length / 2 - 0.25), 0.0), (T - 2 * C.BROW_WALL - 1.0, length - 8.0, H - 2 * C.BROW_WALL - 4.0)))
    # knuckle in front of the node, neck + serrated disc into the slot
    kx0 = x_end
    L.union(wing, L.add_box_local("knuckle", MP, (kx0 + KNUCKLE_LEN / 2, side * (abs(h.y) - 1.5), h.z), (KNUCKLE_LEN, 11.0, 20.0)))
    tt = C.BROW_TONGUE_T
    L.union(wing, L.add_box_local("neck", MP, ((h.x - 2.0 + kx0 + 1.0) / 2, side * abs(h.y), h.z), (kx0 + 1.0 - (h.x - 2.0), tt, 14.0)))
    L.union(wing, L.add_cyl_local("disc", MP, (h.x, side * abs(h.y), h.z), C.BROW_DISC_R, tt, axis="Y", verts=48))
    L.fillet(wing, width=1.0)
    for d in C.BROW_TENON_PINS:
        L.cut(wing, L.add_cyl_local("tenonpin", MP, (T / 2, side * (W / 2 - d), tz / 2), C.PIN_DIA / 2, tz + 6.0, axis="Z", verts=24))
    hx, hy, hz = C.BROW_HINGE
    L.cut(wing, L.add_cyl("bolt", (hx, side * hy, hz), C.M3_CLEAR_DIA / 2, tt + 4.0, axis="Y", verts=24))
    sr = C.HINGE_SERR
    L.union(wing, L.serration_solid("serr", (hx, side * (hy + tt / 2), hz), (0.0, side, 0.0),
                                    r_in=sr["r_in"], r_out=sr["r_out"], teeth=sr["teeth"], height=sr["height"], phase_deg=sr["phase_tongue"]))
    return wing


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    L.finalize_and_export(make(-1 if args.mirror else +1), args.out, PRINT_ROT, NOTES)
