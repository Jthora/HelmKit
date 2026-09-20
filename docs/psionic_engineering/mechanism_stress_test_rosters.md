# Mechanism stress-test: rosters and iterative critique

**Status**: v0, 2026-08-06. Pure ideation/critique exercise — explicitly decoupled from any committed design. Per direct instruction: the existing notional designs (bifilar PCB coil, topology B helmet shell, TPMS lattice, etc.) are set aside here as *aesthetic* reference points only, not technical constraints. This document is not gated against `docs/inventory.md` the way `alternative_architectures_roster.md` is — that doc answers "what can we build," this one answers "what would actually make a stabilizer/entrainment device work, if anything." Feasibility gets re-attached only at the very end, and only to whatever survives critique.

**Method**: generate a roster, critique every item on it honestly (plausibility, evidence, engineering handle, failure mode), let the critique reshape the next roster, repeat. Four rounds, run to convergence (Round 4 explains why the process stops there rather than continuing indefinitely).

**Critique axes used throughout**:
- **Evidence** — is there real, mainstream evidence this mechanism affects the human nervous system at all, independent of psionics?
- **Engineering handle** — is there a concrete, buildable thing to point at, or is the mechanism unfalsifiable/no moving parts to test?
- **Track** — borrowing the wiki's own split: **Track A** (useful/buildable regardless of whether ψ is real) vs **Track B** (only does anything if ψ specifically is real).
- **Failure mode** — what does it look like when this doesn't work, so a null result is informative rather than ambiguous?

---

## Round 1 — Raw mechanism sweep

Cast wide on purpose, including weak/bad ideas — the point of Round 1 is to not prematurely filter.

### 1A. Classical neuro/physio biofeedback (no exotic physics required)

| Mechanism | Evidence | Engineering handle | Track | Critique |
|---|---|---|---|---|
| Paced-breathing HRV coherence | Strong, decades of published work | Simple (existing PPG + haptic/audio pacer) | A | Already the L0/L1 floor. Real, boring, works. The honest baseline every other idea has to beat. |
| EEG neurofeedback (alpha/theta training) | Real but modest/contested effect sizes, publication-bias concerns | Moderate (dry EEG electrodes, real-time band-power) | A | Consumer-grade dry electrodes are noisy; effect depends heavily on protocol quality. Worth doing carefully or not at all — a bad neurofeedback loop can train the *artifact* (jaw clench, eye movement) instead of the signal. |
| GSR (skin conductance) biofeedback | Real, used clinically for anxiety/arousal | Simple (2-electrode conductance) | A | Slow signal (seconds), good for arousal trend not moment-to-moment stabilization. Easy add-on, not a centerpiece. |
| Closed-loop binaural/isochronic auditory entrainment | Real for driving EEG frequency-following response; effect on subjective state weaker/mixed | Simple (any audio transducer, already in inventory as bone-conduction) | A | Frequency-following response itself is well-replicated; the leap to "therefore stabilized/indefatigable" is the weak link, not the entrainment itself. |
| Pupillometry-based arousal feedback | Real (pupil diameter tracks LC-NE arousal system) | Needs eye camera — new sensor class | A | Genuinely underused signal for this application; camera-based, so privacy/complexity cost is nontrivial for a head-worn device. |

### 1B. Classical bioelectric/biophysical (real transducer physics, effect-on-cognition less settled)

