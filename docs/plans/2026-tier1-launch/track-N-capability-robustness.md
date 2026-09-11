# Track N — Capability robustness (firmware + host software)

**Status:** `phase-2-built` (2026-09-11: phases 0, 1 and 2 landed in firmware and tools; 24 native + 226 host tests; target builds at 12 % flash; bench gates, the IMU / switch wiring and the first real capture pending). Nothing in this track needs money except the IMU already planned under Track M.
**Owner:** firmware/mk0.5 + tools/. **Builds on:** [track-M-combat-trim.md](track-M-combat-trim.md) §7 (M-F1..M-F6), [track-E](track-E-firmware-wave-m1.md), [track-J](track-J-sensor-bring-up.md), [track-K](track-K-bench-readiness.md).

## 1. Purpose

Track M defines what the helm senses and cues. This track makes each of those capabilities survive the conditions the helm is for: a sweating, moving wearer taking hits; a belt-pack link that gets yanked; a battery that runs down mid-round; an operator in gloves who presses the wrong button; a sensor that drops off the I²C bus. It also makes every failure reproducible on the bench, because a capability whose failure cannot be reproduced cannot be called robust.

The state on 2026-09-11 (audit in the session log): the ESP32-S3 target builds (7 % RAM, 9 % flash), 8 native tests pass, 211 host tests pass. Real drivers exist for the MAX30102, MLX90614, GSR module and battery; the AD8232, MAX30205 and OLED are header-only stubs; there is no IMU; the operator interface is serial keys; logging is NDJSON over USB with no sequence numbers and no buffering; CI builds the legacy Nano sketch, not the Mk0.5 target; the firmware README still describes the May sprint's day-one scaffold.

## 2. What "robust" means here

A capability is robust when all five hold:

1. **It keeps working** under motion, sweat, impacts, heat, gloves and a flaky link, within stated limits.
2. **When it cannot, it fails loud and safe.** The channel's quality flag says so on every affected line, the status LED and OLED say so, and the log records why (health line with a reason code).
3. **It recovers without a power cycle.** Sticky faults are retried with backoff; a reattached sensor rejoins within 10 s.
4. **It degrades in a known order.** Raw streams are dropped before derived events; derived events are dropped before cues; cues are never emitted in a mode that forbids them.
5. **Its failure is reproducible on the bench** by a fixture, a replay or a checklist step, and covered by a test that CI runs.

Two existing patterns are kept: **host reference first, firmware second** (the Python implementation is the behavioural spec and the equivalence oracle, as `rr_replay.py` is for `r_peak.cpp`), and **no stim below Mk1** (`safety/no_stim_below_mk1.h` stays; the coil driver gets a second, separate interlock, N-F8).

## 3. Capability matrix

