# Safety floor

<!-- Source: docs/safety.md, docs/architecture.md §3, Psi Stabilizer
     external/psiStabilizer/docs/safety_guidelines.md
     Status: v0 (2026-05-18)
     Target length: 6-8 printed pages.
-->

The HelmKit sits on a wearer's head. Anything mounted on it that emits
energy is, by default, a wearable energy emitter aimed at a brain. The
safety floor is the document that makes that fact non-negotiable.

This chapter is the printed version of the project's binding safety
posture. The repository copy at [`docs/safety.md`](../../safety.md) is
the canonical machine-readable version; both copies say the same thing
and the more conservative copy wins if they ever drift. The chapter
inherits unchanged from the Psi Stabilizer project's
`safety_guidelines.md` document and extends the same posture for
head-mounted emitters.

The HelmKit is **not** a medical device. It is not intended to
diagnose, treat, cure, or prevent any disease. The front-matter
disclaimer in this volume and the project disclaimer at
[`docs/legal/disclaimer.md`](../../legal/disclaimer.md) are binding.
Nothing in this chapter relaxes either of those documents.

## 1. Hard exclusions — all generations

The following are not allowed on **any** generation of the HelmKit
without a documented and externally reviewed exception. There is no
software path to disable any of them. They are wired in at the hardware
layer.

1. **Unregulated transcranial direct- or alternating-current
   stimulation (tDCS / tACS).** Only medical-grade, current-limited,
   well-characterized stimulators may even be considered, and only at
   Mk2.0 or later. Mk1 does not ship any DC-coupled scalp stimulation.
2. **Very-high-voltage exposure on or near the wearer.** No
   high-voltage stages exit the rear-helm compartment. The bus is
   5 V DC; nothing else exists at the head.
3. **Unscreened photic stimulation at flicker rates in the
   photic-epilepsy band** (approximately 3–60 Hz). Photic modality, if
   shipped, requires explicit per-wearer photic-epilepsy screening and
   a written acknowledgement.
4. **Sustained radio-frequency emission at the head without measured
   specific-absorption rate.** Any RF emitter on the device must have
   measured SAR at the wear position on a head phantom (or equivalent),
   a hardware interlock that disables emission above a documented
   threshold, and a documented duty cycle, peak power, and average
   power.
5. **Stimulation without recording.** The hardware interlock between
   stimulation-enabled and recording-active is mandatory and is the
   single non-negotiable line in the entire architecture. It is enforced
   in firmware on MCU-A *and* in hardware via the GPIO-pull check on
   MCU-B; either layer disabling drive forces the system to a
   non-resettable lockout state.

## 2. Frequency-band posture

The project's working hypothesis space includes RF emission at
1.245 GHz, 2.45 GHz, and 300–900 MHz, pulsed at 1–100 Hz, for
brainwave entrainment. This section sets *when* each band is allowed on
the device.

| Band | Mk1 | Mk2 | Mk3 |
|------|-----|-----|-----|
| Sub-MHz pulsed magnetic ($\leq$ few hundred µT, Persinger-class) | **Allowed** as a Mk1 entrainment option (G2-c). Long literature trail; well-characterized safety envelope. | Allowed | Allowed |
| 300–900 MHz pulsed RF | **Deferred.** Not on Mk1 hardware at all. | **Allowed** behind a measured SAR figure, a hardware interlock, and a pre-registered study. First place this band can physically exist on the device. | Allowed if Mk2 evidence supports it |
| 1.245 GHz pulsed RF | Deferred | Deferred. Same gates as 2.45 GHz. | Decision deferred to Mk3 based on Mk2 evidence and regulatory review |
| 2.45 GHz pulsed RF | Deferred | Deferred. Microwave-band emission near the brain has known thermal SAR concerns; gates are stricter than sub-GHz. | Decision deferred to Mk3 based on Mk2 evidence and regulatory review |
| Audio (binaural, isochronic, bone-conduction) | **Allowed** as Mk1 entrainment option (G2-a) | Allowed | Allowed |
| Photic (visible LED flicker) | Allowed with photic screening (G2-b) | Allowed | Allowed |

"Deferred" does *not* mean "rejected." It means the device is not
allowed to physically emit in that band until the safety gates have
been crossed. The hypothesis is preserved as R&D scope; the device is
not allowed to be the place where that R&D first happens prior to the
gates being passed.

