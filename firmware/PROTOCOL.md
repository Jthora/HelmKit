# HelmKit firmware — serial protocol

This is the contract between every HelmKit MCU and the Pi 4 host.
Frame format is fixed at sprint 0.3. Future protocol versions
bump the version tag in field 0 (`HKMK0` → `HKMK1` → …) so a
host can talk to mixed-version chips during a transition.

## 1. Wire format

ASCII, line-oriented, `\n` terminated. Each frame is exactly one
line. Frames never contain literal `\n`, `\r`, or the field
separator `|` in payload positions.

```
HKMK0|<ms>|<tick>|<mcusr_hex>|<freeram>|<buildid>|<crc8_hex>\n
```

| # | Field | Type | Description |
|---|---|---|---|
| 0 | `HKMK0` | literal | Protocol version tag. Bump when the frame layout changes. |
| 1 | `ms` | `uint32` decimal | `millis()` at emit. Wraps at ~49.7 days. |
| 2 | `tick` | `uint32` decimal | Heartbeat counter since boot. Starts at 1. Monotonic until reset. |
| 3 | `mcusr_hex` | 2 hex chars | Reset cause register snapshot from `.init3`. Decoded below. |
| 4 | `freeram` | `int16` decimal | Free SRAM in bytes (stack/heap gap). Conservative. |
| 5 | `buildid` | string | `git rev-parse --short HEAD`, optionally `-dirty`. `dev` if no git. |
| 6 | `crc8_hex` | 2 hex chars | CRC-8 over the body (fields 0–5 plus their separators). |

### Reset-cause bits (field 3)

The ATmega328P's `MCUSR` register, masked to four bits we care
about. Multiple bits can be set if reset causes stacked (rare
but possible with brown-out + WDT).

| Bit | Mask | Name | Meaning |
|---|---|---|---|
| 0 | `0x01` | `PORF` | Power-on reset. Normal cold boot. |
| 1 | `0x02` | `EXTRF` | External reset. RESET pin pulled low. |
| 2 | `0x04` | `BORF` | Brown-out reset. Vcc dipped below BOD threshold. **Investigate.** |
| 3 | `0x08` | `WDRF` | Watchdog reset. Code hung past WDT timeout. **Investigate.** |

A bare `0x01` is healthy. Anything with `BORF` or `WDRF` set is
a flag for the host to log loudly and possibly halt session
activation until the operator acknowledges.

## 2. Boot banner lines (informational, NOT heartbeat)

Before the first heartbeat, the firmware emits human-readable
banner lines starting with `# `. The host parser MUST ignore
any line that does not begin with the protocol version tag
followed by `|`.

Example banner:

```
# helmkit-mk0 nano boot build=ee15859-dirty mcusr=0x01 (POR )
# F_CPU=16000000 Hz  freeRam=1804 B
# protocol=HKMK0 (see firmware/PROTOCOL.md)
```

## 3. CRC-8 specification

Dallas/Maxim 1-Wire CRC-8.

| Parameter | Value |
|---|---|
| Polynomial | `0x31` (`x^8 + x^5 + x^4 + 1`) |
| Init | `0x00` |
| Reflect input | no |
| Reflect output | no |
| Final XOR | `0x00` |

The CRC is computed over **the body**: all bytes of fields 0–5
including their `|` separators, NOT including the `|` before
field 6, NOT including field 6 itself, NOT including `\n`.

Reference implementation (the one in `nano_bringup.ino`):

```c
static uint8_t crc8(const char *data, size_t len) {
  uint8_t crc = 0x00;
  for (size_t i = 0; i < len; i++) {
    crc ^= (uint8_t)data[i];
    for (uint8_t b = 0; b < 8; b++) {
      if (crc & 0x80) crc = (uint8_t)((crc << 1) ^ 0x31);
      else            crc = (uint8_t)(crc << 1);
    }
  }
  return crc;
}
```

Python reference (used by `tools/heartbeat_smoketest.py`):

```python
def crc8(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc
```

## 4. Frame examples

Power-on cold boot, third heartbeat, dirty build:

```
HKMK0|3050|3|01|1804|ee15859-dirty|7B
```

After a watchdog reset (note `mcusr=0x08`):

```
HKMK0|1050|1|08|1810|ee15859|A3
```

(CRCs are illustrative; verify with the reference implementation.)

## 5. Parser rules for hosts

1. Read one line. Strip trailing `\r\n` / `\n`.
2. If the line does not start with `HKMK0|`, treat it as a
   comment / banner / log line. Pass through to debug log.
3. Split on `|`. Expect exactly 7 fields.
4. Recompute CRC-8 over fields 0–5 joined by `|`. Compare against
   field 6 (parsed as hex). On mismatch: log + discard.
5. Verify `tick` is greater than the last seen `tick` from the
   same `buildid`. A non-monotonic `tick` with the same `buildid`
   means the chip reset (re-armed) — surface this prominently.
6. If `mcusr_hex & 0x0C` (BORF or WDRF), surface a session-level
   warning.

## 6. Future protocol versions

When the frame layout changes, bump the version tag (`HKMK0` →
`HKMK1`). Hosts should accept both during a transition window
and emit a deprecation warning when they see the older tag.

Pending features that may force a bump:

- Sprint 0.3a: add `state` field (OFF / ARMED / SESSION / FAULT)
- Sprint 0.4: add `sensors` block (INA219 V/I, DS18B20 °C)
- Sprint 0.4: Heltec V3 uses the same protocol but with its
  own tag (`HKHV3` for the V3 device)

Each bump gets a row in this section with the date and the
delta.
