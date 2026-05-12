# Falsification — what would invalidate the framework

The wiki's [`Falsification Criteria for Psionics`](https://wiki.fusiongirl.app/wiki/Falsification_Criteria_for_Psionics) page enumerates ten predictions $F_1\ldots F_{10}$ whose failure would refute either the whole framework or specific components. This doc records the engineering-relevant subset and the **wiki's own statement of current evidence status** for each.

The framework, on its own terms, stands or falls on this list. The HelmKit repo's job is to (a) document which experiments engage which falsifier, and (b) **not over-claim** beyond what the current evidence supports.

---

## The ten criteria — wiki-canonical

| ID | Prediction | Disconfirms | Wiki-stated current status |
|---|---|---|---|
| **F1** | Aggregate ganzfeld effect $d > 0$ with $p < 0.001$ at $N > 10{,}000$ multi-lab preregistered. | The claim of ψ-mediated [Anomalous Cognition](https://wiki.fusiongirl.app/wiki/Anomalous_Cognition). | Storm et al. 2010 / Cardeña 2018 aggregate $d \approx 0.14$–$0.20$. **Consistent.** |
| **F2** | RV effect size independent of viewer-target distance $< 20{,}000$ km. | Massless-ψ-field claim (would imply non-$1/r$ propagation). | Star Gate corpus (Utts 1996) — no significant distance dependence. **Consistent.** |
| **F3** | Driving a coherent matter substrate at resonance produces ψ-coupling effects larger than off-resonance by ratio $Q$. | Coherent-matter enhancement of ψ-coupling. | **No published direct test at sufficient sample size.** |
| **F4** | At fixed RF input power, increasing substrate coherence (not SAR) increases ψ-output. | Coherence-dependent mechanism (would imply purely thermal). | **Pilot data only.** ← *Mk1+ instrumentation could in principle engage this.* |
| **F5** | Pharmacological microtubule disruption (taxol/colchicine/vinblastine) reduces AC effect size. | Microtubule-substrate hypothesis. | No direct test (ethical barriers). Anaesthesia studies are an indirect proxy. |
| **F6** | Anaesthesia abolishes AC effect (microtubule-mediated consciousness). | Microtubule-mediated-consciousness claim. | Indirect evidence consistent; no controlled study of autonomic-AC under anaesthesia. |
| **F7** | Same $\alpha$ from device-emission measurement and AC-detection measurement (within $3\sigma$). | The single-parameter framework. | **No precision measurement of $\alpha$ exists yet.** ← *Mk2+ could engage this.* |
| **F8** | $\lambda \psi^4$ self-coupling consistent with stable solitons. | "Thought-form" interpretation. | Theoretical work in progress. |
| **F9** | No violation of energy / momentum / charge conservation. | The framework's structure (would falsify the action principle). | No credible over-unity claim survives rigorous testing. **Consistent.** |
| **F10** | Standard-Model physics recovered as $\alpha \to 0$. | Compatibility with mainstream physics. | $\alpha \lesssim 10^{-10}$ of EM coupling — consistent with no observed Standard-Model anomaly. |

---

## Methodological floor the wiki requires

For a falsification claim to be sustained, the wiki requires:

1. Pre-registration of primary hypotheses, predictions, analyses.
2. Statistical power $\geq 80\%$ for the predicted effect.
3. Multi-lab replication (single-lab nulls not sufficient).
4. Independent verification — raw-data-level reproducibility.
5. Replication-crisis-era methodological tightness.

This is the floor every HelmKit pre-registration template inherits.

---

## What Mk1 / Mk2 / Mk3 can actually engage

Most of $F_1\ldots F_{10}$ require multi-operator population-scale studies that no Mk1 device touches. The honest list of what this repo's hardware roadmap could, in principle, contribute to:

| Falsifier | Earliest possible engagement | What it would take |
|---|---|---|
| **F3** (resonance enhancement) | Mk2 | Same emitter at on/off-resonance, identical input power, RNG / sensor cohort downstream. |
| **F4** (SAR-independence of ψ-coupling) | Mk2 with calibrated FDTD SAR map + matched coherent vs incoherent substrate. | Decouple the deposited thermal power from substrate coherence — non-trivial. |
| **F7** (universal $\alpha$) | Mk3 at earliest | Precision device-side emission measurement; matched precision AC-effect measurement on same operator. |
| **F1, F2, F5, F6** | Not Mk* device-side | Population-scale neuroscience / parapsychology lab work; HelmKit data could be a side input. |
| **F8, F9, F10** | Theoretical / cosmological | Out of repo scope. |

**Mk1's job is none of these.** Mk1's job is to land the apparatus, the safety architecture, and the validated HRV-biofeedback baseline (see [`mk1_buildplan.md` §4](mk1_buildplan.md#4-the-first-study)) so that Mk2 and beyond can engage F3 and F4 honestly.

---

## What is NOT the framework's responsibility (wiki-stated)

Per the wiki's own framing — the framework does **not** claim:

- All parapsychological claims (astrology, tarot, dowsing) are framework predictions.
- All anomalous subjective experiences are ψ-mediated.
- Metaphysical entities (souls, afterlife, theology) are inside the theory's domain.

We adopt the same scope discipline. HelmKit experiments engage one or more of $F_1$–$F_{10}$, or they make no framework-level claim at all.

---

## See also

- [`docs/psionics_field_theory.md`](psionics_field_theory.md) — the Lagrangian and EFT this list is falsifying.
- [`docs/wiki_synthesis.md`](wiki_synthesis.md) — engineering translation including Pass 2 (the wiki's 2026-05-12 content drop).
- [`docs/mk1_buildplan.md`](mk1_buildplan.md) §4 — pre-registration template inheritance.
- Wiki: [`Falsification Criteria for Psionics`](https://wiki.fusiongirl.app/wiki/Falsification_Criteria_for_Psionics).

## Primary citations from the wiki page

- Popper, K. R. (1959). *The Logic of Scientific Discovery.*
- Lakatos, I. (1970). "Falsification and the methodology of scientific research programmes."
- Utts, J. (1996). "An assessment of the evidence for psychic functioning." *JSE* 10:3.
- Mossbridge, J., Tressoldi, P., Utts, J. (2012). "Predictive physiological anticipation preceding seemingly unpredictable stimuli." *Frontiers in Psychology* 3:390.
- Cardeña, E. (2018). "The experimental evidence for parapsychological phenomena: A review." *American Psychologist* 73:663–677.
- Storm, L., Tressoldi, P. E., Di Risio, L. (2010). Ganzfeld meta-analysis.
