# H2 — ELF-modulated UHF/GHz hypothesis (Frey-class)

The empirical face of the psi-phonon polariton introduced in [`docs/psion_quasiparticle.md`](psion_quasiparticle.md). This document is the theoretical and engineering brief for **H2**, an alternative-and-parallel hypothesis to H1 (Persinger-class magnetic near-field, the current Mk1 baseline).

> **Status.** Theory and inventory brief only. **No Mk1.5 hardware is authorised by this document.** A Mk1.5 build requires (a) Mk1 L1 pass per [`docs/mk1_buildplan.md §4.0`](mk1_buildplan.md), (b) an SAR phantom and ICNIRP-compliance bench, (c) its own pre-registration. None of those are in place yet.

---

## 1. The three hypotheses, on the mechanism axis

The wiki's Mk1 → Mk2 → Mk3 progression has historically been read as a **risk-ascending ladder** on a single hypothesis. That reading was wrong. On the *mechanism* axis, the three hypotheses are siblings, not stages:

| Tag | Hypothesis | Carrier | Primary mechanism | Current Mk1 hardware probes? |
|---|---|---|---|---|
| **H1** | Persinger-class magnetic near-field | sub-MHz, complex envelopes 1–100 Hz | $B^2/\mu_0$ deposition in cortex; eddy currents; coherent magnetic perturbation of neural state | **Yes.** This is the current Mk1 baseline. |
| **H2** | Frey-class ELF-modulated UHF | 300 MHz – 3 GHz, pulse rate 1–100 Hz | Thermoelastic conversion of pulsed RF in tissue water → focused longitudinal pressure wave (psi-phonon polariton) reaching deep neural structures | **No.** Distinct emitter family. Distinct safety floor. |
| **H3** | Coherent water / microtubule | Variable; possibly THz / sub-THz | Penrose–Hameroff Orch-OR; Celardo 2019 microtubule superradiance | **No.** Far from current instrumentation. |

H1 and H2 both engage the wiki's $\alpha\,\psi\,F^2$ vertex. They differ in *which* component of $F^2$ they maximise (dominantly $B^2$ for H1, dominantly $E^2$ via radiation for H2) and in *which auxiliary channel* dominates the observable (eddy-current neural perturbation for H1; thermoelastic pressure wave for H2).

A Mk1 L2 pass on H1 does not validate H2, and a Mk1 L2 null on H1 does not invalidate H2. They are independent claims.

---

## 2. The Frey effect — primary-source anchor

The Frey effect (Frey 1962, *J Appl Physiol* 17:689–692) is the canonical mechanism for H2:

- **Carrier:** Frey's original work centred on **1.245 GHz** via waveguide/horn antenna.
- **Modulation:** ~**50 pulses/second**, perceived as buzzing, clicking, hissing, or knocking.
- **Threshold:** peak power density **< 80 mW/cm²** at the surface to elicit perception in alert subjects; average power well below thermal-damage thresholds.
- **Mechanism (Lin 1976–1980s):** thermoelastic expansion. Pulsed RF absorbed in tissue water raises local temperature by ~$\mu$K per pulse; expansion launches a pressure wave; cochlea perceives the wave as audible click.
- **Reproductions:** Guy, Lin, Foster, Elder & Chou (2003 review), and dozens of military/medical follow-ups. The effect is well-established and not contested.

**Patents in the public record:**

