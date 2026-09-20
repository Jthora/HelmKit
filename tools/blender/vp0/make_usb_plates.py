#!/usr/bin/env -S blender --background --python
"""
make_usb_plates.py -- the two small-parts plates for the USB folder (Track P, roster A10): tiny parts printed
together so every layer has time to cool. Lays the listed STLs out in a grid with 8 mm gaps and exports one STL
per plate into the generated set, keeping each part's print orientation.
Run:  blender --background --python tools/blender/vp0/make_usb_plates.py
"""
import bpy, os, sys
from pathlib import Path
GEN = Path(__file__).resolve().parents[3] / "3D-Models/HelmKit/_generated/vp0"
PLATES = {
    "silver_small_parts": [("knob_clip", 2), ("visor_slider", 2), ("cover_side", 2)],
    "black_small_parts":  [("bar_pin", 2), ("button_cap_s", 2), ("button_cap_l", 1), ("port_plug", 2), ("port_plug_flush", 4), ("port_coupler", 2)],
}
GAP, ROW_W = 8.0, 170.0
for plate, items in PLATES.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = []
    for name, n in items:
        for _ in range(n):
            bpy.ops.wm.stl_import(filepath=str(GEN / f"{name}.stl"))
            ob = bpy.context.selected_objects[0]; ob.name = name
            objs.append(ob)
    x = y = 0.0; row_h = 0.0
    for ob in objs:
        xs = [v.co.x for v in ob.data.vertices]; ys = [v.co.y for v in ob.data.vertices]; zs = [v.co.z for v in ob.data.vertices]
        w, d = max(xs) - min(xs), max(ys) - min(ys)
        if x + w > ROW_W and x > 0:
            x = 0.0; y += row_h + GAP; row_h = 0.0
        ob.location = (x - min(xs), y - min(ys), -min(zs))
        x += w + GAP; row_h = max(row_h, d)
    for ob in objs: ob.select_set(True)
    bpy.ops.object.transform_apply(location=True)
    bpy.ops.object.join()
    ob = bpy.context.active_object; ob.name = plate
    bpy.ops.wm.stl_export(filepath=str(GEN / f"{plate}.stl"), export_selected_objects=True, ascii_format=False)
    with open(GEN / f"{plate}.txt", "w") as fh:
        fh.write(f"{plate}.stl\n  one plate of small parts, print orientation kept: " + ", ".join(f"{n} x{q}" for n, q in items) + "\n  brim; small parts together so each layer cools (roster A10)\n")
    print("plate", plate, "objects", len(objs), "extent", round(x, 1), round(y + row_h, 1))
