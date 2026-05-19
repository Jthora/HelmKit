# Track J — Mk0.5 Sensor Bring-up Sprint

- **Status**: `scoped`
- **Wiki-blocked?**: no
- **Depends on**: Track I (landed: `0a7da22` chain) — BOM + wiring + G2 protocol + capture tool + oracle decision.
- **Depends on**: operator bench verification of [`docs/inventory.md §11`](../../inventory.md) open items (Heltec V3 vs V2; Diitao breakout pull-up state + supply rail; GSR connector geometry).
- **Unblocks**: Mk0.5 physical bench session; G2 closure; Tier 1 DIY Build Kit honest demo path.

---

## 1. Goal

Bring up every sensor on the Mk0.5 bench surface, end-to-end, in the
Mk0.5 firmware, with every channel landing in the canonical NDJSON
stream and at least one comparison or sanity-check per channel.

Ship the analysis script that consumes capture sessions and computes
the G2 pass/fail gate. **Close G2** with three independent passing
sessions on three different days against the on-board AD8232 oracle.

This is the bridge from the paper artifacts Track I shipped (BOM,
wiring, protocol, capture tool, oracle decision) to a real working
bench.

---

## 2. Scope

In scope:

- Drivers for every sensor in [`inventory.md §3.7`](../../inventory.md):
  Diitao MAX30102 (already running via firmware Wave J), MLX90614,
  GSR, MAX30205, AD8232.
- New NDJSON channels per [`firmware/mk0.5/docs/SCHEMA.md`](../../../firmware/mk0.5/docs/SCHEMA.md)
  §2.2 (all reserved 2026-05-18, only `ecg-rr` newly added):
  `temp-forehead` + `temp-forehead.amb` (MLX90614), `gsr` (GSR
  module), `temp-skin.L` + `temp-skin.R` (MAX30205 ×2), `ecg`
  (AD8232), `ecg-rr` (Pan-Tompkins reuse).
- One Pan-Tompkins reuse from Wave J for `ecg-rr` (same detector,
  ECG-band coefficients).- `tools/analyze_g2.py` per [`g2_hrv_validation.md §5`](../../protocols/g2_hrv_validation.md):
  consumes a capture session + oracle, emits the three pass-gate
  metrics, writes a session report.
- Three G2 sessions on three different days → close G2.

Out of scope (defer to a later track):

- Optimised mechanical mount beyond the bench primer in
  [`mk0.5_wiring.md`](../../firmware/mk0.5_wiring.md) and
  [`ppg_mounting_notes.md`](../../mechanical/ppg_mounting_notes.md).
- TENS output / electrical stim — electrodes are inventoried for
  ECG/GSR sensing only at this stage. Stim is a Mk1.x problem.
- Calibration of MLX90614 against a NIST-traceable reference (the
  MAX30205 paired cross-check is good enough for the Mk0.5 safety
  floor).
- Wireless transport. NDJSON over USB-CDC remains the canonical
  capture path through Track J.

---

## 3. Pre-conditions

All three operator-side bench checks resolved 2026-05-18 (see
[`inventory.md §11`](../../inventory.md)). Recorded here for the audit
trail.

| # | Check | Status | Resolution |
|---|-------|--------|------------|
| 1 | Heltec board revision: silkscreen reads `HTIT-WB32LAF` (V3, ESP32-S3) — *not* V2 (ESP32). | ✅ resolved 2026-05-18 | Silkscreen confirmed `HTIT-WB32LAF`. Firmware target stands; no port. |
| 2 | Diitao MAX30102: on-board pull-up state (SMT marking `472`/`103` near SDA/SCL) and VIN rail. | ✅ resolved 2026-05-18 | SMT marking `472` confirmed → 4.7 kΩ pull-ups present. Do not add externals. VIN held at 3V3 by [`mk0.5_wiring.md §3.1`](../../firmware/mk0.5_wiring.md) policy (safe on any clone). |
| 3 | GSR module connector geometry (3.5mm TRS / Dupont / JST). | ✅ resolved 2026-05-18 | 3.5mm TRS confirmed. Tip + Ring carry the two finger electrodes; Sleeve = ground/shield. Lead-routing pattern to the Red Dot electrodes is therefore standard 2-conductor + shield. |

