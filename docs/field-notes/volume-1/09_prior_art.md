# Prior art

<!-- Source: wiki anchor pages, docs/wiki_anchors.md, docs/falsification.md
     Status: v0 (2026-05-18)
-->

This chapter is the annotated bibliography of primary literature the
HelmKit platform engages with. For each entry we give the citation, a
one-sentence summary of the claim, the project's verdict at the time of
this printing, and which HelmKit subsystem (if any) depends on it.

The verdicts use three labels:

- **Rederivable** — we have either reproduced the central calculation
  ourselves or could do so from the published methods. The result is
  inside the project's working assumption space and constrains a real
  design decision.
- **Suggestive** — the result is intriguing, has not been definitively
  replicated or refuted, and influences our hypothesis space without
  driving a current design decision. We engage it at G3 (framework
  contribution) where appropriate.
- **Aspirational** — the result would be transformative if true, the
  evidence is currently insufficient by mainstream standards, and the
  project treats it as a long-horizon falsification target rather than
  a load-bearing design input.

We do not lean on any single source as proof. We lean on the
combination of (a) the project's own derivations, (b) the wiki's
geometries treated as design specification per Chapter 4, and (c) the
literature catalogued below, with each source's role labeled.

---

## Electromagnetic neuromodulation

**Persinger, M.A. (2012). "Brain electromagnetic activity and lightning:
potentially congruent scale-invariant quantitative properties." *Frontiers
in Integrative Neuroscience*, 6:19.**
The "God Helmet" research program — weak (microtesla-class) complex
pulsed magnetic fields applied to the temporal lobes produce reported
shifts in mood, perception, and sense of presence. **Verdict: suggestive.**
The Persinger results have a long history of failed and partial
replications (Granqvist et al. 2005, St-Pierre & Persinger 2006). The
HelmKit's Mk1 stim envelope sits inside the Persinger amplitude band,
and Mk1.0 G3 is structured to either replicate the effect with proper
sham or publish a clean null. **Subsystem dependence:** Mk1 bifilar
coil drive amplitudes; Mk1.5 motion-tolerant Combat mode envelope.

**Dotta, B.T., Saroka, K.S., Persinger, M.A. (2012). "Increased photon
emission from the head while imagining light in the dark is correlated
with changes in electroencephalographic power: support for Bókkon's
biophoton hypothesis." *Neuroscience Letters*, 513(2): 151-154.**
Reports correlation between voluntary visual imagery, EEG signature
shifts, and ultraweak photon emission from the head. **Verdict:
suggestive.** The biophoton literature is contested; the measurement
itself requires near-perfect dark conditions, single-photon-counting
PMTs, and exquisite source isolation. Outside Mk1 scope; potential Mk3
adjunct if the Psi Defender's haloscope-adjacent instrumentation
program produces compatible sensors. **Subsystem dependence:** none in
Mk1. Long-horizon Psi Defender scope only.

**Saroka, K.S., Persinger, M.A. (2014). "Quantitative evidence for direct
effects between earth-ionosphere Schumann resonances and human cerebral
cortical activity." *International Letters of Chemistry, Physics and
Astronomy*, 39: 166-194.**
EEG signatures correlated with measured local Schumann-resonance
fluctuations. **Verdict: suggestive.** The signal-to-noise at the
Schumann amplitudes ($\sim$ 1 pT class) is genuinely demanding;
correlation does not establish causation. Drives Mk1's choice of 7.83
Hz envelope as the *first* modulation frequency the bifilar payload is
tested against, rather than as a load-bearing claim about mechanism.
**Subsystem dependence:** Mk1 bifilar drive envelope frequency choice.

---

## Field theories of consciousness

