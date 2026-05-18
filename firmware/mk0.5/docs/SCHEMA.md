# Mk0.5 NDJSON Schema

**Authority.** This document is **subordinate** to
[`external/psiStabilizer/docs/data_schemas.md`](../../../external/psiStabilizer/docs/data_schemas.md).
That file is the *single source of truth* for channel names, units, sample
rates, file layout, and quality semantics. This file describes only:
1. What Mk0.5 firmware emits today (subset of psiStabilizer v0.1).
2. What HelmKit Mk1.x will require psiStabilizer to add (proposed v0.2).
3. How the ESP32 (no wall-clock) bridges to the Pi log-sink's wall-clock `t`.

If this file disagrees with `data_schemas.md`, `data_schemas.md` wins.

**Schema version emitted by Mk0.5 firmware:** `v0.1` (compatible subset).
**Schema version required by Mk1.5:** `v0.2` (proposed extension below).

---

## 1. Line format

One JSON object per line, NDJSON. Conforms to psiStabilizer §3.

```
{"t":1714512000.123,"ch":"ppg-hrv","v":12345,"q":"ok"}
```

| Field | Type    | Required | Meaning |
|-------|---------|----------|---------|
| `t`   | number  | ✅       | Unix seconds, float. **See §3 for ESP32-bridging rule.** |
| `ch`  | string  | ✅       | Channel name. See §2. |
| `v`   | number  | ✅       | Raw value (calibration happens downstream per `data_schemas.md` §6). |
| `q`   | string  | ⚠️ optional | `ok` / `gap` / `noise` / `out-of-range`. Default `ok` if omitted. Mk0.5 ALWAYS emits explicitly to make analysis logic uniform. |

**No other fields.** No `unit`, no `sensor_id`, no `rev`. Those live in `meta.yaml`.

---

## 2. Channel registry

### 2.1 v0.1-compatible (psiStabilizer-ratified, emit today)

| Channel    | Source           | Rate    | Raw unit             | Notes |
|------------|------------------|---------|----------------------|-------|
| `ppg-hrv`  | MAX30102 IR ADC  | 100 Hz  | uint32 ADC counts    | Mk0.5 emits IR only; Red is reserved for SpO2-derivative (out of v0.1). Quality: `gap` when `finger_present==false`. |

### 2.2 v0.2-proposed (HelmKit Mk0.5 adds; awaits psiStabilizer §1 append)

| Channel             | Source            | Rate    | Raw unit         | Notes |
|---------------------|-------------------|---------|------------------|-------|
| `ppg-rr`            | Mk0.5 R-peak DSP  | event   | uint16 ms        | Per-beat RR interval derived from `ppg-hrv` via Pan-Tompkins-on-PPG (firmware Wave J, `src/dsp/r_peak.cpp`). `v` = interval in ms to previous accepted peak; `v=0` for the first peak in a stream. Quality `ok` when 250 ≤ v ≤ 2000; `out-of-range` otherwise. Carries a non-standard `conf` field = peak_amp / adaptive_threshold (≥ 1.0). |
| `gsr`               | CJMCU-6701 ADC    | 50 Hz   | uint16 ADC (0..4095) | Calibrated to µS in analysis. Quality: `out-of-range` if rail-pinned. |
| `temp-forehead`     | MLX90614 obj      | 4 Hz    | float32 °C       | Ambient (`temp-forehead.amb`) emitted at same cadence for environmental cross-ref. |
| `temp-forehead.amb` | MLX90614 ambient  | 4 Hz    | float32 °C       | |
| `ecg`               | AD8232 out        | 250 Hz  | uint16 ADC       | Wave 2. Quality: `gap` when LO+ or LO- asserted (leads-off). |
| `temp-skin.L`       | MAX30205 @ 0x48   | 5 Hz    | float32 °C       | Left temple. Wave 2. ±0.1°C accuracy. |
| `temp-skin.R`       | MAX30205 @ 0x49   | 5 Hz    | float32 °C       | Right temple. Wave 2. PRIOR_ART §3.11 M5 differential channel. |
| `vbat`              | ESP32 ADC1_CH0    | 1 Hz    | uint16 ADC       | Health channel, not physiology. Useful for session-quality flagging. |
| `cue`               | Mk0.5 L0 state    | event   | string           | Values: `inhale`, `exhale`, `hold`, `session-start`, `session-end`. Matches psiStabilizer §3 cue-state event style. |

When psiStabilizer ratifies v0.2 these names migrate from this file's §2.2
into `data_schemas.md` §1 unchanged. Firmware does not change.

### 2.3 Reserved channel namespaces (do NOT use without coordination)

- `eeg-*` — reserved for OpenBCI / Mk2.0 (psiStabilizer A02).
- `ambient-*` — reserved for environmental sensors (psiStabilizer A01).
- `mag-*` — reserved for $F^2$ probe magnetometer channels.

---

## 3. ESP32 time bridging

The ESP32 has no battery-backed RTC; `millis()` rolls from 0 on each boot.
psiStabilizer's `t` requires Unix seconds. Resolution:

1. **On the wire from ESP32 → Pi:** firmware emits `t` as `millis()/1000.0`,
   i.e. seconds-since-boot. This is a number; format is valid.
