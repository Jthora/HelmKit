# HelmKit firmware — safety model

This document defines the **four-belt safety model** every
HelmKit MCU firmware target must satisfy, starting with sprint
0.3 bring-up and inherited by every subsequent sprint.

The model is enforced primarily by **code review against this
document**, secondarily by CI compile gates + smoketest, and
ultimately by [`BENCH_CHECKLIST.md`](BENCH_CHECKLIST.md) before
a chip is socketed into the powered platform.

The reviewer's loyalty is to the model, not to me, not to the
schedule.

---

## 1. The fault we are protecting against

The B-PWR Nano drives K1, the relay that gates `12V_RAIL` to
every downstream load including any future stimulator coil and
any module on the bus. K1 is wired **fail-open**: when K1's
coil is de-energized, its contacts open, and `12V_RAIL` is
disconnected.

The fault we are protecting against is: **K1's coil gets
energized (or kept energized) when it shouldn't be**, putting
the operator at risk of an unintended stimulus delivery.

The four belts each block this fault through an independent
mechanism. Any single belt failing is not sufficient to cause
the fault. Two simultaneous failures may be, which is why we
do not stop at three.

---

## 2. The four belts

### Belt 1 — explicit fail-safe pin init

Every firmware target that has access to K1_DRIVE (D3 on the
Nano) **must**, in `setup()`, before any other code touches
D3, execute:

```c
pinMode(K1_DRIVE_PIN, OUTPUT);
digitalWrite(K1_DRIVE_PIN, LOW);
```

When a future sprint (0.3a) implements the safety state machine
and raises K1_DRIVE HIGH inside an `ARMED` or `SESSION_ACTIVE`
state, the line that does so **must** carry an inline comment
citing `§6.5.5` of the circuit spec, and the surrounding
function **must** drop K1_DRIVE LOW on every error path.

### Belt 2 — implicit fail-safe for everything else

Every other §3.3.2 platform-bus pin on the Nano must be
`INPUT_PULLUP` at boot. This means:

- A stray solder bridge between two pins reads HIGH on both,
  never gets the chance to short an output through a pin.
- A probe touch never registers as a glitch on a driven line.
- A pin that doesn't get its production role wired in until a
  later sprint stays inert in the meantime.

The convention is enforced by the `enforceFailSafePins()`
function in every Nano firmware target. New pins added to
§3.3.2 must be added to that function in the same commit.

### Belt 3 — watchdog timer

`wdt_enable(WDT_TIMEOUT_CODE)` is called in `setup()` after
fail-safe pin init. The current timeout is `WDTO_2S` for
bring-up. Sprint 0.3a tightens this to `WDTO_250MS` once the
state machine is in place.

The watchdog catches:

- Infinite loops introduced by a buggy edit.
- Library calls that block longer than expected.
- A stack-overflow that corrupts the return path but somehow
  leaves the loop spinning.

The discipline: **`wdt_reset()` must be called as the FIRST
statement of every iteration of `loop()`**. Any code path that
forks the main loop (a future ISR-driven event loop, a future
state machine entry/exit, etc.) must explicitly preserve this
invariant.

Allowed exception: the boot-time `delay(100)` for USB-CDC
enumeration is bracketed by `wdtPet()` calls in
`nano_bringup.ino` so even setup() never goes longer than
~150 ms without a pet.

### Belt 4 — observability

`MCUSR` is captured at `.init3` (a gcc naked hook that runs
before `main()`), then cleared. The boot banner decodes the
captured flags into human-readable form (`POR`, `EXT`, `BOD`,
`WDT`).

This means: if a chip resets for any reason, the next boot
banner tells us why. A WDT reset is not silent. A brown-out is
not silent. A glitchy external reset line is not silent.

The host parser (sprint 0.5 Pi 4 service) MUST surface
`mcusr & 0x0C` (BORF | WDRF) as a session-level warning, per
[`PROTOCOL.md`](PROTOCOL.md) §5 rule 6.

---

## 3. The banned-API list

These are forbidden across every firmware target, no exceptions
without an explicit one-line waiver in the file header and a
reference to this section.

| Banned | Why |
|---|---|
| `String` class | Heap fragmentation. ATmega328 has 2 KB SRAM total; the heap is where reliability goes to die on this chip. |
| `malloc` / `free` | Same reason. All buffers are stack or static. |
| `new` / `delete` | Same reason. |
| Floating-point in any ISR | Slow, non-deterministic latency, and AVR pulls in fp routines that can blow flash budget. |
| `delay()` in `loop()` | Blocks the WDT pet path. Forbidden. (`delay()` is allowed in `setup()` because setup runs once and is bounded.) |
| `Serial.print()` of a `String` | See first row. Use `F("...")` for flash strings. |
| Library tracking memory in heap (e.g. `ArduinoJson` without static buffers) | Same heap reason. Configure for stack-only or don't use. |

