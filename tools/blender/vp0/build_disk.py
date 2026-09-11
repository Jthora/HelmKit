#!/usr/bin/env -S blender --background --python
"""
build_disk.py -- vp0.7 enclosed disk (--out-dir): dome shell + back plate.

The disk is a closed lens: a 2.5 mm paraboloid dome (outside) on a 3 mm rim
wall, with a Ø110 x 12 cavity for the coil apparatus, closed by a 3 mm back
plate (head side) on six M3 screws. The back plate carries the BAYONET: a
Ø34 boss on its cavity side with a Ø20.6 bore, two entry notches, a groove
the stalk's lugs turn 90 deg into, a detent bump and a stop wall. Nothing
metallic sits on the disk axis. Coil feed exits through a Ø6 hole.
Print: dome up with supports under the shell (or on edge); back plate flat,
boss up. Qty: 2 each (same STLs both sides).
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

R_IN = C.DISK_R - C.DISK_RIM_WALL      # 58.05 rim wall inner radius


def n_out(r):
    return C.DISK_N_RIM + C.DISK_SAG * (1.0 - (r / C.DISK_R) ** 2)


def axis_frame(side, n0=0.0):
    """Disk-local frame: origin on the axis at n = n0 from the back face, local Z = disk axis outward (+/-Y)."""
    return L.frame((C.CX, side * (C.DISK_IN_Y + n0), C.CZ), (0.0, side, 0.0), (1.0, 0.0, 0.0))


def dome(side=+1):
    axis = "Y" if side > 0 else "-Y"
    yc = side * C.DISK_IN_Y
    rs = [C.DISK_R * i / 48 for i in range(49)]
    prof = [(r, n_out(r)) for r in rs]                                  # outer surface: vertex -> rim edge
    prof += [(C.DISK_R, C.DISK_PLATE_T), (R_IN, C.DISK_PLATE_T), (R_IN, n_out(R_IN) - C.DISK_SHELL_T)]
    prof += [(r, n_out(r) - C.DISK_SHELL_T) for r in reversed(rs) if r < R_IN - 0.5]   # inner surface back to the axis
    shell = L.revolve("disk_dome", prof, axis=axis, center=(C.CX, yc, C.CZ), segments=160)
    M = axis_frame(side)
    for k in range(C.DISK_SCREWS):
        a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
        cx, cy = C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a)
        h = C.DISK_PLATE_T + C.DISK_CAVITY[1]
        L.union(shell, L.add_cyl_local("boss", M, (cx, cy, (C.DISK_PLATE_T + 0.1 + h) / 2), 3.5, h - C.DISK_PLATE_T - 0.1, axis="Z", verts=24))
    # apex boss inside the shell for the knob dish, the shaft hole and the C-clip seat
    kb = C.DISK_KNOB
    bd, bh = kb["apex_boss"]
    n_in = n_out(0.0) - C.DISK_SHELL_T                      # inner surface at the apex
    L.fillet(shell, width=0.8, angle_deg=60.0)
    L.union(shell, L.add_cyl_local("apexboss", M, (0.0, 0.0, n_in + 0.1 - bh / 2), bd / 2, bh, axis="Z", verts=64))   # after the fillet: its rim sits inside the shell
    for k in range(C.DISK_SCREWS):
        a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
        cx, cy = C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a)
        L.cut(shell, L.add_cyl_local("tap", M, (cx, cy, C.DISK_PLATE_T + 5.0), C.M3_TAP_DIA / 2, 12.0, axis="Z", verts=16))
    dd, ddep = kb["dish"]
    n_top = n_out(0.0)
    L.cut(shell, L.add_cyl_local("dish", M, (0.0, 0.0, n_top - ddep / 2 + 1.0), dd / 2, ddep + 2.0, axis="Z", verts=64))
    L.cut(shell, L.add_cyl_local("shafthole", M, (0.0, 0.0, n_top - 8.0), kb["hole"] / 2, 20.0, axis="Z", verts=32))
    # v0.14: the dome prints ON EDGE (axis horizontal). A 0.15 mm flat at the rim's lowest point is its first layer (6 mm chord,
    # invisible), and a small notch in the dish rim at the bottom marks the knob's unlocked position.
    L.cut(shell, L.add_box("printflat", (C.CX, yc, C.CZ - C.DISK_R - 7.0 + C.DISK_PRINT_FLAT), (200.0, 80.0, 14.0)))
    mw, md = C.DISK_UNLOCK_MARK
    # at the bottom in the WORN pose: the dome turns with the plate, so in the modelled (entry) pose it sits `travel` further round
    a_mark = (90.0 if side > 0 else 270.0) + lock_travel_deg()
    Mm = M @ Matrix.Rotation(math.radians(a_mark), 4, "Z")
    L.cut(shell, L.add_box_local("unlockmark", Mm, (dd / 2 + 0.5, 0.0, n_top - md / 2 + 0.5), (2.0, mw, md + 1.0)))
    return shell


def lock_travel_deg():
    """Plate rotation from the entry notch to the stop, from the lug width, the bump width and the bump angle (all in plate degrees)."""
    lw, lr, _ = C.STALK_LUG
    r_lug = C.STALK_D / 2 + lr / 2
    g_r = C.BAYONET_GROOVE[0]
    rb_in = C.STALK_D / 2 + 0.5
    rc = (rb_in + g_r + 0.5) / 2
    half_lug = math.degrees(lw / 2 / r_lug)
    half_bump = math.degrees(C.BAYONET_STOP["bump_w"] / 2 / rc)
    return C.BAYONET_STOP["bump_deg"] - half_bump - half_lug


def bore_local_angle(M):
    """Plate-frame angle (deg) and radius of the flange's cable bore in the modelled (entry) pose."""
    cb = C.CABLE_BORE
    q = M.inverted() @ Vector((C.CX - cb["dx"], M.translation.y, cb["z"]))
    return math.degrees(math.atan2(q.y, q.x)), math.hypot(q.x, q.y)


