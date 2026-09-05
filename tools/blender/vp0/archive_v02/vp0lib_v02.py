"""
vp0lib.py -- shared mesh helpers for the vp0.2 generators. Blender-only.

Everything builds in the assembly frame described in canon.py. Booleans use
the EXACT solver. Every part goes through `finalize_and_export()` which checks
manifoldness, rotates into print orientation and writes an STL + sidecar.

Boolean hygiene (Blender 5.0 EXACT solver), learned on vp0.1:
  * ring bodies and pucks are revolves, never cylinder primitives with n-gon caps
  * serration/ridge solids are unioned LAST and sink into their host
  * no two bodies share a face plane or a tangent line (rings 5.2 vs bands 5.0)
  * rotationally symmetric cuts go into the revolve profile
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy  # type: ignore
import bmesh  # type: ignore
from mathutils import Matrix, Vector  # type: ignore
from mathutils.bvhtree import BVHTree  # type: ignore

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import canon as C  # noqa: E402


# ---------------------------------------------------------------------------
# Scene / object plumbing
# ---------------------------------------------------------------------------

def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 0.001


def _link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def obj_from_bm(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.update()
    return _link(bpy.data.objects.new(name, me))


def obj_from_pydata(name, verts, faces):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate(verbose=False)
    me.update()
    ob = _link(bpy.data.objects.new(name, me))
    recalc_normals(ob)
    return ob


def recalc_normals(ob) -> None:
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def select_only(ob) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def apply_transform(ob) -> None:
    select_only(ob)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def delete(ob) -> None:
    bpy.data.objects.remove(ob, do_unlink=True)


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def frame(origin, ez, ex_hint=(1.0, 0.0, 0.0)) -> Matrix:
    """4x4 local frame: local Z = ez, local X = ex_hint made perpendicular, local Y = Z x X."""
    ez = Vector(ez).normalized()
    ex = Vector(ex_hint)
    ex = ex - ez * ex.dot(ez)
    if ex.length < 1e-6:
        ex = Vector((0.0, 1.0, 0.0)) - ez * ez.y
        if ex.length < 1e-6:
            ex = Vector((0.0, 0.0, 1.0)) - ez * ez.z
    ex.normalize()
    ey = ez.cross(ex)
    M = Matrix.Identity(4)
    for r in range(3):
        M[r][0] = ex[r]
        M[r][1] = ey[r]
        M[r][2] = ez[r]
        M[r][3] = origin[r]
    return M


def _axis_rot(axis: str) -> Matrix:
    return {
        "Z": Matrix.Identity(4),
        "-Z": Matrix.Rotation(math.pi, 4, "X"),
        "Y": Matrix.Rotation(-math.pi / 2.0, 4, "X"),
        "-Y": Matrix.Rotation(math.pi / 2.0, 4, "X"),
        "X": Matrix.Rotation(math.pi / 2.0, 4, "Y"),
        "-X": Matrix.Rotation(-math.pi / 2.0, 4, "Y"),
    }[axis]


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

def add_box(name, center, dims):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = dims
    apply_transform(ob)
    ob.location = center
    apply_transform(ob)
    return ob


def add_box_local(name, M: Matrix, center, dims):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = dims
    apply_transform(ob)
    ob.matrix_world = M @ Matrix.Translation(Vector(center))
    apply_transform(ob)
    return ob


def add_cyl(name, center, radius, depth, axis="Z", verts=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts)
    ob = bpy.context.active_object
    ob.name = name
    ob.matrix_world = Matrix.Translation(Vector(center)) @ _axis_rot(axis)
    apply_transform(ob)
    return ob


def add_cyl_local(name, M: Matrix, center, radius, depth, axis="Z", verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts)
    ob = bpy.context.active_object
    ob.name = name
    ob.matrix_world = M @ Matrix.Translation(Vector(center)) @ _axis_rot(axis)
    apply_transform(ob)
    return ob


def add_hex_prism(name, center, across_flats, depth, axis="Z"):
    return add_cyl(name, center, across_flats / math.sqrt(3.0), depth, axis=axis, verts=6)


def add_hex_prism_local(name, M, center, across_flats, depth, axis="Z"):
    return add_cyl_local(name, M, center, across_flats / math.sqrt(3.0), depth, axis=axis, verts=6)


def revolve(name, profile, axis="Y", center=(0.0, 0.0, 0.0), segments=128):
    """
    Revolve a closed (r, n) polygon about an axis. n = local axial coordinate
    (0 at `center`, increasing along `axis`); r = radius. Points on the axis
    (r == 0) are allowed; the degenerate fan is dissolved.
    """
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0.0, n)) for r, n in profile]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 1.0),
                   dvec=(0.0, 0.0, 0.0), angle=2.0 * math.pi, steps=segments, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(center)) @ _axis_rot(axis), verts=bm.verts)
    return obj_from_bm(name, bm)


def extrude_polygon(name, poly, thickness, M: Matrix | None = None, z0=0.0):
    """
    Prism from a simple 2D polygon [(u, v), ...] in local XY, extruded along local Z
    from z0. Caps are triangulated with a constrained Delaunay (mathutils CDT): ear
    clipping emits zero-area triangles when several outline vertices are collinear
    (rack root lines, ridge plates), which breaks the EXACT boolean solver.
    """
    from mathutils.geometry import delaunay_2d_cdt
    import mathutils
    n = len(poly)
    coords = [mathutils.Vector((u, v)) for u, v in poly]
    vc, ed, fc, ov, oe, of = delaunay_2d_cdt(coords, [], [list(range(n))], 1, 1e-6)
    imap = {}
    for k, origs in enumerate(ov):
        for i in origs:
            imap[i] = k
    bm = bmesh.new()
    bot = [bm.verts.new((c.x, c.y, z0)) for c in vc]
    top = [bm.verts.new((c.x, c.y, z0 + thickness)) for c in vc]
    for f in fc:
        if len(f) >= 3:
            bm.faces.new([bot[i] for i in reversed(f)])
            bm.faces.new([top[i] for i in f])
    for i in range(n):
        a, b2 = imap.get(i), imap.get((i + 1) % n)
        if a is None or b2 is None or a == b2:
            continue
        bm.faces.new((bot[a], bot[b2], top[b2], top[a]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if M is not None:
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return obj_from_bm(name, bm)


# ---------------------------------------------------------------------------
# 2D profiles
# ---------------------------------------------------------------------------

def involute_gear_poly(N, module, pa_deg, samples=8, backlash=0.1):
    """Spur gear outline, CCW, centred on the origin, one tooth centred on +X."""
    pa = math.radians(pa_deg)
    rp = module * N / 2.0
    rb = rp * math.cos(pa)
    ra = rp + module
    rr = rp - 1.25 * module
    inv = lambda th: math.tan(th) - th
    half_tooth = math.pi / (2 * N) - backlash / (2 * rp)
    psi_b = half_tooth + inv(pa)                      # half-angle at the base circle

    def psi(r):
        if r <= rb:
            return psi_b
        return psi_b - inv(math.acos(rb / r))

    pts = []
    for k in range(N):
        a0 = 2 * math.pi * k / N
        prof = []
        rs = [rr, rb] + [rb + (ra - rb) * (i + 1) / samples for i in range(samples)]
        for r in rs:                                   # right flank, root -> tip
            prof.append((r, -psi(r)))
        for r in reversed(rs):                         # left flank, tip -> root
            prof.append((r, +psi(r)))
        for r, ang in prof:
            pts.append((r * math.cos(a0 + ang), r * math.sin(a0 + ang)))
    return pts


def rack_poly(length, module, pa_deg, body_h, backlash=0.15, margin=1.0):
    """Rack outline: teeth along +u pointing +v, pitch line at v=0, body down to v=-body_h. CW."""
    p = math.pi * module
    a = module
    d = 1.25 * module
    t = math.tan(math.radians(pa_deg))
    half_p = p / 4.0 - backlash / 2.0
    n = int((length - 2 * margin) // p)
    x0 = margin + (length - 2 * margin - n * p) / 2.0
    pts = [(0.0, -body_h), (0.0, -d)]
    for k in range(n):
        xc = x0 + p / 2.0 + k * p
        pts += [(xc - (half_p + d * t), -d), (xc - (half_p - a * t), a),
                (xc + (half_p - a * t), a), (xc + (half_p + d * t), -d)]
    pts += [(length, -d), (length, -body_h)]
    return pts


def sawtooth_poly(teeth, r_in, r_out, rise_frac=0.15, direction=+1):
    """Ratchet rim outline. direction=+1: steep face first (CCW), gentle ramp after."""
    pts = []
    p = 2 * math.pi / teeth
    for k in range(teeth):
        a0 = k * p
        if direction > 0:
            pts.append((r_in * math.cos(a0), r_in * math.sin(a0)))
            a1 = a0 + rise_frac * p
            pts.append((r_out * math.cos(a1), r_out * math.sin(a1)))
        else:
            pts.append((r_in * math.cos(a0), r_in * math.sin(a0)))
            a1 = a0 + (1.0 - rise_frac) * p
            pts.append((r_out * math.cos(a1), r_out * math.sin(a1)))
    return pts


def ridge_plate_poly(u0, u1, pitch, height, base, phase):
    """Triangle-wave ridges along u (peaks at u = phase + k*pitch), on a base plate from v=-base to 0."""
    pts = [(u0, -base), (u0, 0.0)]
    k0 = math.floor((u0 - phase) / pitch) - 1
    k1 = math.ceil((u1 - phase) / pitch) + 1
    for k in range(k0, k1 + 1):
        peak = phase + k * pitch
        valley = peak + pitch / 2.0
        for u, v in ((peak, height), (valley, 0.0)):
            if u0 < u < u1:
                pts.append((u, v))
    pts += [(u1, 0.0), (u1, -base)]
    return pts


# ---------------------------------------------------------------------------
# Serrations / curves / ribbons
# ---------------------------------------------------------------------------

def serration_solid(name, face_pt, normal, r_in=C.SERR_R_IN, r_out=C.SERR_R_OUT,
                    teeth=C.SERR_TEETH, height=C.SERR_H, overlap=C.SERR_OVERLAP,
                    phase_deg=0.0, valley=-0.15):
    bm = bmesh.new()
    nth = teeth * 2
    ti, to, bi, bo = [], [], [], []
    for j in range(nth):
        th = 2.0 * math.pi * j / nth + math.radians(phase_deg)
        h = height if (j % 2 == 1) else valley
        c, s = math.cos(th), math.sin(th)
        ti.append(bm.verts.new((r_in * c, r_in * s, h)))
        to.append(bm.verts.new((r_out * c, r_out * s, h)))
        bi.append(bm.verts.new((r_in * c, r_in * s, -overlap)))
        bo.append(bm.verts.new((r_out * c, r_out * s, -overlap)))
    for j in range(nth):
        k = (j + 1) % nth
        bm.faces.new((ti[j], to[j], to[k], ti[k]))
        bm.faces.new((bo[j], bi[j], bi[k], bo[k]))
        bm.faces.new((to[j], bo[j], bo[k], to[k]))
        bm.faces.new((ti[k], bi[k], bi[j], ti[j]))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(Vector(normal).normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(face_pt)) @ rot, verts=bm.verts)
    return obj_from_bm(name, bm)


def catmull_rom(waypoints, samples_per_seg=16, alpha=0.5):
    """
    Centripetal Catmull-Rom (alpha=0.5) through N-dimensional waypoints. The uniform
    variant overshoots and loops where waypoint spacing is uneven, which makes a
    swept ribbon self-intersect; centripetal never does.
    """
    import numpy as np
    P = [np.array(w, dtype=float) for w in waypoints]
    P = [P[0] + (P[0] - P[1]) * 0.01] + P + [P[-1] + (P[-1] - P[-2]) * 0.01]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0.0
        t1 = t0 + max(np.linalg.norm(p1 - p0), 1e-9) ** alpha
        t2 = t1 + max(np.linalg.norm(p2 - p1), 1e-9) ** alpha
        t3 = t2 + max(np.linalg.norm(p3 - p2), 1e-9) ** alpha
        last = (i == len(P) - 3)
        for k in range(samples_per_seg + (1 if last else 0)):
            t = t1 + (t2 - t1) * k / samples_per_seg
            A1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            A2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            A3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
            B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3
            q = (t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2
            out.append(tuple(q.tolist()))
    return out


def ribbon(name, pts, wide, ext):
    """
    Sweep a rectangle along a polyline. pts: centreline Vectors; wide: W direction
    (Vector or per-station list); ext: per-station (w_pos, w_neg, n_pos, n_neg),
    N = T x W. Negative extents offset the section.
    """
    n = len(pts)
    verts = []
    per_station = isinstance(wide, (list, tuple)) and len(wide) == n and not isinstance(wide[0], (int, float))
    for i in range(n):
        p = Vector(pts[i])
        if i == 0:
            T = Vector(pts[1]) - Vector(pts[0])
        elif i == n - 1:
            T = Vector(pts[-1]) - Vector(pts[-2])
        else:
            T = Vector(pts[i + 1]) - Vector(pts[i - 1])
        T.normalize()
        W = Vector(wide[i] if per_station else wide)
        W = (W - T * W.dot(T)).normalized()
        N = T.cross(W).normalized()
        wp, wn, npos, nneg = ext[i]
        verts += [p + W * wp + N * npos, p + W * wp - N * nneg, p - W * wn - N * nneg, p - W * wn + N * npos]
    faces = []
    for i in range(n - 1):
        a, b = 4 * i, 4 * (i + 1)
        for k in range(4):
            k2 = (k + 1) % 4
            faces.append((a + k, a + k2, b + k2, b + k))
    faces.append((0, 3, 2, 1))
    e = 4 * (n - 1)
    faces.append((e, e + 1, e + 2, e + 3))
    return obj_from_pydata(name, verts, faces)


# ---------------------------------------------------------------------------
# Booleans
# ---------------------------------------------------------------------------

def bool_op(host, tool, op="DIFFERENCE", keep_tool=False):
    mod = host.modifiers.new(name=f"b_{tool.name[:24]}", type="BOOLEAN")
    mod.operation = op
    mod.object = tool
    mod.solver = "EXACT"
    select_only(host)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if not keep_tool:
        delete(tool)
    return host


def union(host, *tools):
    for t in tools:
        bool_op(host, t, op="UNION")
    return host


def cut(host, *tools):
    for t in tools:
        bool_op(host, t, op="DIFFERENCE")
    return host


def intersect(host, tool):
    return bool_op(host, tool, op="INTERSECT")


def mirror_y(ob, name=None):
    new = ob.copy()
    new.data = ob.data.copy()
    new.name = name or (ob.name + "_R")
    _link(new)
    new.matrix_world = Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)) @ ob.matrix_world
    apply_transform(new)
    recalc_normals(new)
    return new


def transformed_copy(ob, M: Matrix, name):
    new = ob.copy()
    new.data = ob.data.copy()
    new.name = name
    _link(new)
    new.matrix_world = M @ ob.matrix_world
    apply_transform(new)
    if M.determinant() < 0:
        recalc_normals(new)
    return new


# ---------------------------------------------------------------------------
# Standard sub-assemblies
# ---------------------------------------------------------------------------

def ring_paddle(name, center, radius, side=+1):
    """Plain arm ring on the pod axis through `center` (x, y, z), thickness RING_T, axis Y, bored M5."""
    rb = C.M5_CLEAR_DIA / 2.0
    t = C.RING_T / 2.0
    return revolve(name, [(rb, -t), (radius, -t), (radius, t), (rb, t)], axis="Y", center=center, segments=96)


def serrate(host, center, side=+1, serr_in=True, serr_out=True):
    """Union serrations onto the +/-Y faces of the ring at `center`. Must be the last boolean."""
    cx, cy, cz = center
    inb = -side
    if serr_in:
        union(host, serration_solid(host.name + "_sin", (cx, cy + inb * C.RING_T / 2.0, cz), (0.0, inb, 0.0)))
    if serr_out:
        union(host, serration_solid(host.name + "_sout", (cx, cy - inb * C.RING_T / 2.0, cz), (0.0, -inb, 0.0)))
    return host


def pivot_bore(host, center, length=40.0):
    cut(host, add_cyl("bore", center, C.M5_CLEAR_DIA / 2.0, length, axis="Y", verts=48))
    return host


def port_boss(name, M: Matrix):
    """Socket boss block standing on its host: mouth at local origin, boss along -Z, sunk PORT_BOSS_SINK."""
    h = C.PORT_BOSS_H + C.PORT_BOSS_SINK
    return add_box_local(name, M, (0.0, 0.0, -h / 2.0), (C.PORT_BOSS, C.PORT_BOSS, h))


def port_cutters(M: Matrix, tag="", header=True, xbolt_len=None):
    sq = C.PORT_SQ + C.PORT_CLEAR
    tools = [
        add_box_local("psock" + tag, M, (0.0, 0.0, -C.PORT_DEPTH / 2.0 + 0.5), (sq, sq, C.PORT_DEPTH + 1.0)),
        add_cyl_local("pxb" + tag, M, (0.0, 0.0, -C.PORT_XBOLT_DEPTH), C.PORT_XBOLT_DIA / 2.0, xbolt_len or (C.PORT_BOSS + 4.0), axis="X"),
    ]
    if header:
        hw, ht, hd = C.PORT_HDR_POCKET
        tools.append(add_box_local("phdr" + tag, M, (0.0, 0.0, -C.PORT_DEPTH - hd / 2.0 + 0.01), (hw, ht, hd)))
    return tools


def port_plug(name, M: Matrix, flange=True):
    """Post into the socket (local -Z from the mouth) plus a flange resting on the mouth plane."""
    ext = 1.0 if flange else 0.0          # post sinks into the flange: no coplanar contact for the solver
    post = add_box_local(name, M, (0.0, 0.0, -(C.PORT_PLUG_LEN - ext) / 2.0), (C.PORT_SQ, C.PORT_SQ, C.PORT_PLUG_LEN + ext))
    if flange:
        union(post, add_box_local(name + "_fl", M, (0.0, 0.0, C.PORT_FLANGE_T / 2.0),
                                  (C.PORT_FLANGE, C.PORT_FLANGE, C.PORT_FLANGE_T)))
    return post


def port_plug_xhole(M: Matrix, tag=""):
    return add_cyl_local("pplx" + tag, M, (0.0, 0.0, -C.PORT_XBOLT_DEPTH), C.M3_CLEAR_DIA / 2.0, C.PORT_SQ + 6.0, axis="X")


def pod_port_frame(angle_deg, side=+1):
    """Mouth frame of a pod port: radial socket in the pod's XZ plane, cross-bolt along Y."""
    a = math.radians(angle_deg)
    d = Vector((math.cos(a), 0.0, math.sin(a)))
    mouth = Vector((C.CX, side * C.POD_PORT_Y, C.CZ)) + d * (C.DISH_R + C.PORT_BOSS_H)
    return frame(mouth, d, (0.0, side, 0.0))


