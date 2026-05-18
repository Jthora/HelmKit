# G2 — HRV Validation Protocol (Mk0.5)

- **Status**: `v0` (Track I commit 3 of 6)
- **Gate**: G2 of the Mk0.5 / Mk1.x gating triple (`G1✓ / G2✓ / G3-null = honest success`).
- **What G2 validates**: that the `ppg-rr` stream emitted by Mk0.5
  firmware reflects real cardiac inter-beat intervals to within an
  agreed accuracy band when compared against an oracle device, *and*
  that the device responds to a known HRV perturbation (paced
  breathing at 6 br/min) the same way the oracle does.

This is **not** a clinical validation. It is a self-consistency check
that lets every downstream HRV-conditioned claim rest on a measured,
not assumed, sensor.

---

## 1. Equipment

- **DUT**: Mk0.5 device per [`mk0.5_bom.md`](../firmware/mk0.5_bom.md),
  flashed with the firmware at the commit being validated.
- **Oracle**: per [`g2_oracle_device.md`](g2_oracle_device.md). Default
  is Polar H10 chest strap + Polar Sensor Logger Android app.
- **Capture host**: a laptop running [`tools/capture_ndjson.py`](../../tools/capture_ndjson.py),
  Python ≥ 3.10, pyserial installed.
- **Environment**: quiet room, stable ambient temperature 18–24 °C,
  diffuse light (no direct sun or pulsing artificial light on the
  sensor site).
- **Operator**: seated upright in a chair with back support and feet
  flat on the floor. **One operator at a time.**
- **Timer**: phone stopwatch is fine; the paced-breathing app of choice
  for the operator (e.g. "Paced Breathing" Android app at 6 br/min
  with a 5 s inhale / 5 s exhale) is the breath pacer.

---

## 2. Protocol (the 5/5/5)

| Segment | Duration | Activity | Notes |
|---------|----------|----------|-------|
| Setup | ~5 min | Don the chest strap, mount the Mk0.5 PPG per [`ppg_mounting_notes.md`](../mechanical/ppg_mounting_notes.md), start both captures, log into meta. | Capture must be running **before** the operator settles, so the start-of-baseline timestamp is well-defined. |
| Baseline | 5 min | Seated quiet rest. Eyes open or closed, no phone, no talking. Normal spontaneous breathing — **do not** consciously slow or deepen it. | Establishes the operator's resting RR distribution. |
| Paced | 5 min | Paced breathing at **6 br/min** (5 s in, 5 s out). | Known HRV-amplifying manoeuvre; RMSSD should rise materially. |
| Recovery | 5 min | Seated quiet rest, normal breathing. | Returns to baseline; lets you see whether the paced effect washes out. |
| Wrap | ~2 min | Stop both captures, record operator subjective rating (see §4). | |

**Total**: 17 minutes door-to-door including setup and wrap.

Do not interleave segments. Do not pause and resume mid-segment.
If anything goes wrong (sensor falls off, operator coughs through a
paced cycle, phone buzzes), abort and restart the entire session.

---

## 3. Data layout

One session = one directory under `captures/`:

```
captures/
└── 20260622T144312Z_g2_op-jt/
    ├── dut.ndjson              # full Mk0.5 NDJSON stream (all channels)
    ├── oracle.csv              # Polar Sensor Logger RR export
    ├── meta.yaml               # session metadata (see below)
    └── notes.md                # free-form operator notes (optional)
```

Timestamp is UTC, ISO 8601 basic. Operator suffix lets multiple ops
share a workstation.

`meta.yaml` schema (minimal):

```yaml
session_id: 20260622T144312Z_g2_op-jt
operator: jt
firmware_commit: <git sha of firmware/mk0.5 at time of capture>
dut_serial: heltec-v3-001
oracle_device: polar-h10
oracle_serial: <strap serial>
ambient_temp_c: 21.5
room_light: diffuse-overhead-led
caffeine_last_4h: false
alcohol_last_24h: false
sleep_h_last_24h: 7.5
operator_mood: 3            # 1=poor, 5=excellent (subjective)
notes: |-
  First-of-day session; cold start.
```

The session_id matches the directory name byte-for-byte. The
firmware_commit field is the integrity link: if you ever want to know
"what firmware emitted this data?", you read this field. Do not
re-flash mid-session.

---

## 4. Operator subjective rating (blinded)

Before opening any data file or computing any metric, the operator
records a **subjective** rating of how the session felt:

- **Mood (1–5)**: how the operator generally feels.
- **Coupling (1–5)**: how confident the operator is that the PPG had
  good skin contact throughout.
- **Pacing (1–5)**: how well the operator stayed on the 6 br/min cue
  during the paced segment.
- **One-line free text**.

This goes into `notes.md`. It exists to catch "the data looks great
but the operator knows the sensor was sliding around" cases before
the numbers bias the report.

---

## 5. Analysis (specification only)

The actual analysis script ships in a later track (`tools/analyze_g2.py`
is **not** part of Track I). This section specifies what that script
will compute so the protocol is self-contained.

Per session, compute on each of {baseline, paced, recovery}:

