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
| `ecg`               | AD8232 out        | 250 Hz  | uint16 ADC       | Wave 2 / Track J Bridge C. Quality: `gap` when LO+ or LO- asserted (leads-off). |
| `ecg-rr`            | Mk0.5 R-peak DSP  | event   | uint16 ms        | Per-beat RR interval derived from `ecg` via Pan-Tompkins-on-ECG (Track J Bridge C; same detector as `ppg-rr` with classical 5–15 Hz ECG-band coefficients, `src/dsp/r_peak.cpp`). Wire shape identical to `ppg-rr` (carries non-standard `conf` field). First peak in stream emits with `v=0` and `q=ok`. This is the **canonical G2 oracle channel** per [`g2_oracle_device.md`](../../../docs/protocols/g2_oracle_device.md) v0.1. |
| `temp-skin.L`       | MAX30205 @ 0x48   | 5 Hz    | float32 °C       | Left temple. Wave 2. ±0.1°C accuracy. |
| `temp-skin.R`       | MAX30205 @ 0x49   | 5 Hz    | float32 °C       | Right temple. Wave 2. PRIOR_ART §3.11 M5 differential channel. |
| `vbat`              | ESP32 ADC1_CH0    | 1 Hz    | uint16 ADC       | Health channel, not physiology. Useful for session-quality flagging. |
| `cue`               | Mk0.5 L0 state    | event   | string           | Values: `inhale`, `exhale`, `hold`, `session-start`, `session-end`. Matches psiStabilizer §3 cue-state event style. |

When psiStabilizer ratifies v0.2 these names migrate from this file's §2.2
into `data_schemas.md` §1 unchanged. Firmware does not change.

### 2.3 v0.3-proposed (Track M combat trim; host-side reference in `tools/analyze_combat_session.py`)

Names from `docs/plans/2026-tier1-launch/track-M-combat-trim.md` §3.1. Not emitted by any firmware yet; the analyser accepts them
so captures made by hand-wired sensors can be scored before the firmware exists. Same `{t, ch, v, q}` shape.

| Channel           | Source                              | Rate   | Raw unit        | Notes |
|-------------------|-------------------------------------|--------|-----------------|-------|
| `temp-nose`       | MLX90614 obj aimed at the nose tip  | 4 Hz   | float32 °C      | Sensor bar. Breathing rate (`resp-thermal`) and the arousal slope are derived on the host. `temp-forehead` is accepted as a fallback by the analyser. |
| `eda-forehead`    | GSR module via the forehead fabric patches | 20–50 Hz | uint16 ADC | Replaces the finger straps. `q=noise` when the skin-temperature slope says thermal sweating (host rule, > 0.05 °C/min). |
| `resp-thermal`    | Mk0.5 `dsp/resp_thermal` on the MLX stream | event | float32 breaths/min | One line per detected breath; `v` = rate over the trailing 30 s. Emitted whenever the thermopile stream runs ('t'); the channel is the same whether the thermopile reads the forehead or the nose ('N' toggles `temp-forehead` / `temp-nose`), so only trust it with the nose-tip aim. |
| `still`           | IMU motion energy, thresholded      | 1 Hz   | 0 / 1           | 1 = still. HRV is only computed inside runs of 1 lasting ≥ 60 s. |
| `impact`          | IMU                                 | event  | float32 g (peak)| One line per event ≥ 10 g; direction and the 200 ms window go to `meta.yaml` / a sidecar until v0.3 is ratified. |
| `imu`             | 6-axis IMU                          | 50–100 Hz | packed or per-axis | Layout to be fixed with the IMU purchase (Track M phase 1). |
| `cue` values      | Mk0.5 L0 / host                     | event  | string          | Adds `round-start`, `round-end`, `prime`, `sanctuary`, `tally` (operator keys m M b B i n y) to the v0.2 set (`inhale`, `exhale`, `hold`, `session-start`, `session-end`), and the mode machine's outputs `mode:<name>`, `tally-ack`, `impact:<N>g`, `summary:tally=<N>` (`layers/modes`). |

### 2.4 Track N line kinds and fields (emitted since 2026-09-11)

