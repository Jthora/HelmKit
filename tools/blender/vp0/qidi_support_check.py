#!/usr/bin/env python3
"""
qidi_support_check.py -- QIDI Studio's "It seems object X has floating cantilever" check, reproduced from its source
(QIDITECH/QIDIStudio master: TreeSupport::detect_overhangs, PrintObject::is_support_necessary), Track P 2026-09-25.

Per layer, on outlines opened by the line width (features narrower than 0.42 mm are dropped): overhang = the layer minus
the layer below grown by layer_height / tan(31 deg). An overhang cluster is a cantilever when one of its contours (the
outer one or a hole's) lies entirely more than a line width from the layer below, or when a point of its outline is more
than 3 mm from where it rests. The slicer warns when the largest such distance exceeds 6 mm. Floating regions (the other
warning) are layer_islands.py. Three guesses at this rule passed parts the slicer rejected; this is the rule itself.

Run:  blender --background --python tools/blender/vp0/slice_layers.py -- part.stl /tmp/part.json
      python3 tools/blender/vp0/qidi_support_check.py /tmp/part.json [z_from z_to]    (needs numpy, scipy, Pillow)
A 176 x 200 mm part takes ~20 min at the 0.05 mm raster the 0.42 mm line width needs; pass a z range to check a band.
"""
import json, sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
L = json.load(open(sys.argv[1])); RES = 0.05
if len(sys.argv) > 3: L = [l for l in L if float(sys.argv[2]) - 0.25 <= l['z'] <= float(sys.argv[3])]
W_LINE, ANG = 0.42, 31.0
LH = L[0].get("lh", 0.2) if L else 0.2              # the layer height the part was sliced at (slice_layers --layer)
OFF = LH / np.tan(np.radians(ANG))
for l in L:                                  # older dumps: one shell
    l.setdefault("shells", [l.get("loops", [])])
xs = [p[0] for l in L for sh in l["shells"] for lp in sh for p in lp]; ys = [p[1] for l in L for sh in l["shells"] for lp in sh for p in lp]
x0, y0 = min(xs) - 3, min(ys) - 3; W = int((max(xs) - x0 + 3) / RES); H = int((max(ys) - y0 + 3) / RES)
def mask(shells):
    u = np.zeros((H, W), bool)
    for loops in shells:
        u |= mask1(loops)
    return u
def mask1(loops):
    m = np.zeros((H, W), bool)
    for lp in loops:
        im = Image.new("1", (W, H), 0); ImageDraw.Draw(im).polygon([((x - x0) / RES, (y - y0) / RES) for x, y in lp], fill=1)
        m ^= np.array(im, bool)
    return m
edt = lambda m: ndimage.distance_transform_edt(m) * RES
def extrudable(m):                         # lslices ∩ offset2(lslices, -w/2, +w)
    er = edt(m) > W_LINE / 2
    return m & (edt(~er) <= W_LINE) if er.any() else np.zeros_like(m)
prev = None; worst = []; tails = []
for l in L:
    cur = extrudable(mask(l["shells"]))
    if prev is not None:
        dlow = edt(~prev)                                    # distance to the lower layer's material
        # "floating regions" (sharp tail): a region of this layer with nothing within 0.1 line width below it
        lab_c, nc = ndimage.label(cur)
        for k, sl in enumerate(ndimage.find_objects(lab_c), start=1):
            reg = lab_c[sl] == k
            if not (reg & (dlow[sl] <= 0.1 * W_LINE)).any():
                yy, xx = np.nonzero(reg)
                tails.append((l["z"], reg.sum() * RES * RES, x0 + (xx.mean() + sl[1].start) * RES, y0 + (yy.mean() + sl[0].start) * RES))
        over = cur & (dlow > OFF)
        lab, n = ndimage.label(over)
        for k, sl in enumerate(ndimage.find_objects(lab), start=1):
            m = 140
            ys_ = slice(max(sl[0].start - m, 0), min(sl[0].stop + m, H)); xs_ = slice(max(sl[1].start - m, 0), min(sl[1].stop + m, W))
            comp = lab[ys_, xs_] == k; dl = dlow[ys_, xs_]
            thresh = dl <= W_LINE                              # lower_layer_support_thresh
            bg, nb = ndimage.label(~comp)
            border = set(np.unique(np.r_[bg[0], bg[-1], bg[:, 0], bg[:, -1]])) - {0}
            dist, why = 0.0, ""
            for b in range(1, nb + 1):                         # every contour: the outer one and each hole's
                ring = comp & ndimage.binary_dilation(bg == b)
                if not ring.any(): continue
                if not (ring & thresh).any():                  # a totally floating contour
                    d = dl[ring].max() - W_LINE
                    if d > dist: dist, why = d, ("floating outer contour" if b in border else "floating HOLE contour")
            if not why:
                base = comp & (dl <= W_LINE + 0.1)
                if base.any():
                    outer = comp & ndimage.binary_dilation(np.isin(bg, list(border)))
                    d = edt(~base)[outer].max()
                    if d > 3.0: dist, why = d, "outline > 3 mm from base"
            if why:
                yy, xx = np.nonzero(comp)
                worst.append((dist, l["z"], why, comp.sum() * RES * RES, x0 + (xx.mean() + xs_.start) * RES, y0 + (yy.mean() + ys_.start) * RES, (xx.max() - xx.min()) * RES, (yy.max() - yy.min()) * RES))
    prev = cur
print(f"QIDI floating regions (sharp tails): {len(tails)}" + (" -> WARNS" if tails else " -> no warning"))
for z, a, cx, cy in tails[:10]:
    print(f"   z {z:6.2f}  area {a:6.2f} mm2 at ({cx:7.1f},{cy:7.1f})")
worst.sort(reverse=True)
mx = worst[0][0] if worst else 0.0
print(f"QIDI cantilever clusters: {len(worst)}; max_cantilever_dist {mx:.2f} mm -> {'WARNS (> 6 mm)' if mx > 6 else 'no warning'}")
for d, z, why, a, cx, cy, w, h in worst[:12]:
    print(f"   {d:6.2f} mm  z {z:6.2f}  {why:26s} area {a:7.2f} mm2 at ({cx:7.1f},{cy:7.1f}) extent {w:5.1f} x {h:5.1f}")
