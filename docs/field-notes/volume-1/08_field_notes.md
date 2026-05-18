# Field notes

<!-- Source: Mk0 form-iteration history (3D-Models/), Track C derivation
     (docs/derivations/bifilar_near_field_enhancement.md), Sensor Wave 1
     (Mk0.5 in flight as of 2026-05-16).
     Status: v0 (2026-05-18)
-->

This chapter is the working bench log. It collects the actual work — the
iterations, the measurements, the math that paid off, the math that did
not, the prints that fit, the prints that did not — that produced the
device described in this volume.

The format for every entry is the same:

> **Date.** What we were trying to do. What we did. What we measured (or
> derived). What we changed in the design afterwards.

This is **Volume I's** bench log. It is intentionally short. The Mk0.5
Sensor Wave only finished its in-flight integration as this volume went
to press, so most of the entries that *will* live here are still
upstream of their first measurement. Subsequent volumes will carry
longer logs. We have chosen to ship the volume now, with the short log,
rather than wait — both because the design as it stands deserves to be
on record, and because the project's discipline is to publish at gates,
not to publish when the story is convenient.

---

## Entry 1 — Mk0 form, nine iterations (2024-Q4 → 2026-Q1)

**What we were trying to do.** Produce a printable, non-enclosed helmet
frame that fits a real human head, supports the eight hardpoint
positions described in Chapter 2, prints without supports on a hobby
FDM printer, weighs under 600 grams in PETG, and survives 30 minutes of
continuous wear without fatigue.

**What we did.** Iterated the frame nine times across roughly fifteen
months of intermittent CAD time. The first three iterations were
exploratory — establishing the helmet shell's parametric basis, the
hardpoint coordinate system, and the headband fit envelope. Iterations
four through six refined the rear-helm compartment for compute and
battery clearance. Iterations seven and eight tuned the temple-boom
geometry to clear the wearer's ears and glasses. Iteration nine —
`v2_type-b_iter9.3mf` — froze the design and is the current Mk0.0
canonical artifact. Print parameters: PETG, 0.20 mm layer height,
30% gyroid infill, no supports, approximately 14 hours total print time
across the four shell pieces.

**What we measured.** Fit checked against three head sizes (54, 57, and
60 cm circumference) with insertable padding for size adjustment.
Weight: 412 g bare frame, 587 g with the current Mk0 strap-and-pad set.
Continuous-wear comfort: at least 30 minutes for the developer head;
not yet broader sample.

**What we changed.** Each iteration generated a one-line lesson logged
in the 3D-Models directory's commit history. The lessons that
mattered most: (a) the rearhelm compartment needs at least 18 mm
clearance under the shell for a Raspberry Pi 5 plus heatsink, not the
12 mm an early measurement assumed; (b) the temple boom needs a
3-degree outward cant to clear common glasses-frame profiles; (c) the
headband needs an adjustable strap rather than a fixed-size insert,
because the head-size distribution we want to fit is wider than the
single-size tolerance budget; (d) the chin-strap hardpoint is load-
bearing and needs to anchor into the shell rather than the strap fabric,
which iterations 1–4 had reversed.

The Mk0.0 milestone — G1 only, no sensing, no stim — is closed by
this entry.

---

## Entry 2 — Bifilar near-field enhancement, first-principles derivation (2026-05-17)

**What we were trying to do.** Honestly characterize the on-axis
near-field enhancement of the bifilar series-opposing coil the project
proposes to use as the Mk1 stim payload. The wiki describes the
geometry; the literature on Tesla bifilar coils mixes engineering
results with claim-marketing in ways that make it impossible to take
any single source at face value. We needed our own derivation.

**What we did.** Modeled two circular coplanar loops of radius $a$,
separated by axial spacing $d$, carrying equal and oppositely-directed
currents $I$. Computed the axial $B_z$ field from the standard
single-loop Biot–Savart result, then formed the enhancement factor

$$
\eta_B(r) = \frac{|B_{\text{bifilar}}(r)| - |B_{\text{single}}(r)|}{|B_{\text{single}}(r)|}
$$

at on-axis distance $r$. Solved analytically; numerical sanity-check
against a 1024-element discretized Biot–Savart sum agrees to better
than 0.1% across the relevant radius range.

