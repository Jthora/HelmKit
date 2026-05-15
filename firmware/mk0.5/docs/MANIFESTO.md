# HelmKit Mk0.5 — Manifesto

This document is the **keel doc** for the Mk0.5 firmware. When any other
doc, comment, schema, or code change contradicts what is written here, this
doc wins, and the contradicting artifact is the bug.

---

## 1. Why HelmKit exists

HelmKit is a head-worn psi-tech device staged across a seven-step Mk
ladder (Mk0.0 → Mk3.0). The point of the ladder is not engineering polish:
it is to **make falsification cheap**. Every Mk-stage ships an artifact
that can produce a publishable result — positive, null, or anomaly —
*before* the next stage is funded or built.

Mk0.5 is the **biofeedback floor**. It carries no stim payload.

The Mk0.5 mission, in one sentence:

> Demonstrate that the L0 paced-breathing + L1 HRV-coherence rendering +
> L2 session-container stack, by itself, on a single substrate, produces
> reproducible wearer-benefit signal — *before* any bifilar-coil stim is
> introduced at Mk1.0.

Everything in this firmware exists to serve that mission. Anything that
does not serve it is dead weight.

---

## 2. Why Mk0.5 cannot fail by silence

A wearable physiological device that fails silently is worse than one
that never shipped, because silent failure produces *fictitious data*
which contaminates the falsification programme it was built to feed.

Therefore Mk0.5 firmware obeys this rule:

> Every failure must produce a structured, machine-readable, timestamped
> witness that is causally tied to the build that produced it.

Concretely:

- Every smoke-test failure carries a `SmokeFail` enum code (M9), a
  free-text reason, two evidence integers, the terminal `Health` of the
  driver, and the `boot_id` of the running firmware.
- Every NDJSON line carries the schema version, git SHA, dirty flag, and
  boot ID so a single line is sufficient to reconstruct *which build
  produced this exact byte*.
- The status LED carries a temporally non-aliasing safety-witness
  pattern (M10) so an observer who glances at the device for one second
  cannot confuse a transient fault with a safety-halt state.

If a future contributor adds a code path that fails without producing
one of these witnesses, that code path is a bug.

---

## 3. Why the schema is subordinate to the physics

The NDJSON schema, the SmokeFail enum, the LED patterns, and the serial
command grammar are *engineering conveniences*. They serve the physics
investigation, not the other way around.

This means:

- The schema MAY be broken at any Mk-version boundary if doing so
  produces a clearer measurement.
- Backwards-compatibility with previous Mk-version logs is **not** a
  blocking constraint. Re-emit historic logs through a re-parser if you
  must; do not contort the live wire format to preserve the past.
- The `schema` field in every NDJSON line exists precisely so that future
  parsers can reject incompatible historic data deliberately, rather than
  silently mis-parsing it.

What the schema **must** preserve is *self-description*: every line must
be sufficient, in isolation, to identify the build that produced it.
That is non-negotiable.

---

## 4. Why the safety floor is sacred

Mk0.5 carries no stim payload, so the operative safety surface is small:
heat-dissipation, electrical isolation of the AFE, and the protocol-level
discipline of never claiming clinical effect.

But the *protocol* for safety-halts established here will be inherited by
Mk1.0+ when stim is introduced. Therefore, even at Mk0.5 with no stim
hardware:

- Stim-fault codes (`kStim*`, range 100–199 in SmokeFail) are reserved
  *now* (M9). Downstream tools compile against them today.
- The `kSafetyHalt` LED pattern (M10) is implemented *now*, even though
  Mk0.5 cannot currently raise a stim-induced safety halt.
- The "force-retry after safety-halt requires an operator-acknowledgement
  capital `R`" gate is enforced *now*, even though no fault in Mk0.5
  currently triggers it.

The keel principle: **the safety protocol exists before the hazard does**.
If we wait to write the protocol until Mk1.0 ships, we will write it
under pressure, and we will get it wrong.

---

## 5. Why every error is a scientific datum

A driver that fails is not a bug to be fixed and forgotten. It is
*data*. The fact that the MAX30102 returned `kLowSampleRate` at this
ambient temperature, with this skin contact, on this electrode pad
generation, is a datum about the sensor stack that matters for the
falsification programme.

Therefore:

- `SmokeResult::fail()` is not an error-return convention. It is a
  structured observation.
- Free-text reason strings are sanitized but not truncated; they
  describe the *observed* condition, not a polite excuse.
- The NDJSON `kind:"smoke"` line is treated as scientific output, not
  diagnostic chatter. It is logged to the Pi sink, archived, and
  citable.

Future AIs reading these logs years from now must be able to
reconstruct, from the NDJSON stream alone, the empirical envelope in
which Mk0.5 was operated.

---

## 6. Why this doc exists

The compaction-resistant version of the Mk0.5 worldview lives here, in
prose, not in code comments. Code rots, comments lie, but a one-page
manifesto in the docs tree is checked into the repo and version-tagged.

If you are a future contributor (human or AI) and you find yourself
about to write a feature, a refactor, or a schema change that
contradicts §1–§5 above, stop. Either change this manifesto first (with
a commit message explaining why the keel has shifted), or do not make
the change.

— Mk0.5 firmware, 2026-05.
