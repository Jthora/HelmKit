// HelmKit Mk0.5 — per-boot session identity.
//
// Closes critique F7 (session_id). Every boot mints a 64-bit nonce so that
// the Pi log-sink can disambiguate back-to-back sessions even when the
// operator forgets to label them.
//
// The boot_id is the canonical aggregation key for cross-line correlation
// inside one session. The session_id (set by the host log-sink, optional
// in the firmware) groups boots that belong to one experimental session.
// In Mk0.5 they are the same value; that distinction shows up at Mk1.5+.

#pragma once

#include <stdint.h>
#include <esp_random.h>

namespace helmkit::log {

// Lazily-initialized 64-bit boot identifier. Stable for the lifetime of
// this boot. Format on the wire: 16 lowercase hex chars.
uint64_t boot_id();

// Writes the boot_id to `out` (must be >=17 bytes) and returns it.
const char* boot_id_hex(char out[17]);

}  // namespace helmkit::log
