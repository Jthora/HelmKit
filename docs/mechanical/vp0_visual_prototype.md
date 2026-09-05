# HelmKit vp0.9 — visual prototype part set

- **Status**: `v0.9` generated 2026-09-05, **not yet printed**. Clean-slate set; consumes nothing from Mk0.5-β.
- **Lineage**: v0.1 headphone pivots → v0.2 brain-core pods, port standard, ratchet → v0.3 flush sockets, no pivots, fillets → v0.4 reinforcement pass → v0.5 protected knob, integral brow spars → v0.6 cradle architecture, floating pods on brackets, pull dial → v0.7 centre-mounted enclosed disks, everything on the cradle, cylinder ports, rail visor, pylons → v0.8 the Nexus (one hub per side on the disk axis: disk, visor pivot, add-on ports) → **v0.9 robustness + lean pass: no loose pins (captive index nails, screw-and-knob disk lock), no spare ports, fixed visor reach on bolted tabs, crown arch back on the hub-node sockets, print-one nape pin-lock instead of the dial, PETG nexus.**
- **Generators**: [`tools/blender/vp0/`](../../tools/blender/vp0/README.md). Canon: [`canon.py`](../../tools/blender/vp0/canon.py).
- **Hand-editable assembly**: [`3D-Models/HelmKit_vp0/vp0_assembly.blend`](../../3D-Models/HelmKit_vp0/vp0_assembly.blend).
- **Reports** (from `assemble_vp0.py`): `3D-Models/HelmKit/_generated/vp0/renders/{clearance,mass,collisions,snag}.txt`; print-orientation audit: `print_check.py`.
- **Print target**: QIDI X-MAX3. Cradle and nexus in PETG, everything else PLA for the fit prototype; PA12-CF or PC for the hit-rated build.

## 1. Wearer inputs and fixed physics

| Input | Value | Note |
|---|---|---|
| Head width, straight, above the ears | 155 mm | |
| Head length, glabella to back | 202.5 mm | |
| Circumference | 58 cm | phantom plan exponent 2.45 |
| Brain core | 10 mm forward, 35 mm above the ear canals | disk axis passes through it |
| Disk diameter | **122.1 mm, physics, do not change** | wavelength-linked |
| Coil apparatus cavity | Ø110 × 12 mm, **assumed** | change `DISK_CAVITY` once the coil exists; the lock boss intrudes 4 mm at one spot (r 50.5..55, 240°) |

The phantom is a superellipsoid with no cheekbones, brow ridge or ears. Foam thickness absorbs the difference.

## 2. Architecture (v0.9)

The **cradle** holds the head. On each side a **Nexus** sits on the disk axis between the cradle's hub node and the disk: it mounts the disk and carries the visor pivot. The **disks** are sealed lenses hung at their centre. Nothing else touches the disks. Every adjustable joint is held by a captive pin or a screw, never by friction, and nothing that comes out of the helm is a loose part.

**Cradle.** A 30 × 5 mm PETG band on the hat line (z 40..70, above the ears): one U print for the forehead and sides with two solid nodes per side and a 3 mm doubler on the outer face for 30 mm either side of the hub node (a disk hit puts about 6 N·m into that node; the doubler takes the band from 48 to 24 MPa), plus two tilted rear halves that meet in the nape module. 10 mm foam blocks velcro to the inside (forehead, sides; 6 mm under the nodes); the crown pad sits under the arch apex. Cables run on the inside of the band under the foam. Strap slot pairs behind the hub nodes and on the rear halves take a Y chin strap if the shake test asks for one.

| Node | x | Carries |
|---|---|---|
| hub | −3..23, on the disk axis | three M3 × 30 through-holes for the Nexus (heads under the foam); a 16 mm pin lug on its outer face above the visor ring, bolted through along x by the pin keeper; 8.3 socket from the top (crown arch coupler) |
| rear | −58..−32, hangs 18 below the band | tapered tenon socket for the rear half (nail); 8.3 socket from the top (antenna pylon) |

**Cylinder port standard.** 8 mm peg, 8.3 mm socket, 15 mm deep, M3 cross-bolt (or a nail) at 7 mm from the mouth. Used at four places: two arch couplers, two pylon pegs. Printed pegs take a nail down their core with epoxy; 8 mm aluminium rod drilled with the guide is the hit-rated option. Spares: double-male coupler, drill guide. No unused sockets, so no plugs.

