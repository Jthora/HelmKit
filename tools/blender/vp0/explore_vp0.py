#!/usr/bin/env -S blender --background --python
"""
explore_vp0.py -- the STRUCTURAL PROTOTYPE (v0.18) as one .blend to explore how it goes together.

Every printed part of the build in its worn place, named by its print file and coloured as printed (black / grey PLA);
every nail, bolt, nut, screw, washer and spring in its hole; and a TIMELINE that puts it together in the order of the
assembly instructions. Frame 1 is fully exploded; each step slides its parts in along their real insertion path (the
disks turn through the bayonet); the last frame is the finished helm. Timeline markers name the steps.
Tinkering: every part's origin is at its centre, or on its pivot where it has one (disks on their axis, pylon blades on
the hinge); the VISOR empty swings the whole brow on the disk axis. The text block reset_parts puts everything back.

--check sweeps every step's moving parts along their path against the parts they meet (shared volume sampled on a
grid, the method that found the first assembly's faults: surface contact alone hid them) and writes a per-step result.

Run (from the repo root):
    blender --background --python tools/blender/vp0/explore_vp0.py -- \\
        [--blend 3D-Models/HelmKit_vp0/vp0_explore.blend] [--check report.txt] [--renders DIR]
"""
from __future__ import annotations
import math, sys, time
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import bpy  # type: ignore
import bmesh  # type: ignore
from mathutils import Matrix, Vector  # type: ignore
from mathutils.bvhtree import BVHTree  # type: ignore
import vp0lib as L
import canon as C
import assemble_vp0 as A
import build_disk, build_nexus, build_crown_arch_half, build_apex_block, build_cradle_front, build_rear_band_half
import build_brow_center, build_brow_rail, build_brow_link, build_visor_slider, build_brow_lid, build_nape_core, build_nape_dial
import build_pylon, build_port_parts

DEFAULT_BLEND = "3D-Models/HelmKit_vp0/vp0_explore.blend"
STEP_FRAMES, GAP, LEAD, TAIL = 30, 8, 12, 24

COLOURS = {"black": ((0.040, 0.042, 0.047, 1.0), 0.0, 0.55), "grey": ((0.46, 0.47, 0.49, 1.0), 0.0, 0.5),
           "steel": ((0.80, 0.81, 0.84, 1.0), 0.9, 0.3), "zinc": ((0.62, 0.65, 0.70, 1.0), 0.9, 0.35),
           "nail": ((0.72, 0.68, 0.60, 1.0), 0.8, 0.4), "spring": ((0.90, 0.72, 0.28, 1.0), 0.9, 0.3),
           "foam": ((0.20, 0.22, 0.28, 1.0), 0.0, 0.9), "skin": ((0.85, 0.66, 0.55, 0.22), 0.0, 0.8)}

OB: dict[str, bpy.types.Object] = {}        # key -> object
INFO: dict[str, dict] = {}                   # key -> custom properties
HW_ROWS: list[tuple[str, str, str]] = []     # (key, what, where) for the README's hardware list


# ---------------------------------------------------------------------------
# scene helpers
# ---------------------------------------------------------------------------

def material(name):
    m = bpy.data.materials.get(f"vp0x_{name}")
    if m:
        return m
    rgba, metal, rough = COLOURS[name]
    m = bpy.data.materials.new(f"vp0x_{name}")
    m.diffuse_color = rgba
    m.metallic, m.roughness = metal, rough
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Metallic"].default_value = metal
        bsdf.inputs["Roughness"].default_value = rough
        if rgba[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    if rgba[3] < 1.0 and hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    return m


def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def put(key, ob, name, colour, coll, **info):
    """Register an object: name, colour, collection, custom properties. Transforms are baked first (matrix = identity)."""
    if ob.type == "MESH":
        mw = ob.matrix_world.copy()
        if mw != Matrix.Identity(4):
            ob.data.transform(mw)
            ob.matrix_world = Matrix.Identity(4)
    ob.name = name
    if ob.data and hasattr(ob.data, "materials"):
        ob.data.materials.clear()
        ob.data.materials.append(material(colour))
    ob.color = COLOURS[colour][0]
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)
    OB[key] = ob
    INFO[key] = info
    return ob


def bbox_centre(ob):
    if ob.type == "MESH":
        vs = [v.co for v in ob.data.vertices]
    else:
        vs = [Vector(p.co[:3]) for s in ob.data.splines for p in s.points]
    lo = Vector([min(v[i] for v in vs) for i in range(3)])
    hi = Vector([max(v[i] for v in vs) for i in range(3)])
    return (lo + hi) / 2


def set_origin(ob, o):
    o = Vector(o)
    ob.data.transform(Matrix.Translation(-o))
    ob.location = o


# ---------------------------------------------------------------------------
# hardware (modelled to read clearly, shanks 0.1 under nominal so a screw in a tapped pilot does not register as a clash)
# ---------------------------------------------------------------------------

def _cone(bm, M, r0, r1, z0, z1, segs=24):
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r0, radius2=r1, depth=z1 - z0,
                          matrix=M @ Matrix.Translation((0.0, 0.0, (z0 + z1) / 2)))


def fastener(name, pt, axis, length, kind):
    """pt = the head's bearing face on the axis (for a countersunk screw: the head's top face); axis = into the work."""
    M = L.frame(Vector(pt), Vector(axis).normalized())
    bm = bmesh.new()
    if kind == "m3_cap":          # socket head cap screw
        _cone(bm, M, 2.75, 2.55, -3.0, 0.0); _cone(bm, M, 1.4, 1.4, -0.01, length - 0.3); _cone(bm, M, 1.4, 1.1, length - 0.3, length)
    elif kind == "m3_pan":        # self-tapping pan head
        _cone(bm, M, 2.8, 2.2, -2.0, 0.0); _cone(bm, M, 1.4, 1.4, -0.01, length - 1.5); _cone(bm, M, 1.4, 0.5, length - 1.5, length, segs=16)
    elif kind == "m3_csk":        # countersunk: pt is the head's top
        _cone(bm, M, 2.9, 1.4, 0.0, 1.7); _cone(bm, M, 1.4, 1.4, 1.69, length - 0.3); _cone(bm, M, 1.4, 1.1, length - 0.3, length)
    elif kind == "m4_cap":
        _cone(bm, M, 3.5, 3.3, -4.0, 0.0); _cone(bm, M, 1.9, 1.9, -0.01, length - 0.4); _cone(bm, M, 1.9, 1.5, length - 0.4, length)
    elif kind == "nail12_cut":    # 12 ga common nail, cut to length and filed flat
        _cone(bm, M, 3.4, 3.2, -1.2, 0.0, segs=32); _cone(bm, M, 1.34, 1.34, -0.01, length)
    elif kind == "nail16":        # 16 ga common nail, point left on
        _cone(bm, M, 2.0, 1.9, -0.8, 0.0); _cone(bm, M, 0.795, 0.795, -0.01, length - 1.6, segs=16); _cone(bm, M, 0.795, 0.05, length - 1.6, length, segs=16)
    else:
        raise ValueError(kind)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def nut(name, center, axis, af=5.5, t=2.4, hole=1.5, about=None):
    """Hex nut built with the same primitive call as the pockets (same flats orientation); `about` = (angle_deg, pivot_xz)
    replays the cradle's 7-degree pocket rotation about Y."""
    ob = L.add_hex_prism(name, center, af, t, axis=axis)
    L.cut(ob, L.add_cyl("hole", center, hole, t + 2.0, axis=axis, verts=20))
    if about:
        ang, (px, pz) = about
        ob.matrix_world = Matrix.Translation((px, 0.0, pz)) @ Matrix.Rotation(math.radians(ang), 4, "Y") @ Matrix.Translation((-px, 0.0, -pz)) @ ob.matrix_world
        L.apply_transform(ob)
    return ob


