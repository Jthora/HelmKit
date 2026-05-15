// HelmKit Mk0.5 — NDJSON serial logger.
//
// Wave G upgrade (2026-05-15): real implementation. Closes critique items
// RP1 (kind:"error" events), RP4 (transactional single-line emit), and is
// the canonical wire-format anchor for the SmokeFail enum.
//
// All emitters serialize into a stack-local buffer (256 B) and then issue
// exactly one Serial.println so that USB-CDC buffer drops cannot split a
// JSON line.
#pragma once

#include <Arduino.h>
#include <stdint.h>

#include "drivers/sensor.h"
#include "drivers/smoke_fail.h"
#include "drivers/smoke_result.h"

namespace helmkit::log {

// Call once early in setup() — captures (bool)Serial into a module flag.
void init();
bool serial_attached();

// Wire shape: {"t":0.000,"kind":"hello","mk":50,"git":"<sha>","dirty":0,
//              "schema":"...","boot":"<16-hex>","build":"<__DATE__ __TIME__>"}
void emit_hello();

// Wire shape: {"t":<s>,"kind":"smoke","source":"<n>","ok":<0|1>,
//              "code":"<str>","code_num":<u16>,"health":"<str>",
//              "ev_a":<u32>,"ev_b":<u32>,"note":"<reason>","boot":"<hex>"}
void emit_smoke_result(const char* source,
                       const helmkit::drivers::SmokeResult& r);

// Wire shape: {"t":<s>,"kind":"error","source":"<n>","code":"<str>",
//              "code_num":<u16>,"health":"<str>","ev_a":<u32>,"ev_b":<u32>,
//              "note":"<reason>","boot":"<hex>"}
void emit_error(const char* source,
                helmkit::drivers::SmokeFail code,
                const char* note,
                uint32_t evidence_a = 0,
                uint32_t evidence_b = 0,
                helmkit::drivers::Health terminal_health =
                    helmkit::drivers::Health::kError);

}  // namespace helmkit::log
