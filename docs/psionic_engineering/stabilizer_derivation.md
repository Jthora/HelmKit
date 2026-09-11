# Psi Stabilizer for the HelmKit — derivation from physiology to coil

**Status**: working derivation, 2026-09-11. Decisions taken by Jordan on 2026-09-11 that frame it:
the Mk1 coil is designed and sized for **ordinary electromagnetism** (the wiki framework's α = 0
sub-theory), the primary physiological target is **HRV coherence near 0.1 Hz**, and the disk
diameter 122.1 mm is the free-space wavelength at 2.455 GHz (the deferred 2.45 GHz Defender band),
so it places no constraint on the Mk1 coil.

Companion tool: [`tools/stabilizer_field_model.py`](../../tools/stabilizer_field_model.py)
(stdlib-only near-field model of a bifilar pancake in the disk; tests in
`tests/test_stabilizer_field_model.py`). Mechanical context:
[`docs/mechanical/vp0_visual_prototype.md`](../mechanical/vp0_visual_prototype.md).

Every number below is either computed by the tool, read from a primary source named with its
PMID, or transcribed from the ICNIRP guideline PDFs and checked against them. Numbers taken from
the wiki are labelled as such.

---

## 1. What the sources actually specify

| Source | Coil | Frequency | Placement |
|---|---|---|---|
| wiki `Psi Stabilizer` (fusiongirl and cosmiccodex) | none; functional page. cosmiccodex adds Kuramoto / Ott–Antonsen theory | "sub-MHz, ICNIRP-bounded" | unspecified |
| wiki `Bifilar Coil Engineering` + `Ψ Resonator` | 0.3 mm traces, 0.2 mm gap, on a 110 × 90 mm oblate-spheroid shell; mode-matched winding | 40 kHz, 200 V pulsed, ~100 A | whole head |
| wiki `HelmKit Mk1.0`, repo `mk0_pcb_bifilar_coil.md` | 30 × 30 mm two-layer series-opposing PCB spiral, 18 turns/side | 1–8 MHz carrier, 7.83 Hz envelope, "≤ 500 µT at scalp" | brow / rear pocket |
| repo Mk0.5-β Defenders | 12.24 mm caduceus pair on the ear line | 2.45 GHz reactive near field | ear discs |

None of these derives its frequency or amplitude from a physiological target. The two designs
are different physics regimes: 40 kHz is a capacitive, E-field-dominant regime; 1–8 MHz with a
7.83 Hz envelope is a magnetic-induction idea. The cosmiccodex mirror labels all pages drafts;
the two arithmetic errors `tools/verify_psi_equations.py` found on the coil page are still there.
The 729-page corpus does not contain "122.1". The Mk1.0 page's "≤ 500 µT at scalp" is not
compatible with the ICNIRP 2020 general-public reference level at MHz (2.2/f_MHz A/m, i.e. 2.8 µT
at 1 MHz averaged over 30 min), see §5.

## 2. Target physiology: HRV coherence

*What it is.* Heart-rate oscillation at the baroreflex resonance, close to 0.1 Hz (a 10 s
period, about six breaths per minute), with respiration, heart rate and blood pressure phase-
locked. Measured as LF-band (0.04–0.15 Hz) power concentrated in one peak, or as RMSSD rising
during pacing, which is exactly what `tools/analyze_g2.py` already scores.

*What moves it, with evidence.* Slow paced breathing at the resonance frequency, i.e. HRV
biofeedback. The mechanism is strengthening of baroreflex homeostasis (Lehrer & Gevirtz 2014,
PMID 25101026). Across 58 randomised trials the pooled effect is small to moderate, larger against
inactive than active controls, largest for anxiety, depression, anger and performance (Lehrer et
al. 2020, PMID 32385728). That is the effect size envelope a Stabilizer should be designed and
powered for; `tools/experiment_design.py power --d 0.4` gives the sample sizes.