def bayonet_boss(M, z0):
    """Annulus revolve for the bayonet boss about M's Z (own segment count and inner radius: no seams shared with the plate revolve)."""
    bd, bh = C.BAYONET_BOSS
    boss = L.revolve("boss", [(8.5, z0), (bd / 2, z0), (bd / 2, bh), (8.5, bh)], axis="Z", center=(0.0, 0.0, 0.0), segments=100)
    boss.matrix_world = M @ boss.matrix_world
    L.apply_transform(boss)
    return boss


def bayonet_cuts(plate, M, mouth=True, z_below=1.0, side=+1):
    """Bore, lug notches, groove with stop walls (and the head-side elephant-foot mouth) about M's Z axis; local z = 0 is the head face.
    Every coaxial cutter is rotated by an odd angle so no vertex lands on a radial line of the revolves."""
    bd, bh = C.BAYONET_BOSS

    def rot(deg):
        return M @ Matrix.Rotation(math.radians(deg), 4, "Z")

    L.cut(plate, L.add_cyl_local("bore", rot(1.3), (0.0, 0.0, (bh + 1.0 - z_below) / 2), C.STALK_D / 2 + 0.3, bh + 1.0 + z_below, axis="Z", verts=72))
    if mouth:
        L.cut(plate, L.add_cyl_local("mouth", rot(2.1), (0.0, 0.0, 0.0), C.STALK_D / 2 + 0.9, 1.2, axis="Z", verts=60))   # 0.6 elephant-foot relief at the head-side mouth
    lw, lr, lh = C.STALK_LUG
    g_r, g0, g1 = C.BAYONET_GROOVE
    for sx in (+1, -1):
        L.cut(plate, L.add_box_local("notch", rot(0.9), (sx * (C.STALK_D / 2 + lr / 2), 0.0, (C.BAYONET_CAM[0] + 0.3 - 1.0) / 2), (lr + 0.6, lw + 1.0, C.BAYONET_CAM[0] + 0.3 + 1.0)))
    # groove tool: a lofted ring whose FLOOR cams from n_notch at the entry notch down to n_stop over the quarter turn, so the
    # lugs (n 4..7 off the flange face) pull the plate onto the flange as it is turned; rotated 2.37 deg (never lands on a bore,
    # plate or boss vertex line). The stop walls are carved out of the tool, so the plate keeps that material after one cut.
    n_notch, n_stop = C.BAYONET_CAM
    r_in = C.STALK_D / 2 + 0.1

    def n_floor(theta):                       # theta: degrees past the notch (period 180)
        t = theta % 180.0
        if t <= 90.0:
            return n_notch + (n_stop - n_notch) * (t / 90.0)
        return n_stop if t <= C.BAYONET_STOP["flat_end"] else n_notch      # flat long enough for the whole 30-deg lug to sit on it

    NST = 100
    stations = []
    for i in range(NST):
        a = 360.0 * i / NST                   # tool frame; the tool is then rotated by 2.37, the notch sits at 0.9
        n0 = n_floor(a + 2.37 - 0.9)
        stations.append((a, [(r_in, n0), (g_r, n0), (g_r, g1), (r_in, g1)]))
    groove = L.loft_ring("groove", stations, axis="Z", center=(0.0, 0.0, 0.0))
    groove.matrix_world = rot(2.37) @ groove.matrix_world
    L.apply_transform(groove)
    for sx in (+1, -1):
        Mb = rot(0.9 + C.BAYONET_STOP["bump_deg"] + (0.0 if sx > 0 else 180.0))
        rb_in = C.STALK_D / 2 + 0.5
        rc = (rb_in + g_r + 0.5) / 2
        L.cut(groove, L.add_box_local("bump", Mb, (rc, 0.0, (n_stop - 0.6 + g1 + 0.4) / 2), (g_r + 0.5 - rb_in, C.BAYONET_STOP["bump_w"], g1 - n_stop + 1.0)))
    L.cut(plate, groove)
    # lock notch in the boss bore: the stalk's radial pin (world top) drops into it after the 98 deg turn
    lk = C.BAYONET_LOCK
    nw, nd = lk["notch"]
    na, nb = lk["notch_n"]
    phi = (-side * lk["pin_world_deg"]) % 360.0 + lock_travel_deg()   # the pin's plate-frame angle after the turn (rot() is mirrored between the sides)
    L.cut(plate, L.add_box_local("locknotch", rot(phi), (C.STALK_D / 2 + 0.3 + nd / 2 - 0.5, 0.0, (na + nb) / 2), (nd + 1.0, nw, nb - na)))


