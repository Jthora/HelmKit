/*
 * HelmKit Mk0 — sprint 0.3 firmware bring-up (HARDENING PASS)
 * Target: Arduino Nano v3 (ATmega328P, 16 MHz)
 * Role:   B-PWR safety MCU (per docs/sprint_0.2_circuit_spec.md §3.3.2)
 *
 * This file implements the FOUR-BELT safety model declared in
 * firmware/SAFETY.md. Even at bring-up, the kill relay K1 must
 * stay de-energized through any single fault:
 *
 *   Belt 1 — explicit:    K1_DRIVE (D3) initialized OUTPUT LOW
 *                         before setup() returns. Bring-up never
 *                         raises it. See §6.5.5.
 *   Belt 2 — implicit:    All other §3.3.2 platform pins set to
 *                         INPUT_PULLUP so stray bridges read HIGH
 *                         instead of glitching outputs.
 *   Belt 3 — temporal:    Watchdog timer enabled at 2 s. Any hang
 *                         >2 s resets to belt 1's safe state.
 *   Belt 4 — observable:  MCUSR is read and reported at every
 *                         boot. We know whether the last reset
 *                         was WDT / BOD / external / power-on.
 *
 * Banned in this file (and across firmware/):
 *   - String class       (heap fragmentation)
 *   - malloc/free        (heap on a safety MCU is forbidden)
 *   - float in ISR       (slow, non-deterministic)
 *   - delay() in loop    (blocks WDT pet path; allowed only in setup)
 *
 * Acceptance for sprint 0.3 (phase 2 — hardening):
 *   - Compiles clean with `arduino-cli compile`
 *   - WDT enabled at boot (verify by inserting a 3 s busy-loop;
 *     chip should reset and report WDRF in the MCUSR snapshot)
 *   - K1_DRIVE (D3) measured LOW from setup() onward
 *   - Structured heartbeat frame on Serial @ 115200 (see PROTOCOL.md)
 *   - tools/heartbeat_smoketest.py exits 0 against live serial
 */

#include <Arduino.h>
#include <avr/wdt.h>

// ---- build identity ----------------------------------------------------
// BUILD_ID is injected at compile time via -DBUILD_ID="<hash>" from the
// build script. If absent (e.g. raw arduino-cli compile without the
// wrapper), fall back to "dev" so the firmware still names itself.
#ifndef BUILD_ID
#define BUILD_ID "dev"
#endif
#define FW_PROTO_VERSION "HKMK0"

// ---- pin map (mirrors docs/sprint_0.2_circuit_spec.md §3.3.2) ----------
// Bring-up firmware uses NONE of these pins functionally. They are
// declared here so setup() can drive them to their fail-safe state
// (belt 1 + belt 2). When sprint 0.3a wires K1_DRIVE_PIN HIGH inside
// the safety state machine, that line MUST cite §6.5.5 in a comment.
static const uint8_t LED_PIN        = LED_BUILTIN;  // D13, on-board LED
static const uint8_t K1_DRIVE_PIN   = 3;            // D3, K1 relay coil (§6.5.5)
static const uint8_t SAFETY_N_PIN   = 2;            // D2, SAFETY_n bus (§3.3.2)
static const uint8_t BUZZER_PIN     = 4;            // D4, audible alarm (§7 row 5)
static const uint8_t LED_RED_PIN    = 5;            // D5, HV/coil-armed (§5.6)
static const uint8_t LED_AMBER_PIN  = 6;            // D6, watchdog-OK (§5.6)
static const uint8_t LED_GREEN_PIN  = 7;            // D7, session-active (§5.6)
static const uint8_t FAN_DRIVE_PIN  = 8;            // D8, Mk0.5 fan (§5.9.3)
// A4 = SDA, A5 = SCL — Wire owns them when initialized. Not init'd here.

