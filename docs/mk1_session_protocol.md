# Mk1 — Session Protocol (the wearer-benefit floor)

This document specifies the **session structure and biofeedback layers that run on every Mk1 wear-session, regardless of stim payload state.** It is the wearer-benefit deliverable. The bifilar coil stim payload sits *on top* of this floor; whether or not the stim does anything, this protocol delivers evidence-graded stabilization on its own merits.

The same protocol runs on **active and sham arms** of the Mk1 RCT. Only the stim payload differs. This means the sham wearer is not deprived of benefit; the RCT isolates the stim payload's marginal contribution above an already-working device.

> **Cross-references.** [`mk1_buildplan.md §4.0`](mk1_buildplan.md) defines the three-grade pass model (G1 engineering / G2 wearer-benefit / G3 stim-payload) that this protocol satisfies. [`mk1_f2_probe.md`](mk1_f2_probe.md) supplies the parallel record-side instrumentation. [`roadmap.md`](roadmap.md) defines how this protocol propagates as the spine through Mk1.5 → Mk2 → Mk3.

---

## 1. Layered architecture

Five layers, **L0 through L4**. Mk1 implements L0, L1, L2. Mk2 adds L3 (neurofeedback), L4 (state-aware container adaptation). The session-protocol module is the same code path across Mk levels; later Mks add layers, they do not replace lower ones.

| Layer | Mk | What | Evidence base | Cost at Mk1 |
|---|---|---|---|---|
| **L0** Resonance breath pacer | Mk1+ | ~6 bpm audio + LED breathing cue running through the entire active period | Highest-evidence stabilization tool in modern psychophysiology (Lehrer & Gevirtz resonance-frequency breathing, $d \approx 0.4$–$0.8$ for stress / anxiety endpoints) | ~30 LOC, zero hardware |
| **L1** Closed-loop HRV-coherence feedback | Mk1+ | Live HRV coherence metric computed at 1 Hz, rendered as slow tone-pitch modulation (audio) or LED brightness (visual) | Strong (HeartMath / biofeedback meta-analyses, Goessl et al. 2017, $d \approx 0.3$–$0.6$) | ~50 LOC + small DSP module, zero hardware |
| **L2** Session container | Mk1+ | Structured 30-min protocol: settling → onboarding → active → closure → reflection | Standard in mindfulness/biofeedback protocols; small but real adherence benefit | Pre-recorded audio + state machine |
| **L3** EEG neurofeedback | Mk2 | Alpha / theta-ratio or alpha-band power rendered as second audio channel | Strong (Gruzelier et al., alpha-theta neurofeedback) | Requires Mk2 EEG channel |
| **L4** State-aware container adaptation | Mk2 | Container branches on detected wearer arousal at session start | Emerging; no large meta-analysis yet | Requires Mk2 fusion compute |

---

## 2. L0 — Resonance breath pacer

### Specification
- **Pacing rate:** default 6 breaths per minute (0.1 Hz). Wearer-adjustable in `5.5`–`6.5` bpm range during onboarding; locked for the rest of the session.
- **Inhale : exhale ratio:** 4 : 6 (40% inhale, 60% exhale). Pre-registered; not user-adjustable in Mk1.
- **Render channel:** bone-conduction audio (gentle sine sweep, 200 Hz → 300 Hz on inhale, 300 Hz → 200 Hz on exhale) AND status LED breathing pattern in synchrony.
- **Sample rate:** 50 Hz update on both channels.
- **Onset / offset:** fades in over 5 s at active-period start, fades out over 5 s at active-period end. Not present during settling, closure, or reflection phases.

### Rationale
Resonance-frequency breathing is the single most robust autonomic-stabilization intervention in the modern psychophysiology literature. It is mechanism-neutral, requires no theory of psionics to work, and has effect sizes ($d \approx 0.4$–$0.8$) larger than any plausible psion-mediated effect at Mk1's $F^2$ envelope. Running it as the floor of every session means the wearer gets *real benefit* on every session even if every stim payload turns out null. This is the engineering realization of the §0a "wearer benefit regardless of framework outcome" mission.

