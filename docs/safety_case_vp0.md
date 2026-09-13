# HelmKit first-prototype safety case (vp0.17 print set, Mk0.5 firmware phase 2)

**Status:** v0, 2026-09-13. The safety argument for the first physical helm, hazard by hazard, with the control that
holds each one and the check that proves the control is in place. It inherits the rules in [safety.md](safety.md)
(hard exclusions, frequency-band posture, screening, session procedure) and the four-belt firmware model in
[`../firmware/SAFETY.md`](../firmware/SAFETY.md), and adds what the printed helm and the Track N firmware make
concrete. Nothing here is a claim of benefit. It is the list of ways this object could hurt its wearer and what
stops each one.

The order below is the order of severity for a one-person build. The coil comes last on purpose: it is the only
hazard in this document that does not exist until someone wires it, and the case's first rule is that it stays
that way until the gates in §6 are passed.

## 0. The rules this case rests on

1. **Nothing on the head emits energy at the first wear.** The first prototype is a sensing, pacing and logging
   instrument. The disks carry a foil lining and empty spool formers. No coil is wound, no driver exists, no
   current flows near the head. This is the Track M build policy and the Track N interlock (N-F8), and it is
   the single most important sentence in this document.
2. **A hazard control that cannot be verified is not a control.** Each row below names its check.
3. **Reference levels, not basic restrictions, are the operating limit for any future coil.** They are the
   numbers a phone magnetometer can check. Exceeding one needs a written dosimetry argument read by someone else.
4. **The four-belt firmware model stays:** stim outputs fail safe at pin init, everything else fails safe by
   default, no stim below Mk1, and stim without recording is impossible by hardware.

## 1. Mechanical

| Hazard | Where | Control | Check |
|---|---|---|---|
| A disk shears off the stalk under a hit and strikes the wearer or a partner | full trim, nexus stalk (PLA, layers across the bending load) | Disks are never worn in sparring: the combat trim has no disks, nexus, crown, visor or pylons by design. The full trim is a bench, sanctuary and filming configuration. | The trim table in the spec; no disk parts in the combat print list |
| Head impact transmitted by a rigid band | both trims | 7 mm PETG band with foam pad frames; the combat trim sits under standard sparring headgear, which remains the protective layer | Fit gate M-G1: the helm under headgear, 30 min shadowboxing |
| Sharp edges, pinch points at the nape dial and the bayonet | nape module, disk locks | 0.8 mm fillets on every printed edge; the pull-to-release dial; the knob is a centre knob with no exposed lever | Coupon A and B fit tests; a gloved-hand pass over every part before first wear |
| Eye strike from the sensor bar or the visor on a fall | combat trim bar, full trim visor | The bar sits on the band's outer front face, 1 mm chamfers, no part protrudes past the headgear's face opening more than the bar's 24 mm; the visor is full-trim only | Headgear fit report (`fit.txt`): parts through the face opening |
| Strangulation or snag by straps, cables, rope spines | rear halves, umbilical | No chin strap. The umbilical to the belt pack is a single cable with a zip-tie strain relief that pulls free of the base window under a load well below the strap's; rope spines are inside the band under flush covers | Pull test on the umbilical: it must release from the base before the band moves on the head |
| Small parts (nails cut flush, shear pins, pawl springs) coming loose in use | everywhere | Nails cut flush and captive under foam or covers; printed shear pins with the M3 centre screw; springs inside tunnels | Assembly checklist row per fastener; a shake test after assembly |
| Heat: PLA parts softening in a hot car under bolt preload | disks, formers, pods | Load-bearing parts are PETG (cradle, rear halves, nexus, covers); PLA parts carry no preload except the disk plate screws, which are torqued lightly | Material column in the parts table; a hot-car exposure of one PLA disk plate before Season 1 |
| Skin contact materials | pads, band inner face | PLA, PETG, closed-cell foam on hook-and-loop, washable; no adhesives on skin | Foam replaced and washed per the maintenance note |

