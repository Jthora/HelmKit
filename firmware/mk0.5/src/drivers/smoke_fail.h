// HelmKit Mk0.5 — structured fault taxonomy.
//
// Closes critique items H1 (string-only error vocab), H2 (no Health→reason
// mapping), and forms the wire-format substrate for kind:"error" NDJSON
// events (see docs/SCHEMA.md §2.2).
//
// Defensive-publication note (PRIOR_ART claim M9):
//   The numeric ranges below are reserved as part of the disclosed wire
//   format. 0–99 = sensor-domain (Mk0.5+). 100–199 = stim-domain (Mk1.0+,
//   reserved here so the schema does not break when Mk1.0 introduces stim
//   safety events). 200+ = host/network (Mk1.5+). Reserving the ranges
//   before they are needed is the same forward-compat discipline that paid
//   off when SCHEMA v0.2-proposed reserved gsr/ecg/vbat channels.

#pragma once

#include <stdint.h>

#include "drivers/sensor.h"

namespace helmkit::drivers {

enum class SmokeFail : uint16_t {
    kNone               = 0,

    // -- Sensor domain (Mk0.5+) -------------------------------------------
    kNoAck              = 10,   // I2C address did not ACK
    kWrongPartId        = 11,   // ACK but device returned wrong part-id
    kConfigFailed       = 12,   // ACK + part-id ok but config write failed
    kBeginFailed        = 13,   // catch-all begin() failure (use sparingly)
    kLowSampleRate      = 20,   // delivered fewer samples than gate requires
    kFifoOverflow       = 21,   // driver-internal or hardware FIFO overflowed
    kI2cStalled         = 22,   // pump() returned 0 samples for too long
    kOutOfRange         = 23,   // sensor reading outside physical plausibility
    kMutexTimeout       = 30,   // ADC mutex (or other shared) timed out
    kHeapExhausted      = 31,   // new(std::nothrow) returned null
    kNotImplemented     = 90,   // Wave-N stub; surface in note which sensor

    // -- Stim domain (Mk1.0+, RESERVED — do not emit at Mk0.5) ------------
    kStimCurrentExcursion  = 100,
    kStimImpedanceLow      = 101,
    kStimElectrodeFloat    = 102,
    kStimPatientDisconnect = 103,
    kStimSafetyHalt        = 104,

    // -- Host / network domain (Mk1.5+, RESERVED) -------------------------
    kHostTimeSyncFailed    = 200,
    kHostBacklogOverflow   = 201,

    kUnknown            = 65535,
};

// Canonical wire string. Stable across versions. Used in NDJSON
// "code" field. Adding new values requires bumping HELMKIT_SCHEMA_VERSION
// in platformio.ini build_flags.
inline const char* smoke_fail_str(SmokeFail c) {
    switch (c) {
        case SmokeFail::kNone:                  return "none";
        case SmokeFail::kNoAck:                 return "no-ack";
        case SmokeFail::kWrongPartId:           return "wrong-part-id";
        case SmokeFail::kConfigFailed:          return "config-failed";
        case SmokeFail::kBeginFailed:           return "begin-failed";
        case SmokeFail::kLowSampleRate:         return "low-sample-rate";
        case SmokeFail::kFifoOverflow:          return "fifo-overflow";
        case SmokeFail::kI2cStalled:            return "i2c-stalled";
        case SmokeFail::kOutOfRange:            return "out-of-range";
        case SmokeFail::kMutexTimeout:          return "mutex-timeout";
        case SmokeFail::kHeapExhausted:         return "heap-exhausted";
        case SmokeFail::kNotImplemented:        return "not-implemented";
        case SmokeFail::kStimCurrentExcursion:  return "stim-current-excursion";
        case SmokeFail::kStimImpedanceLow:      return "stim-impedance-low";
        case SmokeFail::kStimElectrodeFloat:    return "stim-electrode-float";
        case SmokeFail::kStimPatientDisconnect: return "stim-patient-disconnect";
        case SmokeFail::kStimSafetyHalt:        return "stim-safety-halt";
        case SmokeFail::kHostTimeSyncFailed:    return "host-time-sync-failed";
        case SmokeFail::kHostBacklogOverflow:   return "host-backlog-overflow";
        case SmokeFail::kUnknown:               return "unknown";
    }
    return "unknown";
}

// Health → SmokeFail mapping. The Health enum is the live-state model; the
// SmokeFail enum is the post-mortem report. This function is the single
// source of truth for the projection.
inline SmokeFail smoke_fail_from_health(Health h) {
    switch (h) {
        case Health::kUninit:      return SmokeFail::kBeginFailed;
        case Health::kOk:          return SmokeFail::kNone;
        case Health::kNoAck:       return SmokeFail::kNoAck;
        case Health::kOutOfRange:  return SmokeFail::kOutOfRange;
        case Health::kGap:         return SmokeFail::kNone;  // gap is not a fail
        case Health::kOverflow:    return SmokeFail::kFifoOverflow;
        case Health::kError:       return SmokeFail::kUnknown;
    }
    return SmokeFail::kUnknown;
}

}  // namespace helmkit::drivers