### Sham behaviour
**Identical on active and sham arms.** L0 is *not* the stim payload; it is the protocol floor. The wearer on a sham session still gets resonance-frequency breath pacing. This raises the *floor* on both arms but does not confound the active-vs-sham contrast on the stim payload.

---

## 3. L1 — Closed-loop HRV-coherence feedback

### Metric: HRV coherence

At each 1 Hz update tick:

1. Compute beat-to-beat intervals from PPG over the trailing 60 s window.
2. Apply Lomb–Scargle periodogram (handles uneven sampling) to RR-interval series.
3. Define coherence ratio:
$$\text{Coherence} = \frac{P_{\text{LF peak}}}{P_{\text{total}}}$$
where $P_{\text{LF peak}}$ is integrated spectral power in a ±0.015 Hz window around the dominant peak in 0.04–0.26 Hz, and $P_{\text{total}}$ is integrated 0.0033–0.40 Hz. Standard HeartMath-style coherence; well-defined; replicable.
4. Smooth with a 5 s EMA. Map smoothed value to a perceptual scale via a fixed lookup.

### Rendering

- **Audio channel (default):** the bone-conduction L0 tone gains a secondary low-amplitude harmonic whose pitch tracks coherence. High coherence → harmonic in tune with the breath tone (consonant). Low coherence → harmonic detuned by up to a minor third (mildly dissonant). Wearer perception: "the tone sounds more pleasant the more coherent I am."
- **Visual channel (optional):** indicator LED at `HP-F` modulates brightness with coherence (smoothed; no flicker faster than 0.5 Hz). Disabled by default to avoid photic-driving artifacts mid-session.

### Closed-loop nature
This is closed-loop **biofeedback rendering**, not closed-loop stim. The stim payload schedule remains open-loop at Mk1 per the safety architecture; L1 only modulates the *wearer-facing perceptual signal*. MCU-A handles L1 in software; MCU-B's stim-disable interlock is unaffected.

### Sham behaviour
**Identical on active and sham arms.** Same metric, same rendering. The wearer's own HRV coherence is the driving signal; it has nothing to do with whether the coil is energized.

### Failure modes
- If PPG signal quality drops (motion artifact, sensor decoupling) for > 5 s, L1 fades the harmonic to silent and the indicator LED holds at last-good level. Logged to NDJSON as `l1_dropout` event. L0 continues unaffected.
- If the metric computation overruns its 1 s budget, the missed tick is skipped (no late renders). Budget headroom on a Pi Zero 2 W is ~400 ms; the metric is comfortably real-time-safe.

---

## 4. L2 — Session container

### Phases

| Phase | Duration | Audio | Stim | Sensing |
|---|---|---|---|---|
| **Settling** | 3 min | Pre-recorded guided audio: posture, intention, baseline-attention cue. No L0 tone. | Off. | Logging on; baseline HRV collected. |
| **Onboarding** | 2 min | L0 breath pacer fades in. Brief guided audio confirms wearer is locked into the pace. | Off. | Logging on; baseline RMSSD computed from final 60 s of this phase. |
| **Active** | 20 min | L0 + L1 running. No spoken content. | **Stim payload runs** (active arm) or **does not** (sham arm). MCU-A holds GPIO-stim-enable per arm. | Full logging including $F^2$ probe. |
| **Closure** | 2 min | L0 + L1 fade out over 30 s; pre-recorded guided closure audio: gentle attention release, transition cue. | Off. | Logging on; recovery RMSSD collected. |
| **Reflection** | 3 min | Silent or optional ambient track. Wearer instructed to complete post-session Likert panel on companion device or paper card. | Off. | Logging on (passive). |

**Total: 30 min.**

### State machine

Implemented in `software/helmkit_mk1/protocol.py`. States transition on wall-clock timer; no transition is gated on a wearer action (avoids self-pacing confound). Transitions are logged as NDJSON `phase` events. The state machine drives a hardware `GPIO-stim-allow` line that is the *software side* of the existing MCU-B interlock; MCU-B independently confirms phase=`active` and arm=`active` before passing stim.

