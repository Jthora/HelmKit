# Wokwi simulation — nano_bringup

This directory lets you verify `nano_bringup.ino` **without
plugging in a physical Nano**. It unblocks DoD gates 6 and 7 of
sprint 0.3 for anyone reviewing the firmware before the build
day.

## Two ways to run it

### Option 1 — wokwi.com (zero install)

1. Open <https://wokwi.com/projects/new/arduino-nano>
2. Replace the contents of `sketch.ino` with
   [`../nano_bringup.ino`](../nano_bringup.ino).
3. Click the wrench icon → "Edit `diagram.json`" → paste the
   contents of [`diagram.json`](diagram.json).
4. Click ▶︎ Start. The simulator opens a serial monitor.

**Expected output** (after ~100 ms):

```
# helmkit-mk0 nano boot build=dev mcusr=0x01 (POR )
# F_CPU=16000000 Hz  freeRam=1804 B
# protocol=HKMK0 (see firmware/PROTOCOL.md)
HKMK0|1050|1|01|1804|dev|XX
HKMK0|2050|2|01|1804|dev|XX
...
```

The on-board D13 LED blinks at 1 Hz. The blue "K1 coil" LED on
the diagram stays **OFF** the whole time — that's the visual
proof of Belt 1 (K1_DRIVE held LOW at boot, never raised by
bring-up firmware).

### Option 2 — VS Code Wokwi extension (local)

Requires the [Wokwi for VS Code](https://docs.wokwi.com/vscode/getting-started)
extension and a free license token.

1. Compile the sketch locally so a `.hex` exists:
   ```bash
   ./firmware/build.sh nano_bringup
   ```
   Note: `build.sh` doesn't currently materialize the `.hex`
   into `firmware/nano_bringup/build/`. Use `arduino-cli`'s
   `--output-dir`:
   ```bash
   arduino-cli compile \
     --fqbn arduino:avr:nano:cpu=atmega328 \
     --output-dir firmware/nano_bringup/build/arduino.avr.nano \
     firmware/nano_bringup
   ```
2. Open `firmware/nano_bringup/wokwi/diagram.json` in VS Code.
3. Cmd-Shift-P → "Wokwi: Start Simulator".

Output is identical to Option 1.

## What the simulation proves

- ✅ Toolchain → compile → boot path works end-to-end.
- ✅ Boot banner emits before first heartbeat.
- ✅ MCUSR decoded correctly (Wokwi cold-boot is `POR`).
- ✅ K1_DRIVE (D3) is LOW at and after boot.
- ✅ R/A/G indicator LEDs stay OFF (Belt 2 INPUT_PULLUP keeps
  them un-driven).
- ✅ D13 blinks at 1 Hz.

## What the simulation does NOT prove

- The WDT actually resets a hung chip. Wokwi's AVR simulation
  models WDT but it's worth confirming on real silicon by
  temporarily inserting a `while(1){}` after the boot banner
  and observing a WDRF-flagged re-boot.
- BOD behavior at low Vcc. Wokwi runs at a perfect 5.0 V; the
  brown-out path needs a real bench.
- USB-UART chip behavior (CH340 vs FT232). Wokwi emulates an
  idealized serial port.

These three gaps are the reason `BENCH_CHECKLIST.md` still
exists — bench verification has a different job than simulation.

## Saving CRCs from sim runs

If you copy a frame out of the Wokwi serial monitor, paste it
into `firmware/tools/fixtures/<your_scenario>.txt` to grow the
CI fixture set. The smoketest's CRC check will tell you
immediately if you grabbed it cleanly.