- **US 4,877,027** (Brunkan, 1989) — "Hearing system" via pulsed microwave at 1 GHz – 10 GHz.
- **US 3,951,134** (Malech, 1976) — "Apparatus and method for remotely monitoring and altering brain waves."
- **US 6,587,729** (O'Loughlin et al., 2003) — "Apparatus for audibly communicating speech using the radio frequency hearing effect."

These are cited as **primary-source evidence that the Frey channel is real, instrumentable, and has decades of engineering development**. They are not cited as evidence that the wiki's framework is correct; they are evidence that the *mechanism the framework needs* is well-established physics.

---

## 3. Why 1.245 GHz earns the historical anchor (and 2.45 GHz does not)

Two corrections to common lore that the wiki's earlier framing was carrying:

### 3.1 Water dielectric relaxation is not at 2.45 GHz

The Debye relaxation peak of liquid water at body temperature (310 K) sits at approximately **18–22 GHz**, not 2.45 GHz. The 2.45 GHz ISM band was chosen for microwave ovens by engineering convenience (regulated band, magnetron availability, penetration-vs-efficiency compromise), **not** because water resonates there.

Sources: Gabriel 1996 tissue dielectric tables; IT'IS Foundation tissue properties database.

Any wiki text claiming "2.45 GHz is the water-resonance frequency" must be corrected.

### 3.2 1.245 GHz earns its anchor from the Frey corpus, not from water

Frey's original 1962 experiments locked in a specific photon-to-phonon conversion efficiency at 1.245 GHz in head-sized tissue volumes. That number is the **historical reproducibility anchor** — same carrier ≈ same baseline Frey response, comparable across labs decades apart. Choosing 1.245 GHz for a Mk1.5 H2 emitter is a *citation-comparability* choice, not a physics-resonance choice.

### 3.3 Penetration depth is monotonic with frequency, not resonant

Approximate skin / penetration depths in muscle-class tissue (Gabriel 1996):

| Frequency | Penetration depth (50% power) |
|---|---|
| 100 MHz | ~10 cm |
| 300 MHz | ~5 cm |
| 900 MHz | ~3 cm |
| 1.245 GHz | ~2 cm |
| 2.45 GHz | ~1.5 cm |
| 20 GHz | ~1 mm |

Monotonic. "300–900 MHz gives deeper penetration than 2.45 GHz" is true; "1.245 GHz hits a resonance" is false. The lower-band attraction is penetration; the 1.245 GHz attraction is Frey-corpus comparability.

---

## 4. Hybridization Lagrangian (engineering reference)

The vertex catalog from [`docs/psion_quasiparticle.md §2`](psion_quasiparticle.md), restricted to the tissue-relevant subset:

$$\mathcal{L}_\text{tissue} = \mathcal{L}_\text{EM} + \mathcal{L}_\psi + \mathcal{L}_\text{acoustic} + \alpha\,\psi\,F^2 + \gamma\,F^2 P + \eta\,\psi\,P$$

where $P(x,t)$ is the local acoustic pressure field. The three coupling constants:

- $\alpha$ — wiki postulate, F10-bounded $\lesssim 10^{-10}\,e$.
- $\gamma$ — **mainstream physics**; sets the Frey-effect amplitude. Measurable (and measured) in photoacoustic literature.
- $\eta$ — induced; the consequence of $\alpha$ and $\gamma$ sharing the EM intermediary. The hybrid eigenstate of (psion + phonon) in tissue is the **psi-phonon polariton**.

**Observational implication:** a Frey pulse delivers *both* a Frey-channel pressure wave (large, well-characterized) *and*, if $\alpha \neq 0$, a small psion-mediated co-pressure (axion-class strength, unobservable in audio measurement). To isolate the psion contribution you must find an observable where the two channels predict *different* signatures. Candidates:

- Spatial pattern divergence (psion channel is not refraction-bounded the way EM is).
- Polarization / mode-mixing divergence at fluid-membrane interfaces.
- Subjective response divergence vs audiometric response (the $g_2 C \psi^2$ EFT coupling routes psion content into $C$ without going through audible acoustics).

None of these are Mk1.5-class measurements. Mk1.5 measures the *combined* pressure response and the *subjective + autonomic* response; differential analysis against H1 at matched $F^2$ is the first available divergence test.

---

## 5. Mk1.5 pre-registration sketch — **proposal only, not authorised**

The shape of a Mk1.5 study, when (and only when) Mk1 has passed L1+L2:

- **Hypothesis.** H2 (Frey-class GHz pulsed) and H1 (Persinger-class magnetic) drive the wiki's $\alpha\psi F^2$ vertex through different EM components. At matched local $F^2$ deposition in target neural tissue, the two should produce *similar* primary-endpoint effects *unless* an additional hybrid channel (psi-phonon polariton) is operationally relevant — in which case H2 outperforms H1.
- **Design.** Cross-over, sham-controlled, blinded. Three arms per subject: H1-active, H2-active, sham. Order randomized, sealed envelope.
- **Primary endpoint.** Same as Mk1: time-to-coherence on HRV RMSSD return-to-baseline under standardised stressor. Pre-registered.
- **Secondary endpoint.** EEG alpha-band coherence change, audiometric Frey-perception threshold (for H2 arm only — used to confirm dose delivery, not as endpoint).
- **Matching.** Equal $F^2$ at scalp-surface reference probe. Independently SAR-verified per arm.
- **Sham for H2.** Energized but detuned emitter (carrier off-frequency) to control for thermal placebo. Sham SAR matched to active SAR within $\pm 10\%$.
- **Sample size.** $n \geq 30$ paired sessions per arm. Power calc from Mk1 L2 result.
- **Safety floor.** All arms below ICNIRP basic-restrictions for occupational exposure at the relevant band. Hard interlock on integrated SAR per session.
- **Failure modes published.** Any direction.

This is the *shape*; pre-registration only happens after Mk1 passes and after the safety bench is verified.

---

## 6. Safety floor for H2

The Mk1.5 H2 path **raises** the safety floor above current Mk1:

| Concern | Mk1 (H1) | Mk1.5 (H2) |
|---|---|---|
| Carrier | sub-MHz | 1.245 GHz (or band-equivalent) |
| Tissue penetration | ~surface eddy currents | bulk thermal deposition |
| Standards | ICNIRP magnetic basic restrictions | ICNIRP RF basic restrictions + SAR |
| Phantom required | optional for Mk1 | **mandatory** for any Mk1.5 bench work |
| Thermal monitoring | optional | **mandatory continuous IR or fiber-optic** |
| Frey-perception baselining | n/a | per-subject perception threshold determined before any session |
| Time-integrated SAR interlock | n/a | **mandatory hard cutoff** |
| MCU-B blacklist | as Mk1 | **extended** with carrier-frequency, peak-PD, time-integrated SAR fields |
| Sham coil | as Mk1 | sham emitter (detuned, energized) |

Until every row of this table is met on bench, no H2 stim hardware powers on in the presence of a human subject.

---

## 7. Inventory match

The H2 carrier band is covered by existing inventory items already documented in [`docs/inventory_capability_map.md`](inventory_capability_map.md):

- **HackRF One** — 1 MHz – 6 GHz TX/RX, half-duplex, up to 20 MS/s. 1.245 GHz is comfortably in-band. Useful for bench characterisation and ELF-envelope generation under software control.
- **MAX2870** wideband synthesizer — 23.5 MHz – 6 GHz output. 1.245 GHz in-band. SPI-controllable. Cheap (~$30 modules).
- **ADF4351** PLL synthesizer — 35 MHz – 4.4 GHz output. 1.245 GHz in-band. SPI-controllable. Cheaper (~$15 modules).

Antenna side requires a band-appropriate horn or patch — not in current inventory. SAR phantom not in current inventory. Fiber-optic thermometer not in current inventory.

**Procurement floor for Mk1.5 H2 bench (estimate):**

| Item | Approx. cost |
|---|---|
| 1.245 GHz patch/horn antenna | $30–80 |
| SAR-equivalent tissue phantom | $200–800 |
| Fiber-optic tissue thermometer | $300–1000 |
| Calibrated RF power meter (band-appropriate) | $200–500 |
| Faraday-shielded bench enclosure | $200–600 |
| **Floor total** | **~$1k–3k** |

This is **above** the Mk1 procurement floor (~$35–55 for the MAX30102) by two orders of magnitude. That is the right order of magnitude for raising the safety floor.

---

## 8. Falsifier engagement

H2 specifically engages:

- **F3** — coherent-substrate resonance enhancement. The Frey channel *is* a coherent-substrate resonance in the thermoelastic sense. If H2 outperforms H1 at matched $F^2$, that is direct evidence for F3-style enhancement.
- **F4** — coherence-dependent (non-SAR) ψ-output. Mk1.5 with SAR-matched arms is the cleanest available test.
- **F7** — single-$\alpha$ universality. If H1 and H2 are matched on $F^2$ but produce different effects, that is *also* evidence that something beyond a single-vertex coupling is in play. F7 disconfirmation is possible.
- **F10** — recovery of Standard-Model physics at $\alpha \to 0$. Mk1.5 does not push F10. Null on H2-vs-H1 divergence is consistent with $\alpha = 0$.

H2 does **not** engage:

- F1, F2 — RV / ganzfeld population-level claims. Out of Mk1.5 scope.
- F5, F6 — microtubule / anaesthesia. Pharmacology not in scope.
- F8 — soliton stability. Theory, not measurement.
- F9 — conservation laws. Not at risk from this design.

---

## 9. Operator-claim firewall

Nothing in this document licenses operator-facing claims about psion-mediated effects, microwave hearing as a feature, or any "remote audio" capability. The H2 path, if pursued at all, is pursued as a **research instrument** with sham-controlled blinded design, exactly as Mk1 is.

The marketing-firewall paragraph from [`docs/psionics_field_theory.md §3`](psionics_field_theory.md) applies in full to any Mk1.5 device:

> Operators are explicitly cautioned: Mk0–Mk1 Psi-Tech does not amplify intention to macroscopic effect. Any subjective experience of efficacy in current devices is best explained by ritual, placebo, and group-coherence wellbeing effects.

A Mk1.5 H2 device is **still Mk1-generation Psi-Tech** for the purposes of this caution. Promotion to a higher claim-band requires a successful Mk2 study, not a successful Mk1.5 study.

---

## 10. Open questions

- **Q1.** Is the "modulation envelope is what couples to $C$" hypothesis (envelope-frequency-matters, carrier-only-as-vehicle) correct, or does the carrier choice itself bias the $\alpha\psi F^2$ vertex? Bench-resolvable with multi-carrier matched-envelope sweeps.
- **Q2.** Does the thermoelastic Frey channel saturate before the psion-mediated channel becomes detectable, or vice versa? Probably the former; design experiments to compress the Frey channel (audiometric masking, e.g.) while preserving the psion channel.
- **Q3.** Are there carrier frequencies where the psion-channel-to-Frey-channel ratio is favorable? Lin's thermoelastic theory predicts the Frey amplitude falls at low frequencies (below ~300 MHz the pulse simply doesn't deposit enough localised energy); the psion vertex has no such floor in principle. Sub-300-MHz pulsed work may have a better channel-ratio at the cost of penetration.
- **Q4.** GEM extension: is the $\alpha_G\,\psi\,R^2$ coupling relevant at any wearable scale? Per [`docs/psion_quasiparticle.md §11`](psion_quasiparticle.md), almost certainly not. Listed only to close the loop.