## 2. Electrical and battery

| Hazard | Where | Control | Check |
|---|---|---|---|
| LiPo fire or swelling on the head | nape pod | 1000 mAh single-cell LiPo with a protection circuit; charged off the head only, on a fire-safe surface, never in the pod; the belt-pack option moves the cell off the head entirely and is the recommended sparring configuration | Charging procedure in the bench checklist; visual cell inspection before every session; the pod's slide switch cuts the cell |
| Deep discharge, brownout resets mid-session | nape pod | Firmware low-battery policy: under 3.5 V for 10 s ends the session cleanly, stops every stream, shows the fault page; brownout detector on and logged; the session resumes after an involuntary reset | Track N gate N-G3 on the bench (fake low battery with `V`, forced reset) |
| USB power on the head | nape pod USB-C window | The USB is for bench work and charging off the head; on the head the helm runs from the cell or the belt pack only | Session procedure step 1 |
| Shock from a mains charger | belt pack, bench | 5 V USB chargers only; nothing mains-connected touches the helm | Bench inventory |
| Wiring shorts through sweat | harness, junction bay | 3.3 V / 5 V logic only on the head; the junction window faces the +u end wall out of the sweat path (v0.17); drip lip; connectors keyed | Water-drip test on the assembled nape base with the electronics powered |

## 3. Sensors on the skin and near the eyes

| Hazard | Where | Control | Check |
|---|---|---|---|
| Current through the skin from the EDA module | forehead fabric patches | The GSR module applies a fixed low DC voltage across two electrodes on the same forehead; no path across the heart; no adhesive electrodes anywhere on the body by project rule | Measure the open-circuit electrode voltage and the short-circuit current of the module once; both go in this document |
| IR LED irradiance at the cornea | sensor bar, 850 to 940 nm LEDs 25 to 35 mm from the eyes | The LEDs are not fitted at the first prototype. Before they are: an IEC 62471 exempt-group budget for the irradiance at the cornea at the bar's standoff, then a measurement, then a duty cycle in firmware that cannot exceed it | The budget and the measurement written into this section before the LEDs are soldered |
| Thermopile, MAX30102 LED | bar, forehead carrier | MAX30102 LED current at the driver default (about 6 mA) is far under the skin and eye limits; the thermopile emits nothing | Driver constant recorded (`led_brightness`); no change without a note here |
| Bone conduction sound pressure | hub pads (Mk1) | Not fitted at the first prototype. Before it is: output limited in hardware to conversational level, measured with the transducer on a head form | Measurement written here first |
| Pacer light in the field of view | status LED, brow LED lane | The status LED is on the pod, not in view. The brow LED lane is not fitted at the first prototype; when it is, the pacer's rates (6 to 20 per minute) are far below the photic band, and screening for photosensitive epilepsy applies per safety.md §3 | Screening form; rate limits in `layers/pacer.h` |

## 4. Firmware behaviour that protects the wearer

| Property | Where it lives | Check |
|---|---|---|
| No stimulation output can exist below Mk1 | `safety/no_stim_below_mk1.h`, compile-time | Build fails if a stim symbol appears |
| A future coil driver cannot compile without a named gate record | Track N N-F8 interlock (to be added with the driver) | Build fails without `HELMKIT_COIL_GATE_PASSED` |
| Every channel carries a quality flag; failures are logged, not hidden | `log/ndjson`, SCHEMA §4 | Analyser integrity line: skipped lines, lost lines, boots |
| The helm cannot hang silently | 5 s task watchdog, boot line with the reset reason | Bench gate: the `W` key resets the board and the boot line says `task-wdt` |
| Low battery ends a session cleanly | `layers/power_policy.h` | Bench gate N-G3 |
| Cues are never emitted in a mode that forbids them | `layers/modes`, native-tested | `pio test -e native` |

## 5. Data and the wearer's privacy

