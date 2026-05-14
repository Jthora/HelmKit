# PRIOR ART DECLARATION — HelmKit™

**Document version:** 1.0
**Date of this declaration:** 2026-05-14
**Repository:** <https://github.com/Jthora/HelmKit>
**Zenodo concept DOI (always-latest):** [10.5281/zenodo.20183948](https://doi.org/10.5281/zenodo.20183948)
**Zenodo version DOI (this baseline, `v0.1-prior-art-baseline`):** [10.5281/zenodo.20183949](https://doi.org/10.5281/zenodo.20183949)
**Inventor / declarant:** Jordan Trana
**Status:** Public — intentionally non-confidential.

---

## 1. Purpose and legal basis

This document, together with the commit history of the public repository
identified above, constitutes a **defensive publication** of the HelmKit™
design, its constituent inventive elements, the associated session protocol,
the falsification programme, and the supporting theory.

Public disclosure of an invention prior to the effective filing date of any
third-party patent application bars that third party from obtaining a valid
patent on the disclosed subject matter. The applicable legal authorities
include:

- **United States — 35 U.S.C. § 102(a)(1):** "A person shall be entitled to a
  patent unless … the claimed invention was patented, described in a printed
  publication, or in public use, on sale, or otherwise available to the
  public before the effective filing date of the claimed invention."
- **United States — 35 U.S.C. § 102(b)(1)(A):** one-year inventor grace
  period for the inventor's own prior public disclosures.
- **European Patent Convention — Article 54(2):** anything "made available to
  the public" before the priority date forms part of the state of the art.
- **Patent Cooperation Treaty (PCT) Article 33(2)–(3):** same novelty and
  inventive-step bar based on publicly available prior art.
- **Berne Convention (copyright)** and **Paris Convention (industrial
  property)**: extend recognition of prior disclosure to ~180 signatory
  countries.

Each commit referenced in §3 below is a timestamped, cryptographically-hashed
public disclosure. The GitHub repository is publicly indexed and crawled;
mirror copies are preserved on Zenodo, the Internet Archive Wayback Machine,
and arXiv (theoretical documents) on the schedule described in §6.

---

## 2. Disclaimer of patent intent

The inventor and contributors **do not intend to patent** the inventive
elements listed in §3. Any future patent application by any party that
attempts to claim the listed subject matter is presumptively invalid on
grounds of anticipation (35 U.S.C. § 102) and/or obviousness (35 U.S.C.
§ 103) over the prior art established by this repository.

The AGPL-3.0-or-later and CERN-OHL-S-2.0 licenses applied to this work
contain express patent grants; any contribution to this repository carries
those grants by acceptance of the license terms. See [`LICENSE`](LICENSE).

---

## 3. Inventory of disclosed inventive elements

Each row lists an element of the HelmKit design, its first-disclosure commit
(short SHA), the commit date, and the file(s) where the element is described.
For full text and provenance, fetch the named commit from the repository.

### 3.1 System architecture

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| A1 | **HelmKit modular psionic headpiece** — 3D-printed open mounting frame with standardized hardpoints for swappable Psi-Tech modules | `d61c911` | 2026-04 | [`README.md`](README.md), [`docs/architecture.md`](docs/architecture.md), [`docs/roadmap.md`](docs/roadmap.md) |
| A2 | **Mk0 → Mk1 → Mk1.5 → Mk2 → Mk3 staged-evidence roadmap** with explicit per-Mk defining-question gates | `d61c911`, refined `e1e301d` | 2026-04 → 2026-05 | [`docs/roadmap.md`](docs/roadmap.md) |
| A3 | **Hardpoint specification** — standardized mechanical/electrical mounting points (`HP-F`, `HP-EL`, `HP-ER`, etc.) | `d61c911` | 2026-04 | [`docs/architecture.md`](docs/architecture.md) |
| A4 | **Cross-cutting principles** — eight ladder-wide invariants for every HelmKit generation | `e1e301d` | 2026-05 | [`docs/roadmap.md`](docs/roadmap.md) |

### 3.2 Dual-MCU safety architecture

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| B1 | **Dual-MCU safety architecture** — separation of stim driver (MCU-A) and safety supervisor (MCU-B) on independent supplies | `d61c911`, hardened `50167b9` | 2026-04 → 2026-04 | [`docs/architecture.md`](docs/architecture.md), [`firmware/`](firmware/) |
| B2 | **Stim-disabled-when-not-recording hardware interlock** — physical signal path that drops stim output to zero with no software in the loop when the capture loop is off | `d61c911` | 2026-04 | [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §5.1 |
| B3 | **Stim-disabled-when-not-active-phase interlock** — MCU-B confirms session-container phase = `active` AND arm = `active` before passing stim | `e1e301d` | 2026-05 | [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §5.1, [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) |
| B4 | **Safety blacklist** — firmware-level refusal of seizure-band, cardiac-coupling, and Frey-effect-band modulation patterns | `d61c911`, restated `ced11da` | 2026-04 | [`docs/wiki_synthesis.md`](docs/wiki_synthesis.md) §2.3, [`docs/safety.md`](docs/safety.md) |
| B5 | **Four-belt safety architecture** in bring-up firmware | `50167b9` | 2026-04 | [`firmware/`](firmware/) |

### 3.3 Closed-loop biofeedback floor (L0 / L1 / L2)

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| C1 | **L0 resonance-frequency breath pacer** — ~6 bpm bone-conduction audio + LED breathing cue, 4:6 inhale:exhale, integrated with stim platform | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §2 |
| C2 | **L1 closed-loop HRV-coherence biofeedback rendering** — Lomb–Scargle periodogram on 60s RR-interval window from PPG, coherence ratio LF-band / total, rendered as audio harmonic that consonates with breath tone | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §3 |
| C3 | **L2 structured 30-minute session container** — settling 3min → onboarding 2min → active 20min → closure 2min → reflection 3min state machine | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §4 |
| C4 | **Always-on biofeedback floor on both active and sham arms** — sham wearer receives identical L0+L1+L2; only stim payload differs between arms | `e1e301d` | 2026-05 | [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §0a |
| C5 | **L3 EEG neurofeedback layer** (Mk2 deferred) — alpha/theta-ratio rendered as second audio channel alongside L1 | `e1e301d` | 2026-05 | [`docs/roadmap.md`](docs/roadmap.md) Mk2 |
| C6 | **L4 state-aware container adaptation** (Mk2 deferred) — L2 phase durations branch on detected wearer arousal at session start | `e1e301d` | 2026-05 | [`docs/roadmap.md`](docs/roadmap.md) Mk2 |

### 3.4 Three-grade evaluation framework

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| D1 | **G1 / G2 / G3 independent pass-grade evaluation model** for Mk-class wearable devices | `e1e301d` | 2026-05 | [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §4.0 |
| D2 | **G1 engineering grade** — apparatus calibration + dual-MCU interlock verification + full-sensory sham-equivalence + L0/L1/L2 bench verification + valid end-to-end session ingest | `e1e301d` | 2026-05 | [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §5.1 |
| D3 | **G2 wearer-benefit grade** — 4-week within-subject ABAB or AB-BA crossover, no stressor, pre-registered composite endpoint of $\Delta$morning-RMSSD + $\Delta$weekly-PSS-Likert + $\Delta$sleep-onset-latency with pre-registered weights | `e1e301d` | 2026-05 | [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §4.0 (G2) |
| D4 | **G3 stim-payload grade** — sham-controlled blinded paired RCT, $n \geq 30$, cold-pressor stressor at minute 22 of active phase, time-to-coherence primary endpoint | `e1e301d` | 2026-05 | [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §4.0 (G3) |
| D5 | **Cold-pressor stressor protocol locked at 4±1°C / 90s / non-dominant hand to wrist / minute 22** as standardized G3 stressor | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §6 |
| D6 | **Honest-success outcome matrix** — G1✓/G2✓/G3-null formally defined as a publishable successful outcome | `e1e301d` | 2026-05 | [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §4.0 |

### 3.5 Sham-equivalence specification

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| E1 | **Six-channel sham-equivalence specification** — sham must be indistinguishable from active across visual, mechanical, audible, thermal, EMI, and vibrational channels, each with named measurement instrument | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §7 |
| E2 | **Spectrum-analyzer-at-the-wearer-ear audible-channel sham gate** | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §7, [`docs/mk1_buildplan.md`](docs/mk1_buildplan.md) §5.1 |
| E3 | **IR-camera thermal-load equivalence verification** | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §7 |
| E4 | **RM3100 baseline EMI sham gate** | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §7 |
| E5 | **Accelerometer-on-temple-boom vibration sham gate** | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §7 |

### 3.6 $F^2$ probe

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| F1 | **DIY bifilar-pickup $F^2$ probe** — calibrated near-field $F^2 = E^2 - c^2 B^2$ measurement instrument for wearable-class emitters | `f03c479` | 2026-05 | [`docs/mk1_f2_probe.md`](docs/mk1_f2_probe.md) |
| F2 | **Use of $F^2$ probe as cross-Mk forward-compatible instrumentation channel** — same probe, same NDJSON schema, from Mk1 through Mk3 | `f03c479`, integrated `e1e301d` | 2026-05 | [`docs/mk1_f2_probe.md`](docs/mk1_f2_probe.md), [`docs/roadmap.md`](docs/roadmap.md) |
| F3 | **Matched-$F^2$ H1-vs-H2 three-arm RCT design** (Mk1.5 scope) — same delivered $F^2$ envelope on sub-MHz bifilar coil vs Frey-class pulsed UHF vs sham | `e1e301d` | 2026-05 | [`docs/roadmap.md`](docs/roadmap.md) Mk1.5 |

### 3.7 Stim payloads

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| G1 | **Mk0 bifilar PCB coil** — ~30 × 30 mm series-opposing bifilar PCB coil, 1–8 MHz carrier modulated at 7.83 Hz envelope, $\leq 500$ μT at scalp distance | `d61c911` | 2026-04 | [`docs/mk0_pcb_bifilar_coil.md`](docs/mk0_pcb_bifilar_coil.md) |
| G2 | **H2 modulated-UHF hypothesis** — Frey-class pulsed UHF (~1.245 GHz) as candidate psi-phonon polariton drive | `9080283` | 2026-05 | [`docs/h2_modulated_uhf_hypothesis.md`](docs/h2_modulated_uhf_hypothesis.md) |
| G3 | **FDTD coil design-cert outline** for Mk0 bifilar coil | `a9cb233` | 2026-04 | [`docs/sprint_0.3_fdtd_coil_design.md`](docs/sprint_0.3_fdtd_coil_design.md) |

### 3.8 Data architecture

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| H1 | **NDJSON session schema** with reserved `src` channels for physiology, $F^2$ probe, protocol state, and salt-hashed subjective free-text | `d61c911`, extended `e1e301d` | 2026-04 → 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §8 |
| H2 | **Forward-compatible schema policy** — new channels added, old channels never renamed or repurposed | `e1e301d` | 2026-05 | [`docs/roadmap.md`](docs/roadmap.md) cross-cutting principles |
| H3 | **Pre/post + next-morning Likert panel** — calm / energy / clarity / intrusive thoughts / comfort / sleep-quality, 1–7 scale | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §5 |
| H4 | **Salt-hashed free-text storage** — 240-char post-session free-text fields stored as SHA-256 hash with per-session salt | `e1e301d` | 2026-05 | [`docs/mk1_session_protocol.md`](docs/mk1_session_protocol.md) §8 |

### 3.9 Falsification programme

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| J1 | **F1–F10 falsification table** with engineering-relevant Mk-engagement mapping | `5380703` | 2026-05 | [`docs/falsification.md`](docs/falsification.md) |
| J2 | **F11 candidate** — Primakoff null-search at predicted psion mass range, haloscope-class apparatus | `9080283`, formalized `e1e301d` | 2026-05 | [`docs/falsification.md`](docs/falsification.md), [`docs/psion_quasiparticle.md`](docs/psion_quasiparticle.md) §10 |
| J3 | **F3-precursor and F4-precursor designations** for Mk1.5 matched-$F^2$ engagement | `e1e301d` | 2026-05 | [`docs/falsification.md`](docs/falsification.md) |
| J4 | **Mk3 Dicke superradiance $N^2$ scaling test** — two-unit prediction of $N^2 = 4×$ output scaling at matched per-unit drive vs $N=2$ linear summation null | `e1e301d` | 2026-05 | [`docs/roadmap.md`](docs/roadmap.md) Mk3 |

### 3.10 Theory framework

| # | Element | First disclosure | Date | Primary file(s) |
|---|---|---|---|---|
| K1 | **Psionics Effective Field Theory Lagrangian** with consciousness order parameter $C$, ψ-field, and the $\alpha \psi F^2$, $g_F C F^2$, $g_1 C \psi$, $g_2 C \psi^2$ coupling structure | `d61c911`, `5380703` | 2026-04 → 2026-05 | [`docs/psionics_field_theory.md`](docs/psionics_field_theory.md) |
| K2 | **Psion quasiparticle ontology** — spin-0 self-conjugate real scalar with mass $m$ and coupling $\alpha$; axion-analog vertex structure | `9080283` | 2026-05 | [`docs/psion_quasiparticle.md`](docs/psion_quasiparticle.md) |
| K3 | **Two-channel discipline** — explicit separation of direct ($g_F C F^2$, CEMI) and indirect ($\alpha \psi F^2$ → $g_2 C \psi^2$, psion-mediated) EM↔consciousness coupling | `9080283` | 2026-05 | [`docs/psion_quasiparticle.md`](docs/psion_quasiparticle.md), [`docs/wiki_refactor_brief.md`](docs/wiki_refactor_brief.md) §1.3 |
| K4 | **Psi-phonon polariton** — hybrid in tissue; technical referent for Frey-effect-class observations | `9080283` | 2026-05 | [`docs/psion_quasiparticle.md`](docs/psion_quasiparticle.md), [`docs/h2_modulated_uhf_hypothesis.md`](docs/h2_modulated_uhf_hypothesis.md) |
| K5 | **Wiki-claim-firewall** — Mk-level-bracketed claim discipline: psion-mediated effects do not appear in Mk1 operator-facing copy | `9080283` | 2026-05 | [`docs/wiki_refactor_brief.md`](docs/wiki_refactor_brief.md) §1.6 |

---

## 4. Itemized novelty statement

For the avoidance of doubt regarding the combination of features that
constitutes the HelmKit invention, the following arrangements are each
independently disclosed as inventive:

1. The combination of **B1+B2+B3** — a head-worn stimulator whose stim path is
   gated by two independent hardware interlocks (capture-loop active AND
   session-protocol phase = active) on a supervisor MCU separate from the
   stim driver MCU.
2. The combination of **C1+C2+C3+C4** — a head-worn device in which the
   closed-loop HRV-coherence biofeedback rendering, paced-breathing pacer, and
   structured session container all run identically on active and sham arms
   of a sham-controlled study, isolating the marginal contribution of the
   stim payload.
3. The combination of **D1+D2+D3+D4+D5+D6** — a published evaluation framework
   under which a head-worn psi-tech device may be graded as a publishable
   success (G1✓/G2✓) under a multi-week within-subject trait-endpoint
   ABAB study while simultaneously contributing a publishable null (G3 null)
   on a single-session sham-controlled framework-contribution RCT, with a
   locked cold-pressor stressor at minute 22.
4. The combination of **E1+E2+E3+E4+E5** — a six-channel sham-equivalence
   specification with named measurement instruments per channel, enforced as
   a G1 gate.
5. The combination of **F1+F2+F3** — a DIY calibrated $F^2$ probe instrument
   inherited across an Mk-class device ladder for matched-$F^2$ comparisons
   of distinct stim modalities.
6. The combination of **H1+H2+H3+H4** — a session NDJSON schema integrating
   physiology, near-field $F^2$ measurement, session-protocol state, and
   salt-hashed subjective free-text under a forward-compatible-channels
   policy.
7. The combination of **B4 + the Mk-roadmap claim-firewall (K5) + the
   honest-success matrix (D6)** — a discipline under which a vendor of
   head-worn stim devices structurally cannot make wearer-facing claims
   beyond the evidence available at the device's Mk-grade.

Each item above is disclosed in this repository's commit history as of the
dates in §3. No party may obtain a valid patent on any of these combinations
based on a filing date later than the corresponding first-disclosure commit
date.

---

## 5. Out-of-scope

The following are explicitly not claimed as inventive elements of HelmKit;
they are background art:

- The use of paced breathing to influence autonomic state generally
  (Lehrer & Gevirtz literature).
- The general concept of HRV-coherence biofeedback (HeartMath et al.).
- The general concept of bifilar / caduceus / Tesla coil geometries.
- The general concept of cold pressor as an autonomic challenge.
- ABAB / AB-BA crossover designs in general.
- EEG neurofeedback in general.
- The OpenBCI / MAX30102 / RM3100 / Pi 5 / Heltec V3 component classes.
- The Frey microwave-auditory effect as a phenomenon.

What is disclosed as inventive is the **specific arrangement** of these
elements into the HelmKit substrate, with the specific safety, sham,
evaluation, and theory disciplines described above.

---

## 6. Preservation, replication, and notification

To strengthen the prior-art posture, the following actions are scheduled:

1. **Zenodo** — automatic archival of every tagged GitHub release as a
   DOI-stamped citable snapshot. First release tag: `v0.1-prior-art-baseline`,
   archived at [10.5281/zenodo.20183949](https://doi.org/10.5281/zenodo.20183949).
   The concept DOI [10.5281/zenodo.20183948](https://doi.org/10.5281/zenodo.20183948)
   always resolves to the latest archived version.
2. **Internet Archive Wayback Machine** — periodic snapshot submission of
   the GitHub repository URL and any associated wiki.
3. **arXiv** — submission of [`docs/psionics_field_theory.md`](docs/psionics_field_theory.md),
   [`docs/psion_quasiparticle.md`](docs/psion_quasiparticle.md), and
   [`docs/falsification.md`](docs/falsification.md) as preprints under the
   `physics.hist-ph` / `quant-ph` / `q-bio.NC` categories, as applicable.
4. **OSF (Open Science Framework)** — pre-registration of G2 and G3 studies
   per [`docs/mk1_buildplan.md §4.1`](docs/mk1_buildplan.md). Each
   pre-registration is itself a DOI-stamped disclosure of the corresponding
   experimental design.
5. **GPG-signed commits** — all subsequent commits to this repository carry
   GPG signatures verifying authorship cryptographically.

## 7. Updates

This document is updated as new inventive elements are added to the
HelmKit substrate. Updates take the form of new commits to this file with
appended rows and a bumped document-version number. The first-disclosure
date of an element is the date of the commit in which it first appeared in
the repository, **not** the date it was added to this index.

## 8. Contact

Open an issue on the HelmKit GitHub repository for any inquiry regarding
this declaration.

---

*This declaration is published under the Creative Commons Attribution-
ShareAlike 4.0 International license (CC-BY-SA-4.0); see [`LICENSE`](LICENSE).
It may be reproduced, mirrored, and cited freely.*
