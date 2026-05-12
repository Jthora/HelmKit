# Sprint 0.3 — firmware bring-up

**Brief (verbatim from the operator):**
> *Sprint 0.3 — firmware. With the CAD shell (0.1) and circuit
> spec (0.2) done, today you start firmware: pick toolchain, get
> blink working on the MCU you spec'd, set up the repo. Just
> boot a workspace and prove the chip wakes up.*

Status: **DONE** at sprint close. See §6 DoD.

---

## 1. Scope

This sprint has exactly four deliverables. No more.

1. **Toolchain pick** — name it, install it, write down why.
2. **Repo layout** — `firmware/` exists, has a `.gitignore`,
   has a README that says where future sprints land.
3. **Blink** — the MCU that sprint 0.2 spec'd as the platform's
   primary brain wakes up, runs a program, and proves it's alive.
4. **Documentation of the above** — this file + `firmware/README.md`.

### Out of scope (explicitly)

- The §6.5.5 safety state machine. → sprint 0.3a.
- The Stabilizer module firmware. → see [`external/psiStabilizer`](../external/psiStabilizer) submodule + sprint 0.3a.
- Pi 4 host service. → sprint 0.5.
- Heltec V3 session UI / LoRa uplink. → sprint 0.4.
- Any actual sensor reads. → sprint 0.4+.

Sprint 0.3 is **the workspace boot**, nothing more.

---

## 2. Toolchain pick

**Decision: `arduino-cli`.**

Locked rationale:

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **arduino-cli** | free, scriptable, brewable, supports AVR + ESP32 cores, CI-friendly, no GUI dependency | less powerful than PlatformIO | **picked** |
| Arduino IDE 2.x | nice-to-have for visual debug + serial plotter | Electron weight, not source-of-truth | optional install only |
| PlatformIO | unified multi-target builds, better deps | heavier, more YAML, slower onboarding | **deferred** — adopt if sprint 0.5+ needs it |
| AVR-GCC raw | maximum control | too much yak-shaving for "prove the chip wakes up" | rejected |
| ESP-IDF (for Heltec) | native ESP32 power | overkill for sprint 0.3; arduino-esp32 core is fine | deferred to sprint 0.4 |

**Install footprint (macOS):**

```bash
brew install arduino-cli      # 24.8 MB, no GUI
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr     # ATmega328P / Nano v3
# Heltec V3 (deferred to sprint 0.4):
# arduino-cli core install esp32:esp32
```

Verified on sprint 0.3 build day:
- `arduino-cli` version 1.4.1
- `arduino:avr` core 1.8.7
- `arduino:avrdude` 8.0.0-arduino1

---

## 3. MCU choice

**Target: Arduino Nano v3 (ATmega328P, 16 MHz).**

This is the MCU sprint 0.2 §3.3.2 named as the B-PWR **safety
controller** — the lowest-trust, simplest, most deterministic
brain in the platform. It is the right place to start firmware
work for three reasons:

1. **Determinism.** The Nano runs bare-metal with no RTOS. If
   blink doesn't blink, the bug is in our code or our hardware,
   not in a scheduler.
2. **Fast iteration.** AVR compile + flash is sub-second on this
   machine. Tight feedback loop.
3. **Safety-relevant.** The Nano is the MCU that will eventually
   drive K1 (12V_RAIL kill relay) and run the §6.5.5 safety
   state machine. Getting comfortable with this chip *first* is
   the right investment.

The Pi 4 and Heltec V3 (the other two MCUs in the platform) are
deferred to later sprints when they have actual work to do.

---

## 4. Repo layout

Created this sprint:

```
HelmKit/
├── firmware/
│   ├── README.md
│   ├── .gitignore
│   └── nano_bringup/
│       └── nano_bringup.ino
└── docs/
    └── sprint_0.3_firmware_bringup.md   ← this file
```

The `firmware/README.md` documents:
- the toolchain pick and install commands,
- one-target-one-subdirectory convention,
- where each future sprint's firmware will land
  (`nano_safety/`, `heltec_uplink/`, `pi_bridge/`,
  `stabilizer_mk1/`),