**McFadden, J. (2002). "Synchronous firing and its influence on the
brain's electromagnetic field." *Journal of Consciousness Studies*, 9(4):
23-50.** The CEMI (conscious electromagnetic information) field theory:
endogenous EM field of synchronized neuronal firing is itself the
substrate of conscious experience. **Verdict: rederivable.** The
underlying biophysics — that synchronous firing produces measurable
local-field potentials, that those LFPs sum into a brain EM field
detectable by MEG — is uncontroversial. The interpretive claim that
this field *is* consciousness is the contested step. The project treats
CEMI as the **direct EM-consciousness channel** in the
two-channel decomposition; the wiki's
$\alpha\psi F^2$ vertex is the **indirect channel**. **Subsystem
dependence:** the entire wearer-side measurement program — EEG (Mk2+),
ambient-field survey (Mk0.5+), and the project's claim that
"measuring the wearer's EM environment is intrinsically interesting"
inherits from CEMI's stance.

**Effective Field Theory of Consciousness (wiki page; canonical Lagrangian
on the FusionGirl wiki, 2026-05-12 drop).** A five-coupling effective
theory unifying the classical $\psi$ field, the consciousness order
parameter $C$, and the electromagnetic field strength tensor $F$. Four
of the five couplings are bounded by the project's $F_1$-$F_{11}$
falsifiers. **Verdict: rederivable + aspirational.** The Lagrangian
is mathematically well-defined and its couplings produce specific
predictions; whether any of the couplings are non-zero is the empirical
question the falsification program is structured to answer.
**Subsystem dependence:** the entire framework. Specific couplings
drive specific Mk-level engagements: $\alpha$ at Mk1 (precursor) and
Mk2 (direct); $g_F$ at Mk2; $g_2$ at Mk3.

---

## Quantum biology

**Bandyopadhyay, A. and collaborators (2013-2023). Microtubule resonance
series, including Sahu et al. (2013) "Multi-level memory-switching
properties of a single brain microtubule," *Applied Physics Letters* 102,
123701, and follow-on work through 2023.** Microtubule structures show
discrete electrical resonance peaks across kHz through GHz; the cited
1.245 GHz peak figures prominently in the wiki's Frey-class UHF
hypothesis. **Verdict: suggestive.** The lab measurements are real and
replicated within the Bandyopadhyay group; cross-lab replication is
limited. Drives the Mk2.5 H2 (Frey-class UHF) modality as a
matched-$F^2$ test target. Mk1 does not engage this work directly.
**Subsystem dependence:** Mk2.5 H2 emitter band selection; Mk3.0 dyadic
protocol frequency selection.

**Hameroff, S., Penrose, R. (2014). "Consciousness in the universe: a
review of the 'Orch OR' theory." *Physics of Life Reviews*, 11(1): 39-78.**
Orchestrated Objective Reduction: consciousness arises from
quantum-coherent computation in tubulin microtubules, terminating by
gravitationally-triggered objective reduction. **Verdict: aspirational.**
The proposal motivates the project's interest in microtubule resonance
frequencies as a target band, without committing the project to the
Orch-OR interpretation. Falsification path: Tegmark's decoherence-time
critique (Tegmark 2000) puts the burden on the proposal; subsequent
warm-coherence results in photosynthesis and bird-magnetoreception have
shifted but not closed the question. **Subsystem dependence:**
indirect — informs band selection at Mk2.5+; no Mk1 dependence.

**Kalra, A.P. et al. (2023). "Electronic energy migration in microtubules."
*ACS Central Science*, 9(3): 352-361.** Direct measurement of
electronic excitation transfer along tubulin lattices. **Verdict:
rederivable.** Clean room-temperature measurement; less interpretively
loaded than the Bandyopadhyay or Hameroff–Penrose programs. Strengthens
the *biophysical-plausibility* arm of the microtubule-band hypothesis
without committing to any particular interpretation. **Subsystem
dependence:** indirect — informs Mk2.5 band selection at the
biophysical-plausibility layer.

---

## Group / multi-wearer effects

