# Track P annex — fasteners and lines: pins, rope, cable, cord, strap

**Status:** planned 2026-09-20; **Phase 0 applied the same day** (canon pin sizes, strap pitch and chamfer constants, `vp0lib.slot_chamfer`, d1 v2 built and verified, calibration rows). Phases 1-4 not applied. Decisions taken with Jordan the same day after coupon H; every item
below is tied to the print step that must not start without it. Companion to
[`track-P-print-to-completion.md`](track-P-print-to-completion.md) §13 and the spec's print-process rules
([`../../mechanical/vp0_visual_prototype.md`](../../mechanical/vp0_visual_prototype.md) §6.1).

## 1. The three facts that decided the pins

1. **Sweat.** Every pin lives in it: tenon heads under the nape foam, the nape pins at the wettest point on the
   head, the index pin at the temple. Bright common nails rust; sealed or stainless or not steel.
2. **The coil.** The index pin sits ~35 mm off the disk axis and the lock pin sits *in the stalk, on the axis*,
   where canon already forbids metal. Neither carries a load that needs steel. The rope spine's metal-filled
   epoxy would put iron powder along the whole hat line: same objection, larger.
3. **Combat trim wears no disks** (`--trim combat` drops everything on the nexus), so the disk lock is about
   bumps in full trim, not blows; and anything loose on the helmet in combat trim is a projectile.

The nails on hand are 12 ga (2.68 mm) and 16 ga (1.59 mm). The design was drawn for ~3.0 and 2.0. Every hole
below is re-sized to what is in the box.

## 2. Pin decisions (final)

| spot | decision | holes / part |
|---|---|---|
| rear-half tenon ×2 | 12 ga nail cut to length, epoxied, head sealed under epoxy | `PIN_DIA` 2.9 → tenon and node teardrops 3.1 (slip; the epoxy is the joint); `PIN_HEAD_DIA` 7.0 |
| peg cores | none for print one | add only if a pylon snaps at the peg |
| socket cross-pins ×4 | M3 bolt + nut, as designed | unchanged |
| combat plug retainer ×4 | M3 × 8 thread-forming, captive; a lever slot in the cap | plug cross hole 3.4 → 2.5; the socket block's 3.4 stays (it passes the bolt in full trim) |
| nape pin-lock ×2 | 16 ga nails now; then a U-pin bent from 1.6 mm stainless rod on a printed jig | `NAPE_PINLOCK_PIN` dia 1.6, hole 1.8, bottom 1.7; the two counterbores merged into one 5 × 9 slot so the U's bridge sits flush and is the tie point |
| brow-rail index plunger ×2 | printed PLA plunger: 3.2 shank in the 3.4 keeper, integral spring flange and thumb paddle, printed lying down; steel spring stays | new part `index_plunger` (small-parts plate); the C-collar and its glue go |
| bayonet lock pin ×2 | printed PLA pin Ø3.2 × 7.8 driven by the knob eccentric, in the lock post | new part `disk_lock_pin`; the post is coupon I |

Buy when convenient (~$10, none blocking): 1 m of 1.6 mm stainless TIG rod (U-pins, never rusts), 3 mm brass rod
(tenons, if cutting nails palls). Check the 12 ga box: dull grey is galvanised and needs no sealing.

## 3. Lines: what changes and why

| element | fault | change |
|---|---|---|
| rope spine: epoxy | metal-filled = iron powder along the hat line, nearest the coils | unfilled or glass-filled epoxy, BOM and spec |
| rope spine: rope | nylon/polyester cord does not bond to epoxy (pulls out of its tube); twine rots | fibreglass tow or a 4 mm strip of glass cloth; same channel, same cover |
| rope spine: ends | the channel stops 2 mm short of the solid nodes on both sides, where a crack starts | run the channel into the node by 3 mm (`build_cradle_front`, `build_rear_band_half`) |
| coil cable | no connector: a "removable" disk is removed by unthreading a Ø5 bore | JST-XH 2-pin under the hub-node foam; the disk carries a 60 mm pigtail through the arc slot |
| coil cable | the arc slot's printed edges chafe the lead on every turn | 0.6 mm chamfer on the slot edges (`build_disk.back`) |
| harness cable | "ethernet pairs": bulk cable is solid core and fatigues at the terminations | stranded patch cable, BOM |
| harness joints | under glued foam at the nape, in sweat | adhesive-lined heat-shrink on every joint; foam on hook-and-loop, not glue, BOM + spec |
| harness covers | the rear half's inner harness cover is glued: a cable under it is entombed | cover strips on cable runs clip (a snap lip), only spine covers glue (`build_spine_covers`) |
| brow LED cable | crosses the tilt pivot with no slack specified | 30 mm service loop at the link pocket, assembly step |
| umbilical | zip ties through sharp printed slots | GX16-8 aviation connectors, panel-mounted in the belt pack and the nape core base (Ø16 hole replaces the Ø8 hole + zip-tie slots); screw-lock; the coils are off in combat trim so no breakaway is needed |
| nexus lanyard | a cord loop on headgear; insurance against the old bayonet | dropped from the BOM and the assembly; the Ø4 hole stays |
| nail lanyard | thread round a nail head, a flailing pin | goes with the U-pin (its bridge is the tie point) |
| chin strap: webbing | slots are 14 mm tall, BOM says 15 mm webbing: it does not fit | 12 mm polyester webbing + side-release buckle; slot height unchanged |
| chin strap: slots | pairs 8 mm apart leave a 4 mm web loaded across its layers (~500 N); sharp printed edges cut webbing | pairs 12 mm apart; 1 mm chamfer on every slot edge (`STRAP_SLOT`); check the cradle's slots against the spine channel (slot W −2.5..+11.5, channel W +8..+12) and move the slot down if they share a span |
| chin strap: policy | "only if the shake test asks" | required in combat trim; optional in sanctuary; spec §2 |
| coil former | magnet-wire solder joints break under vibration | pot each joint on the pad boss with epoxy, assembly step |
| EDA fabric | fabric-to-wire termination unspecified | snap stud riveted into the patch; the TENS snap leads in the inventory plug straight on |

