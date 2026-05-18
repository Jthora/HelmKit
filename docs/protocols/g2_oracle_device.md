# G2 — Oracle Device (reference HRV truth source)

- **Status**: `v0.1` (Track I commit 6 of 6; addendum 2026-05-18 supersedes §TL;DR / §3 with on-board AD8232)
- **Used by**: [`g2_hrv_validation.md`](g2_hrv_validation.md)
- **Question this doc answers**: which device do we use as the
  reference RR stream against which the Mk0.5 `ppg-rr` channel is
  validated?

---

## TL;DR (2026-05-18 update)

**Use the on-board AD8232 ECG front-end** (in inventory per
[`docs/inventory.md §3.7`](../inventory.md), arriving ~June 1 2026)
with 3M Red Dot wet-gel electrodes via TENS lead wires (both in
inventory). The same Mk0.5 firmware emits `ppg-rr` and `ecg-rr` to
the same NDJSON file with the same timebase — the comparison is
in-board, zero clock-skew, no Bluetooth, no phone app, no CSV column
drift.

**Polar H10 + Polar Sensor Logger** remains the documented fallback
for (a) sessions where the AD8232 path is unavailable (broken unit,
firmware regression on the ECG driver) or (b) off-bench / mobile-wearer
scenarios where a chest strap is the only practical sensor. See
[§3](#3-fallback-polar-h10--polar-sensor-logger) below.

The rest of this doc (selection criteria §1, options matrix §2) is
preserved for posterity — it documents *why* the original H10 choice
was correct given the procurement state at the time, and *why* the
AD8232 supersedes it now that it is on hand.

---

## 1. Selection criteria

The oracle must:

1. Be widely-trusted in the HRV literature (so the 20 % gate in
   [g2_hrv_validation.md](g2_hrv_validation.md) §6 has a defensible
   anchor).
2. Emit **per-beat RR intervals**, not just heart-rate averages. A
   device that only reports HR-per-second loses the variability
   signal entirely.
3. Export RR intervals to a flat file (CSV / TSV / NDJSON) without
   a proprietary cloud-account hop.
4. Be affordable on the project budget (≤ $100).
5. Have a clear documented capture path that does not require
   building a custom SDK app on day one.

---

## 2. Options considered

| Device | RR export | Cost | Why considered | Why selected / rejected |
|--------|-----------|------|----------------|--------------------------|
| **Polar H10** (chest strap) | Yes, via Polar BLE GATT or Polar Sensor Logger CSV | $80 | Gold standard in HRV literature (Schaffer & Ginsberg 2017, Gilgen-Ammann 2019, dozens of follow-ups). Sub-ms RR resolution. | **SELECTED.** |
| **Wahoo TICKR / TICKR Fit** | Yes, via BLE HR-Service or HRV Logger iOS | $50–80 | Cheaper, also research-validated. | **BACKUP (iOS path).** Acceptable but with slightly more app friction. |
| **Garmin HRM-Dual** | Yes, BLE+ANT+. RR via Garmin Connect IQ apps. | $70 | Wide compatibility. | **REJECTED.** Per-beat RR export path requires either a Garmin watch as intermediary or a Connect IQ side-app; too many moving parts. |
| **Phone-camera PPG** (e.g. HRV4Training app) | Yes, but… | $0 | Already in the operator's pocket. | **REJECTED.** Same physics class as the DUT — using it as oracle creates a tautology. We need a *different* sensor modality to validate against. |
| **Consumer wrist HR** (Apple Watch, Fitbit) | Mostly no — most expose only HR-per-second, not per-beat RR; raw access requires Apple Health export that is heavily smoothed | $200+ | Already present in many operators' lives. | **REJECTED.** Per-beat data is gated behind device-specific SDKs that smooth or interpolate before export. Not honest oracle data. |
| **Single-lead ECG patch** (e.g. BITalino, AD8232 dev board) | Yes, raw waveform | $50–150 | Closest to "ground truth". | **REJECTED FOR NOW.** Right physics, but requires custom R-peak detection on the oracle side, which means we'd be debugging two detectors simultaneously. Park for Mk1.x revalidation. **→ 2026-05-18 reversal:** procured (1× AD8232 in inventory, arriving ~June 1). The "two detectors" objection dissolves because the same firmware Pan-Tompkins detector already shipped in Wave J for `ppg-rr` is reused on the ECG channel for `ecg-rr` — it is **one** detector applied to two inputs, not two. Selected as canonical oracle per the 2026-05-18 TL;DR. |

---

## 3. Fallback: Polar H10 + Polar Sensor Logger

### 3.1 What you buy

- **Polar H10** chest strap. ~$80 direct from Polar or Amazon.
  - Confirm the elastic strap is included; some bundles ship the
    transmitter only.
  - Replaceable CR2025 battery (lasts ~400 h logged use).
  - BLE + 5 kHz analog. We use BLE.

### 3.2 What you install

- **Polar Sensor Logger** by `j-pekka_kaivosoja` on the Google Play
  Store. Free, no account required, exports `.csv` to local storage.
  - Tested with versions 2.x. If a future version breaks the column
    order, the [G2 protocol §8 row "Oracle CSV column drift"](g2_hrv_validation.md)
    covers the remediation.

### 3.3 Capture flow

1. Wet the H10 electrode strip (saliva or tap water).
2. Don the strap, transmitter centred mid-sternum.
3. Open Polar Sensor Logger → "ECG + HR + RR" → "Start logging".
4. Verify both **HR** and **RR** rows are populating (~1 Hz HR,
   per-beat RR).
5. Run the [G2 5/5/5 protocol](g2_hrv_validation.md).
6. Stop logging. The app writes
   `polar-sensor-logger/<UTC>_<MAC>.csv` to local storage.
7. Transfer the CSV via USB (the laptop is already plugged in via
   the DUT) into `captures/<session_id>/oracle.csv`.

### 3.4 CSV schema (as of Polar Sensor Logger v2.x)

```
Phone timestamp;sensor timestamp [ns];Heart rate [bpm];RR-interval [ms]
2026-06-22T14:43:12.000;...;62;968
2026-06-22T14:43:13.020;...;61;984
...
```

Only the `Phone timestamp` and `RR-interval [ms]` columns are used by
the analysis. The semicolon delimiter is preserved as-is.

---

## 4. Backup: Wahoo TICKR + HRV Logger iOS

If Android isn't available:

- **Wahoo TICKR** (the regular TICKR, not TICKR X — the X has its
  own quirks). ~$50.
- **HRV Logger** by Marco Altini on the App Store. ~$5. Exports CSV
  to Files / iCloud Drive.
- Capture flow is conceptually identical; column names differ
  slightly (`R-R Interval (ms)` instead of `RR-interval [ms]`).

The analysis script's column map handles both via a `--oracle-format`
flag; default is `polar-sensor-logger`.

---

## 5. What about a "second oracle" for redundancy?

Tempting, but **no**. A second oracle (e.g. a finger pulse-ox running
alongside H10) just shifts the agreement-validation question one
level down and creates a tri-way comparison nobody has the budget to
analyse properly. The H10 has 20+ years of literature behind it as a
research-grade RR source; that's our anchor. If H10-vs-Mk0.5 fails,
the bug is in the Mk0.5 stack, not the oracle.

The exception: if a G2 session unexpectedly **passes** but downstream
Mk1.x results are noise-dominated, then we revisit the oracle and
add an ECG-patch comparison. That's a known unknown, tracked here
rather than addressed pre-emptively.

---

## 6. Storage and provenance

Per session, the oracle CSV is committed alongside the DUT NDJSON
into `captures/<session_id>/oracle.csv` (see
[g2_hrv_validation.md §3](g2_hrv_validation.md)). `meta.yaml` records
the oracle device serial number and the strap battery percentage
at session start.

If the H10 transmitter is ever replaced (e.g. lost or returned), the
new serial number gets a new row in this doc with a one-line note
about when the swap happened. That gives downstream readers a way to
spot oracle-induced drift in long-running comparisons.

---

## 7. Decision log

- **2026-05-18**: Polar H10 selected over alternatives (this doc, v0).
  Phone-PPG and consumer-wrist devices explicitly rejected on
  modality / smoothing grounds. ECG-patch deferred to Mk1.x.
