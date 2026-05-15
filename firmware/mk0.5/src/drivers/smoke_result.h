// HelmKit Mk0.5 — structured smoke-test result.
//
// Replaces `bool` smoke-test returns with a self-describing struct so that
// when a free-tier AI session debugs a failing gate during the May-20 ->
// June-1 blackout window, the failure mode is in the data, not in the head
// of the person who wrote the test.
//
// Wave F upgrade (2026-05-15): added structured `code` (SmokeFail) and
// `terminal_health` (Health). `reason` is retained as the human-readable
// note field. The combination of (code, terminal_health, evidence_a/b,
// reason) is the canonical wire shape of a kind:"error" NDJSON event.

#pragma once

#include <stdint.h>

#include "drivers/sensor.h"

namespace helmkit::drivers {

// Forward-decl. Full definition in drivers/smoke_fail.h. We don't include
// it here to avoid a header cycle (smoke_fail.h includes us indirectly via
// sensor.h is fine, but mutual TU inclusion via callers is messier).
enum class SmokeFail : uint16_t;

struct SmokeResult {
    bool ok;
    SmokeFail code;            // structured failure code (kNone when ok)
    Health terminal_health;    // sensor's last-known health at result time
    const char* reason;        // human-readable note; nullable when ok
    uint32_t evidence_a;       // sensor-specific (see docs/SCHEMA.md §2.2)
    uint32_t evidence_b;       // sensor-specific

    static SmokeResult pass(uint32_t a = 0, uint32_t b = 0,
                            Health th = Health::kOk) {
        return SmokeResult{
            true,
            static_cast<SmokeFail>(0),   // kNone
            th,
            nullptr,
            a, b,
        };
    }

    static SmokeResult fail(SmokeFail code,
                            const char* reason,
                            uint32_t a = 0, uint32_t b = 0,
                            Health th = Health::kError) {
        return SmokeResult{false, code, th, reason, a, b};
    }

    // Back-compat overload for callers not yet migrated to SmokeFail codes.
    // DEPRECATED: convert to the 5-arg form before Wave 2.
    static SmokeResult fail(const char* reason,
                            uint32_t a, uint32_t b) {
        return SmokeResult{false,
                           static_cast<SmokeFail>(65535),  // kUnknown
                           Health::kError,
                           reason, a, b};
    }
};

}  // namespace helmkit::drivers

