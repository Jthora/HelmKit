# Indefatigability entrainment — concept speculation, v0

**Status**: Speculative concept, 2026-08-06. Not a build commitment, not yet integrated into `docs/mk_ladder.md`/`docs/roadmap.md`. Direct follow-on from `mechanism_stress_test_rosters.md` at the repo owner's explicit request to reach for the highest-priority capability the stress test surfaces. No literature-grounding pass (in the style of `literature_grounding.md`) has been run on the specific claims below yet — that's the recommended next step, not something to treat as already vetted.

## 0. Reframe, stated plainly

"Indefatigability" — a state immune to fatigue — has no known mechanism, psi or otherwise. What's actually achievable, and what the rest of this doc means every time it says "indefatigability" as shorthand, is: **detect fatigue onset early and intervene to materially extend time-to-decline**, not eliminate fatigue. This matters because it changes the architecture from "broadcast a state and hope" (Round 2's worst-evidenced pattern) to a closed detect-and-intervene loop — which also happens to be the only architecture Round 2 found trustworthy.

**Central disclosure**: every lever below is Track A — real, evidenced, and requires nothing about ψ to be true. If you want a device that plausibly does *something* real for sustained cognitive performance, this is close to achievable with current-ish inventory. If the goal was specifically to demonstrate psionic capability, this doesn't do that — it's a different, parallel win. Worth deciding explicitly whether that's the win you want here, or whether you want the psi-linkage preserved even if weaker.

## 1. What actually causes measurable performance decline under sustained load

Kept brief — real citations belong in a proper literature-grounding pass, not invented here:

