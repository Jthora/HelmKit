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
    outward_normals(ob)
    return ob


def outward_normals(ob) -> None:
    """Make face normals consistent and outward (fresh single-shell primitives only)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def recalc_normals(ob) -> None:
    """Flip every face (used after a mirror transform). Keeps sealed cavities inward-facing: a global
    'recalc outward' would turn an internal void into an overlapping solid and double the volume."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
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


def add_cone(name, center, r_base, r_top, depth, axis="Z", verts=32):
    """Truncated cone: r_base at the -axis end, r_top at the +axis end (countersinks: wide end toward the screw head)."""
    bpy.ops.mesh.primitive_cone_add(radius1=r_base, radius2=r_top, depth=depth, vertices=verts)
    ob = bpy.context.active_object
    ob.name = name
    ob.matrix_world = Matrix.Translation(Vector(center)) @ _axis_rot(axis)
    apply_transform(ob)
    return ob


def add_cone_local(name, M: Matrix, center, r_base, r_top, depth, axis="Z", verts=32):
    bpy.ops.mesh.primitive_cone_add(radius1=r_base, radius2=r_top, depth=depth, vertices=verts)
    ob = bpy.context.active_object
    ob.name = name
    ob.matrix_world = M @ Matrix.Translation(Vector(center)) @ _axis_rot(axis)
    apply_transform(ob)
    return ob


_AXES = {"Z": (0.0, 0.0, 1.0), "-Z": (0.0, 0.0, -1.0), "Y": (0.0, 1.0, 0.0), "-Y": (0.0, -1.0, 0.0), "X": (1.0, 0.0, 0.0), "-X": (-1.0, 0.0, 0.0)}


def add_teardrop_local(name, M, center, radius, depth, axis="Z", up=(0.0, 1.0, 0.0), verts=24):
    """v0.17: a hole for printing HORIZONTAL: a cylinder with a 45-deg roof toward `up` (the print's up, perpendicular to the
    axis), so no bridge sags into the bore. `axis` is a name or a vector, `up` a vector, both in M's frame (M None = world)."""
    ax = Vector(_AXES[axis]) if isinstance(axis, str) else Vector(axis).normalized()
    upv = Vector(up); upv = (upv - ax * upv.dot(ax)).normalized()
    ex = upv.cross(ax).normalized()
    ey = ax.cross(ex)
    R = Matrix(((ex.x, ey.x, ax.x), (ex.y, ey.y, ax.y), (ex.z, ey.z, ax.z))).to_4x4()
    F = (M if M is not None else Matrix.Identity(4)) @ Matrix.Translation(Vector(center)) @ R
    poly = []
    for i in range(verts + 1):
        t = math.radians(135.0 + 270.0 * i / verts)
        poly.append((radius * math.cos(t), radius * math.sin(t)))
    poly.append((0.0, radius * math.sqrt(2.0)))
    return extrude_polygon(name, poly, depth, F, z0=-depth / 2.0)


def add_teardrop(name, center, radius, depth, axis, up, verts=24):
    return add_teardrop_local(name, None, center, radius, depth, axis, up, verts)


def lr_notches(ob, side, center, along, size=1.5, pitch=3.0, thru=None):
    """v0.17: cut one small notch on a LEFT part, two on a RIGHT part, along a visible edge (centre and direction in world).
    thru=(axis_index, length): a nick THROUGH a thin plate (the box is `length` long on that world axis) so no wall thins."""
    n = 1 if side > 0 else 2
    a = Vector(along).normalized()
    c = Vector(center)
    dims = [size, size, size]
    if thru is not None:
        dims[thru[0]] = thru[1]
    for i in range(n):
        p = c + a * ((i - (n - 1) / 2.0) * pitch)
        cut(ob, add_box("lrnotch", (p.x, p.y, p.z), tuple(dims)))
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