The posture reflects three pieces of physics. Sub-MHz pulsed magnetic
fields at sub-millitesla amplitudes have decades of published
characterization (Persinger, Koren, and the replication attempts that
followed). The safety envelope is known. Sub-GHz pulsed RF at low
power exists in many consumer devices (Wi-Fi, cellular, Bluetooth);
near-the-head transmission is not novel — but the *specific pulsed
waveforms* the wiki framework proposes have not been characterized for
their interaction with neural tissue, and that characterization is
Mk2 work. The 2.45 GHz band at the head is the Wi-Fi and microwave-oven
band; even at low average power, pulsed waveforms there interact with
established tissue-absorption literature in ways that demand SAR
measurement, not assumption. Meanwhile, audio, photic, and sub-MHz
magnetic modalities can deliver 1–100 Hz brainwave entrainment with
none of these concerns. Mk1 exploits exactly those.

## 3. Per-wearer screening

Before any wear session, the operator screens for:

- **Photosensitive epilepsy history** — mandatory exclusion if any
  photic modality is in use.
- **Cardiac pacemaker or other implanted electronic device** —
  mandatory exclusion if any magnetic-coil or RF modality is in use.
- **Cochlear implant or metallic head implant** — mandatory exclusion
  for magnetic-coil modality; case-by-case review for any RF modality.
- **Pregnancy** — precautionary exclusion at Mk1; reviewable per
  modality at Mk2 or later.
- **Active migraine, recent concussion, or current neurological
  treatment** — case-by-case; default exclude.
- **Age under 18** — excluded at all generations of the research
  instrument. A future Mk3 wellness-product framing would require its
  own pediatric review and is out of scope for this volume.

A written screening form is filled out and stored with the session log.

## 4. Session safety procedure

Every wear session, every modality, follows the same seven-step
procedure:

1. **Pre-flight.** Visually inspect the device. Check cable integrity.
   Check battery state-of-charge. Verify the recording-active interlock
   with a meter — actually meter it, every session.
2. **Consent.** The wearer reads the modality-specific intended-use
   sheet and signs consent for that session, on paper.
3. **Recording first.** Begin recording **before** any stimulation
   hardware is energized. The interlock will refuse to enable the
   drive otherwise, but the operator does not rely on the interlock to
   catch operator error — recording-first is a habit and a checklist
   item.
4. **Begin stimulation.** The wearer reports a baseline subjective
   state — calm, energy, clarity, intrusive thoughts, body comfort —
   on a Likert panel logged alongside the physiological channels.
5. **Emergency-stop within hand reach.** The wearer holds an
   emergency-stop button at all times. A press triggers immediate full
   stim cutoff; recording continues. There is no "are you sure" prompt.
6. **End stimulation.** Recording continues for at least five minutes
   post-stim. This window catches any post-session physiological
   transients and gives the wearer time to settle before any data
   review.
7. **Close out.** Stop recording. Save the session log. The wearer
   reports a post-session subjective state on the same Likert panel.
   Both reports are stored with the log.

## 5. The hardware behind the rules

The procedure above only works if the hardware enforces it. Chapter 2
described the dual-MCU checker-doer pattern at the platform level. This
section is the wearer-relevant summary of what that pattern enforces.

**MCU-B has read-only authority over an opto-isolated cutoff on the
stimulation drive path.** MCU-A — the doer, which runs the user
interface, the BLE telemetry, and the modulation waveform — *cannot
bypass* the cutoff. MCU-A can only request that drive be enabled. If
MCU-B refuses, the drive does not energize.

MCU-B continuously measures drive forward and reflected power via a
directional coupler, coil temperature via a thermistor, body-proximity
via a capacitive sensor on the headband, and ambient field via an
independent electric / magnetic probe. It has its own LDO from the
battery, its own crystal, and its own firmware — written by a reviewer
who is not on the MCU-A team and audited under Frama-C, SPARK, TLA+, or
an equivalent peer-review path. The firmware target is under 5 kLOC,
with no dynamic memory allocation and no external dependencies beyond
the MCU vendor's HAL.

**On any MCU-B alert** — a blacklist hit, a watchdog timeout from MCU-A
exceeding 100 ms, a sensor reading out of envelope, body-proximity
lost — the system enters a **non-resettable lockout**. Drive is cut
immediately via the opto-isolated relay. The event is logged in
tamper-evident memory with a sequence number, cause code, and
timestamp. Recovery requires a physical reset action: a manual switch
inside the helmet, accessible only by removing the rearhelm cover. There
is no software-only path out of a lockout. That is intentional. The
checker's value depends entirely on its independence from the doer's
control path.

