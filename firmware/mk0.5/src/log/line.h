// HelmKit Mk0.5 — pure helpers for the NDJSON writer (Track N, N-F1).
//
// No Arduino here: this header is compiled into the native Unity tests.
//
//   append_seq   inserts the per-boot sequence number `,"n":<seq>` before the
//                closing brace of a finished JSON object. Every line the
//                firmware produces consumes a sequence number, written or
//                not, so a gap in `n` on the host is exactly one lost line.
//   LineClass    what a line is for the degradation policy: raw sample
//                streams are shed before events (Track N §2, rule 4).
//   LinkStats    counters the `hb` heartbeat reports (drops per class, lines
//                lost while the link was down, lines written).

#pragma once

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

namespace helmkit::log {

enum class LineClass : uint8_t {
    kEvent = 0,   // cues, RR intervals, breaths, health, hb, boot, smoke, error, hello
    kRaw   = 1,   // gsr, temp-* samples: droppable first under load
};

// Returns false and leaves `buf` untouched when the object is not closed or
// the sequence field does not fit in `cap`.
inline bool append_seq(char* buf, size_t cap, uint32_t seq) {
    if (buf == nullptr || cap == 0) return false;
    const size_t len = strnlen(buf, cap);
    if (len >= cap || len < 2 || buf[len - 1] != '}') return false;
    char tail[24];
    const int tl = snprintf(tail, sizeof tail, ",\"n\":%lu}", (unsigned long)seq);
    if (tl <= 0) return false;
    if (len - 1 + (size_t)tl + 1 > cap) return false;   // +1 for the NUL
    memcpy(buf + len - 1, tail, (size_t)tl + 1);
    return true;
}

struct LinkStats {
    uint32_t written       = 0;
    uint32_t dropped_raw   = 0;   // buffer full or link down, raw class
    uint32_t dropped_event = 0;   // buffer full or link down, event class
    uint32_t link_down     = 0;   // subset of the drops: the host was not attached
    bool     link          = false;

    void note(LineClass cls, bool written_ok, bool link_up) {
        link = link_up;
        if (written_ok) { ++written; return; }
        if (!link_up) ++link_down;
        if (cls == LineClass::kRaw) ++dropped_raw; else ++dropped_event;
    }
    uint32_t dropped() const { return dropped_raw + dropped_event; }
};

}  // namespace helmkit::log
