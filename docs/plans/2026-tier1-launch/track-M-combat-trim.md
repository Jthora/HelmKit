# Track M — Combat Trim: pad-free sensing, modes and cueing for sparring

- **Status**: `scoped` (2026-09-11). Nothing built yet; mechanical work lands in the vp0 generators, firmware on the Mk0.5 host.
- **Owner**: HelmKit-side AI assistant + Jono.
- **Depends on**: the vp0.11 mechanical set (`tools/blender/vp0/`), the Mk0.5 firmware drivers already landed in Track J (MAX30102, MLX90614, GSR, MAX30205, AD8232), the G2 protocol and `tools/analyze_g2.py`, `tools/experiment_design.py` for pre-registration.
- **Unblocks**: a HelmKit that is usable in sparring; the Sanctuary ABAB (Track M-C4); the Mk1.5 Combat rung without waiting for coil stimulation.
- **Constraints set by Jono (2026-09-11)**: no adhesive electrodes on the body, sensing must survive movement and sweat, the HelmKit is specifically for combat training, no budget for new materials (a sub-$10 IMU is the one purchase this track asks for).

## 1. Purpose

Two things the current design does not do: sense the wearer without sticky pads, and survive a sparring round. The physiological derivation ([`docs/psionic_engineering/stabilizer_derivation.md`](../../psionic_engineering/stabilizer_derivation.md)) already moved the working function of the Stabilizer from the coil to a closed-loop regulator with a breathing pacer. This track gives that regulator senses that work under motion and sweat, a mode set for combat training, and a mechanical trim that can be worn under or as headgear.

The design principle behind every sensor choice: **fix the sensor to the head so the wearer's motion is common-mode**, measure the face without contact from the brow, measure the scalp through the pads the cradle already presses on, and take precision measurements in the still windows between rounds, which is when the Recover mode runs anyway.

## 2. Two trims from one cradle

| | Combat trim | Full trim |
|---|---|---|
| Cradle U, rear halves, nape module | yes | yes |
| Pad frames with sensors (§3) | yes | yes |
| Sensor bar (§4) | yes, 15 mm off the forehead, padded | replaced by the visor panel |
| Disks, nexus, pylons, crown arch | off, via the existing quick releases | on |
| Bone-conduction transducers in the hub pads | yes | yes |
| Fits under standard sparring headgear | required (gate M-G1) | not required |
| Purpose | training sessions | Sanctuary sessions, coil experiments, the look |

Sparring rules for the combat trim, checked by the assembly report in a `--trim combat` mode: no part beyond 20 mm from the skull except the sensor bar; no edge radius under 3 mm on anything facing the face; the sensor bar must be captive to the cradle by a breakaway that yields before the neck does (a peg that shears, not a bolt); the IMU logs every event above a threshold.

## 3. Sensing without adhesives

### 3.1 Channel map

