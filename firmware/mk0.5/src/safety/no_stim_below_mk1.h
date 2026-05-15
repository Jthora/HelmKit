// HelmKit Mk0.5 — compile-time safety guard.
//
// Mk0.5 has NO stim payload. Mk1.0 introduces the first stim driver. To
// prevent a future driver TU from accidentally being compiled into a
// Mk0.5 build (e.g. someone copies a stim file from a Mk1.0 branch),
// every stim translation unit MUST include this header and trip the
// static_assert if HELMKIT_MK < 100.
//
// HELMKIT_MK encoding: integer = Mk * 100. So Mk0.5 = 50, Mk1.0 = 100,
// Mk1.5 = 150, Mk2.0 = 200, etc. Defined in platformio.ini build_flags.
//
// Usage in a future stim driver:
//   #include "safety/no_stim_below_mk1.h"
//   HELMKIT_REQUIRE_STIM_GATE();
//
// This guard is BELT-AND-SUSPENDERS on top of the architectural rule that
// stim hardware is physically absent from Mk0.5 builds. Both should be
// true; if either is true the head is safe.

#pragma once

#ifndef HELMKIT_MK
#  error "HELMKIT_MK must be defined in platformio.ini build_flags"
#endif

#define HELMKIT_REQUIRE_STIM_GATE()                                          \
    static_assert(HELMKIT_MK >= 100,                                          \
        "Stim driver compiled into a sub-Mk1.0 build. Per HelmKit safety "    \
        "floor (PRIOR_ART.md K1/K5, BLACKOUT_PLAN.md Decision #5), no stim " \
        "payload may ship below Mk1.0. Remove the stim TU from this build " \
        "or bump HELMKIT_MK after explicit safety review.")