def washer(name, center, axis, r_in, r_out, t):
    return L.revolve(name, [(r_in, 0.0), (r_out, 0.0), (r_out, t), (r_in, t)], axis=axis, center=center, segments=64)


def spring(name, M, z0, z1, r_mean, wire_r, turns):
    """Helix along local Z of frame M as a bevelled curve."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = wire_r
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    n = int(turns * 24)
    sp.points.add(n)
    for i in range(n + 1):
        a = 2 * math.pi * turns * i / n
        p = M @ Vector((r_mean * math.cos(a), r_mean * math.sin(a), z0 + (z1 - z0) * i / n))
        sp.points[i].co = (p.x, p.y, p.z, 1.0)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def hw(key, ob, what, where, coll, colour="steel"):
    HW_ROWS.append((key, what, where))
    return put(key, ob, f"{what} · {where}", colour, coll, hardware=what, where=where)


# ---------------------------------------------------------------------------
# the build
# ---------------------------------------------------------------------------

SIDES = ((+1, "L"), (-1, "R"))
GROUPS = ("1 Ring: cradle, rear halves, nape", "2 Hubs: spool, visor rail, nexus flange", "3 Brow: panel, faceplate, links",
          "4 Crown: couplers, arch halves, apex", "5 Antennas: pylons", "6 Disks", "Reference (not printed)")


def build():
    Y = lambda s: Vector((0.0, s, 0.0))
    for name in GROUPS:                  # created up front so the Outliner lists them in build order
        collection(name)
    # ---- 1 ring: cradle, rear halves, nape block -----------------------------------------------------------------
    ring = collection("1 Ring: cradle, rear halves, nape")
    ring_hw = collection("1 Ring hardware", ring)
    put("cradle", build_cradle_front.make(), "cradle_front", "black", ring, print_file="black-pla/cradle_front", count=1,
        connects="rear halves' tenons into the two rear nodes (12 ga nail each); hub nodes carry the nexus stacks (3 x M3 x 30 each) and the crown couplers; rear nodes carry the pylon pegs")
    Mn = build_nape_dial.M
    rl, rr = build_rear_band_half.make(+1), build_rear_band_half.make(-1)
    for ob in (rl, rr):                 # FIELD MOD: the pin-lock's nails cannot pass the solid rack strips; drill through them
        for u in NAPE_DRILL_U:
            L.cut(ob, L.add_cyl_local("drill", Mn, (u, 0.0, 0.0), NAPE_DRILL_D / 2, C.NAPE_HV + 4.0, axis="Y", verts=16))
    put("rear_L", rl, "rear_band_half (LEFT)", "black", ring, print_file="black-pla/rear_band_half", count=1, field_mod=f"two Ø{NAPE_DRILL_D} holes drilled through the rack strip, through the nape block's holes 1 and 3, at your fit",
        connects="tenon slides into the cradle's LEFT rear node along the band (up and forward, 49 deg), 12 ga nail across; its rack strip runs through the nape block's upper tunnel")
    put("rear_R", rr, "rear_band_half_R (RIGHT)", "black", ring, print_file="black-pla/rear_band_half_R", count=1, field_mod=f"two Ø{NAPE_DRILL_D} holes drilled through the rack strip with the left one",
        connects="tenon into the RIGHT rear node, 12 ga nail across; its rack strip runs through the nape block's lower tunnel")
    put("nape", build_nape_core.make_base(), "nape_core_base", "black", ring, print_file="black-pla/nape_core_base", count=1,
        connects="the two racks slide through its tunnels from opposite ends; at your fit, drill holes 1 and 3 through both racks (the block is the jig), then a 1 inch 16 ga nail from the top in hole 1 (locks the left rack) and one from the bottom in hole 3 (locks the right rack); cap screws onto the bay")
    put("cap", build_nape_core.make_cap(), "nape_core_cap", "black", ring, print_file="black-pla/nape_core_cap", count=1,
        connects="closes the junction bay: two countersunk M3 x 8")
    pz = C.REAR_START[2] + 6.0 * C.REAR_T_IN[2]
    for s, t in SIDES:
        y0 = C.NODE_IN_Y + C.PIN_HEAD_DEPTH
        hw(f"tnail_{t}", fastener("n", (C.TENON_PIN_X, s * y0, pz), Y(s), C.NODE_OUT_Y - y0, "nail12_cut"),
           f"12 ga nail cut to {C.NODE_OUT_Y - y0:.0f} mm", f"tenon {t}", ring_hw, "nail")
    cb_d, cb_h = C.NAPE_PINLOCK_PIN["cbore"]
    R3 = Mn.to_3x3()
    hw("nnail_0", fastener("n", Mn @ Vector((NAPE_DRILL_U[0], C.NAPE_HV / 2 - cb_h, 0.0)), R3 @ Vector((0.0, -1.0, 0.0)), NAPE_NAIL_LEN, "nail16"),
       '16 ga nail 1"', "nape hole 1, from the top (left rack)", ring_hw, "nail")
    hw("nnail_1", fastener("n", Mn @ Vector((NAPE_DRILL_U[1], -C.NAPE_HV / 2, 0.0)), R3 @ Vector((0.0, 1.0, 0.0)), NAPE_NAIL_LEN, "nail16"),
       '16 ga nail 1"', "nape hole 3, from the bottom (right rack)", ring_hw, "nail")
    W_OUT = build_nape_core.W_OUT
    for i, (u, v) in enumerate(C.NAPE_CORE["pod_screws"]):
        hw(f"capscrew_{i}", fastener("s", Mn @ Vector((u, v, W_OUT + C.NAPE_CORE["cap_t"])), Mn.to_3x3() @ Vector((0.0, 0.0, -1.0)), 8.0, "m3_csk"),
           "M3 x 8 countersunk", f"nape cap {i + 1}", ring_hw)

    # ---- 2 hubs: spool, visor rail (with its pawl slider), washer, nexus flange ----------------------------------
    hubs = collection("2 Hubs: spool, visor rail, nexus flange")
    hubs_hw = collection("2 Hubs hardware", hubs)
    vp = C.VISOR_PAWL
    for s, t in SIDES:
        put(f"spool_{t}", build_nexus.spool(s), f"nexus_spool.{t}", "black", hubs, print_file="black-pla/nexus_spool", count=2,
            connects="flat plate against the hub node's outer face; the visor rail's ring turns on its Ø36 hub; the three nexus bolts pass through")
        put(f"rail_{t}", build_brow_rail.make(s), f"brow_rail_{t}", "grey", hubs, print_file=f"grey-pla/brow_rail_{t}", count=1,
            connects="Ø36.7 ring over the spool hub, arm forward; pawl slider in its tunnel clicks into the hub's notches; the brow link's lap fits its half-lap at the front end (2 x M3 x 10)")
        put(f"slider_{t}", build_visor_slider.make(s), f"visor_slider.{t}", "black", hubs, print_file="black-pla/silver_small_parts (plate)", count=2,
            connects="pawl in the rail's tunnel: tip into the hub notches, spring on its stem, thumb tab out of the rail's top edge")
        Mr = build_brow_rail.rail_frame(C.RAIL_ANGLE, s)
        yc = s * (vp["y0"] + vp["slot"][0] / 2.0)
        Ms = Mr @ Matrix.Translation((0.0, yc, 0.0)) @ Matrix.Rotation(math.pi / 2, 4, "Y")       # local z = the rail axis
        hw(f"pspring_{t}", spring("sp", Ms, vp["body_r"] + 1.0, vp["r_spring"], 1.3, 0.15, 7), "Ø3 x 10 spring", f"visor pawl {t}", hubs_hw, "spring")
        put(f"nexus_{t}", build_nexus.flange(s), f"nexus_{t}", "black", hubs, print_file=f"black-pla/nexus_{t}", count=1,
            connects="Ø68 flange over the spool, stalk outward: the disk's bayonet locks onto its two lugs; three M3 x 30 from outside through flange, spool and node")
        y_w = C.NEXUS_RING_Y0 + C.NEXUS_RING[2] + 0.1
        hw(f"washer_{t}", washer("w", (C.CX, s * y_w, C.CZ), "Y" if s > 0 else "-Y", 18.3, 21.5, 0.8), "thin washer Ø36.6 x 0.8", f"rail ring {t}", hubs_hw, "zinc")
        cd, cdep = C.NEXUS_HEAD_CBORE
        af, pdep = C.NEXUS_NUT_POCKET
        for i, (x, z) in enumerate(C.NEXUS_BOLTS):
            hw(f"nbolt_{t}{i}", fastener("b", (x, s * (C.NEXUS_Y[1] - cdep), z), Y(-s), 30.0, "m3_cap"), "M3 x 30", f"nexus {t}{i + 1}", hubs_hw)
            hw(f"nnut_{t}{i}", nut("n", (x, s * (C.NODE_IN_Y + pdep - 1.2), z), "Y", about=(7.0, (x, z))), "M3 nut", f"nexus {t}{i + 1} (node pocket)", hubs_hw, "zinc")

    # ---- 3 disks ---------------------------------------------------------------------------------------------------
    disks = collection("6 Disks")
    disks_hw = collection("6 Disks hardware", disks)
    trav = build_disk.lock_travel_deg()
    kb = C.DISK_KNOB
    for s, t in SIDES:
        Ma = build_disk.axis_frame(s)
        Rl = Ma @ Matrix.Rotation(-math.radians(trav), 4, "Z") @ Ma.inverted()      # entry pose -> turned to the stop (worn)
        dome = build_disk.dome(s, saddle=False); dome.matrix_world = Rl; L.apply_transform(dome)
        back = build_disk.back(s); back.matrix_world = Rl; L.apply_transform(back)
        put(f"dome_{t}", dome, f"disk_dome.{t}", "grey", disks, print_file="grey-pla/disk_dome", count=2,
            connects="six M3 x 10 from the back plate's side into its bosses; the knob's shaft passes through its apex")
        put(f"back_{t}", back, f"disk_back_{t}", "black", disks, print_file=f"black-pla/disk_back_{t}", count=1,
            connects="the bayonet: two notches take the nexus stalk's lugs, then the disk turns to the stop and the cam groove pulls it tight")
        Mk = Matrix.Translation((C.CX, s * (C.DISK_IN_Y + C.DISK_THICK + 0.2), C.CZ)) @ Matrix.Rotation(s * math.pi / 2, 4, "X")
        put(f"knob_{t}", A.placed(build_nexus.disk_knob(), Mk), f"disk_knob.{t}", "black", disks, print_file="black-pla/disk_knob", count=2,
            connects="through the dome's apex hole from outside, shaft down the axis into the stalk; the clip holds it (decorative until the lock is designed)")
        Mc = Matrix.Translation((C.CX, s * (C.DISK_IN_Y + kb["clip_n"] - kb["clip"][2] / 2), C.CZ)) @ Matrix.Rotation(-s * math.pi / 2, 4, "X")
        put(f"clip_{t}", A.placed(build_nexus.knob_clip(), Mc), f"knob_clip.{t}", "black", disks, print_file="black-pla/silver_small_parts (plate)", count=2,
            connects="snaps sideways into the knob shaft's groove inside the dome")
        for k in range(C.DISK_SCREWS):
            a = math.radians(30.0 + 360.0 * k / C.DISK_SCREWS)
            p = Rl @ Ma @ Vector((C.DISK_SCREW_R * math.cos(a), C.DISK_SCREW_R * math.sin(a), 0.0))
            hw(f"dscrew_{t}{k}", fastener("s", p, Y(s), 10.0, "m3_pan"), "M3 x 10 self-tapping", f"disk {t}{k + 1}", disks_hw)

    # ---- 4 brow ----------------------------------------------------------------------------------------------------
    brow = collection("3 Brow: panel, faceplate, links")
    brow_hw = collection("3 Brow hardware", brow)
    MP = build_brow_center.MP
    put("panel", build_brow_center.make(), "brow_center", "grey", brow, print_file="grey-pla/brow_center", count=1,
        connects="each link's bar into a pocket in its back face (one M3 x 16 from underneath); faceplate in the front recess (4 x M3 x 8)")
    put("lid", build_brow_lid.make(), "brow_lid (faceplate)", "grey", brow, print_file="grey-pla/brow_lid", count=1,
        connects="drops into the panel's front recess, four M3 x 8")
    x0 = C.BROW_T - build_brow_center.LID_RECESS + 0.2
    for i, (y, z) in enumerate(C.BROW_LID_SCREWS):
        hw(f"fscrew_{i}", fastener("s", MP @ Vector((x0 + C.BROW_LID_T, y, z)), MP.to_3x3() @ Vector((-1.0, 0.0, 0.0)), 8.0, "m3_pan"), "M3 x 8", f"faceplate {i + 1}", brow_hw)
    cbd, cbh = C.BROW_LINK["screw_cbore"]
    for s, t in SIDES:
        put(f"link_{t}", build_brow_link.make(s), f"brow_link_{t}", "grey", brow, print_file=f"grey-pla/brow_link_{t}", count=1,
            connects="lap screws onto the rail's half-lap (2 x M3 x 10 from the rail's outer face); its bar bends inboard into the panel's back pocket (M3 x 16 from below)")
        Mk = MP @ Matrix.Translation((0.0, s * C.BROW_POCKET_Y, C.BROW_POCKET_Z)) @ Matrix.Rotation(-s * math.radians(C.BROW_LINK["angle"]), 4, "Z")
        zb = -C.BROW_POCKET_Z - 1.0
        for d in C.BROW_LINK["screws_d"]:
            hw(f"lscrew_{t}", fastener("s", Mk @ Vector((d, 0.0, zb + cbh)), Mk.to_3x3() @ Vector((0.0, 0.0, 1.0)), 16.0, "m3_cap"), "M3 x 16", f"brow link {t} into panel", brow_hw)
        Mr = build_brow_rail.rail_frame(C.RAIL_ANGLE, s)
        for i, sb in enumerate(C.RAIL_BOLTS_S):
            hw(f"rbolt_{t}{i}", fastener("s", Mr @ Vector((sb, s * (C.RAIL_Y0 + C.RAIL_T - 1.5), 0.0)), Y(-s), 10.0, "m3_pan"), "M3 x 10", f"rail {t} lap {i + 1}", brow_hw)

    # ---- 5 crown ---------------------------------------------------------------------------------------------------
    crown = collection("4 Crown: couplers, arch halves, apex")
    crown_hw = collection("4 Crown hardware", crown)
    sx, sy = C.HUB_SOCKET
    z_c0 = C.CRADLE_Z + C.HUB_NODE_W[1] - C.CYL_DEPTH
    for s, t in SIDES:
        Mcp = Matrix.Translation((sx, s * sy, z_c0)) @ Matrix.Rotation(math.pi / 2, 4, "Z")      # turned so its cross holes run along Y, as the node's
        put(f"coupler_{t}", A.placed(build_port_parts.coupler(), Mcp), f"port_coupler.{t}", "black", crown, print_file="black-pla/port_coupler", count=2,
            connects="lower half in the hub node's top socket, pinned by a 12 ga nail from INSIDE cut flush (the hole's outer end is under the nexus spool, so no bolt fits); upper half in the arch foot's socket, M3 x 20 across")
        hw(f"ccnail_{t}", fastener("n", (sx, s * C.NODE_IN_Y, C.HUB_CROSS_Z), Y(s), C.HUB_NODE_OUT_Y - C.NODE_IN_Y, "nail12_cut"),
           f"12 ga nail cut to {C.HUB_NODE_OUT_Y - C.NODE_IN_Y:.0f} mm", f"coupler {t} in hub node (from inside)", crown_hw, "nail")
        fy = C.CROWN_FOOT[1]
        hw(f"cfbolt_{t}", fastener("b", (C.CX, s * (sy + fy / 2), C.CROWN_CROSS_Z), Y(-s), 20.0, "m3_cap"), "M3 x 20", f"crown foot {t}", crown_hw)
        hw(f"cfnut_{t}", nut("n", (C.CX, s * (sy - fy / 2 - 1.2), C.CROWN_CROSS_Z), "Y"), "M3 nut", f"crown foot {t}", crown_hw, "zinc")
    arch = build_crown_arch_half.make()
    put("arch_L", L.transformed_copy(arch, Matrix.Translation((ARCH_GAP / 2, 0.0, 0.0)), "aL"), "crown_arch_half.L", "grey", crown,
        print_file="grey-pla/crown_arch_half", count=2, connects="foot over the left coupler (M3 x 20 across); its flat top bar lies in the apex channel, ridges meshed with the right half's")
    put("arch_R", L.transformed_copy(arch, Matrix.Translation((-ARCH_GAP / 2, 0.0, 0.0)) @ build_crown_arch_half.right_half_matrix(), "aR"), "crown_arch_half.R", "grey", crown,
        print_file="grey-pla/crown_arch_half (the same file, turned round)", count=2, connects="the same print as the left, turned 180 deg about the vertical")
    L.delete(arch)
    put("apex", build_apex_block.make(), "apex_block", "grey", crown, print_file="grey-pla/apex_block", count=1,
        connects="open-topped channel: both bars drop in from above, ridges together; one M4 through both walls and both bars' slots clamps them")
    zA = C.CROWN_APEX_Z
    sxa = C.APEX_SLEEVE[0]
    hw("m4", fastener("b", (C.CX + sxa / 2 - 3.5, 0.0, zA), (-1.0, 0.0, 0.0), M4_LEN, "m4_cap"), f"M4 x {M4_LEN:.0f}", "apex clamp", crown_hw)
    hw("m4nut", nut("n", (C.CX - sxa / 2 + C.M4_NUT_T / 2, 0.0, zA), "X", af=C.M4_NUT_AF, t=C.M4_NUT_T, hole=2.0), "M4 nut", "apex clamp (pocket)", crown_hw, "zinc")

    # ---- 6 antennas (pylons) ---------------------------------------------------------------------------------------
    ant = collection("5 Antennas: pylons")
    ant_hw = collection("5 Antennas hardware", ant)
    SX, SY, HZ = build_pylon.SX, build_pylon.SY, build_pylon.HZ
    Mz = A.rot_about_z(SX)
    peg = A.placed(build_pylon.peg(+1), Matrix.Translation((SX, SY, 0.0)) @ Matrix.Rotation(math.pi / 2, 4, "Z") @ Matrix.Translation((-SX, -SY, 0.0)))   # cross hole along Y
    base, blade, knob = build_pylon.base(+1), build_pylon.blade(+1), build_pylon.knob(+1)
    g = C.HINGE_GAP / 2
    y_knob = SY + g + C.PYLON_EAR_T + 1.0
    for s, t in SIDES:
        M = Matrix.Identity(4) if s > 0 else Mz
        put(f"peg_{t}", L.transformed_copy(peg, M, "p"), f"pylon_peg.{t}", "black", ant, print_file="black-pla/pylon_peg", count=2,
            connects="lower 14.5 mm in the rear node's top socket (M3 x 20 across), upper 6 mm epoxied into the pylon base")
        put(f"pbase_{t}", L.transformed_copy(base, M, "b"), f"pylon_base.{t}", "grey", ant, print_file="grey-pla/pylon_base", count=2,
            connects="epoxied onto the peg; its two ears and serrations clamp the blade's root on the hinge bolt")
        put(f"blade_{t}", L.transformed_copy(blade, M, "bl"), f"pylon_blade.{t}", "grey", ant, print_file="grey-pla/pylon_blade", count=2,
            connects="root tongue between the base's ears on an M3 x 30; tilts in serration steps (select it and rotate on Y)")
        put(f"pknob_{t}", L.transformed_copy(knob, M, "k"), f"pylon_knob.{t}", "grey", ant, print_file="grey-pla/pylon_knob", count=2,
            connects="glued onto the hinge bolt's head: hand-tighten to lock the tilt")
        hw(f"pcbolt_{t}", fastener("b", (SX, s * C.NODE_OUT_Y, C.CRADLE_Z + C.REAR_NODE_W[1] - C.CYL_PIN_Z), Y(-s), 20.0, "m3_cap"), "M3 x 20", f"pylon peg {t} in rear node", ant_hw)
        hw(f"pcnut_{t}", nut("n", (SX, s * (C.NODE_IN_Y - 1.2), C.CRADLE_Z + C.REAR_NODE_W[1] - C.CYL_PIN_Z), "Y"), "M3 nut", f"pylon peg {t} in rear node", ant_hw, "zinc")
        hw(f"hbolt_{t}", fastener("b", (SX, s * (y_knob + C.PYLON_KNOB[1] - 3.0), HZ), Y(-s), 30.0, "m3_cap"), "M3 x 30", f"pylon hinge {t}", ant_hw)
        hw(f"hwasher_{t}", washer("w", (SX, s * (y_knob - 0.9), HZ), "Y" if s > 0 else "-Y", 1.7, 3.5, 0.8), "M3 washer (wave)", f"pylon hinge {t}", ant_hw, "zinc")
        hw(f"hnut_{t}", nut("n", (SX, s * (SY - g - C.PYLON_EAR_T + 3.0 - 2.0), HZ), "Y", t=4.0), "M3 nyloc nut", f"pylon hinge {t} (ear pocket)", ant_hw, "zinc")
    for ob in (peg, base, blade, knob):
        L.delete(ob)

    # ---- reference: head, ears, foam -------------------------------------------------------------------------------
    ref = collection("Reference (not printed)")
    put("head", L.head_phantom(), "head phantom", "skin", ref)
    for s, t in SIDES:
        put(f"ear_{t}", A.ear_phantom(s), f"ear phantom.{t}", "skin", ref)
    pw, pl, pt = C.CROWN_PAD
    apex_bottom = C.CROWN_APEX_Z - (C.CROWN_T + 0.4) / 2 - C.APEX_FLOOR_T
    put("crownpad", L.add_box("crownpad", (C.CX, 0.0, apex_bottom - pt / 2), (pw, pl, pt)), "foam: crown pad 12 mm", "foam", ref)
    nw, nh, nt = C.NAPE_PAD
    put("napepad", L.add_box_local("napepad", Mn, (0.0, 0.0, -C.NAPE_PINLOCK_T / 2 - nt / 2), (nw, nh, nt)), "foam: nape pad", "foam", ref)


# hardware choices the README flags (see the check report): the apex block is 34 wide, so the instructions' M4 x 50 stood
# 19.5 mm out of the nut side; an M4 x 35 leaves 4.5. The nape-lock nail length is what the box holds.
M4_LEN = 35.0
NAPE_NAIL_LEN = 25.4          # 16 ga x 1": from the top it passes the whole upper (left) rack and stops 0.6 short of the lower one
NAPE_DRILL_U = (C.NAPE_PINLOCK_HOLES[0], C.NAPE_PINLOCK_HOLES[2])   # holes 1 and 3 (u 0 and one pitch)
NAPE_DRILL_D = 1.7            # through both rack strips, the block as the drill guide (a 1/16" bit, or a hot nail)
ARCH_GAP = 0.6                # the two bars side by side with their ridges interleaved (verified 0 mm3 at this spacing)


# ---------------------------------------------------------------------------
# assembly sequence
# ---------------------------------------------------------------------------

def steps():
    """Each step: (title, [(keys, into_direction, distance)], turn) where turn = (keys, angle_about_+Y_at_start) or None.
    into_direction is the way the part travels as it goes in; it starts `distance` back along it."""
    T = Vector(C.REAR_T_IN).normalized()
    Y = lambda s: Vector((0.0, s, 0.0))
    Z = Vector((0.0, 0.0, 1.0))
    X = Vector((1.0, 0.0, 0.0))
    Mn = build_nape_dial.M.to_3x3()
    v_up, n_out = Mn @ Vector((0.0, 1.0, 0.0)), Mn @ Vector((0.0, 0.0, 1.0))
    MP = build_brow_center.MP.to_3x3()
    rail_dir = build_brow_rail.rail_frame(C.RAIL_ANGLE, 1).to_3x3() @ X
    trav = math.radians(build_disk.lock_travel_deg())
    LR = lambda pre, s: [f"{pre}_{'L' if s > 0 else 'R'}"]
    both = lambda pre: [f"{pre}_L", f"{pre}_R"]
    S = []
    S.append(("Ring: nape block slides onto the LEFT half's rack", [(["nape"], Y(+1), 75.0)], None))
    S.append(("Ring: RIGHT half's rack slides into the nape block's other tunnel", [(["rear_R"], Y(+1), 150.0)], None))
    S.append(("Ring: both tenons slide up into the rear nodes (racks loose)", [(["rear_L", "rear_R", "nape"], T, 50.0)], None))
    S.append(("Ring: 12 ga nail across each rear node and tenon, from inside", [(LR("tnail", s), Y(s), 30.0) for s in (1, -1)], None))
    S.append(('Ring: set the fit, drill holes 1+3 through both racks; 1" nail down hole 1, 1" nail up hole 3',
              [(["nnail_0"], -v_up, 30.0), (["nnail_1"], v_up, 30.0)], None))
    S.append(("Couplers (before the hubs): down into the hub nodes' top sockets", [(both("coupler"), -Z, 45.0)], None))
    S.append(("Couplers: 12 ga nail from inside through node and coupler, cut flush outside", [(LR("ccnail", s), Y(s), 30.0) for s in (1, -1)], None))
    S.append(("Hubs: three M3 nuts into each hub node's inner face", [([f"nnut_{t}{i}" for i in range(3)], Y(s), 30.0) for s, t in SIDES], None))
    S.append(("Hubs: pawl slider + spring into the rail's tunnel (DOES NOT FIT as printed)", [(LR("slider", s) + LR("pspring", s), rail_dir, 30.0) for s in (1, -1)], None))
    S.append(("Hubs: spool flat against the hub node", [(LR("spool", s), Y(-s), 30.0) for s in (1, -1)], None))
    S.append(("Hubs: rail ring over the spool hub, arm forward", [(LR("rail", s) + LR("slider", s) + LR("pspring", s), Y(-s), 55.0) for s in (1, -1)], None))
    S.append(("Hubs: thin washer on the hub", [(LR("washer", s), Y(-s), 75.0) for s in (1, -1)], None))
    S.append(("Hubs: nexus flange, stalk outward", [(LR("nexus", s), Y(-s), 95.0) for s in (1, -1)], None))
    S.append(("Hubs: three M3 x 30 from outside into the nuts", [([f"nbolt_{t}{i}" for i in range(3)], Y(-s), 125.0) for s, t in SIDES], None))
    brow_group = ["panel", "lid", "link_L", "link_R", "lscrew_L", "lscrew_R"] + [f"fscrew_{i}" for i in range(4)]
    S.append(("Brow: each link's bar into the panel's back pocket", [([f"link_{t}"], MP @ Matrix.Rotation(-s * math.radians(C.BROW_LINK["angle"]), 3, "Z") @ X, 30.0) for s, t in SIDES], None))
    S.append(("Brow: M3 x 16 up through the panel into each link", [([f"lscrew_{t}"], MP @ Z, 25.0) for s, t in SIDES], None))
    S.append(("Brow: faceplate into the front recess", [(["lid"], -(MP @ X), 30.0)], None))
    S.append(("Brow: four M3 x 8 through the faceplate", [([f"fscrew_{i}" for i in range(4)], -(MP @ X), 25.0)], None))
    S.append(("Brow: the panel's laps slide back into the rails' half-laps", [(brow_group, -rail_dir, 70.0)], None))
    S.append(("Brow: two M3 x 10 through each rail into the lap", [([f"rbolt_{t}{i}" for i in range(2)], Y(-s), 30.0) for s, t in SIDES], None))
    S.append(("Crown: apex block in place (its foam pad rests on the head)", [(["apex", "crownpad"], -Z, 45.0)], None))
    S.append(("Crown: left arch half down: foot over the coupler, bar into the channel", [(["arch_L"], -Z, 70.0)], None))
    S.append(("Crown: right arch half down beside it, ridges meshing", [(["arch_R"], -Z, 70.0)], None))
    S.append(("Crown: M3 x 20 across each arch foot and coupler (before the disks)", [(LR("cfbolt", s), Y(-s), 35.0) for s in (1, -1)] + [(LR("cfnut", s), Y(s), 25.0) for s in (1, -1)], None))
    S.append((f"Crown: M4 x {M4_LEN:.0f} through the block and both bars, nut in the pocket", [(["m4"], -X, 55.0), (["m4nut"], X, 25.0)], None))
    S.append(("Antennas: pegs down into the rear nodes' top sockets", [(both("peg"), -Z, 35.0)], None))
    S.append(("Antennas: M3 x 20 across each rear node and peg (before the disks)", [(LR("pcbolt", s), Y(-s), 35.0) for s in (1, -1)] + [(LR("pcnut", s), Y(s), 25.0) for s in (1, -1)], None))
    S.append(("Antennas: base glued down onto the peg", [(both("pbase"), -Z, 55.0)], None))
    S.append(("Antennas: blade root down between the ears", [(both("blade"), -Z, 90.0)], None))
    S.append(("Antennas: M3 x 30 through the knob, head in its recess (glue)", [(LR("hbolt", s), Y(-s), 30.0) for s in (1, -1)], None))
    S.append(("Antennas: wave washer onto the bolt", [(LR("hwasher", s), Y(s), 35.0) for s in (1, -1)], None))
    S.append(("Antennas: knob, bolt and washer through the ears and the blade root", [(LR("pknob", s) + LR("hbolt", s) + LR("hwasher", s), Y(-s), 45.0) for s in (1, -1)], None))
    S.append(("Antennas: nyloc nut into the inner ear's pocket", [(LR("hnut", s), Y(s), 25.0) for s in (1, -1)], None))
    disk = lambda t: [f"dome_{t}", f"back_{t}", f"knob_{t}", f"clip_{t}"] + [f"dscrew_{t}{k}" for k in range(C.DISK_SCREWS)]
    S.append(("Disks: knob shaft through the dome's apex, from outside", [(LR("knob", s), Y(-s), 45.0) for s in (1, -1)], None))
    S.append(("Disks: clip snaps onto the shaft inside the dome", [(LR("clip", s), X, 25.0) for s in (1, -1)], None))   # its open side (+x) leads
    S.append(("Disks: back plate onto the dome's rim", [(LR("back", s), Y(s), 45.0) for s in (1, -1)], None))
    S.append(("Disks: six M3 x 10 through the plate into the bosses", [([f"dscrew_{t}{k}" for k in range(C.DISK_SCREWS)], Y(s), 30.0) for s, t in SIDES], None))
    S.append(("Disks: plate's notches over the stalk's lugs, push flat", [(disk(t), Y(-s), 170.0) for s, t in SIDES], None))
    S.append(("Disks: turn to the stop (the cam pulls it tight)", [], [(disk(t), s * trav) for s, t in SIDES]))
    S.append(("Finish: cap over the nape bay, two countersunk M3 x 8", [(["cap", "capscrew_0", "capscrew_1"], -n_out, 35.0), (["capscrew_0", "capscrew_1"], -n_out, 20.0)], None))
    S.append(("Finish: foam pad at the nape", [(["napepad"], n_out, 30.0)], None))
    return S


def schedule(S):
    """Frames per step, and per object the list of (f0, f1, offset) and (f0, f1, angle) contributions."""
    loc, rot, plan = {}, {}, []
    f = 1 + LEAD
    turn_of = {}                       # key -> (turn step index, angle): directions of earlier steps turn with the part
    for i, (_, _, turn) in enumerate(S):
        for keys, ang in (turn or []):
            for k in keys:
                turn_of[k] = (i, ang)
    for i, (title, moves, turn) in enumerate(S):
        f0, f1 = f, f + STEP_FRAMES
        plan.append((title, f0, f1))
        for keys, d, dist in moves:
            for k in keys:
                v = -Vector(d).normalized() * dist
                if k in turn_of and turn_of[k][0] > i:
                    v = Matrix.Rotation(turn_of[k][1], 3, "Y") @ v
                loc.setdefault(k, []).append((i, f0, f1, v))
        for keys, ang in (turn or []):
            for k in keys:
                rot.setdefault(k, []).append((i, f0, f1, ang))
        f = f1 + GAP
    return loc, rot, plan, f - GAP + TAIL


def _ramp(t, f0, f1):
    return min(1.0, max(0.0, (t - f0) / (f1 - f0)))


def offset_at(key, t, loc, rot):
    v = Vector((0.0, 0.0, 0.0))
    for _, f0, f1, off in loc.get(key, []):
        v += off * (1.0 - _ramp(t, f0, f1))
    a = sum(ang * (1.0 - _ramp(t, f0, f1)) for _, f0, f1, ang in rot.get(key, []))
    return v, a


def remaining_after(key, i, loc, rot):
    v = Vector((0.0, 0.0, 0.0))
    for j, _, _, off in loc.get(key, []):
        if j > i:
            v += off
    return v, sum(ang for j, _, _, ang in rot.get(key, []) if j > i)


def animate(loc, rot, frame_end):
    for k, ob in OB.items():
        frames = sorted({1, frame_end} | {f for _, f0, f1, _ in loc.get(k, []) + rot.get(k, []) for f in (f0, f1)})
        if k not in loc and k not in rot:
            continue
        for t in frames:
            v, a = offset_at(k, t, loc, rot)
            ob.delta_location = v
            ob.keyframe_insert(data_path="delta_location", frame=t)
            if k in rot:
                ob.delta_rotation_euler = (0.0, a, 0.0)
                ob.keyframe_insert(data_path="delta_rotation_euler", frame=t)


# ---------------------------------------------------------------------------
# insertion check
# ---------------------------------------------------------------------------

def pose_matrix(key, t, loc, rot):
    ob = OB[key]
    v, a = offset_at(key, t, loc, rot)
    return Matrix.Translation(Vector(ob["home"]) + v) @ Matrix.Rotation(a, 4, "Y")


class Posed:
    def __init__(self, key, M):
        me = OB[key].data
        self.vs = [M @ v.co for v in me.vertices]
        self.ps = [tuple(p.vertices) for p in me.polygons]
        self.tree = BVHTree.FromPolygons(self.vs, self.ps, epsilon=0.0)
        self.lo = Vector([min(v[i] for v in self.vs) for i in range(3)])
        self.hi = Vector([max(v[i] for v in self.vs) for i in range(3)])


_RAYS = (Vector((0.5773, 0.5774, 0.5773)), Vector((-0.6234, 0.4561, -0.6352)).normalized(), Vector((0.2113, -0.8771, 0.4314)).normalized())


def _parity(tree, p, d):
    n, o = 0, Vector(p)
    while True:
        h = tree.ray_cast(o, d, 1e4)
        if h[0] is None:
            return n % 2 == 1
        n += 1
        o = h[0] + d * 1e-4


def _inside(tree, p):
    """Majority of three skew rays: one ray grazing an edge, or a mesh with a few open edges, flips a single parity test."""
    a, b = _parity(tree, p, _RAYS[0]), _parity(tree, p, _RAYS[1])
    return a if a == b else _parity(tree, p, _RAYS[2])


def shared(a: Posed, b: Posed, step=0.25):
    """Volume inside both (mm3), sampled on a grid around the faces that cross; plus whether one sits wholly inside the other."""
    lo = Vector([max(a.lo[i], b.lo[i]) for i in range(3)])
    hi = Vector([min(a.hi[i], b.hi[i]) for i in range(3)])
    if any(hi[i] <= lo[i] for i in range(3)):
        return 0.0
    pairs = a.tree.overlap(b.tree)
    if not pairs:
        small, big = (a, b) if len(a.vs) < len(b.vs) else (b, a)
        if all(big.lo[i] <= small.lo[i] and small.hi[i] <= big.hi[i] for i in range(3)) and _inside(big.tree, small.vs[0]):
            return -1.0                                               # wholly inside: flagged, volume not sampled
        return 0.0
    cs = [a.vs[j] for i, _ in pairs[:3000] for j in a.ps[i]]
    rlo = Vector([max(lo[i], min(c[i] for c in cs) - 1.5) for i in range(3)])
    rhi = Vector([min(hi[i], max(c[i] for c in cs) + 1.5) for i in range(3)])
    n = [max(1, int((rhi[i] - rlo[i]) / step)) for i in range(3)]
    while n[0] * n[1] * n[2] > 150000:
        step *= 1.5
        n = [max(1, int((rhi[i] - rlo[i]) / step)) for i in range(3)]
    cnt = 0
    for ix in range(n[0]):
        for iy in range(n[1]):
            for iz in range(n[2]):
                p = (rlo[0] + (ix + 0.37) * step, rlo[1] + (iy + 0.41) * step, rlo[2] + (iz + 0.43) * step)
                if _inside(a.tree, p) and _inside(b.tree, p):
                    cnt += 1
    return cnt * step ** 3


def check(S, loc, rot, plan):
    meshes = [k for k, ob in OB.items() if ob.type == "MESH" and not k.startswith(("head", "ear_"))]
    out = ["Insertion check: every step's moving parts swept along their path against the parts already together with them.",
           "Shared volume (mm3) on a 0.25 mm grid around crossing faces; 'inside' = one part wholly inside the other.",
           "clear < 0.5 mm3 everywhere on the path; touch < 5; BLOCKED otherwise. Paths sampled every 2.5 mm / 3 deg.", ""]
    t0 = time.time()
    for i, (title, moves, turn) in enumerate(S):
        title, f0, f1 = plan[i]
        moving = sorted({k for keys, _, _ in moves for k in keys} | {k for keys, _ in (turn or []) for k in keys})
        moving_m = [k for k in moving if k in meshes]
        if not moving_m:
            out.append(f"{i + 1:2d}. {title}\n      (no meshes to check)")
            continue
        travel = max([dist for _, _, dist in moves] + [abs(a) * 60.0 for _, a in (turn or [])])     # 3 deg per sample on a turn
        ns = max(4, int(math.ceil(travel / 2.5)))
        # static partners: same remaining motion after this step as the moving part (they are already together)
        partners = {}
        for m in moving_m:
            rv, ra = remaining_after(m, i, loc, rot)
            partners[m] = [o for o in meshes if o not in moving and (remaining_after(o, i, loc, rot)[0] - rv).length < 1e-6
                           and abs(remaining_after(o, i, loc, rot)[1] - ra) < 1e-9]
        static_cache = {}
        worst = {}                        # (m, o) -> (vol, s)
        for j in range(ns + 1):
            s_ = j / ns
            t = f0 + s_ * (f1 - f0)
            for m in moving_m:
                pm = Posed(m, pose_matrix(m, t, loc, rot))
                for o in partners[m]:
                    if o not in static_cache:
                        static_cache[o] = Posed(o, pose_matrix(o, t, loc, rot))
                    po = static_cache[o]
                    if any(pm.hi[q] < po.lo[q] or po.hi[q] < pm.lo[q] for q in range(3)):
                        continue
                    v = shared(pm, po)
                    key = (m, o)
                    if v != 0.0 and (key not in worst or (v < 0) or v > worst[key][0] >= 0):
                        worst[key] = (v, s_)
                    if j == ns and v != 0.0:
                        worst[(m, o, "home")] = (v, 1.0)
        rows = []
        for key, (v, s_) in sorted(worst.items(), key=lambda kv: -abs(kv[1][0]) if kv[1][0] >= 0 else -1e9):
            m, o = key[0], key[1]
            tag = "inside" if v < 0 else ("touch" if v < 5.0 else "BLOCKED")
            if v >= 0 and v < 0.5:
                continue
            where = "seated (end of path)" if len(key) == 3 else f"at {s_ * 100:3.0f}% of the path"
            rows.append(f"      {tag:7s} {OB[m].name} x {OB[o].name}: {('%.1f mm3' % v) if v >= 0 else 'wholly inside'} {where}")
        verdict = "clear" if not rows else ("BLOCKED" if any("BLOCKED" in r or "inside" in r for r in rows) else "touch")
        out.append(f"{i + 1:2d}. [{verdict}] {title}")
        out += rows
        print(f"check {i + 1}/{len(S)} {verdict} {title} ({time.time() - t0:.0f} s)", flush=True)
    out.append("")
    out.append(nape_nail_check())
    return "\n".join(out)


def nape_nail_check():
    """The pin-lock as designed: can a nail dropped through any of the four holes pass the UNDRILLED racks?
    A full-length nail at each hole, the nape block slid along the racks over a whole pitch in 0.1 mm steps."""
    Mn = build_nape_dial.M
    R3 = Mn.to_3x3()
    cb_d, cb_h = C.NAPE_PINLOCK_PIN["cbore"]
    p = math.pi * C.GEAR_MODULE
    OB["_rl"], OB["_rr"] = build_rear_band_half.make(+1), build_rear_band_half.make(-1)
    for k in ("_rl", "_rr"):
        OB[k]["home"] = (0.0, 0.0, 0.0)
    racks = (Posed("_rl", Matrix.Identity(4)), Posed("_rr", Matrix.Identity(4)))
    clear_any = []
    for k in range(int(p / 0.1) + 1):
        d = k * 0.1
        for u in C.NAPE_PINLOCK_HOLES:
            nl = fastener("tmp", Mn @ Vector((u + d, C.NAPE_HV / 2 - cb_h, 0.0)), R3 @ Vector((0.0, -1.0, 0.0)), C.NAPE_HV - cb_h, "nail16")
            OB["_tmp"] = nl
            nl["home"] = (0.0, 0.0, 0.0)
            pn = Posed("_tmp", Matrix.Identity(4))
            v = [shared(pn, r) for r in racks]
            if v[0] < 0.5:
                clear_any.append((round(u + d, 2), round(v[1], 1)))
            L.delete(nl)
    for k in ("_rl", "_rr", "_tmp"):
        if k in OB and k != "_tmp":
            L.delete(OB[k])
        OB.pop(k, None)
    head = "Nape pin-lock as designed (undrilled racks): a nail dropped from the top"
    if not clear_any:
        return (head + " meets solid LEFT rack at every hole and every block position over a whole pitch:\n"
                "  the tooth gaps are only on the strip's lower edge; above them the strip is solid, so no nail can pass it.\n"
                f"  Field fix modelled here: drill Ø{NAPE_DRILL_D} through both racks via holes 1 and 3 at your fit, a 1\" nail down hole 1\n"
                "  (left rack) and a 1\" nail up hole 3 (right rack); or two 1 1/2\" 16 ga nails down both holes.")
    return head + " passes the left rack at: " + ", ".join(f"u {u} (right rack {v} mm3)" for u, v in clear_any[:12])


# ---------------------------------------------------------------------------
# file setup
# ---------------------------------------------------------------------------

def origins_and_pivots():
    trav_axis = {}
    for s, t in SIDES:
        trav_axis[t] = Vector((C.CX, s * C.DISK_IN_Y, C.CZ))
    for k, ob in OB.items():
        if k.startswith(("dome_", "back_", "knob_", "clip_", "dscrew_")):
            o = trav_axis[k.split("_")[1][0]]                     # on the disk axis: the bayonet turn is a rotation about it
        elif k.startswith("blade_"):
            o = Vector((build_pylon.SX, (1 if k.endswith("L") else -1) * build_pylon.SY, build_pylon.HZ))
        else:
            o = bbox_centre(ob)
        set_origin(ob, o)
        ob["home"] = tuple(o)


VISOR_KEYS = ("rail_", "slider_", "pspring_", "link_", "lscrew_", "rbolt_", "fscrew_")


def visor_rig():
    e = bpy.data.objects.new("VISOR (rotate on Y: 0 worn, -30 parked)", None)
    e.empty_display_type = "CIRCLE"
    e.empty_display_size = 30.0
    e.location = (C.CX, 0.0, C.CZ)
    e.rotation_euler = (math.pi / 2, 0.0, 0.0)
    e.rotation_euler = (0.0, 0.0, 0.0)
    e.lock_location = (True, True, True)
    e.lock_rotation = (True, False, True)
    c = e.constraints.new("LIMIT_ROTATION")
    c.use_limit_y = True
    c.min_y, c.max_y = -math.radians(C.VISOR_PARK_DEG - C.RAIL_ANGLE), 0.0
    c.use_transform_limit = True
    e["is_control"] = True
    collection("3 Brow: panel, faceplate, links").objects.link(e)
    inv = Matrix.Translation(e.location).inverted()
    for k, ob in OB.items():
        if k.startswith(VISOR_KEYS) or k in ("panel", "lid"):
            ob.parent = e
            ob.matrix_parent_inverse = inv
    return e


README = """HelmKit vp0.18 -- STRUCTURAL PROTOTYPE explorer
================================================
1 unit = 1 mm. +X forward, +Y the wearer's LEFT, +Z up. Origin between the ear canals.
Generated by tools/blender/vp0/explore_vp0.py (re-run it after any canon change; it overwrites this file).

