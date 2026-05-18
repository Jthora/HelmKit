# Roadmap — the Mk ladder

<!-- Source: docs/roadmap.md, docs/mk_ladder.md, docs/falsification.md,
     docs/mk1_buildplan.md
     Status: v0 (2026-05-18)
     Target length: 5-7 printed pages.
-->

The HelmKit ships in *generations*. Each generation is one rung on a
seven-step ladder, named in the format `MkX.Y` where the integer step
`X.0` introduces a canonical capability and the half-step `X.5`
stress-tests it. The ladder is the project's commitment device — it
says, in advance, what each step has to demonstrate before the next
one is permitted to start.

This chapter is the wearer-readable version of the canonical roadmap
([`docs/roadmap.md`](../../roadmap.md)) and the ladder-semantics
document ([`docs/mk_ladder.md`](../../mk_ladder.md)). The two
documents in the repository remain authoritative; both copies say the
same thing.

## The seven steps

| Step | Defining capability | Stim scope | State-aware? | Current status |
|------|---------------------|:----------:|:------------:|----------------|
| **Mk0.0** | Form — the frame fits a real head and can be printed | — | — | **OK** Done (v2 type-b iter 9) |
| **Mk0.5** | Form + sensing + biofeedback floor (Tranquil, stationary) | — | — | **active** In flight (Sensor Wave 1 ETA 2026-05-16) |
| **Mk1.0** | + bifilar-coil stimulation, sham-controlled, Tranquil stationary | H1 (sub-MHz coil) | — | — Pending Mk0.5 G2 |
| **Mk1.5** | + motion-tolerant Combat mode (moving / exerting wearer) | H1 | — | — Pending Mk1.0 |
| **Mk2.0** | + EEG + state-aware closed-loop adaptive stimulation | H1 closed-loop | **OK** | — Pending Mk1.x |
| **Mk2.5** | + matched-$F^2$ H1-vs-H2 three-arm comparison (Frey-class UHF) | H1 + H2 | **OK** | — Pending Mk2.0 |
| **Mk3.0** | Dyadic — two synchronized helmets, $F_7$ engagement, manufacturable | H1 (+H2 if cleared) | **OK** | — Pending Mk2.x |

## What `.0` and `.5` mean

The numbering pattern is intentional and consistent across rungs. A
`MkX.0` introduces the **canonical capability** that defines the rung
— the minimum-viable single-arm single-wearer working form of the new
capability. A `MkX.5` **extends, compares, or stress-tests** the
`X.0` capability without changing its fundamental architecture.

- Mk0.0 introduces form. Mk0.5 extends form with sensing and a
  biofeedback floor.
- Mk1.0 introduces stimulation atop the floor. Mk1.5 extends Mk1.0 with
  motion tolerance — the same device, with electrodes engineered to
  survive sweat and motion, plus a Combat-mode firmware preset.
- Mk2.0 introduces state-awareness atop the stim. Mk2.5 extends Mk2.0
  with a second stim modality and a matched-$F^2$ three-arm
  comparison.
- Mk3.0 introduces multi-wearer scaling atop everything below it. There
  is no Mk3.5 in the current roadmap — Mk3.0 already carries the
  production-and-regulatory axis, and further sub-revision is product
  roadmap territory rather than scientific roadmap.

Mk0.5 is the one asymmetric rung in the pattern. Mk0.0 was
non-electronic; the integer-to-half-step transition there is a
discontinuous capability jump — "sensors exist on it now." Every later
`X.0 → X.5` transition stays within one architecture and only extends
conditions.

## The three independent grades — G1, G2, G3

Every Mk step has its own three grades, gated independently and shipped
as their own outcomes.

**G1 — Engineering.** The apparatus does what it claims, mechanically.
It is calibrated, interlocked, and sham-equivalent across all sensory
channels.

**G2 — Wearer-benefit.** Trait-level improvement to the wearer's life
under a within-subject multi-week ABAB design. The endpoint is a
composite of root-mean-square-of-successive-differences (RMSSD)
heart-rate-variability trend, a Perceived Stress Scale Likert measure,
and sleep quality. **This is the primary deliverable.** Every Mk is
shippable on G2 alone if its stim payload nulls.

**G3 — Framework-contribution.** Single-session sham-controlled blinded
randomized-controlled-trial design with a locked stressor, contributing
data to the $F_1$–$F_{11}$ programme described in
[`docs/falsification.md`](../../falsification.md).

A Mk step is **complete** when G1 passes, G2 either passes or is
published-null with mechanism analysis, and (if the step has a stim
payload) G3 either passes or is published-null with mechanism
analysis. A `G1·OK / G2·OK / G3-null` outcome is **honest success**: the
device worked for the wearer, the framework took a hit on this
implementation, and the next step inherits calibrated input rather
than starting from zero.

Different steps emphasize different grades. Mk0.0 is G1-only. Mk0.5 is
G1 + G2 only (no stim, no G3). Mk1.0 is the first step that touches all
three grades. Mk2.0 emphasizes per-mode G2 and the $F_3$ / $F_4$
engagement at G3. Mk3.0 emphasizes dyadic G2 and the $F_7$ engagement
plus the Dicke superradiance $N^2$ scaling test at G3.

