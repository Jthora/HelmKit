# Mk0.5 — Prior-Art Index (3D-printable references)

- **Status**: `v0` (2026-05-20)
- **Source library**: `/Volumes/Ext2TB/3D Models/Downloads/` (off-repo,
  ~16 GB, 362 Thingiverse models with LICENSE.txt + README.txt
  preserved per model directory).
- **Purpose**: Catalog third-party open-source 3D models that may
  inform the Mk0.5 / Mk1+ physical engineering. Errs on the side of
  *over-listing*: many are reference-only and will never be imported.
  Better to know what's available and ignore it than to miss a
  useful prior art.
- **Companion doc**: [`mk0.5_base_crown_architecture.md`](mk0.5_base_crown_architecture.md).

---

## 1. License-tier convention

| Tier | Meaning | HelmKit policy |
|---|---|---|
| **🟢 PD** | Public Domain dedication | Use freely; credit the dedicator anyway. |
| **🟢 CC-BY** | Attribution only | **Safe to incorporate.** Add to `3D-Models/HelmKit/_derived/ATTRIBUTIONS.md` when used. |
| **🟡 CC-BY-SA** | Attribution + Share-Alike | "Viral" — any derivative STL must also be CC-BY-SA, which would force *only that derivative* (not the whole HelmKit repo) to be CC-BY-SA. Use only when the geometry is irreplaceable and a SA derivative-island is acceptable. |
| **🔴 CC-BY-NC** / **CC-BY-NC-SA** / **CC-BY-NC-ND** | Non-commercial | **Reference only.** HelmKit's roadmap explicitly contemplates Mk3 productization; importing NC vertices into the repo would permanently bar that path. Measure and re-implement; do not import. |
| **⚪ GPL / other** | Software-style copyleft | Case-by-case; usually treat as 🟡 or 🔴. |

Library distribution (2026-05-20 snapshot):

| Tier | Count |
|---|---|
| CC-BY | 179 |
| CC-BY-NC | 60 |
| CC-BY-SA | 60 |
| CC-BY-NC-SA | 44 |
| CC-BY-NC-ND | 9 |
| Public Domain | 3 |
| Other (GPL, etc.) | ~7 |
| **Total** | **362** |

---

## 2. Rails, mounts, dovetails

| Tier | Asset | Why it matters for HelmKit |
|---|---|---|
| 🟢 CC-BY | **Picatinny rail - 23185** (SFE_Tim) | Canonical Thingiverse Picatinny. Has `.skp` (SketchUp) source. **The primary tooth-profile reference** for R1's integral rail. |
| 🟢 CC-BY | **Picatinny Rail Female Diamond Grip - 2897402** (cmdctrl) | Female slot side with `.svg` source. Sanity-check for pod dovetail tolerances. |
| 🟢 CC-BY | **Black Aces Tactical Rail - 3873295** (Esteran) | Secondary straight-rail reference for cross-comparison of dimensional consistency. |
| 🟢 CC-BY | **Lucid Gloves ESP32U Mount - 5160208** | ESP32 board mount pattern. HelmKit uses ESP32-S3 Heltec — footprint differs but mounting logic transfers (board standoffs, USB-C clearance, antenna keep-out). |
| 🟢 CC-BY | **Articulating, Wall-Mounted, Magnetic Phone Mount - 2448971** | Articulating-arm geometry. Reference for any future temple-boom that needs to *swing out* (PPG, magnetometer arms). |
| 🟢 CC-BY | **Raspberry Pi 4/5 1U rack-mount bracket - 4125055** | Bracket-to-rail transition geometry — useful when the rear compute pod docks to R2's M-LOK slot. |
| 🟢 CC-BY | **Katana / wakizashi / sword mount - 3330097** | Curved cradle on a wall — geometric cousin of R2's occipital cradle. |
| 🔴 CC-BY-NC-SA | **Forearm Gauntlet Picatinny Rails L & R - 5197830** (Kajukenbo) | ★ **Closest existing prior art to R1's curved rail.** Forearm ≈ skull crown geometrically. **Reference only — do not import vertices.** Re-implement curved-rail sweep from scratch using SFE_Tim's CC-BY tooth profile. |
| 🟡 CC-BY-SA | **Rival Tactical Rail Clip - 2972579** | Belt + MOLLE rail clip variations. Visual reference for the TPU detent leaf only. |

