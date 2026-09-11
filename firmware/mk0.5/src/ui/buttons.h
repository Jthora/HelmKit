// HelmKit Mk0.5 — debounced buttons and slide switch (Track N, N-U1 / N-U3).
//
// Pure, header-only, native-tested. main.cpp reads the GPIOs every loop and
// feeds the level; this classifies presses:
//
//   kShort   released before `long_ms`
//   kLong    held for `long_ms`; fired once, at the moment the threshold
//            passes (not on release), so the operator feels the point of no
//            return; the release that follows fires nothing
//
// A 20 ms debounce rejects contact bounce and glove taps. The slide switch
// reports debounced level changes.

#pragma once

#include <stdint.h>

namespace helmkit::ui {

struct ButtonConfig {
    uint32_t debounce_ms = 20;
    uint32_t long_ms     = 1500;
};

enum class Press : uint8_t { kNone = 0, kShort, kLong };

class Debounced {
 public:
    explicit Debounced(uint32_t debounce_ms = 20) : debounce_ms_(debounce_ms) {}
    // Returns +1 when the debounced level becomes true, -1 when it becomes false, 0 otherwise.
    int feed(uint32_t t_ms, bool level) {
        if (!init_) { init_ = true; raw_ = stable_ = level; raw_t_ = t_ms; return 0; }
        if (level != raw_) { raw_ = level; raw_t_ = t_ms; }
        if (raw_ != stable_ && (int32_t)(t_ms - raw_t_) >= (int32_t)debounce_ms_) {
            stable_ = raw_;
            return stable_ ? +1 : -1;
        }
        return 0;
    }
    bool level() const { return stable_; }
 private:
    uint32_t debounce_ms_;
    bool init_ = false, raw_ = false, stable_ = false;
    uint32_t raw_t_ = 0;
};

class Button {
 public:
    explicit Button(const ButtonConfig& cfg = {}) : cfg_(cfg), db_(cfg.debounce_ms) {}

    // `pressed` = the debounce input (true while the contact is closed).
    Press feed(uint32_t t_ms, bool pressed) {
        const int edge = db_.feed(t_ms, pressed);
        if (edge > 0) { press_t_ = t_ms; long_fired_ = false; held_ = true; return Press::kNone; }
        if (edge < 0) {
            held_ = false;
            return long_fired_ ? Press::kNone : Press::kShort;
        }
        if (held_ && !long_fired_ && (int32_t)(t_ms - press_t_) >= (int32_t)cfg_.long_ms) {
            long_fired_ = true;
            return Press::kLong;
        }
        return Press::kNone;
    }
    bool held() const { return held_; }

 private:
    ButtonConfig cfg_;
    Debounced    db_;
    bool         held_ = false, long_fired_ = false;
    uint32_t     press_t_ = 0;
};

}  // namespace helmkit::ui