## Gating logic — no skipping

Each step is gated on evidence from the step below it:

- **Mk0.0 → Mk0.5.** Mk0.0 frame is wearable for at least 30 minutes
  without fatigue. **OK** Done (iter9 frozen).
- **Mk0.5 → Mk1.0.** Mk0.5 demonstrates the L0+L1+L2 biofeedback floor
  delivers measurable wearer benefit on a within-subject ABAB (n=1, on
  the developer first). Without this, adding a stim payload is putting
  a coil on top of a device that has not itself been shown to do
  anything.
- **Mk1.0 → Mk1.5.** Mk1.0 G1 passes (stim hardware is credible) AND
  G2 passes (Tranquil benefit demonstrated) AND G3 either passes or
  null-with-published-data. The Combat extension is justified only
  after the floor-plus-stim integration is solid for the easier
  (stationary) case.
- **Mk1.5 → Mk2.0.** Mk1.x scope completed — both Tranquil and Combat
  working. The EEG investment (around $250 of hardware capex) is
  justified only after the sensor-fusion firmware is mature on the
  simpler autonomic-nervous-system-only stack.
- **Mk2.0 → Mk2.5.** Mk2.0's closed-loop adapts cleanly to a single
  stim modality first. Adding a second stim modality requires the
  state-aware substrate to do matched-$F^2$ comparison correctly.
- **Mk2.5 → Mk3.0.** The multi-stim comparison has decided which stim
  path the production design ships with. Dyadic and manufacturable is
  a sufficiently different engineering problem that it should not start
  until single-wearer evidence has resolved.

No skipping integer steps. No skipping half-steps either — they are
real gates, not version-number cosmetics.

## The cross-cutting principles

Eight principles hold across every Mk. They are the connective tissue
between generations.

1. **The biofeedback floor is the spine.** Every Mk inherits the
   resonance-breath pacer (L0), the closed-loop HRV-coherence rendering
   (L1), and the structured session container (L2). Stim payloads are
   *additions on top*, never replacements. Mk2 adds L3 (EEG
   neurofeedback) and L4 (state-aware container adaptation). Each is
   additive. A Mk3 wearer always has L0–L4 working *even if every stim
   payload nulls* — the device benefits them regardless.

2. **Three independent grades per Mk.** G1, G2, G3 as described above.
   Each is pre-registered separately. Each is shippable as its own
   outcome.

3. **Always-on instrumentation; opt-in stimulation.** Photoplethysmography,
   electroencephalography (Mk2 and later), the $F^2$ probe, galvanic
   skin response (Mk2 and later), and the coil temperature thermistor
   are always recording when the helmet is worn. Stimulation is
   opt-in per session, gated by the dual-MCU interlock plus the
   container's `phase` and `arm` state.

4. **Sham extends to all sensory channels.** Every Mk's sham must be
   indistinguishable from the active arm on visual, mechanical,
   audible, thermal, electromagnetic-interference, and vibrational
   channels. Visual-only sham is insufficient; a G3 null with weak sham
   is uninterpretable.

5. **Trait endpoints lead state endpoints.** Every Mk's G2 primary is a
   multi-week trait composite. The single-session stressor-recovery
   measurement stays as a secondary and as the G3 framework endpoint.
   Trait is what the wearer experiences and reports; state is what
   falsifies a hypothesis.

6. **Wearer reports are first-class data.** Subjective Likert panels —
   calm, energy, clarity, intrusive thoughts, body comfort, sleep —
   pre and post every session, with weekly aggregates, logged in
   NDJSON alongside the physiological channels. Pre-registered weights
   in the G2 composite.

7. **The wiki claim-firewall holds at every Mk.** Wearer-facing claim
   language at any Mk equals what *that* Mk's G2 can demonstrate, and
   nothing more. No psion language, no $\psi$-field language, no
   framework-internal vocabulary in wearer-facing copy ever. The
   firewall is binding across all generations and across all
   wearer-facing surfaces — packaging, manual, website, this volume.

8. **Forward-compatible data schema.** The NDJSON channel schema is
   designed so a Mk1 dataset is queryable by Mk3-era tooling and vice
   versa. New channels are added; old channels are never renamed or
   repurposed.

## The cross-project milestone

