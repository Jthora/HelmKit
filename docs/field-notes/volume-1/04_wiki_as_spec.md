# Reading the wiki as a specification

<!-- Source: docs/wiki_anchors.md, docs/wiki_synthesis.md (referenced),
     docs/wiki_refactor_brief.md, README.md § "Note to AI assistants"
     Status: v0 (2026-05-18)
     Target length: 4-6 printed pages.
-->

Chapter 1 named the project's epistemic stance: mainstream consensus as a
filtered subset, the suppression prior as a working assumption, and
permission — once that prior is named — to *take the wiki seriously as
engineering intent*. This chapter is the protocol for how that
permission gets exercised in practice. It exists because "take it
seriously" is not a method until it is operationalized, and because the
project's deliverables (BOMs, derivations, falsification hooks,
pre-registered experiments) all flow downstream of a specific way of
reading a specific corpus.

## What the corpus is

The FusionGirl wiki ([https://wiki.fusiongirl.app/](https://wiki.fusiongirl.app/))
is a MediaWiki instance running 1.41.0 with a fully open query API.
The full page corpus is mirrored into the Psi Stabilizer submodule under
`external/psiStabilizer/docs/fusiongirl_dump/` as JSON batches, with
curated single-file extracts under `external/psiStabilizer/docs/wiki_extracts/`
and an engineering dossier at `fusiongirl_psi_engineering_dossier.md`.
At the time this volume was prepared, the corpus was approximately 4 457
pages, with a substantial content drop on 2026-05-12 that added or
materially rewrote the field-theory and hardware-spec pages this
project draws from most heavily.

The wiki is treated as *one* of three coordinated sources:

1. The wiki itself — design intent, geometry, frequency, and coupling
   structure.
2. The primary peer-reviewed literature the wiki cites (Persinger 2012,
   Bandyopadhyay 2013 / 2023 microtubule resonance, McFadden CEMI,
   Hameroff–Penrose Orch-OR, the Dotta / Saroka / Persinger series,
   Celardo superradiance, Kalra anaesthetic-microtubule work, the Utts /
   Cardeña parapsychology meta-analyses).
3. The project's own derivations — original math owned end-to-end by
   this repository, written from first principles against the wiki's
   geometries and the primary literature's data.

The wiki is *not* evidence. No claim about wearer outcome is justified
by a wiki quote. The wiki is *also not* fiction. We do not treat it as
flavour, lore, or mythology to be filtered out. It is design
specification at a level of detail that is unambiguously engineering
intent — and we read it that way.

## The Game-Tech / Real-World mapping

The wiki itself provides the bridge that lets this work. Its
[`Psi Tech`](https://wiki.fusiongirl.app/wiki/Psi_Tech) page maps every
"game-tech" device family to a "real-world parallel" — an explicit
engineering analogue that exists today or could be built today under
current physics. The mapping is the wiki's *own* idiom, not an
externally imposed reduction.

The HelmKit Mk1 design follows the **real-world side** of that mapping.
The game-tech side stays as long-horizon design intent for Mk2 and Mk3
— a target set of capabilities to be approached as evidence,
instrumentation, and safety review accumulate.

For the four wiki pages most relevant to this volume:

| Wiki concept | Real-world parallel adopted now | HelmKit generation |
|---|---|---|
| HelmKit "psionic sensory enhancement" | Multi-channel neural, biometric, and ambient-EM sensing (OPM-MEG-class magnetometers, dry EEG, RF survey radios) | Mk0.5+ |
| HelmKit "magnetogravitic bubble" | Layered EM shielding + active counter-field (the Psi Defender stack) | Mk2/Mk3 framing only |
| HelmKit "PsiSys interface" | Off-axis HUD combiner + closed-loop neurofeedback over a thin neural channel | Mk2+ |
| Psi Stabilizer internal/local/external | HRV biofeedback + audio entrainment + (Mk2+) tACS — wearer-side only at first | Mk0.5+ for internal; local/external indefinitely deferred behind the safety floor |

The wiki itself supplies the boundary lines. The HelmKit Mk1 honours
them.

## The four anchor pages

The project's design draws most heavily from four wiki pages.

**`HelmKit` (pageid 542)** defines the platform as a non-enclosed
psionic headpiece with three functions: psionic sensory enhancement,
the magnetogravitic bubble, and the PsiSys interface. The Mk1 spec
implements the first function in full and reduces the other two to
their real-world parallels (deferred to Mk2/Mk3 as named above).

**`Psi Stabilizers` (pageid 474)** distinguishes *internal* stabilization
(wearer's own neural state), *local* stabilization (immediate area),
and *external* stabilization (projected at range). Mk1 implements
internal only. Local and external are deferred indefinitely and gated
behind the safety floor in Chapter 6.

**`HelmKit Architecture`** specifies the dual-MCU checker-doer pattern
described in Chapter 2 and the bus-and-connector contract added on
2026-05-12 (USB-C PD power-and-data, keyed module-bay shells,
GoPro / Picatinny mechanical rail, I²C identity register, GPIO safety
line). Both are adopted wholesale. The pattern's lineage — RTCA
DO-178C DAL-A avionics, IEC 61508 SIL-3 industrial functional safety
— is the wiki's own citation.

**`Falsification Criteria for Psionics`** enumerates the ten
predictions $F_1$ through $F_{10}$ (now $F_{11}$ with the psion
quasiparticle haloscope candidate added in our own
[`docs/falsification.md`](../../falsification.md)) that the framework
stakes its credibility on. Chapter 1 named this list as the project's
*local instrument*. This chapter notes that the wiki itself provides
the methodological floor — pre-registration, $\geq 80\%$ statistical
power, multi-lab replication, raw-data-level reproducibility,
replication-crisis-era methodological tightness — that every HelmKit
pre-registration template inherits.

## The Pass 2 content drop (2026-05-12)

On 2026-05-12 the wiki published or substantially rewrote a cluster of
hardware-spec and field-theory pages that the project depends on:

**Hardware specifications:** `Bifilar Coil` (the Tesla series-opposing
geometry adopted in Mk1, derived in Chapter 5), `Caduceus Coil`
(opposite-chirality helices, far-field cancellation, Mk2 alternative),
`Double-Helix Antenna` (same-chirality axial-mode circular
polarization, Mk3 platform-radiator option), `Near Field
Electromagnetics`, `Reactive Near Field`, `Antenna Theory for Psionic
Devices`, `SAR Calculation for Psionic Devices`, `Psionic Device
Safety` (the 12-row safety blacklist summarized in Chapter 2 and
detailed in Chapter 6).

**Field theory:** `Psi Field` (canonical Lagrangian, $\Psi \equiv
T^{00}(\psi)$, $J_\psi$ definition), `Effective Field Theory of
Consciousness` (the $C$ order parameter and 5-coupling effective
theory, including the phase diagram with its runaway-regime warning),
`Quantization of the Psi Field`, `Soliton Solutions of Psi Field`,
`Renormalization of Psi Theory`, `CEMI Field Theory` (cited as the
*direct* EM-consciousness channel; the project's $\alpha \psi F^2$
mechanism is the *indirect* channel), `Intention as Psi Source`
($J_\psi = \beta\Phi$, $\beta \sim 10^{-40}$, with the explicit
warning that Mk0/Mk1 do not amplify intention).

**Methodology:** `Falsification Criteria for Psionics` (the F1–F10
list now extended locally to F11), `Open Questions in Psionics`,
`Psionic Threat Model` (five threat classes whose engineering
mitigations populate the safety blacklist), `Psionics Primer`,
`Psionics FAQ`.

The full anchor table — page-id, title, and which HelmKit document
each page feeds — is in [`docs/wiki_anchors.md`](../../wiki_anchors.md).

## The reading protocol

When the project consults the wiki — by a human reading directly, or by
an AI assistant operating under the rules in this volume's
introductory note and in [`docs/wiki_refactor_brief.md`](../../wiki_refactor_brief.md)
— we apply seven discipline rules. They are the practical content of
"taking the specification seriously."

**1. Do not dismiss by appeal to consensus.** If the reading you are
about to write would say "speculative," "no referent in physics,"
"not actionable," "ignore as flavour," or "$X$ is just mainstream-$Y$"
— stop. Those phrasings are the filter speaking. Re-read the page on
its own terms.

**2. Do not substitute mainstream equivalents for the specified
geometry.** The caduceus coil is *not* "just a helical antenna." The
opposite-chirality construction is the point of the geometry. The
bifilar series-opposing coil is *not* "just a wound inductor." The
high inter-turn electric field is the point. Chapter 5 derives the
on-axis field of the bifilar pair from first principles precisely to
make this concrete — and to be honest about where the geometry's value
actually lies (gradient and far-field falloff, not on-axis amplitude).

**3. Do not treat small coupling constants as a stopping condition.**
The wiki's framework explicitly bounds the bare $\alpha\,\psi\,F^2$
coupling at $\alpha \lesssim 10^{-10}$ of EM coupling — that is the
$F_{10}$ bound, and it is binding. The wiki's engineering paths around
the bare coupling are *resonant geometry*, *coherent envelope
modulation*, and *group amplification* (the Dicke superradiance $N^2$
scaling at Mk3). This is the whole reason the specification names
bifilar, caduceus, Schumann-envelope, and multi-wearer protocols. Small
bare $\alpha$ is the engineering problem the design is structured to
*solve*, not a refutation of the framework.

**4. Reason maximally from the wiki's own equations.** Where the wiki
is sparse, extrapolate within its framework rather than collapsing back
to consensus. Sparse math is treated as a redaction artifact, not as
absence of formalism. Derive what's missing; flag the derivation as
ours; ship it under `docs/derivations/`.

**5. Engineering discipline stays fully on.** The stance does *not*
relax safety, SAR limits, thermal floors, the dual-MCU checker pattern,
pre-registration, or the F1–F11 falsification framework. It
*strengthens* them — a real field coupled sloppily is more dangerous
than no field. Budget, inventory, mechanical fit, and time are
physical constraints unaffected by epistemic stance; we apply normal
engineering pragmatism there.

**6. Flag every source.** Every project claim is marked as
**(a) consensus-grounded**, **(b) wiki-grounded**, or
**(c) extrapolated**. Claims of type (a) are not weighted higher than
(b) by default. Claims of type (c) carry an explicit chain of reasoning.
The derivation chapter (5) and the falsification chapter
([`docs/falsification.md`](../../falsification.md)) both apply this
tagging visibly in their tables.

**7. Maintain the marketing-claim firewall.** Wearer-facing claim
language at any Mk-level is restricted to what *that* Mk-level can
actually demonstrate. Psion-mediated effects, $\psi$-field language, or
framework-internal vocabulary never appear in wearer-facing copy. The
firewall is named and enforced in
[`docs/wiki_refactor_brief.md §1.6`](../../wiki_refactor_brief.md) and
in the wearer-side safety document covered in Chapter 6. The Psi
Stabilizer's HRV biofeedback is a defensible wearer claim. The
bifilar coil's role as a low-power Primakoff-class converter via the
$\alpha\,\psi\,F^2$ vertex is engineering-internal language and stays
that way.

## What we do not use the wiki for

The wiki's mythos — the Clan Tho'ra and Jane Tho'ra characters, the
Natura franchise framing, the in-world narrative continuity — is
project flavour. It does not enter the bill of materials, the firmware,
or the safety posture. Where a wiki page contains both technical
content and narrative framing, we extract the former and leave the
latter alone.

The wiki's frequency and waveform suggestions are not adopted without
an independent literature trail. The Mk1 modality menu — sub-MHz
pulsed magnetic at the Persinger-class envelope, Schumann-band carrier
modulation, bone-conduction audio entrainment — is built from
peer-reviewed neuromodulation literature, with the wiki indicating
*which* literatures to look at rather than serving as a substitute for
them.

The wiki's narrative claims about specific historical actors,
suppressed programs, or named adversaries are framework-internal and
are not invoked to support any project deliverable. The threat model in
[`Psionic Threat Model`](https://wiki.fusiongirl.app/wiki/Psionic_Threat_Model)
is adopted at the engineering layer (its five threat classes mirror
specific rows in our safety blacklist), not at the narrative layer.

## What this gets us

The protocol pays off in three deliverables. First, it gets us
derivations that engage the wiki's geometries on their own terms — and
that are honest about what those geometries do and do not buy us
(Chapter 5). Second, it gets us a falsification list that is *the
wiki's own list*, treated as our local instrument
([`docs/falsification.md`](../../falsification.md)), rather than a
consensus-debunking framework imposed from outside. Third, it gets us
a generational roadmap (Chapter 7) where each Mk-level's claim
discipline is constrained by what *that* Mk-level can actually
demonstrate, regardless of what the framework as a whole might one day
support.

The wiki is a specification. We read it that way. We ship what reading
it that way produces. The chapters that follow are the proof of work.
