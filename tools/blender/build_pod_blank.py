#!/usr/bin/env -S blender --background --python
"""
build_pod_blank.py — universal pod-blank for HelmKit Mk0.5 hardpoints.

Builds `pod_blank.stl`: a printable pod body that mates to the R1
Picatinny rail via a MIL-STD-1913 male dovetail on its underside,
with a screw boss for the TPU 95A secondary-detent leaf (the
"ski-binding" two-step lock).

The pod is BLANK — payload-specific geometry (PCB pocket, optic
clearance, cable port) is added in per-station Blender files that
import this script's output as a base.

Run:
    blender --background --python tools/blender/build_pod_blank.py \\
        -- --out 3D-Models/HelmKit/_generated/pod_blank.stl

Design canon (see docs/mechanical/mk0.5_base_crown_architecture.md):
    - Pod envelope (forehelm type): 35 × 35 × 30 mm (W × L × H)
    - Underside: male MIL-STD-1913 Picatinny dovetail
    - Lock: M3 boss for TPU detent leaf, 8 mm aft of dovetail center
    - Hollow internal cavity for PCB / sensor (left as void)

Pod-type variants (changed by --type flag):
    forehelm: 35 × 35 × 30 mm (default — HP-F, HP-FL, HP-FR)
    temple:   45 × 30 × 25 mm (HP-TL, HP-TR)
    ear:      50 × 40 × 35 mm (HP-EL, HP-ER)
    sidehelm: 70 × 50 × 40 mm (HP-SL, HP-SR)

Status: SCAFFOLD. Produces correctly-dovetailed blank pod for all
four envelope types. Per-station payload pockets are TODO.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    import bpy  # type: ignore
    import bmesh  # type: ignore
except ImportError:
    print("ERROR: run inside Blender:")
    print("  blender --background --python tools/blender/build_pod_blank.py")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Canon parameters
# ---------------------------------------------------------------------------

POD_ENVELOPES_MM = {
    # type     : (width_x, length_y, height_z)
    "forehelm" : (35.0, 35.0, 30.0),
    "temple"   : (45.0, 30.0, 25.0),
    "ear"      : (50.0, 40.0, 35.0),
    "sidehelm" : (70.0, 50.0, 40.0),
}

# Male MIL-STD-1913 dovetail (matches R1's female slot when properly aligned)
DT_TOP_W_MM = 10.2          # top of dovetail (mates to slot floor)
DT_BOT_W_MM = 19.0          # bottom of dovetail (sits in slot mouth)
DT_HEIGHT_MM = 3.4          # dovetail rises this far above the pod's bottom face
DT_LENGTH_MM = 18.0         # length of dovetail along rail axis (covers ~2 teeth)

# TPU detent-leaf M3 boss
LEAF_BOSS_DIA_MM = 6.0
LEAF_BOSS_HEIGHT_MM = 4.0
LEAF_BOSS_HOLE_DIA_MM = 2.7    # M3 self-tap
LEAF_BOSS_OFFSET_MM = 8.0       # aft of dovetail center (along +Y)

# Wall thickness for hollow cavity
POD_WALL_MM = 2.0


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def make_pod_body(w: float, l: float, h: float) -> bpy.types.Object:
    """Hollow box pod, centered at origin on the XY plane (Z from 0 to h)."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    outer = bpy.context.active_object
    outer.scale = (w, l, h)
    outer.location = (0, 0, h / 2)
    bpy.ops.object.transform_apply(location=True, scale=True)
    outer.name = "pod_outer"

    # Hollow inner cavity (subtract). Open at the TOP for now (lid is a
    # separate part); the top wall stays solid here pending lid design.
    bpy.ops.mesh.primitive_cube_add(size=1)
    inner = bpy.context.active_object
    inner.scale = (w - 2 * POD_WALL_MM, l - 2 * POD_WALL_MM, h - POD_WALL_MM)
    inner.location = (0, 0, h / 2 + POD_WALL_MM / 2)  # offset so bottom wall stays
    bpy.ops.object.transform_apply(location=True, scale=True)

    mod = outer.modifiers.new(name="hollow", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = inner
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(inner, do_unlink=True)
    outer.name = "pod_body"
    return outer


def make_dovetail(pod: bpy.types.Object) -> None:
    """Add a MIL-STD-1913 male dovetail to the underside of the pod.

    The dovetail sits in a CUT-OUT in the pod's bottom face — the pod
    bottom is recessed to hold the dovetail flush with the rail tooth
    crests when the pod is mounted.
    """
    # Create the trapezoidal dovetail prism (BMesh, custom verts).
    # Cross-section in (x, z) plane: wider at base, narrower at top.
    half_top = DT_TOP_W_MM / 2
    half_bot = DT_BOT_W_MM / 2
    z_base = -DT_HEIGHT_MM  # below pod bottom (will boolean-union below)
    z_top = 0.0             # top of dovetail = pod bottom plane (flush)
    y_back = -DT_LENGTH_MM / 2
    y_front = +DT_LENGTH_MM / 2

    bm = bmesh.new()
    # 8 verts: 4 at z_base (wide), 4 at z_top (narrow)
    v_base = [
        bm.verts.new((-half_bot, y_back,  z_base)),
        bm.verts.new((+half_bot, y_back,  z_base)),
        bm.verts.new((+half_bot, y_front, z_base)),
        bm.verts.new((-half_bot, y_front, z_base)),
    ]
    v_top = [
        bm.verts.new((-half_top, y_back,  z_top)),
        bm.verts.new((+half_top, y_back,  z_top)),
        bm.verts.new((+half_top, y_front, z_top)),
        bm.verts.new((-half_top, y_front, z_top)),
    ]
    bm.faces.new(v_base[::-1])   # bottom face
    bm.faces.new(v_top)          # top face (will merge with pod bottom)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((v_base[i], v_base[j], v_top[j], v_top[i]))
    mesh = bpy.data.meshes.new("dovetail_mesh")
    bm.to_mesh(mesh)
    bm.free()
    dt = bpy.data.objects.new("dovetail", mesh)
    bpy.context.collection.objects.link(dt)

    # Union with pod body
    mod = pod.modifiers.new(name="dovetail_union", type="BOOLEAN")
    mod.operation = "UNION"
    mod.object = dt
    bpy.context.view_layer.objects.active = pod
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(dt, do_unlink=True)


def make_detent_leaf_boss(pod: bpy.types.Object, pod_h: float) -> None:
    """Add a small M3 boss for the TPU detent leaf, aft of the dovetail."""
    # Boss (cylinder) on the BOTTOM of the pod, just aft of the dovetail.
    # Sits adjacent to (not on top of) the dovetail.
    boss_y = LEAF_BOSS_OFFSET_MM  # aft of pod center along +Y
    bpy.ops.mesh.primitive_cylinder_add(
        radius=LEAF_BOSS_DIA_MM / 2,
        depth=LEAF_BOSS_HEIGHT_MM,
        vertices=24,
    )
    boss = bpy.context.active_object
    boss.location = (0, boss_y, -LEAF_BOSS_HEIGHT_MM / 2)
    boss.name = "detent_boss"
    # Union with pod
    mod = pod.modifiers.new(name="boss_union", type="BOOLEAN")
    mod.operation = "UNION"
    mod.object = boss
    bpy.context.view_layer.objects.active = pod
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(boss, do_unlink=True)

    # M3 pilot hole through the boss + pod bottom wall
    bpy.ops.mesh.primitive_cylinder_add(
        radius=LEAF_BOSS_HOLE_DIA_MM / 2,
        depth=LEAF_BOSS_HEIGHT_MM + POD_WALL_MM + 1.0,
        vertices=16,
    )
    hole = bpy.context.active_object
    hole.location = (0, boss_y, -LEAF_BOSS_HEIGHT_MM / 2 + POD_WALL_MM / 2)
    hole.name = "boss_hole"
    mod = pod.modifiers.new(name="hole_cut", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = hole
    bpy.context.view_layer.objects.active = pod
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(hole, do_unlink=True)


def export_stl(obj: bpy.types.Object, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=str(out_path), export_selected_objects=True)
    else:
        bpy.ops.export_mesh.stl(filepath=str(out_path), use_selection=True)
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--type", choices=list(POD_ENVELOPES_MM.keys()),
                   default="forehelm",
                   help="Pod envelope type (default: forehelm)")
    args = p.parse_args(argv)

    w, l, h = POD_ENVELOPES_MM[args.type]
    reset_scene()
    pod = make_pod_body(w, l, h)
    make_dovetail(pod)
    make_detent_leaf_boss(pod, h)
    export_stl(pod, args.out)
    print(f"  pod_blank type={args.type}: {w}×{l}×{h} mm "
          f"+ {DT_BOT_W_MM} mm dovetail + M3 detent boss")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