Robustness plumbing from `docs/plans/2026-tier1-launch/track-N-capability-robustness.md`. The analyser reads all of them;
psiStabilizer ingest ignores unknown fields and `kind` lines.

| Line / field | Shape | Notes |
|---|---|---|
| `n` (every line) | uint32, per boot, starts at 1 | The `seq` promised in §5 rule 3, per line rather than per channel. A line that could not be written (link down, TX ring full) still consumes a number, so a gap in `n` is exactly one lost line. |
| `kind: boot` | `{"t","kind":"boot","reason","reason_num","wdt","mk","git","schema","boot"}` | First line after `hello`. `reason` from `esp_reset_reason()`: `poweron`, `sw`, `panic`, `int-wdt`, `task-wdt`, `wdt`, `brownout`, `deepsleep`, `ext`, `sdio`, `unknown`. `wdt` = 1 when the loop task joined the 5 s task watchdog. |
| `ch: hb` | `{"t","ch":"hb","v":<uptime s>,"q":"ok","drops","drops_ev","link_down","heap","boot"}` | Every 5 s. `drops` is cumulative per boot (all classes), `drops_ev` the event-class subset, `link_down` the subset lost while no host was attached. A gap in `hb` is a link gap, not a sensor gap. |
| `kind: health` | `{"t","kind":"health","source","from","to","attempt","note","boot"}` | One line per driver health transition (gap / ok flapping rate-limited to one per 2 s) and per re-begin attempt; `source` is `ppg-hrv`, `temp`, `gsr` or `i2c1` (bus recovery). |

Drop policy (Track N §2 rule 4): raw sample lines (`gsr`, `temp-*`) are the `raw` class and are shed first; RR intervals,
breaths, cues, health, heartbeat, boot, smoke and error lines are the `event` class. Phase 0 counts both; Phase 2 buffers
the event class to flash while the link is down. Since phase 1 the firmware sheds the raw class itself when more than 20
lines dropped in one heartbeat interval and restores it after 30 s without a drop (`kind:health`, source `link`).

Phase 1 channels (emitted since 2026-09-11; the `still` / `impact` rows of §2.3 are now live):

| Channel | Shape | Notes |
|---|---|---|
| `still` | `{t, ch:"still", v: 0/1, q:"ok"}` at 1 Hz | `dsp/motion.h`: RMS dynamic acceleration over 2 s below 0.05 g. Only while the IMU stream runs (`a`). |
| `impact` | `{t, ch:"impact", v: <peak g>, q:"ok"}` per event | dynamic acceleration ≥ 10 g; peak captured over a 200 ms window that is also the refractory. `t` = the first crossing. |
| `activity` | `{t, ch:"activity", v: <mean g>, q:"ok"}` per 10 s | mean dynamic acceleration: an exertion index. |
| `ppg-q` | `{t, ch:"ppg-q", v: 0..1, q:"ok"/"low"/"gap"}` per 10 s | fraction of in-range beats in the trailing 10 s; `low` below 0.8, `gap` with no beats. The fusion rule's per-window quality. |
| `vbat` | `{t, ch:"vbat", v: <ADC count>, q:"ok", volts, pct}` per 5 s | with the heartbeat. `pct` from a 1S LiPo open-circuit curve. |
| `btn` | `{t, ch:"btn", v:"<name>:<short|long>"}` per press | names `round`, `prime`, `tally`; the slide switch logs `sanctuary:on` / `sanctuary:off`. Every press is logged even when the mode machine ignores it. |
| `cue` values added | `confirm-end`, `low-battery`, `session-resumed`, `check-nose-sensor` | first `M` press; low-battery policy fired; session resumed after an involuntary reset; donning check failed (no three breaths within 30 s of session start). |
| `kind:smoke` source `imu` | as §1 | boot self-test when the IMU stream starts: 50 reads, |a| within 1 g ± 10 %; `ev_a` = mean milli-g. |
| `temp-*` q `gap` | | thermopile fogged: object within 0.3 °C of ambient for 20 s. The breathing extractor ignores fogged samples. |
| `gsr` q `gap` | | electrode lifted: below the open-circuit floor (100) for 1 s. |

