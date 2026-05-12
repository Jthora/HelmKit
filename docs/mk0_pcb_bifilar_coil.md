# Mk0/Mk1 Bifilar PCB Coil — Fab-Ready Spec for Desktop CNC

**Status:** Design spec. Ready to translate to Gerber/G-code once copper-clad stock dimensions are confirmed during inventory.
**Target fab:** Desktop CNC PCB mill (isolation milling, single-sided or double-sided FR4 / phenolic copper-clad).
**Wiki anchor:** Tesla series-opposing bifilar coil per `Bifilar Coil` page; Mk1 Stabilizer/Harmonizer drive element per `Psi Stabilizer` page (1–8 MHz carrier, 7.83 Hz envelope target). See [wiki_anchors.md § Pass 2](wiki_anchors.md).

> Engineering intent: maximize **inter-turn E-field** with **suppressed far-field B dipole** via series-opposing winding. Voltage-driven, low current, low SAR — a Tesla bifilar, not a generic spiral inductor.

---

## 1. Geometry

### 1.1 Overall

- **Outer envelope:** 30 mm × 30 mm square (matches wiki Mk1 spec; fits the helm shell rear-cranium pocket).
- **Substrate:** FR4 or phenolic copper-clad, **1.6 mm or 0.8 mm** thickness, **1 oz Cu (35 µm)**. Use whatever you have most of.
- **Sides used:** Two-sided preferred (mirror windings on top and bottom layer for ideal series-opposing). Single-sided fallback shown in §1.4.
- **Mounting:** Four 2.5 mm corner holes at 25 mm pitch for M2 standoffs; non-plated, milled.

### 1.2 Spiral pattern (each side)

```
Top layer (CCW from outside to center):     Bottom layer (CW from outside to center):
  ┌─────────────────────────┐                 ┌─────────────────────────┐
  │ ╭─────────────────────╮ │                 │ ╭─────────────────────╮ │
  │ │ ╭─────────────────╮ │ │                 │ │ ╭─────────────────╮ │ │
  │ │ │ ╭─────────────╮ │ │ │                 │ │ │ ╭─────────────╮ │ │ │
  │ │ │ │  (centre→)  │ │ │ │                 │ │ │ │ (←centre)   │ │ │ │
  │ │ │ ╰─────────────╯ │ │ │   series        │ │ │ ╰─────────────╯ │ │ │
  │ │ ╰─────────────────╯ │ │   opposing      │ │ ╰─────────────────╯ │ │
  │ ╰─────────────────────╯ │   via           │ ╰─────────────────────╯ │
  └─────────────────────────┘                 └─────────────────────────┘
       OUT terminal (corner)                       IN terminal (corner)
```

- **Trace width `w`:** 0.30 mm (12 mil) — comfortably above most desktop mill resolutions (0.1–0.2 mm) and gives ~1 A continuous capacity, far above what we'll ever drive.
- **Trace spacing `s`:** 0.30 mm — equal to width. Wide enough to mill reliably, narrow enough for strong inter-turn capacitive coupling (which is exactly what a Tesla bifilar wants).
- **Turn count `N`:** 18 turns per side (counts from outer ring to center pad).
- **Inner termination radius:** ~2 mm center pad for via to opposite layer.
- **Outer termination:** corner pad 3 × 3 mm, drilled 1.0 mm for wire terminal.

### 1.3 Series-opposing connection (the critical part)

The Tesla bifilar pattern is **not** two adjacent wires wound together. In the wiki's series-opposing form, the top spiral winds **outward → inward CCW**; the bottom spiral winds **outward → inward CW** (mirror chirality). The two layers are joined at the **center** via a single plated/wire via. Drive is applied across the two **outer** terminals.

Current convention:
- Drive `V+` enters at top-layer outer corner.
- Current spirals CCW inward (top), passes through center via, spirals CW outward (bottom).
- Exits at bottom-layer outer corner (opposite corner from `V+`).

Effect:
- The far-field magnetic dipoles from the two layers are **antiphase** → far-field B largely cancels.
- The voltage gradient between adjacent turns on the **same layer** is `V_drive × (1/N)` between neighbors at like radius — that's the small bit.
- The voltage gradient between **top and bottom layers at the same radius** is large and varies with radius, since one is at "going in" potential and the other at "coming out" potential. This is the E-field the geometry is built to create.

If you want to verify this in your head: short the center via, drive top+, ground bottom−. Top spiral is at +V at outer, dropping to 0 at center. Bottom spiral is at 0 at center, dropping to −V at outer. Two layers stacked 1.6 mm apart, with opposite-sign potentials, makes a high E-field between them in the dielectric.

### 1.4 Single-sided fallback

