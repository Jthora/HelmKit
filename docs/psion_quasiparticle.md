# Psion — the quasiparticle of the ψ-field

This is the **engineering-canonical** definition of the psion and the cluster of objects that follow from it: the Psi Field as a classical-field configuration, the psi-phonon polariton as the hybrid acoustic-psionic excitation in tissue, and the diagrammatic structure that ties all of this to mainstream physics.

It is the companion to [`docs/psionics_field_theory.md`](psionics_field_theory.md) (which lays out the Lagrangian) and to [`docs/falsification.md`](falsification.md) (which lays out what would refute it). Where this document and either of those diverge, **the Lagrangian wins** — this page is forced by the math already on the Lagrangian page; it is not new physics, it is a finished naming pass.

> **Build-side discipline.** Nothing in this document moves the Mk1 build plan, the safety architecture, the BOM, or the operator-facing claim language. It changes only the internal engineering and theory vocabulary, and it sharpens the falsifiers. See §7 for the firewall.

---

## 1. Definitions

### 1.1 Psion

**Psion** *(n.)* — the quantum of the ψ-field.

- Real, neutral, massive scalar boson.
- Spin-0.
- Self-conjugate (its own antiparticle).
- Mass $m$ ; empirically open, bounded above by Yukawa-range arguments on biological-scale interaction lengths.
- Self-coupling $\lambda$ ; required non-zero for the soliton solutions of [`Soliton Solutions of Psi Field`](https://wiki.fusiongirl.app/wiki/Soliton_Solutions_of_Psi_Field).
- Electromagnetic coupling $\alpha$ via the vertex $\alpha\,\psi\,F_{\mu\nu}F^{\mu\nu}$.
- Carries no conserved charge. Single-psion production and absorption are kinematically allowed.
- Falsification bound $\alpha \lesssim 10^{-10}\,e$ (see [`docs/falsification.md`](falsification.md) F10).

### 1.2 Psi Field

**Psi Field** *(n.)* — the classical-field configuration $\psi(x,t)$ of the underlying quantum field, i.e. a coherent state of many psions.

The relationship between "Psi Field" and "psion" is identical to the relationship between "electromagnetic field" and "photon": one object, two complementary descriptions. Operator-facing wiki pages may speak of *the field*; theory pages quantize it and speak of *the psions*. Both are correct simultaneously.

This is the load-bearing reframe of the wiki's earlier ambiguous "subtle-energy" language: a Psi Field configuration is now a *coherent state in a specific Hilbert space*, not a metaphor.

### 1.3 Psi-phonon polariton

**Psi-phonon polariton** *(n.)* — the hybridized eigenstate of the coupled (psion + acoustic-phonon) system in tissue, mediated by virtual photons through the $\alpha\,\psi\,F^2$ and thermoelastic ($\gamma F^2 P$) vertices.

This is the **observable face of psion–EM coupling in tissue**: a Frey-effect-class pulse is partially a psion excitation, partially a longitudinal pressure wave, and the true eigenstates are mixed in the same way a phonon-polariton in a polar crystal mixes a phonon and a photon.

See [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md) for the empirical face of this object.

### 1.4 Pressure-wave / "psi" etymology

The etymological linkage between *ψυχή* (psyche, "breath / pressure / animating principle") and the pressure-wave aspect of the psi-phonon polariton is **defensible as a description of the dominant observable channel in tissue**, but is not a physical identity. The pressure field is a scalar field; pressure waves in tissue are longitudinal in geometry; the symbol $\psi$ is a wavefunction-class symbol in physics. These three statements are consistent and the wiki may use the pressure framing in plain-language passages, but every technical page must use $\psi$ for the quantum field and $P$ for pressure. Conflation is forbidden.

---

## 2. The vertex catalog

The ψ-Lagrangian from [`docs/psionics_field_theory.md §1`](psionics_field_theory.md) yields a small fixed set of fundamental interaction vertices. Listing them explicitly so that wiki refactors and downstream physics arguments can name the diagram they invoke:

| Vertex | Term | Meaning |
|---|---|---|
| 4-psion self-interaction | $\tfrac{\lambda}{4}\psi^4$ | Soliton-binding; superradiant $N^4$ scaling. |
| ψ–photon–photon | $\alpha\,\psi\,F_{\mu\nu}F^{\mu\nu}$ | Primakoff-class: photons ↔ psions in an EM background. |
| ψ–consciousness (EFT) | $g_1 C\psi,\; g_2 C\psi^2,\; g_3 C^2\psi,\; g_4 C^2\psi^2$ | Indirect EM ↔ $C$ channel. |
| Direct CEMI | $g_F\,C\,F_{\mu\nu}F^{\mu\nu}$ | McFadden CEMI; direct EM ↔ $C$ channel. |
| Intentional source | $J_\psi\,\psi$ with $J_\psi = \beta\,\Phi(x,t)$ | Intention-density as ψ source. Mk0–Mk1 explicitly **not** an amplification path. |
| Thermoelastic (added by the medium) | $\gamma\,F^2 P$ | Mainstream physics; the Frey channel. |
| ψ–phonon (induced, hybrid) | $\eta\,\psi\,P$ | Derived; consequence of $\alpha\psi F^2$ and $\gamma F^2 P$ sharing the EM intermediary. |

The first five are wiki-canonical. The sixth and seventh formalize what the user's "psi = pressure" insight pointed at: once you accept the Lagrangian *and* you accept thermoelastic conversion (which is mainstream), the hybrid coupling is forced.

---

## 3. The axion analogy

The vertex $\alpha\,\psi\,F^{\mu\nu}F_{\mu\nu}$ has the diagrammatic structure of the **axion-photon coupling** in QCD-axion / ALP (axion-like-particle) physics. This is not a coincidence; it is a generic feature of any scalar coupled to gauge fields at lowest order.

Consequences:

1. **Falsifier F10 is an axion-class bound.** Reading $\alpha \lesssim 10^{-10}\,e$ in haloscope language: the psion sits in the same exclusion-plot regime as ALP searches. The wiki inherits decades of methodology from ADMX, ALPS, OSQAR, CAST, IAXO.
2. **Primakoff conversion is the canonical detection mode.** A photon in a strong static field can convert to a psion (production) and back (detection). This is *the* falsifiable single-vertex test, and it is what a future Mk3+ haloscope-style scanner would implement.
3. **Mass is unconstrained at low values.** Low-mass psions are long-lived against decay to two photons ($\tau \sim 1/\alpha^2 m^3$ in natural units, astronomically long at axion-class $\alpha$ for sub-eV $m$). For biological-scale Yukawa ranges, $m \lesssim 1\ \mu\text{eV}/c^2$ is a natural envelope.

This is the framework's bridge to mainstream particle physics. **Use it.**

---

## 4. Quasiparticle map

For wiki-side and engineering-side reading consistency, the canonical quasiparticle map:

| Quasiparticle | Quantum of | Family analogue |
|---|---|---|
| Photon | EM field $A_\mu$ | — |
| Phonon | lattice / acoustic displacement | — |
| Psion | ψ-field | **Scalar boson; axion-class.** |
| Phonon-polariton | photon ⊗ phonon (in polar dielectrics) | — |
| Psi-polariton | photon ⊗ psion (via $\alpha\psi F^2$) | **In an EM cavity.** |
| Psi-phonon polariton | photon ⊗ psion ⊗ phonon (in tissue) | **In a thermoelastic medium.** |
| Psion-soliton | many-psion semi-classical bound state | Q-ball / non-topological soliton. |

The last three rows are the new namespace pieces. The wiki's [`Glossary of Psionics`](https://wiki.fusiongirl.app/wiki/Glossary_of_Psionics) should adopt this table verbatim.

---

## 5. What "Psi Field coherence" means after this

Promoting ψ from "subtle energy" to "real quantum field with named quantum" makes every coherence claim on the wiki suddenly inherit the machinery of quantum optics:

- **First-order coherence** $g^{(1)}(\tau)$: phase memory of the ψ-field. Already implicit in the wiki's resonance arguments.
- **Second-order coherence** $g^{(2)}(0)$: photon-statistics analogue. $g^{(2)}(0) = 1$ ⇒ coherent (laser-like); $> 1$ ⇒ thermal; $< 1$ ⇒ genuinely quantum (anti-bunched). **This is a falsifiable property** of any putative ψ-source.
- **Dicke superradiance** of psions: the wiki's $N^2$ amplitude / $N^4$ intensity claim for coherent multi-operator sources is now derivable, not postulated. Same theorem as photon superradiance.
- **Coherent-state representations**: a "trained focused state" sourcing a Psi Field becomes mathematically a Glauber-class coherent state of psions, with displacement parameter $\alpha_\psi \propto \langle J_\psi \rangle$ in the appropriate frame.

The wiki's [`Resonant Pipeline`](https://wiki.fusiongirl.app/wiki/Resonant_Pipeline) and [`Psi Mesh`](https://wiki.fusiongirl.app/wiki/Psi_Mesh) become **theorems** of psion quantum optics rather than postulates. That is a structural upgrade.

---

## 6. What stays the same

This refactor changes vocabulary and sharpens theory. It does not change:

- The Mk1 build plan, hardware, BOM, or safety architecture. The dual-MCU four-belt safety model is hypothesis-agnostic; it applies to any stim driver under any mechanism hypothesis.
- The F1–F10 falsifiers. F10 becomes more recognizable as an axion-class bound; the others read the same.
- The marketing / operator-facing claim discipline. The Stabilizer is sold on its mainstream-supported HRV-biofeedback effect, full stop. Psion language is **internal engineering language**, never user-facing.
- The wiki's explicit Mk0–Mk1 caution that "Psi-Tech does not amplify intention to macroscopic effect" — preserved verbatim wherever it appears.

---

## 7. Build-side firewall

The psion vocabulary may appear in:

- This document.
- [`docs/psionics_field_theory.md`](psionics_field_theory.md).
- [`docs/falsification.md`](falsification.md).
- [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md).
- [`docs/wiki_refactor_brief.md`](wiki_refactor_brief.md).
- Future Mk2+ theoretical pages explicitly marked as such.

It **must not** appear in:

- [`docs/mk1_buildplan.md`](mk1_buildplan.md) outside the §4.0 three-layer pass/fail model's Layer-3 disclaimer.
- [`docs/safety.md`](safety.md).
- Operator manuals, user-facing pages, or marketing copy at any Mk-level we are currently shipping.
- Any pre-registration document for an Mk1 study. Pre-registered endpoints are stated in physiological language (HRV RMSSD, EEG alpha-band coherence, etc.), full stop.

The firewall exists because the psion picture, while internally well-formed, is at axion-class coupling: **Mk1 does not measure psions and could not even in principle given thermal noise floors**. Any claim that conflates internal theory vocabulary with what the device demonstrates is a violation of the wiki's own Mk0–Mk1 caution and of this firewall.

---

## 8. What Mk1 *can* engage

Nothing of psion physics directly. Mk1's purpose is the L1 + L2 gates from [`docs/mk1_buildplan.md §4.0`](mk1_buildplan.md):

- **L1** — apparatus does what it claims, mechanically.
- **L2** — apparatus produces a measurable physiological effect above blinded sham at $n \geq 30$.

A Mk1 L2 pass does not engage F1–F10. It does, however, license Mk1.5 / Mk2 work, where the psion picture becomes empirically reachable in two specific places:

1. **Mk1.5 (H2 path)**: matched-$F^2$ comparison of magnetic-near-field (H1) vs pulsed-GHz Frey-class (H2) emitters. A divergence at matched $F^2$ would be the first empirical signature of the hybrid psi-phonon channel. See [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md).
2. **Mk2 (F4 / F7 instrumentation)**: precision $\alpha$ measurement via Primakoff-class device-emission detection. See [`docs/falsification.md`](falsification.md) F4 and F7.

Mk3 is where direct psion-channel claims become operationally possible at all, and even then only at multi-operator population-study scale (F1, F2) or via a haloscope-class device (a new F11 candidate; see §10).

---

## 9. Two-channel discipline

Every claim about "EM affects consciousness" or "consciousness affects EM" must specify which channel:

- **Direct (CEMI) channel.** $g_F\,C\,F^2$. McFadden 2002. EM field is part of the substrate of $C$; consciousness reads/writes EM directly.
- **Indirect (psion-mediated) channel.** $\alpha\,\psi\,F^2$ × $g_2\,C\psi^2$. EM sources psions; psions couple to $C$.

These are not the same channel. They predict different functional forms, different scaling with $F^2$, and different correlation structures with intentionality. The wiki and this repo must distinguish them in every technical sentence. Hand-wavy "the field affects consciousness" is forbidden in new writing.

This is also where the user's question about V2K / microwave-hearing literature finds its proper home: the *acoustic* response is dominantly the Frey ($\gamma F^2 P$) channel; the *subjective* response may have a small psion-mediated component via $g_2 C\psi^2$. Same input, two channels, two predictions, one of which is well-measured and one of which is at axion-class strength. Honesty about which is which.

---

## 10. New falsifier candidate: F11

**F11 (candidate)** — In a haloscope-class RF cavity tuned to a candidate psion mass $m$ in a strong static $B$ field, single-photon excess (or deficit) at the Primakoff conversion rate predicted by $\alpha$ from independent device-emission measurement, at $> 5\sigma$.

- Disconfirms: the framework's claim that $\alpha \neq 0$ in our universe.
- Disconfirmed by: a null at sensitivity below the existing F10 bound across a contiguous mass range — i.e., a haloscope sweep that pushes $\alpha < 10^{-12}\,e$ over $\mu\text{eV}$-class masses.
- Status: **far out of scope for HelmKit Mk1 / Mk2 / Mk3.** This is a Mk4+ or external-collaboration target. Listed here so the falsifier table is complete; not pursued by this repo at any scheduled milestone.

The Falsification page in the wiki should add F11 with this exact framing.

---

## 11. GEM extension (placeholder)

Gravitoelectromagnetism (GEM), the weak-field linearisation of general relativity, admits a coupling

$$\mathcal{L}_{\psi G} = -\alpha_G\,\psi\,R_{\mu\nu}R^{\mu\nu}$$

by analogy with the EM coupling. The strength $\alpha_G$ would be suppressed relative to $\alpha$ by approximately the ratio of gravitational to electromagnetic forces (~$10^{-40}$), placing any GEM-mediated psion process far below practical detectability in a wearable device.

GEM is the natural home of any future engagement with the Penrose–Hameroff Orch-OR "gravitationally-induced collapse" framework. It is a Mk3+ theoretical placeholder; **not pursued at any current Mk-level**. Documented here so the wiki refactor has a place to file the symbol.

---

## 12. See also

- [`docs/psionics_field_theory.md`](psionics_field_theory.md) — the Lagrangian and its parameters.
- [`docs/falsification.md`](falsification.md) — F1–F10 (+F11 candidate).
- [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md) — empirical face of the psi-phonon polariton.
- [`docs/wiki_refactor_brief.md`](wiki_refactor_brief.md) — per-page manifest for the wiki-curator agent.
- [`docs/mk1_buildplan.md`](mk1_buildplan.md) §4.0 — three-layer pass/fail.
- [`docs/wiki_synthesis.md`](wiki_synthesis.md) — engineering translation of the wiki.

### Wiki anchors

- [`Psi Field`](https://wiki.fusiongirl.app/wiki/Psi_Field)
- [`Quantization of the Psi Field`](https://wiki.fusiongirl.app/wiki/Quantization_of_the_Psi_Field)
- [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness)
- [`Soliton Solutions of Psi Field`](https://wiki.fusiongirl.app/wiki/Soliton_Solutions_of_Psi_Field)
- [`Renormalization of Psi Theory`](https://wiki.fusiongirl.app/wiki/Renormalization_of_Psi_Theory)
- [`CEMI Field Theory`](https://wiki.fusiongirl.app/wiki/CEMI_Field_Theory)
- [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source)
- [`Glossary of Psionics`](https://wiki.fusiongirl.app/wiki/Glossary_of_Psionics)
- [`Falsification Criteria for Psionics`](https://wiki.fusiongirl.app/wiki/Falsification_Criteria_for_Psionics)
