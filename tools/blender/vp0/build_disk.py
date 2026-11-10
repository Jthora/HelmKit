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


def _saddle(shell, side, yc):
    """Sacrificial print saddle for the on-edge dome (Track P, 2026-09-20). The dome stands on its 0.15 mm flat, 6 x 16 mm,
    for 122 mm of height: 5 % of its footprint, the worst perch in the set. A 1 mm plate under the rim with six fins rising
    to the rim's lower arc, each joined to the rim by a 0.8 x 6 mm neck, makes the bed contact a 92 x 30 plate and braces
    the first 17 mm of height. The flat still lands on the bed through a slot in the plate, so nothing bonds to the rim's
    outer surface except the six necks, which snap off. Tree supports still do the rim crown and the apex boss."""
    R = C.DISK_R
    z_bed = C.CZ - R + C.DISK_PRINT_FLAT                       # the flat's face: the print bed
    y_mid = yc + side * (C.DISK_PLATE_T + C.DISK_N_RIM) / 2.0  # the rim's mid-width
    PLATE, FIN_T, FIN_W, NECK_W, NECK_L, GAP = 1.0, 1.2, 16.0, 0.8, 6.0, 0.6

    def h(x):                                                  # rim underside above the bed at |x|
        return R - math.sqrt(R * R - x * x) - C.DISK_PRINT_FLAT

    sad = L.add_box("saddle", (C.CX, y_mid, z_bed + PLATE / 2.0), (92.0, 30.0, PLATE))
    L.cut(sad, L.add_box("saddleslot", (C.CX, y_mid, z_bed + PLATE / 2.0), (28.0, 20.0, PLATE + 2.0)))   # the flat lands on the bed here; rim clears the plate by 0.5 at the slot edge
    for xf in (-42.0, -32.0, -22.0, 22.0, 32.0, 42.0):
        lo, hi = abs(xf) - FIN_T / 2.0, abs(xf) + NECK_W / 2.0
        top = z_bed + h(lo) - GAP                              # fin top clear of the rim across the fin's whole width
        z0 = z_bed + PLATE - 0.3                               # sunk into the plate: no coplanar face
        L.union(sad, L.add_box(f"fin{xf:+.0f}", (C.CX + xf, y_mid, (z0 + top) / 2.0), (FIN_T, FIN_W, top - z0)))
        neck_top = z_bed + h(hi) + 0.4                         # into the 3 mm rim wall by 0.4 at the neck's high side
        L.union(sad, L.add_box(f"neck{xf:+.0f}", (C.CX + xf, y_mid, (top - 0.2 + neck_top) / 2.0), (NECK_W, NECK_L, neck_top - top + 0.2)))
    L.union(shell, sad)


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
    _saddle(shell, side, yc)
    mw, md = C.DISK_UNLOCK_MARK
    # at the bottom in the WORN pose: the dome turns with the plate, so in the modelled (entry) pose it sits `travel` further round
    a_mark = (90.0 if side > 0 else 270.0) + lock_travel_deg()
    Mm = M @ Matrix.Rotation(math.radians(a_mark), 4, "Z")
    L.cut(shell, L.add_box_local("unlockmark", Mm, (dd / 2 + 0.5, 0.0, n_top - md / 2 + 0.5), (2.0, mw, md + 1.0)))
    return shell


def lock_travel_deg(lug_reach=None):
    """Plate rotation from the entry notch to the stop, from the lug width, the bump width and the bump angle (all in plate degrees)."""
    lw, lr, _ = C.STALK_LUG
    if lug_reach is not None:
        lr = lug_reach                      # a retired coupon pins the reach it printed with
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


def bayonet_boss(M, z0, h=None):
    """Annulus revolve for the bayonet boss about M's Z (own segment count and inner radius: no seams shared with the plate revolve).
    h overrides the canon height (coupon F: an open groove needs no wall above the lugs)."""
    bd, bh = C.BAYONET_BOSS
    if h is not None:
        bh = h
    boss = L.revolve("boss", [(8.5, z0), (bd / 2, z0), (bd / 2, bh), (8.5, bh)], axis="Z", center=(0.0, 0.0, 0.0), segments=100)
    boss.matrix_world = M @ boss.matrix_world
    L.apply_transform(boss)
    return boss