Enforcement: code review against this list. CI does not yet
grep for these — that's a hardening item for a future sprint.

---

## 4. The pin-citation convention

When a firmware line interacts with a §3.3.2 pin in a
non-fail-safe way (i.e. drives an output, reads a signal that
gates safety logic, etc.), the line MUST carry an inline
comment referencing the §-section of the circuit spec that
owns the pin's role:

```c
digitalWrite(K1_DRIVE_PIN, HIGH);   // §6.5.5: enter ARMED, energize K1 coil
```

This is non-negotiable for safety-relevant pins (K1_DRIVE,
SAFETY_N). It is strongly encouraged for everything else.

Rationale: code review of a single PR can verify the citation
matches the spec section. Without the citation, the reviewer
has to remember the entire pin map. With the citation, the
reviewer follows one link.

---

## 5. What sprint 0.3 bring-up firmware does NOT guarantee

The hardening pass closed the structural gaps but it is still
bring-up firmware. It explicitly does NOT:

- Implement the §6.5.5 safety state machine (OFF / ARMED /
  SESSION_ACTIVE / FAULT). That is sprint 0.3a.
- Read SAFETY_n and act on it. The pin is pulled up; the read
  is not wired to any logic. Sprint 0.3a.
- Drive K1 HIGH under any circumstances. K1 stays LOW forever
  in bring-up. Sprint 0.3a flips this.
- Read any sensors (INA219, DS18B20, MPU9250, etc.). Sprint 0.4.
- Communicate with the Pi 4 over anything beyond the serial
  heartbeat. Sprint 0.5.
- Handle stacked reset causes (e.g. BOD-then-WDT). The boot
  banner decodes all bits set, but the host policy for
  responding to stacked causes is sprint 0.5 work.

If you are reviewing a PR that claims to do any of the above
inside `firmware/nano_bringup/`, **stop**. That work belongs in
its own sprint directory.

---

## 6. Hardware preconditions

These are the platform-side assumptions the firmware depends on.
If any of them changes, the firmware safety story changes too.

1. K1 is wired **fail-open**: coil de-energized → 12V_RAIL
   disconnected. `nano_bringup.ino` assumes this. Verified by
   [`docs/sprint_0.2_circuit_spec.md`](../docs/sprint_0.2_circuit_spec.md) §6.5.5.
2. The Nano's Vcc is fed from `5V_LOGIC` behind a polyfuse and
   a TVS. Brown-out detection at 2.7 V is the last line of
   defense.
3. The Nano's RESET pin has a 10 kΩ pull-up. (Stock Nano boards
   provide this; no external part required.)
4. The §3.3.2 platform-bus pins are NOT actively driven by any
   other MCU. The Nano is the sole owner. If the Pi 4 (B-SIG
   side) ever drives a pin that the Nano also drives, the
   contention is a hardware bug, not a firmware bug — but the
   firmware will not detect it.

If a future hardware revision violates any of these, this
document must be updated in the same PR.

---

## 7. Change discipline

Changes to any of the four belts require:

1. A commit message that names which belt is being modified.
2. An update to this document if the belt's mechanism changes.
3. A new fixture in `firmware/tools/fixtures/` if the protocol
   or boot behavior changes observably.
4. CI green.
5. Manual reviewer sign-off on the safety implications.

Tightening a belt (e.g. shrinking the WDT timeout) is preferred
over loosening one. Loosening any belt requires a documented
rationale in the commit message.

---

## 8. Reviewer's quick check

When reviewing a firmware PR, run through this in order:

- [ ] Does `setup()` still call `enforceFailSafePins()` before
      anything that could fault?
- [ ] Does `setup()` still call `wdtArm()`?
- [ ] Is `wdtPet()` still the first call in every iteration of
      `loop()`?
- [ ] Are all §3.3.2 pin interactions tagged with a §-reference
      comment?
- [ ] Does the heartbeat frame still match `PROTOCOL.md`?
- [ ] Does CI pass?
- [ ] If MCUSR fault bits appear in any new fixture: is the
      scenario named and the failure documented?
- [ ] Does the commit message reference which belt(s) were
      touched?

If any answer is "no" or "I don't know", block the PR until
resolved.
