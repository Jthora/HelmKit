# Track E — Firmware Wave J (MAX30102 + R-peak + RR NDJSON)

- **Status**: `dsp-landed; pending on-target validation`
- **Wave naming note**: this track was originally drafted under the
  name "Wave M1" with a parallel `firmware/wave-m1/` source tree, but
  the actual Mk0.5 firmware bring-up converged on `firmware/mk0.5/`
  with a `Wave J` (J = pumped channel J, sensor data) integration
  inside that tree. This doc is the rewrite that reflects what
  actually landed.
- **Depends on**:
  - Mk0.5 driver layer (Wave I): `firmware/mk0.5/src/drivers/max30102.{h,cpp}` (sample callback, smoke gate).
  - NDJSON sample/event surface: `firmware/mk0.5/src/log/ndjson.{h,cpp}` and `firmware/mk0.5/docs/SCHEMA.md` v0.1.
  - L0 paced-breathing pacer (commit `2872333`), still co-resident.
- **Unblocks**:
  - Honest Tier 1 DIY demo (device measures something real and emits it).
  - HRV-conditioned modes in Mk0.5 (downstream from RR stream).
  - The G2 on-wrist validation gate.

---

## Goal

Add a **continuous PPG sensing → R-peak detection → RR-interval
NDJSON emission** path to the Mk0.5 firmware. After this lands, the
device measures heart-rate variability and emits it on the same
NDJSON wire surface as every other channel, in a format the
downstream `psiStabilizer` ingest pipeline can already consume.

This is Wave J of the Mk0.5 firmware bring-up ladder
([docs/mk0.5_firmware_bringup.md](../../mk0.5_firmware_bringup.md)
§3).

## Hardware target

- **Board**: Heltec WiFi LoRa 32 V3 (ESP32-S3-based; canonical Mk0.5 host).
- **Sensor**: MAX30102 PPG breakout, I²C, 3v3, on the external bus
  (`Wire1` @ GPIO `kExtI2cSda` / `kExtI2cScl`).
- **Existing wiring**: identical to the Wave I sensor-smoke target;
  no new pins or connectors.

## Functional spec — what landed

The 4-commit chain `895d5bf → b664de2 → 332e9a0 → <this commit>`
implements the following:

### 1. Streaming R-peak detector (commit `895d5bf`)

`firmware/mk0.5/src/dsp/r_peak.{h,cpp}` — Pan-Tompkins variant
adapted to PPG (not ECG). Operates entirely streaming at the 100 Hz
sample rate: no buffering, no offline pass, one-sample latency.

Pipeline:

1. 50-sample SMA high-pass detrend (cutoff ~0.5 Hz; kills DC + respiratory drift).
2. 3-tap causal derivative `y[n] = x[n] − x[n−2]`.
3. Point-wise square.
4. 150 ms (15-sample) moving-window integration.
5. SPKI/NPKI adaptive threshold:
   - SPKI: `0.125 * peak_amp + 0.875 * SPKI` on each peak.
   - NPKI: `0.01 * mwi + 0.99 * NPKI` every sample.
   - threshold = `NPKI + 0.25 * (SPKI − NPKI)`.
6. 250 ms refractory window (refractory-survivors are dropped, **not**
   emitted as out-of-range).
7. RR sanity gate 250–2000 ms — out-of-range RR values are emitted
   with `q="out-of-range"` (not dropped) so downstream can audit.

### 2. `ppg-rr` NDJSON channel (commit `b664de2`)

`firmware/mk0.5/src/log/ndjson.{h,cpp}` — new emitter
`emit_ppg_rr(t_ms, rr_ms, in_range, confidence)`. Wire shape
matches the psiStabilizer v0.1 sample format:

```
{"t":12.872,"ch":"ppg-rr","v":872,"q":"ok",
 "conf":2.31,"boot":"a3f2c91e0bd4abcd"}
```

Important property: `t` is the **peak timestamp**, not the emit
timestamp. The wire stream is therefore **replay-deterministic** —
a recorded `ppg-hrv` sample stream replayed through the detector
yields identical `ppg-rr` lines. The Python reference (below)
relies on this invariant.

`docs/SCHEMA.md` was updated:

- §2.2 channel registry: `ppg-rr` row (event-rate, uint16 ms, Wave J).
- §4 quality emission rules: `ppg-rr` row.
- §6 worked examples: 3-line example covering the first-peak anchor
  (`v=0`), normal beat, and out-of-range beat.

Schema version is unchanged (`ppg-rr` slots into the existing
v0.2-proposed channel set).

### 3. `main.cpp` streaming integration (commit `332e9a0`)

New commands on the serial REPL:

- **`g`** — begin PPG streaming. Configures the sensor at 100 Hz /
  `sample_avg=4`, resets the detector, sets `g_streaming=true`.
  Refused after a safety halt; operator must `R` first (same
  discipline as `p`).
- **`x`** — stop streaming; calls `Max30102::shutdown()` (sensor
  drops to ~0.7 µA idle).

In `loop()`, while streaming: `g_ppg.pump()` then drain
`g_rpeak` via `emit_ppg_rr` (FIFO is 8 deep; at 100 Hz with a 10 ms
loop period the typical drain is 0–1 peaks per tick).

The boot smoke test is unchanged and still gates startup.

### 4. Python reference + plan rewrite (this commit)

`firmware/mk0.5/scripts/rr_replay.py` — pure-stdlib Python port of
the detector with identical constants and state-machine ordering.
Two modes:

- `--self-test`: synthesises 60 s @ 100 Hz of PPG-like signal at
  60 bpm and asserts:
  - detection rate ≥ 95 % (1 peak per beat),
  - mean RR within 2 % of 1000 ms,
  - RMS RR error ≤ 75 ms,
  - first-peak `v=0` anchor present.
  The 75 ms RMS gate is deliberately generous: the MWI argmax
  wanders inside the 150 ms integration window, so per-beat RR
  jitter of ~5–7 samples on a clean synthetic signal is inherent to
  the algorithm and **matches firmware behaviour**. On-target HRV
  validation will compare summary statistics (RMSSD), not per-beat RR.
- `--replay <file|->`: reads recorded `ppg-hrv` NDJSON sample lines
  and emits the corresponding `ppg-rr` lines. Lets you diff a
  captured firmware `ppg-rr` stream against a fresh Python run on
  the same input — i.e. verifies firmware/Python algorithmic
  equivalence post-hoc.

## What this track does NOT include

- **On-target HRV validation (G2)** — there is no Mk0.5 in this
  session to wear. The 5-minute resting vs paced-breathing RMSSD
  comparison is deferred to a hardware session. The track is
  `dsp-landed; pending on-target validation` until that runs.
- **No PlatformIO native-env unit tests on the firmware side.** The
  Python reference covers the algorithmic-equivalence question; a
  proper firmware test harness is a separate (lower-priority) cleanup.
- **No BLE / SD-card transport.** USB-CDC NDJSON only.
- **No HRV-derived modes (RMSSD/SDNN/pNN50 inside firmware).** The
  device emits RR; analysis is downstream in `psiStabilizer` ingest.

## Acceptance criteria

### G1 (algorithmic — DONE)

1. ✅ `rr_replay.py --self-test` passes locally (see commit
   `<this commit>` log).
2. ✅ Firmware compiles under the existing `firmware/mk0.5/platformio.ini`
   (no new toolchain deps).
3. ✅ Every emitted `ppg-rr` line validates as a JSON sample-line per
   SCHEMA §2.2 + §4.

### G2 (on-wrist — DEFERRED)

4. ⏳ With sensor on a fingertip / wrist, ≥ 95 % of beats over 60 s
   yield a valid `ch:"ppg-rr"` line.
5. ⏳ Resting 5-min RMSSD < paced-breathing 5-min RMSSD on the same
   wearer, same session, sham-blinded order. This is the F-row in
   [docs/falsification.md](../../falsification.md) for the HRV
   sensing layer.
6. ⏳ False-positive rate at rest: < 1 phantom RR / minute.

When G2 runs, the resulting captures + analysis go into
`firmware/mk0.5/validation/<date>_resting_vs_paced/` and the
falsification doc gets updated.

## File deliverables (actual)

- `firmware/mk0.5/src/dsp/r_peak.{h,cpp}` (detector)
- `firmware/mk0.5/src/log/ndjson.{h,cpp}` (+ `emit_ppg_rr`)
- `firmware/mk0.5/src/main.cpp` (streaming wiring + `g`/`x` commands)
- `firmware/mk0.5/docs/SCHEMA.md` (`ppg-rr` channel registered)
- `firmware/mk0.5/scripts/rr_replay.py` (Python reference + self-test)
- This plan doc, rewritten to match.

## What ships

Track E ships as the 4-commit chain in master:

| # | SHA       | Commit |
|---|-----------|--------|
| 1 | `895d5bf` | `dsp(mk0.5): streaming Pan-Tompkins R-peak detector for PPG IR` |
| 2 | `b664de2` | `ndjson(mk0.5): add ppg-rr channel emitter + SCHEMA v0.2 entry` |
| 3 | `332e9a0` | `main(mk0.5): wire PPG streaming + R-peak emit (Wave J integration)` |
| 4 | this      | `tools(mk0.5): Python rr_replay reference + Track E plan rewrite` |

The G2 on-wrist validation pass is a separate, hardware-session
work-item tracked under this same track once it runs.
