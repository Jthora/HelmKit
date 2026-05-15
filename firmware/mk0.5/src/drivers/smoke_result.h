// HelmKit Mk0.5 — structured smoke-test result.
//
// Replaces `bool` smoke-test returns with a self-describing struct so that
// when a free-tier AI session debugs a failing gate during the May-20 ->
// June-1 blackout window, the failure mode is in the data, not in the head
// of the person who wrote the test.

#pragma once

#include <stdint.h>

namespace helmkit::drivers {

struct SmokeResult {
    bool ok;
    const char* reason;        // human-readable; NULL when ok
    uint32_t evidence_a;       // sensor-specific (e.g. sample count)
    uint32_t evidence_b;       // sensor-specific (e.g. overflow count)

    static SmokeResult pass(uint32_t a = 0, uint32_t b = 0) {
        return SmokeResult{true, nullptr, a, b};
    }
    static SmokeResult fail(const char* reason,
                            uint32_t a = 0, uint32_t b = 0) {
        return SmokeResult{false, reason, a, b};
    }
};

}  // namespace helmkit::drivers
