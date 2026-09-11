#!/usr/bin/env -S blender --background --python
"""
build_nape_core.py -- vp0.15 electronics core (--out-dir): the nape CORE BASE, its cap, the core PODS, the socket foot, button caps.

Local nape frame (build_nape_dial.M): u = -Y (wearer's right), v = W (up the band), w = outward. The pin-lock block spans
w -5.3 .. 5.3; the core base keeps that block (rack tunnels, four-lobe nail slot) and adds a JUNCTION BAY behind it
(w 5.3 .. 19.3): a hollow box, open outward, with two Ø4 harness holes through the block's web (u +/-22, between the rack
tunnels), a junction-board standoff pair, a connector window in the bottom wall for the belt umbilical with a strain-relief
hole, a jumper window in the outer wall, and two M3 bosses on the outer wall.

  nape_core_base   print standing on its bottom end like the pin-lock (nail holes vertical); the bay is a side pocket
  nape_core_cap    belt-only: closes the bay (2 mm plate, two M3 x 8 into the bosses)
  core_pod_nape    helm-only or both: 62 x 50 x 24 box on the base's outer face; Heltec on rails, LiPo under it, small boards
                   in the +v strip; OLED window in the lid, USB-C window in the +u end, three 12 mm tact switches in the top
                   (+v) wall under printed caps (the middle one large: the tally), slide-switch slot in the -u end, jumper
                   window in the back wall; two M3 x 8 from inside into the base's bosses
  core_pod_slab    the socket option: 62 x 22 x 40 slab standing on a rear-node socket via the socket foot; Heltec on edge (or
                   the LiPo + small boards in the second slab); OLED window and buttons on the outboard (-v) wall
  core_pod_lid_*   lids for both pods (four M3 x 8 into corner bosses)
  core_socket_foot 50 x 20 x 4 plate with the port-standard Ø8 peg (M3 cross-pin) and two M3 taps matching the pod's mount holes
  button_cap_s/l   caps for the tact switches

The pods are built in a local frame (x = u, y = v, z = depth from the back wall's outer face); the assembly places them.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import vp0lib as L
import canon as C
import build_nape_dial as ND
from mathutils import Matrix, Vector  # type: ignore

NC = C.NAPE_CORE
T = C.NAPE_PINLOCK_T                     # 10.6: the block spans w +/- 5.3
HU, HV = C.NAPE_HU, C.NAPE_HV
W_OUT = T / 2 + NC["bay_d"] + NC["wall"]  # 19.3: the base's outer face


def make_base():
    """Pin-lock block + junction bay."""
    base = ND.make_pinlock()
    base.name = "nape_core_base"
    wall, bd = NC["wall"], NC["bay_d"]
    w0, w1 = T / 2 - 0.1, W_OUT                                 # bay box from just inside the block's outer face to the outer wall
    bay = ND.box("bay", (0.0, 0.0, (w0 + w1) / 2), (HU, HV, w1 - w0))
    L.fillet(bay, width=0.8)
    L.union(base, bay)
    # cavity: open toward +w until the outer wall
    L.cut(base, ND.box("cav", (0.0, 0.0, (T / 2 + T / 2 + bd) / 2), (HU - 2 * wall, HV - 2 * wall, bd)))
    # harness holes through the block's web between the rack tunnels (v 0), inner face -> bay
    for u in (-NC["web_u"], NC["web_u"]):
        L.cut(base, ND.cyl("web", (u, 0.0, 0.0), NC["web_hole"] / 2, T + 1.0, verts=20))
    # junction board standoffs on the bay floor (the block's outer face): two Ø5 x 3 with M3 taps, 24 apart along u at v -6
    jw, jh, jst = NC["junction"]
    for u in (-12.0, 12.0):
        post = ND.cyl("post", (u, -6.0, T / 2 + jst / 2 - 0.05), 2.5, jst + 0.1, verts=20)
        L.union(base, post)
        L.cut(base, ND.cyl("ptap", (u, -6.0, T / 2 + jst - 1.5), C.M3_TAP_DIA / 2, 3.0 + 1.0, verts=12))   # 3.5 deep from the post top, clear of the rack tunnel below
    # umbilical connector window + strain relief in the bottom (v-) wall
    cw, ch = NC["conn"]
    L.cut(base, ND.box("connwin", (0.0, -HV / 2, T / 2 + bd / 2), (cw, wall + 2.0, ch)))
    ud, uz = NC["umbilical"]
    for u in (-12.0, 12.0):                                             # zip-tie slots through the bottom wall beside the window: the strain relief
        L.cut(base, ND.box("zip", (u, -HV / 2, T / 2 + bd / 2), (uz, wall + 2.0, 2.2)))
    # jumper window through the outer wall (to the pod), and the pod / cap bosses with taps
    ww, wh, wv = NC["window"]
    L.cut(base, ND.box("jwin", (0.0, wv, W_OUT - wall / 2), (ww, wh, wall + 2.0)))
    bdia, bh = NC["boss"]
    for (u, v) in NC["pod_screws"]:
        L.union(base, ND.cyl("boss", (u, v, W_OUT - wall - bh / 2 + 0.05), bdia / 2, bh + 0.1, verts=24))
        L.cut(base, ND.cyl("btap", (u, v, W_OUT - (wall + bh) / 2), C.M3_TAP_DIA / 2, wall + bh + 2.0, verts=12))
    return base


def make_cap():
    t = NC["cap_t"]
    cap = ND.box("nape_core_cap", (0.0, 0.0, W_OUT + t / 2), (HU, HV, t))
    L.fillet(cap, width=0.6)
    for (u, v) in NC["pod_screws"]:
        L.cut(cap, ND.cyl("screw", (u, v, W_OUT + t / 2), C.M3_CLEAR_DIA / 2, t + 2.0, verts=16))
        L.cut(cap, ND.cyl("csk", (u, v, W_OUT + t + 0.5 - 0.6), 2.9, 1.2, verts=16))
    L.cut(cap, ND.box("capwin", (0.0, NC["window"][2], W_OUT + t / 2), (NC["window"][0], NC["window"][1], t + 2.0)))   # the umbilical can also leave straight out
    return cap


# ---------------------------------------------------------------------------
# pods: local frame x = u, y = v, z = depth from the back wall's outer face (z 0 = on the base / foot)
# ---------------------------------------------------------------------------

def _pod(spec, name):
    iu, iv, iw = spec["inner"]
    wall, lt, reb = spec["wall"], spec["lid_t"], spec["rebate"]
    ou, ov = iu + 2 * wall, iv + 2 * wall
    H = wall + iw                                    # box height without the lid
    pod = L.add_box(name, (0.0, 0.0, H / 2), (ou, ov, H))
    L.fillet(pod, width=spec["fillet"])
    L.cut(pod, L.add_box("cav", (0.0, 0.0, wall + iw / 2 + 0.5), (iu, iv, iw + 1.0)))
    # lid rebate around the rim: leaves a `lip` wide outer lip
    lip = spec["lip"]
    L.cut(pod, L.add_box("rebate", (0.0, 0.0, H - reb / 2 + 0.5), (ou - 2 * lip, ov - 2 * lip, reb + 1.0)))
    # corner bosses with M3 taps for the lid
    b = spec["boss"]
    for sx in (+1, -1):
        for sy in (+1, -1):
            cx, cy = sx * (iu / 2 - b / 2 + 0.3), sy * (iv / 2 - b / 2 + 0.3)
            L.union(pod, L.add_box("boss", (cx, cy, wall + (iw - reb) / 2 - 0.05), (b, b, iw - reb + 0.1)))
            L.cut(pod, L.add_cyl("ltap", (cx, cy, H - 5.0), C.M3_TAP_DIA / 2, 10.0, axis="Z", verts=12))
    # mounting holes through the back wall (countersunk from inside? the heads sit inside the cavity on the floor)
    for (u, v) in spec["mount"]:
        L.cut(pod, L.add_cyl("mount", (u, v, wall / 2), C.M3_CLEAR_DIA / 2, wall + 2.0, axis="Z", verts=16))
    # jumper / cable window: in the back wall (nape pod) or the -u end wall near the floor (slab: the foot covers its back)
    cface, cw, ch, cpos = spec["cable_window"]
    if cface == "back":
        L.cut(pod, L.add_box("cwin", (0.0, cpos, wall / 2), (cw, ch, wall + 2.0)))
    else:
        L.cut(pod, L.add_box("cwin", (-iu / 2 - wall / 2, 0.0, wall + cpos), (wall + 2.0, cw, ch)))
    # board rails along u (nape pod): two ledges at v +/- gap/2, the board slides in from the lid side
    if spec.get("rails"):
        gap, rh, ledge = spec["rails"]
        for sy in (+1, -1):
            L.union(pod, L.add_box("rail", (0.0, sy * (gap / 2 + ledge / 2 + 0.6), wall + rh / 2 - 0.05), (iu - 2 * b - 1.0, ledge + 1.2, rh + 0.1)))
    # OLED window
    face, ow, oh, ou_ = spec["oled"][:4]
    if face == "-v":
        L.cut(pod, L.add_box("oled", (ou_, -iv / 2 - wall / 2, wall + iw * spec["oled"][4]), (ow, wall + 2.0, oh)))
    # USB window in the +u end wall
    uw, uh, ud = spec["usb"]
    L.cut(pod, L.add_box("usb", (iu / 2 + wall / 2, 0.0, wall + ud), (wall + 2.0, uw, uh)))
    # buttons: pockets on the inside of the wall + plunger holes through it; nape pod: +v (top) wall; slab: -v (outboard) wall
    pk, ph, us, bd = spec["buttons"]
    sy = -1.0 if face == "-v" else +1.0
    for u in us:
        L.cut(pod, L.add_box("bpocket", (u, sy * (iv / 2 - 0.6), wall + bd), (pk, 2.8, pk)))          # locating pocket 0.8 into the wall (1.2 mm left), the switch body sits in it
        L.cut(pod, L.add_cyl("bhole", (u, sy * (iv / 2 + wall / 2), wall + bd), ph / 2, wall + 2.0, axis="Y", verts=16))
    # slide switch slot in the -u end wall
    sw, sh = spec["slide"]
    L.cut(pod, L.add_box("slide", (-iu / 2 - wall / 2, iv / 2 - 6.0 if face != "-v" else 0.0, wall + iw * 0.5), (wall + 2.0, sw, sh)))
    return pod


def _lid(spec, name):
    iu, iv, iw = spec["inner"]
    wall, lt, reb = spec["wall"], spec["lid_t"], spec["rebate"]
    ou, ov = iu + 2 * wall, iv + 2 * wall
    H = wall + iw
    lid = L.add_box(name, (0.0, 0.0, H + lt / 2), (ou, ov, lt))
    lip = spec["lip"]
    L.union(lid, L.add_box("tongue", (0.0, 0.0, H - reb / 2 + 0.05), (ou - 2 * lip - 0.3, ov - 2 * lip - 0.3, reb + 0.1)))
    L.fillet(lid, width=0.6)
    b = spec["boss"]
    for sx in (+1, -1):
        for sy in (+1, -1):
            cx, cy = sx * (iu / 2 - b / 2 + 0.3), sy * (iv / 2 - b / 2 + 0.3)
            L.cut(lid, L.add_cyl("lscrew", (cx, cy, H + lt / 2), C.M3_CLEAR_DIA / 2, lt + reb + 2.0, axis="Z", verts=16))
            L.cut(lid, L.add_cyl("lcsk", (cx, cy, H + lt + 0.5 - 0.6), 2.9, 1.2, axis="Z", verts=16))
    face, ow, oh, ou_ = spec["oled"][:4]
    if face == "lid":
        L.cut(lid, L.add_box("oled", (ou_, 0.0, H + lt / 2), (ow, oh, lt + reb + 2.0)))
    return lid


def make_pod_nape():
    return _pod(C.POD_NAPE, "core_pod_nape")


def make_pod_nape_lid():
    return _lid(C.POD_NAPE, "core_pod_lid_nape")


def make_pod_slab():
    return _pod(C.POD_SLAB, "core_pod_slab")


def make_pod_slab_lid():
    return _lid(C.POD_SLAB, "core_pod_lid_slab")


def make_socket_foot():
    pw, pd, pt = C.SOCKET_FOOT["plate"]
    foot = L.add_box("core_socket_foot", (0.0, 0.0, pt / 2), (pw, pd, pt))
    L.fillet(foot, width=0.8)
    for (u, v) in C.SOCKET_FOOT["taps"]:
        L.cut(foot, L.add_cyl("tap", (u, v, pt / 2), C.M3_TAP_DIA / 2, pt + 2.0, axis="Z", verts=12))
    peg = L.add_cyl("peg", (0.0, 0.0, -C.CYL_PEG_LEN / 2 + 0.05), C.CYL_PEG_D / 2, C.CYL_PEG_LEN + 0.1, axis="Z", verts=48)
    L.union(foot, peg)
    L.cut(foot, L.add_cyl("cross", (0.0, 0.0, -C.CYL_PIN_Z), C.M3_CLEAR_DIA / 2, C.CYL_PEG_D + 4.0, axis="X", verts=24))
    return foot


def make_button_cap(large=False):
    ds, dl = C.BUTTON_CAP["d"]
    d = dl if large else ds
    h = C.BUTTON_CAP["h"]
    bd, bdep = C.BUTTON_CAP["bore"]
    cap = L.add_cyl("button_cap_l" if large else "button_cap_s", (0.0, 0.0, h / 2), d / 2, h, axis="Z", verts=48)
    L.fillet(cap, width=0.8)
    L.cut(cap, L.add_cyl("bore", (0.0, 0.0, bdep / 2 - 0.5), bd / 2, bdep + 1.0, axis="Z", verts=24))
    return cap


# placement helpers for the assembly ----------------------------------------------------------------

def nape_pod_matrix():
    """Pod local frame -> world: back wall on the base's outer face."""
    return ND.M @ Matrix.Translation((0.0, 0.0, W_OUT + 0.1))


