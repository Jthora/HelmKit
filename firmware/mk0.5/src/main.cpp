// HelmKit Mk0.5 — main dispatcher.
//
// Wave F/G/H/I integration. Banner emits both a human-readable preamble
// and a structured kind:"hello" NDJSON line. Smoke test result drives a
// distinct LED pattern. Operator can re-run via single-char serial command
// ('r'), but safety-halts require the explicit 'R' (capital) escape so a
// reflexive retry cannot defeat the safety floor.

#include <Arduino.h>
#include <Preferences.h>

#include "board/adc_mutex.h"
#include "board/i2c_recover.h"
#include "board/pins.h"
#include "board/watchdog.h"
#include "drivers/battery.h"
#include "drivers/imu.h"
#include "drivers/max30102.h"
#include "drivers/max30205.h"
#include "drivers/mlx90614.h"
#include "drivers/gsr.h"
#include "drivers/smoke_fail.h"
#include "dsp/eda.h"
#include "dsp/fog.h"
#include "dsp/motion.h"
#include "dsp/r_peak.h"
#include "dsp/resp_thermal.h"
#include "layers/backoff.h"
#include "layers/degrade.h"
#include "layers/modes.h"
#include "layers/pacer.h"
#include "layers/power_policy.h"
#include "layers/session_store.h"
#include "ui/buttons.h"
#include "log/buffer.h"
#include "log/ndjson.h"
#include "log/session.h"
#include "ui/oled.h"
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

void persist_session();
void modes_cue_sink(const char* cue, void*) {
    helmkit::log::emit_cue(cue);
    if (strncmp(cue, "mode:", 5) == 0 || strncmp(cue, "summary:", 8) == 0) persist_session();   // Track N (N-F5)
}

// Track N phase 1 state (declared early: the sample callbacks use it).
helmkit::dsp::FogDetector     g_fog;          // N-S2: lens fogged -> q="gap"
helmkit::dsp::DonningCheck    g_donning;      // N-S2: three breaths within 30 s of session start
bool                          g_shed_raw = false;   // N-F7: raw streams shed under link pressure
float                         g_breaths_bpm = 0.0f;         // latest breathing rate for the OLED (phase 2)
uint32_t                      g_breaths_at_ms = 0;