## 6. The blacklist

MCU-B ships with the following blacklist hardcoded. Any drive
configuration MCU-A requests that matches *any* row is refused before
the power stage is enabled. The blacklist is factory-set; modifying it
requires reflashing MCU-B with physical access to the helmet, on a
firmware image signed against a hardware-fused public key. MCU-B has no
remote update path.

| # | Forbidden configuration | Reason |
|---|---|---|
| 1 | DC pulses with rise time under 1 ms targeted near thorax-coupled hardpoints | Cardiac stimulation risk |
| 2 | 10–100 Hz pulse trains delivering over 1 mA effective into chest area | Cardiac stimulation risk |
| 3 | 3–8 Hz photic-frequency RF at over 100 V/m head-field | Seizure risk |
| 4 | Strong 1 Hz pulse trains with envelope over 50 % depth | Cardiac entrainment risk |
| 5 | Modulation envelope matching cardiac (0.8–3 Hz) or respiratory (0.1–0.5 Hz) rates at over 5 % depth | Cardiac / respiratory coupling |
| 6 | Pulsed RF 200–3000 MHz with peak power density over 40 mW/cm² and pulse width under 1 ms | Microwave auditory (Frey) effect |
| 7 | Continuous-wave near-field over 50 V/m rms at the head | ICNIRP exceedance |
| 8 | Peak pulsed E-field over 300 V/m | ICNIRP exceedance |
| 9 | **Any** drive while the recording-active GPIO is low | Stim-without-recording forbidden |
| 10 | Any drive while the body-proximity capacitive sensor reads "off" | No drive into open air |
| 11 | Any drive while coil temperature is over 45 °C | Burn risk |
| 12 | Drive duty cycle over 60 % averaged over 10 s | Defence-in-depth on rate control |

The list maps cleanly onto the five threat classes named in the
[`Psionic Threat Model`](https://wiki.fusiongirl.app/wiki/Psionic_Threat_Model)
wiki page — cardiac coupling, seizure, microwave auditory, ICNIRP
exceedance, and stim-without-recording. The mapping was deliberate.
The wiki names the threats; the project encodes them as MCU-B
firmware.

## 7. What we will not claim

The project's claim discipline is constrained by the same posture the
Psi Stabilizer project adopted:

- We will not claim the device improves cognition, protects from
  "psionic" attack, or has any wellness benefit until a pre-registered
  study with falsifiable measurements has been published with positive
  results.
- We will not claim the device is safe beyond the documented safety
  envelope of the modalities it actually implements.
- We will not use wiki or in-world framings as evidence. The wiki is
  design inspiration — see Chapter 4 — not evidence. The
  marketing-claim firewall described there is binding on every
  wearer-facing surface this project produces, including this volume.

The honest content of a wearer-facing Mk1 claim is something like:
*"This device runs a closed-loop heart-rate-variability biofeedback
session with optional audio entrainment, on a frame instrumented to
log the wearer's ambient electromagnetic environment for research
purposes. The biofeedback loop is grounded in published HRV
biofeedback literature. The audio entrainment is grounded in published
binaural-beat literature. Any additional effects from the bifilar coil
stimulation payload are under active research and are reported
honestly, either direction."* That is the floor. Anything beyond it
waits on evidence.

## 8. Data handling

Per session, the following are recorded:

- Sensor channels (biometric, EEG when present, ambient field).
- Stimulation parameters and timing.
- Wearer screening form (with a hashed identifier rather than the
  wearer's name).
- Wearer pre- and post-session subjective reports.
- Device serial number, firmware tag, and frame git-tag.

Storage, retention, and revocation policy follows
`external/psiStabilizer/docs/data_handling.md` until a HelmKit-specific
data-handling document is needed at Mk2 or later.

## 9. What this chapter is and is not

This chapter is binding on the wearer, the operator, the firmware
team, the hardware team, and any third party who builds a module
intending to mount on the platform. It is not legal advice. It is not a
substitute for a clinician's judgement in the screening step. It is not
a guarantee that the device is safe under conditions outside the
documented envelope — and the documented envelope is narrow by design.

When in doubt: don't drive. The cost of refusing a drive that would
have been fine is a session that fell back to the L0+L1+L2 biofeedback
floor, which is the project's wearer-benefit deliverable in any case.
The cost of permitting a drive that should have been refused is an
event the project does not recover its credibility from. The asymmetry
is built into every line of MCU-B firmware. It should be built into the
operator's habits too.
