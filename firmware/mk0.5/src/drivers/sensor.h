// HelmKit Mk0.5 — Sensor base interface.
//
// Every driver in src/drivers/ conforms to this. Reason: during the
// May-20 -> June-1 blackout, Wave-2 sensors (AD8232, MAX30205) will be
// added with only free-tier AI available. A uniform interface lets that
// future-AI clone the MAX30102 pattern mechanically rather than re-deriving
// architecture from scratch.
//
// The interface is intentionally minimal. A driver implements:
//   - begin(bus, cfg)     -- one-shot init, returns ok/fail
//   - pump(logger)        -- non-blocking drain; called from main loop
//   - health()            -- last-known sensor health (idempotent read)
//   - name()              -- channel name (matches docs/SCHEMA.md §2)
//
// Drivers do NOT inherit virtually; this is duck-typed at compile time by
// the dispatcher. Reason: vtables waste flash on a 4 MB partition and the
// driver set is closed (no plugin loading at runtime).

#pragma once

#include <Wire.h>
#include <stdint.h>

#include "drivers/smoke_result.h"

namespace helmkit::drivers {

enum class Health : uint8_t {
    kUninit = 0,   // begin() not yet called
    kOk,
    kNoAck,        // I2C address did not ACK
    kOutOfRange,   // last sample outside calibrated range
    kGap,          // sensor not in contact / leads off
    kOverflow,     // FIFO or driver-internal overflow
    kError,        // catch-all
};

inline const char* health_str(Health h) {
    switch (h) {
        case Health::kUninit:      return "uninit";
        case Health::kOk:          return "ok";
        case Health::kNoAck:       return "no-ack";
        case Health::kOutOfRange:  return "out-of-range";
        case Health::kGap:         return "gap";
        case Health::kOverflow:    return "overflow";
        case Health::kError:       return "error";
    }
    return "?";
}

// Concept (compile-time contract). Drivers do not inherit; the dispatcher
// templates over them. Documented here so future-AI knows what's required.
//
//   class MyDriver {
//   public:
//       bool begin(TwoWire& bus, const MyDriverConfig& cfg);
//       template <typename Logger> size_t pump(Logger& log);
//       Health health() const;
//       static constexpr const char* name();        // channel name
//       SmokeResult smoke_test(TwoWire& bus);       // L0 gate test
//   };

}  // namespace helmkit::drivers