| Capability | Today | What breaks it in use | Robust target | Gate |
|---|---|---|---|---|
| Heart rate (forehead PPG) | driver + R-peak DSP, quality flags per SCHEMA §4 | motion artefact, sweat under the carrier, pressure change on impact, FIFO stall, I²C stall | per-window quality score, boot self-test (LED current, DC level, ambient), FIFO watchdog, second source (BCG from the IMU, ECG when wired), fusion rule ported from the host | N-G6, M-G2 |
| Breathing (nose thermopile) | driver + `resp_thermal` DSP, `temp-nose` switch | ambient drift, lens fog from sweat, aim wander of the bar, breathing through the mouth | ambient compensation from `.amb`, fog detector (object ≈ ambient for 20 s → `gap`), donning check (three breaths seen within 30 s or a cue asks for them), per-breath confidence | N-G6, M-G3 |
| EDA (forehead patches) | GSR driver at 50 Hz, host-side SCR + sweat rule | electrode lift, saturated tonic level in heavy sweat, ADC conflict with VBAT | open-circuit detection → `gap`, saturation → `out-of-range`, firmware port of the sweat rule (needs a skin-temperature source), ADC mutex regression test kept | N-G1, N-G6 |
| Stillness / impact / activity (IMU) | none (`still` = unknown, no `impact`) | clipping on hard hits, mounting orientation, bus load at 100 Hz | LSM6DS3-class over I²C bus 1, `still` at 1 Hz, `impact` ≥ 10 g with 200 ms refractory, activity index, boot self-test (1 g ± 10 % at rest), clip counter | M-G4 |
| Temple / occipital temperature (MAX30205) | header stub | address clash on bus 1, slow response | driver at 5 Hz, both addresses, feeds the sweat rule and heat load | N-G1 |
| Cueing (pacer) | LED + serial cue lines, driven by modes | wrong mode emits a cue, cue lost when the link is down | every cue line carries the mode that produced it; Combat-sustain silence is a native test; bone conduction and the brow LED lane at Mk1 | N-G6 |
| Modes (state machine) | native-tested, millis wrap tested | reset mid-session, operator double-press | session resumes after a reset in Tranquil with the same session id and a `boot` line; end-session needs a long press | N-G2, N-G3 |
| Operator input | serial keys only | gloves, sweat, accidental end, no feedback | three tact buttons + slide switch on the nape pod, debounced, long-press to end, every press logged as a `btn` event and acknowledged by a cue; serial keys stay as the bench path | N-G5 |
| Status display | OLED stub, status LED | operator cannot see which channel is bad | OLED status page (mode, HR, breaths, per-channel quality, battery, link, drop count) and a fault page; LED patterns unchanged | N-G1, N-G5 |
| Logging and link | NDJSON over USB, no sequence numbers, no buffering | cable yank, host asleep, TX buffer overrun, time bridging after reset | `n` sequence field, `drops` health line, heartbeat line every 5 s, derived channels buffered to LittleFS while the link is down and replayed with their original `t`, raw streams dropped first | N-G2 |
| Time | `millis` with host bridging (SCHEMA §3), boot id per boot | reset mid-session, host clock jump | `boot` line with reset reason on every boot; the analyser stitches boots by session id; monotonic `t` per boot enforced | N-G2, N-G3 |
| Power | battery driver, no brownout handling | LiPo sag under load, brownout reset loop, session lost | brownout detector enabled and logged, low-battery threshold ends the session cleanly (summary line, cue), charging state reported | N-G3 |
| Bus health | sticky `kNoAck` until `begin()` | stuck SDA, connector bump, one dead sensor taking the bus | 9-clock bus recovery, per-device re-begin with backoff (5 s, 10 s, 20 s, then every 60 s), health line on every transition | N-G4 |
| Host capture | `tools/capture_ndjson.py`, firmware `capture_ndjson.sh` (needs psistab-ingest) | port renumbering, disconnect, disk full, unlabeled sessions | a capture service (laptop or belt-pack Pi): auto-reconnect, one file per session id, schema validation, disk check, heartbeat gap accounting | N-G2 |
| Host analysis | `analyze_combat_session.py`, 22 tests on a synthetic session | malformed lines, duplicate or out-of-order `t`, several boots in one file, missing channels | never crashes on a capture; reports each unavailable capability and why; `--strict` for CI; golden real captures as fixtures once M-G2 runs | N-G6, N-G7 |
| Test and CI | native Unity (8), unittest (211), CI builds the Nano sketch only | regressions land unnoticed; Python and firmware drift apart | CI runs the Mk0.5 build, the native tests, the host tests and the replay-equivalence check on every push | N-G7 |

## 4. Work items

IDs: N-F firmware core, N-S sensing, N-U operator and display, N-L link and logging, N-H host, N-T test and CI, N-D docs. Each item names the failure it prevents and how it is verified. Hours are working estimates.

### Firmware core (N-F)

