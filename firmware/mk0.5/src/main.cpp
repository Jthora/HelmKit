// HelmKit Mk0.5 — main dispatcher.
//
// Wave F/G/H/I integration. Banner emits both a human-readable preamble
// and a structured kind:"hello" NDJSON line. Smoke test result drives a
// distinct LED pattern. Operator can re-run via single-char serial command
// ('r'), but safety-halts require the explicit 'R' (capital) escape so a
// reflexive retry cannot defeat the safety floor.

#include <Arduino.h>

#include "board/adc_mutex.h"
#include "board/i2c_recover.h"
#include "board/pins.h"
#include "board/watchdog.h"
#include "drivers/max30102.h"
#include "drivers/mlx90614.h"
#include "drivers/gsr.h"
#include "drivers/smoke_fail.h"
#include "dsp/r_peak.h"
#include "dsp/resp_thermal.h"
#include "layers/backoff.h"
#include "layers/modes.h"
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

// Track M (2026-09-11): thermal respiration on the MLX stream and the
// combat-mode state machine. No IMU at Mk0.5: stillness is unknown (-1), so
// Recover ends on its 90 s timeout and no resting HR is learned yet.
helmkit::dsp::RespThermal     g_resp;
helmkit::layers::CombatModes  g_modes;
bool                          g_thermal_on_nose = false;   // 'N': temp-forehead (Mk0.5 wiring) <-> temp-nose (sensor bar)
float                         g_hr_bpm = NAN;              // 60000 / median of the last 5 in-range RR
uint32_t                      g_hr_at_ms = 0;
uint16_t                      g_rr_hist[5] = {0, 0, 0, 0, 0};
uint8_t                       g_rr_n = 0;
uint8_t                       g_rr_head = 0;
uint32_t                      g_last_mode_tick_ms = 0;

void modes_cue_sink(const char* cue, void*) { helmkit::log::emit_cue(cue); }

void on_mlx_sample(const helmkit::drivers::Mlx90614Sample& s) {
    helmkit::log::emit_temp_object(s.t_ms, s.object_c, s.ambient_c, s.in_range,
                                   g_thermal_on_nose ? "temp-nose" : "temp-forehead");
    // Only in-range samples feed the extractor (the analyser uses q="ok" only).
    if (s.in_range && g_resp.process(s.t_ms, s.object_c)) {
        float bpm = 0.0f;
        if (g_resp.rate_bpm(s.t_ms, &bpm)) {
            helmkit::log::emit_resp_thermal(g_resp.last_breath_ms(), bpm);
        }
    }
}

void note_rr(const helmkit::dsp::Peak& p) {
    if (!p.in_range || p.rr_ms == 0) return;
    g_rr_hist[g_rr_head] = p.rr_ms;
    g_rr_head = (uint8_t)((g_rr_head + 1) % 5);
    if (g_rr_n < 5) ++g_rr_n;
    if (g_rr_n < 3) return;
    uint16_t v[5];
    for (uint8_t i = 0; i < g_rr_n; ++i) v[i] = g_rr_hist[i];
    for (uint8_t i = 1; i < g_rr_n; ++i) {            // insertion sort, n <= 5
        const uint16_t x = v[i];
        int8_t j = (int8_t)i - 1;
        while (j >= 0 && v[j] > x) { v[j + 1] = v[j]; --j; }
        v[j + 1] = x;
    }
    g_hr_bpm = 60000.0f / (float)v[g_rr_n / 2];
    g_hr_at_ms = p.t_ms;
}

// Apply the current mode's pacer shape to the L0 pacer without session cues
// (the modes session owns session-start / session-end).
void apply_mode_pacer(uint32_t now) {
    if (!g_modes.in_session()) return;
    const auto cfg = g_modes.pacer();
    if (!cfg.enabled) {
        if (g_pacer.running()) {
            g_pacer.suspend();
            helmkit::ui::status_led_set_intensity(0);
            helmkit::ui::status_led_set(helmkit::ui::Pattern::kIdle);
        }
        return;
    }
    if (!g_pacer.running()) {
        g_pacer.retune(cfg.inhale_ms, cfg.exhale_ms, now);
        g_pacer.resume(now);
    } else if (g_pacer.inhale_ms() != cfg.inhale_ms || g_pacer.exhale_ms() != cfg.exhale_ms) {
        g_pacer.retune(cfg.inhale_ms, cfg.exhale_ms, now);
    }
}

// Operator cue -> wire + state machine + pacer, in that order so the log
// shows the cause before the mode change it produced.
void mode_cue(const char* wire_value, helmkit::layers::ModeCue cue) {
    const uint32_t now = millis();
    helmkit::log::emit_cue(wire_value);
    g_modes.event(now, cue);
    apply_mode_pacer(now);
}

// Wave J Bridge B: GSR analog streaming. Smoke runs at boot after MLX;
// streaming is opt-in via 'e' (electrodermal). 50 Hz cadence keeps log
// volume bounded.
helmkit::drivers::Gsr         g_gsr;
bool                          g_gsr_streaming = false;

