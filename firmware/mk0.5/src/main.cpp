// HelmKit Mk0.5 — main dispatcher.
//
// Wave F/G/H/I integration. Banner emits both a human-readable preamble
// and a structured kind:"hello" NDJSON line. Smoke test result drives a
// distinct LED pattern. Operator can re-run via single-char serial command
// ('r'), but safety-halts require the explicit 'R' (capital) escape so a
// reflexive retry cannot defeat the safety floor.

#include <Arduino.h>

#include "board/adc_mutex.h"
#include "board/pins.h"
#include "drivers/max30102.h"
#include "drivers/smoke_fail.h"
#include "dsp/r_peak.h"
#include "layers/pacer.h"
#include "log/ndjson.h"
#include "log/session.h"
#include "ui/status_led.h"

namespace {

helmkit::drivers::SmokeResult g_last_result{};
bool                          g_last_was_safety_halt = false;
helmkit::layers::Pacer        g_pacer;

// Wave J: persistent PPG instance and R-peak detector for streaming mode.
// Smoke test (above) still uses its own scoped Max30102 — it exercises a
// full begin/destroy cycle on every retry, which is part of the gate.
// The streaming instance below is initialised lazily on first 'g' command
// and torn down on 'x'.
helmkit::drivers::Max30102    g_ppg;
helmkit::dsp::RPeakDetector   g_rpeak;
bool                          g_streaming = false;

void on_ppg_sample(const helmkit::drivers::Max30102Sample& s) {
    // Driver emits gap-quality samples when finger is removed; feed the
    // detector regardless — its high-pass + adaptive threshold absorb the
    // discontinuity. If finger-off persists, no peaks will cross threshold.
    g_rpeak.process(s.t_ms, s.ir);
}

void run_smoke() {
    helmkit::ui::status_led_set(helmkit::ui::Pattern::kTesting);
    Serial.println(F("[main] starting MAX30102 smoke..."));
    helmkit::log::emit_error(
        "mk0.5", helmkit::drivers::SmokeFail::kNone,
        "smoke-start", 0, 0, helmkit::drivers::Health::kOk);
    // Note: emit_error with kNone is being used as a "trace" event here.
    // Wave 2 may split this into a dedicated kind:"trace" emitter.

    g_last_result = helmkit::drivers::max30102_smoke_test();
    helmkit::log::emit_smoke_result("ppg-hrv", g_last_result);

    Serial.print(F("[main] L0 MAX30102 gate: "));
    Serial.println(g_last_result.ok ? F("PASS") : F("FAIL"));

    helmkit::ui::status_led_set(g_last_result.ok
        ? helmkit::ui::Pattern::kPass
        : helmkit::ui::Pattern::kFail);
}

void poll_serial_commands() {
    while (Serial.available() > 0) {
        const int c = Serial.read();
        switch (c) {
            case 'r':
                if (g_last_was_safety_halt) {
                    Serial.println(F("[main] 'r' refused: last halt was a "
                                     "safety halt; use 'R' (capital) to "
                                     "force-acknowledge."));
                    helmkit::log::emit_error(
                        "mk0.5",
                        helmkit::drivers::SmokeFail::kStimSafetyHalt,
                        "retry-refused-after-safety-halt", 0, 0,
                        helmkit::drivers::Health::kError);
                } else {
                    Serial.println(F("[main] re-running smoke..."));
                    run_smoke();
                }
                break;
            case 'R':
                Serial.println(F("[main] safety-halt acknowledged by operator; "
                                 "re-running smoke."));
                g_last_was_safety_halt = false;
                run_smoke();
                break;
            case '?':
                helmkit::log::emit_smoke_result("ppg-hrv", g_last_result);
                break;
            case 'h':
                helmkit::log::emit_hello();
                break;
            case 'p':
                if (g_last_was_safety_halt) {
                    Serial.println(F("[main] 'p' refused after safety halt; "
                                     "use 'R' first."));
                    break;
                }
                if (g_pacer.running()) {
                    Serial.println(F("[main] pacer already running."));
                    break;
                }
                Serial.println(F("[main] starting L0 pacer (6 bpm)."));
                helmkit::ui::status_led_set(
                    helmkit::ui::Pattern::kPacing);
                g_pacer.start(millis());
                break;
            case 's':
                if (!g_pacer.running()) {
                    Serial.println(F("[main] pacer not running."));
                    break;
                }
                Serial.println(F("[main] stopping L0 pacer."));
                g_pacer.stop(millis());
                helmkit::ui::status_led_set_intensity(0);
                helmkit::ui::status_led_set(
                    helmkit::ui::Pattern::kIdle);
                break;
            case 'g': {
                if (g_last_was_safety_halt) {
                    Serial.println(F("[main] 'g' refused after safety halt; "
                                     "use 'R' first."));
                    break;
                }
                if (g_streaming) {
                    Serial.println(F("[main] PPG stream already running."));
                    break;
                }
                // Wave J: enter PPG streaming mode. Reuses the Wire1 bus
                // that the smoke test already initialised.
                helmkit::drivers::Max30102Config cfg;
                cfg.sample_rate_hz = 100;
                cfg.sample_avg = 4;
                if (!g_ppg.begin(Wire1, cfg)) {
                    Serial.println(F("[main] PPG stream begin FAILED."));
                    helmkit::log::emit_error(
                        "mk0.5",
                        helmkit::drivers::SmokeFail::kNoAck,
                        "ppg-stream-begin-failed", 0, 0,
                        helmkit::drivers::Health::kError);
                    break;
                }
                g_rpeak.reset();
                g_streaming = true;
                Serial.println(F("[main] PPG stream started; emitting ppg-rr."));
                break;
            }
            case 'x':
                if (!g_streaming) {
                    Serial.println(F("[main] PPG stream not running."));
                    break;
                }
                g_streaming = false;
                g_ppg.shutdown();
                Serial.println(F("[main] PPG stream stopped."));
                break;
            case '\n':
            case '\r':
            case ' ':
                break;
            default:
                Serial.printf("[main] unknown cmd '%c' (try: r R ? h p s g x)\n",
                              (char)c);
                break;
        }
    }
}

void prose_banner() {
    Serial.println();
    Serial.println(F("===================================================="));
    Serial.println(F(" HelmKit Mk0.5  --  Heltec WiFi LoRa 32 V3"));
    Serial.print  (F(" build: "));
    Serial.print  (F(__DATE__));
    Serial.print  (F(" "));
    Serial.println(F(__TIME__));
    Serial.println(F(" commands: r=retry  R=force-retry-after-safety-halt  "
                     "?=last-result  h=hello  p=pacer-start  s=pacer-stop  "
                     "g=ppg-stream-start  x=ppg-stream-stop"));
    Serial.println(F("===================================================="));
}

}  // namespace