*What does not move it acutely.* Transcutaneous auricular vagus nerve stimulation, i.e. electric
current at the ear, the closest thing to "field at the ear affects the vagus": a living Bayesian
meta-analysis of 16 sham-controlled studies finds strong evidence for the null on vagally mediated
HRV, g = 0.014, BF01 = 24.7 (Wolf et al. 2021, PMID 34473846). Any claim that a contactless field
at the ear steers HRV through the vagus starts from behind that result.

## 3. Coupling channels: dose needed, dose allowed, dose available

The disk coil modelled throughout is the one that fits the pod: a four-terminal bifilar pancake,
ID 40 mm (clears the Ø34 bayonet boss), OD 104 mm, 16.8 turn-pairs of 24 AWG (one metre of Cat5
yields the eight conductors), radial pitch 1.9 mm per turn of each spiral, in the disk plane
44 mm from the scalp, 52 mm from the cortex, 121 mm from the brain core.

| Channel | Physics | Dose that acts (source) | Dose allowed, general public | Disk coil delivers | Verdict |
|---|---|---|---|---|---|
| A. Induced E-field at ELF (Faraday) | dB/dt drives azimuthal E in tissue; the tACS mechanism without electrodes | ≥ 1 V/m to change spiking and subthreshold currents (Vöröslakos 2018, PMID 29396478); 2 mA scalp current reaches 0.8 V/m in cortex, "the lower limit of effectiveness in animal studies" (Huang 2017, PMID 28169833); in-vitro network entrainment at endogenous field strengths (Fröhlich & McCormick 2010, PMID 20624597) | in-situ E in CNS tissue of the head: 0.1/f V/m at 1–10 Hz, 0.01 V/m at 10–25 Hz, 4×10⁻⁴·f at 25–1000 Hz (ICNIRP 2010 Table 2); B reference 200 µT at 25–400 Hz, 5000/f µT at 8–25 Hz (Table 4) | aiding connection, 3 A (6 W in the wire): 250 µT at the scalp, **2.5×10⁻⁴ V/m** in cortex at 10 Hz. Reaching the legal 0.01 V/m needs 117 A; reaching 0.3 V/m needs 3500 A | **not a channel.** A pod coil cannot induce cortical fields within three orders of magnitude of any documented effect, legal or not |
| B. Capacitive E-field, kHz to MHz | the E-field between the ±V windings drives displacement current through the scalp; in-tissue E ≈ ωε₀/\|σ + iωε₀ε_r\| × applied | none established at MHz: membranes cannot follow; kHz tACS at 1 mA changes excitability (Chaieb 2011, PMID 21586823) and temporal interference demodulates two kHz fields (Grossman 2017, PMID 28575667), both at electrode-injected, stimulation-class amplitudes | in-situ E limit 1.35×10⁻⁴·f V/m (54 V/m at 400 kHz, 675 V/m at 5 MHz); local SAR 2 W/kg | opposing connection, 200 V: screening 1.8×10⁻⁵ at 40 kHz gives **5 mV/m** in tissue; 1.1×10⁻³ at 5 MHz gives **0.6 V/m at the tissue surface**, decaying inward, at 5 MHz; SAR ≈ 1 mW/kg | **the wiki's 40 kHz E² design deposits nothing.** At MHz it deposits tACS-scale fields, but at a frequency with no established neural effect. Legal either way |
| C1. Larmor-frequency RF, µT-class | radical-pair magnetoreception is disrupted at the electron Larmor frequency of the ambient field | robins disoriented by 1.315 MHz at **0.48 µT** aligned 24° to the geomagnetic field (Thalau 2005, PMID 15614508); 7 MHz and 0.1–10 MHz broadband (Ritz 2004, PMID 15141211); urban noise 50 kHz–5 MHz, screened ~100×, restores orientation (Engels 2014, PMID 24805233) | 30-min reference level 2.2/f_MHz A/m, i.e. **2.1 µT at 1.315 MHz**; in-situ E 178 V/m | aiding connection: 84 µT per ampere at the cortex, so **0.48 µT needs 6 mA**; SAR negligible | reachable, legal, cheap. Human relevance unknown, and Wang 2019 (below) rules the radical-pair mechanism out for the one documented human response |
| C2. Earth-strength static / slow field rotation | polarity-sensitive transduction (magnetite-like) | alpha-band desynchronisation in human EEG on rotating a 35 µT-class field, sensitive to static components and polarity (Wang et al. 2019, PMID 31028046) | static field: no ICNIRP low-frequency limit below 1 Hz (static-field guidelines apply, tesla-class) | aiding connection, 0.3 A: **25 µT at the cortex**, any slow waveform | the strongest human weak-field datum, and the easiest exposure to reproduce. Replication status must be checked before it carries design weight |
| C3. ELF magnetic, tens of µT | mechanism unknown (far below channel A thresholds) | nocturnal intermittent circularly polarised 60 Hz at **20 µT** reduced HRV power in the blood-pressure / thermoregulation band and raised the respiratory band in two double-blind studies of 77 volunteers; continuous exposure did nothing (Sastre 1998, PMID 9492166); 28.3 µT gave LF-band reductions in older men, REM reductions in older women (Graham 2000, PMID 11068226); a later 24-man study without catheters found no HRV change (Graham 2000, PMID 10972952) | 200 µT reference at 60 Hz | aiding connection: **28 µT at the scalp at 0.2 A** | the only published weak-field HRV effect, fragile and unreplicated in one attempt. Directly reproducible by this coil at 60 Hz; the Mk1 H1 experiment writes itself |
| D. Sensory pacing (light, sound, bone conduction, haptic) | the established HRV biofeedback route | resonance breathing at ~0.1 Hz (Lehrer 2020) | n/a | the brow LEDs and the bone-conduction transducers already in the BOM | **this is what makes a Stabilizer stabilize under α = 0** |
| E. Contact electrical (tACS, taVNS) | electrodes | tACS ≥ 0.8–1 V/m works; taVNS null on vmHRV acutely (Wolf 2021) | ICNIRP contact-current rules | the pods do not touch the head by design | out of scope for the pods |
| F. ψ / F² coupling (α ≠ 0) | the wiki's mechanism | wiki-defined TML protocols | as B | opposing connection maximises inter-winding E²; note from B that the in-tissue EM field at 40 kHz is negligible, so a 40 kHz ψ effect would be an effect of the field in the pod, not in the head | outside this derivation; the same coil serves it |