| Channel | Sensor | Where | On hand? | Motion / sweat | Gives |
|---|---|---|---|---|---|
| Heart rate, HRV | MAX30102 reflectance PPG in the forehead pad frame, pressed on by the cradle (clinical forehead site) | front pad | yes (Diitao, driver landed) | in-round: coarse HR with IMU-referenced filtering; still windows: beat-to-beat RR via the existing `r_peak` path | `ppg-forehead`, `ppg-rr` |
| Heart rate, second source | remote PPG on forehead skin from the brow camera under the bar's own IR illumination | sensor bar | no (ESP32-CAM class, ~$10) | head-fixed camera, small relative motion; fails on impact frames, flagged | `rppg` |
| Heart rate at rest | head ballistocardiography from the IMU | hub node | IMU ~$3–5 (MPU6050) | still windows only | `bcg-rr` |
| Breathing rate | MLX90614 thermopile aimed at the nose tip: nostril airflow swings tip temperature each breath | sensor bar | yes (driver landed) | contactless, sweat-tolerant | `temp-nose`, `resp-thermal` |
| Sympathetic arousal, thermal | sustained nasal-tip temperature drop (thermal-imaging stress marker), forehead temperature | sensor bar, front pad | yes | contactless | `arousal-thermal` |
| Breathing effort, exertion sounds | bone-conduction transducer run as a contact pickup on the cradle, or an electret under the bar | hub pad / bar | transducer in the Mk1 BOM, not yet bought | the contact pickup ignores gym noise | `resp-audio` |
| Impacts, activity, balance | 6-axis IMU in the hub node | hub node | ~$3–5 | the one sensor that likes motion | `imu`, `impact` (g, direction, time), `activity`, `sway`, `still` |
| Skin conductance | two conductive-fabric patches in the forehead pad wired to the existing GSR module (its finger straps retire) | front pad | yes | sweat is the electrolyte; separate thermal sweating from arousal with the thermopile | `eda-forehead` |
| Skin temperature | MAX30205 ×2 in the hub pads | hub pads | yes | contact, sweat-tolerant | `temp-skin.L/R` |
| Thermal load, hydration | humidity in the front pad | front pad | no, cheap later | built for sweat | `pad-humidity` |
| Pupil, blink, gaze | brow IR camera, 850–940 nm LEDs, eye-safe irradiance budget per IEC 62471 | sensor bar | no (with the camera above) | sweat-immune | `pupil`, `blink`, `gaze` |
| Frontal EEG | dry electrodes in the front pad | front pad | Mk2 | Sanctuary only | later |
| Oracle | Polar H10 chest strap (dry electrodes, no adhesive) | chest | yes | validation sessions only | `oracle-rr` |

The AD8232 with 3M Red Dot electrodes leaves the wearable entirely; it may stay on the bench as a second oracle.

### 3.2 Fusion and quality