// ---- heartbeat protocol (see firmware/PROTOCOL.md) ---------------------
// Frame:  HKMK0|<ms>|<tick>|<mcusr_hex>|<freeram>|<buildid>|<crc8>\n
//
// All fields ASCII, '|' separated, terminated by '\n'. CRC-8 is computed
// over the body (everything before the final '|<crc8>') with the
// Dallas/Maxim polynomial 0x31, init 0x00, no reflection. Two-hex-char
// uppercase output. Sprint 0.5 Pi 4 host validates the frame.
static const unsigned long HEARTBEAT_PERIOD_MS  = 1000;
static const unsigned long BLINK_HALF_PERIOD_MS = 500;   // 1 Hz blink
static const uint8_t       WDT_TIMEOUT_CODE     = WDTO_2S;

// ---- module state ------------------------------------------------------
static uint8_t        g_mcusr_snapshot = 0;
static unsigned long  g_last_blink_ms  = 0;
static unsigned long  g_last_beat_ms   = 0;
static unsigned long  g_tick           = 0;
static bool           g_led_state      = false;

// ---- helpers -----------------------------------------------------------

// Free-RAM estimate on AVR: gap between heap top and current stack
// pointer. Returns a conservative byte count. Safe to call from main
// context; not safe from ISR.
static int freeRamBytes() {
  extern int __heap_start;
  extern int *__brkval;
  int v;
  return (int)&v - (__brkval == 0 ? (int)&__heap_start : (int)__brkval);
}

// Dallas/Maxim CRC-8, polynomial 0x31, init 0x00. Suitable for short
// ASCII frames. Constant-time per byte, no table (saves ~256 B flash).
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

// Drive every §3.3.2 platform pin to its documented fail-safe state.
// This is belt 1 (K1 explicit) + belt 2 (everything else high-Z'd via
// INPUT_PULLUP). Called from setup() AND safe to call again from any
// future FAULT handler.
static void enforceFailSafePins() {
  // Belt 1 — K1 relay coil driver: OUTPUT LOW. Kill switch de-energized.
  // §6.5.5: K1 is FAIL-OPEN; LOW on the driver = coil de-energized =
  // 12V_RAIL contacts open = downstream loads disconnected.
  pinMode(K1_DRIVE_PIN, OUTPUT);
  digitalWrite(K1_DRIVE_PIN, LOW);

  // Belt 2 — every other platform-bus pin set INPUT_PULLUP. A stray
  // solder bridge or probe touch reads HIGH, never glitches an output.
  pinMode(SAFETY_N_PIN,   INPUT_PULLUP);  // bus signal, read-only here
  pinMode(BUZZER_PIN,     INPUT_PULLUP);  // §7 — not driven at bring-up
  pinMode(LED_RED_PIN,    INPUT_PULLUP);  // §5.6 — sprint 0.3a wires these
  pinMode(LED_AMBER_PIN,  INPUT_PULLUP);
  pinMode(LED_GREEN_PIN,  INPUT_PULLUP);
  pinMode(FAN_DRIVE_PIN,  INPUT_PULLUP);  // §5.9.3 — Mk0.5 deferral

  // The on-board LED is the ONLY pin this sketch drives functionally.
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}

// Emit one heartbeat frame. Single call site so the format is enforced
// in one place. Sized buffer; snprintf-truncation-safe.
static void emitHeartbeat() {
  char body[80];
  int n = snprintf(body, sizeof(body),
                   FW_PROTO_VERSION "|%lu|%lu|%02X|%d|%s",
                   (unsigned long)millis(),
                   (unsigned long)g_tick,
                   (unsigned)g_mcusr_snapshot,
                   freeRamBytes(),
                   BUILD_ID);
  if (n <= 0 || n >= (int)sizeof(body)) {
    // Truncation or error — emit a minimal frame so the host parser
    // still sees something (and flags it as malformed via CRC).
    Serial.println(F("HKMK0|err|truncated|||00"));
    return;
  }
  uint8_t c = crc8(body, (size_t)n);
  Serial.print(body);
  Serial.print('|');
  if (c < 0x10) Serial.print('0');
  Serial.println(c, HEX);
}

// ---- watchdog --------------------------------------------------------

