// HelmKit Mk0.5 — native unit tests for the Arduino-free Track M modules.
//
//   pio test -e native
//
// RespThermal and CombatModes have Python behavioural specs in
// tools/analyze_combat_session.py; these tests use the same synthetic session
// shapes and tolerances as tests/test_analyze_combat_session.py, so a change
// that breaks one side shows up on the other.

#include <math.h>
#include <stdint.h>
#include <string.h>

#include <unity.h>
#include <string>
#include <vector>

#include "dsp/resp_thermal.h"
#include "layers/modes.h"

using helmkit::dsp::RespThermal;
using helmkit::layers::CombatModes;
using helmkit::layers::Mode;
using helmkit::layers::ModeCue;

namespace {

// Deterministic noise (LCG) so the test is bit-repeatable across hosts.
struct Lcg {
    uint32_t s;
    float next_pm(float amp) {           // uniform in [-amp, amp]
        s = s * 1664525u + 1013904223u;
        return amp * (((float)(s >> 8) / 16777216.0f) * 2.0f - 1.0f);
    }
};

// Nose-tip temperature at 4 Hz: base + slope + breathing sinusoid + noise.
void feed_thermal(RespThermal& r, uint32_t t0_ms, float seconds, float breaths_per_min, float slope_c_per_min, float amp_c, Lcg& rnd) {
    const int n = (int)(seconds * 4.0f);
    for (int i = 0; i < n; ++i) {
        const float t = i / 4.0f;
        const float v = 33.0f + slope_c_per_min * t / 60.0f +
                        amp_c * sinf(2.0f * 3.14159265f * breaths_per_min / 60.0f * t) + rnd.next_pm(0.01f);
        r.process(t0_ms + (uint32_t)(t * 1000.0f), v);
    }
}

void test_resp_rate_rest_12bpm() {
    RespThermal r;
    Lcg rnd{7};
    feed_thermal(r, 1000, 90.0f, 12.0f, 0.0f, 0.15f, rnd);
    float bpm = 0.0f;
    TEST_ASSERT_TRUE(r.rate_bpm(1000 + 90000, &bpm));
    TEST_ASSERT_FLOAT_WITHIN(2.0f, 12.0f, bpm);
    TEST_ASSERT_UINT32_WITHIN(3, 18, r.breaths());       // 12 / min * 90 s = 18
}

void test_resp_rate_round_30bpm_and_arousal_slope() {
    RespThermal r;
    Lcg rnd{11};
    feed_thermal(r, 60000, 120.0f, 30.0f, -0.3f, 0.15f, rnd);
    float bpm = 0.0f, slope = 0.0f;
    TEST_ASSERT_TRUE(r.rate_bpm(60000 + 120000, &bpm));
    TEST_ASSERT_FLOAT_WITHIN(3.0f, 30.0f, bpm);
    TEST_ASSERT_TRUE(r.slope_c_per_min(60000 + 120000, &slope));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, -0.3f, slope);          // nose tip cooling = arousal
}

void test_resp_no_rate_before_two_breaths_and_refractory() {
    RespThermal r;
    float bpm = 0.0f;
    TEST_ASSERT_FALSE(r.rate_bpm(5000, &bpm));
    Lcg rnd{3};
    // 90 breaths / min is above the 60 / min refractory ceiling: the detector must not exceed it
    feed_thermal(r, 0, 60.0f, 90.0f, 0.0f, 0.15f, rnd);
    TEST_ASSERT_TRUE(r.rate_bpm(60000, &bpm));
    TEST_ASSERT_TRUE(bpm <= 61.0f);
}

void test_resp_flat_signal_no_breaths() {
    RespThermal r;
    for (int i = 0; i < 400; ++i) r.process(i * 250, 33.0f);
    TEST_ASSERT_EQUAL_UINT32(0, r.breaths());
}

// ---- modes ---------------------------------------------------------------

struct CueLog {
    char     last[64];
    uint32_t count;
    char     all[1024];
};