- Every channel carries a quality flag derived from the IMU (motion energy in the last 2 s) and from signal statistics (PPG perfusion index, thermopile variance).
- Heart rate is reported only when at least two of {pad PPG, rPPG, BCG} agree within 5 bpm, or one source has a high-quality flag.
- HRV (RMSSD, LF peak) is computed only inside `still` windows ≥ 60 s, detected from the IMU. In-round HRV is not reported at all.
- Breathing rate is the thermal channel, cross-checked by audio when present.
- Arousal index = pupil diameter (when the camera exists) else EDA response rate, with the nasal-tip temperature slope as a slow confirmer.
- Fatigue index = blink rate and duration, HR recovery slope after each round, and the between-round HRV trend, personalised over weeks (the concept doc's finding: per-user models beat general ones, calibration takes 2–3 weeks).
- Impact = IMU events above 10 g, logged with peak, direction and a 200 ms window; cumulative session exposure shown at the end.

## 4. The sensor bar (replaces the visor panel in combat trim)

- Envelope: 140 × 24 × 18 mm, padded on every face-facing edge, 15 mm off the forehead at the pad's plane, on the same two back-face pockets the brow links use, so it is a swap, not a rebuild.
- Window: a 40 × 14 mm face-facing aperture for the camera, the thermopile and the IR LEDs; the LED pacer strip stays on the underside.
- Breakaway: the links' pocket screws are replaced by a shear peg for the bar.
- Power and data ride the existing rail grooves.
- Eye safety: the IR LED irradiance at the cornea is budgeted and measured before the camera is enabled; a hardware current limit sits on the LED supply.

## 5. Pad frames (replace the plain foam blocks)

Printed frames, foam on the head side, with pockets for the sensors and their cables, held by the same pressure that holds the foam:
- **Front frame**: MAX30102 window, two conductive-fabric EDA patches 30 mm apart, humidity pocket, cable exit into the band groove.
- **Hub frames (L/R)**: MAX30205 pocket, bone-conduction transducer seat on the temple.
- **Rear frames**: plain, with the strap-slot pass-through.
The conductive liner for the Sanctuary shield bonds to the frames' outer faces and to the cradle, so the shield and the sensors share one part.

## 6. Modes and cueing

| Mode | Trigger | Targets | Actuators and cues |
|---|---|---|---|
| Sanctuary | manual | low arousal, 0.1 Hz coherence, sensory gating on | pacer on LEDs + bone conduction, magnetic quiet zone (full trim), liner |
| Tranquil | manual, default | coherence during daily use | pacer only |
| Combat-prime | round timer −60 s | sympathetic tone into the useful band | fast-breathing cue by bone conduction, 40 Hz audio burst (short dose, per the indefatigability concept doc §9), round timer on the bar |
| Combat-sustain | round start | hold attention, cap perceived effort | footwork-tempo cue, motivational cue, HR-zone tone, cooling once the nape unit exists |
| Recover | round end or `still` detected | fastest arousal drop, HRV rebound | cyclic-sighing cue, rest-length advice from HRV, hydration prompt |

Plus the **intrusion tally**: one button, one timestamp per intrusive-thought episode, stored with the state window around it. Round timing is manual at first (a button), then from the gym timer's bell via the audio channel.

## 7. Firmware work items (Mk0.5 host, Heltec V3 / ESP32-S3)

Host-side reference first, firmware second (the r_peak.cpp / rr_replay.py pattern): `tools/analyze_combat_session.py` + `tests/test_analyze_combat_session.py` (2026-09-11) implement M-F2, M-F3, the M-F4 rules and the M-F5 state machine on NDJSON captures, so hand-wired sensors can be scored before any firmware exists. Channel names proposed in `firmware/mk0.5/docs/SCHEMA.md` §2.3.

- M-F1: IMU driver, `still` detector, impact detector, activity index; NDJSON channels per SCHEMA conventions. (Host side consumes `still` and `impact` already.)
- M-F2 host reference done: thermal respiration on `temp-nose` (band-pass 0.1–1 Hz, adaptive peak picking, 1 s refractory) and the nose-tip slope per rest/round; firmware port open.
- M-F3 host reference done: SCR rate on `eda-forehead`/`gsr` (phasic rises 0.5–3 s above 0.5 % of tonic) withheld when the skin-temperature slope exceeds 0.05 °C/min; firmware port open.
- M-F4 host reference done: two-source HR agreement within 5 bpm or one high-quality source (≥ 80 % in-range beats per 10 s window), RMSSD only in still rests ≥ 60 s (assumed still without an IMU, flagged), HR recovery slope over the first minute of rest.
- M-F5 host reference done (`CombatModes`): Tranquil / Sanctuary (resonance pacer), Combat-prime (2 s / 1 s for 60 s), Combat-sustain (pacer off, impact cues), Recover (cyclic sigh until HR is within 20 bpm of resting or 90 s), tally and round cues, session summary; firmware port + cue hardware open.
- M-F6 (with the camera): pupil, blink and rPPG on a companion host (phone or laptop) since the ESP32-S3 lacks the headroom; the helm streams frames or the host holds the camera.

## 8. Mechanical work items (vp0 generators)

- M-M1 **done (v0.12, 2026-09-11)**: `build_pad_frames.py` (front plate + three carriers, hub L/R, rear L/R); the assembly's foam references now sit on the frames in both trims. The MAX30205 pocket moved from the hub plate to the rear plate (occipital skin): the hub plate could not hold the transducer seat, the cross-bolt clearance and a pocket at once.
- M-M2 **done (v0.12)**: `build_sensor_bar.py`. It mounts on the band's outer front face (two Ø4 printed shear pins + one M3), not on the brow-link pockets: the combat trim has no rails, and the band is the only stiff surface left at the brow. The carrier sits flush in the floor; the LED lane runs along the front edge.
- M-M3 **done (v0.12)**: `assemble_vp0.py --trim combat` with the headgear phantom (25 mm shell, open face to z 70) and `fit.txt`. **Finding**: the sensing parts pass the 20 mm rule, the shared v0.11 cradle does not (hub nodes 26–34 mm proud, band top edge 24 mm off the narrowing skull, nape pin-lock 37 mm proud at the occiput). Gate M-G1 cannot pass with a standard padded headgear over this cradle; see M-M6.
- M-M4 **done for cables (v0.13)**: cable notches in every pocket tower, the coil-cable hole in the hub plate, the bar's back-wall exit slots into a 3 × 3.4 channel in the band's bottom face with a groove up to the LED bore (check-only cable routes in the combat assembly hold it). Still open: liner bonding surfaces.
- M-M5 placeholder: Ø17.6 / Ø15 × 2 seat on the hub plates; resize to the transducer once the Mk1 BOM names one.
- M-M6 (new, decision needed): a **combat cradle variant** or a headgear choice. Options: slim nodes without the nexus bolt group (the combat trim never mounts a nexus), a lower or chamfered band top edge, a flush nape lock, or an open-crown headgear with a face opening up to the band. Decide after wearing the printed cradle under the headgear on hand.

## 9. Validation ladder

| Gate | What | Pass |
|---|---|---|
| M-G1 fit | combat trim under standard sparring headgear, 30 min shadowboxing | stays put, no pressure points, headgear closes |
| M-G2 HR | forehead pad PPG vs Polar H10 during shadowboxing at three intensities, three sessions | in-round HR within 5 bpm of the oracle for ≥ 80 % of flagged-good time; RMSSD within 20 % in still windows (reuses the G2 criteria) |
| M-G3 breathing | thermal respiration vs manual count and oracle-derived respiration | within 2 breaths/min |
| M-G4 impact | IMU events vs video-annotated hits in light sparring | ≥ 90 % of hits detected, ≤ 10 % false events |
| M-G5 Sanctuary | sham-liner ABAB on the developer with the intrusion tally, pre-registered with `experiment_design.py preregister` | reported as measured; the result decides whether the RF ingredient matters for this wearer |
| M-G6 Combat | cue-on vs cue-off across sparring sessions, partner-blind, pre-registered | RPE per round, HR recovery slope, rounds completed; small effects expected (5–15 % class) |

## 10. Phasing and what it costs

| Phase | Needs money? | Delivers |
|---|---|---|
| 0 · now | no | pad frames and sensor bar printed; MAX30102, MLX90614, GSR patches and MAX30205 wired into the pads; M-G1 and M-G2 |
| 1 · one purchase | IMU ~$3–5 | impacts, stillness, BCG, activity; M-G3, M-G4; the mode state machine on the existing host |
| 2 · when affordable | ESP32-CAM class ~$10, electret | pupil, blink, rPPG, audio breathing; arousal and fatigue indices |
| 3 · Mk1 BOM | bone-conduction pair, LED strip | cueing on the head instead of a phone; M-G6 |
| 4 · later | nape cooling unit | Combat-sustain cooling; the ridgeway duct |

## 11. Risks

- In-round PPG SNR at the forehead under sweat and impacts: mitigated by the quality gate and by only promising HRV between rounds; if M-G2 fails the fallback is the H10 for combat HR with the helm as the cueing and logging platform.
- EDA patches shorting in sweat: use the thermal confirmer and report EDA between rounds only.
- IR eye safety: measured, current-limited, and the camera stays off until the budget is verified.
- Sensor bar under a hook: the shear peg is the fuse; the bar is padded; the camera module is the most expensive thing on the helm and sits behind it.
- Compute: pupil and rPPG do not fit the ESP32-S3; a companion host is assumed.
- Ladder semantics: `docs/mk_ladder.md` ties Mk1.5 Combat to H1 stimulation; this track delivers Combat sensing and cueing without stimulation, so the ladder entry should be amended to "Mk1.5 = motion-tolerant sensing + Combat cueing; stim optional".

## 12. What "Track M lands" means

The combat trim prints, fits under headgear, reports HR and breathing in round and HRV between rounds without anything adhesive on the body, logs every hit, runs the five modes with cues, and has produced one pre-registered Sanctuary result and one pre-registered Combat result. The coil is not on the critical path of any of it.
