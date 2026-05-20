# The HelmKit Mk Ladder — Sub-Revision Semantics

**Purpose.** This document defines what each *integer* and *.5* step in the HelmKit Mk ladder means semantically. It is the canonical reference for "what does Mk1.5 mean vs Mk1.0 vs Mk2.0," cited from [roadmap.md](roadmap.md), [modes.md](modes.md), and [sensor_roster.md](sensor_roster.md).

**Status:** Authored 2026-05-14 after the May-2026 sensor-wave purchase locked in the Mk0.5 milestone and the Tranquil-only / Tranquil+Combat split was made explicit.

---

## 1. The seven-step ladder

| Step | Defining capability | Wearer scope | Stim scope | State-aware | Scope of claim |
|---|---|:--:|:--:|:--:|---|
| **Mk0.0** | Form (frame fits a head) | 1 wearer | — | — | "It exists physically." |
| **Mk0.5** | Form + sensing + biofeedback floor (Tranquil, stationary) | 1 wearer | — | — | "It senses; it gives feedback; no stim claim." |
| **Mk1.0** | + bifilar-coil stim G3 RCT (Tranquil, stationary) | 1 wearer | H1 (sub-MHz coil) | — | "It stabilizes a stationary wearer; the stim payload has been sham-controlled." |
| **Mk1.5** | + motion-tolerant Combat mode | 1 wearer | H1 | — | "It stabilizes a moving / exerting wearer." |
| **Mk2.0** | + EEG + state-aware closed-loop | 1 wearer | H1 (closed-loop) | ✅ | "It adapts stim/feedback to wearer cortical state. Focus / Creative / Vigilance / Social / Recovery modes unlocked." |
| **Mk2.5** | + matched-F² H1-vs-H2 (Frey UHF) three-arm | 1 wearer | H1 + H2 | ✅ | "Matched-F² stim-mechanism comparison. F3 / F4 framework engagement." |
| **Mk3.0** | Dyadic / production | 2+ wearers | H1 (+H2 if Mk2.5 cleared) | ✅ | "Dyadic co-regulation + Dicke superradiance N² test. Manufacturable design." |

---

## 2. The x.0 vs x.5 pattern

The pattern is intentional and consistent across rungs.

### Mk x.0 — *the rung exists*

A Mk **x.0** introduces the **canonical capability** that defines the rung. It is the **minimum-viable single-arm single-wearer working form** of the new capability.

- Mk0.0 introduces *form*.
- Mk1.0 introduces *stim* (atop the floor that landed at Mk0.5).
- Mk2.0 introduces *state-awareness* (atop the stim that landed at Mk1.x).
- Mk3.0 introduces *multi-wearer scaling* (atop everything below it).

### Mk x.5 — *the rung is stress-tested*

A Mk **x.5** **extends, compares, or stress-tests** the x.0 capability without changing its fundamental architecture. The Mk x.5 device is structurally the same as Mk x.0 plus a constrained extension that exercises x.0 against harder conditions or against an alternative.

- Mk0.5 extends Mk0.0 (bare frame) with *sensing and biofeedback floor* — same frame, sensors added. (Special: Mk0.5 functions as the "rung-zero stress test" by adding live sensing to the bare frame.)
- Mk1.5 extends Mk1.0 (stationary Tranquil + stim) with *motion tolerance* — same Mk1 device, electrodes engineered to survive sweat + motion, Combat-mode firmware added.
- Mk2.5 extends Mk2.0 (closed-loop state-aware, single stim) with a *second stim modality* and a *matched-F² three-arm comparison*.

There is no Mk3.5 in the current roadmap. Mk3.0 already carries the production / regulatory / manufacturability axis; further sub-revision is product roadmap territory, not scientific roadmap.

### Mk0.5 is asymmetric on purpose

Mk0.5 is unusual in the pattern because Mk0.0 was *non-electronic*. The integer→half-step extension at the form rung is therefore a discontinuous capability jump — "sensors exist on it now." This is the only rung where x.0 → x.5 crosses a fundamental category boundary. Every later x.0 → x.5 transition stays within one architecture and only extends conditions.

---

## 3. Why this matters — the gating logic

Each step is **gated on evidence** from the step below it:

