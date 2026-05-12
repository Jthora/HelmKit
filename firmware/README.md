# HelmKit firmware

Firmware tree for the HelmKit platform and modules. Each MCU
target gets its own subdirectory.

## Read these first

1. **[`SAFETY.md`](SAFETY.md)** — the four-belt safety model.
   Non-negotiable for every firmware target.
2. **[`PROTOCOL.md`](PROTOCOL.md)** — serial frame format.
   The contract between chip and host.
3. **[`BENCH_CHECKLIST.md`](BENCH_CHECKLIST.md)** — first-flash
   bench procedure.

## Layout

```
firmware/
├── README.md              ← you are here
├── SAFETY.md              ← four-belt safety model (READ FIRST)
├── PROTOCOL.md            ← serial heartbeat frame spec
├── BENCH_CHECKLIST.md     ← first-flash procedure
├── build.sh               ← arduino-cli wrapper with BUILD_ID injection
├── .gitignore
├── nano_bringup/          ← sprint 0.3 deliverable — Nano v3 alive
│   ├── nano_bringup.ino
│   └── wokwi/             ← in-browser simulation (no hardware needed)
└── tools/
    ├── heartbeat_smoketest.py
    └── fixtures/          ← canned serial output for CI
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

### What `nano_bringup.ino` does (phase-2 hardened)

- Implements the four-belt safety model from
  [`SAFETY.md`](SAFETY.md): fail-safe pin init, INPUT_PULLUP on
  every other §3.3.2 pin, watchdog at 2 s, MCUSR snapshot at
  `.init3`.
- Blinks the on-board D13 LED at 1 Hz.
- Emits a structured, CRC-protected heartbeat frame per
  [`PROTOCOL.md`](PROTOCOL.md) once per second.
- Reports BUILD_ID (`git rev-parse --short HEAD`) so multiple
  flashed chips are distinguishable.
- Reports free SRAM so stack/heap headroom is visible.

### What it deliberately does NOT do

- Does **not** raise K1_DRIVE. K1 stays de-energized. §6.5.5
  safety state machine is sprint 0.3a.
- Does **not** read SAFETY_n meaningfully. Pin is pulled up
  but the read is not wired to logic.
- Does **not** read any sensors. Sprint 0.4.
- Does **not** assume external hardware beyond a USB host.

### Build

```bash
./firmware/build.sh nano_bringup
```

The wrapper injects `BUILD_ID` from git and runs arduino-cli
with `--warnings all`.

Phase-2 size: **4860 B flash (15 %), 238 B RAM (11 %)**.

### Flash

See [`BENCH_CHECKLIST.md`](BENCH_CHECKLIST.md) for the first-flash
procedure. Daily flash short loop:

```bash
./firmware/build.sh nano_bringup /dev/cu.wchusbserial-XXXX
python3 firmware/tools/heartbeat_smoketest.py --port /dev/cu.wchusbserial-XXXX
```

### Simulate (no hardware required)

See [`nano_bringup/wokwi/README.md`](nano_bringup/wokwi/README.md).
Open the diagram in [wokwi.com](https://wokwi.com/) or via the
VS Code Wokwi extension and verify identical behavior. The
diagram includes a visual indicator LED on K1_DRIVE that stays
OFF as long as Belt 1 is healthy.

### Acceptance gates (sprint 0.3 DoD — phase 2)

Phase 1 (compile + repo + blink):

- [x] Toolchain picked and documented (`arduino-cli`).
- [x] `firmware/` directory created with `.gitignore`.
- [x] Bring-up sketch compiles clean.

Phase 2 (hardening — added after re-open):

- [x] Four-belt safety model documented in `SAFETY.md`.
- [x] Sketch implements all four belts.
- [x] WDT enabled at 2 s; pet path verified.
- [x] MCUSR snapshot + decode at boot.
- [x] Fail-safe pin init covers every §3.3.2 platform pin.
- [x] Structured heartbeat with CRC-8 per `PROTOCOL.md`.
- [x] BUILD_ID injection from git via `build.sh`.
- [x] Free-RAM reporting + min-headroom assertion in smoketest.
- [x] Host smoketest (`heartbeat_smoketest.py`) with fixture
      mode and live-serial mode.
- [x] CI workflow runs compile + smoketest on every push.
- [x] Wokwi simulation unblocks bench-only gates for any
      reviewer.
- [x] `BENCH_CHECKLIST.md` covers the unsafe step (socketing
      into B-PWR) with multimeter D3-LOW verification.

Bench gates (one-time per physical chip):

- [ ] *(bench)* Sketch flashes to a physical Nano v3.
- [ ] *(bench)* Boot banner reports `mcusr=0x01 (POR )` on cold
      boot.
- [ ] *(bench)* On-board D13 LED blinks at ~1 Hz.
- [ ] *(bench)* D3 measured 0.00 V (Belt 1 verified on silicon).
- [ ] *(bench)* `heartbeat_smoketest.py --port ...` exits 0.
- [ ] *(bench, once per chip)* WDT actually fires: temporary
      `while(1){}` causes WDRF on next banner.

The bench gates are now per-chip rather than per-sprint —
sprint 0.3 closes when all phase-2 git-visible gates are green;
each new physical chip clears its own bench list on first flash.

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
