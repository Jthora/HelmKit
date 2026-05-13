# Mk1 $F^2$ probe — make, don't buy

**Premise.** The bifilar / caduceus emitter family was chosen because the ψ-field source term is $J_\psi \propto F^2 = \tfrac{1}{2}(B^2/\mu_0 - \varepsilon_0 E^2)$ and the reactive near-field is the only EM regime where both $|E|^2$ and $|B|^2$ can be large at the same input power. If we accept that geometric premise on the *emitter* side, we should match it on the *probe* side: a probe that measures $|B|^2$ alone is not measuring $F^2$. We can do better — and we can do it from inventory, with geometry chosen for what we're actually doing, not what's available for ~\$30 at DigiKey.

This document specifies a **tri-element near-field $F^2$ probe** that is shop-buildable, calibrated against our own drive coil, and structurally aligned with the device's emitter philosophy. It replaces the "buy a Hall sensor" line in the earlier audit.

> **Build-side scope.** This is a Mk1 *bench / record-side* probe. It mounts under or beside the bifilar emitter on a flex pigtail; its purpose is to log the actual delivered $F^2$ envelope into NDJSON for every session. It does **not** modify the emitter, the safety architecture, or the wearer-facing claim language.

---

## 1. What we are actually measuring

Three quantities, all the same instant, all the same point, all on shared NDJSON timeline:

| Channel | Sensor | What it measures | Why |
|---|---|---|---|
| **B-mag** | Multi-turn air-core pickup coil, single-axis | $\partial B/\partial t$ along coil axis → integrated to $B(t)$ | Dominant near-field component for our bifilar emitter; baseline reference |
| **B-vec** *(stretch)* | Two additional pickup coils, orthogonal | full vector $\vec B(t)$ → $|\vec B|^2$ | Avoids cos-θ error from probe misalignment; resolves off-axis components |
| **E-mag** | Capacitive plate, small area, high-Z buffer | $E(t)$ normal to plate | $\varepsilon_0 E^2$ contribution to $F^2$ — *the term every commercial near-field probe ignores* |
| **Bifilar null** *(diagnostic)* | Counter-wound bifilar pickup coil, geometrically matched to the emitter | Approximately zero net $\partial B/\partial t$; full capacitive coupling | **Channel-separation diagnostic**: if our bifilar emitter is truly delivering simultaneous large $E^2$ and $B^2$, the bifilar pickup separates the two and gives us a direct "is the emitter doing what we think it's doing?" readout |

The "bifilar null" channel is the genuinely original geometry. Commercial probes don't carry it because they're designed for radiated-field compliance, not reactive-near-field analysis of a Primakoff-class converter. **We do.**

---

## 2. Why a bifilar pickup is the right complement to a bifilar emitter

A counter-wound bifilar coil has, by construction:

- **Near-zero net magnetic dipole moment** (the two windings carry equal-and-opposite current contributions to any external field linking them).
- **Maximum capacitive coupling between adjacent turns** (close-wound counter-flow gives strong inter-turn $E$-field).

