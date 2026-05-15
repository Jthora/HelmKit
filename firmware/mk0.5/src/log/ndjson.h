// HelmKit Mk0.5 — NDJSON serial logger.
// TODO(Day 3): emit one JSON object per line over USB-CDC.
// Forward-compatible with Mk1.0 SD-card sink and Mk1.5 Pi log-sink.
#pragma once
#include <Arduino.h>
namespace helmkit::log {
// void emit_sample(const char* kind, const char* json_payload);
// void emit_event(const char* kind, const char* json_payload);
}  // namespace helmkit::log