def head_phantom(name="head_phantom", seg_u=96, seg_v=48):
    a, b, c = C.HEAD.phantom_semi
    n = C.HEAD.plan_exp
    verts, faces = [], []
    for j in range(1, seg_v):
        v = -math.pi / 2 + math.pi * j / seg_v
        cv, sv = math.cos(v), math.sin(v)
        for i in range(seg_u):
            u = 2 * math.pi * i / seg_u
            cu, su = math.cos(u), math.sin(u)
            verts.append((a * cv * math.copysign(abs(cu) ** (2 / n), cu),
                          b * cv * math.copysign(abs(su) ** (2 / n), su), c * sv))
    rings = seg_v - 1
    bot = len(verts); verts.append((0.0, 0.0, -c))
    top = len(verts); verts.append((0.0, 0.0, c))
    for j in range(rings - 1):
        for i in range(seg_u):
            a0, a1 = j * seg_u + i, j * seg_u + (i + 1) % seg_u
            b0, b1 = (j + 1) * seg_u + i, (j + 1) * seg_u + (i + 1) % seg_u
            faces.append((a0, a1, b1, b0))
    tr = (rings - 1) * seg_u
    for i in range(seg_u):
        faces.append((bot, (i + 1) % seg_u, i))
        faces.append((top, tr + i, tr + (i + 1) % seg_u))
    ob = obj_from_pydata(name, verts, faces)
    ob.location = (0.0, 0.0, C.HEAD.phantom_center_z)
    apply_transform(ob)
    union(ob, add_cyl(name + "_neck", (-15.0, 0.0, -110.0), 52.0, 140.0, axis="Z", verts=48))
    return ob


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def mesh_stats(ob) -> dict:
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    vol = bm.calc_volume(signed=True)
    bm.free()
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    return {"nonmanifold_edges": nonman, "volume_mm3": vol, "mass_g_petg": vol / 1000.0 * C.PETG_DENSITY_G_CM3,
            "bbox": (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)),
            "min": (min(xs), min(ys), min(zs)), "verts": len(ob.data.vertices), "faces": len(ob.data.polygons)}


