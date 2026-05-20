#!/usr/bin/env -S blender --background --python
"""
envelope_visor_swing.py — Phase-3 collision-check geometry.

Sweeps the Forward Visor-Band through all 5 detent positions and
unions every pose into a single STL alongside the Temple Plate
silhouette. Purpose: visually confirm the §12 IFACE_TEMPLE_FWDBAND
numbers don't produce collisions (with ear envelope, opposite
Temple Plate, or itself at 90° stow) before any parametric
generator commits to them.

This is THROWAWAY geometry — primitive boxes / arcs only, no
fillets, ribs, bolts, or printable detail.

Run:
    /Applications/Blender.app/Contents/MacOS/Blender --background \\
        --python tools/blender/envelope_visor_swing.py -- \\
        --out 3D-Models/HelmKit/_envelopes/visor_swing.stl

Source-of-truth: docs/mechanical/mk0.5_topology_beta_architecture.md
§12 IFACE_TEMPLE_FWDBAND.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    import bpy  # type: ignore
except ImportError:
    print("ERROR: run inside Blender (--python ...).")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Canon (mirrors §12 IFACE_TEMPLE_FWDBAND + anthropometric envelope)
# ---------------------------------------------------------------------------

# Hinge axis on Temple Plate (local mm)
HINGE_AXIS_X_MM = 8.0       # +8 fwd of plate datum
HINGE_AXIS_Z_MM = -6.0      # 6 mm below datum
# Temple Plate is L/R symmetric about Y=0; place L at +Y, R at -Y.
TEMPLE_PLATE_Y_MM = 78.0    # ear-to-ear half-width (anthropometric, §2)

# Detent angles (band rotation about hinge axis, from horizontal-down)
DETENT_ANGLES_DEG = (0.0, 30.0, 45.0, 60.0, 90.0)

# Forward Visor-Band crude envelope
FWDBAND_ARC_DEG = 180.0     # spans the brow
FWDBAND_INNER_R_MM = 95.0
FWDBAND_WALL_MM = 4.0
FWDBAND_HEIGHT_MM = 30.0    # vertical strip

# Temple Plate silhouette (crude box)
TEMPLE_W_MM = 60.0          # fore-aft
TEMPLE_H_MM = 50.0          # up-down
TEMPLE_T_MM = 4.0           # plate wall

# Head envelope (anthropometric ear)
EAR_CENTER_X_MM = -10.0     # ~10 mm aft of plate datum
EAR_CENTER_Z_MM = -40.0     # ~40 mm below plate datum
EAR_DIA_MM = 65.0           # auricle bounding sphere


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def make_box(name: str, size_xyz: tuple, loc_xyz: tuple) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc_xyz)
    obj = bpy.context.active_object
    obj.scale = size_xyz
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def make_sphere(name: str, radius: float, loc_xyz: tuple) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc_xyz)
    obj = bpy.context.active_object
    obj.name = name
    return obj


def make_band_arc(name: str) -> bpy.types.Object:
    """Crude Fwd Visor-Band: a 180° arc strip oriented as if hanging
    down from the hinge in the wear-low (0°) position. Axis along +X,
    arc opens downward."""
    outer_r = FWDBAND_INNER_R_MM + FWDBAND_WALL_MM
    inner_r = FWDBAND_INNER_R_MM
    # Build cylinder along Y axis (ear-to-ear), wrapping the brow
    bpy.ops.mesh.primitive_cylinder_add(
        radius=outer_r, depth=FWDBAND_HEIGHT_MM, vertices=96,
    )
    outer = bpy.context.active_object
    outer.name = f"{name}_outer"
    outer.rotation_euler = (math.pi / 2, 0, 0)  # axis → Y
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=inner_r, depth=FWDBAND_HEIGHT_MM + 2.0, vertices=96,
    )
    inner = bpy.context.active_object
    inner.name = f"{name}_inner"
    inner.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    mod = outer.modifiers.new(name="annulus", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = inner
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(inner, do_unlink=True)

    # Half-cull: keep only the forward-and-down hemisphere (X > -outer_r/4)
    cull = make_box(
        f"{name}_cull",
        size_xyz=(2 * outer_r + 20.0, 2 * outer_r + 20.0, outer_r + 20.0),
        loc_xyz=(0, 0, (outer_r + 20.0) / 2),  # cull the UPPER half
    )
    mod = outer.modifiers.new(name="halfcull", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cull
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cull, do_unlink=True)

    outer.name = name
    return outer


def duplicate_obj(src: bpy.types.Object, new_name: str) -> bpy.types.Object:
    new_mesh = src.data.copy()
    new_obj = bpy.data.objects.new(new_name, new_mesh)
    bpy.context.collection.objects.link(new_obj)
    return new_obj


def pose_band_at_detent(band: bpy.types.Object, detent_deg: float) -> None:
    """Translate band so hinge sits at axis, then rotate about hinge axis.

    Hinge axis is along Y (ear-to-ear) at world point
    (HINGE_AXIS_X_MM, 0, HINGE_AXIS_Z_MM).
    """
    # Move pivot to origin (band was built centered on world origin with
    # its inner radius wrapping around the head; the hinge tab lives at
    # the top of the arc at world (0, 0, FWDBAND_INNER_R_MM + WALL/2)
    # in the as-built pose). Simpler model: assume band's hinge axis
    # coincides with the band's local +Z apex, then translate apex →
    # (HINGE_AXIS_X, 0, HINGE_AXIS_Z).
    # Apply: rotation about Y axis (in world frame) about the hinge point.
    band.location = (HINGE_AXIS_X_MM, 0, HINGE_AXIS_Z_MM)
    band.rotation_euler = (0, math.radians(-detent_deg), 0)
    bpy.context.view_layer.update()


def export_all(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=str(out_path), export_selected_objects=True)
    else:
        bpy.ops.export_mesh.stl(filepath=str(out_path), use_selection=True)
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)

    reset_scene()

    # L + R Temple Plate silhouettes (boxes)
    for side, y in (("L", +TEMPLE_PLATE_Y_MM), ("R", -TEMPLE_PLATE_Y_MM)):
        make_box(
            f"temple_plate_{side}",
            size_xyz=(TEMPLE_W_MM, TEMPLE_T_MM, TEMPLE_H_MM),
            loc_xyz=(0, y, 0),
        )

    # Head + ear envelope (anthropometric proxy)
    make_sphere("head_envelope", radius=58.0 * 10 / (2 * math.pi),  # ~92 mm dia
                loc_xyz=(0, 0, 0))
    for side, y in (("L", +TEMPLE_PLATE_Y_MM - 5.0),
                    ("R", -TEMPLE_PLATE_Y_MM + 5.0)):
        make_sphere(f"ear_{side}", radius=EAR_DIA_MM / 2,
                    loc_xyz=(EAR_CENTER_X_MM, y, EAR_CENTER_Z_MM))

    # Build ONE canonical band, then duplicate + pose at each detent
    template = make_band_arc("fwdband_template")
    template.hide_viewport = True
    template.hide_render = True
    # remove template from selection by renaming and unlinking later
    # (we keep it in scene but hidden — it won't export)

    for deg in DETENT_ANGLES_DEG:
        dup = duplicate_obj(template, f"fwdband_pose_{int(deg):02d}deg")
        pose_band_at_detent(dup, deg)

    # Remove template (so it's not in the STL)
    bpy.data.objects.remove(template, do_unlink=True)

    export_all(args.out)
    print(f"  visor swing envelope: {len(DETENT_ANGLES_DEG)} detents "
          f"({', '.join(f'{int(d)}°' for d in DETENT_ANGLES_DEG)})")
    print(f"  hinge axis: local ({HINGE_AXIS_X_MM:+.1f}, 0, {HINGE_AXIS_Z_MM:+.1f}) mm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
