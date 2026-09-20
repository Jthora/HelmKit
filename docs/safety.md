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
| **Near-field E-field-dominant sub-MHz (bifilar/caduceus coil geometry)** | **⚠ GAP — TBD.** See note below. | TBD | TBD |
| 300–900 MHz pulsed RF | **Deferred.** Not on Mk1 hardware at all. | **Allowed** behind a measured SAR figure + interlock + pre-registered study. First place this band can physically exist on the device. | Allowed if Mk2 evidence supports it |
| 1.245 GHz pulsed RF | Deferred | Deferred. Same gates as 2.45 GHz. | Decision deferred to Mk3 based on Mk2 evidence + regulatory review |
| 2.45 GHz pulsed RF | Deferred | Deferred. Microwave-band emission near the brain has known thermal SAR concerns; gates are stricter than sub-GHz. | Decision deferred to Mk3 based on Mk2 evidence + regulatory review |
| Audio (binaural / isochronic / bone-conduction) | **Allowed** as Mk1 entrainment option (G2-a) | Allowed | Allowed |
| Photic (visible LED flicker) | Allowed with photic screening (G2-b) | Allowed | Allowed |

> **Important:** "deferred" does not mean "rejected." It means "the device is not allowed to physically emit in that band until the safety gates have been crossed." The hypothesis is preserved as R&D scope; the device is just not allowed to be the place where that R&D first happens, prior to the gates.

> **⚠ Near-field E-field-dominant row — flagged 2026-08-05, not resolved.** This table has no row that cleanly covers a **bifilar coil's actual physics character**: its whole design point is concentrating E-field between series-opposing traces while cancelling far-field B, which is structurally different from the "Sub-MHz pulsed magnetic" row's Persinger-class solenoid (a B-field device, justified below by magnetic-field literature only). Two open items, both needing the repo owner's review before being treated as settled — **no numeric threshold is proposed here**, deliberately, since drafting one without proper sourcing would risk being mistaken for a vetted limit:
> 1. **Missing row — verified against primary sources 2026-08-06 (corrects an error from the prior pass).** Two rounds of web-search-only research previously concluded that far-field reference levels categorically don't apply to this device because it operates in the reactive near-field. **That conclusion was wrong for this specific band, confirmed by reading the actual ICNIRP 2020 *Health Physics* paper (118(5):483–524) and IEEE C95.1-2019 synopsis directly (PDF text-extracted, not search-snippet-sourced).** ICNIRP 2020 explicitly states: *"EMF frequencies from 100 kHz to 30 MHz are treated as always being within the near-field zone... The present guidelines treat all exposures within this frequency range as near-field, and requires compliance with both the E-field and H-field reference level values in order to be compliant with the reference levels"* (p.496), and separately, for Tables 5/6/8: *"regardless of the far-field/near-field zone distinctions, compliance is demonstrated if neither Einc or Hinc exceeds the above reference level values"* (Table 5, Note 4, p.495). **This means ICNIRP's own simplified field-comparison route already applies to this device's whole 1–8 MHz band** — no SAR modeling is mandatorily required here (full SAR-only assessment only becomes mandatory above ~2 GHz reactive near-field, well outside this device's band).
>
> **Verified numbers, general public, at this device's 1–8 MHz carrier band** (three separate, simultaneously-applicable reference levels — all must be checked, not just one):
> | Table | Quantity/averaging | Formula | At 1 MHz | At 8 MHz |
> |---|---|---|---|---|
> | Table 5 (whole-body, 30-min avg) | E-field / H-field | `300/f_M^0.7` V/m, `2.2/f_M` A/m | 300 V/m, 2.2 A/m | ~70.0 V/m, 0.275 A/m |
> | Table 6 (local exposure, 6-min avg) | E-field / H-field | `671/f_M^0.7` V/m, `4.9/f_M` A/m | 671 V/m | ~156 V/m |
> | Table 8 (peak instantaneous) | E-field / H-field | flat, 100 kHz–10 MHz | 83 V/m, 21 A/m | 83 V/m, 21 A/m |
>
> (The earlier pass's "83 V/m applies below 6.27 MHz" framing was also imprecise — 83 V/m is Table 8's *constant* peak-instantaneous limit across the whole 100 kHz–10 MHz range; 6.27 MHz is just the incidental point where Table 5's frequency-dependent curve happens to cross 83 V/m, not an actual ICNIRP breakpoint.) **The localized-SAR basic restriction (2 W/kg averaged over 10 g, general public, 100 kHz–6 GHz, 6-min avg) is independently confirmed exact** — both ICNIRP 2020 Table 2 and the IEEE C95.1-2019 synopsis state this identically — but per the near-field rule above, checking Einc/Hinc against Tables 5/6/8 directly is the primary, simpler compliance path for this device; SAR is the backstop/basic-restriction quantity behind those reference levels, not a separately-required calculation here.
>
> **No power-based exemption exists in either primary standard** — both were searched directly for "exempt"/"mW"/"de minimis" language; ICNIRP 2020's only exemption is for touching a charged conductor (contact current), not a coupled coil, and IEEE's synopsis shows only a medical-procedure carve-out. The FCC's 1 mW blanket exemption noted in the prior pass is a *US regulatory* provision, separate from the ICNIRP/IEEE *health-guideline* numbers above — both are relevant, neither substitutes for the other.
>
> **Concrete next step, now well-defined**: measure or calculate this coil's actual E-field and H-field at the point(s) of interest (typically the head surface, given proximity) across the 1–8 MHz drive band, and compare directly against the Table 5/6/8 values above. This is now a bounded, primary-source-backed engineering task, not an open-ended "commission a dosimetry study" — and real near-field dosimetry precedent exists for essentially this exact geometry class (small coil close to a human head): published RFID-at-13.56-MHz-near-head exposure studies and wireless-power-transfer human-exposure dosimetry papers are close real-world analogs, closer than cellphone/base-station far-field literature. **Still TBD**: no pass/fail determination is made here — this device's actual field strengths at these frequencies haven't been measured or computed yet.
> 2. **Existing row may already be stale.** The Mk1 bifilar PCB coil actually specified in `docs/mk1_buildplan.md` (Pass 2 wiki-canonical: 1–8 MHz carrier, 7.83 Hz envelope) is driven at a 1–8 MHz *carrier* — arguably not "sub-MHz" at all, only its envelope is. The existing "Sub-MHz pulsed magnetic... Persinger-class" row's G2-c "Allowed" grant may currently rest on safety literature (Persinger/Koren solenoid studies) written for a different device than what's actually being built. This needs explicit review, not an assumption either way.
>
> Until this is resolved, treat the Mk1 bifilar coil's safety classification as **open**, not settled by the table's current "Allowed" language.

### Why this posture
- **Sub-MHz pulsed magnetic** at sub-mT amplitudes has decades of published characterization (Persinger / Koren / replication attempts). The safety envelope is known.
- **Sub-GHz pulsed RF** at low power exists in many consumer devices (Wi-Fi, cellular, Bluetooth). Wearable transmission near the head is not novel but has not been characterized for the specific *pulsed* waveforms the user proposes; that characterization is Mk2 work.
- **2.45 GHz at the head** is the Wi-Fi / microwave-oven band. Even at low average power, pulsed waveforms here interact with established tissue absorption literature in ways that demand SAR measurement, not assumption.
- **Audio + photic + sub-MHz magnetic** can deliver 1–100 Hz brainwave entrainment with none of these concerns. Mk1 should exploit that.
- **Near-field E-field-dominant (bifilar/caduceus)** — posture not yet set; see the flagged gap above.

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
