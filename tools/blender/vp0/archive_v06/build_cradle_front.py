#!/usr/bin/env -S blender --background --python
"""
build_cradle_front.py -- vp0.6 cradle front U: forehead band, side bars, temple + rear nodes.

30 x 5 chamfered ribbon in the horizontal plane z = 55 (band z 40..70, above the
ears) from the left rear node around the forehead to the right rear node. Solid
nodes on the band: the temple nodes carry the brow hinge (open-top clevis slot,
serrated outer ear, M3) and the front pod bracket (M3 + nail); the rear nodes
hang 18 mm below the band, take the rear half's tenon (nail through node and
tenon) and the rear pod bracket. Rope spine groove on the inner face, cable
groove in the top edge, strap slot pairs behind the temple nodes. Foam blocks
velcro to the inner face.
Print: upside down (top edge and node tops on the bed), PETG. Qty: 1.
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

UP = Vector((0.0, 0.0, 1.0))
PRINT_ROT = L.ROT_FLIP
NOTES = ["print upside down (top edge and node tops on the bed); PETG; no supports (6.9 mm bridges over the brow slots)",
         f"brow hinge: {C.HINGE_BOLT} along Y through the temple node; head under the temple foam, nyloc in the bracket's pocket",
         f"rear halves: tenon into the rear node, {C.PIN_DIA} mm nail through node and tenon along Y, epoxy",
         f"spine groove {C.SPINE_GROOVE} on the inner face (rope + epoxy, three segments); cable groove {C.CABLE_GROOVE} in the top edge",
         "foam: forehead 70x26x10, sides 40x26x10, 6 mm under the nodes; velcro"]
H2, T2 = C.CRADLE_H / 2, C.CRADLE_T / 2
NODE_Y = (C.NODE_IN_Y + C.NODE_OUT_Y) / 2
NODE_T = C.NODE_OUT_Y - C.NODE_IN_Y


def centreline():
    left = list(C.CRADLE_WAYPOINTS)
    right = [(x, -y) for (x, y) in reversed(left[:-1])]
    samp = L.catmull_rom(left + right, samples_per_seg=16)
    return L.resample_polyline([Vector((x, y, C.CRADLE_Z)) for (x, y) in samp], 2.0)


def node_frame(x, side):
    """Local X = +x (along the band), Y = +y, Z = up (W)."""
    return L.frame((x, side * NODE_Y, C.CRADLE_Z), UP, (1.0, 0.0, 0.0))


def tenon_frame(side):
    """Rear-half tenon frame at the rear node's rear face: u = into the node (forward-up along the
    rear half), v = up the rear half (W_r), w = +/-Y."""
    o = Vector((C.REAR_START[0], side * C.REAR_START[1], C.REAR_START[2]))
    return L.frame(o, (0.0, -side, 0.0), C.REAR_T_IN)


def tenon_poly(clear=0.0, side=+1):
    """(u, v) outline: full band height at the mouth, symmetric taper to the tip so the tenon stays inside
    the node and the rotated right half matches the same slot."""
    t, mouth_h, depth, tip = C.CRADLE_TENON
    h = mouth_h / 2 + clear
    return [(-1.0, -h), (depth + clear, -(tip + clear)), (depth + clear, tip + clear), (-1.0, h)]


def node_box(name, x, side, w_range, grow=0.0):
    w0, w1 = w_range
    return L.add_box_local(name, node_frame(x, side), (0.0, 0.0, (w0 + w1) / 2), (C.NODE_LEN + grow, NODE_T + grow, w1 - w0))


def make():
    pts = centreline()
    band = L.ribbon("cradle_front", pts, UP, [(H2 - 0.1, H2, T2, T2)] * len(pts), chamfer=1.0)   # top 0.1 below the node tops
    # rope spine groove on the inner (+N) face; cable groove in the top edge, outer half
    gw, gd = C.SPINE_GROOVE
    gpts = [p + UP * C.SPINE_W for p in pts]
    L.cut(band, L.ribbon("spine", gpts, UP, [(gw / 2, gw / 2, T2 + 1.0, -(T2 - gd))] * len(gpts)))
    cw, cd = C.CABLE_GROOVE
    cpts = [p + UP * (H2 - cd / 2) for p in pts]
    L.cut(band, L.ribbon("cable", cpts, UP, [(cd / 2 + 1.0, cd / 2, 0.9, 1.3)] * len(cpts)))
    for side in (+1, -1):
        w0, w1 = C.NODE_W
        for nb in (node_box("tnode", C.TEMPLE_NODE_X, side, (w0 - 0.2, w1)), node_box("rnode", C.REAR_NODE_X, side, C.REAR_NODE_W)):
            L.fillet(nb, width=1.0)          # round the box before the union; the ribbon is chamfered by construction
            L.union(band, nb)
    for side in (+1, -1):
        Mt = node_frame(C.TEMPLE_NODE_X, side)
        # brow hinge: open-top slot from the front face, bolt along Y, serrated outer ear
        sd = C.BROW_SLOT_DEPTH
        L.cut(band, L.add_box_local("bslot", Mt, (C.NODE_LEN / 2 - sd / 2 + 1.0, 0.0, (-5.0 + 17.0) / 2), (sd + 2.0, C.HINGE_SLOT_W, 22.0)))
        hx, hy, hz = C.BROW_HINGE
        L.cut(band, L.add_cyl("bbolt", (hx, side * NODE_Y, hz), C.M3_CLEAR_DIA / 2, NODE_T + 4.0, axis="Y", verts=24))
        L.cut(band, L.add_cyl("bhead", (hx, side * (C.NODE_IN_Y + 0.6), hz), 3.3, 3.2, axis="Y", verts=24))
        # bracket bolt + nail through the temple and rear nodes (along Y)
        for (x, w) in C.FRONT_BRACKET_HOLES + C.REAR_BRACKET_HOLES:
            L.cut(band, L.add_cyl("bh", (x, side * NODE_Y, C.CRADLE_Z + w), C.M3_CLEAR_DIA / 2, NODE_T + 4.0, axis="Y", verts=24))
        # rear-half tenon slot + nail through node and tenon
        t = C.CRADLE_TENON[0] + 0.4
        L.cut(band, L.extrude_polygon("tslot", tenon_poly(0.2, side), t, tenon_frame(side), z0=-t / 2))
        pz = C.REAR_START[2] + 6.0 * C.REAR_T_IN[2]
        L.cut(band, L.add_cyl("tpin", (C.TENON_PIN_X, side * NODE_Y, pz), C.PIN_DIA / 2 + 0.1, NODE_T + 4.0, axis="Y", verts=24))
        L.cut(band, L.add_cyl("tpinhead", (C.TENON_PIN_X, side * (C.NODE_IN_Y + 0.1), pz), C.PIN_HEAD_DIA / 2, C.PIN_HEAD_DEPTH + 2.0, axis="Y", verts=24))
        # strap slots behind the temple node, through the band
        sh, sw = C.STRAP_SLOT
        for x in C.CRADLE_STRAP_X:
            L.cut(band, L.add_box("strap", (x, side * C.CRADLE_SIDE_Y, C.CRADLE_Z + 4.5), (sw, C.CRADLE_T + 2.0, sh)))
    for side in (+1, -1):
        hx, hy, hz = C.BROW_HINGE
        sr = C.HINGE_SERR
        L.union(band, L.serration_solid("serr", (hx, side * (hy + C.HINGE_SLOT_W / 2), hz), (0.0, -side, 0.0),
                                        r_in=sr["r_in"], r_out=sr["r_out"], teeth=sr["teeth"], height=sr["height"], phase_deg=sr["phase_ear"]))
    return band


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
