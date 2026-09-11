// HelmKit Mk0.5 — session state persistence (Track N, N-F5).
//
// Pure encode / decode and the resume rule; the NVS glue (Preferences) lives
// in main.cpp. The state is written on every mode change and cleared when
// the operator ends the session.
//
// Resume rule: there is no clock to measure how long the helm was off, so a
// saved session is resumed only after an INVOLUNTARY restart (brownout,
// panic, any watchdog, software reset). A power-on reset means somebody
// switched the helm off and on: the session is discarded, not resumed.
// (The plan's "within 5 minutes" needs a wall clock the belt pack will
// supply later; this rule is the one the hardware can honour today.)
//
// Wire form (NVS string, <= 48 chars): "1:<session hex16>:<mode>:<tally>:<uptime_ms>"

#pragma once

#include <stdint.h>
#include <stdio.h>
#include <string.h>

namespace helmkit::layers {

struct SessionState {
    bool     valid       = false;
    uint64_t session_id  = 0;      // the boot id of the boot that started the session
    uint8_t  mode        = 0;      // layers::Mode as an integer
    uint32_t tally       = 0;
    uint32_t uptime_ms   = 0;      // millis() at the last write (diagnostic only)
};

inline int encode_session(const SessionState& s, char* out, size_t cap) {
    if (!s.valid) { if (cap) out[0] = '\0'; return 0; }
    return snprintf(out, cap, "1:%016llx:%u:%lu:%lu",
                    (unsigned long long)s.session_id, (unsigned)s.mode,
                    (unsigned long)s.tally, (unsigned long)s.uptime_ms);
}

inline bool decode_session(const char* in, SessionState& out) {
    out = SessionState{};
    if (in == nullptr || in[0] == '\0') return false;
    unsigned long long id = 0; unsigned mode = 0; unsigned long tally = 0, up = 0; int ver = 0;
    if (sscanf(in, "%d:%llx:%u:%lu:%lu", &ver, &id, &mode, &tally, &up) != 5) return false;
    if (ver != 1 || mode > 255) return false;
    out.valid = true; out.session_id = id; out.mode = (uint8_t)mode; out.tally = tally; out.uptime_ms = up;
    return true;
}

// reset reasons from board/watchdog.h; "poweron" and "unknown" do not resume
inline bool involuntary_restart(const char* reason) {
    if (reason == nullptr) return false;
    return strcmp(reason, "brownout") == 0 || strcmp(reason, "panic") == 0 ||
           strcmp(reason, "task-wdt") == 0 || strcmp(reason, "int-wdt") == 0 ||
           strcmp(reason, "wdt") == 0      || strcmp(reason, "sw") == 0;
}

inline bool should_resume(const SessionState& s, const char* reset_reason) {
    return s.valid && involuntary_restart(reset_reason);
}

}  // namespace helmkit::layers