void cue_sink(const char* cue, void* user) {
    auto* log = static_cast<CueLog*>(user);
    strncpy(log->last, cue, sizeof log->last - 1);
    log->last[sizeof log->last - 1] = 0;
    ++log->count;
    if (strlen(log->all) + strlen(cue) + 2 < sizeof log->all) {
        strcat(log->all, cue);
        strcat(log->all, "|");
    }
}

void test_modes_session_flow() {
    CombatModes m;
    CueLog log{};
    m.set_emitter(cue_sink, &log);
    TEST_ASSERT_EQUAL(Mode::kNone, m.mode());
    TEST_ASSERT_FALSE(m.pacer().enabled);

    m.event(0, ModeCue::kSessionStart);
    TEST_ASSERT_EQUAL(Mode::kTranquil, m.mode());
    TEST_ASSERT_EQUAL_STRING("mode:tranquil", log.last);
    TEST_ASSERT_TRUE(m.pacer().enabled);
    TEST_ASSERT_EQUAL_UINT32(4000, m.pacer().inhale_ms);
    TEST_ASSERT_EQUAL_UINT32(6000, m.pacer().exhale_ms);

    for (uint32_t t = 1; t < 30; ++t) m.tick(t * 1000, 64.0f + (float)(t % 3), 1, nanf(""));
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 64.0f, m.resting_hr());

    m.event(30000, ModeCue::kPrime);
    TEST_ASSERT_EQUAL_STRING("prime", m.pacer().pattern);
    TEST_ASSERT_EQUAL_UINT32(2000, m.pacer().inhale_ms);

    m.event(60000, ModeCue::kRoundStart);
    TEST_ASSERT_EQUAL(Mode::kCombatSustain, m.mode());
    TEST_ASSERT_FALSE(m.pacer().enabled);

    m.tick(90000, 150.0f, 0, 14.0f);
    TEST_ASSERT_EQUAL_STRING("impact:14g", log.last);
    m.tick(91000, 150.0f, 0, 6.0f);                          // below the 10 g cue threshold
    TEST_ASSERT_EQUAL_STRING("impact:14g", log.last);

    m.event(100000, ModeCue::kTally);
    TEST_ASSERT_EQUAL_UINT32(1, m.tally());
    TEST_ASSERT_EQUAL_STRING("tally-ack", log.last);

    m.event(180000, ModeCue::kRoundEnd);
    TEST_ASSERT_EQUAL(Mode::kRecover, m.mode());
    TEST_ASSERT_EQUAL_STRING("cyclic-sigh", m.pacer().pattern);
    m.tick(200000, 120.0f, 1, nanf(""));
    TEST_ASSERT_EQUAL(Mode::kRecover, m.mode());               // not yet within 20 bpm of resting
    m.tick(230000, 82.0f, 1, nanf(""));
    TEST_ASSERT_EQUAL(Mode::kTranquil, m.mode());               // recovered

    m.event(300000, ModeCue::kSessionEnd);
    TEST_ASSERT_EQUAL(Mode::kNone, m.mode());
    TEST_ASSERT_EQUAL_STRING("summary:tally=1", log.last);
    TEST_ASSERT_NOT_NULL(strstr(log.all, "mode:tranquil|mode:combat-prime|mode:combat-sustain|impact:14g|tally-ack|mode:recover|mode:tranquil|summary:tally=1|"));
}

void test_modes_timeouts() {
    CombatModes m;
    m.event(0, ModeCue::kSessionStart);
    m.event(10000, ModeCue::kPrime);
    m.tick(69000, nanf(""), -1, nanf(""));
    TEST_ASSERT_EQUAL(Mode::kCombatPrime, m.mode());
    m.tick(70000, nanf(""), -1, nanf(""));
    TEST_ASSERT_EQUAL(Mode::kTranquil, m.mode());
    m.event(100000, ModeCue::kRoundStart);
    m.event(200000, ModeCue::kRoundEnd);
    m.tick(289000, 140.0f, -1, nanf(""));
    TEST_ASSERT_EQUAL(Mode::kRecover, m.mode());
    m.tick(290000, 140.0f, -1, nanf(""));
    TEST_ASSERT_EQUAL(Mode::kTranquil, m.mode());                // no IMU, resting HR never learned: the 90 s timeout ends Recover
}

