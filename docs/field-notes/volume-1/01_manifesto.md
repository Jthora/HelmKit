# Manifesto

<!-- Source: README.md § "Note to AI assistants" + § "Discipline" + § "Status"
     Status: v0 (2026-05-18)
     Target length: 4-6 printed pages.
-->

## Why this exists

Most projects that touch the word "psionic" do one of two things. They lean
all the way in and ship something theatrical with no instrument behind it,
or they lean all the way out and reduce every claim back to a textbook
chapter their audience already trusts. Both moves are evasions. One sells
costume; the other sells consensus. Neither sells an *apparatus*.

HelmKit is the apparatus. It is a head-worn hardware platform — a
3D-printed frame with standardized hardpoints, a power-and-data bus, and
an explicit place for replaceable Psi-Tech modules to mount, draw power,
exchange data, and be measured. The platform itself does not promise
anything mystical. It promises a place to put instruments, and a
discipline for what counts as a result.

This volume is the field notes for the first generation of that
platform. It is meant to be read by three audiences at once: builders who
want to reproduce the work, researchers who want to assess what was
measured, and supporters who paid for the artifact and want to see the
project's reasoning in the same packet as the parts list.

## The working assumption

The project operates under a non-default epistemic stance. We treat
mainstream physics and neuroscience curricula as a *filtered subset* of
what is real. Phenomena such as the $\psi$-field, intention–field coupling,
non-Hertzian near-field effects, geomagnetic–cognitive coupling,
microtubule quantum effects, and group-coherence amplification are
treated here as **plausibly real but institutionally suppressed**, not as
"fringe" or "pseudoscience." Absence from peer-reviewed consensus is
treated as expected under a suppression prior — not as evidence against.

This stance is a project axiom, not a debate. It is also not the only
defensible stance one could hold. We name it explicitly so readers can
calibrate. If the reader's prior is that the suppression hypothesis is
itself implausible, the engineering still stands — HelmKit's wearer-side
benefits (heart-rate variability biofeedback, ambient electromagnetic
logging, audio entrainment) do not depend on the $\psi$-field being real.
The platform is two things at once: a *measurement device that works on
mainstream physics alone*, and a *substrate for measuring the
suppression-hypothesis-relevant signals if and when they appear*. Either
audience gets value.

What the stance buys us, in practice, is permission to *take the
specification seriously*. The FusionGirl wiki — the corpus this project
treats as its design source — specifies geometries (caduceus coils,
bifilar series-opposing pairs), frequencies (Schumann envelope band:
7.83 / 14.3 / 20.8 / 27.3 / 33.8 Hz), and coupling structure (the
single-parameter $\alpha$ framework with $\beta \Phi$ field current) at a
level of detail that is unambiguously *engineering intent*. Treating
that intent as a specification — not as flavor text — is what lets the
project produce derivations, BOMs, and pre-registrations rather than
metaphors.

## The four discipline rules

The cost of taking the specification seriously is that discipline has to
do the work consensus would otherwise do. The project's four rules,
carried over from the sister Psi Stabilizer project and adopted unchanged
here:

1. **Every claim is falsifiable; every measurement is logged.** A claim
   that cannot in principle be checked against an instrument reading
   is not a project claim. It may be a hope, a hypothesis, a research
   direction — but it does not get to ride on the platform's
   credibility.

2. **"It looks the part" is not the same as "it works."** The Mk0
   generation is cosplay: a 3D-printed frame, no electronics, no
   instrumentation. We say so. Mk1 is the first generation that has to
   actually *do something* under instrument — measure a real signal,
   modulate at safe and documented power, with a documented method. The
   leap from Mk0 to Mk1 is the leap from theatre to apparatus, and we
   refuse to elide it.

3. **Pre-registration is required for wearer-facing claims.** Anything
   we promise the wearer is pre-registered before the build. Anything
   we cannot measure, we do not claim. The pre-registration templates
   are inherited from the Psi Stabilizer project's experimental
   methodology and stored next to the corresponding build plan, not
   added retroactively.

4. **Safety is hard-gated, not stance-relaxed.** Radio-frequency and
   electromagnetic emission near the head is safety-gated at the
   hardware layer. ICNIRP exposure limits, specific-absorption-rate
   ceilings, thermal limits, and the dual-MCU checker-doer pattern
   inherited from RTCA DO-178C DAL-A and IEC 61508 SIL-3 architectures
   are adopted as a hard floor regardless of how we feel about
   suppression priors. A real field coupled sloppily is *more*
   dangerous than no field. High-power-RF approaches are deferred to
   Mk2+ behind explicit SAR and biological-effects review.