| Mechanism | Evidence | Engineering handle | Track | Critique |
|---|---|---|---|---|
| Near-field EM coupling (bifilar/SRR/toroidal family) | Physics of the coupler is solid; physiological effect at non-thermal, sub-ICNIRP levels is *not* established | Solid (Roster A of the prior doc) | A/B blend — real transducer, unproven neuro-effect | This is the existing notional design. As a piece of *engineering* it's fine. As a *mechanism for changing mental state*, it currently has no independent evidence trail — it inherits its justification entirely from the wiki's ψ-field claim, which is exactly why it should be treated as Track B, not Track A, until shown otherwise. |
| Transcutaneous vagus nerve stimulation (tVNS) | Real, growing evidence base (ear-clip tVNS affects HRV/vagal tone; some FDA clearances in adjacent indications) | Simple — ear-clip electrode, mild current | A | **Notably absent from every prior roster in this project.** Directly targets autonomic balance, which is the actual physiological substrate of "indefatigability." Worth flagging as probably underrated relative to how much attention the coil has gotten. |
| Transcranial photobiomodulation (near-infrared LED, tPBM) | Real, growing but not yet large evidence base; mitochondrial/cerebral-blood-flow mechanism proposed | Simple — NIR LEDs + printed light-tight housing | A | Cheap, safe at low irradiance, easy to fabricate (LEDs + FDM housing), genuinely underexplored in this project until now. Good Track-A candidate for the "entrainment/indefatigability" goals independent of anything psi-related. |
| Galvanic vestibular stimulation (GVS) | Real, documented arousal/balance effects | Simple electrodes (mastoid) | A | Already named in the prior roster; repeated here because it belongs in the "classical, real, underused" bucket, not the exotic one. |
| Static magnetic field shaping (Halbach, DC) | Weak/mixed evidence for static-field bioeffects at safe field strengths | Trivial (magnets already owned) | A/B blend, weak on both | Real engineering technique, but "does a static field change cognition" has a much thinner evidence base than any AC method above it. Mostly useful as a *background condition* for A/B testing something else, not as a primary mechanism. |
| Low-frequency solenoid fields (Persinger-class) | Contested — original results never independently replicated at claimed effect sizes | Simple (large coil, already covered) | B | Named for completeness; the evidence base is genuinely weaker than tACS/tDCS, not stronger, despite being the most-cited historical precedent for this whole space. |

### 1C. Speculative / fringe mechanisms (mechanism-agnostic, taken seriously enough to critique properly)

