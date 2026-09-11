// HelmKit Mk0.5 — link buffer implementation. See buffer.h.

#include "log/buffer.h"

#include <Arduino.h>
#include <LittleFS.h>
#include <string.h>

namespace helmkit::log {

bool LinkBuffer::begin() {
    ok_ = LittleFS.begin(true);       // format on the first mount
    if (!ok_) return false;
    for (uint8_t i = 0; i < 2; ++i) {
        size_[i] = 0;
        File f = LittleFS.open(path(i), "r");
        if (f) { size_[i] = f.size(); f.close(); }
    }
    // the larger file is the older one when both exist: keep appending to the newer (smaller) one
    active_ = (size_[0] > 0 && size_[1] > 0) ? (size_[0] <= size_[1] ? 0 : 1) : (size_[1] > 0 ? 1 : 0);
    rp_off_ = 0;
    return true;
}

void LinkBuffer::remove_file(uint8_t idx) {
    LittleFS.remove(path(idx));
    size_[idx] = 0;
}

bool LinkBuffer::store(const char* line) {
    if (!ok_ || line == nullptr) return false;
    const size_t len = strnlen(line, kMaxLine);
    if (len == 0 || len >= kMaxLine) return false;
    if (size_[active_] + len + 1 > kCapPerFile) {
        // rotate: the other file's contents are the oldest and go
        const uint8_t other = (uint8_t)(1 - active_);
        if (size_[other] > 0) ++rotations_;
        remove_file(other);
        active_ = other;
        rp_off_ = 0;
    }
    File f = LittleFS.open(path(active_), "a");
    if (!f) return false;
    const size_t w = f.write((const uint8_t*)line, len) + f.write((uint8_t)'\n');
    f.close();
    if (w != len + 1) return false;
    size_[active_] += len + 1;
    ++stored_;
    return true;
}

uint16_t LinkBuffer::replay(uint16_t max_lines, bool (*emit)(const char*)) {
    if (!ok_ || emit == nullptr || !has_pending()) return 0;
    const uint8_t older = (uint8_t)(1 - active_);
    const uint8_t idx = (size_[older] > 0) ? older : active_;
    if (idx != rp_idx_) { rp_idx_ = idx; rp_off_ = 0; }
    File f = LittleFS.open(path(idx), "r");
    if (!f) { remove_file(idx); return 0; }
    if (!f.seek(rp_off_)) { f.close(); remove_file(idx); return 0; }
    uint16_t sent = 0;
    char buf[kMaxLine];
    while (sent < max_lines && f.available()) {
        const size_t start = f.position();
        const size_t n = f.readBytesUntil('\n', buf, kMaxLine - 1);
        buf[n] = '\0';
        if (n == 0) { rp_off_ = f.position(); continue; }
        if (!emit(buf)) { f.seek(start); break; }   // could not send: retry from this line
        rp_off_ = f.position();
        ++sent;
        ++replayed_;
    }
    const bool done = !f.available();
    f.close();
    if (done) {
        remove_file(idx);
        rp_off_ = 0;
    }
    return sent;
}

}  // namespace helmkit::log