void test_modes_ignore_events_outside_session() {
    CombatModes m;
    m.event(5000, ModeCue::kRoundStart);
    TEST_ASSERT_EQUAL(Mode::kNone, m.mode());
    m.event(6000, ModeCue::kSessionStart);
    m.event(7000, ModeCue::kSanctuary);
    TEST_ASSERT_EQUAL(Mode::kSanctuary, m.mode());
    TEST_ASSERT_EQUAL_STRING("resonance", m.pacer().pattern);
}

void test_modes_millis_wrap() {
    CombatModes m;
    const uint32_t near_wrap = 0xFFFFFFFFu - 5000u;
    m.event(near_wrap, ModeCue::kSessionStart);
    m.event(near_wrap + 1000u, ModeCue::kRoundStart);
    m.event(near_wrap + 2000u, ModeCue::kRoundEnd);           // Recover entered 3 s before wrap
    m.tick(near_wrap + 2000u + CombatModes::kRecoverMs - 1000u, nanf(""), -1, nanf(""));
    TEST_ASSERT_EQUAL(Mode::kRecover, m.mode());
    m.tick(near_wrap + 2000u + CombatModes::kRecoverMs, nanf(""), -1, nanf(""));
    TEST_ASSERT_EQUAL(Mode::kTranquil, m.mode());
}

}  // namespace

// ---- Track N: pure pieces of the writer and the retry schedule -------------

#include "layers/backoff.h"
#include "log/line.h"

void test_line_append_seq_before_closing_brace() {
    char buf[64] = "{\"t\":1.000,\"ch\":\"cue\",\"v\":\"x\"}";
    TEST_ASSERT_TRUE(helmkit::log::append_seq(buf, sizeof buf, 42));
    TEST_ASSERT_EQUAL_STRING("{\"t\":1.000,\"ch\":\"cue\",\"v\":\"x\",\"n\":42}", buf);
    // not a closed object: untouched
    char open_obj[64] = "{\"t\":1.0";
    TEST_ASSERT_FALSE(helmkit::log::append_seq(open_obj, sizeof open_obj, 1));
    TEST_ASSERT_EQUAL_STRING("{\"t\":1.0", open_obj);
    // no room: untouched
    char tight[12] = "{\"a\":1}";
    TEST_ASSERT_FALSE(helmkit::log::append_seq(tight, sizeof tight, 4294967295u));
    TEST_ASSERT_EQUAL_STRING("{\"a\":1}", tight);
    // exactly enough room for the largest sequence number
    char fit[8 + 15 + 1] = "{\"a\":1}";
    TEST_ASSERT_TRUE(helmkit::log::append_seq(fit, sizeof fit, 4294967295u));
    TEST_ASSERT_EQUAL_STRING("{\"a\":1,\"n\":4294967295}", fit);
}

void test_link_stats_count_by_class_and_link() {
    helmkit::log::LinkStats st;
    st.note(helmkit::log::LineClass::kEvent, true, true);
    st.note(helmkit::log::LineClass::kRaw, false, true);     // buffer full
    st.note(helmkit::log::LineClass::kEvent, false, false);  // link down
    st.note(helmkit::log::LineClass::kRaw, false, false);    // link down
    TEST_ASSERT_EQUAL_UINT32(1, st.written);
    TEST_ASSERT_EQUAL_UINT32(2, st.dropped_raw);
    TEST_ASSERT_EQUAL_UINT32(1, st.dropped_event);
    TEST_ASSERT_EQUAL_UINT32(2, st.link_down);
    TEST_ASSERT_EQUAL_UINT32(3, st.dropped());
    TEST_ASSERT_FALSE(st.link);
}

