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


def back(side=+1):
    """Annulus revolves (no axis fans) and every coaxial cutter rotated by an odd angle: no vertex on a radial line."""
    M = axis_frame(side)
    r0 = 9.0
    plate = L.revolve("disk_back", [(r0, 0.0), (C.DISK_R - 0.3, 0.0), (C.DISK_R - 0.3, C.DISK_PLATE_T), (r0, C.DISK_PLATE_T)],
                      axis="Z", center=(0.0, 0.0, 0.0), segments=120)
    plate.matrix_world = M @ plate.matrix_world
    L.apply_transform(plate)
    bd, bh = C.BAYONET_BOSS
    boss = L.revolve("boss", [(r0 - 0.5, C.DISK_PLATE_T - 0.1), (bd / 2, C.DISK_PLATE_T - 0.1), (bd / 2, bh), (r0 - 0.5, bh)], axis="Z", center=(0.0, 0.0, 0.0), segments=100)   # own segment count and inner radius: no seams shared with the plate revolve
    boss.matrix_world = M @ boss.matrix_world
    L.apply_transform(boss)
    def rot(deg):
        return M @ Matrix.Rotation(math.radians(deg), 4, "Z")

    L.union(plate, boss)
    # no fillet: the bevel pass leaves edges the bore cut cannot resolve (flat plate, cosmetic only)

    L.cut(plate, L.add_cyl_local("bore", rot(1.3), (0.0, 0.0, bh / 2), C.STALK_D / 2 + 0.3, bh + 2.0, axis="Z", verts=72))
    L.cut(plate, L.add_cyl_local("mouth", rot(2.1), (0.0, 0.0, 0.0), C.STALK_D / 2 + 0.9, 1.2, axis="Z", verts=60))   # 0.6 elephant-foot relief at the head-side mouth
    lw, lr, lh = C.STALK_LUG
    g_r, g0, g1 = C.BAYONET_GROOVE
    for sx in (+1, -1):
        L.cut(plate, L.add_box_local("notch", rot(0.9), (sx * (C.STALK_D / 2 + lr / 2), 0.0, (g0 + 0.3 - 1.0) / 2), (lr + 0.6, lw + 1.0, g0 + 0.3 + 1.0)))
    groove = L.revolve("groove", [(C.STALK_D / 2 + 0.1, g0), (g_r, g0), (g_r, g1), (C.STALK_D / 2 + 0.1, g1)], axis="Z", center=(0.0, 0.0, 0.0), segments=100)
    groove.matrix_world = rot(2.37) @ groove.matrix_world   # 2.37: never lands on a bore (1.3 + 5k), plate (3m) or boss (3.6i) vertex line
    L.apply_transform(groove)
    # detent bump (78 deg) and stop wall (98 deg) past each notch: carved out of the groove TOOL, so the plate keeps
    # that material after a single clean cut (unioning bumps into the finished groove leaves slivers)
    for sx in (+1, -1):
        for ang, tang, h in ((78.0, 1.4, C.BAYONET_DETENT), (98.0, 3.0, g1 - g0 + 0.2)):
            Mb = rot(0.9 + ang + (0.0 if sx > 0 else 180.0))
            r_in = C.STALK_D / 2 + 0.5
            rc = (r_in + g_r + 0.5) / 2
            L.cut(groove, L.add_box_local("bump", Mb, (rc, 0.0, g0 + h / 2 - 0.6), (g_r + 0.5 - r_in, tang, h + 1.0)))
    L.cut(plate, groove)
    for k in range(C.DISK_SCREWS):
        a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
        L.cut(plate, L.add_cyl_local("screw", rot(1.1), (C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a), C.DISK_PLATE_T / 2), C.M3_CLEAR_DIA / 2, C.DISK_PLATE_T + 2.0, axis="Z", verts=16))
    lk = C.DISK_LOCK
    a = math.radians(lk["angle"])
    Mlk = Matrix.Translation((C.CX + lk["r"] * math.cos(a), side * (C.DISK_IN_Y + C.DISK_PLATE_T / 2), C.CZ + lk["r"] * math.sin(a))) @ Matrix.Rotation(math.radians(11.0), 4, "Y")
    L.cut(plate, L.add_cyl_local("lock", Mlk, (0.0, 0.0, 0.0), lk["hole"] / 2, C.DISK_PLATE_T + 2.0, axis="Y", verts=16))   # vertex ring turned 11 deg: the hole centre sits on a revolve radial line
    cr, cd = C.DISK_CABLE_HOLE
    L.cut(plate, L.add_cyl_local("cable", rot(1.1), (cr * math.cos(math.radians(45.0)), cr * math.sin(math.radians(45.0)), C.DISK_PLATE_T / 2), cd / 2, C.DISK_PLATE_T + 2.0, axis="Z", verts=24))
    return plate


PARTS = {
    "disk_dome": (lambda: dome(+1), L.ROT_Y_TO_Z, ["print dome up with tree supports under the shell (or on edge with a brim); 0.12 mm layers for the dome",
                                                    f"six M3 x 8 into the bosses hold the back plate; cavity {C.DISK_CAVITY} for the coil; no metal on the axis"]),
    "disk_back": (lambda: back(+1), L.ROT_Y_TO_Z, ["print flat, bayonet boss up; no supports (3.3 mm groove ceiling bridges)",
                                                    "seat on the nexus flange with the lugs in the notches, quarter turn until it clicks, then the lock nail through the plate into the ear"]),
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
