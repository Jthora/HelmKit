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
    L.fillet(shell, width=0.8, angle_deg=60.0)
    for k in range(C.DISK_SCREWS):
        a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
        cx, cy = C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a)
        L.cut(shell, L.add_cyl_local("tap", M, (cx, cy, C.DISK_PLATE_T + 5.0), C.M3_TAP_DIA / 2, 12.0, axis="Z", verts=16))
    return shell


def bayonet_boss(M, z0):
    """Annulus revolve for the bayonet boss about M's Z (own segment count and inner radius: no seams shared with the plate revolve)."""
    bd, bh = C.BAYONET_BOSS
    boss = L.revolve("boss", [(8.5, z0), (bd / 2, z0), (bd / 2, bh), (8.5, bh)], axis="Z", center=(0.0, 0.0, 0.0), segments=100)
    boss.matrix_world = M @ boss.matrix_world
    L.apply_transform(boss)
    return boss


def bayonet_cuts(plate, M, mouth=True, z_below=1.0):
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
        L.cut(plate, L.add_box_local("notch", rot(0.9), (sx * (C.STALK_D / 2 + lr / 2), 0.0, (g0 + 0.3 - 1.0) / 2), (lr + 0.6, lw + 1.0, g0 + 0.3 + 1.0)))
    groove = L.revolve("groove", [(C.STALK_D / 2 + 0.1, g0), (g_r, g0), (g_r, g1), (C.STALK_D / 2 + 0.1, g1)], axis="Z", center=(0.0, 0.0, 0.0), segments=100)
    groove.matrix_world = rot(2.37) @ groove.matrix_world   # 2.37: never lands on a bore (1.3 + 5k), plate (3m) or boss (3.6i) vertex line
    L.apply_transform(groove)
    # stop wall (98 deg) past each notch: carved out of the groove TOOL, so the plate keeps that material after a single
    # clean cut (unioning bumps into the finished groove leaves slivers). No detent bump: the lock screw holds the position.
    for sx in (+1, -1):
        Mb = rot(0.9 + 98.0 + (0.0 if sx > 0 else 180.0))
        r_in = C.STALK_D / 2 + 0.5
        rc = (r_in + g_r + 0.5) / 2
        h = g1 - g0 + 0.2
        L.cut(groove, L.add_box_local("bump", Mb, (rc, 0.0, g0 + h / 2 - 0.6), (g_r + 0.5 - r_in, 3.0, h + 1.0)))
    L.cut(plate, groove)


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
    bayonet_cuts(plate, M)

    def rot(deg):
        return M @ Matrix.Rotation(math.radians(deg), 4, "Z")

    for k in range(C.DISK_SCREWS):
        a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
        L.cut(plate, L.add_cyl_local("screw", rot(1.1), (C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a), C.DISK_PLATE_T / 2), C.M3_CLEAR_DIA / 2, C.DISK_PLATE_T + 2.0, axis="Z", verts=16))
    # lock boss on the CAVITY side at r 50.5..57.5 (between the dome's screw bosses), tapped through boss and plate for the M3 x 20
    # lock screw that comes from the head side through the nexus ear. Nothing protrudes from the head face: the plate prints flat.
    lk = C.DISK_LOCK
    tr, tw, tt = lk["tab"]
    a = math.radians(lk["angle"])
    Mt = Matrix.Translation((C.CX, side * (C.DISK_IN_Y + C.DISK_PLATE_T + tt / 2.0 - 0.1), C.CZ)) @ Matrix.Rotation(-a, 4, "Y")
    tab = L.add_box_local("lockboss", Mt, (lk["r"], 0.0, 0.0), (tr, tt + 0.2, tw))
    L.fillet(tab, width=0.8)
    L.union(plate, tab)
    L.cut(plate, L.add_cyl_local("locktap", Mt, (lk["r"], -side * (C.DISK_PLATE_T / 2.0), 0.0), lk["tap"] / 2.0, tt + C.DISK_PLATE_T + 4.0, axis="Y", verts=16))
    cr, cd = C.DISK_CABLE_HOLE
    L.cut(plate, L.add_cyl_local("cable", rot(1.1), (cr * math.cos(math.radians(45.0)), cr * math.sin(math.radians(45.0)), C.DISK_PLATE_T / 2), cd / 2, C.DISK_PLATE_T + 2.0, axis="Z", verts=24))
    return plate


PARTS = {
    "disk_dome": (lambda: dome(+1), L.ROT_Y_TO_Z, ["print dome up with tree supports under the shell (or on edge with a brim); 0.12 mm layers for the dome",
                                                    f"six M3 x 8 into the bosses hold the back plate; cavity {C.DISK_CAVITY} for the coil; no metal on the axis"]),
    "disk_back": (lambda: back(+1), L.ROT_Y_TO_Z, ["print flat, bayonet boss up; no supports (3.3 mm groove ceiling bridges)",
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
