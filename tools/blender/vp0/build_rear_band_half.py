#!/usr/bin/env -S blender --background --python
"""
build_rear_band_half.py -- vp0.6 rear band half: tenon into the rear node, rope spine, rack.

30 x 5 chamfered ribbon in a plane tilted ~49 deg (from behind the ear down to
the nape) leaving the cradle's rear node through a tapered tenon (nail through
node and tenon, epoxy), around the occiput to a 50 mm rack strip (module 1.25)
for the enclosed pull dial. Spine groove on the head-side face, cable groove in
the top edge, strap slot pair behind the node.
Print: top edge down (rack teeth up). Qty: 2 (same STL; right = rotated 180 deg
about the outward normal at the nape).
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

W = Vector(C.REAR_W)
T_IN = Vector(C.REAR_T_IN)
PRINT_ROT = L.rot_dir_to(W, (0.0, 0.0, -1.0))
NOTES = ["print with the planar top edge on the bed (rack teeth up); PETG; no supports; BRIM (a 5 mm ridge standing 36 mm)",
         f"tenon into the cradle's rear node: {C.PIN_DIA} mm nail along Y through node and tenon, epoxy",
         "strap slot pair 24 / 32 mm behind the node: rear leg of the chin strap"]
BACK = Vector((C.REAR_BACK_X, 0.0, C.REAR_BACK_Z))
N_OUT = Vector((-math.cos(math.radians(C.REAR_TILT)), 0.0, -math.sin(math.radians(C.REAR_TILT))))
START = Vector(C.REAR_START)
INSIDE = 8.0                       # the ribbon starts this far inside the node, then is trimmed to the node's rear face


def z_of(x):
    return START.z + (x - START.x) * math.tan(math.radians(C.REAR_TILT))


def centre_pts():
    s0 = START + T_IN * INSIDE
    wps = [(s0.x, s0.y), (START.x - 8.0, START.y - 0.5)] + list(C.REAR_WAYPOINTS[1:]) + [(C.REAR_BACK_X, C.RACK_Y0)]
    samp = L.catmull_rom(wps, samples_per_seg=16)
    return L.resample_polyline([Vector((x, y, z_of(x))) for (x, y) in samp], 2.0)


def spine_run(pts):
    """Exposed span of the rear half: from 2 mm behind the node's rear face to 8 mm short of the rack."""
    return [p for p in pts if p.x < START.x - 0.5 and p.y > C.RACK_Y0 + 8.0]   # to 0.5 short of the node's rear face (was 2.0): the rope end sits in the tenon joint's epoxy


def outward_sign(run):
    Tv = (run[1] - run[0]).normalized()
    return 1.0 if Tv.cross(W).dot(N_OUT) > 0 else -1.0


def spine_pts(run, offset_out):
    """Run shifted down the band by 6 (channel centre at v -6) and outward by `offset_out`."""
    sgn = outward_sign(run)
    out = []
    for i, p in enumerate(run):
        a = run[max(i - 1, 0)]; b = run[min(i + 1, len(run) - 1)]
        Tv = (b - a).normalized()
        N = Tv.cross(W).normalized() * sgn
        out.append(p + W * ((C.SPINE["rear_v"][0] + C.SPINE["rear_v"][1]) / 2) + N * offset_out)
    return out