**Nexus (PETG).** Inboard to outboard on the disk axis: the hub node's outer face (y 100); a Ø44 × 1 **spool** flange with a Ø32 × 5.5 hub, the visor ring's bearing; the **visor ring** (Ø44, 4.5 thick, the root of each brow rail) with 24 radial Ø3.4 index holes; a wave washer; the **flange**, Ø60 × 8, bolted through the node with three M3 × 30 that also clamp the spool, carrying the Ø20 bayonet stalk, a full-thickness **lock ear** down-back at 240° to r 58 with the lock-screw hole at r 54, and a Ø4 lanyard hole (cord to a strap slot: a disk that comes off in a fall stays with the helm). No flat ports any more: the arch went back to the hub-node socket and the mic is gone. One STL serves both sides.

**Captive index pin.** A 3.2 × 40 nail drops through a **pin keeper** (a U-saddle over the hub node's lug, one M3 × 25 through the lug along x) into the lug and one of the ring's 24 holes. A small spring between the keeper bar and a printed C-collar glued on the nail pushes it home; pull the head 6 mm to tilt the visor. Nothing to drop in the forest.

**Disks.** A 2.5 mm paraboloid dome shell (outside) on a 3 mm rim wall with six screw bosses, closed by a 2 mm back plate on six M3. The back plate **seats on the nexus flange and ear faces**, so a rim hit reacts over a 22 mm lever instead of the bore. The plate's cavity side carries the **bayonet** (Ø20.6 bore with two entry notches, a 3.2 mm groove the 3 mm lugs turn 90° into, a stop wall; no detent bump) and a 7 × 10 × 6 **lock boss** at 240°, tapped through boss and plate: an M3 × 20 with a printed knob on its head comes from the head side through the 8 mm ear into it. Quarter turn to the stop, screw in: the disk cannot rotate or lift. Nothing protrudes from the plate's head face, so it prints flat. No metal on the disk axis; the coil feed exits through a Ø6 hole beside the stalk and runs under the foam. The stalk is the fuse: a 100 N rim hit puts about 6 N·m on it, under 10 MPa.

- **Crown arch**: two identical chamfered 20 × 7 halves ending in a foot block with an 8.3 socket over the hub node's socket; a 30 mm double-male coupler (M3 cross-bolt each end) joins them. Straight up 20 mm then the superellipse to the overlap bar in the apex sleeve (ridges, M4 clamp, ±13 mm of span). Two cross-bolts out and it lifts off. No spine groove (the rope spine goes back on if a PLA arch cracks).
- **Brow**: 160 × 50 × 15 centre panel (LED bay 128 wide, rounded top bead) on two **rails** (7 × 20, tip at 128 mm from the axis, flush with the panel front) whose roots are the visor rings on the nexus spools: the visor pivots about the disk centre. Tilt in 15° steps with the captive pin; one step down puts the panel at eye level, 60° up parks it over the crown in front of the arch. Reach is **fixed**: an L-shaped **tab** on each panel end (two M3 × 10 into the end face) reaches out to the rail's inner face and takes two M3 × 12 through the rail. To change the reach, print tabs with a different arm (one number in `build_brow_tab.py`).
- **Antenna pylons**: 8 mm peg base in each rear node socket with a clevis; a faceted 140 mm blade (6 mm serrated root tongue, flares to 28 × 14, tapers to 12 × 6; hollow with 2.4 mm walls, Ø4 wire bore) on an M3 hinge with a wave washer and a Ø24 printed knob: 15° notches, hand-locked, folds back along the rear half. Deployed 30° back from vertical.
- **Nape, print one: the pin-lock.** A 52 × 44 × 10.6 block with two rack tunnels (each open at its own end) and two vertical Ø2.2 holes on the mid-plane. Both rear-half racks slide through; a 2 mm nail dropped through the top wall passes both racks' tooth spaces and the web between them and the racks cannot move. The racks are phased so their spaces line up over the u = 0 hole at whole-pitch settings and over the u = p/2 hole at half-pitch ones: 3.9 mm steps of circumference, ±14 mm of range. Thread lanyard keeps the nail. The enclosed **pull dial** (52 × 44 × 26.5: body with ratchet ring, cover, lid, dial, key cap, pinion, retainer with an M5 nut pocket) stays in the generator as the second module (`NAPE_MODULE = "dial"`) for when one-handed adjustment matters.

Overall width at the domes: 282 mm. Disk back face 37 mm off the skull.

## 3. Load path notes (hand calculations)

| Load | Path | Margin |
|---|---|---|
| 100 N hit on a disk rim | back plate → flange + ear faces → three M3 × 30 → hub node + doubler | band 24 MPa; stalk under 10 MPa |
| 40 N sideways on the visor | rail → ring → spool hub → node; index nail in double shear | rail root is the fuse (~40 N); nail good for over 20 N·m |
| pylon side hit | blade → serrated hinge → peg → rear node | 8 mm PLA peg fuses at ~2 N·m: nail its core or use aluminium rod |
| band tension at the nape | rack teeth → 2 mm nail in double shear → other rack | ~600 N nail; tooth flank ~4 MPa at 100 N |
| disk lock | M3 × 20 through 8 mm ear into a 6 mm tapped boss | screw in single shear; prevents rotation and lift |

## 4. Printed parts (print-one set: 37 pieces + coupon + drill guide)

| # | Part | Qty | Orientation | Supports |
|---|---|---|---|---|
| 0 | `fit_coupon.stl` | 1 | flat | no. **Print first**: hole gauges, 8.3 socket + 8 peg + cross-bolt, bayonet boss + stub, ratchet click pair |
| 1 | `cradle_front.stl` (PETG) | 1 | upside down, node and lug tops on the bed | no |
| 2 | `rear_band_half.stl` (PETG) | 2 | top edge down | no |
| 3 | `disk_dome.stl` | 2 | dome up | yes, under the shell, or on edge with a brim for none |
| 4 | `disk_back.stl` | 2 | flat, boss up | no |
| 5 | `nexus.stl` (PETG), `nexus_spool.stl`, `pin_keeper.stl`, `lock_knob.stl`, `pin_collar.stl` | 2 each | flange inner face down, stalk up; spool flange down; keeper bar down; knob and collar flat | no |
| 6 | `crown_arch_half.stl`, `port_coupler.stl` | 2 each | arch on edge, ridged face up; coupler standing | no, brim on the arch |
| 7 | `apex_block.stl` | 1 | on end | no |
| 8 | `brow_center.stl` | 1 | standing on the bottom face | no, brim |
| 9 | `brow_rail_L/R.stl` (with the nexus ring), `brow_tab_L/R.stl` | 1 each | rail on its ring face; tab flange down | no |
| 10 | `brow_lid.stl` | 1 | flat | no |
| 11 | `nape_pinlock.stl` | 1 | either face down | no (6.6 × 15 mm tunnel bridges) |
| 12 | `pylon_base.stl`, `pylon_blade.stl`, `pylon_knob.stl` | 2 each | base inverted; blade on its flat face; knob flat | no |
| 13 | `port_drill_guide.stl` | 1 | see sidecar | no |
| — | `nape_body / cover / lid / dial / key / pinion / retainer.stl` | module 2 only | see sidecars | no |

Slicer: 0.2 mm layers (0.12 for the dome), 3 walls, 20 % gyroid; PLA 210/60 °C, PETG 240/80 °C for the cradle and nexus. Mass: 780 g solid, about 585 g as printed, plus ~80 g foam and hardware. CG (10, 0, 57).

## 5. Non-printed BOM (print-one set)

| Item | Qty |
|---|---|
| nails: 3.2 × 40 (index pins) 2; 3.2 × 40..50 (rear tenons) 2; 2 × 50 or 2 mm rod (nape pin-lock) 1; spares for peg cores | 5 + |
| small compression springs, ~4.5 mm ID × 12 mm free (index pins) | 2 |
| M3 × 30 + nyloc (nexus through the hub node) | 6 |
| M3 × 30 + wave washer + nyloc (pylon hinges) | 2 |
| M3 × 25 + nut (pin keepers through the lugs) | 2 |
| M3 × 20 + nut (cross-bolts: pylon pegs 2, arch couplers 4) | 6 |
| M3 × 20 (disk lock screws, printed knob glued on the head) | 2 |
| M3 × 12 + nut (rails to tabs) | 4 |
| M3 × 10 thread-forming (tabs to panel 4, disk back plates 12, brow lid 4) | 20 |
| wave washers M32 or a 0.9 mm PTFE ring (visor ring to nexus) | 2 |
| M4 × 50 + nut (apex) | 1 |
| thread or thin cord: nexus lanyards 2, nape nail lanyard 1 | |
| 15 mm webbing + buckle for the Y chin strap (only if the shake test asks) | ~1 m |
| foam 10 mm: forehead 70 × 26, sides 40 × 26 × 2; 6 mm under the nodes; crown 40 × 60 × 12; nape 48 × 40 × 10; velcro | |
| module 2 (dial) adds: M5 × 25 + M5 nut, 3/8 × 1/2 in spring, M3 × 6 ×2, M3 × 8 thread-forming ×8 | |

## 6. Print and validation order

1. Fit coupon. A 3.2 nail must press into the 3.2 hole and slip through the 3.4; a 2 mm nail through the 2.2; an M3 must self-tap into the 2.5. The 8 mm peg must slide into the socket and take the cross-bolt. The bayonet stub must drop into the boss and turn a quarter to the stop without force. The ratchet disc must click one way and lock the other.
2. Cradle U (PETG), both rear halves, pin-lock. Tenons in and nailed, racks through the block, nail in the hole whose spaces line up. Foam on, wear the cradle alone: it must sit above the ears and stay put when you shake your head. This is the chin-strap decision.
3. Both nexus sets (flange, spool, keeper, collar, knob, rail rings on the rails) and one disk (dome + back). Bolt the nexus through the node with the spool and ring in the stack, fit the keeper and the sprung nail, bayonet the disk on, lock screw in, check the ear clearance. Measure the coil apparatus against the cavity before printing the second disk.
4. Brow centre, tabs, lid. Tabs on the panel ends, rails bolted to the tabs. Pull the index nails, tilt, let them drop.
5. Crown halves, couplers, apex. Couplers into the hub sockets, feet on, four cross-bolts, set the span.
6. Pylons. Second disk. Wear it, run, then decide which pegs get aluminium cores and whether the dial module is worth its 16 mm.

## 7. Known limitations and open questions

- The coil cavity size is a guess, and the lock boss intrudes into its edge at one spot. So is the pylon position (rear nodes, sweeping back).
- "Extension" of the visor was built as reach (distance from the face), now fixed by the tabs. If it meant width, the tabs become side plates on the same rails.
- The visor is a 118 mm lever from the disk-axis pivot; it is held by the index nail, never by friction. Folding flat means taking the disks off (quarter turn + one screw) and unbolting the nexus (three M3) so the rails slide off, or simply parking at 60°.
- Phantom head has no cheekbones, brow ridge or ears; the nexus spool flange (Ø44 at y 100) passes ~8 mm above a typical pinna. Measure yours.
- 8.3 mm sockets print closer to 8.0 in PLA: ream with the drill guide or open `CYL_SOCKET_D` to 8.5. The back plate has no fillet.
- Print-orientation audit (2026-09-05, `print_check.py`): every STL has its bed face down; the only flagged items are the two intentionally small-footprint parts (collar, standing coupler).
- The bayonet, the pin-lock nail in module-1.25 tooth spaces and the serrated detents are untested in PLA. If the pin-lock nail rattles, go to a 2.2 nail and `hole` 2.4.
- An 8 mm PLA peg alone is the weak link for the pylons under a side hit (about 2 N·m). Put a nail down its core, or use aluminium rod.
- Remaining single points: the three M3 × 30 per nexus (a hub-node crack takes the disk and visor with it; the lanyard keeps the disk on the helm), the printed rail root (~40 N sideways), the PETG stalk.
- Next architecture steps if the fit is right: BOA-style cord tensioner at the nape, pocketed nodes and 2.2 mm dome shell for mass, heat-set inserts for the disk back and tab screws, PA12-CF for the cradle and nexus.
- Nothing has been drop-tested. Capacities are hand calculations.