Phase 2 (emitted since 2026-09-11):

| Line / field | Shape | Notes |
|---|---|---|
| `hr` | `{t, ch:"hr", v: <bpm>, q:"ok"/"gap"}` per 10 s | the single-source half of the host fusion rule (M-F4): the median of the last five in-range RR intervals, reported only when the trailing 10 s window has ≥ 80 % in-range beats and the estimate is under 15 s old; `v` 0 with `q:"gap"` otherwise. A second RR source (ECG) makes it the two-source rule on the host. |
| `scr` | `{t, ch:"scr", v: <rise, raw units>, q:"ok"}` per event | skin-conductance response from `dsp/eda.h`, the streaming port of the host `scr_times`: tonic = EMA 5 s, a phasic rise of ≥ 0.5 % of the tonic level lasting 0.5..3 s, stamped at the peak. Fed only `q:"ok"` samples. |
| `sweat` | `{t, ch:"sweat", v: 0/1, q:"ok"}` per 10 s | the host sweat rule on the helm: skin temperature (`temp-skin.L`, else `.R`) rising faster than 0.05 °C/min over the trailing 60 s. Only while a MAX30205 streams (`c`). |
| `temp-skin.L` / `.R` | as §2.2, 5 Hz | now emitted (MAX30205 at 0x48 / 0x49 on bus 1); raw class. |
| `hb` fields `buffered`, `buf` | | lines parked in the flash link buffer this boot, and bytes still waiting to replay. |
| `replay` (field) | `"replay":1` on a replayed line | the line was written to flash while the link was down and sent later; `t` and `n` are the originals. The analyser counts it in its place. |
| host ack | the host sends the byte `~` after each `hb` | once one ack has been seen in a boot, 10 s without one marks the link unhealthy: event lines go to the buffer, raw lines drop. A plain serial monitor never acks, so only a physically absent host triggers buffering there. |
| `kind:health` sources `linkbuf`, `oled` | | boot-time availability lines: `off -> ready` / `unavailable` / `absent`. |

### 2.5 Reserved channel namespaces (do NOT use without coordination)

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
| AD8232      | `gap` if `LO+` OR `LO-` asserted; `ok` otherwise. (Wave 2 / Track J Bridge C.) |
| `ecg-rr`    | `ok` if `250 <= rr_ms <= 2000` or `rr_ms == 0` (first peak); `out-of-range` otherwise. Refractory-suppressed peaks (<250 ms gap to previous accepted) are not emitted at all. Identical rule to `ppg-rr`. |
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
   handling first. Landed 2026-09-11 as `n` (§2.4): a monotonic per-boot line
   counter, consumed by `tools/analyze_combat_session.py` for lost-line counts.
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

### ECG-derived RR interval (v0.2, Track J Bridge C — canonical G2 oracle)
```
{"t":12.870,"ch":"ecg-rr","v":870,"q":"ok","conf":4.12,"boot":"a3f2c91e0bd4abcd"}
{"t":13.752,"ch":"ecg-rr","v":882,"q":"ok","conf":4.08,"boot":"a3f2c91e0bd4abcd"}
```
Wire shape is byte-for-byte identical to `ppg-rr` so `analyze_g2.py`
can diff the two streams without per-channel decoding logic. The
higher `conf` reflects ECG's tighter SNR vs PPG.

---

## 7. Cross-references

- Authority: [`external/psiStabilizer/docs/data_schemas.md`](../../../external/psiStabilizer/docs/data_schemas.md) v0.1
- Bringup gates: [`docs/mk0.5_firmware_bringup.md`](../../../docs/mk0.5_firmware_bringup.md)
- Mk ladder: [`docs/mk_ladder.md`](../../../docs/mk_ladder.md)
- Blackout window discipline: [`docs/BLACKOUT_PLAN.md`](../../../docs/BLACKOUT_PLAN.md) §3 Decision #3 (Pi = log-sink)
- Defensive IP: [`PRIOR_ART.md`](../../../PRIOR_ART.md) §3.8 (data architecture), §4 combination claim 6
