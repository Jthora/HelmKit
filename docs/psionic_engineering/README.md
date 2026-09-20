# Psionic Engineering — wiki-branch translation index

**Track**: [Track A — wiki content → engineering translation](../plans/2026-tier1-launch/track-A-wiki-translation.md)
**Source**: [`Psionic Engineering`](https://wiki.fusiongirl.app/wiki/Psionic_Engineering) (wiki pageid 6541), first published as part of the 2026-08-05 wiki content drop that Track A was blocked on.
**Cache**: `docs/wiki_cache/psionic_engineering.wikitext` (and sibling `.wikitext` files for every page listed below), synced via `tools/wiki_sync.py` with the "Pass 3" page list in `tools/wiki_pages.yml`.

---

## What the wiki branch is

`Psionic Engineering` is a new 42-page discipline the wiki organizes between `Psionics` (field theory) and `Psi-Tech` (device catalog). Its stated discipline: every material, component, and system must be **derived** from a specific term in the wiki's master ψ-field equation

$$\Box\psi - m_{\rm eff}^2\psi - \lambda_{\rm eff}\psi^3 = \alpha_{\rm eff} F_{\mu\nu}F^{\mu\nu} + J_{\psi}$$

— never invented by analogy alone. It splits every page into:

- **Track A (wiki's own term, same name as this repo's convention by coincidence)** — buildable and testable with existing technology regardless of whether ψ is real: metamaterial fabrication, coil geometry, composite chemistry, control firmware.
- **Track B** — only meaningful if the ψ hypothesis is confirmed: impedance matching to a ψ field, soliton memory states, group-coherence amplification.

It also defines a **TML-1 → TML-5** validation ladder (materials science → bench EM → single-operator sham-controlled → closed-loop → field deployment) with quantitative pass/fail criteria per level. This TML ladder is the wiki's own maturity framework for *this branch specifically* — do not confuse it with this repo's [Mk-ladder](../mk_ladder.md) (Mk0.0→Mk3.0), which governs the HelmKit product as a whole. See [§ Ladder note](#note-two-different-ladders) below.

Of the 42 planned pages, as of this sync only **Branch A (foundation, 6 pages)**, **Branch B (materials, 9 pages)**, **Branch C (components, 12 pages)**, and **D1–D2 of Branch D (drive systems)** have real content. Branches D3–D6, E, F, and G are referenced throughout the hub but are still redlinks on the live wiki (confirmed 2026-08-05) — re-run `tools/wiki_sync.py --check` periodically to catch them landing.

## Translation pages in this directory

| Page | Wiki source | Status | Directly affects |
|---|---|---|---|
| [`bifilar_coil_engineering.md`](bifilar_coil_engineering.md) | [`Bifilar Coil Engineering`](https://wiki.fusiongirl.app/wiki/Bifilar_Coil_Engineering) (D1) | translated | Coexists with, does **not** replace, `../mk0_pcb_bifilar_coil.md` — different power class, see doc |
| [`tpms_lattice_design.md`](tpms_lattice_design.md) | [`TPMS Lattice Design`](https://wiki.fusiongirl.app/wiki/TPMS_Lattice_Design) (B7) + [`Smart Composite Fill`](https://wiki.fusiongirl.app/wiki/Smart_Composite_Fill) (B8) | translated | New candidate shell material system, not yet adopted by `../mechanical/` or `tools/blender/` |
| [`stabilizer_derivation.md`](stabilizer_derivation.md) | n/a — original derivation (wiki `Psi Stabilizer` has no hardware spec) | working, 2026-09-11 | Physiology → coupling channels with doses → near-field model (`tools/stabilizer_field_model.py`) → coil envelope. Under α = 0 a pod coil cannot induce cortical fields; the Stabilizer's HRV effect is a resonance-breathing pacer; the coil is the H1 / ψ experimental arm |
| [`computational_toolkit.md`](computational_toolkit.md) | n/a — original tooling, not a page translation | v2, shipped 2026-08-05 | Six tools: `verify_psi_equations.py`, `experiment_design.py`, `analyze_dyadic_coherence.py`, `forced_choice_protocol.py`, `scan_wiki_consistency.py`, `analyze_ambient_confounds.py` — found 4 confirmed wiki-side arithmetic/consistency discrepancies + 1 literature-citation issue |
| [`literature_grounding.md`](literature_grounding.md) | n/a — checks wiki citations against real primary literature, not a page translation | shipped 2026-08-05 | Real Ganzfeld/Star Gate effect sizes; feeds `experiment_design.py`'s `GANZFELD_HIT_RATE_PRESETS` |
| [`report_to_wiki_maintainers_2026-08-05.md`](report_to_wiki_maintainers_2026-08-05.md) | n/a — outbound report, not a page translation | drafted 2026-08-05, not yet sent | Single consolidated write-up of 5 findings, for the wiki-maintaining AI. Drafted here for review before sending (this repo has no email capability). Tracked in [`wiki_correspondence_log.md`](wiki_correspondence_log.md). |

Not yet translated (lower priority — Branch C component catalog is largely Track-B/speculative for Mk0.5–Mk1 scope, and Branch G "Integrated Systems" pages are still redlinks):

- Branch A (ψ Conservation Laws, Dispersion Relations, Impedance Theory, Boundary Conditions, Green's Functions) — foundational math, cached but not yet translated into `docs/derivations/`.
- Branch C individual component pages (ψ Resonator, Waveguide, Transducer, Filter, Amplifier, Shield/Absorber, Oscillator, Detector, Source, Memory Element, Phase Shifter, Coupler) — cached; each maps to a specific existing/future Psi-Tech module per the hub's table, but none are load-bearing for Mk0.5/Mk1.0 scope yet.
- `Shepard Tone Synthesis` (D2) — cached; relevant to the drive waveform once/if the bifilar coil is ever built to the wiki's newer 200V spec (see the bifilar translation doc's safety note before treating this as buildable now).

## Note: two different ladders

The wiki's own `HelmKit` / `HelmKit Architecture` pages were also revised in this drop and now describe a 7-step **Mk0.0 → Mk3.0** ladder with RF/coil stimulation starting at "Mk1.0." At first read this looked like it might collide with this repo's stance (per the older `../wiki_anchors.md` §5, written 2026-05-12) that wiki content is Mk2+/Mk3-only design intent and Mk1 stays sensing-only.

It does not collide. `../mk_ladder.md` (authored 2026-05-14, two days *after* the `wiki_anchors.md` text) already independently established the same 7-step Mk0.0→Mk3.0 ladder for this repo, with bifilar-coil stim (hypothesis H1) explicitly starting at Mk1.0. `wiki_anchors.md` §5 is simply the older, superseded statement — it predates `mk_ladder.md` by two days and should be read as historical, not current policy. No ladder decision is needed here; `mk_ladder.md` already stands as canonical.

What *is* a live, narrower gap (not a ladder problem, a hardware-safety-classification problem): `../safety.md`'s frequency-band table has rows for magnetic-field bands and RF carrier bands, but no explicit row for a near-field-**E**-dominant sub-MHz emitter — which is exactly what both the existing `../mk0_pcb_bifilar_coil.md` design and the wiki's new `Bifilar Coil Engineering` spec are. See the bifilar translation doc's Safety section for the specific recommendation.