- **Vigilance decrement** — a real, replicated EEG/behavioral signature (rising theta, slowing reaction time, increasing lapses) under sustained attention tasks. This is the *thing being detected*.
- **Autonomic/vagal drift** — HRV declines and sympathetic tone rises under sustained cognitive/stress load; vagal tone is the standard proxy for resilience to this drift. tVNS (ear-clip transcutaneous vagus stimulation) has real, growing evidence for shifting this balance.
- **Circadian/light-driven alertness** — one of the best-evidenced levers in all of human chronobiology: bright, blue-enriched light suppresses melatonin and produces a measurable, fast-onset alerting effect, independent of sleep debt.
- **Gamma-band sensory entrainment (40 Hz)** — a live, mainstream research paradigm (audio/visual/tactile flicker at 40 Hz driving cortical gamma activity). Real and replicated as an entrainment effect; its link to *sustained-attention* performance specifically (as opposed to the neurodegeneration contexts it's mostly studied in) is plausible but not established — flagged honestly as the least-certain lever here.
- **Opportunity-cost framing of "mental fatigue"** (contemporary view, replacing the largely-discredited glucose-depletion story) — fatigue is increasingly understood as a motivational reallocation signal, not literal fuel exhaustion. Relevant because it suggests reward/salience cues (not just raw stimulation) may be part of an effective intervention arm, not just passive arousal boosts.

## 2. Proposed architecture: fatigue-onset detection + tiered intervention loop

Following Round 2's finding that architecture matters more than mechanism, and Round 3's finding that the best combinations keep evidenced and speculative layers separable:

```
[Sensing]  →  [Fatigue-onset classifier]  →  [Tiered intervention]  →  [log + sham-mode toggle]
   HRV/PPG        multi-signal, real-time         escalating arms          for every session
   EEG (if avail)  threshold or lightweight model
   skin temp
   ambient light
```

**Sensing layer**: HRV/PPG (already in the existing sensor roster), optionally EEG frontal channel if available, skin temperature, ambient light sensor (needed both as a confound control and because light-based intervention needs to know the starting condition).

**Detection layer — the actual hard problem**: not the transducers, the classifier. A real-time "is fatigue onset beginning" detector needs to fuse slow HRV trend + (if available) EEG slowing, with enough robustness to not fire on ordinary noise. This is genuinely the piece that needs real engineering and validation work, not assumed away — flagged explicitly so it doesn't get treated as a solved problem because the sensors themselves are simple.

**Intervention layer, tiered/escalating** (cheapest and least intrusive first):
1. **Paced-breathing prompt** — reuses the existing, evidenced L0/L1 biofeedback floor. First-line, no new hardware.
2. **Blue/bright light pulse** — NIR/blue LED array (small addition to the tPBM idea from the mechanism roster, dual-purposed), brief alerting pulse rather than constant exposure (constant bright light near the eyes at all times is neither pleasant nor how the alerting effect is normally delivered).
3. **tVNS burst** — ear-clip electrode, mild current, delivered as a short session rather than continuous.
4. **40 Hz gamma entrainment burst** (audio or tactile) — the least-certain arm, included because it's cheap to add and easy to isolate in an A/B design; should be the first arm dropped if early data doesn't support it.

**Sham/control, mandatory per Round 2**: every arm needs a real/sham toggle from day one — e.g. the light pulse fires but at a sub-threshold intensity, the tVNS delivers a sensation-matched but sub-therapeutic current, matching this project's existing `g2_hrv_validation.md`/`g2_oracle_device.md` blinding conventions.

## 3. Feasibility, cross-referenced against `alternative_architectures_roster.md` tags

| Component | Feasibility | Note |
|---|---|---|
| HRV/PPG sensing | 🟢 Now | Already in the existing sensor roster |
| Paced-breathing intervention | 🟢 Now | Already the L0/L1 floor, no new work |
| NIR/blue LED array | 🟢 Now / 🟡 Minor buy | LEDs + printed housing; may already have suitable LEDs, otherwise trivial purchase |
| tVNS ear-clip | 🟡 Minor buy | Small electrode + mild current driver, not currently in inventory |
| Ambient light sensor | 🟢 Now / 🟡 Minor buy | Common, cheap part |
| EEG frontal channel | Depends on existing sensor roster — check before assuming | Would need confirming against current inventory; not assumed here |
| 40 Hz entrainment (audio/tactile) | 🟢 Now | Reuses existing bone-conduction transducers / haptic actuators |
| Fatigue-onset classifier (software) | 🟢 Now, but real effort | No new hardware — the actual work is here, not in parts |

Net: this is one of the *cheapest* concepts to surface across every roster produced this session — almost everything needed is either already present or a minor purchase, and the honest hard part (the classifier and the validation work) is software/methodology, not hardware.

## 4. Where a psi-augmented version could hook in later — kept clearly separate

If a future passive-pickup measurement (per `mechanism_stress_test_rosters.md` Round 3, combination 2) ever showed a real, replicated signal, one speculative extension would be: treat any detected ψ-coupling signal as an *additional* input to the same fatigue-onset classifier, on the theory that the wiki's own framing (reducing "consciousness order parameter" noise) is at least directionally compatible with a fatigue-resistance goal. **This is not proposed as a near-term design decision** — it's flagged only so the architecture above doesn't have to be redesigned from scratch if that day comes; the input slot is compatible, nothing more. Stated once, not developed further, per the same discipline that's kept Track A and Track B separable throughout this document.

## 5. What this does NOT establish

- No literature-grounding pass has been run on the specific effect sizes/claims above (light-alerting magnitude, tVNS-fatigue literature, 40 Hz-and-attention specifically, vigilance-decrement detection accuracy) — this doc names real research areas, it does not yet verify the specific numbers the way `literature_grounding.md` did for the ganzfeld/Star Gate citations.
- No hardware has been built, no classifier has been trained, no session has been run.
- This is not currently reflected in `docs/mk_ladder.md`'s gates, `docs/roadmap.md`, or `docs/architecture.md`'s hardpoint mapping — it's a concept doc, not yet a roadmap commitment.

## 6. Recommended next step

A focused literature-grounding pass on exactly the four claim clusters in §1 (vigilance-decrement detection, tVNS/vagal-fatigue literature, light-alerting-effect magnitude and timing, 40 Hz gamma-entrainment-and-attention specifically) — same discipline as the existing `literature_grounding.md` — **before** any hardware or roadmap commitment, so the concept gets the same scrutiny the psi claims already received rather than being adopted on the strength of "sounds plausible."

## 7. Literature grounding results (2026-08-06, first cut — web search, not full primary-source reads)

Ran all four. One arm got upgraded, one got a real caveat, one hard problem got confirmed as genuinely hard rather than just under-engineered, one held up as expected.

**Vigilance-onset detection — confirmed hard, not just under-engineered.** Real cross-task, cross-participant deep-learning EEG classifiers exist (MLPNN, TCN, TCN-autoencoder architectures) but top out around **65–69% accuracy** — real, published, but modest. Useful specific finding: right inferior-parietal alpha power rises measurably **up to 20 seconds before** an attention lapse/error — a genuine early-warning precursor worth targeting specifically rather than just watching for the lapse itself. HRV+fNIRS multimodal classifiers (SVM/LDA/RF) are real but reported per-participant, not as a validated general model. **Update to §2**: don't understate this — 65–69% is the honest current ceiling for this kind of classifier in the literature, which means the fatigue-onset detector is likely to need per-user calibration, not a drop-in general model, at least initially.

**tVNS — HRV effect is solid; fatigue-specific claim needs a caveat.** Confirmed real, measurable HRV effects (RMSSD, pRR50, SDRR, HF-HRV all increase with taVNS, persisting into a recovery period) — the autonomic mechanism is real. But did **not** find a dedicated tVNS-and-fatigue-resistance meta-analysis, and found an explicit replicability caution in a 2025 review: "given the many studies with null effects of taVNS, it remains to be determined if results are replicable," attributed to inconsistent stimulation parameters across studies. **Correction to §1**: the HRV/vagal-tone mechanism is solid; "therefore extends time-to-fatigue" is a reasonable inference, not yet a directly-confirmed finding — should be stated as such rather than implied as settled.

**Blue/bright light alerting effect — confirmed strong, as expected.** Mechanism is precisely characterized (melanopsin-containing ipRGCs → suprachiasmatic nucleus → melatonin suppression within 1 hour of exposure, sustained with minimal recovery over several hours) and directly tied to performance: 6500K light exposure produced measurably faster reaction times specifically in sustained-attention tasks. Real guideline numbers exist (250 melanopic lux mEDI target for daytime circadian stimulation). This remains the strongest-evidenced lever in the whole concept.

**40 Hz gamma entrainment — upgraded from "least certain" to directly confirmed for this exact use case.** Found a very recent (2025, Imaging Neuroscience/MIT Press) controlled study — 62 healthy adults, one hour of 40 Hz audiovisual flicker vs. no-flicker control vs. randomized-flicker sham — that directly tested sustained-attention/vigilance performance, not the Alzheimer's/GENUS context this lever was flagged as being borrowed from. Result: the 40 Hz group had **better accuracy and faster reaction times** than both controls, with specific EEG correlates (lower delta power, higher lower-alpha functional connectivity, both correlating with better task performance). **Correction to §2**: this should no longer be "the first arm to cut if data doesn't support it" — of the four levers, it now has the most direct, recent, on-target controlled evidence. The tiering in §2 should be revisited: light-pulse and 40 Hz entrainment are now the two best-evidenced arms; tVNS's mechanism is solid but its fatigue-specific claim is the one that actually needs the caveat going forward.

**Net**: nothing in this pass killed a lever, but the relative confidence ordering changed — worth updating §2's escalation order before treating it as final.

## 8. Second-pass tVNS parameter research (2026-08-06) — a real nuance, not just a parameter table

Went deeper on tVNS specifically, since it's the arm with the most implementation choices (frequency, pulse width, current, electrode site) and the one already flagged with a replicability caution.

**Best-supported parameters found**: 10 Hz/250 µs, 10 Hz/500 µs, and 25 Hz/100 µs protocols at the **cymba concha** (the most-used electrode site in the literature reviewed, versus tragus) significantly increased **SDNN** versus sham in a randomized crossover trial. Current in the broader literature ranges 0.1–50 mA, with most effective protocols intentionally dosed *above* perceptual threshold (participants should feel it).

**The nuance that matters**: those same well-supported protocols increased **SDNN** (overall HRV) but did **not** significantly move **RMSSD** — the specific vagally-mediated HRV marker that §1's "autonomic/vagal drift" framing actually rests on. That's worth being precise about: the §1 tVNS claim was framed around vagal tone specifically, and the best-replicated acute parameters found here move a related-but-different quantity. Not a reason to drop the arm, but the concept doc's language should say "HRV" rather than imply a specifically-vagal mechanism is confirmed at these parameters.

**A gap in protocol *shape*, not just parameters**: the literature clusters into two shapes — brief acute single-session effect studies (minutes, the SDNN result above) and intensive clinical dosing protocols (e.g. one schizophrenia study: 30-minute sessions, twice daily, 5 days/week, for 2 weeks). A 2025 review states plainly that "the optimal dose duration for taVNS has not yet been systematically determined." §2's proposed architecture — a brief burst fired as an escalating, as-needed intervention during a fatigue-onset event — doesn't map cleanly onto either validated shape. That's not disqualifying, but it means the intervention protocol itself, not just the electrode parameters, would need its own validation pass rather than being assumed to inherit the acute-study evidence directly.

**Revision to §2/§3**: use cymba concha placement and a 10 Hz/250–500 µs or 25 Hz/100 µs starting protocol (real, sourced, not guessed), track SDNN as the primary metric rather than assuming RMSSD moves, and treat the brief-burst-as-intervention protocol shape itself as an open question — worth a dedicated small pilot before assuming it inherits either the acute-study or the clinical-dosing evidence base.

## 11. tVNS time-course — the brief-burst shape is more physiologically plausible than §8 left it (2026-08-06)

Follow-up specifically on whether a short, as-needed burst (rather than a sustained session) is a coherent intervention shape at all.

**Onset is fast, and effects outlast the stimulation itself.** HRV changes are reported as most prominent shortly after stimulation onset, with real effects reported from stimulation periods ≤10 minutes in healthy young adults — and one study found the effect (HF-HRV enhancement) **continued into the recovery period after stimulation stopped** (morning sessions specifically). More strikingly: the underlying neuromodulator changes taVNS triggers (via locus coeruleus-norepinephrine — the brain's primary arousal/alertness system, a real, well-characterized pathway, not a hand-wave) have been reported to persist **at least one hour, and sometimes up to 3–8 hours**, in the broader VNS literature. Acute cognitive benefits cluster most consistently in **executive function**, described as "small-to-moderate."

**This meaningfully de-risks the protocol-shape question §8 left open**: a brief burst plausibly *can* have a durable downstream effect via LC-NE persistence, rather than requiring continuous stimulation to matter — good news for the tiered, as-needed architecture in §2, even though the *specific* "burst fired at fatigue onset" protocol still hasn't been tested as a unit.

**One caveat that doesn't generalize the way it might look**: a hypertension-focused study reported "limited clinical impact after a single session" and that short stimulation "may be insufficient to overcome impaired autonomic regulation" — but that's a clinical population and a disease-outcome endpoint (blood pressure regulation in hypertensive patients), not the healthy-adult, acute-alertness question this concept targets. Worth not over-applying that pessimism here.

**Revision to §2**: the brief-burst intervention shape is now better-supported than §8 suggested — keep it in the design, but still worth a small pilot on the *specific* fatigue-onset-triggered-burst protocol rather than assuming it inherits the ≤10-minute acute-study evidence wholesale.

## 12. The §9 drowsiness wrinkle mostly resolves, and audio-only 40 Hz has real direct support (2026-08-06)

Two follow-ups on the 40 Hz arm.

**The drowsiness finding looks population- and context-specific, not a general property of 40 Hz stimulation.** GENUS's actual sleep-related findings, read more closely: 40 Hz stimulation in Alzheimer's patients **rescues disrupted circadian clock-gene expression** (CLOCK, BMAL1, PER2) in mouse models and **improves nighttime sleep quality** in human AD patients over months of daily use — i.e., it's *correcting* a chronically dysregulated circadian system in a specifically impaired population, not sedating a healthy person during waking use. That's a meaningfully different claim than "40 Hz makes people drowsy," and doesn't obviously predict anything about a healthy adult using a brief daytime burst. §9's caution about verifying the short-burst dose empirically still stands, but the drowsiness finding looks less like a fundamental tension with an alerting goal than it first appeared.

**Audio-only (binaural beat) 40 Hz has real, fairly direct support for exactly this use case** — a materially better match than the visual/audiovisual GENUS literature, which was studying AD neuroprotection, not daytime alertness. Found real reports: 40 Hz binaural beats "significantly increased arousal levels and led to a narrower focus of attention," described elsewhere as boosting "alertness and attention," with one exploratory pilot reporting a cognitive-score improvement from a 75% to 85% average under 40 Hz gamma entrainment. **Standard caveat for this literature, stated honestly**: binaural-beat research generally has a known mixed-replication track record — "some studies showing benefits while others have not observed effects on vigilance maintenance" — so treat this as real, direct, promising support, not a settled result.

**Revision to §2/§9**: downgrade the drowsiness concern from "a live tension with the alerting goal" to "worth empirically checking for the short-burst dose, but not expected to be a fundamental problem" — and note that the audio-only arm now has better-matched direct literature support than the visual arm does for this specific (non-AD, daytime-alertness) use case.

## 14. Correction to §12 — the drowsiness finding does NOT look population-specific after all (2026-08-06)

§12's conclusion was wrong, and it's worth saying so plainly rather than leaving it standing. A background research pass pulled the actual adverse-event tables from the GENUS Phase 1 trial (Cimenser/He et al., PMC9714926) instead of relying on summary statements, and the real numbers contradict §12's "population- and context-specific" read:

**Drowsiness/sleepiness occurred in 38.4% of young cognitively-normal participants and 40% of older cognitively-normal participants** in the single-session Phase 1 trial — markedly *higher* than the 6.2% rate in the mild-AD group. That's the opposite of §12's hypothesis that the effect was specific to a circadian-dysregulated (AD) population; if anything, healthy participants showed the effect more, not less. §12's circadian-clock-gene-rescue mechanism may still be real and relevant to the *sleep-quality* findings in AD patients over months of use, but it does not explain away same-session drowsiness in healthy people, which is a different phenomenon happening on a different timescale.

**Also newly found**: the larger-scale Phase 2 OVERTURE trial reported headache (21.7% active vs. 10.7% sham) and tinnitus (15.2% vs. 0%) — adverse events that didn't appear at all in the smaller Phase 1/2A trials. The safety profile expanded with trial scale, which is itself worth remembering as a general pattern, not just a 40 Hz-specific one.

**Correction to §2/§9's revision**: restore drowsiness to a live, real consideration for the short-burst dose specifically — not resolved, not population-specific, a genuine open question that needs its own check rather than an assumed-benign one. This doesn't kill the 40 Hz arm (the sustained-attention benefit and the epilepsy-safety data are still real and still hold), but the alerting-vs-drowsiness tension flagged in §9 was right the first time, and §12's attempt to explain it away was a mistake worth flagging rather than quietly leaving uncorrected.

## 9. 40 Hz entrainment — safety check, since it got promoted without one (2026-08-06)

§7 upgraded 40 Hz entrainment on efficacy grounds without ever checking its safety profile specifically — worth closing that gap before it goes any further.

**Photosensitive epilepsy risk is real but frequency-dependent, and 40 Hz sits outside the danger band**: the most provocative flash frequencies are 3–30 Hz, with **15–25 Hz carrying peak risk** (some sources narrow this to 15–20 Hz); rare individual susceptibility has been reported as low as 5 Hz and as high as 84 Hz, so no frequency is a zero-risk guarantee. 40 Hz specifically has been reported to *not* produce neuronal hyperexcitability in experimental conditions. **Important caveat**: broadcast/web accessibility regulations conservatively flag the *entire* 2–55 Hz range for caution regardless of the underlying risk curve — meaning 40 Hz is empirically safer than the 15–25 Hz peak but still sits inside the broad range regulators treat cautiously as a blanket rule, not a frequency regulators have carved out as unambiguously exempt.

**Real, directly-on-point clinical safety data exists**: GENUS (gamma entrainment using sensory stimuli, the MIT Tsai-lab-associated 40 Hz protocol) has been tested in actual clinical trials, including **volunteers with epilepsy specifically** — the highest-risk population for exactly this concern — with independent epileptologist EEG review. Result: well-tolerated across Phase 1 and Phase 2A studies, no serious adverse events, no seizure activity, even in the epilepsy-patient subgroup. This is about as strong a direct safety signal as this kind of literature search can produce.

**One honest wrinkle worth flagging, not glossing over**: the most commonly reported side effect across these trials was **drowsiness** — mildly counterintuitive for a device meant to *increase* alertness. Most GENUS protocols use long, often overnight/continuous exposure sessions (the Alzheimer's-research context this technique originates from), which is a very different exposure shape than the brief, tactical, escalating burst proposed in §2 — so the drowsiness finding may not transfer directly, but it's a real reason to verify alertness (not just safety) empirically for the *short-burst* protocol specifically, rather than assume the accuracy/reaction-time benefit from §7's cited study (which used a full one-hour continuous session, not a brief burst) automatically holds at a much shorter dose.

**Audio-only entrainment**: the epilepsy-risk mechanism is specifically visual-cortex photic hyperexcitability; audio-only 40 Hz entrainment (already in the design as one of the tiered arms) is understood to carry substantially lower risk by that specific mechanism, though this pass didn't find a dedicated audio-only seizure-risk study to confirm that directly — worth treating as "very likely much lower risk," not "confirmed zero risk," and screening for it explicitly regardless.

**Revision to §2**: 40 Hz entrainment's efficacy case is now real, but so is a reason to test the *short-burst* dose specifically for both safety and actual alerting effect (not just borrow the one-hour continuous-session result), and to keep photic screening (already an existing Mk1 gate, G2-b, per `docs/safety.md`) explicitly applied to this arm rather than assumed unnecessary because 40 Hz is "outside the danger band."

## 10. Beating the classifier ceiling — the real answer is personalization, not more sensors (2026-08-06)

**Multimodal fusion (EEG + pupillometry/eye-tracking) is qualitatively well-supported** — reviewed literature consistently states fusion outperforms single-modality for vigilance-type states. But the one specific reported number found (late fusion of EEG + eye-tracking on a binary attention task: 0.609–0.675 accuracy, 95% CI) doesn't clearly beat the 65–69% EEG-only ceiling from §7 — worth being honest that "fusion helps" is a well-supported qualitative claim in this literature without yet a dramatic quantitative win found in this pass. Adding pupillometry is still worth doing (cheap relative to the sensor roster already planned), just not a silver bullet for the accuracy ceiling on its own.

**The actual silver bullet, found by accident while checking a different question**: **personalized, per-user models dramatically outperform general cross-participant models** — one study reports personalized supervised classifiers reaching **97.7% mean accuracy (AUC 0.997)**, and even a simpler unsupervised approach (flagging deviation from an individual's own established baseline, no labeled fatigue data at all) reached **96.7% AUC**. That's not an incremental improvement over the 65–69% cross-task ceiling — it's a different regime entirely. "Personalized models showed a big improvement... for many participants, the performance almost doubled" versus global/cross-subject classification.

**This changes the actual recommended design**, more than any other single finding in this pass: don't build toward a general-purpose fatigue-onset classifier that works out-of-the-box for any wearer — build toward a **short per-user calibration/baseline-establishing session** (exact optimal duration wasn't found in this pass, but the literature describes it as achievable with "short supervised warm-up sessions," not extensive data collection) that the device runs once, or periodically, per wearer, then detects fatigue onset as *deviation from that individual's own established baseline* rather than trying to match population-level fatigue signatures. This reframes §2's "actual hard problem" from "build an accurate general classifier" (which the 65–69% ceiling suggests may be a genuinely hard ceiling to push past) to "build a good onboarding/calibration flow" (a more tractable, well-precedented engineering problem).

**Revision to §2/§3**: add an explicit per-user calibration session to the architecture (a short baseline-recording flow before the device is used for real), and reframe the fatigue-onset classifier as anomaly/deviation-detection against an individual baseline rather than a general population classifier — this is now the best-supported design choice in the whole concept, not merely one option among several.

## 13. Calibration duration — the real-world number is weeks, not minutes (2026-08-06)

§10 found personalization dramatically outperforms general models but didn't find how *long* calibration needs to take. Checked what real, shipped, high-volume consumer wearables actually use — a better proxy for what's practically achievable than a lab study's "short supervised warm-up."

**Real deployed products calibrate over weeks to months, not minutes**: Garmin's HRV-status feature needs roughly **3 weeks** of nightly data before it's reliable (showing "unavailable" or fluctuating unpredictably before then); WHOOP uses approximately a **30-day** baseline window; Oura's readiness score weights a 14-day recent-trend window against a full **3-month** baseline. All three treat this as an ongoing, continuously-updated process, not a one-time setup step.

**This is a real tension with §10's framing, worth stating plainly rather than smoothing over**: the lab studies behind the 97.7%-accuracy personalized-classifier finding describe "short supervised warm-up sessions," but the products with the most real-world deployment experience at exactly this problem (individual physiological baselining for a consumer wearable) converge on weeks-to-months, not a single onboarding session. The honest read: a short session likely *starts* a usable calibration, but the accuracy numbers from §10's lab studies may assume more calibration data than a single sit-down session provides — the device probably needs to ship with an explicit "accuracy improves over the first few weeks of normal use" expectation rather than promising lab-grade personalization on day one.

**Concrete, reusable operational numbers found**: baselines are typically computed as a rolling **7-day moving average**, with a **1–2 month** window establishing "normal range"; **10–20%** day-to-day deviation is treated as ordinary noise, while a **20–30% sustained drop over several days** is treated as a meaningful signal. These are real, borrowable thresholds for tuning the fatigue-onset classifier's sensitivity rather than picking an arbitrary cutoff. Also worth adopting operationally: measure at the same time and in the same context each day/session, since HRV-based baselining is sensitive to measurement-context consistency.

**Revision to §2/§3**: keep the short initial calibration session (still useful as a cold-start), but explicitly frame accuracy as improving over the first several weeks of ordinary use rather than being lab-grade from session one, and adopt the 10–20%-noise / 20–30%-signal deviation thresholds as the starting point for the fatigue-onset classifier's sensitivity tuning.