- **N-F1 Sequence numbers and drop accounting** (2 h). Every NDJSON line gets `n` (uint32 per boot). When the Serial TX buffer cannot take a line, raw-stream lines are dropped and counted; a `drops` health line reports the count every 5 s while non-zero. Prevents: silent gaps that look like sensor gaps. Verify: N-G2; unit test on the writer with a mocked full buffer.
- **N-F2 Boot line and reset reason** (1 h). On boot emit `boot` with `esp_reset_reason()`, firmware SHA, schema version, boot id, and the previous session id if one was persisted. Prevents: unattributable restarts. Verify: N-G3 (brownout) and N-G2.
- **N-F3 Brownout and low-battery policy** (3 h). Enable the brownout detector at the default level, log it via N-F2. Below the low-battery threshold (from the battery driver, hysteresis 0.1 V, 10 s debounce) the mode machine ends the session (summary line, `cue: low-battery`), the pacer stops, streams stop, the OLED shows the fault page. Prevents: a session that dies without a summary. Verify: N-G3.
- **N-F4 I²C bus recovery and retry with backoff** (4 h). Bus-stuck detection (SDA low with SCL released) → 9-clock recovery, then re-init. `kNoAck`, `kOverflow` and `kError` stop being sticky-until-`begin()`: each device is retried on a backoff schedule (5, 10, 20, then 60 s) and every transition emits a health line. Prevents: one bumped connector killing a session. Verify: N-G4.
- **N-F5 Session persistence across a reset** (3 h). Session id, mode and tally are written to LittleFS on every mode change; a boot within 5 min of the last write resumes the session in Tranquil and emits `cue: session-resumed`. Prevents: a brownout costing the session's identity and tally. Verify: N-G3.
- **N-F6 Task watchdog** (1 h). The main loop feeds the task watchdog; a stall over 3 s resets and is attributed by N-F2. Prevents: a hung I²C transaction freezing the helm silently. Verify: fault injection (a debug key that spins) shows a `boot` line with the watchdog reason.
- **N-F7 Degradation order** (2 h). One place (`layers/degrade`) decides what is shed under load or low battery: raw PPG first, then raw EDA, then temperatures, never derived events or cues. Prevents: ad hoc dropping in three drivers. Verify: unit test on the policy table.
- **N-F8 Coil-driver interlock** (1 h, when a driver exists). Any coil-driver source fails to compile unless `HELMKIT_COIL_GATE_PASSED` names the gate record (the bench field map and replication check from the derivation doc). Separate from `no_stim_below_mk1.h`. Prevents: current near a head before the gates.

### Sensing (N-S)

- **N-S1 PPG self-test and window quality** (4 h). At boot and on demand: LED current in range, DC level in the mid-band, ambient below threshold; result on the `smoke` line. At runtime a 10 s window quality (fraction of in-range beats, DC stability) is emitted as `ppg-q` at 0.1 Hz and used by the fusion rule. Verify: N-G6 against the host reference.
- **N-S2 Thermopile fog and aim** (3 h). Object within 0.3 °C of ambient for 20 s → `gap` on `temp-nose`; at session start the pacer asks for three breaths and the DSP confirms a 0.2 °C swing, else `cue: check-nose-sensor`. Verify: bench with a breath on the lens; M-G3.
- **N-S3 EDA contact and saturation** (2 h). ADC at the rail for 1 s → `out-of-range`; below the open-circuit floor for 1 s → `gap`; 20 Hz sampling; the ADC mutex regression test stays in CI. Verify: lift one patch on the bench.
- **N-S4 IMU driver, `still`, `impact`, activity** (8 h, ~$5 IMU). This is M-F1. Bus 1 at 100 Hz, `still` at 1 Hz from a 2 s motion-energy window, `impact` peak-g events with a 200 ms refractory, activity index per 10 s, clip counter, boot self-test (gravity 1 g ± 10 %, orientation recorded). Unlocks real RMSSD gating and Combat impact cues. Verify: M-G4; native tests on synthetic traces.
- **N-S5 MAX30205 driver** (3 h). Both addresses, 5 Hz, feeds the sweat rule (N-S6) and a heat-load line. Verify: bench against a thermometer.
- **N-S6 Firmware port of the EDA sweat rule and HR fusion** (6 h). Port M-F3 and M-F4 from the host reference with the same constants; native tests on the same synthetic session the host tests use. Verify: N-G6 equivalence.

### Operator and display (N-U)

- **N-U1 Buttons** (4 h, switches from the planned purchase). Three tact switches and the slide switch on the nape pod, debounced in firmware (20 ms), mapped: short press = round start/stop, prime, tally; long press (1.5 s) = session start/end; slide = sanctuary/off. Every press emits `btn` with the mapping and gets a cue acknowledgement. The serial keys remain for the bench. Pins: two of GPIO 45/46 plus GPIO 39 (thermopile alarm, unused) and one more from the reserved LoRa set, recorded in PINOUT (N-D2). Verify: N-G5.
- **N-U2 OLED status and fault pages** (4 h). Mode, HR with source, breaths, per-channel quality as one glyph each, battery, link (up/down/buffering), drop count; a fault page on any sticky health state, brownout or low battery. Verify: N-G1, N-G5.
- **N-U3 Session-end guard** (1 h). Ending a session requires a long press or a second key within 3 s; the first press emits `cue: confirm-end`. Verify: N-G5.

### Link and logging (N-L)

