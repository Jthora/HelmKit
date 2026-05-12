# HelmKit firmware

Firmware tree for the HelmKit platform and modules. Each MCU
target gets its own subdirectory.

## Layout

```
firmware/
├── README.md              ← you are here
├── .gitignore             ← build artifacts, .pio, *.hex, *.elf
└── nano_bringup/          ← sprint 0.3 deliverable — Nano v3 alive
    └── nano_bringup.ino
```

Future sprints will add:

```
firmware/
├── nano_safety/           ← sprint 0.3a — B-PWR safety state machine
├── heltec_uplink/         ← sprint 0.4  — B-SIG session UI + LoRa
├── pi_bridge/             ← sprint 0.5  — Pi 4 host service (Python)
└── stabilizer_mk1/        ← module firmware — see ../external/psiStabilizer
```

---

## Toolchain (sprint 0.3 pick)

**`arduino-cli`** is the locked toolchain for the AVR target (Nano v3).
Rationale:

| Option | Verdict |
|---|---|
| **arduino-cli** ✅ | Free, scriptable, no Electron, CI-friendly, supports both AVR (Nano) and ESP32 (Heltec V3) via core install. **Picked.** |
| Arduino IDE 2.x | Electron app, fine for visual debugging but not the source of truth. Optional install. |
| PlatformIO | More powerful but heavier; can adopt later if multi-target builds need it. Not picked at sprint 0.3. |
| AVR-GCC raw | Too much yak-shaving for sprint 0.3 ("prove the chip wakes up"). |
| ESP-IDF for Heltec | Heltec V3 will use arduino-esp32 core (sprint 0.4); native ESP-IDF deferred. |

Install on macOS:

```bash
brew install arduino-cli
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
```

For the Heltec V3 (sprint 0.4):

```bash
arduino-cli config add board_manager.additional_urls \
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32
```

---

## Sprint 0.3 deliverable — `nano_bringup`

**Goal (from sprint brief):** *"pick toolchain, get blink working on
the MCU you spec'd, set up the repo. Just boot a workspace and
prove the chip wakes up."*

**MCU spec'd in [sprint 0.2 §3.3.2](../docs/sprint_0.2_circuit_spec.md):**
Arduino Nano v3 (ATmega328P) as the B-PWR safety MCU.

### What `nano_bringup.ino` does

- Blinks the on-board D13 LED at 1 Hz.
- Emits `helmkit-mk0 nano alive tick=N` on Serial @ 115200 baud,
  once per second.
- Prints `F_CPU` at boot to confirm fuse/clock setup.

### What it deliberately does NOT do

- Does **not** touch any of the §3.3.2 platform pins (SAFETY_n,
  K1 relay, INA219 I²C, etc.). Those wire up in sprint 0.3a.
- Does **not** implement the §6.5.5 safety state machine.
- Does **not** assume any external hardware. Pure on-chip.

This is *bring-up only*. It proves: toolchain → compile → flash →
boot → LED → serial. End to end.

### Build

```bash
cd /Users/jono/Documents/GitHub/HelmKit
arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328 firmware/nano_bringup
```

Verified clean on sprint 0.3 day-one:
> Sketch uses 2522 bytes (8%) of program storage space.
> Global variables use 197 bytes (9%) of dynamic memory.

### Flash (when a Nano is on the bench)

```bash
# List ports — the Nano shows up as /dev/cu.usbserial-* or
# /dev/cu.wchusbserial-* depending on the USB-UART chip.
arduino-cli board list

# Upload (replace PORT). For OLD-bootloader Nanos add
# :cpu=atmega328old to the FQBN.
arduino-cli upload -p /dev/cu.usbserial-XXXX \
  --fqbn arduino:avr:nano:cpu=atmega328 \
  firmware/nano_bringup

# Watch heartbeat
arduino-cli monitor -p /dev/cu.usbserial-XXXX -c baudrate=115200
```

Expected output after flash:

```
helmkit-mk0 nano boot
sprint 0.3 firmware bring-up — blink + heartbeat
F_CPU=16000000 Hz
helmkit-mk0 nano alive tick=1
helmkit-mk0 nano alive tick=2
helmkit-mk0 nano alive tick=3
...
```

### Acceptance gates (sprint 0.3 DoD)

- [x] Toolchain picked and documented (`arduino-cli`).
- [x] `firmware/` directory created with `.gitignore`.
- [x] Bring-up sketch compiles clean for `arduino:avr:nano:cpu=atmega328`.
- [ ] *(bench)* Sketch flashes to a physical Nano v3.
- [ ] *(bench)* On-board LED blinks at ~1 Hz.
- [ ] *(bench)* `arduino-cli monitor` shows the heartbeat string
      incrementing.

The three bench gates are the operator's hands-on verification
step — they don't gate the sprint commit because the toolchain
+ clean compile is already evidence that the workspace is wired
correctly. The bench check converts compile-time confidence into
on-silicon confidence.

---

## Repo conventions

- One target = one subdirectory containing one `.ino` of the
  same name (arduino-cli convention).
- No build artifacts in git (`.gitignore` covers `build/`,
  `*.hex`, `*.elf`, `.pio/`).
- Each target's `README.md` (or comment header in the `.ino`)
  references the §-section of the circuit spec that owns its
  pin map and role.
- Safety-critical code (sprint 0.3a onward) MUST cite the
  relevant §6.5 row in a comment near the affected lines.

---

## Cross-references

- Circuit spec: [`docs/sprint_0.2_circuit_spec.md`](../docs/sprint_0.2_circuit_spec.md)
- Pin map: §3.3 of the circuit spec
- Safety envelope: [`docs/safety.md`](../docs/safety.md)
- Roadmap: [`docs/roadmap.md`](../docs/roadmap.md)
- Stabilizer module firmware: [`external/psiStabilizer`](../external/psiStabilizer) (submodule)
