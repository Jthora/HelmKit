# HelmKit vp0.4 — visual prototype part set

- **Status**: `v0.4` generated 2026-09-04, **not yet printed**. Clean-slate set; consumes nothing from Mk0.5-β.
- **Lineage**: v0.1 headphone pivots → v0.2 brain-core pods, port standard, ratchet → v0.3 flush sockets, no pivots, fillets → **v0.4 reinforcement pass for a PLA prototype that gets hit**: dome-out shells with no cavity, nail pins in double shear, rope-and-epoxy spines, collar wraps, rope nape with a clam cleat.
- **Generators**: [`tools/blender/vp0/`](../../tools/blender/vp0/README.md). Canon: [`canon.py`](../../tools/blender/vp0/canon.py).
- **Hand-editable assembly**: [`3D-Models/HelmKit_vp0/vp0_assembly.blend`](../../3D-Models/HelmKit_vp0/vp0_assembly.blend).
- **Reports** (from `assemble_vp0.py`): `3D-Models/HelmKit/_generated/vp0/renders/{clearance,mass,collisions,snag}.txt`.
- **Print target**: QIDI X-MAX3. PLA for the fit prototype, PA12-CF or PC for the hit-rated build.

## 1. Wearer inputs and fixed physics

| Input | Value | Note |
|---|---|---|
| Head width, straight, above the ears | 155 mm | |
| Head length, glabella to back | 202.5 mm | |
| Circumference | 58 cm | phantom plan exponent 2.45 |
| Brain core | 10 mm forward, 35 mm above the ear canals | pod axis passes through it |
| Disk diameter | **122.1 mm, physics, do not change** | wavelength-linked |

The phantom is a superellipsoid with no cheekbones, brow ridge or ears. Foam thickness absorbs the difference.

## 2. Architecture (v0.4)

**Pods** are the shield/projector elements themselves: a 3 mm paraboloid shell, concave toward the head, dome outside, on a 16 mm rim ring. No cavity, no electronics. Five flush 10 mm sockets sit in the ring, hidden under the foam ear ring. Ear room at the centre is 38 mm.

**Port standard.** Every socket is 10.3 mm square, 12 deep. The joint is locked by a **nail through both socket walls and the coupler**, in double shear, head in a counterbore and epoxied. Couplers are 10 × 10 × 1 mm aluminium square tube cut to length and drilled with the printed guide, or printed PLA posts. To collapse the helm, drive out six nails and pull six couplers.

| Port | Use | Coupler |
|---|---|---|
| 13° front | brow strut into the wing socket | ~35 mm |
| 90° top | crown arch foot | 23 mm |
| 135° rear-upper | spare (pylons) | cover |
| 206° rear | rear band block | 28 mm |
| 300° front-lower | strap anchor, chin strap | direct |

**Crown arch**: two identical chamfered 30 × 6 halves, feet with a concave rim seat, overlap bars with ridges in the apex sleeve, M4 clamp for ±13 mm of span, foam pad under the sleeve. A 3.9 × 2.8 groove along the head-side face takes epoxy-soaked rope.

**Brow panel**: 100 mm flat centre with 54 mm wings swept back 20°, leaning 13°. LED window in the bottom face, lid with a 12 mm foam pad on the head side, pinned sockets in the wing ends, collar grooves for thread wraps.

**Rear bands**: two identical 30 × 6 chamfered halves in a plane tilted 26°, from a pinned socket block at the pod, hugging the occiput over a foam strip, with a rope spine groove, ending in a rope eye beside the nape.

**Nape**: a 74 × 36 × 6 plate with a foam pad and a **printed clam cleat** (no moving parts). Rope: knot at the right eye, through the plate channel, through the left eye, back into the cleat. Pull the tail to tighten; lift it out of the V to release. Nothing rigid protrudes more than 11 mm.

**Retention**: crown pad and ear rings carry weight, the rear bands bite under the inion, strap anchors take a chin strap of rope or webbing.

## 3. Reinforcement recipe