WATCH IT GO TOGETHER
  Scrub the timeline (bottom) or press Space. Frame 1 = every part exploded along the way it goes in;
  the last frame = the finished helm. The markers on the timeline name each step (zoom the timeline to read them).
  Steps run in an order that WORKS (checked part by part, see the insertion_check text): 1 Ring, the crown couplers,
  2 Hubs, 3 Brow, 4 Crown, 5 Antennas, 6 Disks LAST, Finish. The disks cover the outer ends of the crown-foot and
  pylon-peg cross-bolt holes, so those bolts go in before the disks.

LOOK CLOSER
  Click a part, then Numpad . (View Selected) to zoom to it; Numpad / for Local View (only that part; again to leave).
  Hide a whole group with the eye in the Outliner (top right): each step group has its own "hardware" sub-collection.
  Alt+Z = X-ray (see bolts inside the parts). Alt+B = clipping box (drag a box: everything outside it is cut away).
  Viewport Shading popover (top right of the 3D view) > Color > Random gives every part its own colour.
  Object Properties (orange square) > Custom Properties: the print file, how many, and what it connects to.

TINKER
  Move (G) or rotate (R) anything; it starts from where it sits in the helm.
  Disks: every disk part has its origin on the disk axis. Select one side's disk parts (Outliner: click the first,
  Shift+click the last) and R Y to turn them through the bayonet; the "turn to the stop" step shows the entry pose.
  Pylon blades rotate about the hinge: select one, R Y.
  VISOR empty (the circle at the disk axis): R Y swings the whole brow, 0 = worn, -30 = parked.
  Put everything back: Scripting tab > Text Editor > reset_parts > Run Script (or re-open the file).
  The timeline's animation is on the DELTA transforms, so your own moves and the timeline add together.

