# TPMS Lattice Design + Smart Composite Fill — wiki translation

- **Sources**:
  - [`TPMS Lattice Design`](https://wiki.fusiongirl.app/wiki/TPMS_Lattice_Design), pageid 6550, revid 12548, fetched 2026-08-05T20:41:40Z.
  - [`Smart Composite Fill`](https://wiki.fusiongirl.app/wiki/Smart_Composite_Fill), pageid 6557, revid 12555, fetched 2026-08-05T20:41:41Z.
- **Wiki branch**: Psionic Engineering, Branch B7 and B8 (ψ Materials Science). Treated together because the wiki itself pairs them: B7 specifies the lattice geometry, B8 specifies what fills it.

## Wiki claim

**TPMS Lattice Design (B7)**: triply-periodic-minimal-surface geometries — specifically Gyroid (space group Ia3d) and Schwarz-P (Im3m) — are presented as the mathematically-forced shell geometry for any "ψ resonant shell," on three grounds:

1. **Isotropy** — cubic-symmetry TPMS unit cells have isotropic effective-medium parameters ($\varepsilon_{eff}$, $\mu_{eff}$) in the long-wavelength limit; a conventional octet-truss/BCC lattice does not.
2. **Zero mean curvature** — a minimal surface has $H=0$ everywhere, so a ferrofluid-filled channel experiences no Laplace-pressure gradient ($\Delta P = \gamma(1/R_1+1/R_2) = 0$) and doesn't spontaneously redistribute.
3. **Maximum surface-to-volume ratio** — Gyroid at 25% relative density reaches $S/V \approx 2.7/a$, higher than sphere-packing (~1.8/a), maximizing EM-to-ψ coupling per the wiki's own $\alpha F_{\mu\nu}F^{\mu\nu}$ volume-integral argument.

Concrete specs given: unit cell $a = 1.2$ mm (Stabilizer target, 0.5–2mm general range), 18–25% relative density, DLP stereolithography at 25 μm layer resolution, effective-medium validity requiring $a < L_\psi/10$.

**Smart Composite Fill (B8)**: a three-phase nanocomposite to fill the lattice — BST nanoparticles (Ba₀.₆Sr₀.₄TiO₃, 50–150nm, PEG-silane functionalized) for voltage-tunable dielectric response (target: $\varepsilon_r$ tunability ≥70% from 0–200V), MWCNT at 1–3wt% (below percolation threshold) for electro-acoustic support, PZT-5H ($d_{33} > 600$ pC/N) for parametric amplification, and ferrofluid routed through the TPMS's own channels for real-time permeability control. Fabrication: VARTM infusion, 120°C/2h cure under a 10 kV/cm alignment field.

## Engineering interpretation

This is a proposed **shell material system**, not a proposed *shape* — it's orthogonal to the part-level geometry work already done in `tools/blender/`. The current Mk0.5-β mechanical topology (`../mechanical/mk0.5_topology_beta_architecture.md`) builds solid-infill PETG/TPU parts (top yoke, temple plates, visor bands, pylons) with a conventional FDM printer; nothing in that pipeline currently uses a TPMS lattice, DLP printing, or a multi-phase composite fill.

Read generously, the wiki page is making an argument that's coherent *even discarding the ψ-coupling justification*: TPMS lattices are a legitimate, well-published structural/EM metamaterial strategy (photonic-crystal and acoustic-metamaterial literature both use exactly this class of geometry), and the isotropy/zero-mean-curvature arguments hold regardless of whether ψ exists. The load-bearing, ψ-independent claim — "a Gyroid or Schwarz-P lattice is a good substrate if you want isotropic, fluid-routable effective-medium properties in a printed part" — is Track A by the wiki's own definition and would be true whether or not the rest of the psionics framework is.

What is **not** established: that HelmKit needs this. The current PETG/TPU part suite is solid-infill by design (structural, not resonant-cavity), targets FDM printers already in inventory, and has no stated requirement for tunable $\varepsilon_{eff}$/$\mu_{eff}$. Adopting TPMS + composite fill would mean a DLP printer, BST/MWCNT/PZT/ferrofluid chemistry sourcing, and VARTM infusion tooling — none of which exist in `docs/inventory.md` today, and a much higher fabrication complexity than the current CNC-mill/FDM-print pipeline.

## BOM implication

None for current Mk0.5-β scope. If pursued as a Mk1.5+/Mk2+ shell material candidate: DLP resin printer (multi-material capable, 25μm resolution), BST nanoparticle synthesis or purchase, PEG-silane functionalization chemistry, MWCNT (1–3wt% functionalized), PZT-5H ceramic stock, EMG-900-class ferrofluid, VARTM infusion equipment. This is a materially larger BOM and process investment than anything currently in the mechanical build plan — worth a explicit go/no-go decision before any inventory spend, not an incremental addition.

## Geometry / parameter implication

None applied to `tools/blender/` or `interfaces.py` in this pass. If this material system is ever adopted, it would likely arrive as a *new* generator (e.g. `build_stabilizer_shell_tpms.py`) rather than a modification of the existing solid-part generators, since TPMS lattice generation (level-set surface extraction, e.g. $\sin x\cos y + \sin y\cos z + \sin z\cos x = t$) is a fundamentally different geometry-construction approach than the boolean-primitive `bpy`/`bmesh` chains the current 11 generators use.

## Safety implication

None directly — this is a structural/materials page, not an emitter spec. Indirectly: if this shell is ever built and then paired with the higher-power bifilar coil design from `bifilar_coil_engineering.md` (which explicitly assumes traces embedded on a TPMS/BST substrate), the safety review for that pairing is the coil doc's, not this one's.

## Falsification hook

None directly (F1–F11 are ψ-hypothesis falsifiers; this page's own TML-1 protocol — VNA $\varepsilon_{eff}$ sweep vs. Maxwell-Garnett prediction, no human subjects — is pure materials science and doesn't engage the ψ hypothesis at all, matching the wiki's own claim that TML-1 requires "No — pure materials science").

## Open questions / extrapolations

- (b) The $S/V \approx 2.7/a$ figure and the isotropy claim for cubic-space-group TPMS are standard results from the metamaterial/photonic-crystal literature and are plausible as stated; not independently re-derived here.
- (c) Whether a 1.2mm Gyroid unit cell is actually the right choice for *this* project's shells (vs. an arbitrary wiki example sized for its own "Psi Stabilizer" shell) is unexamined — no HelmKit-specific coherence length $L_\psi$ target exists in this repo's docs to check the $a < L_\psi/10$ validity condition against.
- **Decision made (2026-08-05)**: TPMS Lattice Design + Smart Composite Fill are **Mk2+/aspirational**, not in scope for Mk0.5/Mk1.0. `docs/inventory.md` confirms this concretely, not just as a placeholder deferral — there is no DLP/resin printer (topology B's current parts are all FDM/PETG on a QIDI X-MAX, per `docs/mechanical/mk0.5_topology_beta_architecture.md`) and no BST/PZT/MWCNT composite feedstock anywhere in inventory. Adopting this material system would require new capital equipment first. See `docs/mk1_buildplan.md`'s inventory-grounded confirmation note (§1) for the parallel decision on the related `Bifilar Coil Engineering` page.