| Where | What to do | Why |
|---|---|---|
| every socket | drive a nail through the counterbore, coupler and far wall; clip flush; dab the head with epoxy | pull-out goes from one threaded screw to a steel pin in double shear |
| every socket block | wind thread or twine soaked in epoxy into the collar groove, 5 to 6 turns | resists the splitting mode of a square socket |
| crown arch, rear bands | lay rope soaked in epoxy into the spine groove on the head-side face, press flush, wipe | a cracked band still carries the rope's tensile load |
| pod rim ring | optional: thread wrap around the ring's outer face between sockets | hoop against splitting |
| sockets, hit-rated build | set `CAST_SOCKETS = True`, print sockets 1 mm oversize, cast metal epoxy around the taped socket form | socket walls become epoxy instead of PLA across layers |
| dish surfaces | plain epoxy only, no metal-filled epoxy, nails or wire on or near the shell | keep conductors off the projector element |

## 4. Printed parts

| # | Part | Qty | Orientation | Supports |
|---|---|---|---|---|
| 0 | `fit_coupon.stl` | 1 | flat | no. **Print first**: nail fit, socket fit, cleat jam, groove sizes |
| 1 | `pod_shell.stl` | 2 | dome up | yes, under the shell, or on edge with a brim for none |
| 2 | `crown_arch_half.stl` | 2 | flat, ridged face up | no, brim |
| 3 | `apex_block.stl` | 1 | on end | no |
| 4 | `brow_panel.stl` | 1 | standing on the bottom face | no, brim |
| 5 | `brow_lid.stl` | 1 | flat | no |
| 6 | `rear_band_half.stl` | 2 | top edge down | no |
| 7 | `nape_plate.stl` | 1 | cleat up | no |
| 8 | `port_coupler_crown/rear/brow.stl` | 2 each | flat | no, or aluminium tube |
| 9 | `coupler_drill_guide.stl`, `socket_form.stl` | 1 each | flat | no |
| 10 | `strap_anchor.stl`, `port_cover.stl` | 2 each | see sidecars | no |
| 11 | `port_plug_blank.stl` | as needed | on side | no |

Slicer: 0.2 mm layers (0.12 for the dome), 3 walls, 20 % gyroid; PLA 210/60 °C. Bands and arch carry loads along their layers.

## 5. Non-printed BOM

| Item | Qty |
|---|---|
| nails, ~3 mm shank, 40 to 50 mm | 12 (six joints, one per socket end, plus spares) |
| 10 × 10 × 1 aluminium square tube, 23 / 28 / ~35 mm | 2 each, optional |
| M4 × 50 + nut (apex) | 1 |
| M3 × 8 thread-forming (brow lid) | 4 |
| rope 3 to 4 mm: nape 40 cm, chin strap 60 cm, spines 2 × 40 cm | ~2 m |
| thread or twine + epoxy for collars | |
| foam: ear rings OD 122 / ID 88 / 15; crown 40 × 60 × 12; brow 96 × 44 × 12; nape 74 × 36 × 10; rear strips 50 × 30 × 12 | 2 / 1 / 1 / 1 / 2 |

## 6. Print and validation order

1. Fit coupon. A nail must press into the 3.2 mm holes with light taps without splitting the block; the plug must slide into the socket and pin; rope must jam in the cleat when pulled from the narrow end and lift out; the spine groove must take your rope.
2. One pod shell. Check all five sockets with the coupon plug, then glue the foam ring.
3. Crown halves, apex, couplers. Pin the arch to both pods, set the span, epoxy the spines.
4. Brow panel, lid, brow couplers. Pin, then wrap the wing collars.
5. Rear bands, nape plate, rear couplers, rope. Pin, epoxy spines, rig the nape rope.
6. Second pod. Foam. Wear it, run, then decide which joints get cast sockets.

## 7. Known limitations

- Phantom head has no cheekbones or brow ridge.
- The clam cleat is untested in PLA: if the rope slips, deepen the teeth (`CLEAT.tooth_h`) or narrow the V (`bot_w`).
- Nail diameter is assumed 3.0 mm (`PIN_DIA` 3.2). Measure yours; the coupon tells you.
- The dome prints with supports on the concave face, hidden under the foam; on-edge printing avoids supports but is a tall, narrow print.
- PLA softens around 55 °C: do not leave it in a car. Epoxy spines and cast sockets help it keep shape.
- Nothing has been drop-tested. Capacities in the review are hand calculations.