# The bayonet as it was drawn before Track P's coupons (E printed with it; A and D2 too): roofed groove, inverted cam, lock notch, 0.3 bore,
# 0.6 slot, no reverse block. Retired coupons pin these so a rebuild reproduces what they printed.
LEGACY = dict(cam=(4.5, 3.8), open_top=False, lock=True, bore_clear=0.3, notch_clear=0.3, reverse_block=False, lug_reach=3.0, boss_h=14.5)


def bayonet_cuts(plate, M, mouth=True, z_below=1.0, side=+1, cam=None, open_top=True, lock=False,
                 bore_clear=None, notch_clear=None, reverse_block=True, lug_reach=None, boss_h=None):
    """Bore, lug notches, groove with stop walls (and the head-side elephant-foot mouth) about M's Z axis; local z = 0 is the head face.
    Every coaxial cutter is rotated by an odd angle so no vertex lands on a radial line of the revolves."""
    bd, bh = C.BAYONET_BOSS
    if boss_h is not None:
        bh = boss_h                          # the bore and the open groove run to the top of THIS boss (a retired coupon pins 14.5)
    bore_clear = C.BAYONET_BORE_CLEAR if bore_clear is None else bore_clear
    notch_clear = C.BAYONET_NOTCH_CLEAR if notch_clear is None else notch_clear
    lr = C.STALK_LUG[1] if lug_reach is None else lug_reach       # the lug's radial reach the slot and groove are cut for

    def rot(deg):
        return M @ Matrix.Rotation(math.radians(deg), 4, "Z")

    # bore_clear: canon 0.3 on radius. Coupon G (2026-09-20): a Ø20 stalk in a bore that prints ~20.25 is a friction fit that holds
    # the flange up and reads as "snug" while the cam does nothing, and turns stiff or not at all collar to collar. Coupons pass 0.5.
    L.cut(plate, L.add_cyl_local("bore", rot(1.3), (0.0, 0.0, (bh + 1.0 - z_below) / 2), C.STALK_D / 2 + bore_clear, bh + 1.0 + z_below, axis="Z", verts=72))
    if mouth:
        L.cut(plate, L.add_cone_local("mouth", rot(2.1), (0.0, 0.0, 0.35), C.STALK_D / 2 + 1.3, C.STALK_D / 2 + 0.4, 0.9, axis="Z", verts=60))   # Track P: 45-deg entry cone 0.8 deep on the head (bed) face: elephant-foot relief that survives the first-layer squash
    lw, _, lh = C.STALK_LUG
    g_r, g0, g1 = C.BAYONET_GROOVE
    # cam: (floor at the entry notch, floor at the stop). Coupon E (2026-09-19) proved canon's (4.5, 3.8) is upside
    # down against lugs at n 4..7: 0.34 mm of solid in the lug's path 20 deg in, 0.2 loose at the stop. A caller
    # may pass a corrected cam; open_top drops the groove ceiling (it never touches the lug: the flange stops the
    # plate 0.8 mm before it could) and lock=False skips the knob-lock notch. Defaults reproduce canon exactly.
    n_notch, n_stop = cam if cam is not None else C.BAYONET_CAM
    g_top = bh + 1.0 if open_top else g1
    for sx in (+1, -1):
        # the notch must break OUT of the head face, or the groove is a sealed cavity and the lugs can never
        # enter. It therefore drops by z_below, exactly as the bore does. On the real plate z_below is 1.0 and
        # this is unchanged; on a coupon, where the boss sits on a thicker slab, a fixed 1.0 left the notch
        # capped by the slab and BOTH coupon A and coupon D2 printed a bayonet with no way in (2026-09-19).
        # the slot: from 0.3 inside the stalk's surface to notch_clear beyond the lug's reach. Coupon G: a slot 0.3 beyond the lug
        # (LEGACY) printed too tight to enter; coupon H printed 1.1 beyond a 2.6 lug (r 13.7) and everything entered.
        r_s0, r_s1 = C.STALK_D / 2 - 0.3, C.STALK_D / 2 + lr + notch_clear
        L.cut(plate, L.add_box_local("notch", rot(0.9), (sx * (r_s0 + r_s1) / 2, 0.0, (n_notch + 0.3 - z_below) / 2), (r_s1 - r_s0, lw + 1.0, n_notch + 0.3 + z_below)))
    # groove tool: a lofted ring whose FLOOR cams from n_notch at the entry notch down to n_stop over the quarter turn, so the
    # lugs (n 4..7 off the flange face) pull the plate onto the flange as it is turned; rotated 2.37 deg (never lands on a bore,
    # plate or boss vertex line). The stop walls are carved out of the tool, so the plate keeps that material after one cut.
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
        stations.append((a, [(r_in, n0), (g_r, n0), (g_r, g_top), (r_in, g_top)]))
    groove = L.loft_ring("groove", stations, axis="Z", center=(0.0, 0.0, 0.0))
    groove.matrix_world = rot(2.37) @ groove.matrix_world
    L.apply_transform(groove)
    for sx in (+1, -1):
        Mb = rot(0.9 + C.BAYONET_STOP["bump_deg"] + (0.0 if sx > 0 else 180.0))
        rb_in = C.STALK_D / 2 + 0.5
        rc = (rb_in + g_r + 0.5) / 2
        L.cut(groove, L.add_box_local("bump", Mb, (rc, 0.0, (n_stop - 0.6 + g_top + 0.4) / 2), (g_r + 0.5 - rb_in, C.BAYONET_STOP["bump_w"], g_top - n_stop + 1.0)))
    if reverse_block:
        # Coupon G: from each notch the lug could also turn the WRONG way, 29 deg across the tail of the other sector's entry
        # floor to the back of its stop bump, and stop there as if locked. A block fills that tail, 2 deg clear of the bump
        # and of the notch's edge, so the only way out of the notch is up the ramp.
        r_lug = C.STALK_D / 2 + lr / 2
        half_notch = math.degrees((lw + 1.0) / 2 / r_lug)
        half_bump = math.degrees(C.BAYONET_STOP["bump_w"] / 2 / rc)
        a0 = C.BAYONET_STOP["bump_deg"] + 180.0 + half_bump + 2.0          # just past the other sector's bump
        a1 = 360.0 - half_notch - 2.0                                          # just short of this notch
        blk_w = math.radians(a1 - a0) * rc
        for sx in (+1, -1):
            Mv = rot(0.9 + (a0 + a1) / 2 + (0.0 if sx > 0 else 180.0))
            L.cut(groove, L.add_box_local("revblock", Mv, (rc, 0.0, (n_notch - 0.6 + g_top + 0.4) / 2), (g_r + 0.5 - rb_in, blk_w, g_top - n_notch + 1.0)))
    L.cut(plate, groove)
    if not lock:
        return
    # lock notch in the boss bore: the stalk's radial pin (world top) drops into it after the 98 deg turn
    lk = C.BAYONET_LOCK
    nw, nd = lk["notch"]
    na, nb = lk["notch_n"]
    phi = (-side * lk["pin_world_deg"]) % 360.0 + lock_travel_deg(lr)   # the pin's plate-frame angle after the turn (rot() is mirrored between the sides)
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
    "disk_dome": (lambda: dome(+1), L.ROT_NONE, ["print ON EDGE (axis horizontal) standing on the 6 mm rim flat INSIDE its printed saddle (a 92 x 30 plate with six fins necked to the rim: snap the six 0.8 mm necks after printing, trim the nubs) with a wide brim; needs Z >= 125 mm; interior tree supports under the apex boss, the rim crown and the two LOWEST screw bosses (horizontal cylinders whose first chord hangs 1.3 mm above the curved rim wall: 9 mm2 islands for two layers, layer_islands.py 2026-09-25; the shell itself is within 19 deg of vertical everywhere); 0.16 mm layers; 3 walls",
                                                    f"six M3 x 8 into the bosses hold the back plate; cavity {C.DISK_CAVITY} for the coil; no metal on the axis"]),
    "disk_back_L": (lambda: back(+1), L.ROT_Y_TO_Z, ["LEFT plate. print flat, bayonet boss up; no supports: the groove is OPEN (Track P, coupon H), the wall is 7.6 tall, a block behind each slot stops the wrong-way turn. Onto the nexus stalk: slots over the lugs, plate onto the flange, turn the disk to the stop (about 107 deg; the floor rises 3.2 -> 3.8 under the lugs and seats snug-tight). The knob lock has no notch to engage until the lock post is designed",
                                                      "seat on the nexus flange with the lugs in the notches, quarter turn to the stop (it tightens), then turn the centre knob 180 deg: its eccentric drives the stalk pin into the boss notch"]),
    "disk_back_R": (lambda: back(-1), L.ROT_NEGY_TO_Z, ["RIGHT plate (mirrored). print flat, bayonet boss up; no supports (open groove, Track P coupon H)",
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