// Capture MCUSR as early as possible (gcc .init3 hook, before main()).
// The Optiboot bootloader on a stock Nano clears the WDT enable bit
// before jumping to the application but leaves MCUSR flags intact for
// one read. We snapshot then clear so the next reset reports cleanly.
//
// Belt 4 — observability. Without this, a hung-then-WDT-reset chip
// looks identical to a power-on chip. With this, we know.
void earlyInit() __attribute__((naked, used, section(".init3")));
void earlyInit() {
  g_mcusr_snapshot = MCUSR;
  MCUSR = 0;
  wdt_disable();
}

static inline void wdtPet() { wdt_reset(); }

static void wdtArm() {
  wdt_enable(WDT_TIMEOUT_CODE);
  wdt_reset();
}

// ---- setup / loop ----------------------------------------------------

void setup() {
  // First: pins to fail-safe. Before serial, before WDT, before anything
  // else that could fault. Belt 1 + Belt 2.
  enforceFailSafePins();

  // Then: arm the watchdog. From here on, hanging code resets us. Belt 3.
  wdtArm();

  // Serial last (its buffer setup takes a few ms).
  Serial.begin(115200);
  // delay() allowed in setup per the banned-API list (forbidden only in
  // loop). 100 ms gives the host USB-CDC stack time to enumerate so
  // the first frame isn't lost.
  delay(100);
  wdtPet();

  // Boot banner — human-readable comment lines, NOT heartbeat frames.
  // Host parser ignores any line that doesn't start with FW_PROTO_VERSION '|'.
  Serial.println();
  Serial.print(F("# helmkit-mk0 nano boot build="));
  Serial.print(F(BUILD_ID));
  Serial.print(F(" mcusr=0x"));
  if (g_mcusr_snapshot < 0x10) Serial.print('0');
  Serial.print(g_mcusr_snapshot, HEX);
  Serial.print(F(" ("));
  if (g_mcusr_snapshot & _BV(WDRF))  Serial.print(F("WDT "));
  if (g_mcusr_snapshot & _BV(BORF))  Serial.print(F("BOD "));
  if (g_mcusr_snapshot & _BV(EXTRF)) Serial.print(F("EXT "));
  if (g_mcusr_snapshot & _BV(PORF))  Serial.print(F("POR "));
  Serial.println(F(")"));
  Serial.print(F("# F_CPU="));
  Serial.print((unsigned long)F_CPU);
  Serial.print(F(" Hz  freeRam="));
  Serial.print(freeRamBytes());
  Serial.println(F(" B"));
  Serial.println(F("# protocol=" FW_PROTO_VERSION " (see firmware/PROTOCOL.md)"));

  // Initialize timing so the first heartbeat lands promptly.
  g_last_blink_ms = millis();
  g_last_beat_ms  = millis() - HEARTBEAT_PERIOD_MS + 50;
  wdtPet();
}

void loop() {
  // Pet first thing every iteration. The watchdog only catches hangs
  // INSIDE the body; the body itself must always reach this line.
  wdtPet();

  const unsigned long now = millis();
  // Note: millis() unsigned-wraps at ~49.7 days. The subtractions below
  // are unsigned and wraparound-correct by C arithmetic rules. This is
  // INTENTIONAL — do not "fix" by switching to signed or by adding
  // explicit wrap handling.

  if ((unsigned long)(now - g_last_blink_ms) >= BLINK_HALF_PERIOD_MS) {
    g_last_blink_ms = now;
    g_led_state = !g_led_state;
    digitalWrite(LED_PIN, g_led_state ? HIGH : LOW);
  }

  if ((unsigned long)(now - g_last_beat_ms) >= HEARTBEAT_PERIOD_MS) {
    g_last_beat_ms = now;
    g_tick++;
    emitHeartbeat();
  }

  // No delay() here. Loop spins at ~tens of kHz; WDT pet path is always
  // reached. If a future change introduces a blocking call, the WDT
  // (belt 3) will catch it within WDT_TIMEOUT_CODE.
}
