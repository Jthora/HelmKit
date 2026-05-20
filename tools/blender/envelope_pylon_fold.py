#!/usr/bin/env -S blender --background --python
"""
envelope_pylon_fold.py — Phase-3 collision-check geometry.

Sweeps a Pylon (flat 60 mm × 6 mm × 4 mm prism) through 3 detent
positions about the TPU live-hinge axis on the Temple Plate, plus
the head/ear envelope and opposing Temple Plate. Mirrors L + R.
Purpose: confirm IFACE_TEMPLE_PYLON fold-flat envelope ≤ 75 mm aft
× ≤ 15 mm proud, and no L↔R Pylon collision when both folded.

Throwaway primitives. No printable detail.

Run:
    /Applications/Blender.app/Contents/MacOS/Blender --background \\
        --python tools/blender/envelope_pylon_fold.py -- \\
        --out 3D-Models/HelmKit/_envelopes/pylon_fold.stl

Source-of-truth: docs/mechanical/mk0.5_topology_beta_architecture.md
§12 IFACE_TEMPLE_PYLON.
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
# Canon (§12 IFACE_TEMPLE_PYLON)
# ---------------------------------------------------------------------------

# Hinge axis on Temple Plate (local mm): horizontal fore-aft (axis = X),
# at local (−5, +10, +4).
HINGE_AXIS_X_MM = -5.0      # 5 mm aft of plate datum
HINGE_AXIS_Y_PROUD_MM = 10.0  # 10 mm outboard from plate face (along ±Y per side)
HINGE_AXIS_Z_MM = 4.0       # 4 mm above plate datum

TEMPLE_PLATE_Y_MM = 78.0    # ear-to-ear half-width

# Pylon physical envelope: 60 mm long × 6 mm wide × 4 mm thick prism.
PYLON_LEN_MM = 60.0
PYLON_WIDTH_MM = 6.0
PYLON_THICK_MM = 4.0

# Pylon's local origin (its hinge end) sits AT the hinge axis.
# In deploy (0°) pose: Pylon extends straight UP from hinge (+Z).
# Detents (rotation about hinge X-axis, +=> aft):
#   0° = deploy / straight up
#   45° = mid-fold
#   90° = fold-flat (lies aft, alongside head past ear)
DETENT_ANGLES_DEG = (0.0, 45.0, 90.0)

# Anthropometric
HEAD_DIA_MM = 58.0 * 10 / math.pi  # crude — circumference / π
EAR_CENTER_X_MM = -10.0
EAR_CENTER_Z_MM = -40.0
EAR_DIA_MM = 65.0

# Temple Plate silhouette
TEMPLE_W_MM = 60.0
TEMPLE_H_MM = 50.0
TEMPLE_T_MM = 4.0

# Fold-flat envelope spec to draw as a wireframe-style bound:
FOLD_FLAT_MAX_AFT_MM = 75.0
FOLD_FLAT_MAX_PROUD_MM = 15.0


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


def make_pylon(name: str, y_side_sign: int) -> bpy.types.Object:
    """Build a Pylon prism, hinge end AT origin, body extending +Z.

    `y_side_sign` = +1 for L (outboard = +Y), -1 for R.
    Pylon thickness extends in ±Y from the hinge plane.
    """
    # Cube centered: shift so bottom face at z=0, body extending up
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.scale = (PYLON_WIDTH_MM, PYLON_THICK_MM, PYLON_LEN_MM)
    obj.location = (0, 0, PYLON_LEN_MM / 2)  # bottom at hinge plane
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    obj.name = name
    return obj


def pose_pylon_at_detent(pylon: bpy.types.Object, detent_deg: float,
                         y_side: float) -> None:
    """Rotate Pylon about hinge X-axis (rotation aft = +deg), then
    translate hinge to world hinge point on Temple Plate side `y_side`.
    """
    pylon.location = (HINGE_AXIS_X_MM,
                      y_side + math.copysign(HINGE_AXIS_Y_PROUD_MM, y_side),
                      HINGE_AXIS_Z_MM)
    # +detent = fold aft → rotation about +X axis in the −Z→−X direction
    pylon.rotation_euler = (math.radians(detent_deg), 0, 0)
    bpy.context.view_layer.update()


def export_all(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
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
    args = p.parse_args(argv)

    reset_scene()

    # L + R Temple Plate silhouettes
    for side, y in (("L", +TEMPLE_PLATE_Y_MM), ("R", -TEMPLE_PLATE_Y_MM)):
        make_box(
            f"temple_plate_{side}",
            size_xyz=(TEMPLE_W_MM, TEMPLE_T_MM, TEMPLE_H_MM),
            loc_xyz=(0, y, 0),
        )

    # Head + ears
    make_sphere("head_envelope", radius=HEAD_DIA_MM / 2, loc_xyz=(0, 0, 0))
    for side, y in (("L", +TEMPLE_PLATE_Y_MM - 5.0),
                    ("R", -TEMPLE_PLATE_Y_MM + 5.0)):
        make_sphere(f"ear_{side}", radius=EAR_DIA_MM / 2,
                    loc_xyz=(EAR_CENTER_X_MM, y, EAR_CENTER_Z_MM))

    # Fold-flat envelope wireframe (visual bound)
    for side, y in (("L", +TEMPLE_PLATE_Y_MM + HINGE_AXIS_Y_PROUD_MM),
                    ("R", -TEMPLE_PLATE_Y_MM - HINGE_AXIS_Y_PROUD_MM)):
        # Bounding box centered at: from hinge aft FOLD_FLAT_MAX_AFT_MM,
        # ±FOLD_FLAT_MAX_PROUD_MM from hinge in Y, height PYLON_THICK
        cx = HINGE_AXIS_X_MM - FOLD_FLAT_MAX_AFT_MM / 2
        make_box(
            f"foldflat_bound_{side}",
            size_xyz=(FOLD_FLAT_MAX_AFT_MM, 2 * FOLD_FLAT_MAX_PROUD_MM, PYLON_THICK_MM),
            loc_xyz=(cx, y, HINGE_AXIS_Z_MM),
        )

    # Pylons posed at each detent, both sides
    for side_name, y_side in (("L", +TEMPLE_PLATE_Y_MM), ("R", -TEMPLE_PLATE_Y_MM)):
        for deg in DETENT_ANGLES_DEG:
            name = f"pylon_{side_name}_{int(deg):02d}deg"
            obj = make_pylon(name, y_side_sign=1 if y_side > 0 else -1)
            pose_pylon_at_detent(obj, deg, y_side)

    export_all(args.out)
    print(f"  pylon fold envelope: {len(DETENT_ANGLES_DEG)} detents per side "
          f"({', '.join(f'{int(d)}°' for d in DETENT_ANGLES_DEG)})")
    print(f"  hinge axis: local ({HINGE_AXIS_X_MM:+.1f}, ±{HINGE_AXIS_Y_PROUD_MM:.1f}, "
          f"{HINGE_AXIS_Z_MM:+.1f}) mm")
    print(f"  fold-flat spec: ≤{FOLD_FLAT_MAX_AFT_MM:.0f} mm aft × "
          f"≤{FOLD_FLAT_MAX_PROUD_MM:.0f} mm proud")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
