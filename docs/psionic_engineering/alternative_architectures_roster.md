# Alternative architectures for psionic stabilization / entrainment — a roster

**Status**: v0, 2026-08-06. Exploratory — this is a menu to think from, not a decision record. Nothing here has been adopted; the current Mk1.0 stim payload remains the low-voltage PCB bifilar coil per `docs/mk1_buildplan.md` unless/until this roster leads to an explicit change.

## 0. Framing

### "Transmission" is the wrong word

The bifilar (and caduceus) coil geometries are *specifically engineered to have near-zero far-field radiation* — that's the entire point of the series-opposing / opposite-chirality cancellation trick. A structure engineered not to radiate is not a transmitter. The wiki's own component taxonomy already has the correct word: **ψ Transducer** (EM energy → ψ energy conversion), not ψ Transmitter or ψ Antenna. Real near-field electromagnetics has the matching vocabulary too — *reactive near-field coupler*, *evanescent coupler*, *non-radiating source*. This repo should standardize on "transduction" / "near-field coupling" language going forward and retire "transmission" for anything in this family — it's not pedantry, it pulls in the wrong regulatory model (far-field transmitter rules vs. near-field non-radiating device rules are different regimes) and the wrong mental model of what success looks like.

### What we're actually trying to do, decoupled from mechanism

Three functional goals, stated as measurable targets rather than as "make a ψ device":

1. **Stabilization** — reduce variance/noise in a brain-state variable; a damping/negative-feedback function. (Wiki-EFT framing: drive the "consciousness order parameter C" toward the symmetric phase, away from runaway — same statement in field-theory language.)
2. **Entrainment** — lock an internal oscillator (neural, cardiac, respiratory) to an external rhythmic reference.
3. **Indefatigability** — extend time-to-fatigue. In real physiology this is mostly autonomic balance (vagal tone / HRV), sustained attention-network engagement, and avoiding over/under-arousal — not one lever.

**Important standing fact, worth restating every time this roster gets used**: the existing L0/L1/L2 biofeedback floor is *already* a complete, zero-emission architecture for goal (1) and partially (2) — paced breathing and closed-loop HRV-coherence rendering are real, evidenced techniques, no coil required. The bifilar coil isn't load-bearing for "does the device help the wearer" — it's specifically there for `mk1_buildplan.md`'s *secondary* goal, framework validation (does ψ-mediated coupling add anything above biofeedback alone). Every item below is a candidate for that secondary goal, or for goal (3) via genuinely different physiological levers — not a replacement for the floor.

### Feasibility legend (cross-referenced against `docs/inventory.md`)

| Tag | Meaning |
|---|---|
| 🟢 **Now** | Buildable today from on-hand inventory, no new purchase |
| 🟡 **Minor buy** | Needs a small (<$50-ish), non-exotic purchase |
| 🔴 **Capital** | Needs real capital equipment not in inventory (DLP/resin printer, phased ultrasound array, medical-grade stimulator, etc.) |
| ⛔ **Policy-excluded** | Feasible in principle but currently excluded by `docs/safety.md`'s hard-exclusion list, independent of hardware |

---

## Roster A — Near-field coupler / coil geometries

All of these target the same functional slot as the current bifilar PCB coil (Branch D1 / `ψ Transducer` C3): concentrate local field-strength-squared while suppressing far-field signature. They differ in *how*.

### A1. Bifilar spiral variants (same family as current design)

