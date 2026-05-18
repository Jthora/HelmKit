# Sister modules

<!-- Source: external/psiStabilizer/README.md, external/psionicDefender/README.md,
     README.md § "Sibling/sister project relationship"
     Status: v0 (2026-05-18)
     Target length: 3-5 printed pages.
-->

The HelmKit hosts modules. Modules belong to families. This chapter
introduces the two families the platform was built around, names what
each one does and explicitly does not do, and shows where each one
mounts on the platform's hardpoints.

## The two-family split

The split between the families is simple. One looks outward, at the
environment. The other looks inward, at the wearer.

| | Psi Defender | Psi Stabilizer | **HelmKit** |
|---|---|---|---|
| Direction | Outward — environment | Inward — self | **Platform — head-worn frame + bus** |
| Sense | Ambient EM, RF, acoustic | EEG, HRV, GSR | **Carries either or both** |
| Act | Detect, shield, alert | Entrain, feedback, baseline | **Mount, power, integrate** |
| Question | *What is the environment doing to me?* | *How am I responding, and how do I return to baseline?* | *Where does either question's instrument live?* |
| Repo role | Sister project (separate repo) | Submodule under `external/` | This repository |

Each family is its own repository and its own engineering arc. They
share a wiki corpus, a critique pass, a safety-guidelines document, and
a sensor-stack reference design. They do not share a frame. The HelmKit
is the frame.

The asymmetry — sister-as-separate-repo for Defender, sister-as-submodule
for Stabilizer — is a deployment detail and not a status statement. The
Stabilizer is pinned as a submodule because the HelmKit's wearer-side
software imports its capture and analysis libraries directly, and pinning
the version is how the import surface is held stable. The Defender is a
separate repo because HelmKit consumes its hardware designs (coil
geometries, shielding stacks, antenna patterns), not its software, and a
submodule pin would buy us less than a published BOM and a versioned
release tag.

## Psi Defender — outward

The Psi Defender is the **outward**-facing family. Its job is to detect
and respond to ambient electromagnetic, radio-frequency, and acoustic
phenomena — both the mundane ones (broadband RF noise, low-frequency
magnetic fields, infrasound) and the wiki-specified ones (non-Hertzian
near-field structure, scalar-wave components, intention-coupled field
gradients) under the project's working assumption.

The Defender's instrumentation falls into four blocks:

1. **Layered passive shielding.** Copper or aluminum foil, steel
   plating, mu-metal strips, and (for higher-cost builds) metamaterial
   inserts. The passive layer is mundane RF/EMC engineering and is
   defensible without the suppression prior. It mounts to the
   sidehelm and rearhelm hardpoints (`HP-S*`, `HP-R`) as printed shells
   that snap over the frame.
2. **Magnetic-field disruption.** Mu-metal strips for low-frequency
   redirection; neodymium magnet arrays for the wiki-specified
   "repulsor" topology. The magnet arrays mount to the temple booms
   (`HP-T*`) where the wiki's geometry is most easily achieved.
3. **Acoustic dampening.** Dense foam, mass-loaded vinyl, optional
   piezoelectric noise-cancelling modules. Mounts to the ear-shield
   hardpoints (`HP-EL`, `HP-ER`) on the existing `earShield-v3`
   accessory family.
4. **Active scrambler (optional, Mk2+).** Low-power RF or ultrasonic
   counter-emit, driven from a dedicated microcontroller, gated by the
   HelmKit's MCU-B checker the same way any other emitting module is
   gated. The active scrambler is the only block in the Defender family
   that is subject to the platform's stim-without-recording interlock.

The Defender's advanced subsystems — multi-dimensional copper or gold
tensor coils, magnetohydrodynamic-fluid loops (ferrofluid, mercury,
cold plasma), electrohydrodynamic-fluid loops (electrolytic salt water,
graphene water), and scalar-wave double-helix magnetoflux coils — are
the wiki-specified upper tier of the Defender family. They are not in
the Mk1 scope. They are named here so the reader can locate them in the
roadmap, not so the reader expects them in the first generation.

The Defender's primary audiences, named in its own project README, are
targeted individuals, ravers and festival-goers exposed to potentially
weaponized infrasound, and privacy/civil-liberties advocates. The
HelmKit is the integration point that lets any subset of those
audiences carry a configurable subset of the Defender stack on their
head, rather than as a separate piece of luggage.

## Psi Stabilizer — inward