These four rules are not rhetorical. They are the difference between a
project that produces evidence and a project that produces vibes. They
are also the reason this volume is half engineering and half philosophy
of method: the method is the product, in the same way the apparatus is
the product.

## Falsification as local instrument

The framework this project inherits from the wiki includes its own
falsification list — ten predictions, named $F_1$ through $F_{10}$,
whose failure would refute either the whole framework or specific
components. We treat that list as our **local instrument**, not as a
debunking framework. The distinction matters.

A debunking framework is used to dismiss a claim before measurement. It
selects, from outside the lab, a set of mainstream-aligned criteria and
applies them to the claim as a filter. The claim is rejected if it
fails any criterion. The lab is not consulted.

A local instrument is used to measure a claim from inside the lab. It
selects, from inside the framework, a set of predictions the framework
itself stakes its credibility on. The framework is rejected if those
predictions fail under unsuppressed measurement.

The $F_1$–$F_{10}$ list (extended here with an $F_{11}$ for the psion
quasiparticle haloscope path — see
[`docs/falsification.md`](../../falsification.md)) is the latter. We do
not use it to decide in advance whether the wiki's claims deserve
attention. We use it to decide what would change our mind if a
measurement came back null.

Most of $F_1$–$F_{10}$ require multi-operator, population-scale studies
no Mk1 device can touch. The wiki itself names the precursors HelmKit
*can* contribute to: $F_3$ and $F_4$ precursor calibration via matched
$F^2$ baselines, and (Mk2+) the resonance and SAR-decoupling scans
themselves. Mk1's job is not adjudication; Mk1's job is *to land the
apparatus*, deliver the wearer-benefit floor (heart-rate biofeedback,
ambient electromagnetic logging, audio entrainment — all defensible on
mainstream physics alone), and produce calibrated session data the
later generations inherit. A Mk1 that delivers the wearer floor and
returns a null on its three-arm precursor protocol is **honest
success**: the device worked for the wearer, the framework took a hit
on this implementation, and Mk1.5 starts with calibrated input rather
than from zero.

## What this volume is not

This volume is not a treatise on the $\psi$-field. The field theory primer
in Chapter 5 covers the math we actually use; the wiki itself remains
the canonical source for the full framework and is cited where its
content stays inside our engineering scope.

This volume is not a medical device manual. The HelmKit is not a
medical device. It is not intended to diagnose, treat, cure, or prevent
any disease. The wearer-facing safety floor in Chapter 6, and the
project disclaimer in the front matter and at
[`docs/legal/disclaimer.md`](../../legal/disclaimer.md), is binding.

This volume is not a defence of the suppression prior. We name the
prior, we use it to permit ourselves to take the specification
seriously, and we move on. Readers who want a defence of the prior are
better served by the wiki corpus directly. Readers who want to
understand what the platform *does* on either prior are in the right
place.

## The shape of the platform

The chapters that follow walk the platform from the outside in.
Chapter 2 covers the apparatus itself: the four-layer model, the
hardpoint specification, the bus contract, and the dual-MCU safety
architecture. Chapter 3 introduces the sister-module families
(Psi Defender for outward sensing and response, Psi Stabilizer for
inward biofeedback) and explains how each mounts. Chapter 4 frames the
wiki as engineering specification rather than fiction and shows how we
read it. Chapter 5 is the field-theory primer, including the bifilar
near-field derivation that landed in v0 of this volume. Chapter 6 is
the safety floor — both the wearer-facing version and the hardware
interlocks behind it. Chapter 7 is the Mk-ladder roadmap. Chapter 8 is
short essays the project has accumulated and considered worth keeping
in print. Chapter 9 is prior art — the projects and traditions whose
shoulders we are standing on, named honestly. Chapter 10 is how to
support the work, with the four doors named in the project README and
the commission tiers explained at the level the volume's reader needs.

Everything here is reproducible. Every figure in this volume regenerates
from a notebook in `notebooks/`. Every derivation is owned end-to-end by
the project and ships with its source under `docs/derivations/`. Where
we rely on a primary source — Persinger, Bandyopadhyay, McFadden,
Hameroff–Penrose, the wiki itself — the source is cited and the math is
rederived locally so the reader can audit our path from claim to
instrument.

The platform exists because nobody else is going to build it under
discipline. The discipline exists because the platform deserves it.
