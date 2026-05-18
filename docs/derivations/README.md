# Derivations

Original first-principles math for HelmKit. Each derivation here is owned end-to-end by this project — not summarized from the wiki, not consensus citation chains.

**Track plan**: [`../plan/track-C-derivations.md`](../plan/track-C-derivations.md)

## Index

| # | Slug | Title | Status |
|---|------|-------|--------|
| 1 | `bifilar_near_field_enhancement` | Bifilar series-opposing near-field enhancement factor | planned |
| 2 | `caduceus_far_field_null` | Caduceus coil mutual-cancellation completeness | planned |
| 3 | `schumann_envelope_entrainment` | Envelope modulation depth vs cortical entrainment | planned |
| 4 | `group_coherence_scaling` | N-wearer coherent ensemble SNR vs N | planned |
| 5 | `sar_ceiling_mk05_bifilar` | SAR upper bound for Mk0.5 bifilar emitter @ 1 mW | planned |

## Format

Every doc here follows the template in [`../plan/track-C-derivations.md`](../plan/track-C-derivations.md#format-for-every-derivation):

- Claim (one sentence, quantitative)
- Setup (geometry + variables + units + assumptions)
- Derivation (step-by-step, KaTeX)
- Result (boxed closed form)
- Numerical example
- Falsification hook (links to row in `docs/falsification.md`)
- Notebook (links to `notebooks/<slug>.ipynb`)
- Sources tagged (a) consensus / (b) wiki / (c) extrapolated

## Reproducibility contract

Every derivation must have a paired Track D notebook (`notebooks/<slug>.ipynb`) whose figures regenerate from the closed form. If a derivation is edited, its notebook must be re-run and figure diffs committed in the same PR.