**What we found.** $\eta_B(r) = 3 d r / (a^2 + r^2)$ to leading order
in $d/a$. The maximum is $\eta_B^{\max} = 3d / (2a)$ at $r = a$. For
the proposed Mk1 coil geometry ($a = 15$ mm, $d = 1.5$ mm), this is a
**15% on-axis enhancement at the optimal radius**, not the order-of-
magnitude factor some informal sources advertise. The honest answer is
that the bifilar's value lies in its **gradient structure and far-field
cancellation**, not in on-axis amplitude. The figure in Chapter 5 plots
this; the regenerator notebook is at
[`notebooks/bifilar_near_field.py`](https://github.com/Jthora/HelmKit/blob/master/notebooks/bifilar_near_field.py).

**What we changed.** Reframed the bifilar's role in the Mk1 design from
"on-axis field-amplitude advantage" to "gradient-structure and
far-field-cancellation advantage at modest amplitude." Updated the
falsification list ([`docs/falsification.md`](https://github.com/Jthora/HelmKit/blob/master/docs/falsification.md))
to mark the bifilar payload as engaging $F_3$ (resonance enhancement)
and $F_4$ (SAR-independence) at the precursor level — not at the full
$F_3$ / $F_4$ engagement level, which is Mk2 work. The derivation
itself is the first installment of the project's Chapter-5 line and is
checked in at
[`docs/derivations/bifilar_near_field_enhancement.md`](https://github.com/Jthora/HelmKit/blob/master/docs/derivations/bifilar_near_field_enhancement.md).

---

## Entry 3 — Sensor Wave 1 (Mk0.5 in flight, 2026-05-16 onwards)

**What we are trying to do.** Land the Mk0.5 milestone: the Mk0 frame
plus the L0+L1+L2 biofeedback floor, with all sensors operating and
logging, in a Tranquil-mode wear-test on the developer head.

**What we are doing.** Soldering a Heltec ESP32-S3 development board to
a MAX30102 photoplethysmography sensor on a temple-boom carrier board.
Writing the firmware to read PPG at 100 Hz, run a Pan–Tompkins-style
R-peak detector on the inter-beat interval stream, compute
root-mean-square-of-successive-differences (RMSSD) over rolling
60-second windows, drive an audible / visual breath pacer at the
wearer's resonance frequency (around 0.1 Hz), and log everything as
NDJSON to a microSD card. Logging schema matches the Psi Stabilizer
project's `a01_capture` pipeline for forward compatibility.

**What we are measuring.** PPG signal-to-noise at the temple position
under three conditions: still seated, walking, and heads-down at a
keyboard. RMSSD trend over a single 25-minute wear session, before and
after a guided breath protocol. Subjective Likert panel — calm,
energy, clarity — pre- and post-session.

**What we expect to change.** Whatever the data forces. As of the
late-update to this volume, the firmware-side R-peak detector has
landed in master: streaming Pan–Tompkins variant on PPG IR with
adaptive SPKI/NPKI threshold, 250 ms refractory, RR sanity gate
250–2000 ms; emitted on the NDJSON wire as channel `ppg-rr` with
the same `{t, ch, v, q, boot}` shape the rest of the schema uses;
verified algorithmically against a pure-Python port in
`firmware/mk0.5/scripts/rr_replay.py` (60 s synthetic, 100 % beat
detection, RMS RR jitter under 75 ms — the residual jitter is the MWI
integration window asserting itself and matches firmware). Operator
turns the stream on with the `g` command and off with `x`; the
boot smoke test still gates startup unchanged. What has **not**
happened yet at print time is the on-wrist 5-minute resting vs
paced-breathing RMSSD comparison — that is a hardware session,
not a software session, and is the open G2 row in the falsification
matrix. If the temple-position PPG signal-to-noise is unworkable
under motion, the L2 container will gate Combat mode behind an
"HRV unavailable" flag rather than degrade silently. If the
resonance-breath pacer fails to drive subjective calm in the
developer's own within-subject ABAB block, the Mk0.5 → Mk1.0 gate
has not been crossed and the project says so on record.

---

## What is intentionally not here yet

Entries that are upstream of measurement at the time of this
volume's printing — Mk1.0 bifilar drive-stage bring-up, Mk1.0 first
G3 sham-controlled run, Mk1.5 Combat-mode wear-test in motion, Mk2.0
EEG channel integration — are not written as speculative entries.
They will appear in subsequent volumes after they have actually
happened. The project's discipline is that this chapter contains only
work that has produced a result we can show.

The longest chapter of subsequent volumes is expected to be this one.
That is the design intent.