A physical fact behind rows A and B that both wiki designs skip: amplitude-modulating a MHz
carrier at 7.83 Hz does not produce a 7.83 Hz field in tissue. dB/dt is dominated by the carrier,
tissue is linear at these levels, and there is no demodulation. An induced field at an ELF rhythm
requires driving the coil at that rhythm, where row A applies.

## 4. Field model and its verification

`tools/stabilizer_field_model.py` sums Biot–Savart over the two spiral filaments for B, the vector
potential for the induced field (E = −∂A/∂t), and Coulomb line charges for the electrostatic field,
then applies the tissue screening factor and compares with the ICNIRP general-public tables. Tissue
parameters are Gabriel-class approximations for grey matter and are so labelled. Checks:

- a single loop's on-axis B matches the analytic formula to 0.5 % (test);
- the transcribed ICNIRP 2010 Table 2 and Table 4 values match the guideline PDF line for line
  (`0.1/f`, `0.01`, `4×10⁻⁴f`, `0.4`, `1.35×10⁻⁴f`; `4×10⁻²/f²`, `5×10⁻³/f`, `2×10⁻⁴`, `8×10⁻²/f`,
  `2.7×10⁻⁵` T) and the ICNIRP 2020 Table 5 values match `docs/safety.md` §2 (`300/f_M^0.7` V/m,
  `2.2/f_M` A/m);