def loft_ring(name, stations, axis="Z", center=(0.0, 0.0, 0.0)):
    """
    Closed ring lofted through per-angle (r, n) profiles: stations = [(angle_deg, [(r, n), ...]), ...]
    in increasing angle over one turn, all profiles the same length. Quads join consecutive
    stations and the loop closes, so a profile that varies with angle (a cam groove) stays manifold.
    """
    bm = bmesh.new()
    rings = []
    for ang, prof in stations:
        a = math.radians(ang)
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), n)) for (r, n) in prof])
    m, k = len(rings), len(rings[0])
    for i in range(m):
        A, B = rings[i], rings[(i + 1) % m]
        for j in range(k):
            bm.faces.new((A[j], A[(j + 1) % k], B[(j + 1) % k], B[j]))
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


def ridge_plate_poly(u0, u1, pitch, height, base, phase, valley=-0.1):
    """Triangle-wave ridges along u (peaks at u = phase + k*pitch) on a base plate from v=-base up.
    Valleys sit slightly below the host face (valley < 0) so no ridge vertex lies on it."""
    pts = [(u0, -base), (u0, valley)]
    k0 = math.floor((u0 - phase) / pitch) - 1
    k1 = math.ceil((u1 - phase) / pitch) + 1
    for k in range(k0, k1 + 1):
        peak = phase + k * pitch
        valley_u = peak + pitch / 2.0
        for u, v in ((peak, height), (valley_u, valley)):
            if u0 < u < u1:
                pts.append((u, v))
    pts += [(u1, valley), (u1, -base)]
    return pts


# ---------------------------------------------------------------------------
# Serrations / curves / ribbons
# ---------------------------------------------------------------------------

def serration_solid(name, face_pt, normal, r_in=7.5, r_out=12.0, teeth=24, height=1.0, overlap=0.6,
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


def resample_polyline(pts, step):
    """Resample a polyline of Vectors at (roughly) uniform arc-length spacing; keeps both ends."""
    pts = [Vector(p) for p in pts]
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg)
    n = max(2, int(round(total / step)))
    targets = [total * k / n for k in range(n + 1)]
    out, acc, i = [], 0.0, 0
    for t in targets:
        while i < len(seg) - 1 and acc + seg[i] < t:
            acc += seg[i]
            i += 1
        f = 0.0 if seg[i] < 1e-9 else min(1.0, max(0.0, (t - acc) / seg[i]))
        out.append(pts[i] + (pts[i + 1] - pts[i]) * f)
    return out


def arc_index_range(pts, from_start, from_end):
    """Station indices whose arc-length position is >= from_start and <= total - from_end."""
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + (Vector(pts[i]) - Vector(pts[i - 1])).length)
    return [i for i in range(len(pts)) if from_start <= d[i] <= d[-1] - from_end]


def ribbon(name, pts, wide, ext, chamfer=0.0):
    """
    Sweep a rectangle along a polyline. pts: centreline Vectors; wide: W direction
    (Vector or per-station list); ext: per-station (w_pos, w_neg, n_pos, n_neg),
    N = T x W. `chamfer` > 0 cuts every corner of the section at 45 deg by that
    amount (octagonal section: rounded-looking edges without a bevel pass).
    """
    n = len(pts)
    verts = []
    per_station = isinstance(wide, (list, tuple)) and len(wide) == n and not isinstance(wide[0], (int, float))
    K = 8 if chamfer > 0 else 4
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
        if chamfer > 0:
            c = min(chamfer, (wp + wn) / 4.0, (npos + nneg) / 4.0)
            verts += [p + W * wp + N * (npos - c), p + W * (wp - c) + N * npos,
                      p - W * (wn - c) + N * npos, p - W * wn + N * (npos - c),
                      p - W * wn - N * (nneg - c), p - W * (wn - c) - N * nneg,
                      p + W * (wp - c) - N * nneg, p + W * wp - N * (nneg - c)]
        else:
            verts += [p + W * wp + N * npos, p + W * wp - N * nneg, p - W * wn - N * nneg, p - W * wn + N * npos]
    faces = []
    for i in range(n - 1):
        a, b2 = K * i, K * (i + 1)
        for k in range(K):
            k2 = (k + 1) % K
            faces.append((a + k, a + k2, b2 + k2, b2 + k))
    faces.append(tuple(reversed(range(K))))
    e = K * (n - 1)
    faces.append(tuple(e + k for k in range(K)))
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

