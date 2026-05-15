# HelmKit Modes — Cognitive-Optimization Mode Roster

**Status:** Mk1-era roster, May 2026. Operator-facing modes the HelmKit substrate is intended to support across its Mk0 → Mk3 evolution. Two modes are Mk1-scope flagships (Tranquil, Combat); the rest are deferred-but-architected so the hardware and sensor decisions made now don't foreclose them.

> **The framing.** HelmKit is not a single-purpose device. It is a **techno-mage substrate** with mode-presets for distinct cognitive-optimization targets. A *mode* is a tuple `(target state, sensor loadout, feedback rules, optional stim preset, validation endpoint)` that closes a loop driving the wearer's measured state toward the target.

---

## 1. The mode-tuple schema

Every mode declares:

| Field | Meaning |
|---|---|
| **Target state vector** | Measurable physiological / motor / cognitive markers the mode is trying to produce |
| **Sensor loadout** | Which sensors the mode reads. Subset of the full sensor roster. |
| **Feedback rules** | What the device does in response to live sensor readings. May include audio cue, haptic, LED, visual HUD, or a state transition. |
| **Optional stim preset** | (Mk1.5+) Bifilar-coil drive waveform, if any. Mk1 modes all run with stim = none / sham. |
| **Validation endpoint** | The specific G1/G2/G3 evaluation that confirms this mode "works." |
| **Mk gate** | The Mk-generation at which this mode first ships. |

This schema is intentionally identical to how the build plan thinks about `(stim payload, sham, evaluation)` triples — modes plug into the existing G1/G2/G3 framework.

---

## 2. The mode roster

### 2.1 Tranquil — *flagship A (Mk1 default)*

**Target state.** High HRV (RMSSD ↑); parasympathetic-dominant; alpha-theta cortical (deferred to Mk2 EEG); EDA tonic level low; peripheral skin temperature warm; respiration slow + diaphragmatic.

**Sensor loadout.** PPG (MAX30102) + EDA + skin-temp + (optional EEG at Mk2).

**Feedback rules.**
- L0 paced breath: 6 bpm bone-conduction audio cue + LED breathing.
- L1 HRV-coherence rendering: live coherence ratio audible as a harmonic locked to breath tone.
- L2 30-min session container: settle → onboarding → active → closure → reflection.

**Stim preset.** Mk1: none / sham. Mk1.5+: bifilar coil at 7.83 Hz envelope (the Schumann-Persinger pattern).

**Validation endpoint.**
- G1: dual-MCU + sham-equivalence gates pass.
- G2: 4-week ABAB, composite of ΔRMSSD-morning + ΔPSS-weekly + Δsleep-onset.
- G3: sham-controlled, cold-pressor at minute 22, time-to-coherence primary.

**Mk gate.** Mk1.

**Use case.** Pre-sleep, post-stress recovery, base ANS regulation, meditation scaffold.

---

### 2.2 Combat — *flagship B (Mk1 stretch)*

**Target state.** Flow under exertion. Operationally:
- Vagally-engaged-but-not-collapsed HRV (not the panic-zone collapse, not the rest-zone passivity).
- Relaxed antagonists during strike sequences — shoulder, jaw, forearm EMG <10% MVC at rest *between* strikes.
- Sharp reaction time — no degradation pre vs post.
- Rhythmic tactical breath — nasal, 4-4 or 4-8 box pattern between rounds.
- Stable balance — IMU sway under personal threshold.
- Fast inter-round HRV recovery — RMSSD returns to >70% of baseline within 60s.

**Sensor loadout.** PPG (MAX30102) + EMG (one channel, dominant-side anterior deltoid as primary) + IMU (head + optional wrist) + (optional EDA on forearm) + (optional skin-temp).

**Feedback rules.**
- **Tension alarm.** EMG > threshold for >2 s during rest → haptic buzz or audio chirp. *Teaches you to relax under load.* This is the single most valuable feedback in the whole project.
- **Strike-cadence track.** Optional rhythmic auditory carrier you lock onto. Aligned with rhythmic-auditory-cuing motor-learning literature.
- **Round-recovery scoring.** Between rounds, score time-to-baseline-HRV.
- **Guard-recovery time.** IMU detects strike → return-to-guard latency reported in ms.
- **Breath metronome.** Audio tick locked to prescribed pattern; silent when compliant.

**Stim preset.** Mk1: none / sham. Speculative future: beta-band entrainment, or gamma 40 Hz, or per-wearer learned. **Defer all stim claims; ship the biofeedback loop first.**

