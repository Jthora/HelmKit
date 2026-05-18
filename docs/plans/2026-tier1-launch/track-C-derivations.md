# Track C — Original math derivations (`docs/derivations/`)

- **Status**: `ready`
- **Effort**: ~8 hours for first derivation; 4–6 hours each thereafter
- **Depends on**: nothing
- **Unblocks**: stronger Field Notes Vol. I (Track F); pre-registered F-rows in `docs/falsification.md`

---

## Goal

A growing set of **first-principles math derivations** that this project owns end-to-end. These are not summaries of the wiki — they are original analytic work that:

1. Quantifies the engineering payoff of wiki-specified geometries (so we know what to measure).
2. Is reproducible: each derivation has a paired notebook (Track D) that regenerates its figures.
3. Is cite-able: each derivation goes into Field Notes Vol. I as an appendix.

## First derivation

**`docs/derivations/bifilar_near_field_enhancement.md`**

Derive, analytically:

- Closed-form expression for the enhancement factor $\eta = (E_{\text{bifilar}}^2 + B_{\text{bifilar}}^2/\mu_0) / (E_{\text{dipole}}^2 + B_{\text{dipole}}^2/\mu_0)$ at distance $r$ along the coil axis, both driven at the same total power $P$.
- Series-opposing winding model: two coaxial loops radius $a$, separation $d \ll a$, opposite-phase currents.
- Compare against a same-power single-turn dipole reference.
- Plot $\eta(r)$ for $r/a \in [0.1, 10]$; identify near-field knee where $\eta \to 1$.
- Tabulate $\eta$ at $r = 5$ cm (skull-distance, Mk0.5 geometry).

## Second derivation candidates

(Stack-ranked by leverage on the rest of the project.)

1. **Schumann-envelope modulation depth vs cortical entrainment** — what envelope frequency band and modulation index produce maximum theoretical entrainment, given Pan-Tompkins-detectable HRV signatures.
2. **Caduceus coil mutual-cancellation completeness** — analytic far-field null, near-field non-null, ratio.
3. **Group-coherence amplification scaling** — $N$-wearer coherent ensemble, expected SNR vs $N$, assuming uncorrelated noise floors.
4. **SAR ceiling for Mk0.5 bifilar emitter at 1 mW total** — closed-form upper bound vs ICNIRP 2020 head limit.

## Format for every derivation

```markdown
# <Title>

## Claim
One sentence. Quantitative.

## Setup
Geometry diagram + variable list + units + assumptions.

## Derivation
Step-by-step. KaTeX inline ($...$) and block ($$...$$). Comment each step.

## Result
Final closed form, boxed.

## Numerical example
Project-relevant parameter values plugged in.

## Falsification hook
Which F-row tests this. Or "needs new F-row, proposed: ..."

## Notebook
Link to `notebooks/<slug>.ipynb` (Track D).

## Sources
- (a) consensus
- (b) wiki
- (c) extrapolated — flagged with reasoning shown.
```

## Acceptance criteria per derivation

1. Reproducible by hand to 2 sig figs.
2. Paired notebook produces the same numerical values to floating-point.
3. Result is referenced in at least one F-row in `docs/falsification.md`.
4. PDF-ready: clean KaTeX, no broken refs.

## What ships

One derivation per landing, separate commit each. First commit:

```
docs/derivations/README.md
docs/derivations/bifilar_near_field_enhancement.md
```