- **Archimedean (constant-pitch) spiral — current design.** Simple, well-understood, but field concentration is uneven (denser near center).
- **Logarithmic/self-similar spiral.** A real broadband-antenna geometry (log-spiral antennas are a standard class) — gives more uniform E-field across the whole coil area instead of concentrated near the center. 🟢 Now — same CNC-mill/FR4 fab path as current design, just a different trace-generation function.
- **Fractal / meander-line trace.** Increases total trace length (and inter-trace coupling volume) within a fixed footprint — real, published miniaturization technique. 🟢 Now — same fab path, different Gerber pattern.
- **Toroidal-core bifilar** (wound around a closed torus rather than flat). Closed topologies generally null far-field *better* than a flat spiral (no residual loop-plane leakage), and pack more trace length into a smaller footprint. 🟢 Now — 3D-print a non-conductive PETG/TPU toroidal bobbin, hand-wind bifilar with the BNTECHGO 20 AWG (two strands simultaneously, exactly what inventory's own notes anticipate) or 28 AWG stock.
- **Multi-filar (tri-/quadrifilar).** Cancels higher multipole orders, not just the dipole — a "quieter" far field than plain bifilar. Quadrifilar helices are a well-known real antenna topology (satellite comms, circular polarization) — running the same geometry in cancel-mode rather than radiate-mode is a legitimate variant. 🟢 Now via hand-winding on a printed former (magnet wire stock supports 2–4 simultaneous strands); 🟡 Minor buy if attempting true multilayer PCB (hobby CNC mill isn't well-suited to >2 conductive layers).

### A2. Resonant near-field concentrators (a different primitive than the coil)

The wiki's own Branch C catalog separates **ψ Resonator** (C1, standing-wave, Q>200 target) from **ψ Transducer** (C3, the coil) — the current design conflates them into one non-resonant part. These are real candidates for the missing resonator half:

- **Split-ring resonator (SRR).** Heavily published metamaterial primitive, used for exactly this purpose in high-field MRI RF coil enhancement and near-field wireless power — the gap concentrates E-field far more intensely at resonance than a non-resonant spiral, for the same drive power. Trade-off: narrowband, must sit on resonance, more finicky to tune. 🟢 Now — same PCB mill/FR4 fab path, just a ring-with-a-gap pattern instead of a spiral. This is probably the single highest-value "try this next" item on the whole roster: cheap to fabricate, directly fills a named-but-empty wiki component slot, and is a real, mainstream RF technique independent of anything psi-related.
- **Anapole (toroidal-dipole) mode.** Real, published metamaterial technique (Fedotov et al. and the broader anapole-photonics literature) — cancels *both* electric and magnetic far-field dipole moments simultaneously, strictly better far-field suppression than bifilar. Needs a genuine 3D structure, not a flat PCB. 🟡 Minor buy / assembly complexity — 3D-printed multi-part former + hand winding, more fiddly than A1's toroidal bifilar but same base fab capability.

### A3. Field-shape alternatives (uniform vs. localized)

- **Helmholtz-pair / large-diameter low-turn coil pair.** Used in real biomagnetic-stimulation research (Persinger-class apparatus) for a spatially *uniform* field across the whole head, rather than a concentrated local near-field spot — a genuinely different design goal from everything above. 🟢 Now — inventory's magnet wire + the extracted electromagnet iron cores (already flagged in inventory notes for "Mk2 solenoid experiments") cover this directly.
- **Halbach array (passive, DC).** Not a signal architecture — a *permanent-magnet* arrangement that concentrates field on one face while cancelling on the other. Same cancellation spirit as bifilar, but static, using the **~1700+ neodymium magnets already in inventory** (inventory's own notes flag Halbach arrays as an anticipated Mk2 option). Not a substitute for an AC-driven coupler, but a real candidate for passive field-shaping *alongside* one, or for any DC-bias / static-field-shell exploration. 🟢 Now, and dramatically over-stocked for the purpose.

### A4. Fabrication-route alternatives (same electrical geometry, different how-you-make-it)

- **Conductive paint directly on the 3D-printed frame**, using the already-owned MG Chemicals 843AR (Ag-Cu) / 841AR (Ni) / 838AR (carbon) paints — inventory's own notes already earmark 843AR for "coil-PCB ground-plane patching." Painting a bifilar/SRR/log-spiral trace pattern directly onto a printed PETG part (rather than a separate FR4 PCB) is a genuine, inventory-grounded bridge between the current low-voltage PCB approach and the wiki's newer "traces embedded in the shell" vision — achievable with FDM + paint, not DLP + BST composite. 🟢 Now, and probably the second-highest-value item to prototype after the SRR.
- **Ferrofluid-channel μ_eff tuning, at small scale.** The wiki's TPMS+ferrofluid concept needs a full lattice shell; a *much* simpler version — a printed channel or reservoir adjacent to a coil, filled from inventory's ~2.18 L ferrofluid stock — could let one experimentally vary local permeability without needing true TPMS geometry. Non-cellular channels are ordinary FDM-printable. 🟢 Now, much cheaper way to touch the same physics question the wiki's material-science branch raises.

---

## Roster B — Drive / signal-generation architectures

Where Roster A changes the *coil*, this roster changes *what's fed into it*.

- **Chirp / swept-frequency drive.** Spreads energy over a band instead of one carrier — lowers peak E-field for the same total delivered energy (a real safety win) and doesn't require knowing the wearer's exact resonant frequency in advance. 🟢 Now — pure firmware/DSP change; the XR2206 function generators and ESP32 LEDC PWM can both sweep.
- **Stochastic-resonance-assisted drive.** Real, mainstream nonlinear-systems biophysics: adding an optimal level of broadband noise to a sub-threshold periodic signal can make a nonlinear biological system respond to it *more* reliably than the clean signal alone. Nothing to do with whether ψ is real. 🟢 Now — firmware-only (software dither/noise mixed with the carrier).
- **Coherent multi-element (phased-array) drive.** HelmKit already has L/R Stabilizer pairs and L/R Defender coils, currently driven as independent identical channels — structurally *already* a phased array nobody's using as one. Real precedent: high-field MRI "RF shimming" (multiple coil elements, phase-controlled, to shape the field distribution inside tissue). **Cheap path to this**: multi-output SI5351 variants (already the chosen clock chip) share one PLL across outputs, giving phase-coherent multi-channel generation essentially for free — this is not a hardware change, just picking the right SI5351 variant and a firmware phase-control layer. 🟢 Now / 🟡 Minor buy (a multi-output SI5351 breakout if the current one is single-output).
- **Passive / receive-only mode.** The wiki's own Bifilar Coil Engineering page describes a back-EMF "detector mode" for the *same* coil — passive sensing, zero emission, already specified and unused. Whole architecture worth considering: never drive the coil at all, use it purely as a pickup feeding the existing biofeedback rendering. Zero SAR question, zero safety-table gap to resolve. 🟢 Now.
- **Direct Digital Synthesis (DDS, e.g. AD9833/AD9850-class).** More precise arbitrary-waveform generation than SI5351 (a clock generator, more limited waveform shapes). Not currently in inventory. 🟡 Minor buy — only worth it if SI5351's waveform limitations actually become a bottleneck; not needed to start.
- **HackRF-as-driver.** The HackRF One is TX+RX and already in inventory — in principle an extremely flexible arbitrary-waveform coil driver (any modulation, any carrier in-band, fully SDR-controlled). **Explicitly flagged, not casually recommended**: `tools/analyze_ambient_confounds.py` was deliberately built with zero SDR-invocation code specifically to avoid the transmit-capable-hardware question; using HackRF as a stim driver reopens that question and would need the same opto-isolated dual-MCU hardware interlock as any other driver sitting between it and the coil, engineered explicitly, not assumed. 🟡 Minor buy (interlock engineering effort, not new parts) — worth keeping on the list, not worth rushing into.

---

## Roster C — Alternative modalities (stepping outside EM near-field entirely)

Since the functional goal is stabilization/entrainment/fatigue-resistance, not specifically "build a ψ transducer," these target the same endpoints via different physiological channels.

- **Vibrotactile entrainment.** Real, published (rhythmic tactile stimulation research, e.g. gait/tremor entrainment). Low safety risk — no EM, no photic-epilepsy concern. 🟡 Minor buy (small ERM/LRA haptic actuator) — or possibly 🟢 Now if the existing bone-conduction transducers can be repurposed to produce felt sub-audio vibration, worth a bench check before buying anything.
- **Thermal (mild cyclic scalp/temple stimulation).** Less-established evidence base than the others here, but real research area. 🟡 Minor buy (small Peltier element).
- **Olfactory entrainment.** Different sensory channel entirely (scent-based state induction — e.g. lavender/calm, peppermint/alertness). Weaker evidence base, but essentially zero safety concern and very cheap. 🟡 Minor buy.
- **Mechanical compression / acupressure-point stimulation.** Zero electrical safety concern; traditional-medicine plus limited modern evidence base. 🟢 Now-ish (mechanical design only).
- **Galvanic vestibular stimulation (GVS).** Real, published — mild current via mastoid electrodes affecting the vestibular/balance system, with documented arousal/alertness effects in some studies. Different electrode placement and target system than tDCS/tACS, so it may or may not fall under `safety.md`'s current tDCS/tACS hard exclusion as literally written — **flagged as "needs its own explicit safety review," not assumed excluded and not assumed allowed.**
- **Cranial electrotherapy stimulation (CES).** Worth naming because it's a real, *already-regulated* category (FDA-cleared for anxiety/insomnia in the US; existing commercial precedent — Fisher Wallace, Alpha-Stim) — meaning if transcranial electrical stimulation is ever revisited, CES has an existing regulatory pathway that raw research-grade tDCS/tACS does not. Currently still under `safety.md`'s hard exclusion #1 (medical-grade only, Mk2+). ⛔ Policy-excluded at Mk1, worth knowing the regulatory landscape has a shorter path than "raw tDCS" implies.
- **tACS/tDCS.** The most directly evidence-backed technique for entraining cortical oscillations specifically (real published effects on EEG alpha entrainment, some fatigue/sustained-attention literature). Explicitly excluded by `safety.md` hard exclusion #1 today. Restating plainly: this trades away probably the strongest real evidence base in the whole roster for safety/regulatory conservatism — a deliberate choice already made, not an oversight, and not reopened by this doc. ⛔ Policy-excluded.
- **Transcranial focused ultrasound (tFUS).** Genuinely different modality class (mechanical/acoustic, not EM) — real, increasingly mainstream neuromodulation research, some FDA-cleared uses, real published arousal/mood effects. Needs a phased ultrasound transducer array + precise beamforming control — nothing like this in current inventory. 🔴 Capital — a serious future-Mk direction if the goal shifts from biofeedback-plus-experiment toward actual neuromodulation, not a near-term item.

---

## Summary table

| Item | Category | Feasibility | Real-world grounding |
|---|---|---|---|
| Log-spiral / fractal bifilar trace | A1 | 🟢 Now | Antenna miniaturization literature |
| Toroidal-core bifilar | A1 | 🟢 Now | Standard bifilar-inductor practice |
| Multi-filar (tri/quadrifilar) | A1 | 🟢 Now (hand-wound) | Quadrifilar helix antennas |
| Split-ring resonator (SRR) | A2 | 🟢 Now | MRI RF coil enhancement, metamaterials |
| Anapole / toroidal-dipole mode | A2 | 🟡 Minor buy | Published metamaterial/photonics literature |
| Helmholtz-pair (uniform field) | A3 | 🟢 Now | Persinger-class biomagnetic apparatus |
| Halbach array (passive, DC) | A3 | 🟢 Now, over-stocked | Standard permanent-magnet engineering |
| Conductive paint on printed frame | A4 | 🟢 Now | Bridges to wiki's shell-embedded vision |
| Ferrofluid channel μ_eff tuning (small-scale) | A4 | 🟢 Now | Wiki's own TPMS/ferrofluid concept, descoped |
| Chirp / swept drive | B | 🟢 Now | Radar/spread-spectrum practice |
| Stochastic-resonance-assisted drive | B | 🟢 Now | Mainstream nonlinear biophysics |
| Coherent multi-element (phased) drive | B | 🟢 Now / 🟡 | MRI RF shimming |
| Passive / receive-only mode | B | 🟢 Now | Already specified, unused |
| DDS waveform generation | B | 🟡 Minor buy | Standard signal-generation practice |
| HackRF-as-driver | B | 🟡 (interlock effort) | Reopens a deliberately-avoided question |
| Vibrotactile entrainment | C | 🟡 / possibly 🟢 | Gait/tremor entrainment research |
| Thermal entrainment | C | 🟡 Minor buy | Limited but real research |
| Olfactory entrainment | C | 🟡 Minor buy | Weak but real evidence base |
| Mechanical compression | C | 🟢 Now-ish | Traditional + limited modern evidence |
| Galvanic vestibular stimulation | C | Needs safety review | Real, published, different system than tDCS |
| Cranial electrotherapy stim (CES) | C | ⛔ Policy | FDA-cleared category, still excluded here |
| tACS/tDCS | C | ⛔ Policy | Strongest direct evidence base, excluded for safety |
| Transcranial focused ultrasound | C | 🔴 Capital | Real, mainstream, needs new hardware class |

## Suggested next step, if this moves from brainstorm to comparison

Most of the 🟢 items are cheap enough to prototype in parallel and compare on the *same* G1/G2/G3 wearer-benefit framework already built — none of them require committing to a single "winner" up front. A natural infrastructure step, if wanted: a parametric coil-geometry generator (same spirit as `tools/blender/build_*.py`, but emitting Gerber/SVG for the CNC mill instead of STL) so log-spiral, SRR, fractal, and quadrifilar patterns can all be generated from one parameterized script rather than hand-drawn — `docs/mk0_pcb_bifilar_coil.md` already flags this as a deferred to-do ("A parametrized generator script can be added under `tools/bifilar_coil_gen.py` when you're ready — say the word").