---

## 3. Clips, buckles, latches, quick-releases

The pod's two-step lock + the chin-strap cam buckle both have direct prior art here.

| Tier | Asset | Relevance |
|---|---|---|
| 🟢 CC-BY | **Cloth mask strap clip - quick connector - 4289582** | Quick-disconnect strap connector. ★ Candidate for the chin-strap junction if cam buckle proves too bulky. |
| 🟢 CC-BY | **Small Kydex Belt Clip - 5840616** | Single-screw spring-clip geometry — TPU detent leaf antecedent. |
| 🟢 CC-BY | **Quick Clip belt holder UK FORCES Police - 3378784** | Police-grade quick-release; passes a real motion budget. |
| 🟢 CC-BY | **Utility-belt accesory clip - 79866** | Minimal one-screw clip — design-floor reference. |
| 🔴 CC-BY-NC | **Armor Latch - 5200180** | Two-step armor latch geometry. Mechanism reference for the dovetail+detent lock. |
| 🔴 CC-BY-NC | **Molle Quick Clip - 3577260** | Quick-release MOLLE clip. Mechanism reference. |
| 🔴 CC-BY-NC | **Strap Buckle (No Supports) - 2814683** | 8 STLs of strap buckle variants. Mechanism reference for cam-buckle backup designs. |
| 🔴 CC-BY-NC-SA | **TM Breacher Weapon Catch - 771893** | Spring-loaded catch — mechanism reference for the rail end-stop. |

---

## 4. Straps, webbing, retention

| Tier | Asset | Relevance |
|---|---|---|
| 🟢 CC-BY | Cloth mask strap clip - 4289582 | (Listed above.) |
| 🔴 CC-BY-NC | Strap Buckle (No Supports) - 2814683 | (Listed above.) |

**Note**: most retention will be off-the-shelf nylon webbing + a
commercial side-release cam buckle (e.g. ITW Nexus, ~$3). Printed
buckles are *interesting* but injection-molded nylon buckles are
stronger by an order of magnitude and cost less. Use printed buckles
only for the dev-print fit-check, not the bench-session helmet.

---

## 5. Helmets, head retention, shell topology

Useful for studying *how full-coverage helmets achieve retention*.
None of these are imported; all serve as anatomical / mechanical
reference.

