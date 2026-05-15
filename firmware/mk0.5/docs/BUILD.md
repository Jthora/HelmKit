# Mk0.5 BUILD — toolchain, flash, debug

## 1. Toolchain prerequisites

| Tool          | Version (verified) | Source                                |
|---------------|--------------------|---------------------------------------|
| PlatformIO    | 6.1.19             | `brew install platformio`             |
| Python        | 3.14.4             | macOS Homebrew                        |
| GitHub CLI    | 2.88.1             | `brew install gh`                     |
| ESP-IDF       | (auto)             | Pulled by PlatformIO on first `pio run` |
| Xtensa GCC    | (auto)             | Pulled by PlatformIO on first `pio run` |

First `pio run` downloads ~150 MB of toolchain. This is expected and only
happens once per machine.

## 2. Build

```bash
cd firmware/mk0.5
pio run                    # compile only
pio run --target upload    # compile + flash via CP2102
pio device monitor         # open serial monitor at 115200
```

## 3. Flash via USB

1. Plug Heltec V3 into Mac with USB-C data cable (NOT charge-only).
2. Verify enumeration: `ls /dev/cu.usbserial-*` or `pio device list`.
3. `pio run --target upload`.
4. If upload fails with "Failed to connect", hold BOOT (GPIO 0) while
   pressing RESET, release RESET, then release BOOT. Retry upload.

## 4. Serial monitor

```bash
pio device monitor --filter esp32_exception_decoder --filter time
```

The `esp32_exception_decoder` filter symbolicates panic backtraces against
the most recent build. Without it, a crash prints only raw addresses.

## 5. Debug (JTAG, optional)

Mk0.5 does not require JTAG. USB-CDC logging is sufficient for sensor
smoke tests. Reserve JTAG bring-up for Mk1.0 dual-MCU debugging.

## 6. Common failure modes

| Symptom                                  | Cause                                  | Fix |
|------------------------------------------|----------------------------------------|-----|
| `Could not open /dev/cu.usbserial-*`     | Charge-only cable, or driver missing.  | Swap cable; install Silicon Labs CP210x driver if needed. |
| `Timed out waiting for packet header`    | Board not in download mode.            | BOOT+RESET sequence (see §3). |
| `Brownout detector was triggered`        | USB hub undervolting the board.        | Plug direct into Mac, or use powered hub. |
| `Guru Meditation Error: Core 0 panic'ed` | Stack overflow or null deref.          | Re-run with `CORE_DEBUG_LEVEL=5`; check exception decoder output. |
| OLED stays blank                         | Vext not driven low.                   | Check GPIO 36 is being asserted in setup() before display init. |

## 7. Reproducibility

* Library versions are pinned in `platformio.ini`. Do NOT use `latest`.
* The `.pio/` build directory is gitignored.
* `pio system info` output should be archived in
  `firmware/mk0.5/docs/toolchain-snapshot.txt` whenever a gate is crossed
  (L0, L1, L2, G1, G2). See `docs/mk0.5_firmware_bringup.md`.