If only single-sided copper-clad is available, the same series-opposing topology can be realized as two **side-by-side** spirals on one face, each ~14 mm square, connected center-to-center by a jumper wire on the underside. Loses the through-substrate E-field but keeps the dipole cancellation. Performance drops; use only if double-sided stock is exhausted.

---

## 2. Electrical estimates

These are first-cut. Refine with a 1 kHz LCR meter after milling.

### 2.1 Self-inductance (per side, single spiral)

Using the Wheeler approximation for a flat square spiral:

$$
L \approx 2.34 \cdot \mu_0 \cdot N^2 \cdot \frac{d_\text{avg}}{1 + 2.75 \rho}
$$

where $d_\text{avg} = (d_\text{out} + d_\text{in})/2$ and $\rho = (d_\text{out} - d_\text{in})/(d_\text{out} + d_\text{in})$.

Plugging in $d_\text{out} = 29$ mm, $d_\text{in} \approx 6$ mm, $N = 18$:
- $d_\text{avg} = 17.5$ mm = 0.0175 m
- $\rho = 23/35 = 0.657$
- $L \approx 2.34 \cdot (4\pi \times 10^{-7}) \cdot 324 \cdot 0.0175 / (1 + 1.806)$
- $L \approx 2.34 \cdot 1.257 \times 10^{-6} \cdot 324 \cdot 0.0175 / 2.806$
- $L \approx 5.94 \text{ µH per side}$

For the series-opposing pair, mutual inductance subtracts. Net inductance seen at the terminals is roughly $L_\text{net} \approx 2L(1-k)$ where $k$ depends on substrate thickness — typically $k \approx 0.5$ for 1.6 mm spacing. So **$L_\text{net} \approx 6$ µH** as a working estimate.

### 2.2 Self-capacitance

Inter-turn capacitance on one side (turns are ~0.3 mm apart with FR4 dielectric on substrate face, air above):
- Per-turn-pair $C$ dominated by edge coupling, $\sim 1$ pF.
- 18 turns × pair-wise → ~18 pF on one side.

Top-to-bottom layer capacitance through 1.6 mm FR4 ($\epsilon_r \approx 4.4$):
- Plate-pair area is roughly $w \cdot \text{turn length total} \approx 0.3 \text{ mm} \cdot 18 \cdot 70 \text{ mm avg} \approx 380 \text{ mm}^2$
- $C \approx \epsilon_0 \epsilon_r A / d = 8.85 \times 10^{-12} \cdot 4.4 \cdot 3.8 \times 10^{-4} / 1.6 \times 10^{-3}$
- $C \approx 9.2$ pF

Total **$C_\text{self} \approx 25–30$ pF**.

### 2.3 Self-resonant frequency

$$
f_\text{SRF} = \frac{1}{2\pi\sqrt{LC}}
$$

With $L = 6$ µH and $C = 28$ pF:

$$
f_\text{SRF} \approx \frac{1}{2\pi\sqrt{6\times 10^{-6} \cdot 28 \times 10^{-12}}} \approx 12.3 \text{ MHz}
$$

**This lands the SRF comfortably above the wiki 1–8 MHz drive band**, so the coil operates inductively in-band with self-resonance available as a resonant-mode boost option just above. Tune toward the SRF for maximum E-field at the cost of bandwidth.

### 2.4 DC resistance

- Trace length per side: $N \cdot \pi \cdot d_\text{avg} \approx 18 \cdot 3.14 \cdot 17.5 \text{ mm} \approx 989 \text{ mm}$ ≈ 1 m.
- 1 oz Cu, 0.3 mm wide → 35 µm × 0.3 mm cross-section = $1.05 \times 10^{-8}$ m².
- $R = \rho L / A = 1.68 \times 10^{-8} \cdot 1.0 / 1.05 \times 10^{-8} \approx 1.6$ Ω per side, **~3.2 Ω total DC**.

Acceptable. Skin effect at 8 MHz takes effective resistance to ~10 Ω; still acceptable for a voltage-driven coil.

### 2.5 Q

$Q = \omega L / R$ at 5 MHz mid-band: $Q \approx (2\pi \cdot 5 \times 10^6 \cdot 6 \times 10^{-6}) / 10 \approx 19$.

Moderate Q; matches a voltage-driven low-current emitter operating well below SRF.

---

## 3. Drive interface

| Pin / pad | Function | Connects to |
|---|---|---|
| `OUT_TOP` (top-layer outer corner) | V+ drive | HV module output via current-limit resistor + sense resistor |
| `OUT_BOT` (bottom-layer opposite outer corner) | V− drive / ground return | HV module return via sense resistor to MCU-A ADC |
| Center via | series-opposing tie point | internal — no external connection |
| `MNT1–4` | M2 standoff | non-electrical |