---

## 11. See also

- [`docs/psion_quasiparticle.md`](psion_quasiparticle.md) — theoretical foundation.
- [`docs/psionics_field_theory.md`](psionics_field_theory.md) — Lagrangian.
- [`docs/falsification.md`](falsification.md) — F1–F10, F11 candidate.
- [`docs/wiki_refactor_brief.md`](wiki_refactor_brief.md) — wiki-curator runbook.
- [`docs/mk1_buildplan.md`](mk1_buildplan.md) — Mk1 L1/L2 gates; Mk1.5 prerequisite.
- [`docs/safety.md`](safety.md) — safety doctrine; safety floor for H2 in §6 above is additive.
- [`docs/inventory_capability_map.md`](inventory_capability_map.md) — inventory match in §7 above.

### External references (primary)

- Frey, A.H. (1962). "Human auditory system response to modulated electromagnetic energy." *J Appl Physiol* 17:689–692.
- Lin, J.C. (1980). *Microwave Auditory Effects and Applications.* Charles C Thomas, Springfield IL.
- Elder, J.A.; Chou, C.K. (2003). "Auditory response to pulsed radiofrequency energy." *Bioelectromagnetics* Suppl 6:S162–S173.
- Gabriel, C.; Gabriel, S.; Corthout, E. (1996). "The dielectric properties of biological tissues." *Phys Med Biol* 41:2231–2249.
- IT'IS Foundation Tissue Properties Database (ongoing).
- ICNIRP Guidelines for limiting exposure to electromagnetic fields (100 kHz to 300 GHz), 2020.
- US Patents 4,877,027 ; 3,951,134 ; 6,587,729 (cited in §2).
