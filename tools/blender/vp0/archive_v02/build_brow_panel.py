#!/usr/bin/env -S blender --background --python
"""
build_brow_panel.py -- vp0.2 flat rectangular brow panel with an LED bay.

160 x 50 x 12 shell, 2 mm walls, leaning back BROW_TILT deg to follow the
forehead, open toward the head with a recessed lid. 120 x 6 window in the
bottom face for a downward LED array. Four M3 holes through the front wall
(nut bosses inside) for the arm tabs, four M3 thread-forming lid screws,
two standard port sockets on the top edge.

Print: FRONT FACE DOWN (best finish on the visible face). No supports.
Qty: 1. Lid is build_brow_lid.py.
"""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
from mathutils import Matrix, Vector  # type: ignore

MP = L.frame(C.BROW_ORIGIN, C.BROW_EZ, C.BROW_EX)      # panel-local: x out, y = +Y, z up (tilted)
PRINT_ROT = L.rot_dir_to(C.BROW_EX, (0.0, 0.0, -1.0))  # front face on the bed
NOTES = ["print front face down; no supports; textured bed gives the visible face its finish",
         "hardware: 4x M3x10 + nuts (arms), 4x M3x8 thread-forming (lid)", f"leans back {C.BROW_TILT} deg"]

T, W, H, WALL = C.BROW_T, C.BROW_W, C.BROW_H, C.BROW_WALL
CAV_W = 140.0
CAV_Z = (4.0, H - 4.0)
LID_RECESS_D = 2.2
LID_SCREWS = ((-75.0, 10.0), (75.0, 10.0), (-75.0, H - 10.0), (75.0, H - 10.0))     # (y, local z)


def port_frames():
    out = []
    for y in C.BROW_PORTS_Y:
        mouth = MP @ Vector((T - C.PORT_BOSS / 2, y, H + C.PORT_BOSS_H))
        R = MP.to_3x3()
        out.append(L.frame(mouth, R @ Vector((0, 0, 1)), R @ Vector((1, 0, 0))))
    return out


def make():
    box = lambda n, c, d: L.add_box_local(n, MP, c, d)
    cyl = lambda n, c, r, d, ax: L.add_cyl_local(n, MP, c, r, d, axis=ax)
    panel = box("brow_panel", (T / 2, 0.0, H / 2), (T, W, H))
    frames = port_frames()
    for i, M in enumerate(frames):
        L.union(panel, L.port_boss(f"bboss{i}", M))
    for y, z in C.BROW_ARM_BOLTS:
        for sy in (+1, -1):
            L.union(panel, cyl("nutboss", (T - WALL - 1.5, sy * y, z), 4.0, 3.2, "X"))
    cz0, cz1 = CAV_Z
    cav_x0, cav_x1 = LID_RECESS_D, T - WALL
    L.cut(panel, box("cavity", ((cav_x0 + cav_x1) / 2, 0.0, (cz0 + cz1) / 2), (cav_x1 - cav_x0 + 0.01, CAV_W, cz1 - cz0)))
    L.cut(panel, box("recess", (LID_RECESS_D / 2 - 1.0, 0.0, H / 2), (LID_RECESS_D + 2.0, W - 2 * WALL + 0.4, H - 2 * WALL + 0.4)))
    ww, wt = C.BROW_LED_WINDOW
    L.cut(panel, box("ledwin", (T / 2, 0.0, 1.5), (wt, ww, 7.0)))
    for y, z in C.BROW_ARM_BOLTS:
        for sy in (+1, -1):
            L.cut(panel, cyl("armbolt", (T - 2.0, sy * y, z), C.M3_CLEAR_DIA / 2, 12.0, "X"))
            L.cut(panel, L.add_hex_prism_local("armnut", MP, (T - WALL - 2.6, sy * y, z), C.M3_NUT_AF + 0.3, 3.2, axis="X"))
    for y, z in LID_SCREWS:
        L.cut(panel, cyl("lidscrew", (5.0, y, z), C.M3_TAP_DIA / 2, 12.0, "X"))
    for i, M in enumerate(frames):
        L.cut(panel, *L.port_cutters(M, tag=f"b{i}"))
    return panel


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
