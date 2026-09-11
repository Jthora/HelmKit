// HelmKit Mk0.5 — NDJSON serial logger implementation.
// See ndjson.h.

#include "log/ndjson.h"

#include <stdio.h>
#include <string.h>

#include "drivers/smoke_fail.h"
#include "log/session.h"

#ifndef HELMKIT_GIT_SHA
#  define HELMKIT_GIT_SHA "nogit"
#endif
#ifndef HELMKIT_GIT_DIRTY
#  define HELMKIT_GIT_DIRTY 0
#endif
#ifndef HELMKIT_SCHEMA_VERSION
#  define HELMKIT_SCHEMA_VERSION "0.0"
#endif

namespace helmkit::log {

namespace {

bool      g_attached = false;
LinkStats g_stats;
uint32_t  g_seq = 0;

constexpr size_t kBufSz = 320;   // longest line (smoke result) ~210 B + ,"n":4294967295

// Escape a free-form note into JSON-safe text. Replaces " and \ with _,
// drops control chars. Truncates to at most `cap-1` bytes. Output is NUL-
// terminated. We deliberately do NOT do real \" escaping — the contract is
// "notes are diagnostic strings, not user input"; substitution is faster
// and safer at this stage. Document this in SCHEMA.md.
void sanitize(const char* in, char* out, size_t cap) {
    if (cap == 0) return;
    if (in == nullptr) { out[0] = '\0'; return; }
    size_t j = 0;
    for (size_t i = 0; in[i] != '\0' && j + 1 < cap; ++i) {
        char c = in[i];
        if (c == '"' || c == '\\') c = '_';
        else if (c < 0x20)         c = '_';
        out[j++] = c;
    }
    out[j] = '\0';
}

// Central writer (Track N, N-F1). Appends the sequence number, checks the
// link and the TX ring, never blocks: a line that does not fit is counted,
// not waited for, so a yanked cable cannot stall the loop.
void emit_line(char* buf, LineClass cls = LineClass::kEvent) {
    ++g_seq;
    const bool link = (bool)Serial;
    g_attached = link;
    if (!append_seq(buf, kBufSz, g_seq)) {
        g_stats.note(cls, false, link);
        return;
    }
    if (!link) {
        g_stats.note(cls, false, false);
        return;
    }
    const size_t len = strlen(buf);
    if ((size_t)Serial.availableForWrite() < len + 2) {   // + CR LF
        g_stats.note(cls, false, true);
        return;
    }
    Serial.println(buf);
    g_stats.note(cls, true, true);
}

}  // namespace

void init() {
    g_attached = (bool)Serial;
#if defined(ARDUINO_USB_CDC_ON_BOOT) && ARDUINO_USB_CDC_ON_BOOT
    // Never block on a host that is attached but not draining (the pre-check
    // above makes this a backstop, not the mechanism).
    Serial.setTxTimeoutMs(2);
#endif
}

bool serial_attached() {
    return (bool)Serial;
}

const LinkStats& link_stats() {
    return g_stats;
}

uint32_t seq() {
    return g_seq;
}

void emit_boot(const char* reason, int reason_num, bool wdt_ok) {
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)millis() / 1000.0f;
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"kind\":\"boot\",\"reason\":\"%s\",\"reason_num\":%d,"
             "\"wdt\":%d,\"mk\":%d,\"git\":\"%s\",\"schema\":\"%s\",\"boot\":\"%s\"}",
             t, reason ? reason : "unknown", reason_num, wdt_ok ? 1 : 0,
             HELMKIT_MK, HELMKIT_GIT_SHA, HELMKIT_SCHEMA_VERSION, hex);
    emit_line(buf);
}

void emit_hb(uint32_t t_ms, uint32_t free_heap) {
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)t_ms / 1000.0f;
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"ch\":\"hb\",\"v\":%.1f,\"q\":\"ok\","
             "\"drops\":%lu,\"drops_ev\":%lu,\"link_down\":%lu,\"heap\":%lu,\"boot\":\"%s\"}",
             t, (double)t,
             (unsigned long)g_stats.dropped(), (unsigned long)g_stats.dropped_event,
             (unsigned long)g_stats.link_down, (unsigned long)free_heap, hex);
    emit_line(buf);
}

void emit_health(const char* source, const char* from, const char* to,
                 uint16_t attempt, const char* note_in) {
    char note[64];
    sanitize(note_in, note, sizeof note);
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)millis() / 1000.0f;
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"kind\":\"health\",\"source\":\"%s\",\"from\":\"%s\","
             "\"to\":\"%s\",\"attempt\":%u,\"note\":\"%s\",\"boot\":\"%s\"}",
             t, source ? source : "?", from ? from : "?", to ? to : "?",
             (unsigned)attempt, note, hex);
    emit_line(buf);
}

void emit_hello() {
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)millis() / 1000.0f;
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"kind\":\"hello\",\"mk\":%d,"
             "\"git\":\"%s\",\"dirty\":%d,\"schema\":\"%s\","
             "\"boot\":\"%s\",\"build\":\"%s %s\"}",
             t, HELMKIT_MK,
             HELMKIT_GIT_SHA, HELMKIT_GIT_DIRTY, HELMKIT_SCHEMA_VERSION,
             hex, __DATE__, __TIME__);
    emit_line(buf);
}