**Bridge A is unblocked.** Bridges B and C remain gated on hardware
arrivals (MAX30205 ~May 27, AD8232 ~Jun 1–15) per §4.

---

## 4. Bridge sequencing

Three bridges, each defensible on its own. Each bridge can be paused
or skipped if a sensor doesn't behave; downstream bridges are
serialised on AD8232 arrival but not on each other.

### Bridge A — PPG-only bring-up (this week, May 18–24)

Pre-conditions §3 #1 and #2 resolved 2026-05-18. Bridge A is a go.

- Wire one Diitao MAX30102 per [`mk0.5_wiring.md`](../../firmware/mk0.5_wiring.md)
  §1–§4 (5-wire pin table; VIN to 3V3 rail only; no external pull-ups
  needed — the in-hand units carry `472` = 4.7 kΩ on-board).
- Flash current `master` (firmware Wave J already emits `ppg` and
  `ppg-rr`). No firmware changes required.
- Run a 60-second capture via `tools/capture_ndjson.py` against the
  bench DUT. Confirm `ppg` and `ppg-rr` lines land in NDJSON.
- Run an opportunistic 5/5/5 session per [`g2_hrv_validation.md`](../../protocols/g2_hrv_validation.md)
  **without an oracle** — store the capture, defer pass/fail computation
  until Bridge C lands the oracle.
- Record any bench surprises in
  [`docs/field-notes/volume-1/08_field_notes.md`](../../field-notes/volume-1/08_field_notes.md).

Output: real PPG NDJSON from real silicon. Operator confidence that
the bench fixture, capture tool, and Pan-Tompkins detector all
survive contact with the physical world.

### Bridge B — Thermal + electrodermal (week of May 25, gated on MAX30205 arrival ~May 27)

- MLX90614 driver: I²C `0x5A` read, emit `{"ch":"temp-forehead","v":<°C>}`
  and `{"ch":"temp-forehead.amb","v":<°C>}` at 4 Hz on the existing
  NDJSON stream (per [`SCHEMA.md`](../../../firmware/mk0.5/docs/SCHEMA.md)
  §2.2).
- GSR driver: ADC read on `kGsrAdc=4`, light low-pass, emit
  `{"ch":"gsr","v":<raw>}` at 50 Hz (matches SCHEMA §2.2 sample rate).
  Calibration to µS happens downstream per `data_schemas.md` §6.
- MAX30205 driver: I²C `0x48` and `0x49`, emit
  `{"ch":"temp-skin.L","v":<°C>}` and `{"ch":"temp-skin.R","v":<°C>}`
  at 5 Hz.
- Cross-validation: MLX90614 vs MAX30205 in still air on a paired
  bench fixture must agree within ≤ 0.5 °C. If they don't, the
  MLX90614 emissivity assumption (default 0.95) is wrong for the
  target surface and gets noted, not corrected here.
- No SCHEMA.md bump required — all channels are pre-reserved in §2.2.

Output: full thermal + electrodermal NDJSON surface. Five new
emitting channels (`temp-forehead`, `temp-forehead.amb`, `gsr`,
`temp-skin.L`, `temp-skin.R`) in the wire format.

### Bridge C — ECG + G2 closure (week of June 1+, gated on AD8232 arrival ~June 1–15)

- AD8232 driver: ADC read on `kAd8232Out=5`, `LO+`/`LO−` lead-off
  watch on GPIO 6/7. Emit `{"ch":"ecg","v":<raw>}` at 250 Hz (the
  AD8232 is bandlimited well below half that).
- Reuse Wave J Pan-Tompkins (`firmware/mk0.5/src/dsp/r_peak.{h,cpp}`)
  with ECG-band coefficients (5–15 Hz bandpass, 150 ms MWI window —
  the classical values, the PPG-band shift is the special case).
  Emit `{"ch":"ecg-rr","v":<ms>}` per detected R-peak.