void test_backoff_schedule_5_10_20_60() {
    helmkit::layers::Backoff bo;
    TEST_ASSERT_FALSE(bo.armed());
    TEST_ASSERT_FALSE(bo.due(0));
    bo.arm(1000);
    TEST_ASSERT_TRUE(bo.armed());
    TEST_ASSERT_FALSE(bo.due(5999));
    TEST_ASSERT_TRUE(bo.due(6000));                 // 5 s after the fault
    bo.fail(6000);
    TEST_ASSERT_EQUAL_UINT16(1, bo.attempts());
    TEST_ASSERT_EQUAL_UINT32(16000, bo.next_ms());   // +10 s
    bo.fail(16000);
    TEST_ASSERT_EQUAL_UINT32(36000, bo.next_ms());   // +20 s
    bo.fail(36000);
    TEST_ASSERT_EQUAL_UINT32(96000, bo.next_ms());   // +60 s
    bo.fail(96000);
    TEST_ASSERT_EQUAL_UINT32(156000, bo.next_ms());  // stays at 60 s
    TEST_ASSERT_EQUAL_UINT16(4, bo.attempts());
    bo.succeed();
    TEST_ASSERT_FALSE(bo.armed());
    TEST_ASSERT_EQUAL_UINT16(0, bo.attempts());
    bo.arm(200000);
    TEST_ASSERT_EQUAL_UINT32(205000, bo.next_ms()); // schedule restarts from 5 s
    bo.arm(300000);                                  // arming twice does not move it
    TEST_ASSERT_EQUAL_UINT32(205000, bo.next_ms());
}

void test_backoff_millis_wrap() {
    helmkit::layers::Backoff bo;
    const uint32_t near_wrap = 0xFFFFFFFFu - 2000u;
    bo.arm(near_wrap);                               // due at near_wrap + 5000 (wraps)
    TEST_ASSERT_FALSE(bo.due(near_wrap + 4999u));
    TEST_ASSERT_TRUE(bo.due(near_wrap + 5000u));     // 2999 after the wrap
    TEST_ASSERT_TRUE(bo.due(near_wrap + 7000u));
}

// ---- Track N phase 1: motion, buttons, power, degrade, fog, session store ---

#include "dsp/fog.h"
#include "dsp/motion.h"
#include "layers/degrade.h"
#include "layers/power_policy.h"
#include "layers/session_store.h"
#include "ui/buttons.h"

// feed `seconds` of 100 Hz accelerometer data: gravity on z plus `noise_g` alternating jitter
static void feed_accel(helmkit::dsp::MotionDetector& m, uint32_t& t, float seconds, float noise_g) {
    const int n = (int)(seconds * 100.0f);
    for (int i = 0; i < n; ++i, t += 10) {
        const float j = (i & 1) ? noise_g : -noise_g;
        m.feed(t, j, 0.0f, 1.0f + j);
    }
}

void test_motion_still_vs_moving() {
    helmkit::dsp::MotionDetector m;
    uint32_t t = 1000;
    feed_accel(m, t, 3.1f, 0.01f);                  // resting head: ~0.01 g jitter; 3.1 s closes three 1 s bins
    helmkit::dsp::MotionEvent e;
    int stills = 0, last = -1;
    while (m.pop(e)) if (e.kind == helmkit::dsp::MotionEvent::Kind::kStill) { ++stills; last = (int)e.value; }
    TEST_ASSERT_EQUAL_INT(3, stills);               // one per second
    TEST_ASSERT_EQUAL_INT(1, last);
    TEST_ASSERT_EQUAL_INT(1, m.last_still());
    feed_accel(m, t, 3.1f, 0.3f);                   // shadowboxing: 0.3 g jitter
    last = -1;
    while (m.pop(e)) if (e.kind == helmkit::dsp::MotionEvent::Kind::kStill) last = (int)e.value;
    TEST_ASSERT_EQUAL_INT(0, last);
    TEST_ASSERT_EQUAL_UINT32(0, m.clips());
}