| Mechanism | Evidence | Engineering handle | Track | Critique |
|---|---|---|---|---|
| Passive near-field pickup / "receiver, not transmitter" | N/A (measurement device, not an effect claim) | Solid — just a coil + amp, already specified as unused mode | B (only informative if ψ real) | Best-structured speculative item on this list: it *cannot* cause a placebo/direct-stimulation confound the way any active driver can, because it emits nothing. If ψ coupling is real, a passive pickup is the cleanest possible first look at it. If it isn't, the tool degrades gracefully into a well-understood RF/magnetometer instrument. |
| Dyadic phase-locked coupling (two wearers' devices cross-modulate) | N/A directly; dyadic HRV/EEG synchrony between humans in proximity is real and mundane (shared breathing pace, shared audio cues, mutual gaze) | Moderate — needs `analyze_ambient_confounds.py`-style rigor to separate "biology synchronizing via ordinary channels" from anything else | B, but only after A-level confounds are ruled out | This is only as good as the confound analysis around it. Any dyadic coherence result without a same-room/same-cue control is close to meaningless — the tooling for this already exists (`tools/analyze_dyadic_coherence.py`, `tools/analyze_ambient_confounds.py`), which is the right order of operations: build the null-hypothesis killer *before* the effect claim. |
| Geomagnetic/Schumann-resonance passive exposure (no active drive at all) | Weak, contested epidemiological correlations only | Trivial — literally just don't shield the wearer, or add a tuned passive loop antenna | B | Essentially untestable as currently framed — "ambient exposure" has no dose control, no blinding, and huge confound surface (weather, geomagnetic activity, time of day all correlate with everything). Only worth doing as a logged *covariate* alongside another experiment, never as a standalone mechanism. |
| Orgone-style layered dielectric/organic-inorganic stacking | None — historically discredited, no mechanism, no controlled replication | None — no falsifiable prediction to engineer toward | B, unfalsifiable | Included specifically to reject it with reasons rather than by default assumption: there's no proposed mechanism that makes contact with any known physics, and historically-run tests found no effect. This is the shape of idea the project's own falsification framework (`docs/falsification.md`) exists to filter out — flagging it here so it's explicitly considered-and-declined, not silently never mentioned. |
| Quantum-coherence-in-neural-microtubules-style amplifier claims | None operationalized — the underlying Penrose-Hameroff-adjacent proposals remain unfalsified and are contested even among proponents of quantum-brain theories generally | None — nothing to build; no proposed interface between "microtubule coherence" and any external device | B, unfalsifiable at this level of specificity | Same treatment as above: name it, decline it, for the same reason (no engineering handle, no falsifiable prediction reachable with a head-worn device). If revisited, it would need a specific, external, testable claim, not the general theory. |
| Zero-point/vacuum-energy coupling claims | None — no accepted physics connects vacuum fluctuations to macroscopic bioeffects at achievable field strengths | None | B, red flag | Worth naming once because it recurs in adjacent literature, and worth explicitly flagging as a step beyond "unproven" into "no proposed mechanism consistent with known physics" — the same category of claim that should raise scrutiny regardless of general epistemic openness elsewhere in this project. |

**Round 1 takeaway**: the sweep cleanly separates into three tiers — (i) real, evidenced, Track-A mechanisms that are currently *under*-represented in the project (tVNS, tPBM, pupillometry), (ii) real transducer physics with an *unproven* neuro-effect that's currently over-represented (the whole EM-coupling family, including the existing coil), and (iii) a small number of items that don't survive contact with "what's the falsifiable prediction" and should be named-and-declined rather than carried forward.

---

## Round 2 — Control-loop architecture (orthogonal axis)

This axis is independent of *which* physical mechanism gets used — it's about *how the loop runs*, and it turns out to matter more for trustworthiness than the choice of mechanism does.

| Architecture | Description | Critique |
|---|---|---|
| Open-loop scripted | Fixed stimulation program, no sensing feedback at all | Worst-evidenced pattern in the whole space ("broadcast and hope"). Any positive result is maximally confoundable with expectation/placebo, since there's no way to show the device is doing anything state-*contingent*. Should be avoided as a primary architecture for anything claiming a real effect. |
| Closed-loop, single-variable | One sensor (e.g. HRV) drives one actuator (e.g. breathing pacer) | The existing, evidenced L0/L1 floor. Simple to validate, simple to sham (swap real feedback for a canned replay). |
| Closed-loop, multi-variable/adaptive | Multiple sensors fused (HRV + EEG + GSR), adaptive/ML-driven actuation | More powerful in principle, much harder to validate — an adaptive controller can look like it's "working" by overfitting to noise. Needs a pre-registered fixed model or it becomes unfalsifiable by construction (the classic ML-in-the-loop trap). |
| Passive-only (sensing, no actuation) | Instrumentation with no stimulation at all | Genuinely useful as a *control condition* for every other architecture — establishes whether merely wearing a sensing device and attending to one's own state (a real, well-documented effect on its own) accounts for an apparent result. |
| Dyadic closed-loop | Two wearers' loops cross-modulate each other | Only trustworthy layered on top of the confound-analysis tooling already built — see 1C above. Structurally the most interesting architecture for actually testing a psi-specific claim, and the most confound-prone if done carelessly. |
| Sham-controllable (real/sham toggle built into the architecture, any mechanism) | Not a mechanism — a *requirement* that gets bolted onto whichever mechanism is chosen | Not optional. Every architecture above should be built with a sham mode from day one (matches `docs/protocols/g2_hrv_validation.md`/`g2_oracle_device.md` conventions already in this repo) — retrofitting blinding after the fact is much harder and a common source of retracted results in this exact research area historically. |

**Round 2 takeaway**: closed-loop single-variable biofeedback (evidenced) plus a genuine sham mode is the only architecture that's both trustworthy *and* buildable now. Multi-variable adaptive and dyadic architectures are more interesting long-term but need infrastructure (pre-registration discipline, confound tooling) that mostly already exists in this repo but hasn't been connected to a live device yet.

---

## Round 3 — Recombination ("mix-and-match")

Combining Round 1 survivors with Round 2 architectures, per the explicit instruction to mix-and-match rather than pick one item off a single list.

1. **Evidenced core + toggleable speculative arm.** Closed-loop HRV/tVNS biofeedback (evidenced, Track A) as the always-on core, with the near-field EM coupler (Track B, unproven) wired as a separately toggleable module that can be enabled/disabled per session. *Critique*: this is the single most defensible overall architecture in this whole document — it never bets device efficacy on the unproven part, and it makes the unproven part's contribution isolable via A/B rather than baked in. Doesn't require abandoning the coil work already done; just stops treating it as load-bearing.
2. **Passive pickup + confound killer, no active drive at all.** Wire the coil in receive-only mode, feed it and an ambient-reference channel into the existing `analyze_ambient_confounds.py`, log continuously during ordinary biofeedback sessions. *Critique*: cheapest possible way to touch the actual ψ-coupling question, zero emission so zero new safety-table burden, reuses tooling that already exists and is already tested. The clean "what would we do first, if starting purely from the psi question" answer.
3. **Dyadic pair, evidenced-metric readout.** Two devices, each running architecture 1's evidenced core, with a phase-coherent (SI5351 multi-output) *optional* cross-link between them, HRV/EEG coherence as the readout, confound tooling mandatory before any claim. *Critique*: the most scientifically interesting combination, and the most work — needs two working units, needs the confound pipeline actually exercised on real (not synthetic) data first (already flagged as outstanding in Track L's remaining work). Not a near-term build; a real Mk2+/Mk3 direction.
4. **Static field as a background covariate, not a driver.** Halbach ring worn passively (no active drive at all) during otherwise-ordinary biofeedback sessions, logged as a binary condition (ring in/out) across sessions. *Critique*: cheapest possible test of "does a static field change anything," uses inventory already massively over-stocked for the purpose (see prior roster), and importantly *fails safely* — a null result here is genuinely informative because there's no ambiguity about dose or exposure the way there is with active EM drive.
5. **tPBM as an entrainment-goal specialist, decoupled from the "psionic" framing entirely.** Near-infrared LED array, closed-loop only in the trivial sense of a session timer, targeting indefatigability specifically (the goal least well-served by anything else on this list). *Critique*: doesn't need to be in the same physical assembly as the psi-adjacent work at all — could be a separate accessory, and probably should be, so a real (if modest) Track-A effect doesn't get entangled with the Track-B experiment when interpreting results.

