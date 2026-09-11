// HelmKit Mk0.5 — link buffer on LittleFS (Track N, N-L2).
//
// Event-class lines that cannot reach the host (cable out, host not
// acknowledging, TX ring full) are appended here with their original `t` and
// `n`, and replayed once the link is healthy, tagged "replay":1. Raw sample
// streams are never buffered (they are dropped and counted).
//
// Two files alternate: writes go to the active one; when it passes the cap
// the other is deleted and becomes active. Replay reads the older file first,
// then the active one, in chunks bounded by the caller so the loop never
// stalls; a line the writer cannot send stops the chunk and is retried on
// the next call. Files are removed once fully replayed.
//
// Budget: 2 x 448 KB of the 1.5 MB LittleFS partition. At derived-event rates
// (a few lines per second) that is well over half an hour of link loss.

#pragma once

#include <stddef.h>
#include <stdint.h>

namespace helmkit::log {

class LinkBuffer {
 public:
    static constexpr size_t kCapPerFile = 448 * 1024;
    static constexpr size_t kMaxLine    = 360;

    bool begin();                                   // mounts LittleFS (formats on first use); false = buffering unavailable
    bool store(const char* line);                   // append; false when unavailable or the write failed
    bool has_pending() const { return size_[0] + size_[1] > 0; }
    // Replay at most `max_lines`; `emit` returns false when the line could not be sent (stop, retry later).
    uint16_t replay(uint16_t max_lines, bool (*emit)(const char*));
    size_t   bytes()     const { return size_[0] + size_[1]; }
    uint32_t stored()    const { return stored_; }
    uint32_t replayed()  const { return replayed_; }
    uint32_t rotations() const { return rotations_; }
    bool     available() const { return ok_; }

 private:
    const char* path(uint8_t idx) const { return idx == 0 ? "/lb0.ndjson" : "/lb1.ndjson"; }
    void remove_file(uint8_t idx);

    bool     ok_ = false;
    uint8_t  active_ = 0;
    size_t   size_[2] = {0, 0};
    uint8_t  rp_idx_ = 0;                            // file being replayed
    size_t   rp_off_ = 0;                            // byte offset into it
    bool     rp_on_older_ = false;
    uint32_t stored_ = 0, replayed_ = 0, rotations_ = 0;
};

}  // namespace helmkit::log
