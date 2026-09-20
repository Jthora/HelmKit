# Bifilar Coil Engineering — wiki translation

- **Source**: [`Bifilar Coil Engineering`](https://wiki.fusiongirl.app/wiki/Bifilar_Coil_Engineering), pageid 6571, revid 12570, fetched 2026-08-05T20:41:57Z (see `docs/wiki_cache/bifilar_coil_engineering.meta.json`).
- **Wiki branch**: Psionic Engineering, Branch D1 (Drive and Modulation Systems).
- **Related, older wiki page**: `Bifilar Coil` (pageid, cached as `docs/wiki_cache/bifilar_coil.wikitext`) — the Pass-2 page this repo's existing coil design already anchors to. `Bifilar Coil Engineering` is a new, far more detailed and numerically specific page built on top of it.

## Wiki claim

The bifilar coil is presented as the *unique* coil geometry that maximizes local $E^2$ (the term that sources the wiki's $\alpha F_{\mu\nu}F^{\mu\nu}$ ψ-coupling term) while cancelling far-field $B$ to near zero — the only geometry, per the wiki, that can satisfy ICNIRP limits for a head-worn device while still doing useful EM-to-ψ transduction.

Concrete numbers given:

| Parameter | Wiki value | Basis given |
|---|---|---|
| Trace width | 0.3 mm | DLP-printable at 25 μm resolution, 12× margin |
| Trace gap | 0.2 mm | $E_{peak} = V/d = 200\text{V}/0.2\text{mm} = 1\text{ MV/m}$, with 2.5× dielectric safety margin |
| Drive voltage | 200 V (peak) | ICNIRP-limited for head-worn use |
| Drive frequency | 40 kHz | Matches Shepard-tone carrier scheme; puts the coil in the capacitive regime relative to its ~2 MHz self-resonance |
| Peak current | ~100 A (pulsed, ~0.1% duty cycle) | $I = V/R$ across ~2 Ω trace resistance |
| Far-field E at 10 cm | ~1 V/m | vs. ICNIRP 83 V/m limit — 83× margin claimed |
| Far-field B at 10 cm | ~0.4 μT | vs. ICNIRP 27 μT limit — 67× margin claimed |
| Fabrication | Traces printed/plated directly onto the TPMS lattice shell surface (DLP multi-material or laser-induced-graphene + electroless Cu plating), not a separate PCB | Winding density spatially varies to mode-match a COMSOL-extracted ψ₀₁₀ eigenmode |

## Engineering interpretation

This is a **different physical design** from the coil already specified in `../mk0_pcb_bifilar_coil.md`, not a refinement of it:

| | Existing repo design (`mk0_pcb_bifilar_coil.md`) | Wiki's `Bifilar Coil Engineering` (this page) |
|---|---|---|
| Form factor | Discrete 30×30mm two-layer PCB, milled on desktop CNC | Traces embedded directly on/in a full TPMS lattice shell surface, DLP/LIG fabricated |
| Drive frequency | 1–8 MHz carrier, 7.83 Hz envelope | 40 kHz, three-carrier Shepard-tone scheme |
| Drive voltage | Not specified as high-voltage; implied low-voltage HV-module-driven, current-limited to ≤ 50 mA fault case | 200 V design point, ~100 A peak pulsed current |
| Peak instantaneous power | Not calculated in the existing doc, but current-limited to 50 mA fault case implies low power | 20 kW peak (pulsed, 0.1% duty → 20 W average) |
| Dependency | None — buildable now from inventory | Depends on `TPMS Lattice Design` (B7) and `Smart Composite Fill` (B8) shell existing first |

The wiki page is Track A (its own terminology) in the sense that the electromagnetic engineering — trace geometry, ICNIRP compliance calculation, thermal pulse budget — is buildable and testable without assuming ψ is real. But it is a **materially higher power-class design** than anything currently built or safety-reviewed in this repo: 200V/100A-peak pulsed drive into a head-worn shell is a different risk profile than the existing low-voltage PCB coil, regardless of the ICNIRP far-field margins claimed.

**Recommendation**: treat this page as a **candidate future design**, not a build target for Mk0.5/Mk1.0. The existing `mk0_pcb_bifilar_coil.md` design remains the near-term Mk1.0 coil (per `../mk_ladder.md`'s H1 hypothesis). If the higher-power shell-embedded design is ever pursued (likely Mk1.5+ or Mk2+, once a TPMS-lattice shell exists at all), it needs its own bench-only, unpowered-on-human, instrumented safety pass before being touched — same discipline as everything else on `../safety.md`.

## Verified arithmetic — confirmed discrepancies

Independent recomputation via `tools/verify_psi_equations.py` against the page's own stated inputs and formulas (run `python3 tools/verify_psi_equations.py` to reproduce). 6 of the page's numeric claims reproduce exactly (E-field peak, the full far-field falloff table, B-field cancellation, ICNIRP margins); two do not, both in the same "Pulsed Drive Constraint" section:

1. **Adiabatic pulse temperature rise.** The page states the per-pulse formula `ΔT = P_peak·τ/(ρc_p·V)` gives **9.7°C**, using its own stated inputs (P_peak=20,000W, τ=1μs, ρc_p=3.44×10⁶ J/(m³·K), V=6×10⁻¹³ m³). Recomputing that exact expression gives **≈9690°C** — off by almost exactly 1000×.

   **Root cause identified**: substituting **average** power (P_avg = P_peak × 0.1% duty cycle = 20 W — the page's own duty-cycle figure, stated one paragraph earlier) for the formula's labeled `P_peak` reproduces **9.69°C**, matching the stated answer almost exactly. This pins the error down precisely: the page appears to have used the average power where the formula (by its own variable name and by the physical meaning of a "per-pulse" transient-heating calculation) calls for the peak power. Whether the intended, physically-correct calculation is the ~9.7°C average-power version or the ~9690°C peak-power version is a real modeling question — flagged for the wiki maintainers, not resolved here.

2. **Average pulsed drive power — self-contradiction.** The same section's body text states "average dissipation = 20 W × 0.001 = 20 mW per metre of trace." The page's own later TML sanity-check table states "20 kW peak × 0.1% duty cycle = 20 W average." Straightforward arithmetic (P_peak × duty_cycle = 20,000 W × 0.001) gives exactly **20 W**, matching the sanity-check table and contradicting the body text's 20 mW figure — an internal inconsistency independent of finding #1, though possibly related (both involve a mix-up between the 20,000 W peak figure and the 20 W average figure derived from it).

## Verified arithmetic — cross-page discrepancy (not this page's fault alone)

3. **Shepard-carrier frequencies disagree with the hub page.** The `Psionic Engineering` hub's Branch D summary table states this page's DSP implementation uses "3 carriers (10, 20, 40 kHz)." This page (and `Shepard Tone Synthesis`, which this page's drive chain depends on) consistently states three carriers at **40, 80, 160 kHz** (f₀, 2f₀, 4f₀), with detailed supporting derivation (FPGA clock-division exactness at a 160 MHz clock; harmonic subordination to a 1.5 MHz PZT resonance as its 37th harmonic) that only works out for the 40/80/160 triple. The hub's "10, 20, 40 kHz" appears to be a stale summary-table entry that wasn't updated when the detailed Shepard Tone Synthesis page was written. See `tools/verify_psi_equations.py`'s `check_shepard_tone_carrier_frequency_consistency`.

## BOM implication

None for current Mk0.5/Mk1.0 scope. If pursued later: BST nanocomposite precursors (see `tpms_lattice_design.md` for the composite fill BOM), DLP multi-material printer or CO₂ laser for LIG fabrication, electroless-copper plating bath — none of these are in the current `docs/inventory.md`.

## Geometry / parameter implication

None for the current Mk0.5-β mechanical topology (`../mechanical/mk0.5_topology_beta_architecture.md`) or the `tools/blender/` generator suite — those build solid PETG/TPU parts, not a TPMS lattice, and don't route embedded conductive traces. No change recommended to the generator suite from this page alone.

## Safety implication

**This is the one concrete, actionable finding from this page.** `../safety.md`'s frequency-band table (§2) has rows keyed on magnetic-field bands (sub-MHz pulsed magnetic, allowed at Mk1) and RF carrier bands (300 MHz–2.45 GHz, deferred), but has no row that clearly covers a **near-field, E-field-dominant, sub-MHz emitter with a 200V/100A-peak pulsed drive** — which is what both the wiki's new spec and, to a lesser degree, the existing low-voltage PCB coil actually are (a bifilar coil's whole design point is that it is *not* a magnetic-dipole radiator).

Recommendation (not applied here — this is a safety-table change and should get its own review, not be bundled into a wiki-translation pass): add an explicit row to `../safety.md` §2 for "near-field E-field-dominant coil (bifilar/caduceus), sub-MHz" with its own ICNIRP E-field ceiling and a peak-current / peak-instantaneous-power ceiling, separate from the existing B-field-keyed rows. Until that row exists, any bifilar coil design — including the existing low-voltage one — is being evaluated against a safety table that doesn't have a category that precisely fits it.

## Falsification hook

Not directly F1–F11 (those are ψ-hypothesis falsifiers). The wiki page's own TML-1/TML-2 protocol (trace geometry verification via microscopy + 4-point resistance + HiPot; EMC compliance via near-field E-scan + far-field E/B probes) is pure-EM verification, engages no ψ claim, and would sit alongside `../falsification.md`'s existing F1 sham-control requirement as a **prerequisite gate**, not a new F-row.

## Open questions / extrapolations

- (c) The wiki's mode-matched winding density (dense at equator, sparse at poles, following a COMSOL-extracted ψ₀₁₀ eigenmode) assumes the Psi Stabilizer shell geometry and a specific mode-solve that doesn't exist in this repo. Whether that pattern is even meaningful without the ψ hypothesis is an open question the wiki page itself flags as Track-B-adjacent (the coupling-efficiency justification for the *pattern*, not the coil's basic EM behavior, depends on ψ mode overlap).
- (b) The 200V/40kHz/100A-peak numbers are wiki-stated, not independently re-derived here. The ICNIRP margin claims (83× on E, 67× on B) follow from the wiki's own formulas given its own assumed drive parameters; they have not been checked against IEC/ICNIRP 2020 methodology by this repo.
