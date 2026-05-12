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
