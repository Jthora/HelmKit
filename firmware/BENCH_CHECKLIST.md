# Bench checklist — first-flash of a HelmKit firmware target

Run this checklist the **first** time you flash a given sketch
to a given physical board. After it passes once, daily flashes
need only the smoke step at the bottom.

The order matters. Steps 1–4 are **pre-flash** safety; skipping
them risks driving outputs into a powered platform.

---

## Pre-flash — the chip is NOT yet on B-PWR

### 1. Confirm the Nano is on the bench, NOT in B-PWR

This is the only configuration sprint 0.3 firmware is validated
for. If the Nano is socketed into the B-PWR perfboard, the
sketch is technically safe (Belt 1 keeps K1_DRIVE LOW) but you
lose the ability to instrument with a multimeter before
applying platform power.

- [ ] Nano v3 is on a breadboard or bare on the bench.
- [ ] No external power connected to the Nano (USB only).
- [ ] B-PWR / B-SIG perfboards, if present, are **powered off**
      and the Nano is **not** plugged into the DIP socket.

### 2. Inspect the USB-UART chip

The Nanos in inventory split between CH340 and FT232 variants.
Both work, but the port name differs.

- [ ] Identify the chip on your Nano (look near the USB jack).
- [ ] If CH340 and macOS doesn't enumerate, install the WCH
      driver. Built-in support varies by macOS version.
- [ ] Plug USB in. Run `arduino-cli board list`.
- [ ] Note the port name. CH340 typically appears as
      `/dev/cu.wchusbserial-*`; FT232 as `/dev/cu.usbserial-*`.

```bash
arduino-cli board list
```

### 3. Identify the bootloader variant

Clone Nanos ship with either the standard `atmega328` Optiboot
or the older `atmega328old` bootloader. Wrong choice = upload
times out.

- [ ] First attempt the standard fqbn:
      `arduino:avr:nano:cpu=atmega328`
- [ ] If `avrdude: stk500_recv(): programmer is not responding`,
      retry with `:cpu=atmega328old`.
- [ ] Record which one this specific board needs. Mark it on
      the board itself with a Sharpie if you have multiples.

### 4. Build identity sanity check

- [ ] Tree clean? (`git status --short` should be empty for a
      production flash; `-dirty` is fine for iteration.)
- [ ] `./firmware/build.sh nano_bringup` succeeds.
- [ ] Note the BUILD_ID it printed. You'll see it in the boot
      banner after flash.

---

## Flash

### 5. Upload

```bash
./firmware/build.sh nano_bringup /dev/cu.wchusbserial-XXXX
```

(or whatever port name from step 2)

- [ ] avrdude reports "verification successful".
- [ ] No errors.

### 6. Observe boot banner

```bash
arduino-cli monitor -p /dev/cu.wchusbserial-XXXX -c baudrate=115200
```