void on_gsr_sample(const helmkit::drivers::GsrSample& s) {
    helmkit::log::emit_gsr(s.t_ms, s.raw, s.in_range);
}

// ---- Track N (N-F4 / N-L1): stream supervisor and heartbeat -----------------
//
// Driver health used to be sticky until the operator re-ran the smoke test.
// Each streaming driver now has a supervisor record: every health transition
// is logged, and a sticky fault (no-ack / overflow / error) on a stream the
// operator wants running triggers re-begin attempts on the Backoff schedule
// (5, 10, 20, then 60 s). Before an I²C re-begin the bus is recovered if a
// slave is holding SDA. Gap <-> ok flapping is rate-limited to one line per
// 2 s per stream so a finger lifting on and off cannot flood the log.
struct StreamSupervisor {
    const char*               source;
    helmkit::layers::Backoff  bo;
    helmkit::drivers::Health  last = helmkit::drivers::Health::kUninit;
    uint32_t                  last_flap_ms = 0;
};
StreamSupervisor g_sv_ppg{"ppg-hrv"};
StreamSupervisor g_sv_mlx{"temp"};
StreamSupervisor g_sv_gsr{"gsr"};
uint32_t         g_last_sv_ms = 0;
uint32_t         g_last_hb_ms = 0;
bool             g_wdt_ok     = false;

bool sticky_fault(helmkit::drivers::Health h) {
    using helmkit::drivers::Health;
    return h == Health::kNoAck || h == Health::kOverflow || h == Health::kError;
}

bool soft_state(helmkit::drivers::Health h) {
    using helmkit::drivers::Health;
    return h == Health::kOk || h == Health::kGap || h == Health::kOutOfRange;
}

void recover_ext_bus_if_stuck() {
    if (!helmkit::board::i2c_bus_stuck(helmkit::pins::kExtI2cSda)) return;
    const bool ok = helmkit::board::i2c_bus_recover(Wire1, helmkit::pins::kExtI2cSda,
                                                    helmkit::pins::kExtI2cScl, helmkit::pins::kExtI2cHz);
    helmkit::log::emit_health("i2c1", "stuck", ok ? "released" : "stuck", 0, "9-clock bus recovery");
}

template <typename Retry>
void supervise(StreamSupervisor& s, bool wanted, helmkit::drivers::Health h, uint32_t now, Retry retry) {
    using helmkit::drivers::health_str;
    if (h != s.last) {
        const bool flap = soft_state(h) && soft_state(s.last);
        if (!flap || (now - s.last_flap_ms) >= 2000) {
            helmkit::log::emit_health(s.source, health_str(s.last), health_str(h), s.bo.attempts(),
                                      sticky_fault(h) ? "fault" : "");
            if (flap) s.last_flap_ms = now;
        }
        s.last = h;
    }
    if (!wanted) { s.bo.succeed(); return; }          // operator stopped it: nothing to retry
    if (!sticky_fault(h)) { s.bo.succeed(); return; }
    if (!s.bo.armed()) { s.bo.arm(now); return; }     // first retry 5 s after the fault
    if (!s.bo.due(now)) return;
    if (retry()) {
        helmkit::log::emit_health(s.source, health_str(h), "ok", (uint16_t)(s.bo.attempts() + 1), "re-begin ok");
        s.last = helmkit::drivers::Health::kOk;
        s.bo.succeed();
    } else {
        s.bo.fail(now);
        char note[40];
        snprintf(note, sizeof note, "re-begin failed; next in %lus", (unsigned long)(s.bo.step_ms() / 1000));
        helmkit::log::emit_health(s.source, health_str(h), health_str(h), s.bo.attempts(), note);
    }
}

bool retry_ppg() {
    recover_ext_bus_if_stuck();
    helmkit::drivers::Max30102Config cfg;
    cfg.sample_rate_hz = 100;
    cfg.sample_avg = 4;
    if (!g_ppg.begin(Wire1, cfg)) return false;
    g_rpeak.reset();
    return true;
}

bool retry_mlx() {
    recover_ext_bus_if_stuck();
    helmkit::drivers::Mlx90614Config cfg;
    cfg.period_ms = 250;
    return g_mlx.begin(Wire1, cfg);
}

bool retry_gsr() {
    helmkit::drivers::GsrConfig cfg;
    cfg.period_ms      = 20;
    cfg.adc_timeout_ms = 5;
    return g_gsr.begin(cfg);
}

