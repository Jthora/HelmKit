# Wiki Anchors — Where the HelmKit design draws from the FusionGirl corpus

The FusionGirl wiki (referenced through the psiStabilizer submodule's `docs/fusiongirl_dump/` corpus) is used here as a **design source**, not as evidence. This document records which wiki pages anchor which HelmKit design decisions, and what the corresponding **real-world parallel** is.

The "Game Tech → Real-World Parallel" mapping below is lifted from the wiki's own `Psi Tech` page (pageid 541), which explicitly does this mapping itself. The HelmKit Mk1 design follows the real-world side of that mapping. The wiki side stays as long-horizon design intent for Mk2/Mk3.

---

## 1. Primary anchor: HelmKit (pageid 542) + Helm Kit (pageid 473)

The wiki defines a HelmKit as a **non-enclosed psionic headpiece** with three functions:

| Wiki function | HelmKit Mk1+ interpretation | Real-world parallel |
|---|---|---|
| Psionic sensory enhancement | Multi-channel neural / biometric / ambient EM sensing | OPM-MEG (wearable brain magnetometer); EEG; ambient RF survey |
| Magnetogravitic bubble (head protection) | Not Mk1. Not Mk2. Possible Mk3 framing as a layered **EM-shielded** + **active counter-field** zone around the head, fed by a Defender module. | EM shielding + active noise cancellation of ambient fields |
| PsiSys interface (HUD + neural feed) | Mk2+ HUD optic on `HP-F` hardpoint; Mk2+ closed-loop entrainment as a thin neural feedback channel. | HMD waveguide combiner; closed-loop neurofeedback |

The wiki's own infobox calls the HelmKit "Non-enclosed psionic headpiece" with hair-as-antenna and a magnetogravitic bubble. The hair-as-antenna framing is *not* engineered for; it is the wiki's color. The bubble framing is reduced to "layered EM shielding + active cancellation" in any generation that actually pursues it.

---

## 2. Stabilization anchor: Psi Stabilizers (pageid 474)

The wiki distinguishes:
- **Internal** stabilization (wearer's own neural state)
- **Local** stabilization (immediate area)
- **External** stabilization (projected at range)

For Mk1, **internal** stabilization is the *only* mode in scope. This maps to the psiStabilizer A01 program: measurement + entrainment, on the wearer, for the wearer.

Local / external stabilization (projecting fields beyond the wearer) is deferred indefinitely and gated behind the safety posture in [safety.md](safety.md).

---

## 3. System bus anchor: PsiLink (pageid 4529) + Psi Emitter (pageid 4538)

The wiki describes a **mesh** of Psi Emitters connected via PsiLink, with each emitter both processing locally and acting as an antenna. The architectural lift from this:

| Wiki concept | HelmKit Mk1+ interpretation |
|---|---|
| Mesh of Psi Emitters | Multiple module slots on the frame, each with its own electronics, all on a shared bus |
| PsiLink protocol | The L2 bus + per-hardpoint addressing (see [architecture.md §2.3](architecture.md#23-electrical-contract-l2-bus)) |
| Each emitter is both node and antenna | Mk2+ modules may both sense and emit at the same hardpoint (e.g., temple boom doing both magnetometry and pulsed-magnetic entrainment) |

The wiki's "PsiSys" framing as a distributed ASI is not modeled in firmware; it stays as a long-horizon scoping for the analysis layer.

---

## 4. Defense anchor: Psionic Defenses (pageid 4512)

The wiki's 9-layer defense architecture is interesting; the HelmKit takes only one slice of it (layer 7, "Operator Protection — HelmKit") and reads it as: **the HelmKit is the wearable layer; everything else is environmental and lives in the Psi Defender repo, not here.**

The sister-repo split:
- **psiStabilizer** ←→ wiki layers 6 (Field Stabilization) and 8 (Recovery / Harmonizer)
- **psionicDefender** ←→ wiki layers 1–5 (Early Warning, Area Exclusion, Active Interception, Passive Shield, Network Protection)
- **HelmKit (this repo)** ←→ wiki layer 7 (Operator Protection) + the physical platform that hosts modules from the other two

---

## 5. What the wiki is **not** used for

- The wiki is not evidence. No claim about wearer outcome is justified by a wiki quote.
- The wiki's frequency / waveform suggestions, where they exist, are not adopted without an independent literature trail. The Mk1 modality menu in [mk1_buildplan.md](mk1_buildplan.md) is built from real-world neuromodulation literature, not from in-world lore.
- The wiki's mythos (Clan Tho'ra, Jane Tho'ra, the Natura franchise) is project flavor and does not enter the BOM, the firmware, or the safety posture.

---

## 6. How to consult the wiki

The full wiki corpus is in the psiStabilizer submodule:
- Raw batches: `external/psiStabilizer/docs/fusiongirl_dump/batch_*.json`
- Curated extracts: `external/psiStabilizer/docs/wiki_extracts/`
- Engineering dossier: `external/psiStabilizer/docs/fusiongirl_psi_engineering_dossier.md`

The wiki also exposes a live MediaWiki API at https://wiki.fusiongirl.app/api.php (MediaWiki 1.41.0, fully open query). For a one-off page lookup the simplest call is:

```
https://wiki.fusiongirl.app/api.php?action=query&format=json&prop=revisions&rvprop=content&rvslots=main&redirects=1&titles=Psi%20Stabilizer
```

Relevant pageids for HelmKit-specific consultation:

| pageid | Title | Used in |
|--------|-------|---------|
| 542 | HelmKit | All |
| 473 | Helm Kit (alias) | — |
| 540 | The HelmKit (redirect-ish stub) | — |
| 474 | Psi Stabilizers | architecture, anchors |
| 541 | Psi Tech (real-world parallel table) | All |
| 4538 | Psi Emitter | wiki_synthesis |
| 4529 | PsiLink | anchors |
| 552 | PsiSys | anchors |
| 4516 | Holo Projectors | — |
| 4512 | Psionic Defenses | anchors |
| 151 | Psionics | wiki_synthesis |
| 152 | Psi Field | wiki_synthesis |
| 159 | Tho'ra Tech | — |

Additional pages consulted for [`wiki_synthesis.md`](wiki_synthesis.md) (pageids not enumerated here; titles are stable):

- `HelmKit Architecture` — dual-MCU checker-doer pattern (anchors [`architecture.md` §3](architecture.md#3-safety-architecture-dual-mcu)).
- `Psi-Tech` — triad shares one substrate, signal-pattern differs.
- `Psi Stabilizer`, `Psi Harmonizer`, `Psi Defender` — per-module functional spec.
- `Scientific Foundations of Psionics` — peer-reviewed citation roster (Dotta 2012, Tang & Dai 2014, Celardo 2019, Kalra 2023, Zarkeshian 2018, Roth 2023, Rea 2021, Bok 2024, Utts 1996, Hameroff & Penrose 2014, Schumann 1952, US Patent 3,951,134).
- `Schumann Resonance` — 7.83 Hz default Mk1 entrainment target.
- `Michael Persinger` — Mk1 apparatus precedent (microtesla complex-waveform, temporal lobe solenoids).
- `Tho'ra Tech Maturity Levels` — Mk0→Mk3 convention; "mission-live = triad@Mk1 + Resonant Finder@Mk2" milestone.
- `Tho'ra Mission Doctrine` — consent / shield-not-sword / disengage-on-instability / astrology-rules / transparency.
- `Psi Scanner`, `Psi Ward`, `Neural Firewall` — Mk2+ scoping for sensing, area-shielding, and comms-layer security.

### Pages added in Pass 2 (2026-05-12 wiki content drop)

These pages were published or substantially rewritten on 2026-05-12 and feed [`wiki_synthesis.md` § Pass 2](wiki_synthesis.md#pass-2--2026-05-12-wiki-content-drop), [`psionics_field_theory.md`](psionics_field_theory.md), [`falsification.md`](falsification.md), and the §3.6 connector/bus spec in [`architecture.md`](architecture.md):

**Hardware specs (Mk1+ design anchors):**

- [`Bifilar Coil`](https://wiki.fusiongirl.app/wiki/Bifilar_Coil) — Tesla series-opposing geometry; Mk1 emitter choice.
- [`Caduceus Coil`](https://wiki.fusiongirl.app/wiki/Caduceus_Coil) — opposite-chirality helices, far-field cancellation; Mk2 alt.
- [`Double-Helix Antenna`](https://wiki.fusiongirl.app/wiki/Double-Helix_Antenna) — same-chirality axial-mode CP; Mk3 platform-radiator option.
- [`Near Field Electromagnetics`](https://wiki.fusiongirl.app/wiki/Near_Field_Electromagnetics) — reactive vs Fresnel vs far-field zone formulas.
- [`Reactive Near Field`](https://wiki.fusiongirl.app/wiki/Reactive_Near_Field) — E×H reactive Poynting, $r < 0.62\sqrt{D^3/\lambda}$, $1/r^3$ scaling.
- [`Antenna Theory for Psionic Devices`](https://wiki.fusiongirl.app/wiki/Antenna_Theory_for_Psionic_Devices) — Chu-Harrington Q bound, Wheeler $R_\text{rad}$, body detuning.
- [`SAR Calculation for Psionic Devices`](https://wiki.fusiongirl.app/wiki/SAR_Calculation_for_Psionic_Devices) — $\text{SAR}=\sigma|E|^2/\rho$, brain $\sigma=1.81$ S/m, ICNIRP 2 W/kg ceiling, FDTD requirement.
- [`Psionic Device Safety`](https://wiki.fusiongirl.app/wiki/Psionic_Device_Safety) — 12-row safety blacklist (in OTP fuses on MCU-B).
- [`Psionic Device Overview`](https://wiki.fusiongirl.app/wiki/Psionic_Device_Overview) — emitter family map.

**Field theory (feeds [`psionics_field_theory.md`](psionics_field_theory.md)):**

- [`Psi Field`](https://wiki.fusiongirl.app/wiki/Psi_Field) — canonical Lagrangian, $\Psi \equiv T^{00}(\psi)$, $J_\psi$ definition.
- [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness) — $C$ order parameter + 5-coupling effective theory; phase diagram including runaway regime.
- [`Quantization of the Psi Field`](https://wiki.fusiongirl.app/wiki/Quantization_of_the_Psi_Field).
- [`Soliton Solutions of Psi Field`](https://wiki.fusiongirl.app/wiki/Soliton_Solutions_of_Psi_Field).
- [`Renormalization of Psi Theory`](https://wiki.fusiongirl.app/wiki/Renormalization_of_Psi_Theory).
- [`CEMI Field Theory`](https://wiki.fusiongirl.app/wiki/CEMI_Field_Theory) — sub-case of EFT $g_F C F^2$ coupling.
- [`Intention as Psi Source`](https://wiki.fusiongirl.app/wiki/Intention_as_Psi_Source) — $J_\psi = \beta\Phi$, $\beta\sim10^{-40}$, Mk0/Mk1 not amplifying intention.
- [`Glossary of Psionics`](https://wiki.fusiongirl.app/wiki/Glossary_of_Psionics) — plain-language symbol/term lookup.

**Methodology (feeds [`falsification.md`](falsification.md)):**

- [`Falsification Criteria for Psionics`](https://wiki.fusiongirl.app/wiki/Falsification_Criteria_for_Psionics) — F1–F10 with current-status notes.
- [`Open Questions in Psionics`](https://wiki.fusiongirl.app/wiki/Open_Questions_in_Psionics).
- [`Psionic Threat Model`](https://wiki.fusiongirl.app/wiki/Psionic_Threat_Model) — five threat classes; mirrors the safety blacklist.
- [`Psionics Primer`](https://wiki.fusiongirl.app/wiki/Psionics_Primer), [`Psionics FAQ`](https://wiki.fusiongirl.app/wiki/Psionics_FAQ).

**Biology + biomarker pages (cited but not yet ingested in detail):**

- [`Resonant Neurobiology`](https://wiki.fusiongirl.app/wiki/Resonant_Neurobiology), [`Heart Rate Variability and Psi`](https://wiki.fusiongirl.app/wiki/Heart_Rate_Variability_and_Psi), [`Geomagnetic Sensitivity in Humans`](https://wiki.fusiongirl.app/wiki/Geomagnetic_Sensitivity_in_Humans).
- [`Microtubule`](https://wiki.fusiongirl.app/wiki/Microtubule), [`Orchestrated Objective Reduction`](https://wiki.fusiongirl.app/wiki/Orchestrated_Objective_Reduction), [`Biophotons`](https://wiki.fusiongirl.app/wiki/Biophotons).
- [`Dotta Saroka Persinger 2012`](https://wiki.fusiongirl.app/wiki/Dotta_Saroka_Persinger_2012), [`Celardo Microtubule Superradiance`](https://wiki.fusiongirl.app/wiki/Celardo_Microtubule_Superradiance), [`Kalra Anaesthetic Microtubule`](https://wiki.fusiongirl.app/wiki/Kalra_Anaesthetic_Microtubule), [`Bandyopadhyay Microtubule Conductance`](https://wiki.fusiongirl.app/wiki/Bandyopadhyay_Microtubule_Conductance) — primary-paper citation-anchor pages.