def make(side=+1):
    pts = centre_pts()
    half = C.REAR_H / 2
    band = L.ribbon("rear_band_half", pts, W, [(half, half, C.REAR_T / 2, C.REAR_T / 2)] * len(pts), chamfer=1.0)
    # spine channel in the outer face (3 deep, 4 tall at v -8..-4) over the exposed span; the cover strip is a separate print
    run = spine_run(pts)
    sgn = outward_sign(run)
    d = C.SPINE["rear_d"]
    n_out, n_in = C.REAR_T / 2 + 1.0, d - C.REAR_T / 2
    # Track P: the half prints top edge down, so the groove's -W wall would face down: wedge it (see vp0lib.groove_section)
    sec = L.groove_section(face=sgn * C.REAR_T / 2, floor=sgn * (C.REAR_T / 2 - d), over=sgn * (C.REAR_T / 2 + 1.0), wh=C.SPINE["w"] / 2, depth=d)
    L.cut(band, L.ribbon("spinech", spine_pts(run, 0.0), W, None, section=sec))
    # strap slots through the band behind the node (first: the solver likes them on the plain ribbon)
    sh, sw = C.STRAP_SLOT
    for s in C.REAR_STRAP_S:
        i = L.arc_index_range(pts, INSIDE + s, 0.0)[0]
        Tv = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        Ms = L.frame(pts[i] + Tv * 0.45, W, Tv)          # off the 2 mm station grid: no cutter face on a ribbon ring
        L.cut(band, L.add_box_local("strap", Ms, (0.0, 0.0, 4.5), (sw + 0.3, C.REAR_T + 2.0, sh)))
        L.slot_chamfer(band, Ms @ Matrix.Translation((0.0, 0.0, 4.5)), sw + 0.3, sh, C.REAR_T, C.STRAP_SLOT_CHAMFER)
    # trim to the node's rear face, then add the tapered tenon (4.8 thick: 0.1 inside the band faces)
    # v0.15 harness channel on the INNER face at v +7: from the tenon shoulder to 8 mm short of the rack (the cables then cross
    # the gap to the nape core's web holes under the nape pad)
    rc = C.REAR_CABLE
    run_c = [p for p in pts if p.x < START.x - rc["s0"] and p.y > rc["y_end"]]
    sgn = outward_sign(run_c)
    pts_c = []
    for i, p in enumerate(run_c):
        a = run_c[max(i - 1, 0)]; b = run_c[min(i + 1, len(run_c) - 1)]
        Tv = (b - a).normalized()
        N = Tv.cross(W).normalized() * sgn                       # outward
        pts_c.append(p + W * rc["v"] - N * (C.REAR_T / 2 - rc["d"] / 2 + 0.5))
    # Track P: same wedge on the harness channel (its -W wall faces down in the print). The ribbon's N is the path's
    # T x W, which equals the outward N above only when sgn > 0; the signs below follow that.
    csec = L.groove_section(face=-0.75 * sgn, floor=(rc["d"] / 2 + 0.5) * sgn, over=-(rc["d"] / 2 + 0.5) * sgn, wh=rc["w"] / 2, depth=rc["d"])
    L.cut(band, L.ribbon("cablech", pts_c, W, None, section=csec))
    r0, r1 = C.REAR_NODE_W
    if side > 0:          # the RIGHT half keeps the band running into the node until it has been turned over (see below)
        L.cut(band, L.add_box("nodebox", (C.REAR_NODE_X, CF.NODE_Y, C.CRADLE_Z + (r0 + r1) / 2), (C.NODE_LEN, CF.NODE_T + 4.0, r1 - r0 + 4.0)))
    if side > 0:
        L.union(band, L.extrude_polygon("tenon", CF.tenon_poly(0.0, +1), C.CRADLE_TENON[0] - 0.2, CF.tenon_frame(+1), z0=-(C.CRADLE_TENON[0] - 0.2) / 2))
    pz = START.z + 6.0 * T_IN.z
    if side > 0:
        L.cut(band, L.add_teardrop("tpin", (C.TENON_PIN_X, START.y, pz), C.PIN_DIA / 2 + 0.1, 12.0, (0.0, 1.0, 0.0), -W, verts=24))   # prints horizontal (top edge down): roof toward -W
    # rack strip: u along -Y from y = 50, v along W, w outward
    Mr = L.frame((C.REAR_BACK_X, C.RACK_Y0, z_of(C.REAR_BACK_X)), N_OUT, (0.0, -1.0, 0.0))
    body_h = half - C.RACK_PITCH_W - 0.2
    poly = L.rack_poly(C.RACK_LEN + 2.0, C.GEAR_MODULE, C.GEAR_PA, body_h)
    poly = [(u - C.RACK_SHIFT, C.RACK_PITCH_W - v) for (u, v) in poly]   # phase: a tooth space on y = 0 at the nominal fit
    rack = L.extrude_polygon("rack", poly, C.REAR_T - 0.1, Mr, z0=-(C.REAR_T - 0.1) / 2)
    L.union(band, rack)
    if side < 0:
        # v0.18 (2026-11-10): the RIGHT half. It is still the left half TURNED OVER about N_OUT (that is what puts its rack in the
        # pin-lock's lower tunnel and lets it print exactly like the left, top edge down, rack teeth up). But turning about an axis
        # 49 deg off vertical also flips the angle of the left half's END cut, so the turned end cut ~18 mm diagonally into the right
        # node (938 mm3 measured; the collision report listed cradle-x-rear as "expected" contact). So the band is turned BEFORE its
        # end is trimmed: it arrives with 8 mm running into the node, is trimmed flush to the RIGHT node's rear face, and gets its
        # tenon in the right slot's own frame (CF.tenon_frame(-1): the frame the printed cradle's right slot was cut from).
        turned = L.transformed_copy(band, right_half_matrix(), "rear_band_half_R")
        L.delete(band)
        band = turned
        L.cut(band, L.add_box("nodebox", (C.REAR_NODE_X, -CF.NODE_Y, C.CRADLE_Z + (r0 + r1) / 2), (C.NODE_LEN, CF.NODE_T + 4.0, r1 - r0 + 4.0)))
        L.union(band, L.extrude_polygon("tenon", CF.tenon_poly(0.0, -1), C.CRADLE_TENON[0] - 0.2, CF.tenon_frame(-1), z0=-(C.CRADLE_TENON[0] - 0.2) / 2))
        L.cut(band, L.add_teardrop("tpin", (C.TENON_PIN_X, -START.y, pz), C.PIN_DIA / 2 + 0.1, 12.0, (0.0, 1.0, 0.0), W, verts=24))   # print-up is +W here (turned)
        L.bed_plane(band, PRINT_ROT @ right_half_matrix().inverted(), 0.25)
        return band
    L.bed_plane(band, PRINT_ROT, 0.25)   # Track P: the rack strip's ridge sat 0.2 above the band's (body_h - 0.2); one bed plane
    return band