**Validation endpoint.**
- G1: EMG calibrated against personal MVC; IMU strike-velocity validated against video; sham mode sensory-indistinguishable.
- G2: 4-week within-subject ABAB on your own training. Endpoint: composite of (strike velocity at fixed shoulder EMG) + (round-recovery HRV time) + (post-session RT delta) + (subjective fight-feel Likert).
- G3: sham-controlled with sparring partners; exertion stressor (90s burpees) at minute 22 replacing cold pressor.

**Mk gate.** Mk1 stretch (depends on EMG module + electrodes + the IMU-from-inventory plus the firmware to fuse them).

**Use case.** Backyard martial-arts practice, sparring prep, athletic performance training. **Operator's primary use case.**

---

### 2.3 Focus / Deep Work — *Mk2*

**Target state.** Sustained attention; frontal beta engaged; alpha suppressed; HRV stable but not maximally coherent (focus is mildly sympathetic); low blink rate; minimal task-switching evidence.

**Sensor loadout.** PPG + EEG (frontal) + (optional eye-tracking via camera).

**Feedback rules.**
- 40 Hz gamma binaural underlay (well-tolerated; modest evidence for attention).
- Pomodoro cadence (25-on, 5-off) embedded in audio environment.
- Mind-wander alert: EEG-detected alpha rebound or task-negative spectral signature → soft chime.

**Stim preset.** Defer.

**Validation endpoint.**
- G2: task-completion-rate ABAB on real coding/writing work; subjective focus Likert.
- G3: sham-controlled cognitive battery (PVT, Stroop) post-session vs sham.

**Mk gate.** Mk2 (requires EEG which is Mk2-scope).

**Use case.** Coding, writing, study, focused-craft work.

---

### 2.4 Creative / Ideation — *Mk2*

**Target state.** Diffuse attention; relaxed alpha-theta dominant; default-mode-network signatures; low arousal; permissive associative state. *Opposite of Focus mode.*

**Sensor loadout.** PPG + EEG.

**Feedback rules.**
- Soft binaural at low theta (~6 Hz).
- Long phase blocks (no pomodoro chunking).
- Low cue density — minimal interruption.
- Optional alpha-theta crossover detection (Hardt-style biofeedback for creative incubation).

**Stim preset.** Defer.

**Validation endpoint.**
- G2: idea-generation rate (think AUT — alternate uses task — pre/post comparisons) ABAB.
- G3: sham-controlled AUT cohort.

**Mk gate.** Mk2.

**Use case.** Brainstorming, art, problem incubation, lyric / design / writing-flow work.

---

### 2.5 Vigilance / Sentinel — *Mk2*

**Target state.** Sustained low-grade alertness over long duration. Not high-arousal — endurance, not intensity. ANS in moderate sympathetic but stable; no drift toward drowsiness; reaction time preserved.

**Sensor loadout.** PPG + EDA + IMU (head — drowsiness via head-nod / micro-sleep detection) + reaction-time tactor.

**Feedback rules.**
- Long-duration low-stim alert audio bed.
- Drift-detection alarm: if HRV trends toward sleep-onset profile, sharp alert.
- Periodic random reaction-time probe (the PVT pattern); slow RT triggers escalation.

**Stim preset.** Defer.

**Validation endpoint.**
- G2: long-task vigilance metrics (1-hour sustained-attention task); subjective fatigue Likert.
- G3: sham-controlled long-task with vigilance decrement comparison.

**Mk gate.** Mk2.

**Use case.** Night drive, watch duty, long-form security / sentinel work, all-night work sprints.

---

### 2.6 Social / Charisma — *Mk2*

**Target state.** Porges "social engagement system" engaged — vagal tone on; warm peripheral perfusion; relaxed jaw / face; open posture (IMU-detectable); steady prosody-friendly breath.

**Sensor loadout.** PPG + skin-temp + IMU (posture) + (optional voice analysis via mic for prosody jitter).

**Feedback rules.**
- Pre-session vagal-ramp via Tranquil-mode breath pacer.
- Live posture nudge — haptic cue if IMU detects slouch / closed posture.
- Optional voice-prosody feedback during practice (mic + DSP).

**Stim preset.** Defer.

**Validation endpoint.**
- G2: pre/post social-event self-report; observer ratings if available.
- G3: standardized social-stress task (e.g., TSST — Trier Social Stress Test) sham-controlled.

**Mk gate.** Mk2.

**Use case.** Public speaking, interviews, dates, networking, first impressions.

---