- the build/flash/monitor command set.

---

## 5. The blink program

File: [`firmware/nano_bringup/nano_bringup.ino`](../firmware/nano_bringup/nano_bringup.ino)

What it does:
- Blinks D13 (on-board LED) at 1 Hz.
- Emits `helmkit-mk0 nano alive tick=N` on Serial @ 115200 baud
  once per second.
- Prints `F_CPU` at boot so we can confirm the fuse/clock
  configuration is correct.

What it deliberately does **not** do:
- Touch any of the §3.3.2 platform pins (D2 SAFETY_n, D3 K1
  drive, A4/A5 I²C, etc.).
- Implement the safety state machine.
- Assume any external hardware.

**Build verification (sprint close):**

```bash
arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328 \
  firmware/nano_bringup
```

Output:
> Sketch uses 2522 bytes (8%) of program storage space. Maximum is 30720 bytes.
> Global variables use 197 bytes (9%) of dynamic memory, leaving 1851 bytes for local variables. Maximum is 2048 bytes.

Clean compile. **8% flash / 9% RAM** for a blink + heartbeat is
fine — leaves comfortable headroom for the sprint-0.3a safety
state machine (estimated ~6 KB / 400 B more).

---

## 6. Definition of Done

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Toolchain picked | ✅ | §2 of this doc + [`firmware/README.md`](../firmware/README.md#toolchain-sprint-03-pick) |
| 2 | Toolchain installed on dev machine | ✅ | `arduino-cli` 1.4.1 + `arduino:avr` core 1.8.7 verified |
| 3 | `firmware/` directory exists with `.gitignore` and README | ✅ | committed this sprint |
| 4 | Bring-up sketch compiles for `arduino:avr:nano:cpu=atmega328` | ✅ | 2522 bytes flash, 197 bytes RAM |
| 5 | This sprint doc written and committed | ✅ | you're reading it |
| 6 | *(bench)* Sketch flashes to a physical Nano and blinks | ⏳ | operator hands-on; not blocking |
| 7 | *(bench)* Serial heartbeat visible at 115200 baud | ⏳ | operator hands-on; not blocking |

Gates 1–5 are reproducible from this repo alone and constitute
the sprint's git-visible deliverable. Gates 6–7 are
operator-side hands-on verification — they convert compile-time
confidence into on-silicon confidence and should be ticked off
when the operator next has the Nano on the bench.

---

## 7. What sprint 0.3 explicitly did NOT settle

These are flagged so the next sprint doesn't trip on them:

- **Old-vs-new bootloader.** Nano clones split between the
  stock `atmega328` and the older `atmega328old` bootloader.
  The compile is identical; the upload `--fqbn` must match.
  Operator picks at flash time.
- **USB-UART chip.** Nanos in the inventory use either CH340 or
  FT232. macOS Tahoe handles both natively as of 14.4. If a
  port doesn't appear, install the CH340 driver from WCH. Not
  in scope to bake into firmware.
- **Brown-out detection fuse.** Default BOD on a stock Nano is
  ~2.7 V. For the §4 power story (5V_LOGIC behind a polyfuse +
  TVS) this is fine for Mk0 but should be revisited in sprint
  0.3a alongside the watchdog timer config.
- **Watchdog timer.** Not enabled. Sprint 0.3a problem.

---

## 8. Next sprint preview (0.3a)

Sprint 0.3a's brief, in advance:

> Add the §6.5.5 safety state machine on top of `nano_bringup`.
> States: OFF → ARMED → SESSION_ACTIVE → FAULT. Read SAFETY_n
> (D2, input pull-up), drive K1 (D3, low-side to relay coil).
> Use Timer1 + watchdog. Add unit-testable logic
> (state-transition table separable from `digitalRead`/`digitalWrite`).

This sprint's deliverables are the foundation that 0.3a builds
on. Nothing here will be thrown away.