void test_motion_impact_peak_and_refractory() {
    helmkit::dsp::MotionDetector m;
    uint32_t t = 0;
    feed_accel(m, t, 1.0f, 0.01f);
    // a hit: 12 g then 14 g then 6 g within 30 ms, a second crossing 100 ms later must not count
    m.feed(t, 0.0f, 0.0f, 13.0f); t += 10;          // dyn 12
    m.feed(t, 0.0f, 0.0f, 15.0f); t += 10;          // dyn 14 (peak)
    m.feed(t, 0.0f, 0.0f, 7.0f);  t += 10;
    for (int i = 0; i < 7; ++i, t += 10) m.feed(t, 0.0f, 0.0f, 1.0f);
    m.feed(t, 0.0f, 0.0f, 12.0f); t += 10;          // 100 ms after the first: inside the 200 ms window
    feed_accel(m, t, 0.5f, 0.01f);                  // window closes -> one event
    helmkit::dsp::MotionEvent e;
    int impacts = 0; float peak = 0.0f;
    while (m.pop(e)) if (e.kind == helmkit::dsp::MotionEvent::Kind::kImpact) { ++impacts; peak = e.value; }
    TEST_ASSERT_EQUAL_INT(1, impacts);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 14.0f, peak);
    // a second hit after the window is a second event, and a 16 g axis counts as a clip
    m.feed(t, 16.0f, 0.0f, 1.0f); t += 10;
    feed_accel(m, t, 0.5f, 0.01f);
    impacts = 0;
    while (m.pop(e)) if (e.kind == helmkit::dsp::MotionEvent::Kind::kImpact) ++impacts;
    TEST_ASSERT_EQUAL_INT(1, impacts);
    TEST_ASSERT_EQUAL_UINT32(1, m.clips());
}

void test_motion_activity_every_10s() {
    helmkit::dsp::MotionDetector m;
    uint32_t t = 0;
    helmkit::dsp::MotionEvent e;
    int acts = 0, stills = 0; float last = -1.0f;
    for (int sec = 0; sec < 21; ++sec) {            // drain every second, as the main loop does
        feed_accel(m, t, 1.0f, 0.2f);
        while (m.pop(e)) {
            if (e.kind == helmkit::dsp::MotionEvent::Kind::kActivity) { ++acts; last = e.value; }
            if (e.kind == helmkit::dsp::MotionEvent::Kind::kStill) ++stills;
        }
    }
    TEST_ASSERT_EQUAL_INT(2, acts);                 // at 10 s and 20 s
    TEST_ASSERT_EQUAL_INT(20, stills);
    TEST_ASSERT_TRUE(last > 0.1f && last < 0.3f);   // mean dynamic acceleration of the jitter (~0.2 g)
}

void test_button_debounce_short_long() {
    helmkit::ui::Button b;
    uint32_t t = 0;
    // 5 ms glitch: nothing
    TEST_ASSERT_EQUAL(helmkit::ui::Press::kNone, b.feed(t, false)); t += 10;
    b.feed(t, true); t += 5; b.feed(t, false); t += 30;
    TEST_ASSERT_EQUAL(helmkit::ui::Press::kNone, b.feed(t, false));
    TEST_ASSERT_FALSE(b.held());
    // short press: 200 ms held, event on release
    b.feed(t, true); t += 25; TEST_ASSERT_EQUAL(helmkit::ui::Press::kNone, b.feed(t, true));
    TEST_ASSERT_TRUE(b.held());
    t += 200; b.feed(t, false); t += 25;
    TEST_ASSERT_EQUAL(helmkit::ui::Press::kShort, b.feed(t, false));
    // long press: fires once at 1.5 s while held, nothing on release
    b.feed(t, true); t += 25; b.feed(t, true);
    helmkit::ui::Press got = helmkit::ui::Press::kNone;
    for (int i = 0; i < 200; ++i) { t += 10; const auto p = b.feed(t, true); if (p != helmkit::ui::Press::kNone) { TEST_ASSERT_EQUAL(helmkit::ui::Press::kNone, got); got = p; } }
    TEST_ASSERT_EQUAL(helmkit::ui::Press::kLong, got);
    b.feed(t, false); t += 25;
    TEST_ASSERT_EQUAL(helmkit::ui::Press::kNone, b.feed(t, false));
    // slide switch: debounced edges
    helmkit::ui::Debounced sl(20);
    sl.feed(0, false);
    TEST_ASSERT_EQUAL_INT(0, sl.feed(10, true));
    TEST_ASSERT_EQUAL_INT(+1, sl.feed(31, true));
    TEST_ASSERT_EQUAL_INT(0, sl.feed(40, true));
    sl.feed(50, false);
    TEST_ASSERT_EQUAL_INT(-1, sl.feed(71, false));
}