Captures contain physiology. Raw files stay on the wearer's machines; anything published is scrubbed or
aggregated. Session logs carry a hashed identifier, the firmware tag and the print set version. This follows
safety.md §6 and the Track G honesty rails.

## 6. The coil, if and when it exists

None of this section applies to the first prototype, which has no coil. It is written now so the limits are set
before anyone is tempted.

**Field per ampere, as-built bifilar pancake (ID 44, OD 100, 14.7 turn-pairs of 24 AWG), from
`tools/stabilizer_field_model.py`:**

| Point | Aiding | Opposing (sham) |
|---|---|---|
| scalp, 44 mm from the coil plane | 127 µT/A | 1.35 µT/A |
| cortex, 52 mm, 30 mm off axis | 74 µT/A | 1.29 µT/A |
| brain core, 121 mm | 12.5 µT/A | 0.27 µT/A |

**Reference levels the scalp field is checked against (general public):**

| Frequency | Level | Current at which the scalp reaches it |
|---|---|---|
| static (ICNIRP 2009) | 400 mT | not reachable |
| 8 to 25 Hz (ICNIRP 2010) | 5000 / f µT, 500 µT at 10 Hz | 3.9 A at 10 Hz |
| 25 to 400 Hz (ICNIRP 2010) | 200 µT | 1.57 A |
| 400 Hz to 3 kHz (ICNIRP 2010) | 80 000 / f µT | 0.63 A at 1 kHz |
| 3 kHz to 100 kHz (ICNIRP 2010) | 27 µT | 0.21 A |
| 100 kHz to 10 MHz (ICNIRP 2020, whole-body 30 min, H = 2.2 / f_MHz A/m) | 2.1 µT at 1.3 MHz | 0.017 A |

**Hard limits for any driver that is ever built:**

1. A series resistor and a fuse in the coil lead fix the maximum possible current at **0.2 A** regardless of firmware
   (a 5 V supply into 0.55 Ω plus 24 Ω limits to 0.2 A; the fuse is the backstop). At 0.2 A the scalp sees 25 µT,
   inside every reference level up to 100 kHz.
2. The driver runs only at frequencies where the coil is a resistor, **below 400 Hz**, until a separate case is written
   for anything higher. Above 100 kHz the 2020 whole-body level is exceeded at 17 mA, and the bifilar coil's
   self-resonance (about 1.7 MHz aiding) makes its impedance unpredictable there anyway.
3. The sham is the opposing connection with its own measured residual (about 1 % of aiding at the scalp), set by a
   sealed random schedule, with the arm invisible to the wearer; the blind is proven by a forced-choice test before
   the first pre-registered block.
4. Screening per safety.md §3 applies to the coil modality: no implants, no pacemaker, no pregnancy, no recent
   concussion, adults only.
5. Recording runs before, during and five minutes after any current, and the emergency stop cuts the driver's
   supply, not a firmware flag.
6. Gates before the first current near a head: the phone-magnetometer bench map at 0.1 A against the model at the
   scalp, cortex and core distances, and the replication check on Wang 2019 and Sastre 1998 in the derivation.

## 7. First-wear procedure for the printed helm (no electronics)

1. Coupons A and B printed and their fit findings recorded before any large part.
2. The head-fit gauges (`band_gauge_front`, `band_gauge_rear`) worn and photographed before the cradle prints.
3. Every printed part passed over by a gloved hand for burrs and sharp corners; edges deburred.
4. The cradle assembled with the rear halves, nape module and pad frames only. Worn for five minutes seated, then
   thirty minutes moving, with someone else present the first time. Pressure points and slip recorded.
5. Only then the sensor bar, then the electronics on the bench (Track N checklist), then the electronics on the
   head with the belt pack option first.
6. Disks, nexus, visor and crown only for bench, sanctuary and filming use, never sparring.

## 8. What would change this document

A new emitter of any kind on the helm, a change to the coil geometry or the field model, a change in who wears
it, or a bench result that contradicts a check above. Each such change gets a new dated row here before the
hardware changes.
