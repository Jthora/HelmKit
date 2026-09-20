# Patent landscape and consolidated bibliography

**Status**: v0, 2026-08-06. First patent-specific research pass across HelmKit's core technology areas, run as five parallel background research agents after two prior rounds of academic-literature-only research. This document is the index — it doesn't repeat the full literature findings already written into `safety.md`, `indefatigability_entrainment_concept.md`, and `effective_physics_derivation_audit.md`; it consolidates the *new* patent findings and points to where everything else already lives, so future sessions have one place to start instead of five scattered docs.

## How to use this document

Each entry below is a lead, not a legal clearance. None of this constitutes freedom-to-operate analysis — where a patent's claims look close to something HelmKit is doing, that's flagged for **human patent-counsel review**, not resolved here. HelmKit's actual posture is DIY/personal/open-hardware, which changes the practical risk calculus from a commercial product, but doesn't eliminate it, and this document doesn't take a position on that either way.

---

## 1. Bifilar/near-field coil neurostimulation

**Closest topological match**: [US9306527B1](https://patents.google.com/patent/US9306527B1) — "Systems, apparatuses, and methods for generating and/or utilizing scalar-longitudinal waves" (Hively; assignee Mclean Capital LLC, filed 2015, granted 2016). Claims a series-opposing bifilar winding with the same explicit far-field-cancellation rationale as HelmKit's coil, broad frequency claims likely spanning 1–8 MHz — but scoped to signal transmission through Faraday cages, no biological or head-worn claim. **Flag for human review**, given the geometric/rationale overlap.

**Related, lower overlap**: [US9258395B2](https://patents.google.com/patent/US9258395B2) (LifeWave Inc., "caduceus-style coil," cellphone RF shielding, 400 MHz–2.5 GHz — different band, passive shield not active stimulator); micro-magnetic neurostimulator families using bifilar geometry for classic B-field/induction stimulation (different physics than HelmKit's E-field-dominant design); [US20130200721A1](https://patents.google.com/patent/US20130200721A1) (WiTricity/MIT wireless power transfer with field-cancellation claims — same antenna-theory technique, different application).

**No prior art found** explicitly combining E-field-dominant/B-field-cancelling coil coupling with a head-worn neurostimulation device at MHz frequencies — read as "genuinely underexplored," not as a strong absence-of-prior-art signal (patent search coverage has real limits).

**Academic leads** (near-field MHz bioelectromagnetics, not yet read in full): Gabriel, Lau & Gabriel, "The dielectric properties of biological tissue II" (canonical tissue permittivity dataset, foundational for any MHz coupling calculation); work on capacitive near-field tissue-coupling models for wireless-powered neural implants.

## 2. Transcutaneous auricular vagus nerve stimulation (tVNS)

**Most relevant patent**: [WO2021026606A1](https://patents.google.com/patent/WO2021026606A1) (Parasym Pty Ltd, maker of Nurosym) — concha/tragus clip electrode, claimed current range **0.1–50 mA**, matching HelmKit's candidate parameters almost exactly; broadly written claim 1. **Flag for closer claims review** before building a cymba-concha module at these parameters.

**Lower overlap than it first appeared**: the patent family that dominated initial search results (US11446491, US11097102, US12472355, US11679258 — "Stimulator for use with a mobile device") belongs to **ElectroCore, Inc.** (gammaCore/Truvaga) and targets **cervical (neck)** placement, not the ear — anatomically distinct from HelmKit's design.

**Also broad and ear-targeted**: [US20220016425A1](https://patents.google.com/patent/US20220016425A1) / WO2022016076A1, US Dept. of Veterans Affairs — ear canal/concha/tragus, 1–10,000 Hz, government-owned (different licensing posture than a private assignee).

**Literature additions beyond the two prior rounds**:
- A 2025 Frontiers narrative review (154 papers) found the modal published protocol is **25 Hz, 200–300 µs** at left cymba concha (strongest NTS/locus-coeruleus activation of the ear sites tested) — a real, more specific parameter recommendation than round 2's finding.
- Shen et al. 2022 (*Neuromodulation*, PMID 35396073): **burst** taVNS (5 pulses at 500 Hz, repeated every 200 ms) produced *greater and more consistent* parasympathetic effects than tonic (continuous 25 Hz) stimulation in 42 healthy adults — direct support for a burst-based architecture, though this is intra-session burst *patterning*, not the same as a short overall session.
- A cymba/cavum concha study at ~20 Hz, 1.9 mA, just **7 minutes**, produced immediate P300/reaction-time improvements persisting 21–28 minutes post-stimulation — real evidence a brief session can have a measurable, time-limited effect. True seconds-scale single-burst dosing remains untested in the literature found so far.

Full grounding already in `indefatigability_entrainment_concept.md` §8, §11.

## 3. 40 Hz gamma sensory stimulation (GENUS)

**Patent family**: originates with **MIT** (Tsai Lab: Tsai, Iaccarino, Martorell, Adaikkan, Brown), priority date **2015-11-24**. Family includes US10682490B2, US12296106B2, US12318549, US12138398, WO2019075094A1. **Cognito Therapeutics** (MIT spinout) holds the exclusive license plus its own continuation, [WO2024189112A1](https://patents.google.com/patent/WO2024189112A1).

**Claim scope, the key finding**: audio-only 40 Hz stimulation is covered in the *disclosed* embodiments (no visual component required in at least one claim family), but the core independent claims are anchored to **disease treatment** (dementia, Aβ/tau reduction) — not general alertness. A DIY daytime-alertness, audio-only application looks likely to sit outside the literal claim language based on what could be extracted, but full claim text wasn't accessible to confirm with certainty, and MIT/Cognito's posture in this space should be assumed active rather than assumed dormant. **Flag for human review if this ever becomes a real product rather than a personal-use device.**

**Other holders**: OptoCeutics (Denmark) — "Invisible Spectral Flicker," a proprietary 40 Hz light-delivery method sold as EVY LIGHT under general-wellness framing. No holder found specifically claiming "daytime alertness" as a use — a real gap in what's claimed.

**Real adverse-event data** (superseding the summary-level "no significant AEs" statement from the first literature pass — see indefatigability doc §13 for the correction this triggered): Phase 1 single-session drowsiness rates of **38.4% (young, cognitively normal) and 40% (older, cognitively normal)** — higher than the 6.2% rate in the mild-AD group. Phase 2A (3 months daily): dry eye 25% vs. 0% control, drowsiness 37.5% vs. 14.2%. Larger-scale OVERTURE trial: headache 21.7% vs. 10.7%, tinnitus 15.2% vs. 0% — AEs not seen at all in the smaller early trials. Zero seizures across all trials, including in an epilepsy-patient subgroup.

**Citation chase**: the 2025 sustained-attention study (Attokaren/Zhang/Mettupalli/Singer, Georgia Tech) is too new for a citation trail yet ("cited by 1," unresolved).

## 4. Persinger/"God Helmet" and CEMI/consciousness-field

**The original God Helmet patent**: [CA2214296C](https://patents.google.com/patent/CA2214296C) (Koren & Persinger, filed 1997, granted 2005, **expired 2017 — now public domain**). Claims a signal generator distributing waveforms across multiple channels to solenoids worn by a subject — the generic multi-channel weak-field architecture. No US patent found for this device. Field parameters (weak/complex ~1 µT, EEG/amygdala-pattern-derived waveforms) live in the research literature, not the claims. **Freely practicable as prior art/inspiration** — directly relevant to HelmKit's mechanical/EM design space with no licensing concern.

**CEMI citation chase**: thin. No more-feasible empirical test has displaced Strupp's invasive interhemispheric-shielding proposal (`effective_physics_derivation_audit.md`) in the 2024–2026 window searched. McFadden's own 2025 follow-up (PMC12237978) pivots entirely to AI/computing architecture and proposes no new neuroscience test.

**Consciousness-field patents**: essentially empty for CEMI/psi-field-style claims specifically — informative in itself. What exists instead: clinical EEG/TMS consciousness-level monitors (unrelated mechanism); and, most interestingly, **Psigenics Corp's patent family** (US8073631B2, US8423297B2, US9367288B2, RE44097 — "Device and method for responding to influences of mind") — random-event-generator-based statistical-anomaly detectors, direct descendants of PEAR-lab-style research. Closest thing to "psi field" IP on record, framed as statistical detection rather than field physics — connects back to this project's earlier (set-aside) forced-choice/RNG protocol work.

## 5. Primary safety-standard verification (correction to prior research)

**A real error in the second research round's `safety.md` edit was caught and fixed** — see `safety.md`'s flagged near-field row for the corrected, primary-source-verified numbers (ICNIRP 2020 Tables 5/6/8, confirmed exact SAR basic restriction of 2 W/kg/10g, and the crucial correction that ICNIRP explicitly treats 100 kHz–30 MHz as always-near-field with its own direct field-comparison compliance route — no mandatory SAR modeling in this band, contrary to what the prior pass concluded). Full detail lives in `safety.md` itself, not duplicated here.

**Real near-field dosimetry analogs found**, closer than cellphone/base-station far-field literature: RFID-at-13.56-MHz-near-head exposure studies (hearing-implant-user population), wireless-power-transfer human-exposure dosimetry papers. Not yet read in full — a reasonable next step if `safety.md`'s field-measurement task moves forward.

---

## Where each finding already lives

| Topic | Primary doc |
|---|---|
| Near-field E-field safety limits, SAR, FCC exemption | `docs/safety.md` (flagged blockquote) |
| tVNS parameters, burst-mode evidence, time-course | `indefatigability_entrainment_concept.md` §8, §11 |
| 40 Hz safety, drowsiness correction, audio-only support | `indefatigability_entrainment_concept.md` §9, §12, §14 |
| Vigilance-classifier ceiling, personalization, calibration duration | `indefatigability_entrainment_concept.md` §7, §10, §13 |
| Light-alerting effect | `indefatigability_entrainment_concept.md` §7 |
| CEMI/EFT derivation audit, Strupp paper, MEG reanalysis design | `effective_physics_derivation_audit.md` |
| TPU living-hinge fatigue, heat-set insert bosses | `docs/mechanical/mk0.5_topology_beta_print_plan.md` |
| Coil, tVNS, 40 Hz, Persinger, CEMI patents (this document) | here |

---

## 6. Adjacent-field roster (2026-08-06) — ten parallel category surveys

A second, broader research wave: rather than more depth on HelmKit's own specifics, ten categories adjacent to the whole Psionics undertaking, surveyed in parallel to find what's already out there before doing more original work. Two categories (parapsychology-paradigm replication status; where CEMI sits among real consciousness theories) turned up findings consequential enough to get folded directly into `literature_grounding.md`, `falsification.md`, and this doc's own CEMI section above — summarized here with pointers, not repeated. The other eight are summarized in full below.

**Parapsychology/anomalous cognition, deeper** → folded into `literature_grounding.md` Finding 3 and `falsification.md`'s F1 row. Headline: the 2020s preregistered-replication track record for RNG-PK and precognition is consistently null under the field's own most rigorous recent tests (Maier & Dechamps 2022; the Transparent Psi Project's 420,472-trial replication), while ganzfeld's best current estimate (a real Stage 2 Registered Report) is ES=0.088 — real but roughly a third the size this project's docs previously cited.

**Mainstream consciousness theories vs. CEMI** → folded into this doc's "Where CEMI/the ψ-EFT actually sits" section above. Headline: the *entire* field of consciousness science currently lacks a confirmed leading theory (IIT publicly branded "pseudoscience" by 124 researchers in 2023; a 2025 Nature adversarial collaboration found neither IIT nor Global Workspace Theory's predictions confirmed) — CEMI is a real minority position within that turmoil, but the ψ-coupling extension inherits none of CEMI's comparative legitimacy.

### Quantum biology & magnetoreception

Cryptochrome radical-pair magnetoreception is well-supported mainstream science — a 2021 Nature paper (Xu, Hore, Mouritsen et al.) directly demonstrated migratory-songbird cryptochrome is more magnetically sensitive in vitro than non-migratory species'. Two important cautions found: the 2019 Caltech human-geomagnetic-sensitivity study (Wang, Kirschvink, Shimojo — alpha-band EEG response to weak rotating fields) **has no confirmed independent replication as of 2026**, and is being cited by "electromagnetic hypersensitivity" claims its own authors don't endorse. Microtubule quantum coherence (Orch-OR's physical substrate): even Hameroff's own rebuttal to Tegmark's decoherence critique only extends coherence time to ~10⁻⁵–10⁻⁴s — still orders of magnitude short of millisecond-to-second cognitive timescales. The famous photosynthesis "quantum coherence boosts efficiency" finding has itself been walked back by more recent work (Duan et al. 2017, PNAS) — a track record worth remembering before leaning on any new quantum-biology headline.

### Near-field metamaterials & antenna engineering

**Devaney & Wolf (1973, *Phys. Rev. D*)** is the actual formal-physics justification for "non-radiating current distribution" — the real theorem underlying the whole modern anapole/toroidal-dipole metamaterial literature (Kaelberer/Fedotov/Papasimakis, *Science* 2010; *Nature Materials* 2016 review), and grounds HelmKit's "concentrate near-field, cancel far-field" coil rationale in established antenna theory rather than an ad hoc claim. Split-ring resonators (Pendry et al. 1999) are actively used for near-field E-field enhancement in real MRI RF coils (multiple 2021–2024 papers) — direct precedent for concentrating near-field coupling close to tissue. New near-field head-dosimetry precedent found beyond what's in `safety.md`: BAHA-hearing-implant-users-near-13.56MHz-RFID studies, and smart-glasses EMF exposure literature — both closer real-world analogs than cellphone dosimetry. Honest gap: all SRR/anapole biomedical work found operates at GHz/THz, not HelmKit's 1–8 MHz band — a genuine novelty claim, not a replicated approach, if pursued.

### Comparative neuromodulation landscape

Flow Neuroscience's tDCS device received actual **FDA clearance for major depression in December 2025** — first authorized home-use tDCS antidepressant device. Meanwhile a 2024 meta-analysis (42 studies, 1,386 people) found tACS's working-memory enhancement effect **collapses to essentially zero** after publication-bias correction — a real efficacy problem on top of this project's existing safety-conservatism exclusion. TMS remains the mature clinical baseline (FDA-cleared for MDD, OCD, migraine; seizure risk <0.1–1%). tFUS is growing fast (177 registered trials through Sept 2025) with no FDA neuromodulation clearance yet but no serious AEs reported in low-intensity human studies. GVS remains the least-regulated, least-safety-studied modality on the roster — no landmark trials, mostly mechanistic/simulation work. CES is FDA Class II specifically for anxiety/insomnia, **not** depression — a real, recurring point of industry marketing overreach worth remembering if CES is ever cited as regulatory precedent.

### Wearable biosensing & closed-loop biofeedback

Supervised HRV biofeedback shows a real effect (Pizzoli et al. meta-analysis, g≈0.81–0.83 for stress/anxiety), but a 2025 remote/portable-delivery meta-analysis found the effect **roughly halves** in unsupervised settings (g≈0.44) — directly relevant since HelmKit is exactly that kind of unsupervised consumer device. PPG accuracy is well-validated at the wrist (near the ceiling of what's measurable), decent-but-noisier for raw HR at the ear, and genuinely under-studied for HRV specifically at forehead/temple sites — a real, specific gap for a head-worn design. Independent (non-sponsored) validation found a real accuracy hierarchy among consumer wearables (Oura > WHOOP > Garmin/Polar for HRV), diverging from marketing-parity claims. A cautionary paper, "Why Meditation Wearables Fail" (arXiv), documents reward-misspecification failure modes in closed-loop biofeedback — worth reading before finalizing any closed-loop reward design; no RCT yet demonstrates closed-loop beats open-loop biofeedback despite it being the direction this project has been leaning.

### Circadian & photobiology

Dose-response for light-alerting is strongly non-linear: a 12-minute pulse phase-shifts the circadian pacemaker ~8x more efficiently per minute than 4-hour exposure, and even 15-second pulses show measurable effects — strong direct validation for the tactical-burst design already in `indefatigability_entrainment_concept.md`. Best precedent found: **HumanCharger/Valkee**, a real, clinically-tested ear-canal (non-ocular) light-delivery device — a double-blind trial in transatlantic travelers found 3–4 day jet-lag recovery vs. >7 days placebo (p=0.038) using four 12-minute sessions/day. A denser-than-expected patent cluster exists on head-worn circadian-light devices (headband/eyewear/ear-canal forms). Confirmed numeric target from two independent standards bodies: ≥250 melanopic EDI lux for daytime alerting.

### Cold War/historical psychotronics

Real, declassified: the DIA's 1978 "Paraphysics R&D — Warsaw Pact" report confirms sustained Soviet state funding of psychoenergetics research — but with a documented caveat that the CIA had a pattern of overestimating Soviet capability generally, and US psi funding was partly triggered by fear of a Soviet lead that may have been partly self-generated intelligence paranoia. MKUltra and Star Gate are frequently conflated but are different programs (chemical/behavioral vs. anomalous-cognition research). The actual scholarly fault line from the 1995 AIR review: Utts and Hyman didn't disagree about the statistics, they disagreed about whether statistical anomaly proves psi. Real and categorically separate from psi research: DoD directed-energy bioeffects work (the Frey/microwave-auditory effect is real, patented, mechanistically understood) and the still-contested Havana Syndrome assessments.

### Torsion fields, scalar waves — epistemic hygiene

Both "torsion field" (Akimov/Shipov) and "scalar waves" (Bearden/Tesla-mythology) are confirmed pseudoscience, each a bait-and-switch borrowing a real physics term (Einstein-Cartan torsion; scalar/vector potentials, Aharonov-Bohm) and attaching unfounded free-energy/information-transfer claims to it. The coil patent flagged earlier in this doc (US9306527B1, Hively) turns out to belong to a real credentialed physicist (Oak Ridge National Lab) whose non-mainstream framework has nonetheless been absorbed by the free-energy fringe ecosystem — a more complicated case than outright fraud, still outside mainstream electrodynamics. **Actionable style guidance adopted for this project's own writing**: use "near-field," "reactive power," "evanescent coupling," "flux cancellation" — avoid "scalar," "longitudinal wave," or "torsion." A repo-wide check found this project's own authored docs (as opposed to cached wiki content) are already clean except for `docs/field-notes/volume-1/03_sister_modules.md`, which uses "scalar-wave" language — already flagged stale/deferred per the Mk-ladder rebaseline pass (see memory `mk-ladder-rebaseline-2026-08`), not fixed here, but worth remembering when that deferred update happens.

### Biofield science & energy medicine landscape

NCCIH's most substantial biofield investment (a $1.8M center grant, 2002–2007, University of Arizona) was not renewed after its term. The field's own most substantive 2024 output (Hammerschlag et al.; Sprengel et al.) is about *standardizing how to report trials*, not demonstrating efficacy — a strong signal the evidence base is still considered too heterogeneous to synthesize confidently, decades after the term was coined. Rigorous reviews of touch/energy therapies consistently land on modest-to-null effects plausibly attributable to attention/placebo (Cochrane 2015 on Reiki: insufficient evidence; a comprehensive independent Reiki review: insufficient evidence for any condition). Ultra-weak photon emission (biophotons) is real, measurable biophysics (mainstream explanation: chemiluminescence from oxidative metabolism) — but Popp's stronger "coherent biofield" claims built on it are not accepted by mainstream biophysics, a clear case of a real phenomenon being used to support a much larger unsupported claim.

## Recommended next steps, if this continues

- Human patent-counsel review of US9306527B1 (coil) and WO2021026606A1 (tVNS) specifically — these are the two closest claim-overlap flags, and both are cheap to have a real read done on before any build commitment.
- Read the ICNIRP "New Technologies" note and RAIN RFID industry compliance guidance in full — both surfaced as directly relevant to near-field small-coil compliance and weren't read past the title/abstract level.
- The 2025 sustained-attention 40 Hz study and this project's own use of it deserve a revisit once it accumulates more citations — it's currently a single new study, not yet a replicated finding.
- If a second patent-research round ever happens, it's worth extending to GVS (galvanic vestibular stimulation) and photobiomodulation (tPBM) device patents — both are on the indefatigability roster but weren't included in this round's five threads.
- **The RNG-PK/precognition null-replication finding (§6) is the single most consequential result from either research wave and deserves a deliberate conversation, not just a doc update.** It's been folded into `literature_grounding.md` and `falsification.md` honestly, but what (if anything) it should change about this project's overall confidence posture, F3–F11's remaining untested criteria, or the wiki-correspondence report is a judgment call for the repo owner, not something to resolve unilaterally in a research pass.
- HumanCharger/Valkee (ear-canal light delivery) and the head-worn circadian-light patent cluster are a genuinely promising, under-explored precedent class for the indefatigability concept's light-pulse arm — worth a closer read of the actual device/trial design, not just the summary found here.
- Devaney & Wolf (1973) and the 2020 *Opt. Express* paper bridging it to anapole metamaterials are worth reading in full — they're now this project's strongest citation for the coil's core design rationale and deserve to be cited precisely, not just referenced secondhand.