- **Mk0.0 → Mk0.5:** Mk0.0 frame is wearable for ≥ 30 min without fatigue (✅ done, iter9 frozen).
- **Mk0.5 → Mk1.0:** Mk0.5 demonstrates the L0+L1+L2 floor delivers measurable wearer benefit (G2 within-subject ABAB on the developer, n=1). Without this, adding a stim payload is putting a coil on top of a device that *itself* hasn't been shown to do anything.
- **Mk1.0 → Mk1.5:** Mk1.0 G1 passes (stim hardware credible) AND Mk1.0 G2 passes (Tranquil benefit demonstrated) AND Mk1.0 G3 either passes or null-with-published-data. The Combat extension is justified only after the floor + stim integration is solid for the easier (stationary) case.
- **Mk1.5 → Mk2.0:** Mk1.x scope completed (both Tranquil and Combat working). The EEG investment ($250+ hardware) is justified only after the sensor-fusion firmware is mature on the simpler ANS-only stack.
- **Mk2.0 → Mk2.5:** Mk2.0 closed-loop adapts cleanly to a single stim modality first. Adding a second stim modality requires the state-aware substrate to do matched-F² right.
- **Mk2.5 → Mk3.0:** Multi-stim comparison has decided which stim path the production design ships with. Dyadic + manufacturable is a sufficiently different engineering problem that it should not start until single-wearer evidence has resolved.

**No skipping integer steps.** No skipping .5 steps either — they are real gates, not version-number cosmetics.

---

## 4. The G1 / G2 / G3 grades — orthogonal to Mk ladder

Each Mk step has *its own* G1, G2, G3 gates per the [`cross-cutting principles`](roadmap.md#cross-cutting-principles-the-spine-of-the-whole-ladder):

- **G1 (Engineering):** apparatus does what it claims, mechanically.
- **G2 (Wearer-benefit):** trait-level improvement to the wearer under within-subject multi-week ABAB.
- **G3 (Framework-contribution):** sham-controlled blinded RCT contributing to F1–F11.

A Mk step is **complete** when:
- G1 passes, AND
- G2 passes OR is published-null with mechanism analysis, AND
- (If the step has a stim payload) G3 passes OR is published-null with mechanism analysis.

**Different Mk steps emphasize different G-grades:**

| Step | G1 weight | G2 weight | G3 weight | Notes |
|---|:--:|:--:|:--:|---|
| Mk0.0 | ✅ only | — | — | Engineering check only. |
| **Mk0.5** | ✅ | ✅ | — | Wearer-benefit gate on biofeedback floor; no stim → no G3. |
| **Mk1.0** | ✅ | ✅ | ✅ | First step with stim → first G3. |
| Mk1.5 | ✅ | ✅ | ✅ | Combat G2 ABAB; exertion-stressor G3 variant. |
| Mk2.0 | ✅ | ✅ | ✅ | Per-mode G2; F3/F4 engagement at G3. |
| Mk2.5 | ✅ | ✅ | ✅ | Three-arm G3; G2 inherits Mk2.0. |
| Mk3.0 | ✅ | ✅ | ✅ | Dyadic G2; F7 + Dicke superradiance at G3. |

---

## 5. Mapping to existing documentation

The legacy roadmap (`docs/roadmap.md`) was written before the May-2026 mode-roster expansion and uses the coarser five-step ladder (Mk0 / Mk1 / Mk1.5 / Mk2 / Mk3). The mapping is:

| Legacy | Current |
|---|---|
| Mk0 | Mk0.0 |
| (new step) | **Mk0.5** — Tranquil biofeedback floor, no stim |
| Mk1 | Mk1.0 — Tranquil + coil stim G3 |
| (new step) | **Mk1.5** — Combat mode, motion-tolerant electrodes |
| Mk1.5 (legacy) | Mk2.5 — H1-vs-H2 matched-F² (repositioned: needs Mk2.0 state-aware substrate to do right) |
| Mk2 | Mk2.0 |
| Mk3 | Mk3.0 |

The legacy Mk1.5 entry has been repositioned to Mk2.5 because matched-F² stim comparison is fundamentally a state-aware-substrate problem — it requires the EEG + closed-loop instrumentation that Mk2.0 introduces to do the comparison rigorously. Hardware-prototyping the H2 emitter can still begin earlier; the formal three-arm G3 gate is what moves.

---

## 6. Current state (2026-05-14)

| Step | Status |
|---|---|
| Mk0.0 | ✅ Frozen (iter9). |
| Mk0.5 | 🚧 **In flight.** Sensor Wave 1 arriving 2026-05-16 (MLX90614 + GSR + 3M Red Dot + leads). Wave 2 arriving 2026-05-27 → 2026-06-15 (AD8232 + MAX30205 ×2). MAX30102 already in hand. See [sensor_roster.md §2](sensor_roster.md). Physical architecture: rail-forever three-ring crown ([mechanical/mk0.5_base_crown_architecture.md](mechanical/mk0.5_base_crown_architecture.md), locked 2026-05-20). |
| Mk1.0 | ⏸ Pending Mk0.5 G2 completion + bifilar-coil hardware build. **Inherits** the Mk0.5 Picatinny-rail mechanical contract unchanged; ten named hardpoint IDs persist. |
| Mk1.5 | ⏸ Pending Mk1.0. |
| Mk2.0 | ⏸ Pending Mk1.x + EEG-class purchase ($250+ Mk2 capex). |
| Mk2.5 | ⏸ Pending Mk2.0. |
| Mk3.0 | ⏸ Pending Mk2.x. |