| Tier | Asset | Relevance |
|---|---|---|
| 🟢 CC-BY | **Daft Punk Helmet - 3225502** | Shell topology + visor integration. |
| 🟢 CC-BY | **SpaceX Helmet - 3471482** | Modern aerospace helmet — visor seam, mic boom routing. |
| 🟢 CC-BY | **Robotech Helmet (Macross) - 1883337** | 17-piece multi-shell joinery — reference for how to break a one-piece shell into printable sub-parts (we don't need to, but the seam logic is instructive). |
| 🟢 CC-BY | **Synth Field Helmet (Fallout 4) - 2731612** | Modular hardpoint *aesthetic*. Several visible boom mounts that look like our HP-T* arms. |
| 🟢 CC-BY | **High Detail Visor for Halo 4 Helmet - 5565544** | Visor curvature + mounting tabs. |
| 🟢 CC-BY | **O'neal helmet visor screw - 4667048** | Visor-pivot fastener spec. **Most directly applicable**: same geometry we'd use for HP-F HUD optic pivot. |
| 🟡 CC-BY-SA | **Split Pieces Halo Master Chief Helmet - 6423987** | 16-STL split — reference for split-shell variants only. |
| 🔴 CC-BY-NC | **Halo Reach Emile Helmet - 3266084** | Combat-helmet retention reference. |
| 🔴 CC-BY-NC | **Maska SCH Russian Military Helmet - 4869306** | Real combat helmet — three-point retention prior art. |
| 🔴 CC-BY-NC | **Racing Helmet - 170222** | High-g retention reference (motorsport-grade). |

---

## 6. Visors, optics, HUD mounts

R1's HP-F station is reserved for HUD optics and forward-facing
sensors. The visor literature is rich.

| Tier | Asset | Relevance |
|---|---|---|
| 🟢 CC-BY | **Medical visor - 4315110** | Clean visor pivot — minimum-viable HP-F optic mount. |
| 🟢 CC-BY | **Sports Visor - 2170325** | 3-STL sports visor — anatomical curve reference. |
| 🟢 CC-BY | **Mars Cybernetics Advanced Systems mark 3-27 Recon visor - 2392819** | 10 STLs of modular tactical visor with attachment points — geometrically very close to HelmKit aesthetic. |
| 🟢 CC-BY | **Titanfall Pilot Visor - 5557179** | HUD-with-eyepatch geometry; useful for asymmetric HP-FL/HP-FR designs. |
| 🟢 CC-BY | **Trooper Visor - 3045437** | Minimal eye-slot visor. |
| 🟢 CC-BY | **Widowmaker Talon Visor Overwatch - 2875066** | Cyberpunk single-eye HUD — aesthetic reference. |
| 🟡 CC-BY-SA | **Visor holder_connector for Halo 4 Helmet Full Size A - 174558** | The connector geometry between visor and helmet — close to HP-F's optic mount task. |

---

## 7. Electronics enclosures

| Tier | Asset | Relevance |
|---|---|---|
| 🟢 CC-BY | **Raspberry Pi 4B Case - 3793664** | 59 STLs of variants. Reference compute-node enclosure dimensions; useful when HP-R's compute pod is laid out. |
| 🟢 CC-BY | **Raspberry Pi 4 case - 3714695** | 4-STL variants — cooling cutouts. |
| 🟢 CC-BY | **EMP Generator Case - 5721071** | Hardened-electronics enclosure pattern (relevant for Mk1 stim driver shielding). |
| 🟢 CC-BY | **Lucid Gloves ESP32U Mount - 5160208** | (Listed above.) Direct ESP32 board mount. |
| 🔴 CC-BY-NC | **EMP case with 2 18650 batteries - 2936599** | 18650 dual-cell holder — reference for the on-helm battery pod sizing. |
| 🔴 CC-BY-NC | **'BOOM box' high voltage capacitor bank case - 2980012** | HV-cap enclosure — reference for Mk1 coil-driver capacitor housing. |

---

## 8. Coils, antennas, magnets (Mk1 + Mk1.5 relevance)

Not directly Mk0.5 (no stim payload), but stored against the Mk1
bifilar-coil hardware build documented in
[`docs/mk0_pcb_bifilar_coil.md`](../mk0_pcb_bifilar_coil.md).

| Tier | Asset | Relevance |
|---|---|---|
| 🟢 CC-BY | **Halbach Array - 3959218** | Reference geometry for the Mk2.5 second-stim modality (B-field array). |
| 🟢 CC-BY | **Spherical Halbach magnet array - 5526348** | 9 STLs, three sizes. Magnet-positioning fixtures. |
| 🟢 CC-BY | **Bowl shaped magnet array (LaPoint array) - 5995633 / 5993889** | Magnet-array geometry references for any future field-shaping experiment. |
| 🟢 CC-BY | **Neodymium engine - 2474735** | 16 STLs — magnet jigs and positioning sleeves. |
| 🟡 CC-BY-SA | **Perendev Magnet Motor - 816326** | (Permanent-motion claim is bunk; the *magnet positioning jigs* are useful regardless.) |
| 🟡 CC-BY-SA | **Permanent Magnet Generator - 595037** | Coil-on-core geometry reference. |
| 🟡 CC-BY-SA | **Slanted Loop Mesh - 2271772** | Geometric mesh — reference for antenna-pattern visualization. |

---

## 9. Fans, cooling, vents

Mk1+ compute pod and stim driver will need active or passive
thermal management.

| Tier | Asset | Relevance |
|---|---|---|
| 🟢 CC-BY | **Turbine Fan - 5906512** | 7-STL turbine variants. |
| 🟢 CC-BY | **Power Supply Fan Silencer - 4251317** | Vibration/noise damping shroud. |
| 🟢 CC-BY | **60mm Exhaust Fan Silencer Flowmaster - 4931122** | Quiet-fan integration reference. |
| 🟡 CC-BY-SA | **Various fan size conversion adapters - 21112** | 42 STLs of fan adapters — covers virtually any compute-pod cooling pairing. |

---

## 10. HelmKit's own prior art on the same drive

These are **not** third-party — they're earlier HelmKit / Psi-Tech
project work stored on the same drive. Already in-canon by virtue
of being our own:

| Path | Status |
|---|---|
| `/Volumes/Ext2TB/3D Models/HelmKit/HelmKit-mk2/` | Earlier Mk2 work — superseded by mk_ladder.md's current Mk-numbering. Inspect for reusable geometry but do not assume current. |
| `/Volumes/Ext2TB/3D Models/Psi Tech/Psi Defender/` | Psi Defender project (separate repo `Jthora/psionicDefender`). Geometric prior art for the disc / chest modules. |
| `/Volumes/Ext2TB/3D Models/Psi Tech/Psi Stabilizers/` | Psi Stabilizer (separate repo `Jthora/psiStabilizer`). |
| `/Volumes/Ext2TB/3D Models/EMP/` | EMP Generator + Stealth Wand + Psionic EM Pulse Blaster — relevant when Mk1 coil drive lands. |
| `/Volumes/Ext2TB/3D Models/MagnetoRepulsors/Basic/` | Magneto-repulsor prior art. |
| `/Volumes/Ext2TB/3D Models/Medical/BoneSpeakerAdapters/` | ★ Direct prior art for HP-E* (ear-shield) bone-conduction transducer mount. |
| `/Volumes/Ext2TB/3D Models/PowerPack/EMP Resistant Power Pack/` | Hardened battery pack — relevant if Mk1 coil drive needs an EMP-shielded power source for self-testing. |
| `/Volumes/Ext2TB/3D Models/RaspberryPi/SecureWallMountFrame/` | Wall-mount frame reference. |
| `/Volumes/Ext2TB/3D Models/TheWings/theWings_v01a.blend` | Blender source. (Cosmetic.) |
| `/Volumes/Ext2TB/3D Models/Vents/ConduitPort_4InchConnector/` | Cable conduit reference for the R1 rail's printed-in raceway. |

---

## 11. The five assets we will probably actually touch

If the 362-model library distilled to a high-confidence shortlist
for Mk0.5 work:

1. **`Picatinny rail - 23185`** (CC-BY) — primary tooth-profile reference.
2. **`Picatinny Rail Female Diamond Grip - 2897402`** (CC-BY) — pod-side tolerance check (has SVG).
3. **`Lucid Gloves ESP32U Mount - 5160208`** (CC-BY) — ESP32 board-mount pattern.
4. **`O'neal helmet visor screw - 4667048`** (CC-BY) — visor pivot fastener (HP-F).
5. **`Medical/BoneSpeakerAdapters/`** (our own) — direct HP-E* ear-coupling prior art.

Plus one ★ **reference-only** companion:

- **`Forearm Gauntlet Picatinny Rails L & R - 5197830`** (CC-BY-NC-SA) — geometrically closest prior art to R1's curved rail. **Measure, learn, do not import.**

---

## 12. Workflow for incorporating a CC-BY asset

When the time comes to actually use one of the 🟢 assets:

1. Copy the source folder (with its original LICENSE.txt + README.txt) into `3D-Models/HelmKit/_derived/<author>_<thing-id>/`.
2. Append a row to `3D-Models/HelmKit/_derived/ATTRIBUTIONS.md`:
   `| Thingiverse #<id> | <author> | CC-BY | <imported-on date> | <how used in HelmKit> |`
3. In Blender, derive a new mesh by extracting only the geometric primitive needed (e.g., the rail tooth cross-section profile), then sweep / extrude / combine into the HelmKit shell as original work.
4. The result is *derivative* in spirit — the attribution row is the license-compliant satisfaction of the BY clause.

For 🟡 SA assets: same workflow, but the resulting derivative STL ships under CC-BY-SA (the rest of the repo unaffected) and lives in `3D-Models/HelmKit/_derived/_sa/` to make the boundary obvious.

For 🔴 NC assets: **do not copy into the repo at all.** Open the source folder on the external drive, take notes, close it. Re-implement from notes.

---

## References

- [`mk0.5_base_crown_architecture.md`](mk0.5_base_crown_architecture.md) — the canonical mechanical spec this index supports.
- [`docs/field-notes/volume-1/02_platform.md`](../field-notes/volume-1/02_platform.md) §"hardpoint specification" — the rail-forever contract.
- Library snapshot: `/Volumes/Ext2TB/3D Models/Downloads/` as of 2026-05-20.
- Inventory dump: `/tmp/3dlib_inventory.tsv` (regenerable; not committed — external-drive paths are operator-specific).