def fillet(ob, width=None, segments=None, angle_deg=45.0):
    """Bevel every edge sharper than angle_deg. Reverts if the result is not manifold."""
    width = C.FILLET_MM if width is None else width
    segments = C.FILLET_SEGMENTS if segments is None else segments
    backup = ob.data.copy()
    mod = ob.modifiers.new("fillet", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle_deg)
    mod.use_clamp_overlap = True
    mod.miter_outer = "MITER_ARC"
    select_only(ob)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    s = mesh_stats(ob)
    if s["nonmanifold_edges"] or s["volume_mm3"] <= 0:
        print(f"fillet reverted on {ob.name} ({s['nonmanifold_edges']} non-manifold edges)")
        old = ob.data
        ob.data = backup
        bpy.data.meshes.remove(old)
        return False
    bpy.data.meshes.remove(backup)
    return True


# --- port standard: flush sockets ------------------------------------------

def pod_port_frame(angle_deg, side=+1):
    """Mouth frame of a pod port on the skirt surface: local Z = outward radial, local X = +/-Y (screw axis)."""
    a = math.radians(angle_deg)
    d = Vector((math.cos(a), 0.0, math.sin(a)))
    mouth = Vector((C.CX, side * C.POD_PORT_Y, C.CZ)) + d * C.DISH_R
    return frame(mouth, d, (0.0, side, 0.0))


def port_tunnel(name, M: Matrix, sink=0.5):
    """Housing around a socket sunk into a body, from just inside the mouth plane inward (local -Z)."""
    s = C.PORT_SQ + C.PORT_CLEAR + 2 * C.PORT_TUNNEL_WALL
    length = C.PORT_DEPTH + C.PORT_TUNNEL_WALL - sink
    return add_box_local(name, M, (0.0, 0.0, -sink - length / 2.0), (s, s, length))


