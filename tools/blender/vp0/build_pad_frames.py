#!/usr/bin/env -S blender --background --python
"""
build_pad_frames.py -- vp0.12 pad frames (--out-dir): printed sensor carriers that replace the plain foam blocks.

  pad_front      curved 2 mm plate on the band's inner front face with three windows; 8 mm foam glues to its head side
  carrier_ppg    drops into the centre window from the head side (plug + flange, epoxied): pocket for the MAX30102 module
  carrier_eda    the two side windows (x2): shallow recess for a conductive-fabric EDA patch
  pad_hub_L/R    flat plate on the hub node's inner face: bone-conduction transducer seat, coil-cable hole, cross-bolt clearance
  pad_rear_L/R   flat plate on the rear node's inner face: MAX30205 pocket pillar (occipital skin temperature), cross-bolt clearance
Every frame is held by two M3 x 8 thread-forming screws from the head side (heads under the foam) into taps in the cradle.
Cables run on the head side of the plates under the foam, as before.
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
PT = C.PAD_FRAME["plate_t"]
GAP = C.PAD_FRAME["gap"]


def mirror_if(ob, side):
    if side < 0:
        ob.matrix_world = Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)) @ ob.matrix_world
        L.apply_transform(ob)
        L.recalc_normals(ob)
    return ob


def plug_dims(spec):
    fw, fh, pw, ph, pd = spec
    ins = C.PAD_FRONT["plug_inset"]
    return fw - 2 * ins, fh - 2 * ins


def front_plate():
    pf = C.PAD_FRONT
    pts = CF.centreline()
    run = CF.front_run(pts, pf["half_arc"])
    d_c = T2 + GAP + PT / 2                                   # plate centre, inboard of the band centreline
    pts_pl = [Vector((p.x, p.y, pf["z"])) for p in CF.offset_outboard(run, -d_c)]
    plate = L.ribbon("pad_front", pts_pl, CF.UP, [(pf["h"] / 2, pf["h"] / 2, PT / 2, PT / 2)] * len(pts_pl), chamfer=pf["chamfer"])
    wide = CF.front_run(pts, pf["half_arc"] + 10.0)
    for s_, kind in pf["windows"]:
        pw, ph = plug_dims(pf["carrier_ppg"] if kind == "ppg" else pf["carrier_eda"])
        p, Tv, N = CF.arc_point(wide, s_)
        M = L.frame(Vector((p.x, p.y, pf["z"])), N, Tv)      # local x along the arc, y up, z inboard
        L.cut(plate, L.add_box_local(f"win_{kind}", M, (0.0, 0.0, d_c), (pw + 0.3, ph + 0.3, PT + 2.0)))
    csk_d, csk_depth = C.PAD_FRAME["countersink"]
    for s_ in pf["screws_s"]:
        p, Tv, N = CF.arc_point(wide, s_)
        q = Vector((p.x, p.y, pf["screw_z"]))
        L.cut(plate, CF.normal_cyl("screw", q, N, C.M3_CLEAR_DIA / 2, d_c - 2.0, d_c + 2.0))
        # 90-deg countersink opening on the head-side (inboard) face: wide end inboard
        face = d_c + PT / 2
        M = L.frame(q, N, (0.0, 0.0, 1.0))
        L.cut(plate, L.add_cone_local("csk", M, (0.0, 0.0, face - csk_depth + (csk_depth + 0.5) / 2), C.M3_CLEAR_DIA / 2 + 0.1, csk_d / 2 + 0.5, csk_depth + 0.5, axis="Z", verts=24))
    return plate


def _carrier(name, spec):
    """Local z = inboard (toward the head). plug z -PT..0 (in the plate window), flange 0..ft, tower to 1 mm under the foam surface."""
    fw, fh, pw, ph, pd = spec
    pf = C.PAD_FRONT
    ft, wall = pf["flange_t"], pf["wall"]
    plug_w, plug_h = plug_dims(spec)
    tower_h = pf["foam_t"] - pf.get("tower_under", 1.0) - ft
    body = L.add_box(name, (0.0, 0.0, ft / 2), (fw, fh, ft))
    L.union(body, L.add_box("plug", (0.0, 0.0, -PT / 2 + 0.05), (plug_w, plug_h, PT + 0.1)))
    L.union(body, L.add_box("tower", (0.0, 0.0, ft + tower_h / 2 - 0.05), (pw + 2 * wall, ph + 2 * wall, tower_h + 0.1)))
    z_top = ft + tower_h
    L.cut(body, L.add_box("pocket", (0.0, 0.0, z_top - pd / 2 + 0.5), (pw, ph, pd + 1.0)))
    L.cut(body, L.add_box("notch", (0.0, -ph / 2 - wall / 2, z_top - pd / 2 + 0.5), (4.0, wall + 1.0, pd + 1.0)))   # cable exit through the bottom wall
    return body


def carrier_ppg():
    return _carrier("carrier_ppg", C.PAD_FRONT["carrier_ppg"])


def carrier_eda():
    return _carrier("carrier_eda", C.PAD_FRONT["carrier_eda"])


def _plate(name, spec, side):
    x0, x1 = spec["x"]; z0, z1 = spec["z"]
    y_c = C.NODE_IN_Y - GAP - PT / 2
    pl = L.add_box(name, ((x0 + x1) / 2, y_c, (z0 + z1) / 2), (x1 - x0, PT, z1 - z0))
    L.fillet(pl, width=0.6)
    return pl, y_c, C.NODE_IN_Y - GAP - PT       # plate, its mid-plane y, its head-side face y


def _pillar_pocket(pl, y_in, ft, wall, spec):
    """Rectangular pillar (ft tall on the head side) with a pocket opening toward the skin and a cable notch through its bottom wall."""
    tw, th, td, tx, tz = spec
    L.union(pl, L.add_box("tpillar", (tx, y_in - ft / 2 + 0.05, tz), (tw + 2 * wall, ft + 0.1, th + 2 * wall)))
    L.cut(pl, L.add_box("tpocket", (tx, y_in - ft + td / 2 - 0.5, tz), (tw, td + 1.0, th)))
    L.cut(pl, L.add_box("tnotch", (tx, y_in - ft + td / 2 - 0.5, tz - th / 2 - wall / 2), (4.0, td + 1.0, wall + 1.0)))


def _holes(pl, y_c, spec):
    csk_d, csk_depth = C.PAD_FRAME["countersink"]
    y_in = y_c - PT / 2                                 # head-side face (side +1 build; mirrored later)
    for (x, z) in spec["screws"]:
        L.cut(pl, L.add_cyl("screw", (x, y_c, z), C.M3_CLEAR_DIA / 2, PT + 4.0, axis="Y", verts=16))
        # 90-deg countersink: wide end (r csk_d/2 + 0.5) 0.5 outside the head face, narrowing to the hole at csk_depth
        L.cut(pl, L.add_cone("csk", (x, y_in - 0.5 + (csk_depth + 0.5) / 2, z), csk_d / 2 + 0.5, C.M3_CLEAR_DIA / 2 + 0.1, csk_depth + 0.5, axis="Y", verts=24))
    for key in ("cable", "cross"):
        if key in spec:
            d, x, z = spec[key]
            L.cut(pl, L.add_cyl(key, (x, y_c, z), d / 2, PT + 4.0, axis="Y", verts=24))
    if "bolt_relief" in spec:                           # shallow recesses on the band-side face over the nexus bolt tips
        rd, rdep = spec["bolt_relief"]
        y_out = y_c + PT / 2
        for (x, z) in C.NEXUS_BOLTS:
            L.cut(pl, L.add_cyl("brelief", (x, y_out - rdep + (rdep + 1.0) / 2, z), rd / 2, rdep + 1.0, axis="Y", verts=24))


def hub(side=+1):
    ph = C.PAD_HUB
    pl, y_c, y_in = _plate("pad_hub", ph, side)
    ft = ph["foam_t"]
    bd, bt, br, bx, bz = ph["bct"]
    L.union(pl, L.add_cyl("bpillar", (bx, y_in - ft / 2 + 0.05, bz), bd / 2, ft + 0.1, axis="Y", verts=48))
    L.cut(pl, L.add_cyl("bseat", (bx, y_in - ft + br / 2 - 0.5, bz), bt / 2, br + 1.0, axis="Y", verts=48))
    L.cut(pl, L.add_box("bnotch", (bx, y_in - ft + br / 2 - 0.5, bz - bt / 2 - 0.5), (4.0, br + 1.0, 2.0)))
    _holes(pl, y_c, ph)
    L.lr_notches(pl, side, ((ph["x"][0] + ph["x"][1]) / 2, y_c, ph["z"][1]), (1.0, 0.0, 0.0), size=1.0, thru=(1, PT + 2.0))   # v0.17: one nick L, two R, through the top edge (cut before mirroring)
    return mirror_if(pl, side)


def rear(side=+1):
    pr = C.PAD_REAR
    pl, y_c, y_in = _plate("pad_rear", pr, side)
    _pillar_pocket(pl, y_in, pr["foam_t"], pr["wall"], pr["temp"])
    _holes(pl, y_c, pr)
    L.lr_notches(pl, side, (pr["x"][0], y_c, (pr["z"][0] + pr["z"][1]) / 2), (0.0, 0.0, 1.0), size=1.0, thru=(1, PT + 2.0))   # on the rear (-x) edge: the top edge sits over the cross-bolt clearance hole
    return mirror_if(pl, side)


def carrier_in_place(kind, s_):
    """A carrier posed in its plate window (assembly use)."""
    pf = C.PAD_FRONT
    ob = carrier_ppg() if kind == "ppg" else carrier_eda()
    wide = CF.front_run(CF.centreline(), pf["half_arc"] + 10.0)
    p, Tv, N = CF.arc_point(wide, s_)
    M = L.frame(Vector((p.x, p.y, pf["z"])), N, Tv) @ Matrix.Translation((0.0, 0.0, T2 + GAP + PT))
    ob.matrix_world = M @ ob.matrix_world
    L.apply_transform(ob)
    return ob


def foam_refs():
    """Reference foam bodies on the head side of each frame (not printed)."""
    out = {}
    pf = C.PAD_FRONT
    run = CF.front_run(CF.centreline(), pf["half_arc"])
    d_f = T2 + GAP + PT + pf["foam_t"] / 2
    pts_f = [Vector((p.x, p.y, pf["z"])) for p in CF.offset_outboard(run, -d_f)]
    out["foam_front"] = L.ribbon("foam_front", pts_f, CF.UP, [(pf["h"] / 2, pf["h"] / 2, pf["foam_t"] / 2, pf["foam_t"] / 2)] * len(pts_f))
    for side, tag in ((+1, "L"), (-1, "R")):
        ph, pr = C.PAD_HUB, C.PAD_REAR
        y_f = C.NODE_IN_Y - GAP - PT - ph["foam_t"] / 2
        out[f"foam_hub_{tag}"] = L.add_box("foam_hub", ((ph["x"][0] + ph["x"][1]) / 2, side * y_f, (ph["z"][0] + ph["z"][1]) / 2), (ph["x"][1] - ph["x"][0], ph["foam_t"], ph["z"][1] - ph["z"][0]))
        y_r = C.NODE_IN_Y - GAP - PT - pr["foam_t"] / 2
        out[f"foam_rear_{tag}"] = L.add_box("foam_rear", ((pr["x"][0] + pr["x"][1]) / 2, side * y_r, (pr["z"][0] + pr["z"][1]) / 2), (pr["x"][1] - pr["x"][0], pr["foam_t"], pr["z"][1] - pr["z"][0]))
    return out


PARTS = {
    "pad_front": (front_plate, L.ROT_NONE, ["print standing on its bottom edge (curved plate), brim; countersunk M3 x 8 from the head side; the three carriers plug into the windows from the head side (epoxy); 8 mm foam glues over it, cut around the towers"]),
    "carrier_ppg": (carrier_ppg, L.ROT_NONE, ["print plug down (1.5 mm flange overhang is fine); MAX30102 module in the pocket, optical window toward the skin, cable out through the bottom notch"]),
    "carrier_eda": (carrier_eda, L.ROT_NONE, ["print x2, plug down; glue a conductive-fabric patch into the recess; wire to the GSR module's tip and ring"]),
    "pad_hub_L": (lambda: hub(+1), L.ROT_NEGY_TO_Z, ["LEFT. print outer face down, seat up; countersunk M3 x 8 from the head side; put the three nexus nuts in the node pockets BEFORE this plate goes on (it captures them); the Ø5 recesses on the band face clear the bolt tips; the Ø7.5 hole clears the hub socket's cross-bolt nut or nail; bone-conduction transducer in the round seat; the coil cable passes the Ø5.4 hole"]),
    "pad_hub_R": (lambda: hub(-1), L.ROT_Y_TO_Z, ["RIGHT (mirrored). print outer face down, seat up"]),
    "pad_rear_L": (lambda: rear(+1), L.ROT_NEGY_TO_Z, ["LEFT. print outer face down, pillar up; countersunk M3 x 8; nail the rear-half tenon BEFORE this plate goes on (its edge crosses the nail head's counterbore); MAX30205 in the pocket (occipital skin); 4 mm foam; the Ø7.5 hole clears the rear socket's cross-bolt"]),
    "pad_rear_R": (lambda: rear(-1), L.ROT_Y_TO_Z, ["RIGHT (mirrored). print outer face down, pillar up"]),
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