void emit_smoke_result(const char* source,
                       const helmkit::drivers::SmokeResult& r) {
    using helmkit::drivers::smoke_fail_str;
    using helmkit::drivers::health_str;
    char note[96];
    sanitize(r.reason, note, sizeof note);
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)millis() / 1000.0f;
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"kind\":\"smoke\",\"source\":\"%s\","
             "\"ok\":%d,\"code\":\"%s\",\"code_num\":%u,"
             "\"health\":\"%s\",\"ev_a\":%lu,\"ev_b\":%lu,"
             "\"note\":\"%s\",\"boot\":\"%s\"}",
             t, source ? source : "?",
             r.ok ? 1 : 0,
             smoke_fail_str(r.code),
             static_cast<unsigned>(r.code),
             health_str(r.terminal_health),
             (unsigned long)r.evidence_a,
             (unsigned long)r.evidence_b,
             note, hex);
    emit_line(buf);
}

void emit_error(const char* source,
                helmkit::drivers::SmokeFail code,
                const char* note_in,
                uint32_t evidence_a,
                uint32_t evidence_b,
                helmkit::drivers::Health terminal_health) {
    using helmkit::drivers::smoke_fail_str;
    using helmkit::drivers::health_str;
    char note[96];
    sanitize(note_in, note, sizeof note);
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)millis() / 1000.0f;
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"kind\":\"error\",\"source\":\"%s\","
             "\"code\":\"%s\",\"code_num\":%u,\"health\":\"%s\","
             "\"ev_a\":%lu,\"ev_b\":%lu,\"note\":\"%s\",\"boot\":\"%s\"}",
             t, source ? source : "?",
             smoke_fail_str(code),
             static_cast<unsigned>(code),
             health_str(terminal_health),
             (unsigned long)evidence_a,
             (unsigned long)evidence_b,
             note, hex);
    emit_line(buf);
}

void emit_ppg_rr(uint32_t t_ms,
                 uint16_t rr_ms,
                 bool in_range,
                 float confidence) {
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    // Use the supplied peak-timestamp (millis), not millis() at emit-time —
    // peak-time is what RR is computed against and what downstream analysis
    // needs to be deterministic across replays.
    const float t = (float)t_ms / 1000.0f;
    const char* q = in_range ? "ok" : "out-of-range";
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"ch\":\"ppg-rr\",\"v\":%u,\"q\":\"%s\","
             "\"conf\":%.2f,\"boot\":\"%s\"}",
             t, (unsigned)rr_ms, q, (double)confidence, hex);
    emit_line(buf);
}

void emit_temp_object(uint32_t t_ms,
                      float object_c,
                      float ambient_c,
                      bool in_range,
                      const char* channel) {
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)t_ms / 1000.0f;
    const char* q_obj = in_range ? "ok" : "out-of-range";
    // Object/IR line.
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"ch\":\"%s\",\"v\":%.2f,"
             "\"q\":\"%s\",\"boot\":\"%s\"}",
             t, channel, (double)object_c, q_obj, hex);
    emit_line(buf, LineClass::kRaw);
    // Ambient line; always q="ok" — ambient has no SCHEMA range gate.
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"ch\":\"%s.amb\",\"v\":%.2f,"
             "\"q\":\"ok\",\"boot\":\"%s\"}",
             t, channel, (double)ambient_c, hex);
    emit_line(buf, LineClass::kRaw);
}

void emit_temp_forehead(uint32_t t_ms,
                        float object_c,
                        float ambient_c,
                        bool in_range) {
    emit_temp_object(t_ms, object_c, ambient_c, in_range, "temp-forehead");
}

void emit_cue_at(uint32_t t_ms, const char* value) {
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)t_ms / 1000.0f;
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"ch\":\"cue\",\"v\":\"%s\",\"boot\":\"%s\"}",
             t, value, hex);
    emit_line(buf);
}

void emit_cue(const char* value) {
    emit_cue_at(millis(), value);
}

void emit_resp_thermal(uint32_t t_ms, float breaths_per_min) {
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)t_ms / 1000.0f;
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"ch\":\"resp-thermal\",\"v\":%.1f,"
             "\"q\":\"ok\",\"boot\":\"%s\"}",
             t, (double)breaths_per_min, hex);
    emit_line(buf);
}

void emit_gsr(uint32_t t_ms,
              uint16_t raw,
              bool in_range) {
    char hex[17];
    boot_id_hex(hex);
    char buf[kBufSz];
    const float t = (float)t_ms / 1000.0f;
    const char* q = in_range ? "ok" : "out-of-range";
    snprintf(buf, kBufSz,
             "{\"t\":%.3f,\"ch\":\"gsr\",\"v\":%u,\"q\":\"%s\","
             "\"boot\":\"%s\"}",
             t, (unsigned)raw, q, hex);
    emit_line(buf, LineClass::kRaw);
}

}  // namespace helmkit::log