def right_half_matrix() -> Matrix:
    return Matrix.Translation(BACK) @ Matrix.Rotation(math.pi, 4, N_OUT) @ Matrix.Translation(-BACK)


# ---------------------------------------------------------------------------------------------------------------------
# Sacrificial print frame (Track P, 2026-09-26), after the cradle's: a 6 mm ribbon standing 36 mm on its edge with a free
# end at each side (the tenon, the 54 mm rack strip) is the cradle's problem in miniature. Separate overlapping closed
# shells joined without booleans: 12 x 1.2 mm strips along both faces of the band and on along the rack strip (0.4 mm
# gap), necks every ~15 mm, 20 mm bracing fins every ~30 mm clear of the strap slots, and a tie bar across the inside of
# the L joining the tenon end to the rack end. Added only by the print export below; make() stays clean.
FRAME_T, FRAME_W, FRAME_GAP, FIN_H, FIN_T, NECK_W = 1.2, 12.0, 0.4, 20.0, 1.2, 1.5
FIN_NECK_DEPTHS = (4.0, 14.0)     # below the bed along W: clear of the harness channel (W 7) and the spine (W -4 .. -12)


def print_frame(band):
    import bpy  # type: ignore
    Wn = W.normalized()
    wb = max(v.co.dot(Wn) for v in band.data.vertices)                     # the bed plane along W (the print's -Z)
    t2, g = C.REAR_T / 2.0, FRAME_GAP
    full = centre_pts()
    cum_full = [0.0]
    for a, b in zip(full, full[1:]):
        cum_full.append(cum_full[-1] + (b - a).length)
    run, cum = [], []
    for p, c in zip(full, cum_full):
        if p.x < START.x - 1.0:
            run.append(p); cum.append(c)
    r0 = Vector((C.REAR_BACK_X, C.RACK_Y0, z_of(C.REAR_BACK_X)))
    for k in range(1, 28):                                                  # on along the rack strip (u along -Y)
        run.append(r0 + Vector((0.0, -2.0 * k, 0.0))); cum.append(cum[-1] + 2.0)
    def tn(i):
        Tv = (run[min(i + 1, len(run) - 1)] - run[max(i - 1, 0)]).normalized()
        return Tv, Tv.cross(Wn).normalized()                                # N = T x W, the ribbon's own convention
    pieces = []
    n0, n1 = t2 + g, t2 + g + FRAME_W
    for sgn in (+1, -1):
        secs = []
        for p in run:
            w1 = wb - p.dot(Wn); w0 = w1 - FRAME_T
            a, b = (n0, n1) if sgn > 0 else (-n1, -n0)
            secs.append([(a, w0), (b, w0), (b, w1), (a, w1)])
        pieces.append(L.ribbon("pstrip", run, Wn, None, section=secs))
    strap_arcs = [INSIDE + s for s in C.REAR_STRAP_S]
    s_next = 3.0
    for i, p in enumerate(run):
        if cum[i] - cum[0] < s_next:
            continue
        s_next = cum[i] - cum[0] + 15.0
        Tv, N = tn(i)
        w1 = wb - p.dot(Wn)
        for sgn in (+1, -1):
            M = L.frame(p + Wn * (w1 - FRAME_T / 2.0), Wn, N * sgn)
            pieces.append(L.add_box_local("pneck", M, (t2 - 1.2 + (g + 2.2) / 2.0, 0.0, 0.0), (g + 2.2, NECK_W, FRAME_T)))
    s_next = 10.0
    for i, p in enumerate(run):
        if cum[i] - cum[0] < s_next or any(abs(cum[i] - sa) < 8.0 for sa in strap_arcs):
            continue
        s_next = cum[i] - cum[0] + 30.0
        Tv, N = tn(i)
        w1 = wb - p.dot(Wn)
        for sgn in (+1, -1):
            M = L.frame(p + Wn * w1, Tv * sgn, N * sgn)                    # local x = out from the face, local y = away from the bed
            pieces.append(L.extrude_polygon("pfin", [(n0, 0.0), (n1, 0.0), (n0, FIN_H)], FIN_T, M, z0=-FIN_T / 2.0))
            for dz in FIN_NECK_DEPTHS:
                pieces.append(L.add_box_local("pfneck", M, ((t2 - 1.2 + n0 + 0.3) / 2.0, dz, 0.0), (n0 + 0.3 - (t2 - 1.2), 1.2, FIN_T)))
    # tie bar across the inside of the L: the side where the two ends' strip centres come closest
    best = None
    for sgn in (+1, -1):
        ends = []
        for i in (0, len(run) - 1):
            Tv, N = tn(i)
            ends.append(run[i] + N * sgn * (n0 + FRAME_W / 2.0) + Wn * (wb - run[i].dot(Wn) - FRAME_T / 2.0))
        d = (ends[1] - ends[0]).length
        if best is None or d < best[0]:
            best = (d, ends)
    d, (a, b) = best
    M = L.frame((a + b) / 2.0, Wn, (b - a).normalized())
    pieces.append(L.add_box_local("ptie", M, (0.0, 0.0, 0.0), (d + FRAME_W, 10.0, FRAME_T)))
    for ob in pieces:
        L.apply_transform(ob)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in pieces:
        ob.select_set(True)
    band.select_set(True)
    bpy.context.view_layer.objects.active = band
    bpy.ops.object.join()
    return band


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--right", action="store_true", help="the RIGHT half: the left turned over, its node end and tenon rebuilt for the right node (v0.18)")
    ap.add_argument("--frame", action="store_true", help="add the sacrificial print frame (opt-in since 2026-09-29: Jordan found it overkill; the first layers were the problem)")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    ob = make(-1 if args.right else +1)
    notes = list(NOTES) if not args.right else ["the RIGHT rear half (v0.18): the left half turned over, with its node end and tenon rebuilt for the right node; print exactly like the left, planar top edge on the bed, rack teeth up"] + list(NOTES[1:])
    if args.frame and not args.right:
        print_frame(ob)
        notes.insert(0, "PRINTS WITH A SACRIFICIAL FRAME: strips along both faces and the rack, a tie bar across the L, 20 mm fins, "
                        "joined by small necks. Cut the necks, lift the frame off, pare the stubs flush; pare the RACK STRIP's stubs "
                        "especially flat, since the rack slides through the nape pin-lock's tunnel")
    L.finalize_and_export(ob, args.out, PRINT_ROT @ right_half_matrix().inverted() if args.right else PRINT_ROT, notes)