## 4. Phases, tied to the print order

**Phase 0 — before d1 prints (today). APPLIED 2026-09-20.**
- canon: `PIN_DIA` 2.9, `PIN_HEAD_DIA` 7.0, `NAPE_PINLOCK_PIN` 1.6 / 1.7 / 1.8 with the merged slot, `STRAP_SLOT` pair spacing 12 and the edge chamfer.
- **d1 v2**: PINLOCK ladder 1.6 / 1.7 / 1.8 / 1.9 (16 ga); one U-pin pair (two 1.8 holes one tooth pitch apart under a merged slot; bend a 16 ga nail as the stand-in); HORIZ ladder 2.7 / 2.9 / 3.1 round + teardrop (12 ga) plus 3.4 / 3.6 (the printed plunger); a printed Ø3.2 × 20 pin on the tile, lying down; a strap-slot pair at the new spacing with chamfers; M3 tap / clear, M4 clear, Ø4 blind sockets and both Ø8 socket ladders unchanged. Same tile count, same ~2 h.
- PRINT_LOG calibration rows re-written to the new nominals.

**Phase 1 — before the cradle prints. APPLIED 2026-09-25.** d1 v2 read: the hole numbers are in canon (spec §6.1 rule 8); the spine channel runs 3 mm into each solid node (`SPINE_INTO_NODE`, a potted rope end; the cover strips keep the free span) and to 0.5 mm of the node face on the rear halves; the strap slots are cut in the band's own frame with the chamfer frustums on both faces, both bands. The pin-lock ladder was under size, so the U-pin is retested on the body at 2.5 in Phase 2. d1's numbers into canon or the projects (hole compensation); the spine channel into the nodes; the strap slots checked against the spine and moved if needed; the tenon teardrops at 3.1.

**Phase 2 — rear halves, nape, pads, covers.** *Found 2026-09-25 while enlarging the M3 pilot: the nape dial body's two end lid screws (0, ±17) pass through the rack channels where both racks overlap; they were always there. Move them to the midline web (v 0, 9.4 mm wide) at about u ±27, or show the racks clear them, before the dial set prints.* The nape pin-lock body with the U-pin slot; the rear half's harness cover as a clip; the plug cross hole 2.5; the U-pin bending jig (small-parts plate). BOM: stranded cable, adhesive heat-shrink, hook-and-loop foam, unfilled epoxy, glass tow, 12 mm webbing + buckle, JST-XH pairs, GX16-8 pair.

**Phase 3 — nexus and disks.** The lock post (coupon I, a nail as the stand-in pin) and `disk_lock_pin`; `index_plunger` (read the pin lug's keeper geometry first: hole depth, travel, spring size); the coil connector under the foam; the arc-slot chamfer.

**Phase 4 — electronics and belt pack.** GX16-8 panel cutouts in `belt_pack` and `nape_core_base`; EDA snap studs; coil joint potting in the assembly steps.

## 5. What d1 decides, once re-laddered

1. The tenon pin's slip hole for the 12 ga, round and teardrop, horizontal (the cradle's inverted print).
2. The pin-lock holes for the 16 ga, vertical, and whether a U-pin drops in and pulls out.
3. Whether a printed Ø3.2 pin slides in a printed 3.4 hole, vertical and horizontal: the plunger and its keeper.
4. The node-top sockets on the bed face (the cradle gate proper): which of 8.3 / 8.5 / 8.7 / 8.9 takes the peg after the first layer's squash.
5. M3 thread-forming and clearance, M4 clearance, the Ø4 blind sockets, as before.
6. Whether 12 mm webbing passes the chamfered slot pair, if webbing is to hand.

Everything the cradle's holes depend on is on that one plate.
