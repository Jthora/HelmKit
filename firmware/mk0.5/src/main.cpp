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
#include "drivers/mlx90614.h"
#include "drivers/gsr.h"
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

// Wave J Bridge B: MLX90614 forehead-temp streaming. Smoke runs at boot
// after PPG; streaming is opt-in via 't' so log volume stays bounded.
helmkit::drivers::Mlx90614    g_mlx;
bool                          g_mlx_streaming = false;

void on_mlx_sample(const helmkit::drivers::Mlx90614Sample& s) {
    helmkit::log::emit_temp_forehead(s.t_ms, s.object_c, s.ambient_c, s.in_range);
}

// Wave J Bridge B: GSR analog streaming. Smoke runs at boot after MLX;
// streaming is opt-in via 'e' (electrodermal). 50 Hz cadence keeps log
// volume bounded.
helmkit::drivers::Gsr         g_gsr;
bool                          g_gsr_streaming = false;

void on_gsr_sample(const helmkit::drivers::GsrSample& s) {
    helmkit::log::emit_gsr(s.t_ms, s.raw, s.in_range);
}

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

    // Wave J Bridge B: MLX90614 smoke runs after PPG so Wire1 is already up.
    Serial.println(F("[main] starting MLX90614 smoke..."));
    const auto mlx_result = helmkit::drivers::mlx90614_smoke_test();
    helmkit::log::emit_smoke_result("temp-forehead", mlx_result);
    Serial.print(F("[main] L0 MLX90614 gate: "));
    Serial.println(mlx_result.ok ? F("PASS") : F("FAIL"));

    // Wave J Bridge B: GSR smoke. Pure ADC1, no I²C — independent of Wire1
    // state. ADC1 mutex was already initialised at the top of setup().
    Serial.println(F("[main] starting GSR smoke..."));
    const auto gsr_result = helmkit::drivers::gsr_smoke_test();
    helmkit::log::emit_smoke_result("gsr", gsr_result);
    Serial.print(F("[main] L0 GSR gate: "));
    Serial.println(gsr_result.ok ? F("PASS") : F("FAIL"));

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
            case 't': {
                // Wave J Bridge B: start MLX90614 forehead-temp stream.
                if (g_last_was_safety_halt) {
                    Serial.println(F("[main] 't' refused after safety halt; "
                                     "use 'R' first."));
                    break;
                }
                if (g_mlx_streaming) {
                    Serial.println(F("[main] MLX stream already running."));
                    break;
                }
                helmkit::drivers::Mlx90614Config cfg;
                cfg.period_ms = 250;   // SCHEMA §2.2 = 4 Hz
                if (!g_mlx.begin(Wire1, cfg)) {
                    Serial.println(F("[main] MLX stream begin FAILED."));
                    helmkit::log::emit_error(
                        "mk0.5",
                        helmkit::drivers::SmokeFail::kNoAck,
                        "mlx-stream-begin-failed", 0, 0,
                        helmkit::drivers::Health::kError);
                    break;
                }
                g_mlx_streaming = true;
                Serial.println(F("[main] MLX stream started; emitting temp-forehead."));
                break;
            }
            case 'T':
                if (!g_mlx_streaming) {
                    Serial.println(F("[main] MLX stream not running."));
                    break;
                }
                g_mlx_streaming = false;
                Serial.println(F("[main] MLX stream stopped."));
                break;
            case 'e': {
                // Wave J Bridge B: start GSR electrodermal stream.
                if (g_last_was_safety_halt) {
                    Serial.println(F("[main] 'e' refused after safety halt; "
                                     "use 'R' first."));
                    break;
                }
                if (g_gsr_streaming) {
                    Serial.println(F("[main] GSR stream already running."));
                    break;
                }
                helmkit::drivers::GsrConfig cfg;
                cfg.period_ms      = 20;   // SCHEMA §2.2 = 50 Hz
                cfg.adc_timeout_ms = 5;
                if (!g_gsr.begin(cfg)) {
                    Serial.println(F("[main] GSR stream begin FAILED."));
                    helmkit::log::emit_error(
                        "mk0.5",
                        helmkit::drivers::SmokeFail::kBeginFailed,
                        "gsr-stream-begin-failed", 0, 0,
                        helmkit::drivers::Health::kError);
                    break;
                }
                g_gsr_streaming = true;
                Serial.println(F("[main] GSR stream started; emitting gsr."));
                break;
            }
            case 'E':
                if (!g_gsr_streaming) {
                    Serial.println(F("[main] GSR stream not running."));
                    break;
                }
                g_gsr_streaming = false;
                Serial.println(F("[main] GSR stream stopped."));
                break;
            case '\n':
            case '\r':
            case ' ':
                break;
            default:
                Serial.printf("[main] unknown cmd '%c' (try: r R ? h p s g x t T e E)\n",
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
                     "g=ppg-stream-start  x=ppg-stream-stop  "
                     "t=temp-stream-start  T=temp-stream-stop  "
                     "e=gsr-stream-start  E=gsr-stream-stop"));
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
    if (g_mlx_streaming) {
        // 4 Hz — driver self-throttles; pumping every tick is cheap.
        g_mlx.pump(on_mlx_sample);
    }
    if (g_gsr_streaming) {
        // 50 Hz — driver self-throttles + holds ADC1 mutex briefly.
        g_gsr.pump(on_gsr_sample);
    }
    helmkit::ui::status_led_pump();
    poll_serial_commands();
    delay(10);
}
