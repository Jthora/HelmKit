#!/usr/bin/env -S blender --background --python
"""
build_pylon.py -- vp0.7 antenna pylon (--out-dir): base, blade, knob.

base   8 mm peg into the rear node's top socket (M3 cross-bolt), a block on
       the node, a clevis with a serrated outer ear (M3, wave washer: 15 deg
       notches). Print inverted (ear tops down).
blade  faceted 140 mm blade: 6 mm serrated root tongue in the clevis, flares
       to a 28 x 14 octagonal section, tapers to 12 x 6; hollow (2.4 mm
       walls) to where it is 8 mm thick, Ø4 wire bore to the tip. Its
       inner face is flush with the tongue so it prints lying on that face.
knob   Ø24 lock knob on the hinge bolt's head: tighten by hand to lock.
Qty: 2 sets (same STLs both sides; the blade is mirrored in the assembly).
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

SX, SY = C.REAR_SOCKET                  # (-45, 90.5)
Z_TOP = C.CRADLE_Z + C.REAR_NODE_W[1]  # 70 node top
HZ = C.PYLON_HINGE_Z


def base(side=+1):
    bx, by, bz = C.PYLON_BASE
    g = C.HINGE_GAP / 2
    et, eh = C.PYLON_EAR_T, C.PYLON_EAR_H
    part = L.add_box("pylon_base", (SX, side * SY, Z_TOP + bz / 2), (28.0, 2 * (g + et), bz))
    L.fillet(part, width=1.0)
    for sy in (+1, -1):
        ear = L.add_box("ear", (SX, side * (SY + sy * (g + et / 2)), Z_TOP + bz + eh / 2 - 0.5), (28.0, et, eh + 1.0))
        L.fillet(ear, width=1.0)
        L.union(part, ear)
    L.union(part, L.add_cyl("peg", (SX, side * SY, Z_TOP - C.CYL_PEG_LEN / 2 + 0.5), C.CYL_PEG_D / 2, C.CYL_PEG_LEN + 1.0, axis="Z", verts=48))
    L.cut(part, L.add_cyl("cross", (SX, side * SY, Z_TOP - C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2, C.CYL_PEG_D + 4.0, axis="Y", verts=24))
    L.cut(part, L.add_cyl("bolt", (SX, side * SY, HZ), C.M3_CLEAR_DIA / 2, 2 * (g + et) + 4.0, axis="Y", verts=24))
    L.cut(part, L.add_hex_prism("nutp", (SX, side * (SY - g - et + 1.5 - 1.0), HZ), 5.7, 5.0, axis="Y"))   # nut pocket on the inner ear's outer face
    sr = C.HINGE_SERR
    L.union(part, L.serration_solid("serr", (SX, side * (SY + g), HZ), (0.0, -side, 0.0),
                                    r_in=sr["r_in"], r_out=sr["r_out"], teeth=sr["teeth"], height=sr["height"], phase_deg=sr["phase_ear"]))
    return part


def blade_frame(side=+1, angle=None):
    a = math.radians(C.PYLON_ANGLE if angle is None else angle)
    ez = Vector((-math.sin(a), 0.0, math.cos(a)))          # along the blade: up and back
    return L.frame((SX, side * SY, HZ), ez, (math.cos(a), 0.0, math.sin(a)))


def octagon(w, h, c):
    return [(w / 2 - c, -h / 2), (w / 2, -h / 2 + c), (w / 2, h / 2 - c), (w / 2 - c, h / 2),
            (-w / 2 + c, h / 2), (-w / 2, h / 2 - c), (-w / 2, -h / 2 + c), (-w / 2 + c, -h / 2)]


def loft(name, rings, M):
    verts, faces = [], []
    for z, poly in rings:
        verts += [M @ Vector((u, v, z)) for (u, v) in poly]
    n = len(rings[0][1])
    for i in range(len(rings) - 1):
        a, b = n * i, n * (i + 1)
        for k in range(n):
            faces.append((a + k, a + (k + 1) % n, b + (k + 1) % n, b + k))
    faces.append(tuple(reversed(range(n))))
    e = n * (len(rings) - 1)
    faces.append(tuple(e + k for k in range(n)))
    return L.obj_from_pydata(name, verts, faces)


def blade(side=+1, angle=None):
    M = blade_frame(side, angle)
    rw, rt = C.PYLON_ROOT
    bw, bt = C.PYLON_SECTION
    tw, tt = C.PYLON_TIP
    r = 10.0
    poly = [(r * math.cos(math.radians(180.0 + 180.0 * i / 24)), r * math.sin(math.radians(180.0 + 180.0 * i / 24))) for i in range(25)]
    poly = [(u, v) for (u, v) in poly]                        # lower half circle (v <= 0), u from -r to +r
    poly += [(rw / 2, C.PYLON_FLARE + 2.0), (-rw / 2, C.PYLON_FLARE + 2.0)]
    poly = poly[:1] + poly[1:]
    Mt = M @ Matrix.Translation((0.0, rt / 2 * side, 0.0)) @ Matrix.Rotation(math.pi / 2, 4, "X")   # tongue plane: u = local X, v = local Z; extrudes from +rt/2 toward -Y
    tongue = L.extrude_polygon("pylon_blade", poly, rt, Mt)
    # body: inner face flush with the tongue's inner face (local y = -rt/2), thickness grows outboard
    # every section keeps its inner face on the tongue's inner plane (local y = -rt/2 * side): the blade lies flat to print
    def sec(w, h, c):
        return [(u, v + side * (h - rt) / 2) for (u, v) in octagon(w, h, c)]
    rings = [(C.PYLON_FLARE - 4.0, sec(rw, rt - 0.2, 1.0)),
             (C.PYLON_FLARE + 4.0, sec(bw, bt, 3.0)),
             (C.PYLON_LEN, sec(tw, tt, 1.5))]
    body = loft("body", rings, M)
    L.union(tongue, body)
    L.fillet(tongue, width=0.8)
    # hollow: 2.4 mm walls from the flare to where the section is 8 mm thick, then a wire bore to the tip
    wall = C.PYLON_WALL
    zf, zt = C.PYLON_FLARE + 4.0, C.PYLON_LEN
    def outer(z):
        t = (z - zf) / (zt - zf)
        return bw + (tw - bw) * t, bt + (tt - bt) * t
    zc0 = zf + 8.0
    zc1 = zf + (zt - zf) * (bt - 8.0) / (bt - tt)          # section 8 mm thick here
    def inner(z):
        w, h = outer(z)
        return [(u, v + side * (h - rt) / 2) for (u, v) in octagon(w - 2 * wall, h - 2 * wall, 1.0)]
    L.cut(tongue, loft("cavity", [(zc0, inner(zc0)), (zc1, inner(zc1))], M))
    y_mid = side * (outer(zc1)[1] - rt) / 2
    L.cut(tongue, L.add_cyl_local("bore", M, (0.0, y_mid, (zc1 - 2.0 + zt + 1.0) / 2), C.PYLON_WIRE_D / 2, zt + 1.0 - (zc1 - 2.0), axis="Z", verts=16))
    L.cut(tongue, L.add_cyl_local("bolt", M, (0.0, 0.0, 0.0), C.M3_CLEAR_DIA / 2, rt + 4.0, axis="Y", verts=24))
    sr = C.HINGE_SERR
    face = M @ Vector((0.0, side * rt / 2, 0.0))
    L.union(tongue, L.serration_solid("serr", face, M.to_3x3() @ Vector((0.0, side, 0.0)),
                                      r_in=sr["r_in"], r_out=sr["r_out"], teeth=sr["teeth"], height=sr["height"], phase_deg=sr["phase_tongue"]))
    return tongue


def knob(side=+1):
    kd, kt = C.PYLON_KNOB
    g = C.HINGE_GAP / 2
    y0 = SY + g + C.PYLON_EAR_T + 1.0       # wave washer sits in the 1 mm
    k = L.add_cyl("pylon_knob", (SX, side * (y0 + kt / 2), HZ), kd / 2, kt, axis="Y", verts=64)
    for i in range(8):
        a = 2 * math.pi * i / 8
        L.cut(k, L.add_cyl("grip", (SX + (kd / 2 + 0.5) * math.cos(a), side * (y0 + kt / 2), HZ + (kd / 2 + 0.5) * math.sin(a)), 2.0, kt + 2.0, axis="Y", verts=16))
    L.fillet(k, width=0.6)
    L.cut(k, L.add_cyl("bolt", (SX, side * (y0 + kt / 2), HZ), C.M3_CLEAR_DIA / 2, kt + 2.0, axis="Y", verts=16))
    L.cut(k, L.add_cyl("head", (SX, side * (y0 + kt - 1.5 + 1.0), HZ), 3.1, 5.0, axis="Y", verts=16))
    return k


PARTS = {
    "pylon_base": (lambda: base(+1), L.ROT_FLIP, ["print inverted (ear tops on the bed, peg up); 16 mm bridge; no supports", "8 mm peg into the rear node's top socket, M3 cross-bolt; hinge M3 x 30 + wave washer, nut in the inner ear"]),
    "pylon_blade": (lambda: blade(+1, 0.0), L.rot_dir_to(Vector((0.0, 1.0, 0.0)), (0.0, 0.0, 1.0)), ["print lying on the flat (inner) face; no supports", "Ø4 wire bore from the flare to the tip"]),
    "pylon_knob": (lambda: knob(+1), L.ROT_Y_TO_Z, ["print flat; glue the M3 head into the pocket; tighten to lock the pylon"]),
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
