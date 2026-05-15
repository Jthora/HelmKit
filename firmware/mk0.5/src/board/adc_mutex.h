// HelmKit Mk0.5 — ADC1 arbitration mutex.
//
// Background (see PRIOR_ART.md claim M8, docs/PINOUT.md §3):
//   The Heltec V3 places VBAT divider on ADC1_CH0 (GPIO 1) and we route GSR
//   onto ADC1_CH3 (GPIO 4). Both readers ultimately call analogRead(), which
//   is not reentrant: a context switch mid-read can pin-swap the SAR and
//   corrupt the result. The mutex is the only correctness-preserving primitive
//   here short of disabling preemption.
//
// Discipline:
//   * Acquire BEFORE driving kAdcCtrl (active-low VBAT divider enable).
//   * Hold the mutex for the smallest possible critical section.
//   * Never block on I/O while holding it.
//   * Both gsr.cpp AND battery.cpp must use this mutex. No exceptions.
//
// This file declares; src/board/adc_mutex.cpp defines.

#pragma once

#include <Arduino.h>
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>

namespace helmkit::board {

// Singleton mutex protecting ADC1. Eagerly initialized via adc1_init() in
// setup() (Wave I change; previously lazy). Returns true if the caller now
// owns the mutex; false on timeout.
//
// Closes R6 (mutex creation failure was silently absorbed).
bool adc1_init();
bool adc1_acquire(uint32_t timeout_ms = 50);
void adc1_release();

// RAII helper. [[nodiscard]] makes "forgot to check ok()" a build warning.
class Adc1Lock {
public:
    explicit Adc1Lock(uint32_t timeout_ms = 50)
        : held_(adc1_acquire(timeout_ms)) {}
    ~Adc1Lock() { if (held_) adc1_release(); }
    [[nodiscard]] bool ok() const { return held_; }
    Adc1Lock(const Adc1Lock&) = delete;
    Adc1Lock& operator=(const Adc1Lock&) = delete;
private:
    bool held_;
};

// Safer alternative: the lambda only runs if the lock was acquired. Returns
// true iff the lock was held AND the lambda ran. Closes R5 — there is no
// way to opt out by accident.
template <typename Fn>
inline bool with_adc1_lock(uint32_t timeout_ms, Fn&& fn) {
    Adc1Lock lock(timeout_ms);
    if (!lock.ok()) return false;
    fn();
    return true;
}

}  // namespace helmkit::board
