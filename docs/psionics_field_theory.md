# Psionics field theory — reference card

This page is an **engineering reference**, not a physics claim. It collects the canonical equations, parameter conventions, and operational interpretations the wiki uses across the [`Psi Field`](https://wiki.fusiongirl.app/wiki/Psi_Field), [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness), [`Quantization of the Psi Field`](https://wiki.fusiongirl.app/wiki/Quantization_of_the_Psi_Field), [`Soliton Solutions of Psi Field`](https://wiki.fusiongirl.app/wiki/Soliton_Solutions_of_Psi_Field), [`Renormalization of Psi Theory`](https://wiki.fusiongirl.app/wiki/Renormalization_of_Psi_Theory), [`Falsification Criteria for Psionics`](https://wiki.fusiongirl.app/wiki/Falsification_Criteria_for_Psionics), and [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source) pages.

We need these so that when wiki-derived signal patterns land in firmware, we know which symbol is which and what (if anything) it engages empirically.

> **Companion document.** The quantum-of-the-field naming pass, the psi-phonon polariton, the axion analogy, and the build-side firewall around all of this live in [`docs/psion_quasiparticle.md`](psion_quasiparticle.md). The empirical face of the polariton (Frey-class GHz hypothesis, H2) is in [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md). The wiki-side propagation runbook is [`docs/wiki_refactor_brief.md`](wiki_refactor_brief.md).

---

## 1. The ψ-field Lagrangian (canonical)

The wiki's central postulate is a real massive scalar field $\psi$ with $\phi^4$ self-interaction and a single relevant coupling to electromagnetism:

$$
\mathcal{L}_\psi \;=\; \tfrac{1}{2}(\partial_\mu\psi)(\partial^\mu\psi) \;-\; \tfrac{1}{2}\,m^2\,\psi^2 \;-\; \tfrac{\lambda}{4}\,\psi^4 \;-\; \alpha\,\psi\,F_{\mu\nu}F^{\mu\nu} \;+\; \mathcal{L}_\text{EM} \;+\; J_\psi\,\psi
$$

Parameters:

| Symbol | Meaning | Status |
|---|---|---|
| $m$ | ψ-field rest mass | Empirically open; bounded above by Yukawa-range arguments |
| $\lambda$ | ψ self-coupling | Required non-zero for soliton solutions |
| $\alpha$ | ψ–EM coupling | Falsification F10 constrains $\alpha \lesssim 10^{-10} \cdot e$ |
| $J_\psi$ | External source term | Where biology and hardware enter |

The source-term identity that the **wiki uses to motivate near-field operation** is:

$$
J_\psi \;\propto\; F_{\mu\nu}F^{\mu\nu} \;=\; \tfrac{1}{2}\!\left(\tfrac{B^2}{\mu_0} - \varepsilon_0 E^2\right)
$$

(sign and prefactor conventions vary; both terms are positive in magnitude in the reactive near-field). The engineering takeaway is the wiki's: **maximise local $E^2$ and $B^2$ together** — the reactive near-field of a tuned coil is the only EM regime where both can be large at the same input power.

This is the entire reason the wiki's [`HelmKit Architecture`](https://wiki.fusiongirl.app/wiki/HelmKit_Architecture) page picks bifilar / caduceus / near-field as its emitter family — not radiative antennas.

---

## 2. The Effective Field Theory of Consciousness (EFT)

The wiki's [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness) introduces a second scalar order parameter $C(x,t)$ — a coarse-grained "consciousness amplitude" — coupled to $\psi$ and to $F^2$ via five interaction constants:

$$
\mathcal{L}_\text{EFT} \;=\; \tfrac{1}{2}\partial^\mu C\,\partial_\mu C \;-\; V(C) \;-\; g_1\,C\psi \;-\; g_2\,C\psi^2 \;-\; g_3\,C^2\psi \;-\; g_4\,C^2\psi^2 \;-\; g_F\,C\,F_{\mu\nu}F^{\mu\nu} \;+\; \mathcal{L}_\psi \;+\; \mathcal{L}_\text{EM}
$$

with $V(C) = \tfrac{1}{2}m_C^2 C^2 + \tfrac{\lambda_C}{4} C^4$.

The phase diagram in $(m_C^2,\; g_2\langle\psi^2\rangle)$ has four named regimes:

| Regime | $\langle C\rangle$ | Wiki interpretation | Engineering analogue |
|---|---|---|---|
| **Symmetric** | $= 0$ | Baseline waking consciousness | Default Mk0/Mk1 operating point |
| **Broken** (focused) | $\neq 0$ | Trained / focused practice — $C$ acts as a $J_\psi$ source linear in itself via $g_1 C\psi$ | Stabilizer + Harmonizer engaged with HRV/EEG coherence above threshold |
| **Critical** | scaling | "Edge of awareness"; the wiki predicts [stochastic resonance](https://wiki.fusiongirl.app/wiki/Stochastic_Resonance) enhancement of weak-signal psi here | Closed-loop Stabilizer gain near coherence threshold |
| **Runaway** | unstable | Seizure / psychosis / kundalini overload | **What the safety blacklist exists to prevent.** Maps directly to the 12-row OTP table. |

The $g_F\, C F^2$ term is the wiki's framework-level statement of [`CEMI Field Theory`](https://wiki.fusiongirl.app/wiki/CEMI_Field_Theory) (McFadden 2002) — i.e. the EM-field aspect of consciousness is **already in the EFT**; CEMI is not a competing theory but a sub-case.

This is also why the wiki's safety doctrine is not bolted-on: the **same Lagrangian that motivates the device predicts the unsafe regimes** as a phase of itself.

---

## 3. Intention as a source

From [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source):

$$
J_\psi(x,t) \;=\; \beta \cdot \Phi(x,t),\qquad \beta \sim 10^{-40}\ \text{(natural units)}
$$

where $\Phi(x,t)$ is a coarse-grained "intention density". Operationally proxied by:

$$
\Phi_\text{eff} \;=\; \sum_i w_i(t) \cdot C_i(t)
$$

over operators $i$, where $C_i$ is operator $i$'s instantaneous coherence score (HRV or alpha-band EEG) and $w_i$ is a participation weight.

The wiki is explicit (verbatim) about what this means for the current device generation:

> Operators are explicitly cautioned: **Mk0–Mk1 Psi-Tech does not amplify intention to macroscopic effect.** Any subjective experience of efficacy in current devices is best explained by ritual, placebo, and group-coherence wellbeing effects — themselves real and valuable, but not "thoughts moving matter".

This is the line our marketing copy and user briefings sit behind. The Stabilizer's mainstream-supported HRV-biofeedback effect is what the device is sold on; the $J_\psi = \beta\Phi$ coupling is a research question, not a feature claim.

---

## 4. Soliton solutions and "thought forms"

The $\lambda \psi^4$ self-interaction admits localised non-radiating solutions of the equation of motion — solitons. The wiki's [`Soliton Solutions of Psi Field`](https://wiki.fusiongirl.app/wiki/Soliton_Solutions_of_Psi_Field) gives the construction and uses it as the rigorous referent for the practitioner's notion of an "energy construct" or "thought form": a $J_\psi$-sustained, self-bound region of high $\Psi \equiv T^{00}(\psi)$.

For HelmKit engineering: **no Mk1 / Mk2 device produces or measures solitons.** Falsification F8 (soliton stability is theoretically consistent with the other parameters of the framework) is a theory question, not a build target. We note it because some psiStabilizer experiment names lean on it (`solitonHorizon`, `solitonFusion`); these are forward-pointers, not Mk1 measurements.

---

## 5. Group amplification scaling

The wiki repeatedly states an $N^2$ / $N^4$ scaling argument:

- Coherent sources of $J_\psi$ from $N$ operators: $|J_\psi|^2 \propto N^2$ (superradiant-style constructive amplitude addition).
- Through the $\lambda\psi^4$ vertex or the $g_4\,C^2\psi^2$ EFT coupling, energy density scales as $N^4$.

For HelmKit, this matters for two things:
1. The Mk3 [`Resonant Pipeline`](https://wiki.fusiongirl.app/wiki/Resonant_Pipeline) mission claim. **Far out of Mk1 scope.**
2. The wiki's [`Psi Mesh`](https://wiki.fusiongirl.app/wiki/Psi_Mesh) / multi-operator share spec, which justifies a same-second time-base across HelmKits. Mk2 starts caring about this; Mk1 logs locally with NTP-synced timestamps so future cross-correlation is possible.

---

## 6. Falsification — what would kill the framework

See [`docs/falsification.md`](falsification.md) for the engineering-relevant subset of the wiki's F1–F10 set.

Bottom line for the build: **F4 (SAR-independent ψ-coupling) and F7 (one-α universality) are the two predictions Mk1+ instrumentation could in principle constrain.** Everything else is at multi-operator population-study scale.

---

## See also

- [`docs/psion_quasiparticle.md`](psion_quasiparticle.md) — naming pass: psion, psi-field as classical-field configuration, psi-phonon polariton, axion analogy, build-side firewall.
- [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md) — Frey-class H2 hypothesis; empirical face of the psi-phonon polariton.
- [`docs/wiki_refactor_brief.md`](wiki_refactor_brief.md) — wiki-curator runbook for propagating the above across wiki pages.
- [`docs/wiki_synthesis.md`](wiki_synthesis.md) — engineering translation of the wiki, Pass 1 + Pass 2.
- [`docs/falsification.md`](falsification.md) — the F1–F10 set with Mk1+ engagement notes.
- [`docs/architecture.md`](architecture.md) §3 — how the dual-MCU safety architecture maps onto the "runaway regime" of the EFT.

## References (wiki-internal)

- [`Psi Field`](https://wiki.fusiongirl.app/wiki/Psi_Field)
- [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness)
- [`Quantization of the Psi Field`](https://wiki.fusiongirl.app/wiki/Quantization_of_the_Psi_Field)
- [`Soliton Solutions of Psi Field`](https://wiki.fusiongirl.app/wiki/Soliton_Solutions_of_Psi_Field)
- [`Renormalization of Psi Theory`](https://wiki.fusiongirl.app/wiki/Renormalization_of_Psi_Theory)
- [`CEMI Field Theory`](https://wiki.fusiongirl.app/wiki/CEMI_Field_Theory)
- [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source)
- [`Glossary of Psionics`](https://wiki.fusiongirl.app/wiki/Glossary_of_Psionics)