**Celardo, G.L. et al. (2019). "On the existence of superradiant excitonic
states in microtubules." *New Journal of Physics*, 21, 023005.** Microtubule
collective states could exhibit Dicke superradiance — $N^2$ scaling of
emission intensity in $N$ coherent emitters. **Verdict: suggestive
+ aspirational.** Theoretically clean; experimentally unexamined at the
relevant scale. Drives the Mk3.0 dyadic protocol design and the
$F_7$ universal-coupling falsifier. Mk1 does not engage this.
**Subsystem dependence:** Mk3.0 dyadic emission test; Resonant Pipeline
$N^2$ scaling claim.

**Utts, J. (1996). "An assessment of the evidence for psychic functioning."
*Journal of Scientific Exploration*, 10(1): 3-30. And Cardeña, E. (2018).
"The experimental evidence for parapsychological phenomena: a review."
*American Psychologist*, 73(5): 663-677.** Meta-analyses of
parapsychological replication data, with positive overall effect sizes
at small-but-non-zero magnitudes after publication-bias correction.
**Verdict: suggestive.** The HelmKit project does **not** stake its
design on these meta-analyses being correct. We engage them at G3 by
ensuring our pre-registration discipline matches the methodological
floor the parapsychology field has had to develop — large samples,
sham controls, blinded analysis, registered analytical plans — and by
treating any positive Mk2.5+ result as embedded in that broader
question rather than as standalone proof.
**Subsystem dependence:** none direct; informs G3 methodology
standards.

---

## Safety and bioelectromagnetics

**IEEE C95.1-2019. "IEEE Standard for Safety Levels with Respect to Human
Exposure to Electric, Magnetic, and Electromagnetic Fields, 0 Hz to 300
GHz."** The current IEEE safety standard. **Verdict: load-bearing.**
This is the standard the project's safety floor (Chapter 6) is
calibrated against, in combination with the ICNIRP 2020 guidelines.
**Subsystem dependence:** MCU-B blacklist rows 6-8 (RF and CW ICNIRP
exceedance lines); SAR measurement requirement for all RF modalities.

**ICNIRP (2020). "Guidelines for limiting exposure to electromagnetic
fields (100 kHz to 300 GHz)." *Health Physics*, 118(5): 483-524.** The
current ICNIRP RF safety standard. **Verdict: load-bearing.** Used
identically to the IEEE standard above. **Subsystem dependence:** MCU-B
blacklist rows 6-8; Mk2+ RF SAR interlock thresholds.

**Frey, A.H. (1962). "Human auditory system response to modulated
electromagnetic energy." *Journal of Applied Physiology*, 17(4): 689-692.**
The microwave-auditory effect: pulsed RF in the 200-3000 MHz band
produces auditory perception at peak power densities above
$\sim$ 40 mW/cm² with pulse widths under $\sim$ 1 ms. **Verdict:
rederivable.** The effect is well-established in mainstream
biological-effects literature. Forms the basis of MCU-B blacklist
row 6 and is referenced explicitly in Chapter 6's safety floor.
**Subsystem dependence:** MCU-B blacklist row 6; Mk2.5 H2 modality
safety envelope.

---

## What this chapter is not

This bibliography is **not exhaustive** — the project's bibliography
file at [`docs/bibliography.md`](https://github.com/Jthora/HelmKit/blob/master/docs/bibliography.md)
is the longer version. The entries above are the ones that are either
load-bearing for a current design decision or have shaped the
project's hypothesis space in a way the reader needs to know about to
evaluate the volume's claims.

The bibliography is also **not a defence**. We do not invoke the
literature to justify claims the literature does not justify. Where the
verdict is "suggestive" or "aspirational," the wearer-facing claim
language stays inside what the device can actually demonstrate, per the
claim firewall named in Chapter 4 and Chapter 6.

The bibliography will grow with each subsequent volume. Volume II is
expected to expand the field-theory section (with the project's own
follow-up derivations on the caduceus far-field null and the Schumann
envelope) and the safety section (with the SAR-ceiling derivation owed
to Track C).
