#!/usr/bin/env -S blender --background --python
"""
build_pod_bracket.py -- vp0.6 pod-to-cradle brackets and the crown hinge plug (--out-dir).

Every pod hangs off the cradle on two rigid brackets, each a rounded 10 mm post
nail-pinned in a pod port with a lip on the ring surface and a 6 mm web plate
hanging inboard (y 97..103) that bolts to a cradle node (M3 + a nail in shear).
  bracket_front  13 deg port  -> temple node; pocket for the brow hinge nyloc
  bracket_rear   175 deg port -> rear node
  hinge_plug     90 deg port  -> clevis for the crown arch tongue (M3, serrated outer ear)
Webs are drawn in the port frame (13 deg skew to the node faces, cosmetic) so
every part prints standing on the post tip with no supports.
Qty: front L + R (--mirror), rear L + R, hinge plug x 2 (same STL).
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

WEB_X = (-(C.POD_PORT_Y - C.NODE_OUT_Y), -(C.POD_PORT_Y - C.NODE_OUT_Y) + C.BRACKET_ARM[2])   # local x: y 97..103
WEB_Z = (-C.PORT_PLUG_LEN, 11.0)                    # radial: post tip .. 11 outside the ring
FRONT_YT = (-5.0, 22.0)                             # tangential (up at 13 deg) range of the front web
REAR_YT = (-11.0, 16.0)                             # tangential (down at 175 deg) range of the rear web


def radial(angle):
    a = math.radians(angle)
    return Vector((math.cos(a), 0.0, math.sin(a)))


def _post_and_lip(name, M):
    part = L.rounded_post(name, M, C.PORT_PLUG_LEN + 1.0, -C.PORT_PLUG_LEN)
    ls, lt = C.HINGE_PLUG_LIP
    L.union(part, L.add_box_local("lip", M, (-1.0, 0.0, lt / 2), (ls + 2.0, ls, lt)))   # y 102..120 on the ring surface
    return part


def bracket(angle, side, yt, holes, nut_pocket=None):
    M = L.pod_port_frame(angle, side)
    name = "bracket_front" if angle < 90 else "bracket_rear"
    part = _post_and_lip(name, M)
    y0, y1 = yt if side > 0 else (-yt[1], -yt[0])
    L.union(part, L.add_box_local("web", M, ((WEB_X[0] + WEB_X[1]) / 2, (y0 + y1) / 2, (WEB_Z[0] + WEB_Z[1]) / 2),
                                  (WEB_X[1] - WEB_X[0], y1 - y0, WEB_Z[1] - WEB_Z[0])))
    L.fillet(part, width=0.8)
    L.cut(part, L.add_cyl_local("pin", M, (0.0, 0.0, -C.PORT_PIN_DEPTH), C.PIN_DIA / 2, C.PORT_SQ + 6.0, axis="X", verts=24))
    yw = side * (C.NODE_OUT_Y + C.BRACKET_ARM[2] / 2)
    for (x, w) in holes:
        L.cut(part, L.add_cyl("h", (x, yw, C.CRADLE_Z + w), C.M3_CLEAR_DIA / 2, C.BRACKET_ARM[2] + 2.0, axis="Y", verts=24))
    if nut_pocket:
        x, z = nut_pocket
        L.cut(part, L.add_cyl("nut", (x, side * (C.NODE_OUT_Y + 4.3 / 2 - 1.0), z), 3.5, 4.3 + 2.0, axis="Y", verts=24))
    return part


def front(side=+1):
    return bracket(C.FRONT_PORT_ANGLE, side, FRONT_YT, C.FRONT_BRACKET_HOLES, nut_pocket=(C.BROW_HINGE[0], C.BROW_HINGE[2]))


def rear(side=+1):
    return bracket(C.REAR_PORT_ANGLE, side, REAR_YT, C.REAR_BRACKET_HOLES)


def hinge_plug(side=+1):
    """Post + lip + clevis for the crown arch tongue: ears 6 thick, 30 wide, HINGE_PLUG_H tall; serrated outer ear."""
    M = L.pod_port_frame(90.0, side)
    part = _post_and_lip("hinge_plug", M)
    ls, lt = C.HINGE_PLUG_LIP
    g = C.HINGE_SLOT_W / 2
    et, eh = C.HINGE_PLUG_EAR_T, C.HINGE_PLUG_H
    for sx in (+1, -1):
        L.union(part, L.add_box_local("ear", M, (sx * (g + et / 2), 0.0, lt + eh / 2 - 0.5), (et, C.CROWN_W, eh + 1.0)))
    L.fillet(part, width=0.8)
    zb = C.CROWN_HINGE_Z - (C.CZ + C.DISH_R)
    L.cut(part, L.add_cyl_local("bolt", M, (0.0, 0.0, zb), C.M3_CLEAR_DIA / 2, 2 * (g + et) + 4.0, axis="X", verts=24))
    L.cut(part, L.add_cyl_local("pin", M, (0.0, 0.0, -C.PORT_PIN_DEPTH), C.PIN_DIA / 2, C.PORT_SQ + 6.0, axis="X", verts=24))
    sr = C.HINGE_SERR
    face = M @ Vector((g, 0.0, zb))
    L.union(part, L.serration_solid("serr", face, M.to_3x3() @ Vector((-1.0, 0.0, 0.0)),
                                    r_in=sr["r_in"], r_out=sr["r_out"], teeth=sr["teeth"], height=sr["height"], phase_deg=sr["phase_ear"]))
    return part


def print_rot(angle):
    return L.rot_dir_to(radial(angle), (0.0, 0.0, 1.0))


PARTS = {
    "bracket_front_L": (lambda: front(+1), print_rot(C.FRONT_PORT_ANGLE), ["print standing on the post tip and web edge; no supports", "13 deg port -> temple node: M3 + nail along Y; nyloc pocket for the brow hinge on the inner face"]),
    "bracket_front_R": (lambda: front(-1), print_rot(C.FRONT_PORT_ANGLE), ["mirror of bracket_front_L"]),
    "bracket_rear_L": (lambda: rear(+1), print_rot(C.REAR_PORT_ANGLE), ["print standing on the post tip and web edge; no supports", "175 deg port -> rear node: M3 + nail along Y"]),
    "bracket_rear_R": (lambda: rear(-1), print_rot(C.REAR_PORT_ANGLE), ["mirror of bracket_rear_L"]),
    "hinge_plug": (lambda: hinge_plug(+1), L.ROT_FLIP, ["print ears down, post up (6.9 mm bridge under the lip); no supports", f"crown arch tongue between the ears, {C.HINGE_BOLT}; nail-pin the post in the top port"]),
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