**Round 3 takeaway**: the strongest combinations all share one property — they keep the evidenced (Track A) and speculative (Track B) parts *structurally separable*, so results can be attributed to one or the other. The combinations that blend them inseparably (e.g., "the coil drives the biofeedback loop's stimulation") are exactly the ones the critique keeps flagging as hardest to interpret.

---

## Round 4 — Convergence, and why this is where the process stops

Beyond Round 3, further rosters would mostly be re-permutations of the same primitives (swap tVNS for tPBM in combination 1, swap Halbach for Persinger-coil in combination 4, etc.) rather than genuinely new mechanism classes — that's the signal to stop generating and converge, per the instruction to run "until exhausted."

**Kill list (named, declined, with reasons — not silently dropped):**
- Orgone-style dielectric stacking — no mechanism, no falsifiable prediction.
- Microtubule-quantum-coherence-style claims — no engineering interface at the device level.
- Zero-point/vacuum-energy coupling — inconsistent with accepted physics at achievable scales.
- Open-loop scripted stimulation as a *primary* architecture — not because the mechanism is bad, but because the architecture can't produce an interpretable result regardless of mechanism.
- Ambient Schumann/geomagnetic exposure as a *standalone* mechanism — no dose control, only usable as a logged covariate.

**Promoted, underrated in prior project docs:**
- tVNS and tPBM — real evidence, simple engineering, absent from every prior roster until this pass.
- Passive receive-only operation — already specified in the wiki, already unused, structurally the cleanest way to touch the actual psi question without any emission-safety burden.

**Structural finding that matters more than any single mechanism**: this project's docs have so far treated "the coil" as both the stabilizer *and* the psi-test instrument at once. Every combination that survived Round 3's critique instead **separates** those two jobs — an evidenced Track-A core doing the stabilizing, and a structurally isolable Track-B module (ideally passive) doing the psi-adjacent measurement. That separation, not any particular new component, is the actual output of this stress test.

**Explicitly not decided here**: which combination (if any) becomes a real next build. This document stops at "here's the stress-tested design space and what survives scrutiny" — matching this project's established pattern of flagging findings for the repo owner's call rather than silently adopting them.
