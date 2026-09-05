#!/usr/bin/env -S blender --background --python
"""
build_brow_wing.py -- vp0.5 brow wing with integral spar (left; --mirror for right).

Tenon (pinned into the centre panel) -> 54 mm wing swept back 20 deg with the
top bead -> 20 x 12 spar along the panel normal -> rounded 10 mm post into the
pod's front port (nail-pinned there). One piece from panel to pod.
Print: standing on the bottom face, spar and post lying on the bed. Qty: 1 L + 1 R.
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
WING = math.radians(C.BROW_WING_ANGLE)
NOTES = ["print standing on the bottom face; no supports (spar and post rest on the bed)",
         "--mirror for the right wing; post pins into the pod front port, tenon pins into the centre panel"]


def mouth_local(side):
    """Pod front-port mouth in panel coordinates."""
    Mm = L.pod_port_frame(C.FRONT_PORT_ANGLE, side)
    pm = Vector((Mm[0][3], Mm[1][3], Mm[2][3]))
    return MP.inverted() @ pm


def make(side: int = +1):
    tx, tz, td = C.BROW_TENON
    wing = L.add_box_local("brow_wing", MP, (T / 2, side * (W / 2 - td / 2 + 0.25), tz / 2), (tx, td + 0.5, tz))
    Mw = MP @ Matrix.Translation((T / 2, side * W / 2, H / 2)) @ Matrix.Rotation(side * WING, 4, "Z")
    L.union(wing, L.add_box_local("body", Mw, (0.0, side * (C.BROW_WING_LEN / 2 - 0.25), 0.0), (T, C.BROW_WING_LEN + 0.5, H)))
    L.union(wing, L.add_cyl_local("bead", Mw, (0.0, side * (C.BROW_WING_LEN / 2 - 0.25), H / 2), C.BROW_TOP_BEAD_R, C.BROW_WING_LEN - 0.3, axis="Y", verts=32))
    # hollow the wing body (sealed cavity, 2 mm walls): saves ~30 g per wing
    L.cut(wing, L.add_box_local("hollow", Mw, (0.0, side * (C.BROW_WING_LEN / 2 - 0.25), 0.0), (T - 2 * C.BROW_WALL - 1.0, C.BROW_WING_LEN - 8.0, H - 2 * C.BROW_WALL - 4.0)))
    # spar from inside the wing end to the pod mouth, then the post into the socket
    m = mouth_local(side)
    e = Vector((T / 2 - C.BROW_WING_LEN * math.sin(WING), side * C.POD_PORT_Y, C.BROW_STRUT_LOCAL_Z))
    sz, sy = C.BROW_SPAR
    x_in = e.x + 4.0
    spar_len = x_in - m.x
    L.union(wing, L.add_box_local("spar", MP, ((x_in + m.x) / 2, e.y, (e.z + sz / 2) / 2), (spar_len, sy, e.z + sz / 2)))
    Mpost = L.frame(MP @ Vector((m.x, e.y, e.z)), Vector(C.BROW_EX), (0.0, side, 0.0))   # mouth frame, z outward = +ex
    L.union(wing, L.rounded_post("post", Mpost, C.PORT_PLUG_LEN + 1.0, -C.PORT_PLUG_LEN))
    L.fillet(wing, width=1.0)
    L.cut(wing, L.add_cyl_local("pin", Mpost, (0.0, 0.0, -C.PORT_PIN_DEPTH), C.PIN_DIA / 2, C.PORT_SQ + 6.0, axis="X", verts=24))
    for d in C.BROW_TENON_PINS:
        L.cut(wing, L.add_cyl_local("tenonpin", MP, (T / 2, side * (W / 2 - d), tz / 2), C.PIN_DIA / 2, tz + 6.0, axis="Z", verts=24))
    return wing


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    L.finalize_and_export(make(-1 if args.mirror else +1), args.out, PRINT_ROT, NOTES)
