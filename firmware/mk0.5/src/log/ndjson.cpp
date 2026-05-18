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

bool g_attached = false;

constexpr size_t kBufSz = 256;

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

void emit_line(const char* buf) {
    if (!g_attached) return;
    Serial.println(buf);
}

}  // namespace

void init() {
    g_attached = (bool)Serial;
}

bool serial_attached() {
    return g_attached;
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
    if (!g_attached) return;
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

}  // namespace helmkit::log