void on_mlx_sample(const helmkit::drivers::Mlx90614Sample& s) {
    const bool fogged = g_fog.feed(s.t_ms, s.object_c, s.ambient_c);
    const char* q = fogged ? "gap" : (s.in_range ? "ok" : "out-of-range");
    if (!g_shed_raw) {
        helmkit::log::emit_temp_object_q(s.t_ms, s.object_c, s.ambient_c, q,
                                         g_thermal_on_nose ? "temp-nose" : "temp-forehead");
    }
    // Only good samples feed the extractor (the analyser uses q="ok" only).
    if (s.in_range && !fogged && g_resp.process(s.t_ms, s.object_c)) {
        g_donning.breath(s.t_ms);
        float bpm = 0.0f;
        if (g_resp.rate_bpm(s.t_ms, &bpm)) {
            helmkit::log::emit_resp_thermal(g_resp.last_breath_ms(), bpm);
            g_breaths_bpm = bpm;
            g_breaths_at_ms = s.t_ms;
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

helmkit::dsp::ScrDetector* g_scr_ptr = nullptr;   // set once the phase 2 block below is initialised (static init order)

void on_gsr_sample(const helmkit::drivers::GsrSample& s) {
    if (!g_shed_raw) {
        helmkit::log::emit_gsr_q(s.t_ms, s.raw, s.open ? "gap" : (s.in_range ? "ok" : "out-of-range"));
    }
    // N-S6: the SCR detector sees only q="ok" samples, like the host reference
    if (g_scr_ptr != nullptr && s.in_range && !s.open) {
        uint32_t tp = 0; float amp = 0.0f;
        if (g_scr_ptr->feed(s.t_ms, (float)s.raw, &tp, &amp)) helmkit::log::emit_num("scr", tp, amp, "ok");
    }
}

// ---- Track N phase 1: IMU, battery, buttons, session persistence ---------------
helmkit::drivers::Imu         g_imu;
bool                          g_imu_streaming = false;
helmkit::dsp::MotionDetector  g_motion;
int8_t                        g_still = -1;                 // latest `still` (-1 = no IMU stream)
float                         g_impact_pending = NAN;       // largest impact since the last mode tick
helmkit::drivers::Battery     g_batt;
helmkit::layers::PowerPolicy  g_power;
uint32_t                      g_last_batt_ms = 0;
bool                          g_low_batt = false;
float                         g_fake_vbat = NAN;            // HELMKIT_DEBUG 'V'
helmkit::layers::Degrade      g_degrade;
helmkit::ui::Button           g_btn_round, g_btn_prime, g_btn_tally;
helmkit::ui::Debounced        g_slide(20);
Preferences                   g_prefs;
helmkit::layers::SessionState g_session;
uint32_t                      g_confirm_end_ms = 0;         // 'M' once = confirm-end; again within 3 s = end
struct RrQ { uint32_t t; bool ok; };
RrQ                           g_rrq[32];                    // last RR intervals for the 10 s `ppg-q` window
uint8_t                       g_rrq_n = 0, g_rrq_head = 0;
uint32_t                      g_last_ppgq_ms = 0;
float                         g_ppgq_frac = 0.0f;

// ---- Track N phase 2: link buffer, OLED, MAX30205, EDA port ----------------------
helmkit::log::LinkBuffer      g_linkbuf;                    // N-L2: event lines parked on flash while the link is down
helmkit::drivers::Max30205    g_skin;                       // N-S5: temple / occipital contact temperature
bool                          g_skin_streaming = false;
helmkit::dsp::ScrDetector     g_scr;                        // N-S6: skin-conductance responses
helmkit::dsp::SlopeWindow     g_skin_slope(60000);          // N-S6: sweat rule input
bool                          g_have_skin = false;
uint32_t                      g_last_sweat_ms = 0;
bool                          g_oled = false;
uint32_t                      g_last_oled_ms = 0;

bool store_line(const char* line) { return g_linkbuf.store(line); }

void on_skin_sample(const helmkit::drivers::Max30205Sample& s) {
    g_have_skin = true;
    if (!g_shed_raw) {
        helmkit::log::emit_num(s.addr == helmkit::drivers::Max30205::kAddrL ? "temp-skin.L" : "temp-skin.R",
                               s.t_ms, s.temp_c, s.in_range ? "ok" : "out-of-range", helmkit::log::LineClass::kRaw);
    }
    // the sweat rule follows the left sensor, or the right one when only it answered
    if (s.in_range && (s.addr == helmkit::drivers::Max30205::kAddrL || !g_skin.present(0))) g_skin_slope.feed(s.t_ms, s.temp_c);
}

void on_imu_sample(const helmkit::drivers::ImuSample& s) {
    g_motion.feed(s.t_ms, s.ax, s.ay, s.az);
    helmkit::dsp::MotionEvent e;
    while (g_motion.pop(e)) {
        switch (e.kind) {
            case helmkit::dsp::MotionEvent::Kind::kStill:
                g_still = (int8_t)e.value;
                helmkit::log::emit_num("still", e.t_ms, e.value, "ok");
                break;
            case helmkit::dsp::MotionEvent::Kind::kImpact:
                if (isnan(g_impact_pending) || e.value > g_impact_pending) g_impact_pending = e.value;
                helmkit::log::emit_num("impact", e.t_ms, e.value, "ok");
                break;
            case helmkit::dsp::MotionEvent::Kind::kActivity:
                helmkit::log::emit_num("activity", e.t_ms, e.value, "ok");
                break;
            default: break;
        }
    }
}

void persist_session() {
    char buf[48];
    if (g_modes.in_session()) {
        g_session.valid      = true;
        if (g_session.session_id == 0) g_session.session_id = helmkit::log::boot_id();
        g_session.mode       = (uint8_t)g_modes.mode();
        g_session.tally      = g_modes.tally();
        g_session.uptime_ms  = millis();
        helmkit::layers::encode_session(g_session, buf, sizeof buf);
        g_prefs.putString("session", buf);
    } else {
        g_session = helmkit::layers::SessionState{};
        g_prefs.remove("session");
    }
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
StreamSupervisor g_sv_imu{"imu"};
StreamSupervisor g_sv_skin{"temp-skin"};
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

void ensure_ext_bus() {
    // Idempotent on the ESP32 driver; restores the bus after a fault-injection end() or a recovery.
    Wire1.begin(helmkit::pins::kExtI2cSda, helmkit::pins::kExtI2cScl, helmkit::pins::kExtI2cHz);
}

bool retry_skin() {
    ensure_ext_bus();
    recover_ext_bus_if_stuck();
    return g_skin.begin(Wire1);
}

bool retry_imu() {
    ensure_ext_bus();
    recover_ext_bus_if_stuck();
    if (!g_imu.begin(Wire1)) return false;
    g_motion.reset();
    return true;
}

bool retry_ppg() {
    ensure_ext_bus();
    recover_ext_bus_if_stuck();
    helmkit::drivers::Max30102Config cfg;
    cfg.sample_rate_hz = 100;
    cfg.sample_avg = 4;
    if (!g_ppg.begin(Wire1, cfg)) return false;
    g_rpeak.reset();
    return true;
}

bool retry_mlx() {
    ensure_ext_bus();
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
    supervise(g_sv_imu, g_imu_streaming, g_imu.health(), now, retry_imu);
    supervise(g_sv_skin, g_skin_streaming, g_skin.health(), now, retry_skin);
}

// ---- Track N phase 1: session start / end paths shared by keys and buttons ----
void stop_all_streams() {
    if (g_streaming) { g_streaming = false; g_ppg.shutdown(); }
    g_mlx_streaming = false;
    g_gsr_streaming = false;
    g_imu_streaming = false;
    g_skin_streaming = false;
}

// ---- Track N phase 2: OLED pages (N-U2) --------------------------------------------
char quality_glyph(bool streaming, helmkit::drivers::Health h, bool fogged = false) {
    using helmkit::drivers::Health;
    if (!streaming) return '-';
    if (fogged || h == Health::kGap) return 'G';
    if (h == Health::kOk || h == Health::kOutOfRange) return 'O';
    return 'B';
}

void refresh_oled(uint32_t now) {
    if (!g_oled) return;
    if (g_low_batt) {
        char v[20];
        snprintf(v, sizeof v, "%.2fV", (double)helmkit::drivers::battery_last().volts);
        helmkit::ui::oled_fault("LOW BATTERY", v, "SESSION ENDED");
        return;
    }
    if (g_last_was_safety_halt) { helmkit::ui::oled_fault("SAFETY HALT", "PRESS R", ""); return; }
    helmkit::ui::OledStatus st;
    st.mode       = g_modes.in_session() ? helmkit::layers::mode_str(g_modes.mode()) : "IDLE";
    st.tally      = g_modes.tally();
    st.in_session = g_modes.in_session();
    st.hr_bpm     = (g_hr_at_ms != 0 && (now - g_hr_at_ms) < 15000) ? g_hr_bpm : 0.0f;
    st.breaths    = (g_breaths_at_ms != 0 && (now - g_breaths_at_ms) < 30000) ? g_breaths_bpm : 0.0f;
    st.q_ppg      = quality_glyph(g_streaming, g_ppg.health());
    st.q_thermo   = quality_glyph(g_mlx_streaming, g_mlx.health(), g_fog.fogged());
    st.q_eda      = quality_glyph(g_gsr_streaming, g_gsr.health());
    st.q_imu      = quality_glyph(g_imu_streaming, g_imu.health());
    const auto& b = helmkit::drivers::battery_last();
    st.batt_known = b.volts > 2.5f;
    st.batt_pct   = b.percent;
    st.link       = !helmkit::log::serial_attached() ? "DOWN" : (g_linkbuf.has_pending() ? "BUF" : "UP");
    st.drops      = helmkit::log::link_stats().dropped();
    helmkit::ui::oled_status(st);
}

void start_session(const char* how) {
    if (g_last_was_safety_halt || g_low_batt) {
        Serial.printf("[main] session start (%s) refused: %s.\n", how, g_low_batt ? "battery low" : "safety halt; use 'R'");
        return;
    }
    if (g_modes.in_session()) { Serial.println(F("[main] modes session already running.")); return; }
    if (g_pacer.running()) g_pacer.suspend();            // the plain pacer hands over silently
    g_session = helmkit::layers::SessionState{};
    g_session.session_id = helmkit::log::boot_id();
    Serial.printf("[main] modes session start via %s (Tranquil, 6 bpm).\n", how);
    mode_cue("session-start", helmkit::layers::ModeCue::kSessionStart);
    if (g_mlx_streaming && g_thermal_on_nose) g_donning.start(millis());   // N-S2: three breaths in 30 s or a cue
}

void end_session(const char* how) {
    if (!g_modes.in_session()) { Serial.println(F("[main] no modes session.")); return; }
    g_donning.cancel();
    g_confirm_end_ms = 0;
    g_modes.event(millis(), helmkit::layers::ModeCue::kSessionEnd);   // emits summary:tally=N and clears the persisted state
    helmkit::log::emit_cue("session-end");
    if (g_pacer.running()) {
        g_pacer.suspend();
        helmkit::ui::status_led_set_intensity(0);
        helmkit::ui::status_led_set(helmkit::ui::Pattern::kIdle);
    }
    Serial.printf("[main] modes session end via %s.\n", how);
}

// N-U3: a serial 'M' needs a second 'M' within 3 s; the first emits confirm-end.
void request_end(uint32_t now) {
    if (!g_modes.in_session()) { Serial.println(F("[main] no modes session.")); return; }
    if (g_confirm_end_ms != 0 && (now - g_confirm_end_ms) < 3000) { end_session("key"); return; }
    g_confirm_end_ms = now;
    helmkit::log::emit_cue("confirm-end");
    Serial.println(F("[main] press 'M' again within 3 s to end the session."));
}

// N-U1: nape pod buttons. Every press is logged as `btn`; the mode machine ignores what makes no sense.
void handle_button(const char* name, helmkit::ui::Press p, uint32_t now) {
    const bool lng = (p == helmkit::ui::Press::kLong);
    char v[24];
    snprintf(v, sizeof v, "%s:%s", name, lng ? "long" : "short");
    helmkit::log::emit_str("btn", now, v);
    if (strcmp(name, "prime") == 0) {
        if (lng) { if (g_modes.in_session()) end_session("button"); else start_session("button"); }
        else       mode_cue("prime", helmkit::layers::ModeCue::kPrime);
    } else if (strcmp(name, "round") == 0) {
        if (g_modes.mode() == helmkit::layers::Mode::kCombatSustain) mode_cue("round-end", helmkit::layers::ModeCue::kRoundEnd);
        else                                                          mode_cue("round-start", helmkit::layers::ModeCue::kRoundStart);
    } else if (strcmp(name, "tally") == 0) {
        mode_cue("tally", helmkit::layers::ModeCue::kTally);
    }
}

void poll_buttons(uint32_t now) {
    const auto r = g_btn_round.feed(now, digitalRead(helmkit::pins::kBtnRound) == LOW);
    if (r != helmkit::ui::Press::kNone) handle_button("round", r, now);
    const auto p = g_btn_prime.feed(now, digitalRead(helmkit::pins::kBtnPrime) == LOW);
    if (p != helmkit::ui::Press::kNone) handle_button("prime", p, now);
    const auto t = g_btn_tally.feed(now, digitalRead(helmkit::pins::kBtnTally) == LOW);
    if (t != helmkit::ui::Press::kNone) handle_button("tally", t, now);
    const int sl = g_slide.feed(now, digitalRead(helmkit::pins::kSlideSanct) == LOW);
    if (sl != 0) {
        helmkit::log::emit_str("btn", now, sl > 0 ? "sanctuary:on" : "sanctuary:off");
        if (sl > 0) mode_cue("sanctuary", helmkit::layers::ModeCue::kSanctuary);
    }
}

// N-F3: 1 Hz battery read; low for 10 s ends the session cleanly and stops the streams.
void poll_battery(uint32_t now) {
    g_batt.pump();
    const float v = isnan(g_fake_vbat) ? helmkit::drivers::battery_last().volts : g_fake_vbat;
    if (g_power.feed(now, v)) {
        g_low_batt = true;
        helmkit::log::emit_cue("low-battery");
        helmkit::log::emit_health("vbat", "ok", "low", 0, "session ended, streams stopped");
        if (g_modes.in_session()) end_session("low battery");
        if (g_pacer.running()) g_pacer.stop(now);
        stop_all_streams();
        helmkit::ui::status_led_set_intensity(0);
        helmkit::ui::status_led_set(helmkit::ui::Pattern::kFail);
    } else if (g_low_batt && !g_power.low()) {
        g_low_batt = false;
        helmkit::log::emit_health("vbat", "low", "ok", 0, "recovered");
        helmkit::ui::status_led_set(helmkit::ui::Pattern::kIdle);
    }
}

// N-S1: 10 s window quality for the PPG-derived heart rate.
void note_rr_quality(const helmkit::dsp::Peak& p) {
    g_rrq[g_rrq_head] = RrQ{p.t_ms, p.in_range};
    g_rrq_head = (uint8_t)((g_rrq_head + 1) % 32);
    if (g_rrq_n < 32) ++g_rrq_n;
}

void emit_ppg_quality(uint32_t now) {
    uint8_t n = 0, ok = 0;
    for (uint8_t i = 0; i < g_rrq_n; ++i) {
        if ((now - g_rrq[i].t) <= 10000) { ++n; if (g_rrq[i].ok) ++ok; }
    }
    const float frac = n ? (float)ok / (float)n : 0.0f;
    g_ppgq_frac = frac;
    helmkit::log::emit_num("ppg-q", now, frac, n == 0 ? "gap" : (frac >= 0.8f ? "ok" : "low"));
    // N-S6: the single-source half of the host fusion rule: HR is reported only from a
    // high-quality window (>= 80 % in-range beats) and a fresh estimate; withheld otherwise.
    const bool fresh = (g_hr_at_ms != 0 && (now - g_hr_at_ms) < 15000);
    if (fresh && frac >= 0.8f) helmkit::log::emit_num("hr", now, g_hr_bpm, "ok");
    else                       helmkit::log::emit_num("hr", now, 0.0f, "gap");
}

// N-F5: resume a persisted session after an involuntary reset.
void restore_session_if_any(uint32_t now) {
    String saved = g_prefs.getString("session", "");
    helmkit::layers::SessionState st;
    if (!helmkit::layers::decode_session(saved.c_str(), st)) return;
    char note[64];
    if (helmkit::layers::should_resume(st, helmkit::board::reset_reason_str())) {
        g_session = st;
        g_modes.restore(now, st.tally);
        apply_mode_pacer(now);
        snprintf(note, sizeof note, "resumed id=%016llx tally=%lu after %s", (unsigned long long)st.session_id,
                 (unsigned long)st.tally, helmkit::board::reset_reason_str());
        helmkit::log::emit_health("session", "lost", "resumed", 0, note);
        helmkit::log::emit_cue("session-resumed");
    } else {
        g_prefs.remove("session");
        snprintf(note, sizeof note, "discarded id=%016llx after %s", (unsigned long long)st.session_id,
                 helmkit::board::reset_reason_str());
        helmkit::log::emit_health("session", "saved", "discarded", 0, note);
    }
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
            case 'm': start_session("key"); break;
            case 'M': request_end(millis()); break;
            case 'a': {
                // Track N (N-S4): IMU stream -> still / impact / activity.
                if (g_last_was_safety_halt) { Serial.println(F("[main] 'a' refused after safety halt; use 'R' first.")); break; }
                if (g_imu_streaming) { Serial.println(F("[main] IMU stream already running.")); break; }
                ensure_ext_bus();
                if (!g_imu.begin(Wire1)) {
                    Serial.println(F("[main] IMU begin FAILED (no chip on 0x68/0x69/0x6A/0x6B)."));
                    helmkit::log::emit_error("mk0.5", helmkit::drivers::SmokeFail::kNoAck, "imu-begin-failed", 0, 0,
                                             helmkit::drivers::Health::kNoAck);
                    break;
                }
                const auto st = g_imu.self_test();
                helmkit::log::emit_smoke_result("imu", st);
                Serial.printf("[main] IMU %s @0x%02x self-test: %s\n", g_imu.chip_name(), g_imu.addr(), st.ok ? "PASS" : "FAIL");
                g_motion.reset();
                g_still = -1;
                g_imu_streaming = true;
                break;
            }
            case 'c': {
                // Track N (N-S5): MAX30205 contact temperature stream (temp-skin.L / .R).
                if (g_last_was_safety_halt) { Serial.println(F("[main] 'c' refused after safety halt; use 'R' first.")); break; }
                if (g_skin_streaming) { Serial.println(F("[main] skin-temp stream already running.")); break; }
                ensure_ext_bus();
                if (!g_skin.begin(Wire1)) {
                    Serial.println(F("[main] MAX30205 begin FAILED (no ACK on 0x48 / 0x49)."));
                    helmkit::log::emit_error("mk0.5", helmkit::drivers::SmokeFail::kNoAck, "max30205-begin-failed", 0, 0,
                                             helmkit::drivers::Health::kNoAck);
                    break;
                }
                g_skin_slope.reset();
                g_skin_streaming = true;
                Serial.printf("[main] skin-temp stream started (%u device(s)).\n", (unsigned)g_skin.devices());
                break;
            }
            case 'C':
                if (!g_skin_streaming) { Serial.println(F("[main] skin-temp stream not running.")); break; }
                g_skin_streaming = false;
                Serial.println(F("[main] skin-temp stream stopped."));
                break;
            case '~':
                helmkit::log::note_ack(millis());       // N-L3: the capture service acknowledges a heartbeat
                break;
            case 'A':
                if (!g_imu_streaming) { Serial.println(F("[main] IMU stream not running.")); break; }
                g_imu_streaming = false;
                g_still = -1;
                Serial.println(F("[main] IMU stream stopped."));
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
            case 'K':
                // N-T3: kill the external I²C bus. Expected: the streams go no-ack, health
                // lines follow, and the supervisor re-begins them on the backoff schedule.
                Serial.println(F("[main] DEBUG: ending Wire1 (bus fault injection)."));
                Wire1.end();
                break;
            case 'F':
                // N-T3: flood the TX ring. Expected: drops counted on the next hb; raw streams shed.
                Serial.println(F("[main] DEBUG: flooding the TX ring with 300 lines."));
                for (int i = 0; i < 300; ++i) helmkit::log::emit_num("dbg", millis(), (float)i, "ok", helmkit::log::LineClass::kRaw);
                break;
            case 'V':
                // N-T3: fake a 3.3 V pack. Expected: low-battery cue after 10 s, session ended, streams stopped.
                g_fake_vbat = isnan(g_fake_vbat) ? 3.3f : NAN;
                Serial.printf("[main] DEBUG: fake vbat %s.\n", isnan(g_fake_vbat) ? "off" : "3.3 V");
                break;
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
    Serial.println(F(" Track N phase 1: a/A=imu stream (still, impact, activity)  M twice within 3 s ends a session  "
                     "buttons on GPIO 26/33/34, slide 40  vbat every 5 s, low battery ends the session"));
    Serial.println(F(" Track N phase 2: c/C=skin-temp stream (MAX30205)  '~'=host ack (buffers events to flash after 10 s "
                     "without one, replays on return)  hr / scr / sweat lines  OLED status page"));
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
    // Track N phase 1: buttons (pull-ups; the planned pins are off the strapping set), battery, persisted session.
    pinMode(helmkit::pins::kBtnRound,   INPUT_PULLUP);
    pinMode(helmkit::pins::kBtnPrime,   INPUT_PULLUP);
    pinMode(helmkit::pins::kBtnTally,   INPUT_PULLUP);
    pinMode(helmkit::pins::kSlideSanct, INPUT_PULLUP);
    g_batt.begin();
    g_prefs.begin("helmkit", false);
    // Track N phase 2: the link buffer (N-L2) and the OLED (N-U2); both optional at runtime.
    if (g_linkbuf.begin()) {
        helmkit::log::set_store(store_line);
        char note[48];
        snprintf(note, sizeof note, "link buffer ready, %lu B pending", (unsigned long)g_linkbuf.bytes());
        helmkit::log::emit_health("linkbuf", "off", "ready", 0, note);
    } else {
        helmkit::log::emit_health("linkbuf", "off", "unavailable", 0, "LittleFS mount failed: events will drop while the link is down");
    }
    g_oled = helmkit::ui::oled_begin();
    helmkit::log::emit_health("oled", "off", g_oled ? "ready" : "absent", 0, g_oled ? "SSD1306 on bus 0" : "no ACK on 0x3C");
    g_scr_ptr = &g_scr;
    run_smoke();
    restore_session_if_any(millis());
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
            note_rr_quality(p);
        }
        if ((now - g_last_ppgq_ms) >= 10000) { g_last_ppgq_ms = now; emit_ppg_quality(now); }   // N-S1
    }
    if (g_imu_streaming) {
        g_imu.pump(on_imu_sample);                  // ~100 Hz; events drained inside
    }
    if (g_skin_streaming) {
        g_skin.pump(on_skin_sample);                // 5 Hz per device
    }
    if (g_linkbuf.has_pending() && helmkit::log::link_healthy(now)) {
        g_linkbuf.replay(20, helmkit::log::emit_stored);   // N-L2: bounded per loop so nothing stalls
    }
    if (g_have_skin && (now - g_last_sweat_ms) >= 10000) {     // N-S6: sweat rule every 10 s
        g_last_sweat_ms = now;
        float sl = 0.0f;
        if (g_skin_slope.slope(&sl)) helmkit::log::emit_num("sweat", now, helmkit::dsp::sweat_rule(sl) ? 1.0f : 0.0f, "ok");
    }
    if ((now - g_last_oled_ms) >= 1000) {           // N-U2
        g_last_oled_ms = now;
        refresh_oled(now);
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
        g_modes.tick(now, hr, g_imu_streaming ? g_still : (int8_t)-1, g_impact_pending);
        g_impact_pending = NAN;
        apply_mode_pacer(now);
        const auto dr = g_donning.poll(now);        // N-S2
        if (dr == helmkit::dsp::DonningCheck::Result::kFail) helmkit::log::emit_cue("check-nose-sensor");
    }
    if ((now - g_last_batt_ms) >= 1000) {           // N-F3
        g_last_batt_ms = now;
        poll_battery(now);
    }
    poll_buttons(now);                              // N-U1
    if ((now - g_last_hb_ms) >= 5000) {                 // Track N (N-L1)
        g_last_hb_ms = now;
        helmkit::log::emit_hb(now, ESP.getFreeHeap(), (uint32_t)g_linkbuf.bytes());
        const auto& b = helmkit::drivers::battery_last();
        helmkit::log::emit_vbat(now, helmkit::drivers::battery_last_raw(), b.volts, b.percent);
        const bool shed = g_degrade.feed(now, helmkit::log::link_stats().dropped());   // N-F7
        if (shed != g_shed_raw) {
            helmkit::log::emit_health("link", g_shed_raw ? "shed" : "ok", shed ? "shed" : "ok", 0,
                                      shed ? "raw streams shed: link dropping lines" : "raw streams restored");
            g_shed_raw = shed;
        }
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
