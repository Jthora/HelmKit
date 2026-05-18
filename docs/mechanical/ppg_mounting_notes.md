# PPG Mounting — Bench Notes

- **Status**: `v0` (Track I commit 5 of 6)
- **Used by**: [`g2_hrv_validation.md`](../protocols/g2_hrv_validation.md) §8
- **Scope**: How to physically couple the MAX30102 to skin during a
  bench session so the data is worth analysing. **Not** an enclosure
  spec — that's a later mechanical track.

---

## 1. What "good coupling" means

A good PPG signal has four mechanical preconditions:

1. **Firm, non-blanching contact.** The sensor face needs to be
   pressed against skin firmly enough that the LED→photodiode optical
   path stays stable across the cardiac cycle. Too loose: ambient
   light leaks in and the pulse rides on a moving DC. Too tight:
   capillary flow is occluded and the pulse amplitude collapses.
   - Sanity check: skin under the sensor stays its normal colour. If
     it goes white, you're occluding — slacken.
2. **Ambient-light isolation.** The MAX30102 photodiode picks up
   *any* near-IR light, not only the LED it owns. A finger sticking
   out from under the sensor in direct sun will produce a 0.1–1 Hz
   "respiratory" wave that is actually room light bouncing off the
   chest. Opaque shroud the sensor + finger.
3. **Motion isolation.** The capillary bed near the sensor responds
   to micro-movements (hand twitches, talking, swallowing). For the
   five-minute G2 segments, the forearm sits *fully supported* on a
   table or chair arm; the operator does not gesture.
4. **Thermal stability.** Vasoconstriction from cold hands halves the
   pulse amplitude. Wait until hands feel warm to the touch before
   starting the baseline segment. In winter, a 2-min warm-water rinse
   before donning the sensor is allowed (and noted in `meta.yaml`).

---

## 2. Finger vs. wrist (bench vs. product)

| Site | Bench? | Product? | Notes |
|------|--------|----------|-------|
| Index or middle finger pad | ✅ default | ❌ | Fat capillary bed, easy to mount, strong waveform, robust against minor motion. Use this for G2. |
| Earlobe | ✅ alternative | ❌ | Used in clinical pulse-ox; cleaner waveform than finger in some operators. Awkward to mount on a breadboard sensor. |
| Wrist (volar / underside) | ⏳ later | ✅ | The Mk-line geometry will eventually live on the wrist or temple. Wrist PPG is materially noisier — finger first, wrist after G2 closes. |
| Forehead / temple | ⏳ Mk1 | ✅ | The actual product geometry. Out of scope for Mk0.5 bench validation. |
| Fingernail bed | ❌ | ❌ | High motion sensitivity, low optical transmission. Don't. |

For G2 bench validation, **use the index finger pad of the
non-dominant hand**. Standardising the site across sessions removes
one variable.

---

## 3. Bench mount recipe (the cheap one that works)

You need:

- The MAX30102 breakout on its breadboard (per
  [`mk0.5_wiring.md`](../firmware/mk0.5_wiring.md)).
- A 1 cm strip of opaque black electrical tape.
- A wide rubber band (e.g. a #64).
- A small foam pad (a folded piece of bubble wrap is fine).

Steps:

1. Free the MAX30102 breakout from the breadboard so it can move with
   the finger (keep the wires plugged; just unplug the breakout from
   the rails or extend with longer F-F jumpers).
2. Place the foam pad under the breakout's PCB so the sensor's optical
   window protrudes ~1 mm above the surrounding components.
3. Drape the finger pad over the sensor window. The pulp of the
   distal phalanx is the target; the joint sits *behind* the sensor.
4. Cap the assembly with the rubber band, looping around the breakout
   and finger 2–3 times. Snug but not tight (see §1 step 1).
5. Drape the tape across the seam between finger and breakout edges
   to block ambient light.

A pre-built finger clip (e.g. the standard pulse-ox cradle that takes
a MAX30102 module) is fine if available — same mechanical principles.

---

## 4. What a good waveform looks like

After the firmware streams `ppg-hrv` at 100 Hz, the IR channel should
show:

- A clear **per-beat oscillation** at the operator's heart rate.
- Each beat has a sharp ascending edge (~80 ms) and a slower
  descending edge with a **dicrotic notch** about 2/3 of the way
  down — a small inflection caused by the aortic valve closing. The
  notch may be faint but should be present on most beats.
- DC level stable to within a few percent over 10 s. Drifting DC = motion or pressure problem.
- Peak-to-trough amplitude on the order of **5,000–30,000 ADC
  counts** (raw `v` in the `ppg-hrv` stream). Below 5 k counts: re-mount.

If the waveform is a clean sinusoid with **no** dicrotic notch and an
amplitude > 50 k counts, you're probably looking at the LED itself
reflecting off the photodiode through ambient-light leakage. Re-shroud.

---

## 5. Anti-patterns

- **Floating sensor on the bench**, finger hovered above it: catches
  every ceiling light flicker. Always cap with shroud.
- **Sensor under the fingernail**: the nail is birefringent and
  motion-sensitive. Use the pulp.
- **Sensor in palm**: too deep, capillary bed is wrong geometry,
  signal is faint.
- **Operator chats during baseline**: throat motion couples into the
  whole-body cardiovascular state. Silence the baseline.
- **Tightening to make the signal "bigger"**: amplitude going up
  while DC goes down is occlusion, not better coupling. The actual
  pulse you're seeing is the pressure your own rubber band is
  applying.
- **Multiple operators in one session**: do not swap finger between
  segments. Same finger, same site, same mount, full 17 minutes.

---

## 6. When the bench mount stops being enough

The bench recipe above is for G2 sessions and for early Mk0.5 dev.
Once Mk1.x stim work begins, the device will need to be worn for
the duration of a session in something more like the eventual product
form. That mechanical work is **not** Track I — it lives downstream
in the post-bench mechanical track once G2 has retired the sensor
question.

If you find yourself wanting to "improve" the bench mount with custom
3D-printed parts before G2 has passed three times, stop and run a
G2 session instead. Mount optimisation is a feedback loop on data,
not on guesses.