void test_power_policy_debounce_and_hysteresis() {
    helmkit::layers::PowerPolicy p;
    uint32_t t = 1000;
    for (int i = 0; i < 9; ++i, t += 1000) TEST_ASSERT_FALSE(p.feed(t, 3.45f));   // 9 s below: not yet
    TEST_ASSERT_FALSE(p.feed(t, 3.60f)); t += 1000;                                // a good read resets the debounce
    for (int i = 0; i < 10; ++i, t += 1000) TEST_ASSERT_FALSE(p.feed(t, 3.45f));
    TEST_ASSERT_TRUE(p.feed(t, 3.45f)); t += 1000;                                 // 10 s continuous: the one-shot
    TEST_ASSERT_TRUE(p.low());
    TEST_ASSERT_FALSE(p.feed(t, 3.55f)); t += 1000;                                // inside the hysteresis: still low
    TEST_ASSERT_TRUE(p.low());
    TEST_ASSERT_FALSE(p.feed(t, 3.65f));                                           // charger: cleared
    TEST_ASSERT_FALSE(p.low());
    TEST_ASSERT_EQUAL_UINT8(0, helmkit::layers::PowerPolicy::percent(3.2f));
    TEST_ASSERT_EQUAL_UINT8(100, helmkit::layers::PowerPolicy::percent(4.25f));
    TEST_ASSERT_EQUAL_UINT8(50, helmkit::layers::PowerPolicy::percent(3.82f));
    TEST_ASSERT_TRUE(helmkit::layers::PowerPolicy::percent(3.90f) > 60 && helmkit::layers::PowerPolicy::percent(3.90f) < 70);
}

void test_degrade_sheds_raw_then_restores() {
    helmkit::layers::Degrade d;
    TEST_ASSERT_FALSE(d.feed(5000, 0));
    TEST_ASSERT_FALSE(d.feed(10000, 10));          // 10 drops in 5 s: tolerated
    TEST_ASSERT_TRUE(d.feed(15000, 60));           // 50 drops: shed
    TEST_ASSERT_TRUE(d.feed(20000, 60));           // quiet 5 s: still shed
    TEST_ASSERT_TRUE(d.feed(40000, 60));           // quiet 25 s: still shed
    TEST_ASSERT_FALSE(d.feed(45001, 60));          // quiet 30 s: restored
    TEST_ASSERT_EQUAL_UINT32(1, d.episodes());
}

void test_fog_and_donning() {
    helmkit::dsp::FogDetector f;
    uint32_t t = 0;
    for (int i = 0; i < 40; ++i, t += 250) TEST_ASSERT_FALSE(f.feed(t, 33.0f, 24.0f));   // 10 s normal
    for (int i = 0; i < 80; ++i, t += 250) TEST_ASSERT_FALSE(f.feed(t, 24.1f, 24.0f));   // 19.75 s since the first close reading: not yet
    TEST_ASSERT_TRUE(f.feed(t, 24.1f, 24.0f)); t += 250;                                  // 20 s: fogged
    TEST_ASSERT_TRUE(f.fogged());
    TEST_ASSERT_FALSE(f.feed(t, 31.0f, 24.0f));                                            // clears at once
    helmkit::dsp::DonningCheck dc;
    TEST_ASSERT_EQUAL(helmkit::dsp::DonningCheck::Result::kIdle, dc.poll(0));
    dc.start(1000);
    TEST_ASSERT_EQUAL(helmkit::dsp::DonningCheck::Result::kPending, dc.poll(2000));
    dc.breath(3000); dc.breath(7000);
    TEST_ASSERT_EQUAL(helmkit::dsp::DonningCheck::Result::kPending, dc.poll(8000));
    TEST_ASSERT_EQUAL(helmkit::dsp::DonningCheck::Result::kFail, dc.poll(31000));     // two breaths in 30 s
    TEST_ASSERT_EQUAL(helmkit::dsp::DonningCheck::Result::kIdle, dc.poll(32000));
    dc.start(40000);
    dc.breath(41000); dc.breath(45000); dc.breath(49000);
    TEST_ASSERT_EQUAL(helmkit::dsp::DonningCheck::Result::kOk, dc.poll(50000));
}