- **N-L1 Heartbeat line** (1 h). `hb` every 5 s with uptime, drop count, buffer fill and battery. Lets the host tell a link gap from a sensor gap. Verify: N-G2.
- **N-L2 Derived-channel buffer on LittleFS** (6 h). While the host has not acknowledged a heartbeat for 10 s, derived channels (`ppg-rr`, `resp-thermal`, `eda` events, `still`, `impact`, `cue`, `btn`, health, `hb`) are appended to a ring file (2 MB reserved of the 8 MB flash, about 40 min of derived data); raw streams are dropped and counted. On reconnection the buffer replays with the original `t` and `n`, tagged `replay: 1`. Verify: N-G2.
- **N-L3 Host acknowledgement** (1 h). The capture service answers each `hb` with one byte; the firmware uses it for N-L2's link-down decision. Without a capture service the serial monitor's absence of acks means buffering after 10 s, which is the safe default.

### Host (N-H)

- **N-H1 Capture service** (6 h). `tools/capture_service.py`: watches for the port, reconnects on loss, answers heartbeats (N-L3), one file per session id, validates each line against the schema, refuses to start under 200 MB free, writes a session index. Runs on a laptop now and as a systemd unit on the belt-pack Pi later. Verify: N-G2.
- **N-H2 Analyser hardening** (4 h). Never crash on a capture: skip and count malformed lines, sort by (`boot`, `t`), stitch boots by session id, report each unavailable capability with its reason (no IMU, thermopile fogged 40 %, link down 3 min) in the summary and JSON; `--strict` exits non-zero on any skipped line for CI. Verify: N-G7 with corrupted fixtures.
- **N-H3 Real-capture fixtures** (2 h once M-G2 runs). The first bench and shadowboxing captures become golden fixtures with expected summaries; the synthetic session stays for unit behaviour.
- **N-H4 Replay equivalence tool** (3 h). Extend the `rr_replay.py` pattern: `tools/replay_equivalence.py` runs the host references on a raw capture and diffs against the firmware's derived lines in the same file (RR RMS ≤ 15 ms, breaths ≤ 1/min, SCR count ± 1, identical mode transitions). Verify: N-G6.

### Test and CI (N-T)

- **N-T1 CI for the Mk0.5 target** (2 h). A job in `.github/workflows/firmware.yml` that runs `pio run -e mk05_heltec_v3` and `pio test -e native` with the PlatformIO cache. Today CI only builds the Nano sketch.
- **N-T2 CI for the host tools** (1 h). `python -m unittest discover -s tests -t .` on 3.11 and 3.14 (pytest is optional and not installed on the dev Mac; the README gets the unittest line, N-D1).
- **N-T3 Fault-injection keys** (2 h). Debug keys behind `HELMKIT_DEBUG`: spin the loop (watchdog), force a NoAck, fill the TX buffer, fake low battery. Each maps to a gate in §5 so the bench checklist can run them.
- **N-T4 Bench checklist per capability** (2 h). `firmware/BENCH_CHECKLIST.md` gains one block per row of §3 with the injection key, the expected log lines and the expected OLED page.

### Docs (N-D)

- **N-D1 README refresh** (1 h). Status line, layout tree (real drivers, stubs, DSP, layers, tests), the unittest command in `tools/README.md`, and removal of the May sprint references or their relabelling as history.
- **N-D2 PINOUT update** (1 h). IMU on bus 1 (address), button GPIOs, OLED already on bus 0; change log entry.
- **N-D3 SCHEMA v0.3 promotion** (1 h). `still`, `impact`, `imu`, `eda-forehead`, `resp-thermal`, `btn`, `hb`, `boot`, `drops`, `ppg-q` move from proposed to emitted as each lands, with their quality rules in §4.

## 5. Validation ladder

| Gate | What | Pass |
|---|---|---|
| N-G1 bench soak | all sensors on the bench, 2 h session | no reset, `drops` 0, every channel `ok` ≥ 99 % of lines, OLED page correct at the end |
| N-G2 yank | USB unplugged for 60 s three times during a bench session | zero derived lines lost (replayed with original `t`), raw gap flagged, boot id unchanged, capture service reconnects within 5 s |
| N-G3 brownout | run the LiPo down under load, then a forced reset mid-session | the log's last line before the reset is the low-battery summary or a `boot` line explains the reset; the session resumes with its id and tally |
| N-G4 bus fault | pull one sensor's connector for 30 s, short SDA for 1 s | other channels continue with `ok`; the sensor rejoins within 10 s of reconnection; one health line per transition |
| N-G5 operator | 30 min shadowboxing in gloves with the nape pod | no accidental session end; every press logged and acknowledged; OLED readable between rounds |
| N-G6 equivalence | one raw capture through the host references and the firmware | RR RMS ≤ 15 ms, breaths ≤ 1/min, SCR count ± 1, identical mode transitions and cue lines |
| N-G7 CI | every push | Mk0.5 build, native tests, host tests and the strict analyser run green |