Recommended drive path (Mk1 first-power):
```
[Nano PWM (Mk0.5)]──[opto]──[HV module enable]──┬──[R_lim 100Ω 2W]──[OUT_TOP]
                                                  │
[MCU-B kill GPIO]──[opto]──[HV enable cutoff] ────┘                  [coil]

[OUT_BOT]──[R_sense 1Ω]──┬──[GND]
                         └──[diff amp]──[Pi 4 ADC]──[I_coil telemetry]
```

Current-limit resistor sized so that worst-case short across the coil draws ≤ 50 mA at the HV module's max V. Sense resistor lets Pi 4 monitor coil current in real time; MCU-B mirrors this read and trips kill on overcurrent.

---

## 4. CNC fab parameters (provisional — refine to your mill's spec)

| Parameter | Value |
|---|---|
| Tool 1 (isolation) | 0.2 mm (8 mil) or 0.25 mm (10 mil) V-bit or end mill |
| Tool 2 (drill via / mount holes) | 1.0 mm carbide drill for via; 2.5 mm for M2 mount holes |
| Tool 3 (outline) | 1.0 mm flat end mill |
| Isolation pass count | 2× isolation paths around each trace (1× minimum if time-limited) |
| Z-depth isolation | substrate thickness − 0.05 mm = ~50 µm into FR4 (just past Cu) |
| Feed rate | 200–400 mm/min isolation, 60–120 mm/min drill, 100–200 mm/min outline |
| Spindle | 12k–20k RPM (per your mill's spec) |

**Workflow:** generate the spiral geometry from a small Python/KiCad script (parametrized on N, w, s, d_out). Export Gerber. Convert Gerber → G-code with FlatCAM or pcb2gcode. Mill in three passes: isolation top, drill, isolation bottom (flip + register on dowel pins).

A parametrized generator script can be added under `tools/bifilar_coil_gen.py` when you're ready — say the word.

---

## 5. Verification checklist (before any power)

1. Visual inspection under loupe: no isolation bridges, no broken traces. Run a continuity test from `OUT_TOP` around the spiral to center via (expect ~1.6 Ω), then center via through bottom spiral to `OUT_BOT` (expect ~1.6 Ω total, ~3.2 Ω end-to-end).
2. LCR meter @ 1 kHz: confirm $L_\text{net}$ within 30% of 6 µH estimate.
3. LCR meter @ 100 kHz: confirm self-capacitance gives reasonable impedance.
4. Network analyzer / VNA sweep 100 kHz – 50 MHz (use your SDR with a noise-source bridge if no VNA): confirm SRF lands in the 10–15 MHz window. If SRF lands below 8 MHz, reduce turn count or widen spacing.
5. Pot the coil in epoxy or silicone **before** the first on-head test (Mk1 onward). Bench tests can use it unpotted in a Faraday-fabric bag.

---

## 6. Sham control variant

For blinded RCT (F1 falsification), fab a **second identical coil** plus a **sham**:
- **Sham A (preferred):** same PCB geometry, but with the center via deliberately **omitted** (laser-marked but not drilled). Looks and weighs the same; coil is open-circuit and emits nothing when driven. Pi 4 ADC can detect open-circuit by reading no current — implement as a "sham detected" log channel so the experimenter remains blinded but the data record knows.
- **Sham B (alternate):** identical coil **wrapped in Faraday fabric** during sham trials, active during active trials. Quick-swappable; requires the experimenter to handle the swap (unblinds the experimenter but keeps the wearer blinded if done out of sight).

Pre-register which sham scheme is used before the first RCT session.

---

## 7. What this gets us

A milled bifilar PCB coil per this spec, paired with the inventory you have, lets us assemble — without procurement — the **wiki-canonical Mk1 Stabilizer drive element**. Combined with Pi 4 (control), Nano (watchdog), 9-axis IMU (head pose), Pi sensor kit (env + likely PPG), Faraday fabric (sham + bench containment), SDR (emission verification), and HV module (drive), we have **every piece needed to first-power a Mk1-class coil module under instrumented bench conditions**.

The only physical gates remaining are: (a) MCU-B watchdog firmware verified, (b) Faraday bench fixture built, (c) sham coil milled, (d) bench-only power-on with no human in the field. **None of those require purchase.**

---

## 8. Cross-refs

- [inventory_capability_map.md](inventory_capability_map.md) — what we have vs. wiki BOM
- [sprint_0.2_circuit_spec.md](sprint_0.2_circuit_spec.md) — overall Mk0 circuit spec this coil plugs into
- [architecture.md § 3.6](architecture.md) — connector/bus spec the coil module conforms to
- [safety.md](safety.md) — safety floor (current limit, kill line, FDTD verification)
- [wiki_synthesis.md § Pass 2](wiki_synthesis.md) — wiki-canonical Mk1 drive chain
- [falsification.md](falsification.md) — F1 sham control requirement