Per the wiki's
[`Tho'ra Tech Maturity Levels`](https://wiki.fusiongirl.app/wiki/Tho%27ra_Tech_Maturity_Levels)
page, the broader Psi-Tech mission "goes live" the moment **(a)** the
core triad (Psi Stabilizer, Psi Harmonizer, Psi Defender) clears Mk1
AND **(b)** the Resonant Finder reaches Mk2. The HelmKit repository
owns (a). The wiki's
[`Psi-Tech`](https://wiki.fusiongirl.app/wiki/Psi-Tech)
page confirms that the triad shares one substrate — the HelmKit's
psi-bay plus near-field RF emitter plus dual-MCU safety architecture
— so clearing Mk1 means one Mk1 HelmKit device running all three
signal-pattern presets. Mk1 ships the Stabilizer preset only; the
Harmonizer and Defender presets are firmware additions in Mk2 once
their input pipelines exist.

## Where Mk1 sits

Mk1 is the first generation that has to *work*. The redefinition
landed in May 2026: Mk1 is fundamentally **a closed-loop heart-rate-
variability biofeedback device** with a *layered* stim payload on top.
The biofeedback is the floor, G2-graded, with an evidence base around
$d = 0.4$ to $0.8$ for the resonance-breath pacer alone. The bifilar
coil is the experiment, G3-graded, sham-controlled, blinded RCT.
Earlier roadmap revisions had this inverted; the current revision
fixes it.

Mk1's hardware bill is roughly:

- A Raspberry Pi Zero 2 W (or Pi 5 if EEG is in scope for the build) as
  the compute node, on the rearhelm hardpoint.
- A single-cell lithium-ion battery with a protection PCB, hot-
  swappable, also on the rearhelm.
- A MAX30102-class photoplethysmography sensor on a temple boom for
  HRV.
- An RM3100 triaxial magnetometer on the other temple boom for ambient
  electromagnetic survey.
- A DIY bifilar-coil $F^2$ probe (specified in
  [`docs/mk1_f2_probe.md`](../../mk1_f2_probe.md)) for measuring the
  stim dose delivered — required for G3, forward-compatible with
  Mk1.5's matched-$F^2$ comparison.
- Bone-conduction transducers on the ear-shield hardpoints for the
  audio entrainment channel.
- One stim payload: the bifilar PCB coil. Roughly 30 mm × 30 mm,
  series-opposing, driven 1–8 MHz carrier modulated at 7.83 Hz
  envelope, via an SI5351 reference clock into a Class-D amplifier
  with a matching network. Field bound at scalp distance: under
  500 µT. BOM bound: under $250. ICNIRP-bounded.
- The dual-MCU safety architecture from Chapter 2.
- A µSD card on the rearhelm compute, logging NDJSON in the same
  schema as the Psi Stabilizer `a01_capture` pipeline.

Mk1 explicitly does NOT transmit 1.245 GHz, 2.45 GHz, or 300–900 MHz
RF at the head. Those bands require SAR measurement, FCC licensing
review, and a biological-effects literature review that Mk1 will not
have completed. The project's hypothesis space for those frequencies
is preserved as Mk1.5 / Mk2 R&D — not killed.

A Mk1 result of `G1·OK / G2·OK / G3-null` is honest success — device
works, wearer benefits from the floor, coil stim payload nulls. The
device ships on G2 grounds; the stim payload iterates at Mk1.5.

## Where Mk2 and Mk3 sit

Mk2.0 adds EEG, closed-loop adaptive stimulation, the $F^2$-probe
upgrade to triaxial, galvanic skin response, and the ambient
electromagnetic dosimeter that feeds the Psi Defender preset. The L3
EEG-neurofeedback layer and the L4 state-aware container-adaptation
layer come in here. Sub-GHz pulsed RF (300–900 MHz) becomes available
under safety review with mandatory SAR measurement; 2.45 GHz remains
deferred.

Mk2.5 adds a second stim payload — the Frey-class pulsed UHF emitter —
and runs the three-arm matched-$F^2$ comparison (H1 active, H2 active,
sham) at $n \geq 30$ per arm. This is the first generation where the
$F_3$ resonance-enhancement falsifier and the $F_4$ SAR-independence
falsifier can be engaged directly.

Mk3.0 attempts the matched device-emission and AC-detection measurement
that engages the $F_7$ universal-$\alpha$ falsifier; the wiki-stated
minimum is two Mk3 pairs in independent setups. Mk3.0 also attempts the
Dicke superradiance $N^2$ scaling test on dyadic operation. The Psi
Defender's haloscope-class adapter that would engage the $F_{11}$ psion
quasiparticle null search is named for Mk3 but is far enough out that
planning it in detail now would be speculation.

## What is **not** on the ladder

A few capabilities the wiki names, and that the project's working
assumption permits as long-horizon scope, are explicitly absent from
the ladder above:

- The HelmKit's wiki-described **magnetogravitic bubble** is reduced
  to "layered EM shielding plus active counter-field" and lives in the
  Psi Defender sister-project's roadmap, not in HelmKit's. The
  HelmKit hosts it; it does not generate it.
- The Psi Stabilizer's wiki-described **local** and **external**
  stabilization modes (projecting fields beyond the wearer) are
  deferred indefinitely behind the safety floor in Chapter 6.
- The Psi-Tech triad's **Harmonizer** and **Defender** presets, beyond
  the Mk1 Stabilizer preset, are scheduled for Mk2 once their input
  pipelines exist. They are not in the Mk1 BOM.
- The **2.45 GHz pulsed RF** band remains deferred at every Mk
  currently in the ladder; the decision to admit it is pushed to Mk3
  evidence and regulatory review.

The ladder is the project's commitment about what it will demonstrate
before claiming what. The deferred capabilities are not abandoned —
they are placed past gates the project has not yet earned the right to
cross.