2. **At ingest on Pi:** the log-sink rewrites `t` to wall-clock by adding
   the session boot-time offset. The boot-time offset is captured by:
   - Pi sends a `time-sync` byte immediately after USB-CDC enumerates; ESP32
     replies with current `millis()`. Pi records `(unix_time_at_sync,
     esp_millis_at_sync)` into `meta.yaml`.
   - Ingest then computes `t_wallclock = unix_time_at_sync + (t_emitted - esp_millis_at_sync/1000.0)`.
3. **`meta.yaml` captures the offset** so re-analysis is deterministic.

This means the on-SD-card or stdout NDJSON from Mk0.5 *is not directly
loadable* by psiStabilizer's analysis pipeline. The Pi log-sink is the
ingestion adapter. This is acceptable because Mk0.5 is single-MCU and the
Pi is the canonical log-sink per BLACKOUT_PLAN §3 Decision #3.

When/if Mk1.5 gains a DS3231 RTC (currently not budgeted), this bridge layer
becomes trivial — firmware emits true Unix `t` and the ingestion adapter
becomes a passthrough.

---

## 4. Quality flag emission rules

Mk0.5 firmware emits `q` explicitly on every sample. Decision tree per sensor:

| Sensor      | Emit `q` |
|-------------|----------|
| MAX30102    | `ok` if `ir > finger_ir_threshold`; `gap` otherwise. |
| `ppg-rr`    | `ok` if `250 <= rr_ms <= 2000` or `rr_ms == 0` (first peak); `out-of-range` otherwise. Refractory-suppressed peaks (<250 ms gap to previous accepted) are not emitted at all. |
| GSR         | `ok` if `100 < raw < 4000`; `out-of-range` at rails; `gap` if no electrodes (not yet detectable in hardware — placeholder TODO). |
| MLX90614    | `ok` if `15 < obj_c < 45`; `out-of-range` otherwise. |
| AD8232      | `gap` if `LO+` OR `LO-` asserted; `ok` otherwise. (Wave 2.) |
| MAX30205    | `ok` if `30 < temp_c < 42`; `out-of-range` otherwise. (Wave 2.) |
| VBAT        | `ok` always; downstream consumers ignore `vbat` for physiology gating. |

`noise` is reserved for analysis-time annotation; Mk0.5 firmware does not
detect noise online.

---

## 5. Forward-compatibility rules

1. **Never rename a channel** that has emitted real data. Add a new channel,
   migrate, deprecate.
2. **Never change a channel's raw unit** without a major schema bump.
3. **Adding a field to a line object** (e.g. `seq`) requires consumer-side
   handling first. Mk0.5 firmware will add `seq` (monotonic per-channel
   sample counter) at the v0.2 bump for drop-detection.
4. **The Pi log-sink is allowed to enrich**: e.g. inject a `t_wallclock`
   field at ingest, rename it back to `t` in the parquet rollup. The
   firmware-emitted file is the immutable record.

---

## 6. Worked examples

### MAX30102 normal sample
```
{"t":12.345,"ch":"ppg-hrv","v":78912,"q":"ok"}
```

### MAX30102 finger removed mid-stream
```
{"t":15.000,"ch":"ppg-hrv","v":1023,"q":"gap"}
```

### Session start event (L0 cue channel, v0.2)
```
{"t":0.500,"ch":"cue","v":"session-start","q":"ok"}
{"t":0.500,"ch":"cue","v":"inhale","q":"ok"}
```

### GSR baseline + startle spike (v0.2)
```
{"t":30.020,"ch":"gsr","v":1845,"q":"ok"}
{"t":30.040,"ch":"gsr","v":1848,"q":"ok"}
{"t":30.060,"ch":"gsr","v":2310,"q":"ok"}
```

### AD8232 leads-off (v0.2, Wave 2)
```
{"t":12.000,"ch":"ecg","v":0,"q":"gap"}
```

### PPG-derived RR interval (v0.2, Wave J)
```
{"t":12.872,"ch":"ppg-rr","v":872,"q":"ok","conf":2.31,"boot":"a3f2c91e0bd4abcd"}
{"t":13.756,"ch":"ppg-rr","v":884,"q":"ok","conf":2.18,"boot":"a3f2c91e0bd4abcd"}
{"t":15.900,"ch":"ppg-rr","v":2144,"q":"out-of-range","conf":1.42,"boot":"a3f2c91e0bd4abcd"}
```
First peak after stream-start emits with `v=0` and `q=ok` to anchor the
series. `conf` is a non-standard extension (additionalProperties
permissive); analysis can ignore it.

---

## 7. Cross-references

- Authority: [`external/psiStabilizer/docs/data_schemas.md`](../../../external/psiStabilizer/docs/data_schemas.md) v0.1
- Bringup gates: [`docs/mk0.5_firmware_bringup.md`](../../../docs/mk0.5_firmware_bringup.md)
- Mk ladder: [`docs/mk_ladder.md`](../../../docs/mk_ladder.md)
- Blackout window discipline: [`docs/BLACKOUT_PLAN.md`](../../../docs/BLACKOUT_PLAN.md) §3 Decision #3 (Pi = log-sink)
- Defensive IP: [`PRIOR_ART.md`](../../../PRIOR_ART.md) §3.8 (data architecture), §4 combination claim 6
