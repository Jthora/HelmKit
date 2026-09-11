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
    return UNITY_END();
}