The Psi Stabilizer is the **inward**-facing family. Its job is to
measure the wearer's nervous-system state — electroencephalography
(EEG), heart-rate variability (HRV), galvanic skin response (GSR),
ambient electromagnetic exposure as a wearer-context channel — and to
stabilize that state via gentle, peer-reviewed entrainment modalities:
binaural and isochronic audio, dim photic entrainment, and (Mk2+, only
with attorney review and explicit safety-floor compliance) medical-
grade transcranial alternating-current stimulation.

The Stabilizer adopts the operational definition the Defender project
introduced and the Stabilizer project carries forward: *Psionics =
Psychological Electronics. Psi = EM Pressure.* A Psi Stabilizer is
therefore a **homeostatic device for the electromagnetic-psychological
pressure on the nervous system**. The definition is doing real work — it
names the thing being stabilized in measurable terms (EM pressure on
neural tissue, indexed by HRV and EEG) and it draws the line between
what the Stabilizer is (homeostatic instrument) and what it is not
(broadcaster, transmitter, treatment device).

The Stabilizer's first archetype, A01, is a baseline logger: a
Raspberry-Pi-class compute node with a MAX30102 photoplethysmography
sensor (HRV), an RM3100 magnetometer (ambient EM), a TSL2591 light
sensor, and a microphone, all streaming asynchronous NDJSON to local
storage. A01's BOM is approximately $165 at v0.1; the v0.1 buy-list
itself is ~$5 (just the MAX30102 breakout), with everything else drawn
from project inventory or documented-deferred with explicit trigger
conditions. A01 mounts to the rearhelm hardpoint (`HP-R`) for the
compute node and to the temple booms (`HP-TL`, `HP-TR`) for the
biosignal sensors. The ear-shield hardpoints (`HP-EL`, `HP-ER`) carry
the audio-entrainment transducers.

Subsequent archetypes (A02 through A12) extend the baseline: paced-
breathing biofeedback (A03), photic entrainment (A04), tACS-grade
stimulation (A07, behind the safety floor), group-coherence multi-
wearer protocols (A11). The full roster is in
`external/psiStabilizer/docs/archetypes/02_roster.md` and is not
duplicated here. What matters for this volume is that *every Stabilizer
archetype is a HelmKit module*. The Stabilizer project's job is to
design the archetype, write the experiment pre-registration, and ship
the capture and analysis libraries. The HelmKit's job is to host it.

The real-world parallels the Stabilizer's own README names — tDCS, tACS,
neurofeedback, binaural beats, EEG biofeedback, HRV biofeedback — are
the mainstream-physics-defensible portion of what the Stabilizer family
ships. They are not a hedge. They are the floor below which every
Stabilizer archetype operates, regardless of how the framework-level
falsification work resolves.

## How sister modules mount on the platform

Every sister module mounts at one or more hardpoints. The mount itself
is the L1 contract from Chapter 2: a 2-bolt M3 pattern at 20 mm centers,
a captive-nut pocket, a polarity rib, a documented footprint envelope, a
4 mm × 8 mm cable pass-through to the L2 raceway. The cable is USB-C
PD, strain-relieved at the connector. The keyed module-bay shell and
the GoPro / Picatinny rail segment carry the mechanical load.

On the data side, each module declares which bus lanes it consumes
(I²C, USB 2.0 HS, UART) and what its safety profile is. The platform's
MCU-A reads the module's identity register, looks up the safety
profile, forwards it to MCU-B for cross-check against the blacklist,
and only then enables the data lane and the RF-enable GPIO. From the
module's perspective, mounting on a HelmKit is reduced to: print the
shell, terminate the cable, register the identity code, and obey the
RF-enable line. From the platform's perspective, hosting a module is
reduced to: provide the lane, gate the emit line, log the swap.

A typical Mk1 configuration mounts a Psi Stabilizer A01 baseline logger
(rearhelm + temple booms + ear-shields), a Psi Defender passive
shielding kit (sidehelm + rearhelm), and reserves the forehelm hardpoints
for the Mk2+ HUD optic. The L2 power budget for that configuration is
roughly 1.2 A at 5 V steady — well under the PMIC's 3 A cap — and gives
the wearer 8 to 12 hours of mission time on the Mk1 reference battery
(two 18650 cells, ~22 Wh).

## What this volume covers next

Chapter 4 reads the wiki as a specification rather than as fiction, and
shows the protocol the project uses to read it. Chapter 5 is the
field-theory primer, including the bifilar-coil derivation that landed
in v0 of this volume and that the Psi Defender's active scrambler block
and the Psi Stabilizer's photic-entrainment block both reference.
Chapter 6 is the safety floor — the document the wearer reads, and the
hardware interlocks behind it. The sister modules are the *occupants*
of the platform. The next chapters are about the *substrate they live
on*.
