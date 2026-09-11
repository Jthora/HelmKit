#!/usr/bin/env -S blender --background --python
"""
build_brow_rail.py -- vp0.8 brow rail with its nexus ring (left; --mirror for right).

A Ø44 ring (bore 32.3) that runs on the nexus spool between the spool's
thrust flange and a wave washer, with 24 radial Ø3.4 index holes in its rim
(15 deg tilt steps; a spring-loaded nail in the cradle's pin lug locks it),
and a 7 x 20 rail (root gusset 26 tall at the rim) leaving it at 13 deg above forward to s 90, where the LINK
half-laps onto it (two M3 x 10) and bends inboard behind the brow panel. A spring pawl slider in a tunnel along
the rail axis drops into the spool hub's notches; its thumb tab pokes out of the rail's top edge at r 37..39.
Print: lying on a side face. Qty: 1 L + 1 R.
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

NOTES = ["print lying on the inner (ring) face; no supports",
         "runs on the nexus spool; the pawl slider (insert from the bore, spring behind it) locks the tilt in 15 deg steps: pull the tab, swing, let go"]


def rail_frame(angle_deg, side):
    return Matrix.Translation((C.CX, 0.0, C.CZ)) @ Matrix.Rotation(-math.radians(angle_deg), 4, "Y")


def make(side=+1):
    od, idia, t = C.NEXUS_RING
    y0 = C.NEXUS_RING_Y0
    axis = "Y" if side > 0 else "-Y"
    ring = L.revolve("brow_rail", [(idia / 2.0, 0.0), (od / 2.0, 0.0), (od / 2.0, t), (idia / 2.0, t)], axis=axis, center=(C.CX, side * y0, C.CZ), segments=100)
    # gusset + bar as ONE polygon (radial s, tangential) extruded along Y at the bar's y
    a = math.radians(C.RAIL_ANGLE)
    h_ring, r_bar = C.RAIL_GUSSET
    s0 = od / 2.0 - 2.0
    hh = C.RAIL_H / 2.0
    poly = [(s0, -h_ring), (r_bar, -hh), (C.RAIL_S1, -hh), (C.RAIL_S1, hh), (r_bar, hh), (s0, h_ring)]
    Mg = Matrix.Translation((C.CX, 0.0, C.CZ)) @ Matrix.Rotation(-a, 4, "Y") @ Matrix.Rotation(-math.pi / 2.0, 4, "X")
    z0 = C.RAIL_Y0 if side > 0 else -(C.RAIL_Y0 + C.RAIL_T)
    L.union(ring, L.extrude_polygon("bar", poly, C.RAIL_T, Mg, z0=z0))
    Mr = rail_frame(C.RAIL_ANGLE, side)
    yc = side * (C.RAIL_Y0 + C.RAIL_T / 2.0)
    # half-lap for the link: the rail's INNER half goes over s 75..90; two M3 x 10 through the outer half, heads half-recessed
    lap0, lap1 = C.RAIL_LAP
    lt = C.BROW_LINK["lap_t"]
    L.cut(ring, L.add_box_local("lap", Mr, ((lap0 + lap1 + 1.0) / 2.0, side * (C.RAIL_Y0 + lt / 2.0 - 0.25), 0.0), (lap1 - lap0 + 1.0, lt + 0.5, C.RAIL_H + 2.0)))
    for s_b in C.RAIL_BOLTS_S:
        L.cut(ring, L.add_cyl_local("bolt", Mr, (s_b, yc, 0.0), C.M3_CLEAR_DIA / 2.0, C.RAIL_T + 4.0, axis="Y", verts=16))
        L.cut(ring, L.add_cyl_local("head", Mr, (s_b, side * (C.RAIL_Y0 + C.RAIL_T - 0.75 + 0.5), 0.0), 3.1, 2.5, axis="Y", verts=20))
    # pawl slider tunnel along the rail axis (opens into the bore), stem slot, thumb-tab slot through the top edge
    vp = C.VISOR_PAWL
    sy0 = vp["y0"]
    sw_y, sw_t = vp["slot"]
    ys = side * (sy0 + sw_y / 2.0)
    L.cut(ring, L.add_box_local("slot", Mr, ((vp["r_in"] + vp["r_spring"]) / 2.0, ys, 0.0), (vp["r_spring"] - vp["r_in"], sw_y, sw_t)))
    st_t, _ = vp["stem"]
    L.cut(ring, L.add_box_local("stemslot", Mr, ((vp["r_spring"] - 0.5 + vp["r_out"]) / 2.0, ys, 0.0), (vp["r_out"] - vp["r_spring"] + 0.5, sw_y, st_t)))
    ts0, ts1 = vp["tab_s"]
    L.cut(ring, L.add_box_local("tabslot", Mr, ((ts0 + ts1) / 2.0, ys, hh / 2.0 + 1.0), (ts1 - ts0, sw_y, hh + 4.0)))
    # LED cable groove along the underside (bottom tangential edge) of the bar, centred in the thickness; ends before the lap
    cd, cw, cs0, cs1 = C.RAIL_CHANNEL
    L.cut(ring, L.add_box_local("cablech", Mr, ((cs0 + cs1) / 2.0, yc, -hh - 1.0 + (cd + 1.0) / 2.0), (cs1 - cs0, cw, cd + 1.0)))
    pn = Mr @ Vector((60.0, side * (C.RAIL_Y0 + C.RAIL_T), hh))                  # v0.17 L/R notches on the bar's top outer edge
    L.lr_notches(ring, side, pn, Mr.to_3x3() @ Vector((1.0, 0.0, 0.0)))
    return ring


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    side = -1 if args.mirror else +1
    L.finalize_and_export(make(side), args.out, L.ROT_Y_TO_Z if side > 0 else L.ROT_NEGY_TO_Z, NOTES)