- Ship `tools/analyze_g2.py` per
  [`g2_hrv_validation.md §5`](../../protocols/g2_hrv_validation.md):
  consumes a capture session, computes baseline / paced / recovery
  RMSSD for both `ppg-rr` and `ecg-rr`, emits the three pass-gate
  metrics + a one-page report.
- Run three G2 sessions on three different days against the on-board
  AD8232 oracle. Each must pass all three gates with the same firmware
  commit. **G2 closes** on the third pass.

Output: G2 closed; honest demo path open for Tier 1 DIY Build Kit;
unblocks every downstream Mk0.5 → Mk1.x physiological-state work.

---

## 5. Planned commits

Approximate, in order. Each is its own commit; small enough to
land independently.

| # | Commit | Bridge | Status / Gated on |
|---|--------|--------|-------------------|
| 1 | `schema(mk0.5): add ecg-rr; align Track J to canonical channel names` | A pre-flight | ✅ landed |
| 2 | `firmware(mk0.5): MLX90614 driver + temp-forehead/temp-forehead.amb NDJSON` | B | ✅ landed `25e7a9a` (2026-05-18) |
| 3 | `firmware(mk0.5): GSR driver + gsr NDJSON channel` | B | ✅ landed `1aaf4f0` (2026-05-18) |
| 4 | `firmware(mk0.5): MAX30205 driver + temp-skin.L/R NDJSON + MLX cross-check` | B | MAX30205 arrival (~May 27) |
| 5 | `firmware(mk0.5): AD8232 driver + ecg NDJSON channel + lead-off watch` | C | AD8232 arrival (~June 1) |
| 6 | `dsp(mk0.5): Pan-Tompkins reuse on ECG band + ecg-rr emit` | C | commit 5 |
| 7 | `tools(g2): analyze_g2.py — RMSSD pass/fail per g2_hrv_validation.md §5` | C | commit 6 |
| 8 | `Track J (closure): G2 passes 3/3 sessions; Track J lands` | C | commits 1–7 + three passing sessions |

Final commit count may shift ±1 once Bridge B sensors are on the
bench and the GSR module's actual data behaviour is known.

---

## 6. Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Heltec is V2, not V3 (pre-condition §3 #1 fails) | low | Halt Track J, re-scope to V2 port or new-board order. Inventory has it as "Heltec LoRa 32" with revision unverified. |
| Diitao MAX30102 4-pack ships with no pull-ups and we don't notice → I²C bus flaky | low | [`mk0.5_wiring.md §3.1`](../../firmware/mk0.5_wiring.md) makes the inspection a written step. Spare 4.7k from inventory resolves in 30 s. |
| AD8232 arrival slips past June 15 | medium | Bridges A and B do not depend on it. G2 closure slips, but the rest of Track J completes. Polar H10 fallback is still documented in [`g2_oracle_device.md §3`](../../protocols/g2_oracle_device.md) for the impatient case. |
| GSR signal is dominated by motion artefact at the wrist | high (known biology) | Track J emits raw + simple-filtered `gsr`. Sophisticated artefact rejection is a Mk1.x problem and explicitly out of scope here. |
| G2 sessions fail the 20 % RMSSD gate | medium | [`g2_hrv_validation.md §8`](../../protocols/g2_hrv_validation.md) already has a failure-mode remediation table. First failure ≠ Track J failure. |

---

## 7. What "Track J lands" means

- Five new NDJSON channel emitters live on `master` against the
  canonical names in [`SCHEMA.md`](../../../firmware/mk0.5/docs/SCHEMA.md)
  §2.2: `temp-forehead` (+ `.amb`), `gsr`, `temp-skin.L`/`temp-skin.R`,
  `ecg`, `ecg-rr`.
- `tools/analyze_g2.py` shipped.
- Three G2 sessions on three different days passing the [`g2_hrv_validation.md`](../../protocols/g2_hrv_validation.md)
  gate with the same firmware commit.
- This doc updated: `status: scoped` → `landed`, "What shipped"
  section populated with all commit SHAs.
- Plan [`README.md`](README.md) row J ticked to `landed`.

---

## What shipped

(empty — Track J is `scoped`, not yet underway)