void supervise_all(uint32_t now) {
    supervise(g_sv_ppg, g_streaming,     g_ppg.health(), now, retry_ppg);
    supervise(g_sv_mlx, g_mlx_streaming, g_mlx.health(), now, retry_mlx);
    supervise(g_sv_gsr, g_gsr_streaming, g_gsr.health(), now, retry_gsr);
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
            // ---- Track M combat modes (layers/modes.h). 'm' opens a session that
            // owns the pacer; 'p'/'s' are the plain L0 pacer and should not be
            // mixed with it.
            case 'm':
                if (g_last_was_safety_halt) {
                    Serial.println(F("[main] 'm' refused after safety halt; use 'R' first."));
                    break;
                }
                if (g_modes.in_session()) {
                    Serial.println(F("[main] modes session already running."));
                    break;
                }
                if (g_pacer.running()) {
                    g_pacer.suspend();          // the plain pacer hands over silently
                }
                Serial.println(F("[main] modes session start (Tranquil, 6 bpm)."));
                mode_cue("session-start", helmkit::layers::ModeCue::kSessionStart);
                break;
            case 'M':
                if (!g_modes.in_session()) {
                    Serial.println(F("[main] no modes session."));
                    break;
                }
                g_modes.event(millis(), helmkit::layers::ModeCue::kSessionEnd);   // emits summary:tally=N
                helmkit::log::emit_cue("session-end");
                if (g_pacer.running()) {
                    g_pacer.suspend();
                    helmkit::ui::status_led_set_intensity(0);
                    helmkit::ui::status_led_set(helmkit::ui::Pattern::kIdle);
                }
                Serial.println(F("[main] modes session end."));
                break;
            case 'b': mode_cue("round-start", helmkit::layers::ModeCue::kRoundStart); break;
            case 'B': mode_cue("round-end",   helmkit::layers::ModeCue::kRoundEnd);   break;
            case 'i': mode_cue("prime",       helmkit::layers::ModeCue::kPrime);      break;
            case 'n': mode_cue("sanctuary",   helmkit::layers::ModeCue::kSanctuary);  break;
            case 'y': mode_cue("tally",       helmkit::layers::ModeCue::kTally);      break;
            case 'N':
                g_thermal_on_nose = !g_thermal_on_nose;
                g_resp.reset();
                Serial.print(F("[main] thermopile channel: "));
                Serial.println(g_thermal_on_nose ? F("temp-nose (sensor bar)") : F("temp-forehead (Mk0.5 wiring)"));
                break;
#ifdef HELMKIT_DEBUG
            case 'W':
                // Track N fault injection: spin without feeding the watchdog.
                // Expected: reset within 5 s and a boot line with reason task-wdt.
                Serial.println(F("[main] DEBUG: spinning for the task watchdog..."));
                for (;;) { }
#endif
            case '\n':
            case '\r':
            case ' ':
                break;
            default:
                Serial.printf("[main] unknown cmd '%c' (try: r R ? h p s g x t T e E m M b B i n y N)\n",
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
    Serial.println(F(" combat modes (Track M): m=session-start  M=session-end  b=round-start  "
                     "B=round-end  i=prime  n=sanctuary  y=tally  N=thermopile forehead<->nose"));
    Serial.println(F(" every line carries n (sequence); hb every 5 s; health lines on driver transitions; "
                     "faulted streams re-begin at 5/10/20/60 s (Track N)"));
    Serial.println(F("===================================================="));
}

}  // namespace

void setup() {
    helmkit::ui::status_led_begin(helmkit::pins::kStatusLed);
    helmkit::ui::status_led_set(helmkit::ui::Pattern::kBoot);

    // Track N (N-F1): a 4 KB TX ring so a burst (a temp pair plus an RR line)
    // does not overflow the default 256 B ring while the host is between polls.
    Serial.setTxBufferSize(4096);
    Serial.begin(115200);
    // Give USB-CDC a moment to attach so the banner isn't lost.
    const uint32_t t0 = millis();
    while (!Serial && (millis() - t0) < 2000) {
        helmkit::ui::status_led_pump();
    }
    helmkit::log::init();

    prose_banner();
    helmkit::log::emit_hello();
    // Track N (N-F2 / N-F6): why this boot happened, then the loop task joins
    // the 5 s task watchdog (the smoke loops feed it themselves).
    g_wdt_ok = helmkit::board::wdt_begin(5);
    helmkit::log::emit_boot(helmkit::board::reset_reason_str(), helmkit::board::reset_reason_num(), g_wdt_ok);

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
    g_modes.set_emitter(modes_cue_sink, nullptr);
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
            note_rr(p);
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
    if (g_modes.in_session() && (now - g_last_mode_tick_ms) >= 1000) {
        // Track M: 1 Hz mode tick. HR older than 15 s (PPG stream off or
        // finger-off) counts as unknown; no IMU at Mk0.5 -> still = -1.
        g_last_mode_tick_ms = now;
        const float hr = (g_hr_at_ms != 0 && (now - g_hr_at_ms) < 15000) ? g_hr_bpm : NAN;
        g_modes.tick(now, hr, -1, NAN);
        apply_mode_pacer(now);
    }
    if ((now - g_last_hb_ms) >= 5000) {                 // Track N (N-L1)
        g_last_hb_ms = now;
        helmkit::log::emit_hb(now, ESP.getFreeHeap());
    }
    if ((now - g_last_sv_ms) >= 1000) {                 // Track N (N-F4)
        g_last_sv_ms = now;
        supervise_all(now);
    }
    helmkit::board::wdt_feed();                         // Track N (N-F6)
    helmkit::ui::status_led_pump();
    poll_serial_commands();
    delay(10);
}