def rounded_rect_poly(w, h, r, n=6):
    """CCW rounded rectangle centred on the origin (u, v)."""
    pts = []
    cx, cy = w / 2.0 - r, h / 2.0 - r
    for x0, y0, a0 in ((cx, cy, 0.0), (-cx, cy, 90.0), (-cx, -cy, 180.0), (cx, -cy, 270.0)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((x0 + r * math.cos(a), y0 + r * math.sin(a)))
    return pts


def port_socket_cut(M: Matrix, tag=""):
    sq = C.PORT_SQ + C.PORT_CLEAR + (2 * C.CAST_OVERSIZE if C.CAST_SOCKETS else 0.0)
    poly = rounded_rect_poly(sq, sq, C.PORT_CORNER_R + C.PORT_CLEAR / 2.0)
    return extrude_polygon("psock" + tag, poly, C.PORT_DEPTH + 1.0, M, z0=-C.PORT_DEPTH)


def rounded_post(name, M: Matrix, length, z0):
    """10 mm post with rounded long edges along local Z from z0 to z0+length."""
    return extrude_polygon(name, rounded_rect_poly(C.PORT_SQ, C.PORT_SQ, C.PORT_CORNER_R), length, M, z0=z0)


def port_pin_cutters(M: Matrix, x_far, x_near, tag=""):
    """Nail pin in double shear along local X at the pin depth: through hole from x_far (beyond the far
    wall) to x_near (beyond the near, accessible face) plus a head counterbore at the near face."""
    tools = [add_cyl_local("ppin" + tag, M, ((x_far + x_near) / 2.0, 0.0, -C.PORT_PIN_DEPTH),
                           C.PIN_DIA / 2.0, abs(x_near - x_far), axis="X", verts=24),
             add_cyl_local("phead" + tag, M, (x_near - 1.0 - C.PIN_HEAD_DEPTH / 2.0 + 1.0, 0.0, -C.PORT_PIN_DEPTH),
                           C.PIN_HEAD_DIA / 2.0, C.PIN_HEAD_DEPTH + 2.0, axis="X", verts=24)]
    return tools


def collar_cutter(M: Matrix, center_z, size, tag=""):
    """Shallow groove ring around a square block (thread-and-epoxy wrap seat): a frame of COLLAR_GROOVE depth."""
    w, d = C.COLLAR_GROOVE
    outer = add_box_local("collar_o" + tag, M, (0.0, 0.0, center_z), (size + 2.0, size + 2.0, w))
    inner = add_box_local("collar_i" + tag, M, (0.0, 0.0, center_z), (size - 2 * d, size - 2 * d, w + 2.0))
    return cut(outer, inner)


def clam_cleat(name, M: Matrix, base_z=0.0):
    """
    No-moving-parts rope cleat: a block with a V-slot along local X that narrows downward; transverse
    grooves on both jaws. Rope enters from -X under load, the tail leaves +X; pull the tail to
    tighten, lift the rope out of the V to release. Dimensions from canon CLEAT.
    """
    K = C.CLEAT
    Lc, Wc, Hc = K["length"], K["width"], K["height"]
    blk = add_box_local(name, M, (0.0, 0.0, base_z + Hc / 2.0), (Lc, Wc, Hc))
    tw, bw = K["top_w"], K["bot_w"]
    slot_bottom = base_z + Hc - 8.0
    poly = [(-tw / 2, base_z + Hc + 1.0), (tw / 2, base_z + Hc + 1.0), (bw / 2, slot_bottom), (-bw / 2, slot_bottom)]
    Mv = M @ frame((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))   # extrude along local X; poly in (y, z)
    cut(blk, extrude_polygon("vslot", poly, Lc + 2.0, Mv, z0=-Lc / 2.0 - 1.0))
    half = math.atan2((tw - bw) / 2.0, 8.0)
    for k in range(K["teeth"]):
        x = -Lc / 2.0 + Lc * (k + 0.5) / K["teeth"]
        for sy in (+1, -1):
            # cylinder lying along the jaw face (direction tilted by the V half-angle), axis on the face
            ymid = sy * (bw / 2 + (tw - bw) / 4.0)
            zmid = slot_bottom + 4.0
            d = Vector((0.0, sy * math.sin(half), math.cos(half)))
            Mt = M @ frame((x, ymid, zmid), d, (1.0, 0.0, 0.0))
            cut(blk, add_cyl_local("tooth", Mt, (0.0, 0.0, 0.0), K["tooth_h"] + 0.3, 10.0, axis="Z", verts=16))
    return blk


def port_screw_cutters(M: Matrix, wall_from, wall_to, tag=""):
    """Locking screw along local +X: clearance hole from local x=wall_from (inside the socket) to wall_to
    (outer face), counterbore 2 mm at the outer face."""
    tools = [add_cyl_local("pscrew" + tag, M, ((wall_from + wall_to) / 2.0, 0.0, -C.PORT_PIN_DEPTH),
                           C.M3_CLEAR_DIA / 2.0, wall_to - wall_from, axis="X", verts=24),
             add_cyl_local("pcbore" + tag, M, (wall_to - 0.5, 0.0, -C.PORT_PIN_DEPTH), 3.1, 3.0, axis="X", verts=24)]
    return tools


def port_plug(name, M: Matrix, lip=None):
    """Rounded post into the socket (local -Z from the mouth). Optional lip (square side, thickness) on the mouth plane."""
    post = rounded_post(name, M, C.PORT_PLUG_LEN, -C.PORT_PLUG_LEN)
    if lip:
        side, t = lip
        union(post, add_box_local(name + "_lip", M, (0.0, 0.0, t / 2.0 - 0.5), (side, side, t + 1.0)))
    return post


def port_plug_thread_hole(M: Matrix, tag=""):
    """Thread-forming M3 hole through the post along local X at the screw depth."""
    return add_cyl_local("pthr" + tag, M, (0.0, 0.0, -C.PORT_PIN_DEPTH), C.M3_TAP_DIA / 2.0, C.PORT_SQ + 4.0, axis="X", verts=16)


def coupler(name, length):
    """Double-male rounded post along local Z, centred, pin holes PORT_PIN_DEPTH from each end (along X)."""
    c = rounded_post(name, Matrix.Identity(4), length, -length / 2.0)
    for z in (length / 2.0 - C.PORT_PIN_DEPTH, -(length / 2.0 - C.PORT_PIN_DEPTH)):
        cut(c, add_cyl("pin", (0.0, 0.0, z), C.PIN_DIA / 2.0, C.PORT_SQ + 6.0, axis="X", verts=24))
    return c


def face_ratchet_ring(name, face_pt, normal, r_in, r_out, teeth, height, overlap=0.6, direction=+1):
    """
    Axial sawtooth ring standing on a face: each tooth rises steeply at its start and slopes back to
    the face over one pitch. Two rings generated with the same `direction` on facing surfaces mesh;
    turning one way rides the ramps, the other way locks. Flip `direction` to swap.
    """
    bm = bmesh.new()
    p = 2.0 * math.pi / teeth
    T = []
    for k in range(teeth):
        a0, a1 = direction * k * p, direction * (k + 1) * p
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        T.append(dict(hi_i=bm.verts.new((r_in * c0, r_in * s0, height)), hi_o=bm.verts.new((r_out * c0, r_out * s0, height)),
                      lo_i=bm.verts.new((r_in * c1, r_in * s1, -0.1)), lo_o=bm.verts.new((r_out * c1, r_out * s1, -0.1)),
                      b_i=bm.verts.new((r_in * c0, r_in * s0, -overlap)), b_o=bm.verts.new((r_out * c0, r_out * s0, -overlap))))
    n = teeth
    for k in range(n):
        t, nx, pv = T[k], T[(k + 1) % n], T[(k - 1) % n]
        bm.faces.new((t["hi_i"], t["hi_o"], t["lo_o"], t["lo_i"]))            # ramp
        bm.faces.new((t["lo_i"], t["lo_o"], nx["hi_o"], nx["hi_i"]))          # step
        bm.faces.new((t["b_o"], nx["b_o"], t["lo_o"], t["hi_o"], pv["lo_o"]))  # outer wall
        bm.faces.new((pv["lo_i"], t["hi_i"], t["lo_i"], nx["b_i"], t["b_i"]))  # inner wall
        bm.faces.new((t["b_i"], nx["b_i"], nx["b_o"], t["b_o"]))              # bottom
    bmesh.ops.triangulate(bm, faces=bm.faces, ngon_method="EAR_CLIP")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(Vector(normal).normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(face_pt)) @ rot, verts=bm.verts)
    return obj_from_bm(name, bm)


def foam_ring(name, center, r_out, r_in, thickness, axis="Y"):
    return revolve(name, [(r_in, 0.0), (r_out, 0.0), (r_out, thickness), (r_in, thickness)], axis=axis, center=center, segments=96)


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
    return {"nonmanifold_edges": nonman, "volume_mm3": vol, "mass_g_petg": vol / 1000.0 * C.DENSITY_G_CM3,
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
             f"  solid volume: {s['volume_mm3']/1000.0:.1f} cm3   solid mass: {s['mass_g_petg']:.0f} g (as-printed with infill is less)",
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