def back(side=+1):
    """Annulus revolves (no axis fans) and every coaxial cutter rotated by an odd angle: no vertex on a radial line."""
    M = axis_frame(side)
    r0 = 9.0
    plate = L.revolve("disk_back", [(r0, 0.0), (C.DISK_R - 0.3, 0.0), (C.DISK_R - 0.3, C.DISK_PLATE_T), (r0, C.DISK_PLATE_T)],
                      axis="Z", center=(0.0, 0.0, 0.0), segments=120)
    plate.matrix_world = M @ plate.matrix_world
    L.apply_transform(plate)
    L.union(plate, bayonet_boss(M, C.DISK_PLATE_T - 0.1))
    # no fillet: the bevel pass leaves edges the bore cut cannot resolve (flat plate, cosmetic only)
    bayonet_cuts(plate, M, side=side)

    def rot(deg):
        return M @ Matrix.Rotation(math.radians(deg), 4, "Z")

    for k in range(C.DISK_SCREWS):
        a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
        L.cut(plate, L.add_cyl_local("screw", rot(1.1), (C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a), C.DISK_PLATE_T / 2), C.M3_CLEAR_DIA / 2, C.DISK_PLATE_T + 2.0, axis="Z", verts=16))
    # v0.16: the cable exit is an ARC SLOT from the bore's plate-frame angle at entry to its angle when locked, so the lead
    # threaded through the flange bore is never dragged: the plate turns around it.
    a_b, r_b = bore_local_angle(M)
    trav = lock_travel_deg()
    sw = C.DISK_CABLE_SLOT_W
    n_mid = C.DISK_PLATE_T / 2
    pts = []
    n = max(4, int(math.radians(trav) * r_b / 1.5))
    for i in range(n + 1):
        a = math.radians(a_b + trav * i / n)
        pts.append(M @ Vector((r_b * math.cos(a), r_b * math.sin(a), n_mid)))
    wide = M.to_3x3() @ Vector((0.0, 0.0, 1.0))
    slot = L.ribbon("slot", pts, wide, [(n_mid + 1.0, n_mid + 1.0, sw / 2, sw / 2)] * len(pts))
    for a in (a_b, a_b + trav):
        L.union(slot, L.add_cyl_local("slotend", M, (r_b * math.cos(math.radians(a)), r_b * math.sin(math.radians(a)), n_mid), sw / 2, C.DISK_PLATE_T + 2.0, axis="Z", verts=24))
    L.cut(plate, slot)
    L.lr_notches(plate, side, (C.CX, side * (C.DISK_IN_Y + C.DISK_PLATE_T / 2), C.CZ + C.DISK_R), (1.0, 0.0, 0.0), size=1.0, thru=(1, C.DISK_PLATE_T + 2.0))   # v0.17: one nick L, two R, through the plate's top edge (0.5 deep)
    return plate


PARTS = {
    "disk_dome": (lambda: dome(+1), L.ROT_NONE, ["print ON EDGE (axis horizontal) standing on the 6 mm rim flat with a wide brim; needs Z >= 125 mm; interior tree supports only under the apex boss and the rim crown (the shell itself is within 19 deg of vertical everywhere); 0.16 mm layers; 3 walls",
                                                    f"six M3 x 8 into the bosses hold the back plate; cavity {C.DISK_CAVITY} for the coil; no metal on the axis"]),
    "disk_back_L": (lambda: back(+1), L.ROT_Y_TO_Z, ["LEFT plate (lock boss down-front). print flat, bayonet boss up; no supports (3.5 mm groove ceiling bridges)",
                                                      "seat on the nexus flange with the lugs in the notches, quarter turn to the stop (it tightens), then turn the centre knob 180 deg: its eccentric drives the stalk pin into the boss notch"]),
    "disk_back_R": (lambda: back(-1), L.ROT_NEGY_TO_Z, ["RIGHT plate (mirrored). print flat, bayonet boss up; no supports (3.5 mm groove ceiling bridges)",
                                                    "seat on the nexus flange with the lugs in the notches, quarter turn to the stop, then the M3 x 20 lock screw from the head side through the ear into the tapped boss"]),
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
