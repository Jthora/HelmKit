#!/usr/bin/env -S blender --background --python
"""
build_pod_shell.py -- vp0.4 pod: Ø122.1 paraboloid shell, dome outside, no cavity.

3 mm shell concave toward the head on a 16 mm rim ring (4 mm wall). Five
flush sockets in the ring, each locked by a nail in double shear driven from
the dome edge through the coupler and out under the foam. Nothing lives
inside: the pod is the shield/projector element itself.

Print: dome UP with supports under the shell (hidden by the foam ring), or
standing on its rim edge with a brim for a support-free print.
Qty: 2 (identical L/R).
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
from mathutils import Vector  # type: ignore

PRINT_ROT = L.ROT_Y_TO_Z
NOTES = ["print dome up with tree supports under the shell (or on edge with a brim: no supports); 0.12 mm layers for the dome",
         f"five flush ports at {C.POD_PORT_ANGLES}; nail {C.PIN_DIA} mm through the dome edge, coupler and ring bottom",
         "no electronics inside; foam ring OD 122 / ID 88 / 15 mm glued to the rim face"]


def n_out(r):
    return C.RING_H + C.DOME_SAG * (1.0 - (r / C.RING_IN_R) ** 2)


def make(side: int = +1):
    axis = "Y" if side > 0 else "-Y"                     # n = 0 at the cushion face, increasing outboard
    yc = side * C.RIM_Y
    rs = [C.RING_IN_R * i / 40 for i in range(41)]
    prof = [(r, n_out(r)) for r in rs]                   # outer surface: vertex -> ring inner edge
    prof += [(C.DISH_R, C.RING_H), (C.DISH_R, 0.0), (C.RING_IN_R, 0.0), (C.RING_IN_R, C.RING_H - C.SHELL_T)]
    prof += [(r, n_out(r) - C.SHELL_T) for r in reversed(rs[1:])]   # inner surface: ring -> near the vertex
    prof.append((0.0, n_out(0.0) - C.SHELL_T))
    shell = L.revolve("pod_shell", prof, axis=axis, center=(C.CX, yc, C.CZ), segments=160)
    frames = {ang: L.pod_port_frame(ang, side) for ang in C.POD_PORT_ANGLES}
    for ang, M in frames.items():
        L.union(shell, L.port_tunnel(f"tun{int(ang)}", M))
    L.fillet(shell, width=1.0)
    x_far = -(C.POD_PORT_Y - C.RIM_Y) - 1.0              # beyond the cushion face
    x_near = (C.RIM_Y + n_out(C.DISH_R - C.PORT_PIN_DEPTH)) - C.POD_PORT_Y + 1.0   # beyond the dome edge
    for ang, M in frames.items():
        L.cut(shell, L.port_socket_cut(M, tag=str(int(ang))))
        L.cut(shell, *L.port_pin_cutters(M, x_far, x_near, tag=str(int(ang))))
    return shell


if __name__ == "__main__":
    L.std_main(lambda: make(+1), PRINT_ROT, NOTES)
