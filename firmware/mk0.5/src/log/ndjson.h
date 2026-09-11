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
#include "log/line.h"

namespace helmkit::log {

// Call once early in setup(). Track N: the link state is re-read on every
// line, so a cable plugged in after boot starts logging without a reset.
void init();
bool serial_attached();

// Track N (N-F1): every line carries a per-boot sequence number `n`; lines
// that could not be written (link down or TX buffer full) still consume one,
// so a gap in `n` on the host is exactly one lost line. Counters per class.
const LinkStats& link_stats();
uint32_t         seq();

// Track N (N-L2 / N-L3). The link is healthy when a host is attached and,
// once a host has ever acknowledged a heartbeat this boot (byte '~'), the
// last acknowledgement is under 10 s old. Event-class lines that cannot be
// written while the link is unhealthy (or the TX ring is full) go to the
// store hook instead of being dropped; emit_stored() replays one such line,
// tagged "replay":1, and returns false when it could not be sent.
void set_store(bool (*store)(const char* line));
void note_ack(uint32_t now_ms);
bool link_healthy(uint32_t now_ms);
bool ack_seen();
bool emit_stored(const char* line);

// Track N (N-F2). Wire shape: {"t":<s>,"kind":"boot","reason":"<str>",
//   "reason_num":<n>,"wdt":<0|1>,"mk":50,"git":"<sha>","schema":"...","boot":"<hex>"}
void emit_boot(const char* reason, int reason_num, bool wdt_ok);

// Track N (N-L1). Heartbeat every 5 s so the host can tell a link gap from a
// sensor gap. Wire shape: {"t":<s>,"ch":"hb","v":<uptime_s>,"q":"ok",
//   "drops":<u32>,"drops_ev":<u32>,"link_down":<u32>,"buffered":<u32>,"buf":<bytes>,"heap":<u32>,"boot":"<hex>"}
void emit_hb(uint32_t t_ms, uint32_t free_heap, uint32_t buffered_bytes);

// Track N phase 1: generic sample emitters for the new channels (still,
// impact, activity, vbat, ppg-q: numeric; btn: string). `cls` picks the
// drop class (raw streams are shed first).
void emit_num(const char* ch, uint32_t t_ms, float v, const char* q, LineClass cls = LineClass::kEvent);
void emit_str(const char* ch, uint32_t t_ms, const char* v);
// vbat with the schema's raw ADC count as v plus volts / pct fields.
void emit_vbat(uint32_t t_ms, uint16_t raw, float volts, uint8_t pct);
// gsr / temp with an explicit quality string ("ok" / "out-of-range" / "gap").
void emit_gsr_q(uint32_t t_ms, uint16_t raw, const char* q);
void emit_temp_object_q(uint32_t t_ms, float object_c, float ambient_c, const char* q, const char* channel);

// Track N (N-F4). One line per driver health transition and per retry.
// Wire shape: {"t":<s>,"kind":"health","source":"<n>","from":"<h>","to":"<h>",
//   "attempt":<u16>,"note":"<str>","boot":"<hex>"}
void emit_health(const char* source, const char* from, const char* to,
                 uint16_t attempt, const char* note);

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

// Wave J Bridge B. Emit a single GSR sample as SCHEMA §2.2 channel `gsr`
// (raw uint16 0..4095, 50 Hz). q field flips on out-of-range per SCHEMA
// §4 (100 < raw < 4000 -> ok, else out-of-range — rail-pinned readings
// almost always indicate electrode disconnect or short).
void emit_gsr(uint32_t t_ms,
              uint16_t raw,
              bool in_range);

// Track M (2026-09-11). One `cue` event line, the same shape the L0 pacer has
// always emitted: {"t":<s>,"ch":"cue","v":"<value>","boot":"<hex>"}. Values per
// SCHEMA §2.2 (inhale / exhale / session-start / session-end) and §2.3
// (round-start / round-end / prime / sanctuary / tally, plus the mode machine's
// "mode:<name>", "tally-ack", "impact:<N>g", "summary:tally=<N>").
void emit_cue(const char* value);                   // t = millis() now
void emit_cue_at(uint32_t t_ms, const char* value);

// Track M. MLX90614 object / ambient pair on a caller-chosen channel:
// "temp-forehead" is the Mk0.5 wiring (emit_temp_forehead delegates here,
// byte-identical output); "temp-nose" when the thermopile rides the combat
// trim's sensor bar aimed at the nose tip (SCHEMA §2.3). The ambient line is
// "<channel>.amb".
void emit_temp_object(uint32_t t_ms,
                      float object_c,
                      float ambient_c,
                      bool in_range,
                      const char* channel);

// Track M. Breath event on `resp-thermal` (SCHEMA §2.3): v = breaths per
// minute over the trailing 30 s at the time of the breath, q = "ok".
void emit_resp_thermal(uint32_t t_ms, float breaths_per_min);

}  // namespace helmkit::log