def slab_matrix(side):
    """Slab pod on the rear-node socket of `side`: the foot plate on the node top, the pod's u along +x, its -v (buttons) outboard."""
    pt = C.SOCKET_FOOT["plate"][2]
    z0 = C.CRADLE_Z + C.REAR_NODE_W[1] + pt + 0.1
    rot = Matrix.Rotation(0.0 if side < 0 else math.pi, 4, "Z")     # -v must point outboard: for the left (+y) that is -y -> rotate 180 deg
    return Matrix.Translation((C.REAR_SOCKET[0], side * C.REAR_SOCKET[1], z0)) @ rot


def foot_matrix(side):
    pt = C.SOCKET_FOOT["plate"][2]
    return Matrix.Translation((C.REAR_SOCKET[0], side * C.REAR_SOCKET[1], C.CRADLE_Z + C.REAR_NODE_W[1] + 0.1))


PARTS = {
    "nape_core_base": (make_base, ND.PARTS["nape_pinlock"][1], ["print standing on its bottom end like the pin-lock (nail holes vertical; the bay is a side pocket, 12 mm bridges); brim",
                                                                 "junction perfboard 30 x 20 on the two posts (M3); helm harness in through the Ø4 web holes from the head side; umbilical through the bottom window with a zip tie on the cable inside; jumper to the pod through the outer window"]),
    "nape_core_cap": (make_cap, L.rot_dir_to(ND.N_OUT, (0, 0, -1)), ["belt-only: closes the bay; two countersunk M3 x 8 into the base bosses; print outer face down"]),
    "core_pod_nape": (make_pod_nape, L.ROT_NONE, ["print open side up (back wall on the bed); no supports (button pockets are 12 mm bridges)",
                                                  "Heltec V3 slides onto the rails from the lid side (OLED up), 1000 mAh LiPo under it, IMU / GSR / amp in the +v strip; two M3 x 8 from inside into the base; three 12 mm tact switches in the top wall under the caps; slide switch in the -u end"]),
    "core_pod_lid_nape": (make_pod_nape_lid, L.ROT_FLIP, ["print outer face down; OLED window; four countersunk M3 x 8"]),
    "core_pod_slab": (make_pod_slab, L.ROT_NONE, ["print open side up; the socket option: stands on a rear-node socket via the foot; Heltec on edge (or the LiPo + small boards in the second slab); OLED window and buttons on the outboard wall"]),
    "core_pod_lid_slab": (make_pod_slab_lid, L.ROT_FLIP, ["print outer face down; four countersunk M3 x 8"]),
    "core_socket_foot": (make_socket_foot, L.ROT_FLIP, ["print inverted (plate down, peg up); 8 mm peg into a rear-node socket with the M3 cross-pin; the pod's two mount screws go into the plate's taps"]),
    "button_cap_s": (lambda: make_button_cap(False), L.ROT_NONE, ["x2; press onto the tact switch plungers (round / mode)"]),
    "button_cap_l": (lambda: make_button_cap(True), L.ROT_NONE, ["x1; the tally button: tap the back of your head"]),
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