### 2.7 Recovery / Healing — *Mk2*

**Target state.** Maximum parasympathetic; near-sleep cortical signatures; reduced peripheral perfusion (cool extremities, classic recovery-state); high tonic vagal HRV; minimal sympathetic activity.

**Sensor loadout.** PPG + skin-temp + (EEG for sleep-stage detection in Mk2).

**Feedback rules.**
- Deepest-possible breath pacer (~4 bpm).
- Sleep-adjacent audio bed (delta-leaning binaural, very low intensity).
- Skin-temp-warm-then-drop trajectory cued (the natural pre-sleep thermal pattern).

**Stim preset.** Defer.

**Validation endpoint.**
- G2: sleep-onset latency, sleep-quality Likert, morning-RMSSD ABAB.
- G3: sham-controlled actigraphy-validated sleep metrics.

**Mk gate.** Mk2 (overlaps strongly with Tranquil; may merge or specialize).

**Use case.** Post-illness, jet lag, injury recovery, scheduled deep-rest blocks.

---

### 2.8 Dyadic / Co-regulation — *Mk3*

**Target state.** Two wearers synchronize physiology — HRV cross-coherence, breath entrainment, possibly EEG inter-brain coupling.

**Sensor loadout.** PPG + EEG + low-latency wireless link between two HelmKit units.

**Feedback rules.** Each wearer hears a render of the *other's* coherence layered with their own. The system rewards mutual entrainment.

**Stim preset.** Mk3 — bifilar coils run identical waveform on both units for the N²-superradiance test.

**Validation endpoint.** Dicke superradiance test: 4× output at N=2 vs linear sum null.

**Mk gate.** Mk3.

**Use case.** Therapy dyads, partner training, synastry-pair experiments, **the F-test for the psion-quasiparticle hypothesis.**

---

### 2.9 Future / speculative — *deferred*

Architected for; not on the near-term roadmap:

- **Trance / Ritual** — long-form theta-gamma protocol; possibly stroboscopic + audio + stim.
- **Lucid-Dream Onset** — REM-detection-triggered subtle audio/tactile cues.
- **Pain Modulation** — vagal-tone training combined with stim payload; clinical-trajectory mode.
- **Empathic / Co-regulation (clinical)** — therapist + client dyad version of 2.8.

---

## 3. The mode-by-sensor matrix

Which sensors each mode requires. ✅ = primary; ◐ = optional / improves; — = not used.

| Sensor | Tranquil | **Combat** | Focus | Creative | Vigilance | Social | Recovery | Dyadic |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **PPG (MAX30102)** ✅ have | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **EMG** | — | ✅ | — | — | — | ◐ | — | — |
| **EDA / GSR** | ✅ | ◐ | ◐ | — | ✅ | — | ◐ | — |
| **Skin-temp (IR or contact)** | ◐ | ◐ | — | — | — | ✅ | ✅ | — |
| **IMU 9-DoF** ✅ have | ◐ | ✅ | — | — | ✅ | ✅ | — | ◐ |
| **EEG** (Mk2) | ◐ | — | ✅ | ✅ | ◐ | — | ✅ | ✅ |
| **RT tactor / button** | — | ◐ | ◐ | — | ✅ | — | — | — |
| **Mic / voice** | — | — | — | — | — | ◐ | — | — |
| **Camera / eye** | — | ◐ | ◐ | — | ◐ | — | — | — |
| **DS18B20 contact temp** ✅ have | ◐ | — | — | — | — | ◐ | ◐ | — |
| **Polar H10 chest ECG** | ◐ G1 | ◐ G1 | — | — | — | — | — | — |

**Reading this matrix for purchase decisions:** any sensor that lights up under both Tranquil **and** Combat is high-priority for Mk1. Anything that only lights up under Mk2+ modes can wait.

---

## 4. The Mk1-scope decision

For Mk1 we ship **Tranquil + Combat** as a two-mode device. Everything else is documented-but-deferred.

Tranquil's loop is mostly already covered:
- PPG → already have (MAX30102).
- Breath pacer → bone-conduction audio (already have drivers).
- Session container → firmware state machine.
- Sham-equivalence → existing six-channel spec.

Combat's loop adds:
- EMG (1-ch) → the new buy.
- IMU on head → already have (3× MPU9250).
- Optional skin-temp → already have (DS18B20, slow but free); upgrade path is MLX90614 or MAX30205.
- Optional EDA → not in inventory; new buy if budget allows.

**See [sensor_roster.md](sensor_roster.md) for the purchase-roster companion to this document.**
