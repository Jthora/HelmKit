// HelmKit Mk0.5 — boot_id implementation.
#include "log/session.h"
#include <stdio.h>

namespace helmkit::log {

namespace {
uint64_t g_boot_id = 0;
}

uint64_t boot_id() {
    if (g_boot_id == 0) {
        // esp_random returns uint32_t; combine two for 64-bit.
        const uint64_t hi = esp_random();
        const uint64_t lo = esp_random();
        g_boot_id = (hi << 32) | lo;
        if (g_boot_id == 0) g_boot_id = 1;  // avoid sentinel collision
    }
    return g_boot_id;
}

const char* boot_id_hex(char out[17]) {
    snprintf(out, 17, "%016llx", (unsigned long long)boot_id());
    return out;
}

}  // namespace helmkit::log