- `mean_rr_ms` (arithmetic mean of in-range RR values)
- `rmssd_ms` = $\sqrt{\frac{1}{N-1}\sum_{i=1}^{N-1} (RR_{i+1} - RR_i)^2}$
- `pnn50_pct` (fraction of successive RR differences > 50 ms)
- `n_beats` (count of in-range beats)
- `n_out_of_range` (count of beats marked `q="out-of-range"`)

Both streams (DUT and oracle) get the same metrics. Then per segment:

- $\Delta_{\mathrm{RMSSD}} = |\mathrm{RMSSD}_{\mathrm{DUT}} - \mathrm{RMSSD}_{\mathrm{oracle}}|$
- relative error $= \Delta_{\mathrm{RMSSD}} / \mathrm{RMSSD}_{\mathrm{oracle}}$

## 6. Pass criteria

A session **passes G2** when **all three** of these hold:

1. **Baseline agreement**: relative RMSSD error ≤ **20 %**.
2. **Paced response**: oracle RMSSD rises by ≥ **1.5×** between
   baseline and paced (sanity-check that the manoeuvre worked at all);
   DUT RMSSD rises by ≥ **1.3×** between the same two segments
   (DUT correctly tracks the response).
3. **Paced agreement**: relative RMSSD error ≤ **20 %** in the paced
   segment too.

Recovery is reported but not gated — bodies are noisy on the way
back down.

**One session pass is not enough.** G2 closes when **three independent
sessions** on three different days, each pass all three criteria,
with the same firmware commit.

The 20 % band is wider than most commercial HRV claims because:

- Polar H10's own published accuracy spec vs. Holter ECG is ≈5 % on
  RMSSD in controlled lab conditions; ≈10 % is realistic in the
  field.
- The MAX30102 finger-PPG has fundamentally different physics
  (pulse-wave arrival vs. R-peak) and a non-negligible per-beat
  bias is expected; **what matters for HRV is consistency, not
  absolute timing**.
- 20 % is conservative enough that algorithmic bugs (off-by-one
  refractory, MWI window drift) will reliably fail the gate, but
  tight enough that the device is honestly useful for Mk1.x
  HRV-conditioned stim decisions.

If the 20 % band turns out to be too generous in practice — i.e. the
device passes G2 but downstream Mk1.x results are noise-dominated —
the band tightens in a later revision of this doc, not silently.

---

## 7. Pre-flight checklist

Before pressing "start capture":

- [ ] Operator is not actively caffeinated (no caffeine in last 4 h)
      or, if so, it is recorded in `meta.yaml`.
- [ ] DUT firmware commit SHA is captured into `meta.yaml`.
- [ ] Oracle device is charged > 50 %.
- [ ] DUT is on USB power (no battery-low surprise mid-session).
- [ ] Both captures are confirmed running (line count > 0 within
      first 10 s) before the baseline segment starts.
- [ ] Phone is on do-not-disturb.
- [ ] Operator has used the bathroom (no fidgeting).

---

## 8. Failure modes and remediation

| Failure mode | Symptom | Remediation |
|--------------|---------|-------------|
| Motion artifact | DUT shows spurious peaks; `q="out-of-range"` count is high | Re-mount per `ppg_mounting_notes.md` §"motion isolation". Forearm rest fully supported. |
| Ambient light leak | DUT baseline IR is unstable, drifts upward when room brightens | Apply opaque tape shroud around the MAX30102 site. |
| Sensor pressure too low | DUT IR amplitude is low (< 5 k counts on the pulse envelope) | Increase pressure — firm but not blanching. |
| Sensor pressure too high | DUT IR amplitude collapses; `q="gap"` increases | Decrease pressure; if a rubber band is used, slacken one wrap. |
| Operator nasal/laboured breathing | Paced segment doesn't pull RMSSD up on the oracle | Abort; re-run when the operator is well. Not a device failure — the manoeuvre simply didn't engage. |
| USB cable power-only | DUT never appears as a serial device | Replace with a known-good data-capable USB-C cable. |
| Oracle CSV column drift | Polar Sensor Logger update changed column order | Open the CSV, verify the `RR-interval [ms]` column is column 2; if not, fix the analysis script's column map. **Do not** re-run the session — the data is still good. |

---

## 9. Reporting

Every G2 session produces a one-page report in
`captures/<session_id>/report.md` (template lives in
`tools/analyze_g2.py` once it ships). The report includes:

- The three pass-criteria results, each with its numeric value and
  pass/fail flag.
- The three per-segment metric tables (DUT and oracle, side by side).
- A single RR-overlay plot per segment.
- The operator subjective rating block, verbatim.
- The firmware commit SHA.

Reports are committed to the repo under
`docs/field-notes/volume-1/g2_sessions/` so the device's validation
history is part of the project record, not stuck on a laptop.

---

## 10. What this protocol does **not** establish

- That the device is medical-grade. It is not.
- That the device measures heart rate variability "as well as" a
  consumer HRV app. The bar is different (and stricter on
  reproducibility).
- That the operator's HRV is interpretable as a state metric. That is
  a Mk1.x downstream concern; G2 only validates the channel.
- That MAX30102 finger-PPG is the long-term sensor topology. It is
  the **bench** topology; on-product geometry is a later mechanical
  problem.
