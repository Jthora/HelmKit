# Wiki refactor brief — psion quasiparticle propagation

**Audience:** the AI agent responsible for curating the [FusionGirl wiki](https://wiki.fusiongirl.app/) psionics pages.

**Purpose:** propagate the psion-as-quasiparticle ontology established in [`docs/psion_quasiparticle.md`](psion_quasiparticle.md) across every wiki page that talks about the ψ-field, while preserving the existing Lagrangian, the F1–F10 falsifiers, and the operator-facing claim discipline.

**Source of truth.** When this brief and any wiki page conflict, the brief wins until the wiki page is updated. When this brief and [`docs/psion_quasiparticle.md`](psion_quasiparticle.md) conflict, that document wins. When *that* document and [`docs/psionics_field_theory.md`](psionics_field_theory.md) conflict, the Lagrangian wins.

---

## 1. Propagation rules — invariants the curator must check on every edit

1. **Lagrangian-as-canon.** Any plain-language description of ψ that contradicts the Lagrangian in [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness) must be edited to match the Lagrangian. Never edit the Lagrangian to match a vague page.
2. **Psion as canonical particle name.** First mention of the ψ-quantum on any page links to [`Psion`](https://wiki.fusiongirl.app/wiki/Psion). No competing names ("psi-quantum", "ψ-particle", "intent particle", "psyon", etc.) introduced without explicit alias-flag back to "psion".
3. **Two-channel discipline.** Any sentence asserting EM ↔ consciousness coupling must specify which channel: **direct** ($g_F\,C\,F^2$, CEMI) or **indirect** ($\alpha\,\psi\,F^2$ → $g_2\,C\,\psi^2$, psion-mediated). Hand-wavy "the field" is forbidden in new writing; existing hand-wavy passages get a `{{needs-channel-spec}}` template.
4. **Quasiparticle ontology.** Where the wiki invokes "vibrations / oscillations / waves of psi," the curator must annotate whether the referent is the classical field $\psi(x,t)$ or the quantum quasiparticle (psion), and if it's the hybrid in tissue, link to [`Psion-Phonon Coupling in Tissue`].
5. **Axion-analogy footnote.** Every page that quantifies $\alpha$ footnotes that $\alpha\psi F^2$ has the diagrammatic structure of the axion-photon coupling, with link to the haloscope / light-shining-through-walls experimental programs (ADMX, ALPS, OSQAR, CAST, IAXO).
6. **Marketing-claim firewall.** Any operator-facing or user-facing page describing a *device function* must restrict its claim language to what the relevant Mk-level can actually demonstrate. Psion-mediated effects **do not** appear in Mk1 operator manuals. They may appear in theoretical pages with an explicit `{{mk-target|Mk2+}}` label.
7. **Falsifier coverage.** Every new theoretical claim must either (a) cite an F-criterion it engages, or (b) state explicitly that it is currently unfalsifiable, tagged `{{unfalsifiable-pending-instrumentation}}`.
8. **Symbol stability.** The canonical parameter names $m$, $\lambda$, $\alpha$, $\beta$, $g_1\ldots g_4$, $g_F$ are stable across pages. Renaming them is forbidden.

---

## 2. Per-page change manifest

Priority key: **P0** = must change before publishing anything else (terminology base). **P1** = downstream consistency. **P2** = polish.

| Page | Priority | Action |
|---|---|---|
| [`Glossary of Psionics`](https://wiki.fusiongirl.app/wiki/Glossary_of_Psionics) | **P0** | Add canonical entries: **Psion**, **Psi Field** (as classical-field configuration), **Psi-Phonon Polariton**, **Psion-Soliton**. Lift the §4 quasiparticle map verbatim. |
| [`Quantization of the Psi Field`](https://wiki.fusiongirl.app/wiki/Quantization_of_the_Psi_Field) | **P0** | Finish the quantization explicitly. Identify the quantum as the psion. State spin-0, real scalar, self-conjugate, mass $m$, coupling $\alpha$. Add canonical commutation relations and Fock-space construction sketch. |
| [`Psi Field`](https://wiki.fusiongirl.app/wiki/Psi_Field) | **P0** | Reframe lead: "the Psi Field is the classical-field aspect of an underlying quantum field whose quantum is the psion." Add coherent-state / occupation-number paragraph. Strip "subtle energy" / "vibrational" language; replace with quantum-optical analogue. |
| [`Psion`](https://wiki.fusiongirl.app/wiki/Psion) (new) | **P0** | **Create.** Body: canonical definition, quantum-number table, vertex catalog, axion comparison, decay-channel discussion, current bounds on $m$ and $\alpha$, link to all coupling pages. Use [`docs/psion_quasiparticle.md §1.1`](psion_quasiparticle.md) as the seed text. |
| [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness) | **P1** | Add §"Two-channel structure of $C$–EM coupling": explicit CEMI vs psion-mediated, with diagrammatic structure. Phase diagram unchanged. |
| [`CEMI Field Theory`](https://wiki.fusiongirl.app/wiki/CEMI_Field_Theory) | **P1** | Cross-link: "CEMI is the *direct* EM-consciousness channel; the *indirect* channel is psion-mediated. CEMI is recovered as a sub-case of the EFT." |
| [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source) | **P1** | Reframe $J_\psi = \beta\Phi$ as "intentional source of psions." **Preserve verbatim** the Mk0–Mk1 caution paragraph. |
| [`Soliton Solutions of Psi Field`](https://wiki.fusiongirl.app/wiki/Soliton_Solutions_of_Psi_Field) | **P1** | Add §"Soliton as semi-classical many-psion bound state." Cross-link Q-ball / non-topological soliton literature. Make explicit: "thought form" has a definite technical referent here. |
| [`Falsification Criteria for Psionics`](https://wiki.fusiongirl.app/wiki/Falsification_Criteria_for_Psionics) | **P1** | F10 annotated as axion-class bound. Add **F11 (candidate)**: Primakoff-conversion null search in a haloscope-style RF cavity (text in [`docs/psion_quasiparticle.md §10`](psion_quasiparticle.md)). |
| [`Psion-Phonon Coupling in Tissue`](https://wiki.fusiongirl.app/wiki/Psion-Phonon_Coupling_in_Tissue) (new) | **P1** | **Create.** Body: hybridization Lagrangian, Frey-effect citation chain, dielectric data, why 1.245 GHz earns historical anchor, SAR/ICNIRP envelope, link to H2 hypothesis. Seed text: [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md). |
| [`HelmKit Architecture`](https://wiki.fusiongirl.app/wiki/HelmKit_Architecture) | **P1** | Add note: "Near-field bifilar / caduceus emitter exploits the $\alpha\psi F^2$ vertex via simultaneous large $E^2$ and $B^2$. Equivalent to a low-power, biologically-coupled Primakoff converter." Mechanism unchanged. |
| [`Psi Emitter`](https://wiki.fusiongirl.app/wiki/Psi_Emitter) | **P1** | Add: "An emitter is a configured source of psions via Primakoff-class conversion in the reactive near-field." Note Mk1 operates well below any plausible non-thermal psion production threshold. |
| [`Psi Scanner`](https://wiki.fusiongirl.app/wiki/Psi_Scanner) | **P1** | Add: "A scanner is a detector for the photon-channel of psion decay (via inverse Primakoff conversion) and for the EM imprint of the ψ-field gradient." Note sensitivity gap vs axion-class bounds. |
| [`Scientific Foundations of Psionics`](https://wiki.fusiongirl.app/wiki/Scientific_Foundations_of_Psionics) | **P1** | Lead reframe: "Psionics is the study of the ψ-field and its quantum, the psion, including its couplings to EM, acoustics, and consciousness." |
| [`Renormalization of Psi Theory`](https://wiki.fusiongirl.app/wiki/Renormalization_of_Psi_Theory) | **P2** | Annotate which couplings run, which are protected. Mention $\alpha$ running as in axion-photon literature. |
| [`Resonant Pipeline`](https://wiki.fusiongirl.app/wiki/Resonant_Pipeline) | **P2** | Reframe $N^2 / N^4$ scaling as Dicke superradiance of psions. Theorem, not postulate. Mk3 target only. |
| [`Psi Mesh`](https://wiki.fusiongirl.app/wiki/Psi_Mesh) | **P2** | Same superradiance framing. |
| [`Schumann Resonance`](https://wiki.fusiongirl.app/wiki/Schumann_Resonance) | **P2** | Annotate: resonance-locked sources entail coherent-state psion emission *if* $\alpha \neq 0$, which is bounded by F10. |
| [`Psychotronics`](https://wiki.fusiongirl.app/wiki/Psychotronics) | **P2** | Annotate historical-mechanism claims with channel mapping. Frey effect → psi-phonon polariton candidate. |
| [`Psi Stabilizer`](https://wiki.fusiongirl.app/wiki/Psi_Stabilizer) | **P2** | Operator-facing. Keep HRV-biofeedback framing. Add one footnote linking to theoretical pages. **No psion language in the device claim.** |
| [`Psi Harmonizer`](https://wiki.fusiongirl.app/wiki/Psi_Harmonizer) | **P2** | Same firewall. |
| [`Psi Defender`](https://wiki.fusiongirl.app/wiki/Psi_Defender) | **P2** | Same firewall. |
| [`Psi Ward`](https://wiki.fusiongirl.app/wiki/Psi_Ward) / [`Neural Firewall`](https://wiki.fusiongirl.app/wiki/Neural_Firewall) | **P2** | Reframe defensive devices as "decoupling environments from ψ-EM mixing channels." Operator firewall applies. |

---

## 3. Verification checks — run on every edited page

- **C1.** First-mention `Psi Field` links to [`Psi Field`](https://wiki.fusiongirl.app/wiki/Psi_Field). First-mention `psion` links to [`Psion`](https://wiki.fusiongirl.app/wiki/Psion). Glossary entries exist.
- **C2.** Any sentence containing `field` + (`affects`|`couples`|`interacts`|`produces`) + (`consciousness`|`brain`|`mind`) specifies channel (direct vs indirect). Else tag `{{needs-channel-spec}}`.
- **C3.** Any device-function claim on a `Psi *` device page is bracketed by Mk-level. The page cites the Mk-level at which the claim is operator-claimable. Else tag `{{claim-firewall-violation}}`.
- **C4.** Any quantitative claim about $\alpha$, $m$, $\lambda$, $\beta$, $g_i$ is within F1–F10 bounds. Discrepancies tagged `{{bound-conflict}}`.
- **C5.** No new "subtle energy" / "vibrational" / "frequency healing" language on any page touched in this refactor. Replace with quantum-optical or coherent-state language. Older un-touched pages keep their text until they're touched.
- **C6.** Every `{{needs-citation}}` tag survives the edit unless a citation was actually added.
- **C7.** Symbol names ($m$, $\lambda$, $\alpha$, $\beta$, $g_i$, $g_F$) unchanged.

---

## 4. Ordering

The curator processes pages in this order — earlier batches are dependencies of later ones:

1. **P0 batch** — Glossary, Quantization, Psi Field, new Psion page. Establishes terminology.
2. **P1 theoretical** — EFT, CEMI, Intention, Soliton, Falsification, Psion-Phonon Coupling, Scientific Foundations.
3. **P1 architectural** — HelmKit Architecture, Psi Emitter, Psi Scanner.
4. **P2 polish** — operator-facing device pages, Schumann, Psychotronics, Resonant Pipeline, Psi Mesh, Renormalization.
5. **Verification pass** — C1–C7 on every touched page.
6. **Backlink pass** — every new term gets back-references from the canonical glossary entry; every page that cites a new term appears in the new term's "What links here."

---

## 5. Prohibitions — the curator must not

- Retcon old user-facing device claims to assert psion-mediated function.
- Delete the Mk0–Mk1 caution paragraph in [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source) or its analogues elsewhere.
- Raise $\alpha$ above $10^{-10}\,e$ anywhere. F10 is binding.
- Delete or weaken F1–F10. Sharpening wording is allowed; weakening claim strength is not.
- Rename canonical parameters ($m, \lambda, \alpha, g_i, g_F, \beta$).
- Introduce GEM-coupling language outside theoretical pages tagged `{{mk-target|Mk3+}}`.
- Conflate "psion," "phonon," and "photon" textually. The hybrid is a *polariton*, a third object.
- Add new falsifiers beyond F11 (candidate) without referencing this brief and updating [`docs/falsification.md`](falsification.md) first.
- Edit the Lagrangian to match a plain-language page. (Rule 1, restated for emphasis.)

---

## 6. Operator interaction protocol

When the curator agent encounters an ambiguous case the rules above do not cover, it must:

1. Tag the relevant page section with `{{needs-human-review|brief=wiki_refactor_brief.md}}`.
2. Log the ambiguity to its operator queue with: page URL, section, conflict description, proposed resolutions.
3. **Not** publish the ambiguous edit.

The human (or downstream review process) resolves the ambiguity and either updates this brief or instructs the agent.

---

## 7. Done criteria

The refactor is complete when:

- All P0 pages match this brief.
- All P1 pages match this brief.
- C1–C7 pass on all touched pages.
- The Glossary contains all four new canonical entries (Psion, Psi Field, Psi-Phonon Polariton, Psion-Soliton).
- The Falsification page contains F11 (candidate).
- No `{{needs-channel-spec}}` or `{{claim-firewall-violation}}` tags remain on P0 or P1 pages.
- P2 pages are scheduled but not blocking.

---

## 8. See also

- [`docs/psion_quasiparticle.md`](psion_quasiparticle.md) — the canonical theory document this brief propagates.
- [`docs/psionics_field_theory.md`](psionics_field_theory.md) — the Lagrangian.
- [`docs/falsification.md`](falsification.md) — F1–F10 (+F11 candidate).
- [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md) — empirical face of the psi-phonon polariton.
- [`docs/wiki_synthesis.md`](wiki_synthesis.md) — earlier engineering translation of the wiki; remains valid, sharpened by this refactor.
- [`docs/wiki_anchors.md`](wiki_anchors.md) — page-to-design-decision mapping.
