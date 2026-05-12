/*
 * HelmKit Mk0 — sprint 0.3 firmware bring-up
 * Target: Arduino Nano v3 (ATmega328P, 16 MHz)
 * Role:   B-PWR safety MCU (per docs/sprint_0.2_circuit_spec.md §3.3.2)
 *
 * This is the "prove the chip wakes up" sketch for sprint 0.3.
 * It does NOT yet implement the safety state machine (§6.5.5) or
 * the SAFETY_n watchdog. It only:
 *
 *   1. Blinks the on-board LED (D13) at 1 Hz.
 *   2. Emits a heartbeat string on Serial @ 115200 baud so we
 *      can verify the USB-serial path is alive end-to-end.
 *
 * Acceptance for sprint 0.3 DoD:
 *   - Compiles clean with `arduino-cli compile`
 *   - Flashes to a physical Nano (or verified via simavr / wokwi if
 *     no Nano is on the bench yet)
 *   - On-board LED blinks at ~1 Hz
 *   - `arduino-cli monitor -p <port> -c baudrate=115200` shows
 *     "helmkit-mk0 nano alive tick=N" once per second
 *
 * NOTHING in this sketch touches any of the §3.3.2 platform pins
 * (D2 SAFETY_n, D3 K1, etc.). Those are sprint 0.3a (Stabilizer
 * firmware + safety state machine). This sketch is bring-up only.
 */

const uint8_t LED_PIN = LED_BUILTIN;  // D13 on Nano v3
const unsigned long BLINK_HALF_PERIOD_MS = 500;  // 1 Hz blink

unsigned long g_last_toggle_ms = 0;
unsigned long g_tick = 0;
bool g_led_state = false;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(115200);
  // Give the USB-CDC bridge a moment; the CH340/FT232 on a Nano
  // does NOT need this but it doesn't hurt and keeps the first
  // line of output deterministic.
  delay(100);

  Serial.println(F("helmkit-mk0 nano boot"));
  Serial.println(F("sprint 0.3 firmware bring-up — blink + heartbeat"));
  Serial.print(F("F_CPU="));
  Serial.print(F_CPU);
  Serial.println(F(" Hz"));
}

void loop() {
  const unsigned long now = millis();
  if (now - g_last_toggle_ms >= BLINK_HALF_PERIOD_MS) {
    g_last_toggle_ms = now;
    g_led_state = !g_led_state;
    digitalWrite(LED_PIN, g_led_state ? HIGH : LOW);

    // Emit heartbeat on the rising edge only (once per full
    // second, not twice).
    if (g_led_state) {
      g_tick++;
      Serial.print(F("helmkit-mk0 nano alive tick="));
      Serial.println(g_tick);
    }
  }
}
