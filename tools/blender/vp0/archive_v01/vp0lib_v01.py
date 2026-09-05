"""
vp0lib.py -- shared mesh helpers for the vp0 generators. Blender-only.

Everything here builds in the assembly frame described in canon.py and
returns plain mesh objects. Booleans use the EXACT solver. Every part
goes through `finalize()` which checks manifoldness and reports volume.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy  # type: ignore
import bmesh  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

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
    bpy.context.scene.unit_settings.scale_length = 0.001  # 1 BU = 1 mm


def _link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def obj_from_bm(name: str, bm) -> bpy.types.Object:
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.update()
    return _link(bpy.data.objects.new(name, me))


def obj_from_pydata(name: str, verts, faces) -> bpy.types.Object:
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
# Primitives
# ---------------------------------------------------------------------------

def add_box(name, center, dims) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.active_object
    ob.name = name
    ob.location = center
    ob.scale = dims
    apply_transform(ob)
    return ob


def _axis_rot(axis: str) -> Matrix:
    """Rotation taking local +Z to the requested world axis."""
    return {
        "Z": Matrix.Identity(4),
        "-Z": Matrix.Rotation(math.pi, 4, "X"),
        "Y": Matrix.Rotation(-math.pi / 2.0, 4, "X"),
        "-Y": Matrix.Rotation(math.pi / 2.0, 4, "X"),
        "X": Matrix.Rotation(math.pi / 2.0, 4, "Y"),
        "-X": Matrix.Rotation(-math.pi / 2.0, 4, "Y"),
    }[axis]


def add_cyl(name, center, radius, depth, axis="Z", verts=64) -> bpy.types.Object:
    """Cylinder centred at `center` with its axis along `axis`."""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts)
    ob = bpy.context.active_object
    ob.name = name
    ob.matrix_world = Matrix.Translation(Vector(center)) @ _axis_rot(axis)
    apply_transform(ob)
    return ob


def add_hex_prism(name, center, across_flats, depth, axis="Z") -> bpy.types.Object:
    r = across_flats / math.sqrt(3.0)
    return add_cyl(name, center, r, depth, axis=axis, verts=6)


def revolve(name, profile, axis="Y", center=(0.0, 0.0, 0.0), segments=128) -> bpy.types.Object:
    """
    Revolve a closed (r, n) polygon about an axis. n is the local axial
    coordinate (0 at `center`, increasing along `axis`); r is radius.
    Profile must not touch r == 0 (put a small bore there instead).
    """
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0.0, n)) for r, n in profile]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 1.0),
                   dvec=(0.0, 0.0, 0.0), angle=2.0 * math.pi, steps=segments,
                   use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    M = Matrix.Translation(Vector(center)) @ _axis_rot(axis)
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return obj_from_bm(name, bm)


def serration_solid(name, face_pt, normal, r_in=C.SERR_R_IN, r_out=C.SERR_R_OUT,
                    teeth=C.SERR_TEETH, height=C.SERR_H, overlap=C.SERR_OVERLAP,
                    phase_deg=0.0, valley=-0.15) -> bpy.types.Object:
    """
    Annular ring of triangular teeth standing on a plane. `face_pt` is a
    point on the host face (on the ring axis), `normal` the outward face
    normal. The solid sinks `overlap` into the host so the union is robust;
    valleys sit `valley` (negative) below the face so no tooth triangle is
    coplanar with the host face (the EXACT solver leaves non-manifold
    edges otherwise).
    """
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


# ---------------------------------------------------------------------------
# Curves + ribbons
# ---------------------------------------------------------------------------

def catmull_rom(waypoints, samples_per_seg=16):
    """Uniform Catmull-Rom through N-dimensional waypoints (tuples). Returns tuples."""
    import numpy as np
    P = [np.array(waypoints[0], dtype=float)] + [np.array(w, dtype=float) for w in waypoints] + \
        [np.array(waypoints[-1], dtype=float)]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        last = (i == len(P) - 3)
        n = samples_per_seg + (1 if last else 0)
        for k in range(n):
            t = k / samples_per_seg
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                       + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)
            out.append(tuple(q.tolist()))
    return out


def ribbon(name, pts, wide, ext) -> bpy.types.Object:
    """
    Sweep a rectangle along a polyline.
      pts  : list of Vector centreline stations
      wide : Vector or list[Vector]; the "wide" direction W (re-orthogonalised to T)
      ext  : per-station (w_pos, w_neg, n_pos, n_neg) extents along W and N,
             where N = T x W. Negative values are allowed (offsets the section).
    """
    n = len(pts)
    verts = []
    for i in range(n):
        p = Vector(pts[i])
        if i == 0:
            T = Vector(pts[1]) - Vector(pts[0])
        elif i == n - 1:
            T = Vector(pts[-1]) - Vector(pts[-2])
        else:
            T = Vector(pts[i + 1]) - Vector(pts[i - 1])
        T.normalize()
        W = Vector(wide[i] if isinstance(wide, (list, tuple)) and not isinstance(wide[0], (int, float)) else wide)
        W = (W - T * W.dot(T)).normalized()
        N = T.cross(W).normalized()
        wp, wn, npos, nneg = ext[i]
        verts += [p + W * wp + N * npos,
                  p + W * wp - N * nneg,
                  p - W * wn - N * nneg,
                  p - W * wn + N * npos]
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


def superellipse_yz(a, b, n_exp, samples=241):
    """Points (0, y, z) for the upper half of |y/a|^n + |z/b|^n = 1, from (+a,0) over to (-a,0)."""
    pts = []
    for i in range(samples):
        t = math.pi * i / (samples - 1)
        c, s = math.cos(t), math.sin(t)
        y = a * math.copysign(abs(c) ** (2.0 / n_exp), c)
        z = b * abs(s) ** (2.0 / n_exp)
        pts.append(Vector((0.0, y, z)))
    return pts


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


def mirror_y(ob, name=None) -> bpy.types.Object:
    """Mirrored copy across the XZ plane (left <-> right)."""
    new = ob.copy()
    new.data = ob.data.copy()
    new.name = name or (ob.name + "_R")
    _link(new)
    new.matrix_world = Matrix.Diag((1.0, -1.0, 1.0, 1.0)) @ ob.matrix_world
    apply_transform(new)
    recalc_normals(new)
    return new


# ---------------------------------------------------------------------------
# Standard sub-assemblies
# ---------------------------------------------------------------------------

def ring_paddle(name, center_y, radius, side=+1) -> bpy.types.Object:
    """
    Plain arm ring on the pivot axis (X=0, Z=0) at Y=center_y, thickness
    RING_T, axis along Y, bored for the M5 pivot. Built as a revolve (not a
    cylinder primitive) because the EXACT solver leaves non-manifold edges
    when serrations are unioned onto an n-gon cap. Apply `serrate()` LAST.
    """
    rb = C.M5_CLEAR_DIA / 2.0
    t = C.RING_T / 2.0
    return revolve(name, [(rb, -t), (radius, -t), (radius, t), (rb, t)],
                     axis="Y", center=(0.0, center_y, 0.0), segments=96)


def serrate(host, center_y, side=+1, serr_in=True, serr_out=True):
    """Union serration rings onto the +/-Y faces of a ring at Y=center_y.
    Must be the final boolean on the part (later cuts through the serrated
    region leave non-manifold slivers)."""
    inb = -side
    if serr_in:
        union(host, serration_solid(host.name + "_sin", (0.0, center_y + inb * C.RING_T / 2.0, 0.0), (0.0, inb, 0.0)))
    if serr_out:
        union(host, serration_solid(host.name + "_sout", (0.0, center_y - inb * C.RING_T / 2.0, 0.0), (0.0, -inb, 0.0)))
    return host


def pivot_bore(host, center_y, length=40.0):
    cut(host, add_cyl("bore", (0.0, center_y, 0.0), C.M5_CLEAR_DIA / 2.0, length, axis="Y", verts=48))
    return host


def head_phantom(name="head_phantom") -> bpy.types.Object:
    a, b, c = C.HEAD.phantom_semi
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=32)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (a, b, c)
    ob.location = (0.0, 0.0, C.HEAD.phantom_center_z)
    apply_transform(ob)
    neck = add_cyl(name + "_neck", (-15.0, 0.0, -110.0), 52.0, 140.0, axis="Z", verts=48)
    union(ob, neck)
    return ob


# ---------------------------------------------------------------------------
# Finalize / export
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
    return {
        "nonmanifold_edges": nonman,
        "volume_mm3": vol,
        "mass_g_petg": vol / 1000.0 * C.PETG_DENSITY_G_CM3,
        "bbox": (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)),
        "min": (min(xs), min(ys), min(zs)),
        "verts": len(ob.data.vertices),
        "faces": len(ob.data.polygons),
    }


def clean(ob) -> None:
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def to_print_frame(ob, rot: Matrix) -> None:
    """Rotate into print orientation, then rest on Z=0 centred on XY."""
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
    bpy.ops.wm.stl_export(filepath=str(out_path), export_selected_objects=True,
                          ascii_format=False, global_scale=1.0, apply_modifiers=True)


def write_sidecar(ob, out_path: Path, notes: list[str]) -> str:
    s = mesh_stats(ob)
    bx, by, bz = s["bbox"]
    lines = [
        f"{Path(out_path).name}",
        f"  print bbox (mm): {bx:.1f} x {by:.1f} x {bz:.1f}   (Z is print height)",
        f"  volume: {s['volume_mm3']/1000.0:.1f} cm3   est. mass PETG: {s['mass_g_petg']:.0f} g",
        f"  mesh: {s['verts']} verts / {s['faces']} faces / non-manifold edges: {s['nonmanifold_edges']}",
    ] + [f"  {n}" for n in notes]
    txt = "\n".join(lines) + "\n"
    Path(out_path).with_suffix(".txt").write_text(txt)
    return txt


def finalize_and_export(ob, out_path, print_rot: Matrix, notes: list[str]) -> str:
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


# Print-orientation rotations (assembly frame -> print frame, Z up)
ROT_Y_TO_Z = Matrix.Rotation(math.pi / 2.0, 4, "X")        # +Y -> +Z
ROT_NEGY_TO_Z = Matrix.Rotation(-math.pi / 2.0, 4, "X")    # -Y -> +Z
ROT_X_TO_Z = Matrix.Rotation(-math.pi / 2.0, 4, "Y")       # +X -> +Z
ROT_FLIP = Matrix.Rotation(math.pi, 4, "X")                # +Z -> -Z
ROT_NONE = Matrix.Identity(4)