def mass_props(ob):
    """(volume mm3, centroid Vector) in world space, from the triangulated closed mesh."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    mw = ob.matrix_world
    V = 0.0
    Cc = Vector((0.0, 0.0, 0.0))
    for f in bm.faces:
        a, b, c = [mw @ v.co for v in f.verts]
        v6 = a.dot(b.cross(c))
        V += v6 / 6.0
        Cc += (a + b + c) / 4.0 * (v6 / 6.0)
    bm.free()
    if abs(V) < 1e-9:
        return 0.0, Vector((0.0, 0.0, 0.0))
    return V, Cc / V


def bvh_of(ob):
    mw = ob.matrix_world
    verts = [mw @ v.co for v in ob.data.vertices]
    polys = [tuple(p.vertices) for p in ob.data.polygons]
    return BVHTree.FromPolygons(verts, polys, all_triangles=False)


def overlap_count(a, b) -> int:
    return len(bvh_of(a).overlap(bvh_of(b)))


# ---------------------------------------------------------------------------
# Finalize / export
# ---------------------------------------------------------------------------

def clean(ob) -> None:
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def to_print_frame(ob, rot: Matrix) -> None:
    ob.matrix_world = rot @ ob.matrix_world
    apply_transform(ob)
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    ob.location = (-(max(xs) + min(xs)) / 2.0, -(max(ys) + min(ys)) / 2.0, -min(zs))
    apply_transform(ob)


def export_stl(ob, out_path: Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    select_only(ob)
    bpy.ops.wm.stl_export(filepath=str(out_path), export_selected_objects=True, ascii_format=False,
                          global_scale=1.0, apply_modifiers=True)


def write_sidecar(ob, out_path: Path, notes) -> str:
    s = mesh_stats(ob)
    bx, by, bz = s["bbox"]
    lines = [f"{Path(out_path).name}",
             f"  print bbox (mm): {bx:.1f} x {by:.1f} x {bz:.1f}   (Z is print height)",
             f"  solid volume: {s['volume_mm3']/1000.0:.1f} cm3   solid PETG mass: {s['mass_g_petg']:.0f} g (as-printed with infill is less)",
             f"  mesh: {s['verts']} verts / {s['faces']} faces / non-manifold edges: {s['nonmanifold_edges']}"] + [f"  {n}" for n in notes]
    txt = "\n".join(lines) + "\n"
    Path(out_path).with_suffix(".txt").write_text(txt)
    return txt


def finalize_and_export(ob, out_path, print_rot: Matrix, notes, mirror=False) -> str:
    if mirror:
        ob.matrix_world = Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)) @ ob.matrix_world
        apply_transform(ob)
        recalc_normals(ob)
    clean(ob)
    s = mesh_stats(ob)
    if s["nonmanifold_edges"]:
        print(f"WARNING: {ob.name} has {s['nonmanifold_edges']} non-manifold edges")
    to_print_frame(ob, print_rot)
    export_stl(ob, Path(out_path))
    txt = write_sidecar(ob, Path(out_path), notes)
    print(txt)
    return txt


def argv_after_dashdash():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def std_main(make, print_rot, notes, mirror_ok=False):
    """Standard CLI: --out path [--mirror]. `make()` builds the left/reference part."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    if mirror_ok:
        ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args(argv_after_dashdash())
    reset_scene()
    ob = make()
    finalize_and_export(ob, args.out, print_rot, notes, mirror=getattr(args, "mirror", False))


ROT_Y_TO_Z = Matrix.Rotation(math.pi / 2.0, 4, "X")        # +Y -> +Z
ROT_NEGY_TO_Z = Matrix.Rotation(-math.pi / 2.0, 4, "X")    # -Y -> +Z
ROT_X_TO_Z = Matrix.Rotation(-math.pi / 2.0, 4, "Y")       # +X -> +Z
ROT_NEGX_TO_Z = Matrix.Rotation(math.pi / 2.0, 4, "Y")     # -X -> +Z  (== +X -> -Z)
ROT_FLIP = Matrix.Rotation(math.pi, 4, "X")                # +Z -> -Z
ROT_NONE = Matrix.Identity(4)


def rot_dir_to(v, target=(0.0, 0.0, 1.0)) -> Matrix:
    return Vector(v).normalized().rotation_difference(Vector(target).normalized()).to_matrix().to_4x4()