CHANGES FROM THE EARLIER INSTRUCTIONS (shown in this file)
  Nape lock: the nails cannot pass the solid rack strips. At your fit, drill Ø1.7 (1/16") through both racks using
    holes 1 and 3 as the guide, then a 16 ga x 1" nail DOWN hole 1 (locks the left rack) and one UP hole 3 (right rack).
  Crown couplers in the hub nodes: the cross hole's outer end is under the nexus spool, so no bolt or nut fits.
    Pin each with a 12 ga nail from INSIDE, cut flush with the node's outer face, before the spool goes on.
  Apex clamp: M4 x 35, not x 50 (the block is 34 wide; a 50 stands 19 mm out of the nut side).
  Pylon knob: it goes on the hinge bolt FIRST (head into its recess), then knob + bolt + washer through the hinge.
  Visor pawl sliders: they cannot go into the printed rails (the thumb tab is taller than the tunnel), and the tab's
    slot lets them move 0.4 mm, not the 2 mm needed to release. Leave them out for now (see insertion_check).

WHAT IS NOT HERE
  Not part of this build: coils and coil formers, pad frames and sensors, cover strips, spine rope, the disk lock pin.
  The cradle is the v0.18 design: its tenon slots run out through the rear nodes' back faces (your printed cradle
  gets the same opening by the hand-cut notch). The two crown halves are the reprinted v0.18 ones.