Used as an emitter (the wiki's choice for the Stabilizer), this produces a near-field with low far-field radiation but strong reactive $E$ and $B$ at scalp distance — the regime where $F^2$ is maximised per watt of drive.

Used as a **pickup probe**, the same geometry has dual selectivity:

- A bifilar pickup in *series-aiding* connection cancels capacitive pickup (the two leads see equal-and-opposite displacement currents) but retains inductive pickup — measures $B$ cleanly.
- A bifilar pickup in *series-opposing* connection cancels inductive pickup (the two windings see opposing $\partial\Phi/\partial t$) but retains capacitive pickup — measures $E$ cleanly.

Co-locating these two pickups in the same physical bifilar coil with a **switchable connection** at the readout end gives us a single probe that can separate $E$ and $B$ contributions at the *same point* in the field, with the *same geometry-induced cosine errors* (which therefore subtract cleanly when computing $F^2$). A pair of off-the-shelf single-element probes cannot do this.

This is the probe-side analogue of the emitter-side bifilar choice. Same principle, mirrored.

---

## 3. Concrete build — single-axis baseline (do this first)

Start narrow. Build the single-axis B-pickup, prove it ingests cleanly into NDJSON, then add the E plate, then add the bifilar pickup. Three sprints, additive.

### 3.1 B-pickup coil (single axis)

**Geometry:**
- Air-cored, no ferrite (linearity matters; saturation must not happen at any drive level we'll run).
- $N = 100$–$200$ turns of 36–40 AWG magnet wire (we have rolls of this in the inventory from the bifilar-emitter experiments).
- Form: 3D-printed bobbin, $\approx 8$ mm OD, $\approx 4$ mm long. Print at 100% infill, PLA acceptable for bench, PETG for permanent.
- Mount: hot-glue or epoxy onto a small FR4 carrier with the readout traces.

**Calibration constant:**
$$V(t) = -N \cdot A \cdot \frac{dB(t)}{dt}$$
where $A$ is the cross-sectional area enclosed by each turn. For $N = 150$, $A = \pi (4\,\text{mm})^2 / 4 \approx 1.26 \times 10^{-5}\,\text{m}^2$, the sensitivity to a 1 µT, 7.83 Hz signal is $\sim 9.3\,\mu\text{V}$ peak — sits comfortably above MCU-A's 12-bit ADC noise floor *after* a 40 dB amplifier (cheap op-amp from inventory). For a 100 kHz carrier component of the same amplitude, the same coil produces $\sim 0.12\,\text{V}$ — directly ADC-readable, no amp.

**Why air core, not Hall:** Hall sensors at our price point ($20–40) max out at DC–10 kHz with mediocre noise floor; the wiki-canonical Stabilizer drive is 1–8 MHz carrier modulated at 7.83 Hz. A pickup coil's frequency response is $\propto f$ across the entire drive bandwidth, which is *exactly the regime our device operates in*. Hall is the wrong tool here.

**Readout chain:**
- Coil → twisted-pair shielded → AD8421 or OPA1612 instrumentation amp at gain 100 (we have both in inventory across the SignalAnalyzer parts).
- Amp → first-order RC high-pass at 1 Hz (kill DC offset and 60 Hz mains).
- HPF → MCU-A ADC channel (Nano's onboard 10-bit is marginal but works for the carrier component; ESP32-S3 spare ADC channel is better if available).
- Integrate digitally in firmware OR record $\partial B/\partial t$ and integrate offline. **Default: record raw, integrate offline.** Storage is cheap; reversibility is precious.

**Calibration procedure:**
- Drive the bifilar emitter at a known current (measured by sense-resistor on MCU-A's existing current monitor).
- Compute expected $B$ at probe location using Biot-Savart for the emitter geometry (we already model this in [`docs/sprint_0.3_fdtd_coil_design.md`](sprint_0.3_fdtd_coil_design.md)).
- Verify probe output matches model within ±15% across 1 kHz – 5 MHz sweep.
- If it doesn't, the model or the construction is wrong; fix one before trusting the other.

**Inventory required:** 36–40 AWG wire (have), small bobbin (3D-print, hours), instrumentation amp (have), passives (have), MCU ADC channel (have). **Cost: zero incremental, ~2 hours of bench time.**

### 3.2 E-pickup plate (add second)

**Geometry:**
- Two small parallel copper plates, $\sim 10 \times 10$ mm, separated by $\sim 5$ mm of air or low-$\varepsilon$ printed structure.
- One plate faces the emitter; the other is ground reference.
- Differential readout to reject common-mode pickup.

**Sensor:**
- High-impedance buffer (JFET input op-amp, e.g. OPA627 or any LF356-class part — have these in inventory). Input impedance $> 10^{11}\,\Omega$ so the plate-to-buffer is voltage-divider-clean.
- Buffer → second instrumentation amp → MCU ADC channel.

**Calibration:**
- Apply a known $E$-field by placing the plate in the gap of a parallel-plate test capacitor driven at known voltage and frequency.
- Verify output linearity across drive band.

**Why this matters more than people think:** the $F^2 = \tfrac{1}{2}(B^2/\mu_0 - \varepsilon_0 E^2)$ relation says you cannot quantify the ψ-source without both components. A B-only measurement is *systematically wrong* in the reactive near-field because the $\varepsilon_0 E^2$ term is non-negligible at distances $\ll \lambda/2\pi$ — which is precisely our operating regime at 7.83 Hz envelopes. The sign in $F^2$ is conventional; both terms contribute in magnitude.

**Inventory required:** copper foil or PCB scraps (have), high-Z op-amp (have), passives, ADC channel. **Cost: zero incremental, ~3 hours of bench time including calibration.**

### 3.3 Bifilar pickup (the unique geometry)

**Geometry:**
- Identical bifilar winding pattern to the emitter, scaled down to probe size (~10 mm bifilar pair, 50–80 turns total).
- Wound on a small printed former with the same pitch as the emitter (so dispersion characteristics scale with frequency the same way).
- Two readout leads brought out as a twisted pair, plus a center-tap.

**Wiring modes (switchable at readout):**

| Mode | Connection | Cancels | Preserves |
|---|---|---|---|
| **Series-aiding** | Both windings in same direction, end-to-end | capacitive (E) | inductive (B) — pure B-pickup |
| **Series-opposing** | Counter-wound, summed at center-tap | inductive (B) | capacitive (E) — pure E-pickup |
| **Differential** | Two ADC channels, one per winding, subtract digitally | — | post-hoc reconstruction of both modes |

**Default mode for Mk1 logging:** **differential**, with both windings recorded as separate ADC channels. We can compute series-aiding and series-opposing offline, plus any linear combination. This costs us one extra ADC channel and gains us full reconstructability of the field decomposition.

**What the bifilar pickup tells us that nothing else does:**
- Is the emitter delivering the bifilar geometry we designed, or has the build introduced asymmetry that converts it into a vanilla single-mode coil?
- Is the ratio of capacitive to inductive contribution at scalp distance what the FDTD model predicts?
- During a session, does that ratio *drift* (e.g. with skin sweat conductance, head-coil distance, hair geometry)?

The third question is the operationally important one. **If the bifilar emitter's $F^2$ delivery drifts during a session because the wearer moves, sweats, or relaxes, the dose is not what we logged it as.** A bifilar pickup catches this directly. No commercial probe will.

**Inventory required:** more 36–40 AWG wire, printed former, two extra ADC channels (have if using ESP32-S3 as MCU-A; tight if Nano). **Cost: zero incremental, ~4 hours including the modal-decomposition calibration.**

---

## 4. Mounting and integration

- All three probes mount on a single small flex-PCB or carrier-PCB that lives **between the bifilar emitter and the scalp**, at the same hardpoint footprint.
- The probe-PCB should be < 1 mm thick so it doesn't materially change the emitter-to-scalp distance.
- One JST-SH 6-pin pigtail brings out: B-pickup differential pair, E-plate differential pair, bifilar pickup pair (center-tap to local ground at the probe).
- The pigtail terminates at MCU-A's existing sensor connector. No new MCU, no new bus.
- Probe ground reference is local; do not ground-bond to the emitter return — that creates a ground loop that swamps the bifilar pickup's selectivity.

---

## 5. NDJSON schema impact

Add the following channels to the Mk1 NDJSON record. Backward-compatible — schema readers that don't recognise them ignore them.

```jsonc
{
  "t": 1234567890.123,
  "src": "f2_probe",
  "ch": {
    "B_axial":  0.000123,   // tesla, integrated from coil dI/dt (single-axis)
    "B_x":      0.000089,   // tesla, x-component (if tri-axial built)
    "B_y":      0.000034,   // tesla, y-component
    "B_z":      0.000054,   // tesla, z-component
    "E_norm":   12.4,       // V/m, normal to scalp
    "bifilar_aid":  4.21e-6,// Wb/s, series-aiding output (B-selective)
    "bifilar_opp":  8.7e-3, // V, series-opposing output (E-selective)
    "F2":       1.27e-7     // J/m^3 ; derived: (B^2/mu0 - eps0*E^2)/2
  }
}
```

The derived `F2` field is computed by the same firmware step that does the integration — it is **not** a raw measurement, and downstream code should be able to recompute it from the raw channels if needed. The raw channels are the source of truth.

---

## 6. Why this is also a Mk1.5 prerequisite

The H2 hypothesis in [`docs/h2_modulated_uhf_hypothesis.md §5`](h2_modulated_uhf_hypothesis.md) calls for a matched-$F^2$ comparison between H1 (Persinger sub-MHz magnetic) and H2 (Frey-class GHz pulsed) emitters. *Matched-$F^2$* is unmeasurable without an $F^2$ probe. Building this for Mk1 means Mk1.5 inherits a working probe and an already-trained calibration workflow.

It also means: if the Mk1 study sees a strong stabilization effect, we can ask "*what was the $F^2$ envelope during the high-effect sessions?*" and search for a dose-response relationship in the existing data. Without the probe, that question is unanswerable.

---

## 7. Build order and time estimate

Conservatively, before Mk1 first session:

1. **B-pickup single-axis** — 2 hours. Validates the readout chain and integration step.
2. **NDJSON schema update** — 1 hour. Adds the `f2_probe` source with the B-channel only. Ships even if E and bifilar are deferred.
3. **E-plate** — 3 hours. Adds the `E_norm` channel.
4. **Bifilar pickup** — 4 hours. Adds the diagnostic channels and the derived `F2`.
5. **End-to-end calibration sweep** — 2 hours. Drive emitter at known current across 1 kHz–5 MHz; verify probe matches Biot-Savart model within ±15%; verify $F^2$ derivation matches expectation.

**Total: ~12 bench-hours, zero incremental dollars.** Versus ~\$20–40 + shipping + calibration-uncertainty for a single-channel Hall probe that doesn't measure $E$, doesn't separate channels, and is the wrong physics anyway.

The make-it path is faster, cheaper, more informative, and structurally aligned with the device. The only reason to consider buying is if bench time is the binding constraint, which it isn't right now.

---

## 8. What this does NOT change

- The emitter. Same bifilar PCB coil per the wiki-canonical Mk1 spec.
- The drive electronics. Same SI5351 + Class-D + matching network.
- The safety architecture. The probe is read-only; it cannot enable or disable stim. MCU-B's blacklist enforcement is unaffected.
- The wearer-facing description of the device. The probe is an internal record-side instrument; the wearer doesn't see it and the marketing copy doesn't mention it.
- The L2 primary endpoint. HRV RMSSD time-to-coherence stays. The probe contributes a *secondary* covariate ($F^2$ delivered per session) that lets us do a dose-response analysis after L2 is filed.

---

## 9. See also

- [`docs/psionics_field_theory.md`](psionics_field_theory.md) — Lagrangian; $J_\psi \propto F^2$ is the source-term identity that motivates measuring $F^2$, not just $B$.
- [`docs/psion_quasiparticle.md`](psion_quasiparticle.md) — Primakoff-converter framing of the bifilar emitter, which makes the bifilar-pickup probe its natural complement.
- [`docs/h2_modulated_uhf_hypothesis.md`](h2_modulated_uhf_hypothesis.md) — matched-$F^2$ design that depends on this probe for Mk1.5.
- [`docs/sprint_0.3_fdtd_coil_design.md`](sprint_0.3_fdtd_coil_design.md) — Biot-Savart / FDTD model used for probe calibration.
- [`docs/mk1_buildplan.md`](mk1_buildplan.md) §0a Mission, §4.0 Layer 1/2/3 pass-fail.
- [`docs/sprint_0.2_circuit_spec.md`](sprint_0.2_circuit_spec.md) — circuit reference for the readout chain.
