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

// Wave J. Emit an RR-interval sample on the `ppg-rr` channel (docs/SCHEMA.md
// §2.2). Sample shape conforms to psiStabilizer v0.1: {t, ch, v, q, boot}
// plus a non-standard `conf` extension (peak_amp / threshold). The first
// peak after a reset has rr_ms == 0 and is still emitted with q="ok" — it
// anchors the per-session RR series so analysis can timestamp the rising
// edge of the first beat. Subsequent peaks emit q="ok" when in_range, or
// q="out-of-range" when the gap is < 250 ms (refractory-survivor) or
// > 2000 ms (drop / artefact).
//   t_ms: millis()-since-boot at peak centroid (bridged to wall-clock at
//         ingest per SCHEMA.md §3).
//   rr_ms: RR interval in milliseconds; 0 = first peak in stream.
//   in_range: true if 250 <= rr_ms <= 2000 OR rr_ms == 0.
//   confidence: peak_amp / threshold; >= 1.0 by construction.
void emit_ppg_rr(uint32_t t_ms,
                 uint16_t rr_ms,
                 bool in_range,
                 float confidence);

// Wave J Bridge B. Emit one MLX90614 sample as the canonical pair of
// SCHEMA §2.2 channels: `temp-forehead` (object/IR °C) and
// `temp-forehead.amb` (ambient °C). Both lines share the same `t_ms`
// timestamp so downstream analysis can pair them by timestamp without
// guessing.
//   t_ms: millis()-since-boot at sample.
//   object_c, ambient_c: float °C, NOT NaN (driver gates upstream).
//   in_range: true if 15 < object_c < 45 per SCHEMA §4; flips q field on
//             the temp-forehead line. ambient line is always q="ok".
void emit_temp_forehead(uint32_t t_ms,
                        float object_c,
                        float ambient_c,
                        bool in_range);

}  // namespace helmkit::log
