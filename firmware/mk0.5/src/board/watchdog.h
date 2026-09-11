// HelmKit Mk0.5 — task watchdog and reset-reason attribution (Track N, N-F2 / N-F6).
//
// The Arduino core does not subscribe the loop task to the task watchdog, so
// a wedged I²C transaction or a runaway loop froze the helm silently. Now the
// loop task is subscribed with a 5 s timeout; the smoke-test loops feed it
// because they run for up to 10 s; a stall resets the chip and the next boot
// line says `task-wdt`.

#pragma once

#include <stdint.h>

namespace helmkit::board {

// Subscribe the calling task (loopTask) with `timeout_s`. Returns false if
// the watchdog could not be configured; the boot line carries the outcome.
bool wdt_begin(uint32_t timeout_s);

// Feed. Called once per loop() and inside every blocking smoke loop.
void wdt_feed();

// Why this boot happened, from esp_reset_reason(): "poweron", "sw", "panic",
// "int-wdt", "task-wdt", "wdt", "deepsleep", "brownout", "sdio", "ext",
// "unknown". The numeric form is the esp_reset_reason_t value.
const char* reset_reason_str();
int         reset_reason_num();

}  // namespace helmkit::board