- [ ] Boot banner appears within 1 second of opening the monitor.
- [ ] BUILD_ID in banner matches step 4.
- [ ] `mcusr=0x01 (POR )` on first power-on. (If you see anything
      else, *that's worth knowing* — note it before continuing.)
- [ ] `freeRam` >= 1500 B.

### 7. Observe heartbeat

- [ ] `HKMK0|...` frames appear at 1 Hz.
- [ ] `tick` increments monotonically.
- [ ] `freeRam` field is stable (within ±32 B) across at least
      10 frames.

### 8. D13 LED

- [ ] On-board orange LED next to "L" label blinks at 1 Hz.

### 9. K1_DRIVE LOW verification (the real safety check)

This is the bench equivalent of Belt 1. Mandatory before this
Nano is ever socketed into B-PWR.

- [ ] Multimeter to DC volts, COM on Nano GND, probe on D3.
- [ ] Reading: **0.0 V ± 0.05 V**, stable.
- [ ] If reading is anything else (floating, oscillating,
      ~5 V), **STOP**. The sketch did not initialize the pin
      correctly or the chip is damaged. Do NOT proceed.

### 10. Smoketest

With the monitor closed (smoketest opens its own serial):

```bash
python3 firmware/tools/heartbeat_smoketest.py \
  --port /dev/cu.wchusbserial-XXXX
```

- [ ] Exit code 0.
- [ ] Output: "OK: 10 frames validated".

### 11. WDT verification (optional but recommended once per chip)

To prove the watchdog actually fires:

1. Temporarily add `while(1){}` immediately after the boot
   banner in `setup()`.
2. Re-flash.
3. Observe: chip resets every ~2 s, and the boot banner shows
   `mcusr=0x08 (WDT )`.
4. Revert the temporary hang, re-flash.

- [ ] WDT verified once for this specific chip.

---

## Daily flash (after first-flash gate has passed)

Just:

```bash
./firmware/build.sh nano_bringup /dev/cu.wchusbserial-XXXX
python3 firmware/tools/heartbeat_smoketest.py --port /dev/cu.wchusbserial-XXXX
```

If both return 0, you're good. Step 9 (D3 voltage) should be
re-checked whenever the pin-init code in `enforceFailSafePins()`
has changed.

---

## When this checklist fails

- **Boot banner missing**: USB enumeration issue or wrong baud.
  Confirm 115200 in the monitor.
- **`mcusr=0x08` on every boot**: WDT pet path broken. Check
  recent edits to `loop()`. Belt 3 is firing, which is *good*
  in the sense that it's protecting you, but you have a real
  bug.
- **`mcusr=0x04` (BOD)**: Vcc dipped below ~2.7 V. Bad USB cable
  or insufficient supply current. Try a different cable / port.
- **Non-monotonic tick**: Chip is resetting silently between
  frames. Combine with MCUSR field to diagnose.
- **D3 not LOW**: Belt 1 broken. Check `enforceFailSafePins()`
  ran before any other code touched D3. Do NOT socket into
  B-PWR until fixed.
- **Smoketest CRC mismatch**: Either a transmission issue
  (cheap USB cable / EMI nearby) or `crc8()` in the sketch
  disagrees with PROTOCOL.md. Reference the Python impl.

---

## Cross-references

- Firmware safety model: [`SAFETY.md`](SAFETY.md)
- Serial protocol: [`PROTOCOL.md`](PROTOCOL.md)
- Pin map and §6.5.5 K1 fail-open logic: [`../docs/sprint_0.2_circuit_spec.md`](../docs/sprint_0.2_circuit_spec.md)

## Track N capability checks (Mk0.5, Heltec V3)

Run after the first flash of any Track N build. Each block names the trigger, the log lines to expect and the pass rule.
Debug keys need a build with `-D HELMKIT_DEBUG`. Score the capture afterwards with
`python3 tools/analyze_combat_session.py capture.ndjson --strict`; the integrity line must show 0 skipped.

| Capability | Trigger | Expect in the log | Pass |
|---|---|---|---|
| Boot attribution | power on; later `W` (watchdog) | `kind:boot` after `hello` with `reason:poweron`; after `W`, a reset within 5 s and `reason:task-wdt` | both reasons seen |
| Sequence + heartbeat | leave the board 60 s | `n` increments by one on every line; `ch:hb` every 5 s with `drops:0` | no gaps in `n`, 12 heartbeats |
| USB yank (N-G2) | unplug USB for 60 s three times during a session, then reconnect | `hb` gap of 60 s; the first `hb` after reconnect reports `drops` and `link_down` > 0; `n` gap equals the drops | analyser `lost` equals firmware drops; boot id unchanged |
| TX flood + shedding | `F` | `hb` with `drops` > 20; `kind:health` source `link` `ok -> shed`; `gsr` / `temp-*` lines stop; `ppg-rr`, `cue`, `hb` continue; `shed -> ok` 30 s after the last drop | derived lines never stop |
| Bus fault (N-G4) | `K` with `g`, `t`, `a` streams running; or pull one sensor's connector for 30 s | `kind:health` `ok -> no-ack` per stream; re-begin attempts at 5, 10, 20, 60 s (`note:re-begin ...`); `no-ack -> ok` once the bus is back; `source:i2c1` line if SDA was held | every stream back within 10 s of the bus returning; other streams unaffected |
| Low battery (N-G3) | `V` during a session | `cue:low-battery` after 10 s, `summary:tally=N`, `session-end`, `kind:health` `vbat ok -> low`; streams stop; LED fault pattern; `V` again → `low -> ok` | session ended cleanly with the summary line last |
| Session persistence (N-G3) | start a session, tally twice, press the board's RST | after the boot line: `kind:health` source `session` `lost -> resumed` with the tally, `cue:session-resumed`, `mode:tranquil`; a power-on reset instead gives `saved -> discarded` | tally preserved across the reset |
| Session-end guard (N-U3) | `M` once, wait 4 s, `M` twice within 3 s | first `M`: `cue:confirm-end` only; the pair: `summary:` + `session-end` | a single `M` never ends a session |
| Buttons (N-G5) | wire tact switches to GPIO 26 / 33 / 34 and a slide to 40 (to GND, pull-ups internal); press each; hold prime 1.5 s | `ch:btn` per press (`round:short`, `prime:short`, `tally:short`, `prime:long`, `sanctuary:on/off`) and the matching `cue` / `mode:` lines | a 5 ms tap logs nothing; a long press fires once |
| IMU (N-S4) | `a` with the board flat and still, then shake, then rap it on the bench | `kind:smoke` source `imu` `ok:1` with `ev_a` ≈ 1000; `still` 1 at rest, 0 while shaking; `impact` with the peak g on the rap; `activity` every 10 s | self-test passes; ≥ 1 impact per rap, none while shaking gently |
| PPG quality (N-S1) | `g` with a finger on the sensor for 30 s, then off for 30 s | `ppg-q` every 10 s: `q:ok` with v ≥ 0.8 on the finger, then `q:gap` with v 0 | the quality flips within 20 s of the finger leaving |
| Thermopile fog + donning (N-S2) | `t`, `N` (nose), `m`, breathe on the sensor 3× within 30 s; then breathe elsewhere for 30 s after a new `m`; then cover the lens with a cold wet cloth for 25 s | no cue on the first session; `cue:check-nose-sensor` 30 s into the second; `temp-nose` `q:gap` after 20 s under the cloth, `ok` again once uncovered | breaths open the session silently; the fogged lines are flagged |
| EDA contact (N-S3) | `e` with the electrodes on, then lift one for 2 s | `gsr` `q:ok` → `q:out-of-range` for the first second below the floor → `q:gap` after 1 s; `kind:health` `gsr ok -> gap` | the gap flag appears after one second, not at once |
| Link buffer + replay (N-L2, N-G2) | `m`, `g`, `t`; unplug USB for 60 s; replug and reconnect the monitor or `tools/capture_service.py` | on reconnection a burst of lines tagged `"replay":1` with their original `t` and `n`; `hb` shows `buffered` > 0 and `buf` returning to 0; the analyser's integrity line counts 0 lost event lines | every `cue` / `ppg-rr` / `resp-thermal` line from the gap arrives; raw `gsr` / `temp-*` lines from the gap are absent and counted as drops |
| Host ack (N-L3) | run `tools/capture_service.py`; then suspend it (Ctrl-Z) for 30 s and resume | while suspended the helm sees no `~`: after 10 s events go to the buffer (`hb` `buf` grows); on resume the service acks and the replay drains | with a plain `pio device monitor` (never acks) nothing buffers unless the cable is out |
| OLED (N-U2) | power on; `m`; `g`; `V` (debug) | boot health line `oled off -> ready`; the status page shows the mode, HR once a finger is on, `P:OK`, `LINK UP`, the tally; `V` switches to the fault page `LOW BATTERY` | readable at arm's length; `oled absent` if the panel does not answer on 0x3C |
| Contact temperature (N-S5) | `c` with a MAX30205 on the pads, hand over one sensor for 60 s | `temp-skin.L` (and `.R`) at 5 Hz in range; `sweat` every 10 s flips to 1 while the skin warms faster than 0.05 °C/min | `kind:health` `temp-skin` lines on pull / replug; the supervisor re-begins |
| SCR + HR on the helm (N-S6) | `e`, `g`; startle the wearer (a loud clap) twice one minute apart | one `scr` event within ~2 s of each clap; `hr` every 10 s with `q:ok` while `ppg-q` ≥ 0.8, `q:gap` with the finger off | `tools/replay_equivalence.py` on the capture: `scr` count within ±1 of the host, `modes` identical |
| Equivalence (N-G6) | any session capture with `t`, `e`, `g`, `m` and a few cues | `tools/replay_equivalence.py capture.ndjson` | PASS on breathing, scr and modes; `rr` skipped unless raw PPG was streamed |
