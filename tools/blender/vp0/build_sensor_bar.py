#!/usr/bin/env -S blender --background --python
"""
build_sensor_bar.py -- vp0.12 combat-trim sensor bar (--out-dir): the padded brow bar that replaces the visor panel for sparring.

A hollow curved bar (24 x 20 section, 2 mm chamfers) hugging the band's outer front face 0.3 mm off the spine cover, z 48..68.
Floor (4 mm): a window with a flush 1.5 mm recess for the sensor CARRIER (camera head, MLX90614 thermopile, two IR LEDs),
screwed from below with two M3 x 8 into taps that break into the cavity; two Ø4 cable holes at the ends of the recess;
an LED pacer lane (5.5 x 2.2) along the front edge of the underside. Back wall: two Ø4 printed PINS into sockets in the band
(the shear fuse) and one M3 x 8 thread-forming at the centre, driven through the window before the carrier goes in.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_cradle_front as CF
from mathutils import Matrix, Vector  # type: ignore

T2 = C.CRADLE_T / 2
SB = C.SENSOR_BAR


def _pts():
    return CF.centreline()


def arc_ribbon(name, half_arc, z0, z1, n0, n1, chamfer=0.0):
    """Ribbon along the front arc for |s| <= half_arc, z0..z1, normal band n0..n1 OUTBOARD of the band centreline."""
    run = CF.front_run(_pts(), half_arc)
    d = (n0 + n1) / 2
    pts = [Vector((p.x, p.y, (z0 + z1) / 2)) for p in CF.offset_outboard(run, d)]
    h = (z1 - z0) / 2; t = (n1 - n0) / 2
    return L.ribbon(name, pts, CF.UP, [(h, h, t, t)] * len(pts), chamfer=chamfer)


def arc_frame(s_, z):
    wide = CF.front_run(_pts(), SB["half_arc"] + 10.0)
    p, Tv, N = CF.arc_point(wide, s_)
    return L.frame(Vector((p.x, p.y, z)), N, Tv), N          # local x along the arc, y up, z inboard


def z_cyl_at(name, s_, n_out, r, z0, z1, verts=24):
    """Vertical cylinder at arc position s_, n_out outboard of the band centreline."""
    M, N = arc_frame(s_, (z0 + z1) / 2)
    return L.add_cyl_local(name, M, (0.0, 0.0, -n_out), r, z1 - z0, axis="Y", verts=verts)


def bar():
    n0 = T2 + SB["standoff"]; n1 = n0 + SB["n"]
    z0 = SB["z"] - SB["w"] / 2; z1 = SB["z"] + SB["w"] / 2
    b = arc_ribbon("sensor_bar", SB["half_arc"], z0, z1, n0, n1, chamfer=SB["chamfer"])
    L.cut(b, arc_ribbon("cavity", SB["cavity_arc"], z0 + SB["floor"], z1 - SB["wall"], n0 + SB["wall"], n1 - SB["wall"]))
    wa, wn0, wn1 = SB["window"]
    L.cut(b, arc_ribbon("window", wa, z0 - 2.0, z0 + SB["floor"] + 0.5, wn0, wn1))
    ra, rn0, rn1, rd = SB["recess"]
    L.cut(b, arc_ribbon("recess", ra, z0 - 2.0, z0 + rd, rn0, rn1))
    ga, gn0, gn1, gd = SB["led_groove"]
    L.cut(b, arc_ribbon("ledlane", ga, z0 - 2.0, z0 + gd, gn0, gn1))
    n_mid = (wn0 + wn1) / 2
    for s_ in SB["carrier_screws_s"]:
        L.cut(b, z_cyl_at("ctap", s_, n_mid, C.M3_TAP_DIA / 2, z0 - 2.0, z0 + SB["floor"] + 1.0, verts=16))
    es, ed, en, eh = SB["exit"]
    for s_ in (-es, es):                      # vertical exit slot down the back wall (opens toward the band): out of the bar's bottom, under the band edge
        L.cut(b, z_cyl_at("exit", s_, en, ed / 2, z0 - 2.0, z0 + eh, verts=20))
    pd, pl_band, pl_total = SB["pin"]
    for s_ in SB["pins_s"]:
        M, N = arc_frame(s_, SB["screw_z"])
        p = Vector((M[0][3], M[1][3], M[2][3]))
        L.cut(b, CF.normal_cyl("pinsock", p, N, (pd + 0.3) / 2, -(n0 - 1.0), -(n0 + (pl_total - pl_band) + 0.5), verts=20))
    M, N = arc_frame(0.0, SB["screw_z"])
    p = Vector((M[0][3], M[1][3], M[2][3]))
    L.cut(b, CF.normal_cyl("screw", p, N, C.M3_CLEAR_DIA / 2, -(n0 - 1.0), -(n0 + SB["wall"] + 1.0)))
    return b


def carrier():
    ca, cn0, cn1, ct = SB["carrier"]
    z0 = SB["z"] - SB["w"] / 2
    c = arc_ribbon("bar_carrier", ca, z0, z0 + ct, cn0, cn1)
    n_mid = (cn0 + cn1) / 2
    s_t, d_t = SB["thermopile"]
    L.cut(c, z_cyl_at("thermopile", s_t, n_mid, d_t / 2, z0 - 1.0, z0 + ct + 1.0, verts=32))
    s_c, d_c = SB["camera"]
    M, N = arc_frame(s_c, z0 + ct / 2)
    L.cut(c, L.add_box_local("camera", M, (0.0, 0.0, -n_mid), (d_c, ct + 2.0, d_c)))
    for s_, d_ in SB["ir_leds"]:
        L.cut(c, z_cyl_at("irled", s_, n_mid, d_ / 2, z0 - 1.0, z0 + ct + 1.0, verts=16))
    for s_ in SB["carrier_screws_s"]:
        L.cut(c, z_cyl_at("cscrew", s_, n_mid, C.M3_CLEAR_DIA / 2, z0 - 1.0, z0 + ct + 1.0, verts=16))
    return c


def pin():
    pd, pl_band, pl_total = SB["pin"]
    return L.add_cyl("bar_pin", (0.0, 0.0, pl_total / 2), pd / 2, pl_total, axis="Z", verts=32)


def pins_in_place():
    """Both pins posed in the band sockets (assembly use)."""
    out = []
    pd, pl_band, pl_total = SB["pin"]
    for s_ in SB["pins_s"]:
        M, N = arc_frame(s_, SB["screw_z"])
        ob = L.add_cyl_local("bar_pin", M, (0.0, 0.0, -(T2 - pl_band + pl_total / 2)), pd / 2, pl_total, axis="Z", verts=32)
        out.append(ob)
    return out


PARTS = {
    "sensor_bar": (bar, L.ROT_NONE, ["print on its bottom face (curved footprint), brim; the top wall bridges the 20 mm cavity",
                                     "carrier screws into the flush recess from below (two M3 x 8); LED lane along the front edge of the underside; two printed pins + one M3 x 8 (through the window, before the carrier) into the band's outer face; cables drop through the Ø3.5 holes in the back wall's foot into the band's bottom-face channel"]),
    "bar_carrier": (carrier, L.ROT_NONE, ["print flat; MLX90614 can in the round hole, camera head in the square, two IR LEDs in the small holes (eye-safe current budget measured first)"]),
    "bar_pin": (pin, L.ROT_NONE, ["print x2 standing; the sparring fuse: shears before the neck does"]),
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