void test_session_store_roundtrip_and_resume_rule() {
    helmkit::layers::SessionState s;
    s.valid = true; s.session_id = 0x0123456789abcdefULL; s.mode = 2; s.tally = 7; s.uptime_ms = 123456;
    char buf[48];
    TEST_ASSERT_TRUE(helmkit::layers::encode_session(s, buf, sizeof buf) > 0);
    TEST_ASSERT_EQUAL_STRING("1:0123456789abcdef:2:7:123456", buf);
    helmkit::layers::SessionState r;
    TEST_ASSERT_TRUE(helmkit::layers::decode_session(buf, r));
    TEST_ASSERT_TRUE(r.valid);
    TEST_ASSERT_EQUAL_UINT32(7, r.tally);
    TEST_ASSERT_EQUAL_UINT8(2, r.mode);
    TEST_ASSERT_TRUE(r.session_id == 0x0123456789abcdefULL);
    TEST_ASSERT_FALSE(helmkit::layers::decode_session("", r));
    TEST_ASSERT_FALSE(helmkit::layers::decode_session("2:00:1:1:1", r));
    TEST_ASSERT_FALSE(helmkit::layers::decode_session("garbage", r));
    TEST_ASSERT_TRUE(helmkit::layers::should_resume(s, "brownout"));
    TEST_ASSERT_TRUE(helmkit::layers::should_resume(s, "task-wdt"));
    TEST_ASSERT_FALSE(helmkit::layers::should_resume(s, "poweron"));
    TEST_ASSERT_FALSE(helmkit::layers::should_resume(s, "unknown"));
    helmkit::layers::SessionState none;
    TEST_ASSERT_FALSE(helmkit::layers::should_resume(none, "brownout"));
}

void test_modes_restore_reenters_tranquil_with_tally() {
    helmkit::layers::CombatModes m;
    std::vector<std::string> cues;
    m.set_emitter([](const char* c, void* u) { static_cast<std::vector<std::string>*>(u)->push_back(c); }, &cues);
    m.restore(5000, 3);
    TEST_ASSERT_TRUE(m.in_session());
    TEST_ASSERT_EQUAL(helmkit::layers::Mode::kTranquil, m.mode());
    TEST_ASSERT_EQUAL_UINT32(3, m.tally());
    TEST_ASSERT_EQUAL_INT(1, (int)cues.size());
    TEST_ASSERT_EQUAL_STRING("mode:tranquil", cues[0].c_str());
    m.event(6000, helmkit::layers::ModeCue::kTally);
    TEST_ASSERT_EQUAL_UINT32(4, m.tally());
}

void setUp() {}
void tearDown() {}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_resp_rate_rest_12bpm);
    RUN_TEST(test_resp_rate_round_30bpm_and_arousal_slope);
    RUN_TEST(test_resp_no_rate_before_two_breaths_and_refractory);
    RUN_TEST(test_resp_flat_signal_no_breaths);
    RUN_TEST(test_modes_session_flow);
    RUN_TEST(test_modes_timeouts);
    RUN_TEST(test_modes_ignore_events_outside_session);
    RUN_TEST(test_modes_millis_wrap);
    RUN_TEST(test_line_append_seq_before_closing_brace);
    RUN_TEST(test_link_stats_count_by_class_and_link);
    RUN_TEST(test_backoff_schedule_5_10_20_60);
    RUN_TEST(test_backoff_millis_wrap);
    RUN_TEST(test_motion_still_vs_moving);
    RUN_TEST(test_motion_impact_peak_and_refractory);
    RUN_TEST(test_motion_activity_every_10s);
    RUN_TEST(test_button_debounce_short_long);
    RUN_TEST(test_power_policy_debounce_and_hysteresis);
    RUN_TEST(test_degrade_sheds_raw_then_restores);
    RUN_TEST(test_fog_and_donning);
    RUN_TEST(test_session_store_roundtrip_and_resume_rule);
    RUN_TEST(test_modes_restore_reenters_tranquil_with_tally);
    return UNITY_END();
}