N-G1 and N-G4 need only the hardware already on hand. N-G5 needs the nape pod printed (vp0.17) and the switches. N-G6 needs one real capture. M-G2, M-G3 and M-G4 from Track M remain the physiological gates and are unchanged.

## 6. Phasing

| Phase | Needs | Items | Delivers |
|---|---|---|---|
| 0 · **done 2026-09-11** | nothing | N-D1, N-D2, N-T1, N-T2, N-F1, N-F2, N-F6, N-F4, N-L1, N-H2 | CI on the real target, attributable restarts and gaps, bus recovery, an analyser that never crashes. Bench gates N-G1..G4 still to run on hardware. |
| 1 · **firmware done 2026-09-11**, bench pending | IMU ~$5, switches | N-S4, N-U1, N-U3, N-F3, N-F5, N-F7, N-S1..N-S3, N-T3, N-T4 | real stillness and impacts, buttons with guards, clean low-battery ending, self-tests, the bench checklist. As built: the IMU driver auto-detects MPU-6050 or LSM6DS3 class parts (register-level, no new library); session state lives in NVS (Preferences), not LittleFS, and resumes only after an involuntary reset (brownout / panic / watchdog / sw) because there is no clock for the plan's 5-minute window; the serial `M` needs a second `M` within 3 s while the button's long press is its own guard; EDA stays at 50 Hz (SCHEMA); the PPG self-test is the existing smoke rate gate plus the new `ppg-q` window quality (LED-current / DC checks wait for a finger on the bench). |
| 2 · **built 2026-09-11**, bench pending | nothing | N-L2, N-L3, N-H1, N-U2, N-S5, N-S6, N-H4, N-D3 | survives a yanked link, OLED status, fusion and sweat rule on the helm, equivalence tool. As built: the link buffer is two alternating 448 KB LittleFS files replayed 20 lines per loop with `"replay":1`; the host ack is the byte `~` and the 10 s rule arms only after the first ack of a boot, so a plain monitor never triggers buffering; the OLED is driven directly over Wire with a built-in 3x5 font at 2x (no library pinned); `hr` carries the single-source half of the fusion rule until an ECG source exists; the SCR detector is a streaming port of the host algorithm and shares its known weakness (a noiseless decay merges into the next ramp, which real ADC noise breaks up); the capture service keeps rejects in one file per output directory. |
| 3 · after M-G2 | one real capture | N-H3, N-G6 | golden fixtures, the equivalence gate closed |
| 4 · Mk1 BOM | bone conduction, LED strip, coil driver | cue hardware, N-F8 | cueing on the head; the coil interlock |

Phase 0 is the cheapest insurance in the repo: every later phase's bugs land in CI instead of on the bench.

## 7. Risks

- **Flash wear from the derived-channel buffer.** 2 MB ring at derived rates is under 10 MB per day of use; LittleFS wear-levels it. Keep raw streams out of flash.
- **I²C bus load with the IMU at 100 Hz.** Four devices at 400 kHz leave headroom, but the MAX30102 FIFO reads are bursty; if the bus saturates, the IMU drops to 50 Hz (impacts are still caught by the accelerometer's own peak latch if the part has one; prefer a part with a high-g interrupt).
- **Button GPIO choice.** GPIO 45/46 are strapping pins on the S3; buttons must be pulled up and read after boot only, or moved to freed LoRa pins. Decide in N-D2 before wiring.
- **Host-first drift.** If a firmware port changes a constant, the Python reference must change in the same commit; N-G6 and N-T2 exist to catch it.
- **The belt-pack Pi does not exist yet.** N-H1 runs on a laptop first; nothing in the firmware assumes the Pi.

## 8. What "Track N lands" means

A bench session can be run by the checklist alone, every fault in §5 has been injected at least once with the expected log and display, one real capture has passed the equivalence gate, and CI is the thing that says whether a change is safe.
