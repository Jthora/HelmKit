#!/usr/bin/env -S blender --background --python
"""
build_brow_panel.py -- vp0.3 brow panel: flat 100 mm centre + two wings swept back 20 deg.

12 mm shell, 2 mm walls, LED window in the bottom face, lid recess on the head
side, a flush port socket in each wing end facing the pod's front port (the
strut is a straight coupler along the panel normal). Panel leans back 13 deg.
Print: standing on its bottom face. Qty: 1. Lid: build_brow_lid.py.
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

MP = L.frame(C.BROW_ORIGIN, C.BROW_EZ, C.BROW_EX)          # local x = outward, y = +Y, z = up (tilted)
PRINT_ROT = L.rot_dir_to(C.BROW_EZ, (0, 0, 1))
T, H = C.BROW_T, C.BROW_H
WING = math.radians(C.BROW_WING_ANGLE)
LID_RECESS = 2.2


def wing_end_local(side):
    """Centre of the wing's end (mid-thickness), panel-local coordinates."""
    return Vector((T / 2 - C.BROW_WING_LEN * math.sin(WING), side * (C.BROW_CENTER_W / 2 + C.BROW_WING_LEN * math.cos(WING)), C.BROW_STRUT_LOCAL_Z))


def wing_socket_frame(side):
    """Mouth frame of the wing-end socket: faces the pod (local -x), screw along +/-Y."""
    e = wing_end_local(side)
    mouth_local = Vector((e.x - C.PORT_BLOCK_LEN / 2, e.y, e.z))
    mouth = MP @ mouth_local
    ez = -Vector(C.BROW_EX)
    return L.frame(mouth, ez, (0.0, side, 0.0))


def coupler_len(side=+1):
    """Brow strut length: pod front-port mouth to wing socket mouth, plus both plugs."""
    Mpod = L.pod_port_frame(C.FRONT_PORT_ANGLE, side)
    Mw = wing_socket_frame(side)
    pm = Vector((Mpod[0][3], Mpod[1][3], Mpod[2][3]))
    wm = Vector((Mw[0][3], Mw[1][3], Mw[2][3]))
    return (wm - pm).length + 2 * C.PORT_PLUG_LEN


BROW_COUPLER_LEN = coupler_len(+1)
NOTES = ["print standing on the bottom face; brim; no supports",
         f"struts: 2x coupler {BROW_COUPLER_LEN:.1f} mm ({C.COUPLER_TUBE}); nail pins through the wing blocks, thread-wrap collars",
         "hardware: 4x M3x8 thread-forming (lid); 96x44x12 foam pad on the lid"]


def make():
    panel = L.add_box_local("brow_panel", MP, (T / 2, 0.0, H / 2), (T, C.BROW_CENTER_W + 2.0, H))
    for side in (+1, -1):
        Mw = MP @ Matrix.Translation((T / 2, side * C.BROW_CENTER_W / 2, H / 2)) @ Matrix.Rotation(side * WING, 4, "Z")
        L.union(panel, L.add_box_local("wing", Mw, (0.0, side * (C.BROW_WING_LEN / 2), 0.0), (T - 0.2, C.BROW_WING_LEN + 2.0, H - 0.2)))
        e = wing_end_local(side)
        Mb = L.frame(MP @ e, Vector(C.BROW_EX), (0.0, side, 0.0))
        L.union(panel, L.add_box_local("wingblock", Mb, (0.0, 0.0, 0.0), (C.PORT_BLOCK, C.PORT_BLOCK, C.PORT_BLOCK_LEN)))
    L.fillet(panel)          # outer edges; the cuts below stay crisp
    # cavity + lid recess + LED window (centre section only)
    cav_x0, cav_x1 = LID_RECESS, T - C.BROW_WALL
    L.cut(panel, L.add_box_local("cavity", MP, ((cav_x0 + cav_x1) / 2, 0.0, H / 2), (cav_x1 - cav_x0, C.BROW_CAV_W, H - 2 * 4.0)))
    L.cut(panel, L.add_box_local("recess", MP, (LID_RECESS / 2 - 1.0, 0.0, H / 2), (LID_RECESS + 2.0, C.BROW_CAV_W + 8.0, H - 2 * C.BROW_WALL + 0.4)))
    ww, wt = C.BROW_LED_WINDOW
    L.cut(panel, L.add_box_local("ledwin", MP, (T / 2, 0.0, 1.5), (wt, ww, 7.0)))
    for y, z in C.BROW_LID_SCREWS:
        L.cut(panel, L.add_cyl_local("lidscrew", MP, (4.0, y, z), C.M3_TAP_DIA / 2, 12.0, axis="X", verts=16))
    for side in (+1, -1):
        Ms = wing_socket_frame(side)
        L.cut(panel, L.port_socket_cut(Ms, tag=f"w{side}"))
        L.cut(panel, *L.port_pin_cutters(Ms, -(C.PORT_BLOCK / 2 + 1.0), C.PORT_BLOCK / 2 + 1.0, tag=f"w{side}"))
        L.cut(panel, L.collar_cutter(Ms, -C.PORT_BLOCK_LEN / 2.0, C.PORT_BLOCK, tag=f"w{side}"))
    return panel


if __name__ == "__main__":
    L.std_main(make, PRINT_ROT, NOTES)