### Sham behaviour
**Container is identical on active and sham arms.** Only the stim-enable line differs in the `Active` phase. Settling, onboarding, closure, reflection audio scripts are byte-identical across arms.

---

## 5. Pre-session and post-session Likert panel

Pre-registered secondary endpoints. Collected on a companion device (phone web form or paper card) immediately before settling and immediately after reflection.

| Item | Scale | Direction |
|---|---|---|
| Calm | 1 (agitated) – 7 (deeply calm) | Higher = better |
| Energy | 1 (drained) – 7 (vital) | Higher = better |
| Mental clarity | 1 (foggy) – 7 (clear) | Higher = better |
| Intrusive thoughts | 1 (none) – 7 (constant) | **Lower** = better |
| Body comfort | 1 (uncomfortable) – 7 (relaxed) | Higher = better |

Plus one free-text field, 240-char max, for post-session only: "Anything notable about this session?"

**Next morning** (within 12 h of session): single-item via companion device:

- Sleep quality last night: 1 (terrible) – 7 (excellent).

All Likert responses are logged to NDJSON in the session record under `subjective.{pre,post,next_morning}`. Free-text is logged hashed-with-salt for privacy but recoverable from a local key.

---

## 6. Stressor protocol (for the single-session G3 RCT only)

The G3 framework-contribution endpoint requires a standardized stressor. The trait-level G2 endpoint does **not** use a stressor; G2 is measured over a four-week ABAB without stressor sessions.

### Cold pressor — **the locked choice**

- **Apparatus:** insulated bucket, 4 L of water at 4 ± 1 °C, calibrated thermometer.
- **Procedure:** wearer's non-dominant hand submerged to wrist for 90 s. Stop early on wearer request (recorded as early-stop event; session retained but flagged).
- **Timing within session:** stressor occurs at minute 22 of the `Active` phase, i.e. 2 min before transition to `Closure`. The remaining 2 min of `Active` plus all of `Closure` and `Reflection` constitute the recovery window.
- **Time-to-coherence:** wall-clock seconds from hand-removal to the smoothed HRV coherence metric crossing back above its pre-stressor 60 s baseline. Computed offline from NDJSON; not used to drive any in-session rendering.

### Why cold pressor
- Validated for autonomic reactivity studies (Lovallo 1975 onwards; thousands of citations).
- Clean, rapid recovery curve (typically 3–8 min in healthy adults).
- Self-administrable, no operator needed.
- No psychological-content confound (unlike Stroop, mental arithmetic, TSST).
- Reproducible across sessions and across wearers.

### Stressor inclusion in G2 vs G3
- **G2 (wearer-benefit, trait-level, 4-week ABAB):** *no stressor.* Daily sessions are stressor-free; primary endpoint is morning resting RMSSD trend + weekly Likert.
- **G3 (stim-payload, single-session RCT):** *cold-pressor at minute 22.* Single-session blinded active-vs-sham comparison.

These are separate study arms drawing from the same session protocol; the wearer is informed pre-enrolment which arm any given session belongs to (G3 sessions are explicitly stressor-disclosed; G2 sessions are stressor-free).

---

## 7. Sham equivalence — what counts as a valid sham

A Mk1 sham coil must be indistinguishable from active on **every** sensory channel the wearer can detect:

| Channel | Verification |
|---|---|
| **Visual** | Same enclosure, same indicator LEDs in identical states, same cable management. |
| **Mechanical** | Same weight, same temple-mount feel, same head pressure. |
| **Audible** | Spectrum-analyzer at wearer's ear position with active vs sham coils installed — no detectable difference at any tone the wearer can hear (20 Hz – 18 kHz). The Class-D amp's switching artifacts, the SI5351 reference oscillator, and any envelope tones must not leak through the enclosure differently between active and sham. |
| **Thermal** | Equivalent dummy load in the sham enclosure dissipating identical wattage to the active coil's measured average — IR camera before/after a 30 min session shows equivalent skin warming. |
| **EMI** | RM3100 magnetometer at temple position records similar baseline noise levels in both arms (the *active arm* emits more, by design — but the *enclosure leakage* and *switching emissions* outside the bifilar coil's intended near-field should match). |
| **Vibration** | Accelerometer on the temple boom records no detectable mechanical signature from the Class-D switching in either arm. |

Sham-equivalence verification is in the [`mk1_buildplan.md §5`](mk1_buildplan.md) G1 exit checklist and must be passed before any G3 session is run.

---

## 8. NDJSON schema additions

Reserved channels for this protocol:

```jsonc
{
  "t": 1234567890.123,
  "src": "protocol",
  "phase": "active",            // settling | onboarding | active | closure | reflection
  "arm":   "active",            // active | sham (sealed until analysis)
  "l0":    { "rate_bpm": 6.0, "phase_rad": 1.57 },
  "l1":    { "coherence": 0.62, "smoothed": 0.58, "rendered_cents": -12 },
  "events": [ "phase_transition", "l1_dropout", "stressor_onset", "stressor_offset" ]
}
```

```jsonc
{
  "t": 1234567890.123,
  "src": "subjective",
  "when": "pre",                // pre | post | next_morning
  "scores": {
    "calm": 4, "energy": 5, "clarity": 4,
    "intrusive": 3, "comfort": 5,
    "sleep_quality": null       // null unless when=="next_morning"
  },
  "free_text_hash": "sha256:..."
}
```

Schema is forward-compatible with Mk2+ additions (L3, L4 will append channels, not modify existing).

---

## 9. Mk1 software footprint

Approximate new code, all in `software/helmkit_mk1/`:

| Module | LOC | Notes |
|---|---|---|
| `protocol.py` | ~150 | L2 state machine, phase transitions, NDJSON events |
| `pacer.py` | ~50 | L0 breath pacer; audio + LED synchronization |
| `coherence.py` | ~80 | L1 HRV coherence metric (Lomb–Scargle + windowed integration) |
| `render.py` | ~60 | L1 audio harmonic rendering, LED brightness mapping |
| `subjective.py` | ~40 | Likert form generation, NDJSON logging, free-text hashing |
| `protocol_cli.py` | ~30 | `helmkit session --arm {active,sham}` wrapper |

Total ~410 LOC of Python. All testable on workstation with synthetic PPG; bench validation against real MAX30102 once it arrives.

---

## 10. Done criteria

The Mk1 session protocol is **ready to support its first wear-session** when:

- [ ] L0 pacer verified on bench against scope on audio output and LED brightness, drift < 0.1 % over 30 min.
- [ ] L1 coherence metric verified against a labeled HRV dataset (e.g. PhysioNet), reproduces published coherence values within 5%.
- [ ] L2 state machine simulated end-to-end, all phase transitions logged correctly, both arms identical in audio/visual output during `Settling`, `Onboarding`, `Closure`, `Reflection`.
- [ ] Likert panel UI renders on companion device, posts to NDJSON correctly, free-text hash verified.
- [ ] Sham-equivalence verification (audible, thermal, EMI, vibrational) passed per §7 with active and sham coils installed.
- [ ] Cold-pressor procedure documented in `experiments/Mk1/EH01_coil.md` and locked before first stressor session.
- [ ] Pre-registration filed for G2 (4-week ABAB) and G3 (single-session RCT) before any session of either arm runs.

---

## 11. See also

- [`docs/mk1_buildplan.md`](mk1_buildplan.md) — overall Mk1 build plan and §4.0 G1/G2/G3 pass model.
- [`docs/mk1_f2_probe.md`](mk1_f2_probe.md) — parallel record-side instrumentation for the stim payload.
- [`docs/roadmap.md`](roadmap.md) — how L0/L1/L2 propagates as the spine across Mk1.5, Mk2, Mk3.
- [`docs/safety.md`](safety.md) — interlock topology this protocol's state machine integrates with.
- [`docs/falsification.md`](falsification.md) — F-criteria; Mk1 G3 contributes precursor data, does not adjudicate any F directly.