void setup() {
    helmkit::ui::status_led_begin(helmkit::pins::kStatusLed);
    helmkit::ui::status_led_set(helmkit::ui::Pattern::kBoot);

    Serial.begin(115200);
    // Give USB-CDC a moment to attach so the banner isn't lost.
    const uint32_t t0 = millis();
    while (!Serial && (millis() - t0) < 2000) {
        helmkit::ui::status_led_pump();
    }
    helmkit::log::init();

    prose_banner();
    helmkit::log::emit_hello();

    // Eager ADC1 mutex init (Wave I / R6). If this fails, every downstream
    // ADC consumer would get mutex-timeouts forever; surface the OS-layer
    // failure with a distinct code.
    if (!helmkit::board::adc1_init()) {
        helmkit::log::emit_error(
            "board",
            helmkit::drivers::SmokeFail::kHeapExhausted,
            "adc1 mutex create failed",
            0, 0, helmkit::drivers::Health::kError);
        helmkit::ui::status_led_set(helmkit::ui::Pattern::kSafetyHalt);
        g_last_was_safety_halt = true;
        // Fall through into loop(); the safety pattern + emitted error are
        // the witness artifacts.
    }

    helmkit::ui::status_led_set(helmkit::ui::Pattern::kIdle);
    g_pacer.begin();
    run_smoke();
}

void loop() {
    const uint32_t now = millis();
    if (g_pacer.running()) {
        g_pacer.tick(now);
        helmkit::ui::status_led_set_intensity(g_pacer.intensity_u8(now));
    }
    if (g_streaming) {
        // Pump driver, then drain any peaks the detector accumulated this
        // tick. Bounded loop — RPeakDetector FIFO is 8 deep; at 100 Hz with
        // a 10 ms loop period we expect 0 or 1 peaks per tick.
        g_ppg.pump(on_ppg_sample);
        while (g_rpeak.has_peak()) {
            const auto p = g_rpeak.consume_peak();
            helmkit::log::emit_ppg_rr(p.t_ms, p.rr_ms,
                                      p.in_range, p.confidence);
        }
    }
    helmkit::ui::status_led_pump();
    poll_serial_commands();
    delay(10);
}