"""

RESET = """import bpy
for ob in bpy.data.objects:
    if "home" in ob.keys():
        ob.location = ob["home"]
        ob.rotation_euler = (0.0, 0.0, 0.0)
    elif ob.get("is_control"):
        ob.rotation_euler = (0.0, 0.0, 0.0)
"""


def texts(plan, report):
    t = bpy.data.texts.new("README")
    t.write(README + "\nSTEPS (frame where each finishes)\n" + "\n".join(f"  {i + 1:2d}. f{f1:4d}  {title}" for i, (title, f0, f1) in enumerate(plan)))
    t.write("\n\nHARDWARE IN THIS FILE\n" + "\n".join(f"  {what:28s} {where}" for _, what, where in HW_ROWS) + "\n")
    bpy.data.texts.new("reset_parts").write(RESET)
    if report:
        bpy.data.texts.new("insertion_check").write(report)


def view_setup(frame_end, plan):
    sc = bpy.context.scene
    sc.render.fps = 24
    sc.frame_start, sc.frame_end = 1, frame_end
    sc.frame_current = frame_end
    sc.timeline_markers.new("exploded", frame=1)
    for i, (title, f0, f1) in enumerate(plan):
        sc.timeline_markers.new(f"{i + 1}. {title}", frame=f1)
    eye, target = Vector((520.0, 470.0, 330.0)), Vector((-5.0, 0.0, 75.0))
    q = (target - eye).to_track_quat("-Z", "Y")
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type != "VIEW_3D":
                continue
            for sp in area.spaces:
                if sp.type != "VIEW_3D":
                    continue
                sp.clip_start, sp.clip_end = 1.0, 20000.0
                sp.lens = 50.0
                sp.shading.type = "SOLID"
                sp.shading.color_type = "MATERIAL"
                sp.shading.show_cavity = True
                sp.shading.cavity_type = "BOTH"
                sp.overlay.show_relationship_lines = False
                r3 = sp.region_3d
                r3.view_perspective = "PERSP"
                r3.view_location = target
                r3.view_rotation = q
                r3.view_distance = (target - eye).length


def renders(out_dir, frames):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light, sh.color_type, sh.show_cavity, sh.cavity_type = "STUDIO", "MATERIAL", True, "BOTH"
    sh.show_object_outline = True
    sc.render.resolution_x, sc.render.resolution_y = 1400, 1000
    w = bpy.data.worlds.new("W"); w.color = (0.93, 0.93, 0.94); sc.world = w
    cd = bpy.data.cameras.new("cam"); cd.lens = 40; cd.clip_end = 20000
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    out_dir.mkdir(parents=True, exist_ok=True)
    keep = sc.frame_current
    for name, f, eye, tgt in frames:
        sc.frame_set(f)
        cam.location = Vector(eye)
        cam.rotation_euler = (Vector(tgt) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = str(out_dir / f"explore_{name}.png")
        bpy.ops.render.render(write_still=True)
    sc.frame_set(keep)
    bpy.data.objects.remove(cam)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--blend", default=DEFAULT_BLEND)
    ap.add_argument("--check", default=None, help="write the insertion check here (slow: minutes)")
    ap.add_argument("--renders", default=None, help="render preview PNGs into this folder")
    args = ap.parse_args(L.argv_after_dashdash())
    L.reset_scene()
    build()
    origins_and_pivots()
    S = steps()
    loc, rot, plan, frame_end = schedule(S)
    missing = sorted({k for keys, _, _ in [m for _, ms, _ in S for m in ms] for k in keys} - set(OB))
    assert not missing, f"steps name unknown objects: {missing}"
    unplaced = sorted(k for k in OB if k not in loc and k not in rot and not k.startswith(("head", "ear_")))
    print("objects with no step (shown in place from frame 1):", unplaced)
    animate(loc, rot, frame_end)
    report = None
    if args.check:
        report = check(S, loc, rot, plan)
        Path(args.check).parent.mkdir(parents=True, exist_ok=True)
        Path(args.check).write_text(report + "\n")
        print(report)
    visor_rig()
    texts(plan, report)
    view_setup(frame_end, plan)
    if args.renders:
        mid = next(f1 for (t, f0, f1) in plan if t.startswith("Disks: six"))
        renders(Path(args.renders), [("assembled", frame_end, (520.0, 470.0, 330.0), (-5.0, 0.0, 75.0)),
                                     ("exploded", 1, (900.0, 820.0, 560.0), (-5.0, 0.0, 75.0)),
                                     ("disks_on", mid, (-520.0, 600.0, 300.0), (-5.0, 0.0, 75.0)),
                                     ("back", frame_end, (-560.0, -430.0, 260.0), (-40.0, 0.0, 40.0))])
    bp = Path(args.blend).resolve()
    bp.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(bp), compress=True)
    print("saved", bp, "frames", frame_end, "steps", len(plan), "objects", len(OB))


if __name__ == "__main__":
    main()
