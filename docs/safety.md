# HelmKit Safety Posture

The HelmKit sits on a wearer's head. Anything we put on it that emits energy is, by default, a wearable energy emitter aimed at a brain. This document sets the rules.

This document inherits from the psiStabilizer safety posture (`external/psiStabilizer/docs/safety_guidelines.md`) and extends it for head-mounted emitters.

---

## 1. Hard exclusions (all generations)

These are not allowed on **any** generation of the HelmKit without a documented and reviewed exception:

1. **Unregulated tDCS / tACS.** Only medical-grade, current-limited, well-characterized stimulators may be considered, and only at Mk2+. Mk1 does not ship any DC-coupled scalp stim.
2. **VHV / high-voltage exposure** on or near the wearer.
3. **Unscreened photic stimulation** at flicker rates in the photic-epilepsy band (≈ 3–60 Hz). Photic modality, if shipped, requires explicit per-wearer photic-epilepsy screening and a written acknowledgment.
4. **Sustained RF emission at the head without measured SAR.** Any RF emitter on the device must have:
   - Measured SAR at the wear position, on a head phantom or equivalent.
   - A hardware interlock that disables emission above a documented threshold.
   - A documented duty cycle, peak power, and average power.
5. **Stim without recording.** The hardware interlock between "stimulation enabled" and "recording active" is mandatory and is the single non-negotiable line in the architecture.

---

## 2. Frequency-band posture

The user's hypothesis space includes RF emission at 1.245 GHz, 2.45 GHz, and 300–900 MHz, pulsed at 1–100 Hz, for brainwave entrainment. This section sets when each band is allowed on the device.

| Band | Mk1 | Mk2 | Mk3 |
|------|-----|-----|-----|
| Sub-MHz pulsed magnetic (≤ few hundred µT, Persinger-class) | **Allowed** as a Mk1 entrainment option (G2-c). Long literature trail; well-characterized safety envelope. | Allowed | Allowed |
| 300–900 MHz pulsed RF | **Deferred.** Not on Mk1 hardware at all. | **Allowed** behind a measured SAR figure + interlock + pre-registered study. First place this band can physically exist on the device. | Allowed if Mk2 evidence supports it |
| 1.245 GHz pulsed RF | Deferred | Deferred. Same gates as 2.45 GHz. | Decision deferred to Mk3 based on Mk2 evidence + regulatory review |
| 2.45 GHz pulsed RF | Deferred | Deferred. Microwave-band emission near the brain has known thermal SAR concerns; gates are stricter than sub-GHz. | Decision deferred to Mk3 based on Mk2 evidence + regulatory review |
| Audio (binaural / isochronic / bone-conduction) | **Allowed** as Mk1 entrainment option (G2-a) | Allowed | Allowed |
| Photic (visible LED flicker) | Allowed with photic screening (G2-b) | Allowed | Allowed |

> **Important:** "deferred" does not mean "rejected." It means "the device is not allowed to physically emit in that band until the safety gates have been crossed." The hypothesis is preserved as R&D scope; the device is just not allowed to be the place where that R&D first happens, prior to the gates.

### Why this posture
- **Sub-MHz pulsed magnetic** at sub-mT amplitudes has decades of published characterization (Persinger / Koren / replication attempts). The safety envelope is known.
- **Sub-GHz pulsed RF** at low power exists in many consumer devices (Wi-Fi, cellular, Bluetooth). Wearable transmission near the head is not novel but has not been characterized for the specific *pulsed* waveforms the user proposes; that characterization is Mk2 work.
- **2.45 GHz at the head** is the Wi-Fi / microwave-oven band. Even at low average power, pulsed waveforms here interact with established tissue absorption literature in ways that demand SAR measurement, not assumption.
- **Audio + photic + sub-MHz magnetic** can deliver 1–100 Hz brainwave entrainment with none of these concerns. Mk1 should exploit that.

---

## 3. Per-wearer screening

Before any wear session, screen:
- Photosensitive epilepsy history (mandatory exclusion if photic modality).
- Cardiac pacemaker / implanted electronic device (mandatory exclusion if magnetic-coil or any RF modality).
- Cochlear implant / metallic head implant (mandatory exclusion for magnetic-coil modality; review for any RF modality).
- Pregnancy (precautionary exclusion at Mk1; reviewable per modality at Mk2+).
- Active migraine, recent concussion, or current neurological treatment (case-by-case; default exclude).
- Age < 18 (excluded at all generations of the research instrument; Mk3 wellness-product framing would require its own pediatric review).

A written screening form is filled out and stored with the session log.

---

## 4. Session safety procedure

Every wear session, every modality:

1. Pre-flight: visually inspect device, check cable integrity, check battery charge, verify recording-active interlock with a meter.
2. Wearer reads the modality-specific intended-use sheet and signs consent for that session.
3. Begin recording **before** any stim hardware is energized.
4. Start stim. Wearer reports baseline subjective state.
5. Wearer holds an **emergency-stop button** within hand reach. Press = full stim cutoff + recording continues.
6. End stim; recording continues for ≥ 5 minutes post-stim.
7. Stop recording. Save session log. Wearer reports post-session subjective state. Both reports stored with the log.

---

## 5. What we will NOT claim

Same posture as psiStabilizer:

- We will not claim the device improves cognition, protects from "psionic" attack, or has any wellness benefit until a pre-registered study with falsifiable measurements has been published with positive results.
- We will not claim the device is safe beyond the documented safety envelope of the modalities it actually implements.
- We will not use wiki / lore framings as evidence. The FusionGirl wiki is **design inspiration**, not evidence (see [wiki_anchors.md](wiki_anchors.md)).

---

## 6. Data handling

Per session, the following are recorded:
- Sensor channels (biometric / EEG / ambient).
- Stim parameters and timing.
- Wearer screening form (hashed identifier only).
- Wearer pre/post subjective report.
- Device serial + firmware tag + frame git-tag.

Storage, retention, and revocation follow `external/psiStabilizer/docs/data_handling.md` until a HelmKit-specific data-handling document is needed (Mk2+).