- series-opposing cancels the far field by more than 10× relative to series-aiding (test).

Key results for the pod coil (ID 40, OD 104, 16.8 turn-pairs, 24 AWG):

| Connection | L | C | SRF | R (5 MHz) |
|---|---|---|---|---|
| opposing (Tesla) | 6.7 µH | 155 pF | 4.9 MHz | 2.7 Ω |
| aiding | 83 µH | 155 pF | 1.4 MHz | 2.7 Ω |

**As built (vp0.15 `coil_former`, 2026-09-11).** The printed former in the disk cavity winds the pair from r 22 to r 50 at 1.9 mm pitch (ID 44, OD 100, 14.7 turn-pairs): the outer turns would clip the six dome-boss holes at r 51.7, and 0.8 mm ribs between furrows are the thinnest a 0.4 mm nozzle prints reliably. Re-running the model with `--id 44 --od 100 --pitch 1.9`: opposing 5.5 µH / 136 pF / 5.8 MHz, aiding 68 µH / 136 pF / 1.66 MHz, 0.55 Ω, 3.3 m of wire per spiral. At 1 A aiding, 10 Hz: 127 µT at the scalp, 74 µT and 6.4×10⁻⁵ V/m in cortex, 0.6 % of the CNS in-situ limit; 155 A would be needed to reach that limit and 4700 A for a tACS-class 0.3 V/m. The conclusion in §3 is unchanged; only the lumped values move by about 18 %.

| Drive | B scalp | B cortex | E_ind cortex | E_ind / CNS limit |
|---|---|---|---|---|
| aiding, 3 A, 10 Hz | 430 µT | 250 µT | 2.2×10⁻⁴ V/m | 0.02 |
| aiding, 0.2 A, 60 Hz | 28 µT | 17 µT | 2.7×10⁻⁵ V/m | 0.001 |
| aiding, 6 mA, 1.315 MHz | 0.9 µT | 0.5 µT | 0.06 V/m | 3×10⁻⁴ |
| opposing, 0.3 A, 200 V, 40 kHz | 0.5 µT | 0.4 µT | 2×10⁻⁴ V/m (plus 5 mV/m capacitive) | 10⁻⁵ |
| opposing, 0.3 A, 200 V, 5 MHz | 0.5 µT | 0.4 µT | 0.19 V/m (plus 0.6 V/m capacitive at the surface) | 3×10⁻⁴ |

## 5. What this makes the Mk1 Stabilizer

1. **The stabilizing function is sensory pacing.** Under α = 0 the only route from this hardware
   to HRV coherence with evidence behind it is a resonance-frequency breathing guide delivered by
   the brow LEDs and bone conduction, closed-loop on the PPG through `analyze_g2`. The wiki's own
   "Anchor (closed-loop)" mode is this, with the emission replaced by a pacer. Design it first; it
   is the part that will demonstrably work.
2. **The disk coil is the experimental arm, not the actuator.** One four-terminal bifilar
   pancake per disk, connected at the driver, gives every exposure the evidence supports:
   - *aiding, 60 Hz intermittent, 0.2 A*: reproduces the Sastre / Graham 20–28 µT exposure, the only
     published weak-field HRV effect. A pre-registered crossover on the developer, scored with the
     existing tool, is a legitimate Mk1 study.
   - *aiding, slow rotation, 0.3 A*: Earth-strength field at the cortex for a Wang-2019-class
     alpha-ERD test once EEG exists (Mk2).
   - *aiding, 1.315 MHz, 6 mA*: the Larmor exposure, for a radical-pair test if anyone wants one.
   - *opposing, 40 kHz or 1–8 MHz, up to 200 V*: the wiki's E²-maximising configuration for the
     ψ arm, with the in-tissue numbers above on record.
3. **The sham needs a second layer.** Cancelling B alone (opposing) leaves E; cancelling E alone
   (aiding, same potential) leaves B. The architecture page's both-channel sham requires a
   counter-wound second pancake stacked on the first. The cavity should keep room for two.
4. **The coil apparatus envelope**, for the mechanical set: two stacked pancakes on printed
   spiral-groove formers, each Ø106 × 3 mm, ID 40, four terminals each, plus a few millimetres for
   a matching network: **Ø106 × 12 mm, centre hole Ø40**. The current `DISK_CAVITY = (110, 12)`
   already fits it; the knob shaft and clip pass through the centre hole with 13 mm to spare.
   The former is a parametric print (`build_coil_former.py`, not yet written): a double
   Archimedean groove 1.0 wide, 1.0 deep, pitch 1.9, from r 20 to r 52.

## 6. Safety numbers for the missing row

`docs/safety.md` §2 has no row for a near-field E-field-dominant sub-MHz emitter. The model gives
the numbers that row needs, for the 200 V opposing configuration at the scalp: in-situ E 5 mV/m at
40 kHz against a 5.4 V/m limit; 0.06–0.6 V/m at 1–5 MHz against 135–675 V/m; local SAR below
1 mW/kg against 2 W/kg; external B under 0.5 µT. The external E at the scalp (≈160 V/m at 44 mm)
exceeds the 83 V/m reference level, which the guidelines say is expected for a source within
centimetres and must be settled by the in-situ dosimetry, which passes. This is a proposal for the
safety review, not a change to the table.

## 7. Validation ladder

- **Bench.** LCR at 1 kHz and a self-resonance sweep against the L, C and SRF above; a 10-turn
  pickup coil at 44 and 52 mm against the B column; a dipole probe for the external E. Agreement
  within 20 % validates the model; disagreement re-calibrates the tissue-free part before any
  human exposure.
- **Human, α = 0.** (a) Pacer only versus no pacer, within-subject ABAB, RMSSD and LF peak,
  `analyze_g2`. (b) Sastre replication: 60 Hz intermittent 28 µT versus sham, double-blind
  crossover, nocturnal or resting, LF power. Pre-register both with
  `experiment_design.py preregister`; power with `experiment_design.py power --d 0.4`.
- **Human, ψ arm.** The wiki's TML-2 and TML-3 protocols, with the both-channel sham, only after
  the α = 0 arms have a baseline.

## 8. Open questions, ranked by how much they change the design

1. Replication status of Wang 2019 and of the Sastre / Graham HRV effect. If neither has held up,
   channel C collapses to the Larmor curiosity and the coil is purely the ψ substrate.
2. Whether the resonance pacer alone reaches the Lehrer-class effect on this wearer. It is the
   cheapest experiment on the list and it gates everything else.
3. The safety row (§6) and the "≤ 500 µT at scalp" statement on the wiki's Mk1.0 page, which
   should be corrected to a frequency-specific value.
4. Whether the coil apparatus is one pancake or two (sham). Two is the recommendation.

## Sources (PMIDs)

Lehrer & Gevirtz 2014 25101026 · Lehrer et al. 2020 32385728 · Wolf et al. 2021 34473846 ·
Huang et al. 2017 28169833 · Vöröslakos et al. 2018 29396478 · Krause et al. 2019 30833389 ·
Fröhlich & McCormick 2010 20624597 · Chaieb et al. 2011 21586823 · Grossman et al. 2017 28575667 ·
Ritz et al. 2004 15141211 · Thalau et al. 2005 15614508 · Engels et al. 2014 24805233 ·
Wang et al. 2019 31028046 · Sastre et al. 1998 9492166 · Graham et al. 2000 11068226, 10972952 ·
Saunders & Jefferys 2007 17495661 · ICNIRP 2010 Health Phys 99:818 · ICNIRP 2020 Health Phys 118:483.
