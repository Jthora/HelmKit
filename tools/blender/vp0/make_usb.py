#!/usr/bin/env python3
"""
make_usb.py -- build the USB print folder for the vp0.17 set (Track P):  helmkit/<filament-colour>/<part>/

Printer: QIDI X-Max 3 (325 x 325 x 315 mm, enclosed, direct drive, 0.4 mm nozzle, textured PEI plate), sliced in
QIDI Studio. For every part in the print-one set it writes, under <out>/helmkit/<colour>/<part>/:
    <part>.stl           the generated part, print orientation (from 3D-Models/HelmKit/_generated/vp0)
    <part>.3mf           a QIDI Studio project: the part centred on the X-Max 3 plate with the machine, filament and
                         process presets and this part's overrides (walls, infill, brim, supports, layer height)
                         embedded. Open it in QIDI Studio, press Slice, then Export G-code (or Print). Nothing to type.
    <part>_settings.txt  the presets and every override, to check the sidebar against or to set by hand
    <part>_notes.txt     the generator's print note (orientation, supports, assembly hardware)
plus helmkit/MANIFEST.md (one row per part: colour, quantity, presets, overrides, budget, grams), helmkit/PRINT_LOG.md
(the log template with the triage rule and the coupon calibration table) and helmkit/README.md (the QIDI Studio steps).

Why projects and not g-code: QIDI Studio 02.06.00.51's command line exports projects and merged settings but crashes
when asked to slice (a null option in its multi-filament update; reproduced with its own exported project files), so
the slice step is done in the app. The project is written by the app's own command line from its bundled X 3 Series
presets, flattened (the command line cannot follow "inherits" without a QDT vendor folder this build does not ship).

Materials: the prototype prints in PLA only. The one PETG spool was 5+ years old and cost an evening in first-layer
failures, material welding to the nozzle and finally a jam (2026-09-16). Drying helped but did not make it dependable,
and a one-shot campaign is the wrong place to nurse a marginal spool. The X-Max 3 can print PAHT-CF and PC-CF (hardened
nozzle, 350 C hotend, chamber heater) and those spools wait for the beta.

Colours: everything in black PLA from one spool (2026-09-29: switching spools spoils print quality). The PETG
profiles further down are kept, unused, because PETG returns for the beta parts on a fresh spool.

Run:  python3 tools/blender/vp0/make_usb.py [--out helmkit] [--only part,part] [--no-3mf]
The small-parts plates (silver_small_parts, black_small_parts) are built first by make_usb_plates.py (Blender).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GEN = ROOT / "3D-Models/HelmKit/_generated/vp0"

APP = Path("/Applications/QIDIStudio.app")
BIN = APP / "Contents/MacOS/QIDIStudio"
PROFILES = APP / "Contents/Resources/profiles"
SERIES = "X 3 Series"                      # the vendor bundle that holds the X-Max 3
MACHINE = "X-Max 3 0.4 nozzle"
PROCESS = "0.20mm Standard @XMax3"
PROCESS_FINE = "0.16mm Optimal @XMax3"     # the dome
BED_TYPE = "Textured PEI Plate"
NOZZLE = "hardened_steel"   # the high-temperature hotend is what is installed (2026-09-15); "brass" for the stock one
# Steel conducts heat about a third as well as brass, so the melt at the tip runs 5 to 10 C under the heater's reading.
# Added to every nozzle temperature while the steel nozzle is in: PETG +10 (the spool's 220 reads 230 at the heater),
# PLA +5. Zero for brass. The temperature tower is the check.
NOZZLE_TEMP_ADD = {"hardened_steel": {"petg": 10, "pla": 5}, "brass": {"petg": 0, "pla": 0}}[NOZZLE]
# PETG is laid onto the plate, not pressed in: it wants the nozzle 0.02 to 0.06 mm higher than the Z offset that is right
# for PLA. The printer runs Klipper. The filament start G-code (carried by the project, unlike printer settings) runs right
# after the machine's purge line, with the nozzle at the first layer height: it lifts the nozzle by the raise and then
# G92 renames that height back to the first layer height, so every Z the slicer emits afterwards sits that much higher.
# G92 lives in Klipper's base position, which G28 resets, and the machine start G-code homes at every print: a cancelled
# PETG print leaves nothing behind and no end G-code is needed. (SET_GCODE_OFFSET, the other kind of Z offset, survives
# homing, which is why it is NOT used: it lingered after a cancel and would have compounded.) The screen's live Z
# adjustment still works on top of it.
PETG_Z_RAISE = 0.04
PETG_FIRST_LAYER = "0.28"     # the PETG first layer height (MATERIAL_PROCESS); G92 below names this height after the lift
PETG_GCODE = dict(filament_start_gcode=[f"; Filament start gcode\nG91\nG1 Z{PETG_Z_RAISE} F600 ; helmkit: PETG is laid, not pressed\nG90\n"
                                        f"G92 Z{PETG_FIRST_LAYER} ; helmkit: the raise now lives in the G92 base, cleared by the next print's G28"],
                  filament_end_gcode=["; Filament-specific end gcode \n;END gcode for filament"])
# Filament presets: the generic ones are the safe default for spools of unknown brand (lower volumetric limits,
# QIDI's own temperatures for this hotend). If a spool is QIDI's own, use its preset instead: "QIDI PLA Rapido Matte",
# "QIDI PLA Basic", "QIDI PETG Basic" ... (names in profiles/X 3 Series/filament, each "@Qidi X-Max 3 0.4 nozzle").
FILAMENT = {"pla": "Generic PLA @Qidi X-Max 3 0.4 nozzle", "petg": "Generic PETG @Qidi X-Max 3 0.4 nozzle"}
# Overrides on the filament presets, from the spools on hand. The silver PETG spool says 220 C (the generic preset
# runs 250 with 240 on the first layer), so PETG prints at the spool's number from layer two; at 220 the melt flows
# slower, so its volumetric cap comes down from 12 to 8 mm3/s (the outer walls then run near 95 mm/s instead of 200).
# The FIRST layer runs at the preset's 240 (230 here + the steel nozzle's 10) with the plate at 85: at 220 the PETG did
# not wet the textured plate (coupon A, 2026-09-15). Not hotter: over-hot PETG sticks to the nozzle and blobs. The
# first layer is the plate-wetting layer; the label's number is for the layers above it.
# Retraction for PETG: Jordan's test values from the first coupon (2026-09-15) on top of the machine preset's 1 mm /
# 30 mm/s / 0.4 mm z-hop; these are the filament's "Setting Overrides" (nil = use the printer's). Revise from the log.
# PLA: the preset's 220 / 210 stands until a spool says otherwise.
FILAMENT_OVERRIDES = {"petg": dict(nozzle_temperature=["220"], nozzle_temperature_initial_layer=["225"], textured_plate_temp_initial_layer=["85"],
                                   filament_max_volumetric_speed=["8"],
                                   # z-hop 0.2 not 0.6: a deep lift gives the tip time to ooze and the ooze lands on the fill as
                                   # the blob that catches; 2 mm minimum travel so the short hops between the fill segments
                                   # around the holes do not retract and restart at all.
                                   filament_retraction_length=["1.25"], filament_retraction_speed=["35"], filament_z_hop=["0.2"],
                                   filament_retraction_minimum_travel=["2"],
                                   # The stock PETG preset runs the chamber exhaust at 100 % for the whole print: a draft of
                                   # room air across the plate, and one edge of coupon A lifted on the third try. PETG has no
                                   # fumes worth filtering; the fan stays off.
                                   activate_air_filtration=["0"], during_print_exhaust_fan_speed=["0"],
                                   **PETG_GCODE),
                      # PLA stays on the stock preset: it has printed reliably on this machine for a long time,
                      # coupons A and B included. Roster A17 wants the fan off for three layers on anything over
                      # 100 mm, which is the first lever to pull IF a large part warps -- pass it per part as
                      # _filament=dict(close_fan_the_first_x_layers=["3"]). Not applied to anything yet.
                      "pla": dict(textured_plate_temp_initial_layer=["65"])}   # 65 C for layer 1 only (60 after): the arm-tip adhesion
# colour folder -> (material, preview colour, density g/cm3)
# No PETG in the prototype: the only PETG spool was 5+ years old and cost an evening in first-layer failures, material
# welding to the nozzle and finally a jam (2026-09-16). Drying helped but did not make it dependable, and a one-shot
# campaign is the wrong place to nurse a marginal spool. The PETG profiles above stay for the beta, unused for now.
# Two colours, ONE switch (Jordan, 2026-09-29/10-08: "black is priority: switching spools spoils print quality"; 2 black
# PLA spools and 1 grey): every black part prints first, then the spool changes once to grey for the visible shells and
# never back. (2026-09-29 I misread that as "all black" and moved every grey row to black; restored 2026-10-08.)
COLOURS = {"grey-pla": ("pla", "#9A9A9A", 1.24), "black-pla": ("pla", "#202020", 1.24)}

# ---------------------------------------------------------------------------------------------------------------
# process overrides (QIDI Studio keys, values as the presets spell them). Everything else is the preset's: speeds,
# temperatures, fans, retraction 1 mm, z-hop 0.4, elephant's foot 0.15, pressure advance.
# ---------------------------------------------------------------------------------------------------------------
COMMON = dict(wall_loops="3", top_shell_layers="5", bottom_shell_layers="4", sparse_infill_pattern="gyroid",
              sparse_infill_density="20%", brim_type="no_brim", skirt_loops="0", skirt_distance="3",
              seam_position="aligned", enable_support="0", support_type="normal(auto)", support_top_z_distance="0.2",
              support_object_xy_distance="0.8", curr_bed_type=BED_TYPE,
              # THE FIRST LAYERS, for every part (2026-09-29: "the real problem is simply the first few layers"). No skirt (it
              # peeled and was dragged at the cradle's arm tip); layer 1 at 20/25 mm/s; solid layers CONCENTRIC (the preset's
              # short zig-zag strokes at 250 mm/s and 10000 mm/s2 were the violence on layer 2); fill speeds and sparse
              # acceleration moderated; walls and everything else stock. The 65 C first-layer plate is in the PLA overrides.
              initial_layer_speed=["20"], initial_layer_infill_speed=["25"],
              bottom_surface_pattern="concentric", internal_solid_infill_pattern="concentric",
              internal_solid_infill_speed=["120"], sparse_infill_speed=["200"], sparse_infill_acceleration=["5000"])
BRIM = dict(brim_type="outer_only", brim_width="5")
WIDE_BRIM = dict(brim_type="outer_only", brim_width="8")
# CAREFUL: tall, thin, low-contact parts (Track P, 2026-09-25). The stock 0.20 Standard preset prints layer 1 at 30-40 mm/s
# and 500 mm/s2, then jumps on layer 2 to inner walls at 300, outer 200, solid infill 250, sparse 270, at 5000-10000 mm/s2:
# a 7-20x step. On the cradle's 7 mm band the solid bottom layers became thousands of short zig-zag strokes at full
# acceleration, violent enough to wreck the print and to tug a part standing on 9 % of its footprint (Jordan's third try).
# Here: every speed a third or less, accelerations 2000-3000, bottom and solid layers CONCENTRIC (they follow the band
# instead of crossing it), and a brim on BOTH sides of the band (outer-only left the inside, where every node meets the
# band, without any). Costs print time; buys a print that finishes.
# GENTLE_START (2026-09-29) replaces CAREFUL on every part. Jordan: the frames and the whole-print slowdown were overkill;
# the real problem is the first few layers, after which the printer does well. The first cradle failures were (a) the jump
# from a slow first layer to the preset's solid bottom layers, laid as short zig-zag strokes at 250 mm/s and 10000 mm/s2,
# and (b) the skirt and brim peeling at an arm tip on layer 1. So: layer 1 fixed (no skirt, 20 mm/s, 65 C plate, brim on
# both sides), solid layers CONCENTRIC (no short strokes), fill speeds and sparse acceleration moderated; walls and the rest
# stock. QIDI Studio's "slow down by height" keys (enable_height_slowdown, slowdown_*) are read by its settings and GUI code
# but by nothing that writes g-code in the public source, so no per-height ramp is relied on.
GENTLE_START = dict(brim_type="outer_and_inner", brim_width="8")   # the first-layer settings moved into COMMON (every part);
                                                                   # this is now only the brim on BOTH sides, for long thin parts
CAREFUL = dict(outer_wall_speed=["60"], inner_wall_speed=["90"], sparse_infill_speed=["100"], internal_solid_infill_speed=["80"],
               top_surface_speed=["60"], gap_infill_speed=["50"], bridge_speed=["30"], travel_speed=["250"],
               default_acceleration=["3000"], outer_wall_acceleration=["2000"], inner_wall_acceleration=["3000"],
               sparse_infill_acceleration=["3000"], top_surface_acceleration=["2000"], travel_acceleration=["5000"],
               bottom_surface_pattern="concentric", internal_solid_infill_pattern="concentric",
               brim_type="outer_and_inner", brim_width="10",
               # attempt 4 failed on its FIRST layer: the skirt (2 lone loops outside the brim, across the open U) and the brim
               # peeled at an arm tip and the nozzle dragged them. No skirt, a slower first layer, a hotter plate and nozzle for it.
               skirt_loops="0", initial_layer_speed=["20"], initial_layer_infill_speed=["25"],
               _filament=dict(textured_plate_temp_initial_layer=["65"], nozzle_temperature_initial_layer=["215"]))
# Process overrides by material, applied over COMMON and under the part's own. PETG at 220 wants slower walls than the
# preset's 200 / 300 (the flow cap would throttle them anyway; these keep the estimate honest and the ringing down),
# slow bridges (the tunnel ceilings and the pod bridges sag at 50), no travel across the outer walls between islands
# (strings between the coupon posts), and a wider support gap because PETG supports weld on.
MATERIAL_PROCESS = {"petg": dict(outer_wall_speed=["120"], inner_wall_speed=["180"], bridge_speed=["30"], reduce_crossing_wall="1",
                                 support_top_z_distance="0.25",
                                 # PETG is laid, not squished: a Z offset that is right for PLA is too close for PETG, the
                                 # squeezed melt sticks to the (steel) nozzle, rides up behind it in a ripple and is torn
                                 # off on the next pass (coupon A, 2026-09-15). A thicker first layer at a walking pace is
                                 # the slicer's half of the cure; the other half is +0.02 to +0.05 on the printer's Z offset.
                                 initial_layer_print_height=PETG_FIRST_LAYER, initial_layer_speed=["20"], initial_layer_infill_speed=["20"],
                                 # The first-layer FILL caught where the walls had not (coupon A, second try): dozens of adjacent
                                 # lines each butting into the wall pile a ridge at the junctions when the flow is a few
                                 # percent high, and PETG scraped off a ridge sticks to the steel tip. 8 % less material on
                                 # the first layer only (a Developer-mode key in the app; the project carries it regardless).
                                 initial_layer_flow_ratio="0.92",
                                 # Concentric bottom surface: the diagonal fill has two wall junctions per line, hundreds
                                 # per layer, and each is where the tip caught (coupon A, third try); loops that follow the
                                 # walls and the holes have a handful. Applies to the bottom-most layer only.
                                 bottom_surface_pattern="concentric"),
                    "pla": {}}

# ---------------------------------------------------------------------------------------------------------------
# the print-one set: (part file, colour, quantity, note, per-part overrides; "_process" picks the process preset)
# ---------------------------------------------------------------------------------------------------------------
PARTS = [
    # first prints
    ("fit_coupon_d1",     "black-pla",   1, "coupon D1 v2, the CRADLE GATE: every hole the cradle depends on, sized to the nails in the box. Pin-lock ladder 1.6-1.9 for the 16 ga, two U-pin pairs, horizontal 2.7 / 2.9 / 3.1 / 3.4 round + teardrop for the 12 ga tenon nail and the printed plunger, M3 tap / clear, M4 clear, the Ø4 blind sockets, both Ø8 socket rows (bed-face row is the cradle's own condition), a chamfered strap-slot pair for 12 mm webbing, the loose peg and a printed Ø3.2 plunger pin", dict(**WIDE_BRIM)),
    ("band_gauge_front",  "black-pla",   1, "head-fit gauge: wear it before the cradle prints",
                                            dict(enable_support="1", support_type="normal(auto)", support_threshold_angle="40", support_on_build_plate_only="1", **BRIM)),
    ("port_drill_guide",  "black-pla",   1, "drill guide for the 8 mm pegs' cross holes", {}),
    # cradle set (PETG)
    ("cradle_front_first_layers", "black-pla", 1, "FIRST-LAYER TEST for the cradle: its bottom 0.6 mm with the cradle's own settings and brim. Minutes, not hours. Every line flat and fused, the brim stuck all round, the arm tips above all; fix the plate or the Z offset before the cradle", dict(sparse_infill_density="40%", **GENTLE_START)),
    ("cradle_front",      "black-pla", 1, "the cradle: GENTLE START (no skirt, first layer 20 mm/s on a 65 C plate, concentric solid layers, fill capped, walls stock), 8 mm brim INSIDE AND OUT, PRINT cradle_front_first_layers FIRST, fan off for 3 layers (preset), door closed; leave the printer alone", dict(sparse_infill_density="40%", **GENTLE_START)),
    ("rear_band_half",    "black-pla", 1, "the LEFT half; GENTLE START, 8 mm brim both sides", dict(sparse_infill_density="40%", **GENTLE_START)),
    ("rear_band_half_R",  "black-pla",   1, "the RIGHT half (v0.18): the left turned over, with its node end and tenon rebuilt for the right node. The old right half (a second copy of the left) cut 18 mm into the right node: keep it as a spare LEFT. Supports ON (build plate only): the tenon's underside starts as a 15 x 5 mm island 5 mm up", dict(enable_support="1", support_type="normal(auto)", support_on_build_plate_only="1", support_threshold_angle="30", **GENTLE_START)),
    ("cover_front",       "black-pla", 2, "two (one flipped); the file holds the strip in pieces (gaps at the tunnel stations); standing, brim", BRIM),
    ("cover_bottom",      "black-pla", 2, "two; 1 mm strips, flat", {}),
    ("cover_rear",        "black-pla", 2, "two; standing, brim", BRIM),
    ("cover_rear_in",     "black-pla", 2, "two; standing, brim", BRIM),
    ("silver_small_parts","black-pla", 1, "one plate: 2 knob clips, 2 visor sliders, 2 cover_side strips (small parts print together so each layer cools)", BRIM),
    # nape module + pads (black)
    ("nape_core_base",    "black-pla",   1, "the nape pin-lock block + junction bay, standing on its bottom end; GENTLE START, 8 mm brim both sides; pin-lock holes 2.3 / 2.5 for the 16 ga nails", dict(**GENTLE_START)),
    ("nape_core_cap",     "black-pla",   1, "belt-only cap", {}),
    ("pad_front",         "black-pla",   1, "standing on its bottom edge; brim", BRIM),
    ("carrier_ppg",       "black-pla",   1, "plug down", {}),
    ("carrier_eda",       "black-pla",   2, "two; plug down", {}),
    ("pad_hub_L",         "black-pla",   1, "outer face down", {}),
    ("pad_hub_R",         "black-pla",   1, "outer face down", {}),
    ("pad_rear_L",        "black-pla",   1, "outer face down", {}),
    ("pad_rear_R",        "black-pla",   1, "outer face down", {}),
    # combat trim
    ("sensor_bar",        "grey-pla",     1, "on its bottom face; brim", BRIM),
    ("bar_carrier",       "black-pla",   1, "flat", {}),
    ("port_coupler",      "black-pla", 2, "REPRINT of the two port couplers (the crown arch feet into the hub node sockets), now LYING on a flat: standing, the 30 mm pegs kept losing the plate and would have been weakest exactly where they are bent", dict(**WIDE_BRIM)),
    ("black_small_parts", "black-pla",   1, "one plate: 2 bar pins, 3 button caps, 2 port plugs, 4 flush plugs, 2 port couplers", BRIM),
    # full trim (grey PLA shells, black PLA structure and internals; all black parts print before the one switch to grey)
    ("disk_dome_first_layers", "grey-pla",  1, "FIRST-LAYER TEST for the dome: its bottom 0.64 mm (four 0.16 layers), the rim flat inside its saddle plate, with the dome's own layer height and brim. Minutes, not seven hours: the saddle and brim stuck flat all round, nothing lifting at the plate's ends", dict(_process=PROCESS_FINE, **WIDE_BRIM)),
    ("disk_dome",         "grey-pla",     2, "two; ON EDGE on the rim flat inside its PRINTED SADDLE (92 x 30 plate, six fins necked to the rim: snap the 0.8 mm necks off afterwards and trim the nubs), 0.16 mm layers, tree supports (interior only get built: the shell is under 19 deg; the apex boss, the rim crown and the two lowest screw bosses are what they hold), wide brim, 122 mm tall; print one, then the other",
                                            dict(_process=PROCESS_FINE, sparse_infill_density="15%", enable_support="1", support_type="tree(auto)", support_threshold_angle="25",
                                                 support_top_z_distance="0.16", support_bottom_z_distance="0.16", outer_wall_speed=["80"], **WIDE_BRIM)),
    ("disk_back_L",       "black-pla",   1, "flat, boss up", {}),
    ("disk_back_R",       "black-pla",   1, "flat, boss up", {}),
    ("disk_knob",         "black-pla", 2, "two; knob face down, shaft up; brim", BRIM),
    ("nexus_L",           "black-pla", 1, "inner face down, stalk up; 40 % infill", dict(sparse_infill_density="40%")),
    ("nexus_R",           "black-pla", 1, "inner face down, stalk up; 40 % infill", dict(sparse_infill_density="40%")),
    ("nexus_spool",       "black-pla", 2, "two; plate down; near solid", dict(sparse_infill_density="80%")),
    ("coil_former",       "black-pla",   4, "four (two per disk); flat, flange down", {}),
    ("bay_spool",         "black-pla",   1, "flat", {}),
    ("crown_arch_half",   "grey-pla",     2, "two; on edge, ridged face up; brim", dict(**GENTLE_START)),
    ("apex_block",        "grey-pla",     1, "LYING on its side (M4 head counterbore down, nut pocket up): standing on end it tore off the plate halfway up", dict(**WIDE_BRIM)),
    ("brow_center",       "grey-pla",     1, "standing on the bottom face; brim", BRIM),
    ("brow_lid",          "grey-pla",     1, "flat, outer face down (transparent PETG is the alternative if the LEDs should shine through)", {}),
    ("brow_rail_L",       "grey-pla",    1, "lying on the ring face", {}),
    ("brow_rail_R",       "grey-pla",    1, "lying on the ring face", {}),
    ("brow_link_L",       "grey-pla",    1, "standing on the bottom edge; brim", BRIM),
    ("brow_link_R",       "grey-pla",    1, "standing on the bottom edge; brim", BRIM),
    ("pylon_base",        "grey-pla",     2, "two; UPRIGHT on the block, hinge slot up (was inverted on its ear tops: a 43.5 mm tower on ~208 mm2, the ratio that tore the apex block off)", dict(**WIDE_BRIM)),
    ("pylon_peg",         "black-pla",     2, "two; LYING on the flat like the port couplers; epoxy into the base's socket", dict(**WIDE_BRIM)),
    ("pylon_blade",       "grey-pla",     2, "two; on the flat inner face; 12 % gyroid (modelled solid)", dict(sparse_infill_density="12%")),
    ("pylon_knob",        "grey-pla",     2, "two; flat", {}),
    # electronics housings (black)
    ("core_pod_nape",     "black-pla",   1, "open side up", {}),
    ("core_pod_lid_nape", "black-pla",   1, "outer face down", {}),
    ("core_pod_slab",     "black-pla",   2, "two (slab option); open side up", {}),
    ("core_pod_lid_slab", "black-pla",   2, "two (slab option); outer face down", {}),
    ("core_socket_foot",  "black-pla",   2, "two (slab option); inverted, peg up", {}),
    ("belt_pack",         "black-pla",   1, "open side up", {}),
    ("belt_pack_lid",     "black-pla",   1, "outer face down", {}),
]

# P1 figures (Track P section 3): the Cura 4.8 pass at Ender-class speeds, one piece, 3 walls, 20 % infill.
# Hours are an upper bound for the X-Max 3 (its Standard preset runs the walls at 200 to 300 mm/s); grams carry over
# (same walls and infill). The real figures come from QIDI Studio when the part is sliced; write them in the log.
P1 = {
    "apex_block": (1.32, 17), "bar_carrier": (0.1, 1), "bar_pin": (0.03, 0), "bay_spool": (0.48, 6),
    "belt_pack": (5.28, 62), "belt_pack_lid": (2.62, 30), "brow_center": (4.78, 60), "brow_lid": (1.18, 14),
    "brow_link_L": (0.58, 8), "brow_link_R": (0.58, 8), "brow_rail_L": (1.02, 13), "brow_rail_R": (1.02, 13),
    "button_cap_l": (0.07, 1), "button_cap_s": (0.03, 0), "carrier_eda": (0.13, 2), "carrier_ppg": (0.2, 2),
    "coil_former": (1.85, 21), "core_pod_lid_nape": (0.97, 11), "core_pod_lid_slab": (0.43, 5),
    "core_pod_nape": (1.87, 21), "core_pod_slab": (1.73, 19), "core_socket_foot": (0.52, 6), "cover_bottom": (0.07, 1),
    "cover_front": (0.13, 2), "cover_rear": (0.08, 1), "cover_rear_in": (0.05, 1), "cover_side": (0.03, 0),
    "cradle_front": (8.15, 98), "cradle_front_first_layers": (0.25, 3), "port_coupler": (0.3, 2), "disk_dome_first_layers": (0.2, 3), "crown_arch_half": (1.67, 22), "disk_back_L": (2.38, 28), "disk_back_R": (2.38, 28),
    "disk_dome": (7.3, 95), "disk_knob": (0.35, 4), 
    "knob_clip": (0.03, 0), "nape_core_base": (2.68, 31), "nape_core_cap": (0.58, 7), "nexus_L": (2.07, 28),
    "nexus_R": (2.08, 28), "nexus_spool": (0.78, 10), "pad_front": (0.27, 3), "pad_hub_L": (0.25, 3),
    "pad_hub_R": (0.25, 3), "pad_rear_L": (0.18, 2), "pad_rear_R": (0.18, 2), "port_coupler": (0.23, 2),
    "port_drill_guide": (0.52, 7), "port_plug": (0.17, 1), "port_plug_flush": (0.13, 1), "pylon_base": (0.75, 10), "pylon_peg": (0.2, 1),
    "pylon_blade": (1.85, 25), "pylon_knob": (0.25, 3), "rear_band_half": (1.83, 23), "rear_band_half_R": (1.83, 23), "sensor_bar": (2.32, 29),
    "visor_slider": (0.03, 1), "band_gauge_front": (1.55, 20), "fit_coupon_d1": (2.0, 60), 
    "silver_small_parts": (0.2, 2),    # 2 knob clips + 2 sliders + 2 cover_side
    "black_small_parts": (1.2, 12),    # 2 bar pins + 3 caps + 2 plugs + 4 flush plugs + 2 couplers
}


# ---------------------------------------------------------------------------------------------------------------
# presets: flatten the bundled inherits chain into one self-contained JSON the command line accepts
# ---------------------------------------------------------------------------------------------------------------
def _series_index() -> dict[str, dict[str, str]]:
    idx = json.load(open(PROFILES / f"{SERIES}.json"))
    return {kind: {e["name"]: e["sub_path"] for e in idx[f"{kind}_list"]} for kind in ("machine", "process", "filament")}


def flatten(kind: str, name: str, index: dict, overrides: dict | None = None) -> dict:
    """Merge a preset with everything it inherits (leaf wins), drop the chain, keep the system name as 'inherits'
    so the command line's printer/process compatibility check sees the right names."""
    chain, n = [], name
    while n:
        sub = index[kind].get(n, f"{kind}/{n}.json")       # the fdm_*_common bases are not in the index
        j = json.load(open(PROFILES / SERIES / sub))
        chain.append(j)
        n = j.get("inherits")
    m: dict = {}
    for j in reversed(chain):
        m.update(j)
    m["from"], m["type"], m["inherits"] = "User", kind, name
    if kind == "machine":   # the print pipeline dereferences these per-extruder keys; give it the single-extruder defaults
        m.update({"extruder_type": ["Direct Drive"], "nozzle_volume_type": ["Standard"], "extruder_variant_list": ["Direct Drive Standard"],
                  "printer_extruder_id": ["1"], "printer_extruder_variant": ["Direct Drive Standard"], "nozzle_type": [NOZZLE]})
    if overrides:
        m.update(overrides)
        # QIDI Studio opens a project by loading the preset NAMED in it and taking from the project's own values only the
        # keys listed here (PresetBundle::load_config_file_config); the command line copies this list into the project.
        # Without it every override is silently replaced by the stock preset (found on coupon A, 2026-09-15).
        m["different_settings_to_system"] = [";".join(overrides)]
    return m


def filament_preset(material: str, preview: str, index: dict, extra: dict | None = None) -> tuple[dict, dict]:
    """The flattened filament preset with the spool's overrides, the nozzle's temperature offset applied to both nozzle
    temperatures; returns (preset, the effective overrides for the settings sheet)."""
    base = flatten("filament", FILAMENT[material], index)
    ov = dict(FILAMENT_OVERRIDES[material])
    if extra:
        ov.update(extra)
    for k in ("nozzle_temperature", "nozzle_temperature_initial_layer"):
        ov[k] = [str(int(ov.get(k, base[k])[0]) + NOZZLE_TEMP_ADD[material])]
    base.update(ov)
    base["filament_colour"] = [preview]
    base["different_settings_to_system"] = [";".join(list(ov) + ["filament_colour"])]   # see flatten()
    return base, ov


def export_project(stl: Path, out_3mf: Path, presets: dict[str, dict], workdir: Path) -> str:
    """Have QIDI Studio's command line write a project (no slice) with the part centred on the plate. Returns ''
    or the error string."""
    files = {}
    for kind, cfg in presets.items():
        files[kind] = workdir / f"{kind}.json"
        files[kind].write_text(json.dumps(cfg, indent=1))
    result = workdir / "result.json"
    result.unlink(missing_ok=True)
    cmd = [str(BIN), "--debug", "1", "--load-settings", f"{files['machine']};{files['process']}", "--load-filaments", str(files["filament"]),
           "--arrange", "1", "--allow-rotations=0", "--export-3mf", out_3mf.name, "--outputdir", str(workdir), str(stl)]
    p = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)
    err = ""
    if result.exists():
        r = json.loads(result.read_text())
        if r.get("return_code", 0) != 0:
            err = r.get("error_string", "error")
    made = workdir / out_3mf.name
    if p.returncode != 0 and not err:
        err = f"exit {p.returncode}"
    if made.exists() and not err:
        shutil.move(str(made), str(out_3mf))
    elif not err:
        err = "no project written"
    return err


def hours(h: float) -> str:
    return f"{int(h)} h {int(round((h - int(h)) * 60)):02d}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "helmkit"))
    ap.add_argument("--only", default=None, help="comma-separated part names")
    ap.add_argument("--no-3mf", action="store_true", help="STL, settings and notes only (no QIDI Studio call)")
    args = ap.parse_args(argv)
    out = Path(args.out).resolve()
    only = set(args.only.split(",")) if args.only else None
    index = _series_index()
    work = Path(tempfile.mkdtemp(prefix="helmkit_usb_"))
    rows, errors = [], 0
    for part, colour, qty, note, extra in PARTS:
        if only and part not in only:
            continue
        stl = GEN / f"{part}.stl"
        if not stl.exists():
            print(f"MISSING {stl}", file=sys.stderr)
            errors += 1
            continue
        material, preview, density = COLOURS[colour]
        d = out / colour / part
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy2(stl, d / f"{part}.stl")
        sidecar = GEN / f"{part}.txt"
        if sidecar.exists():
            shutil.copy2(sidecar, d / f"{part}_notes.txt")
        extra = dict(extra)
        process = extra.pop("_process", PROCESS)
        fil_extra = extra.pop("_filament", {})
        overrides = dict(COMMON)
        overrides.update(MATERIAL_PROCESS[material])
        overrides.update(extra)
        err = ""
        fil, fil_ov = filament_preset(material, preview, index, fil_extra)
        if not args.no_3mf:
            presets = {"machine": flatten("machine", MACHINE, index),
                       "process": flatten("process", process, index, overrides),
                       "filament": fil}
            err = export_project(stl, d / f"{part}.3mf", presets, work)
            if err:
                errors += 1
        h, g = P1.get(part, (0.0, 0))
        with open(d / f"{part}_settings.txt", "w") as fh:
            fh.write(f"{part}  ({colour}, print {qty})\n{note}\n\n")
            fh.write(f"printer   QIDI X-Max 3, 0.4 mm {NOZZLE.replace('_', ' ')} nozzle (+{NOZZLE_TEMP_ADD[material]} C on the nozzle temperatures), {BED_TYPE.lower()}  (QIDI Studio printer preset: {MACHINE})\n")
            fh.write(f"filament  {FILAMENT[material]}\nprocess   {process}\n")
            fh.write(f"budget    up to {hours(h)} (P1 upper bound), about {g} g; the real figures are QIDI Studio's after Slice\n\n")
            fh.write("overrides on the process preset (what the sidebar should show as modified):\n")
            for k in sorted(overrides):
                fh.write(f"  {k} = {overrides[k]}\n")
            fh.write("\noverrides on the filament preset (the spool's numbers, plus the nozzle offset on the temperatures):\n")
            for k, v in fil_ov.items():
                fh.write(f"  {k} = {v[0].replace(chr(10), ' | ')}\n")
            if material == "petg":
                fh.write(f"\nZ: the filament start G-code lifts the nozzle {PETG_Z_RAISE} mm after the purge line and G92 renames that height to\n"
                         f"{PETG_FIRST_LAYER} (PETG is laid, not pressed). Homing at the next print start clears it: nothing to do after a cancel.\n")
            fh.write(f"\nopen {part}.3mf in QIDI Studio -> Slice plate -> Export G-code as {part}.gcode (or Print)\n")
        rows.append((colour, part, qty, note, process, extra, h, g, err))
        print(f"{colour:12s} {part:22s} x{qty}  {process:26s} {'ERR ' + err if err else 'ok'}")
    shutil.rmtree(work, ignore_errors=True)

    if only:
        # a partial rebuild describes a few parts; the manifest, log and README describe the whole set, so they stay as
        # they are (2026-09-26: an --only run had rewritten MANIFEST.md with one row)
        shutil.rmtree(work, ignore_errors=True)
        print(f"wrote {out}  ({len(rows)} parts, {errors} errors; --only: MANIFEST, PRINT_LOG and README left as they were)")
        return 1 if errors else 0

    # ---- manifest
    order = ["black-pla", "grey-pla"]
    lines = ["# HelmKit vp0.17 print manifest", "",
             "QIDI X-Max 3, QIDI Studio. One folder per part under `<colour>/`; each holds the STL, a QIDI Studio project with the presets and this part's overrides embedded, the settings sheet and the generator's print note. Open the project, Slice, Export G-code.",
             "Print order is the Track P gate order: coupons and gauge first, then the cradle set, then the combat trim, then the full trim. Nothing over two hours prints before the coupon it depends on has passed.",
             "Budget hours are the P1 upper bound (Cura pass at Ender-class speeds); the X-Max 3's presets are faster. Grams carry over (same walls and infill). Write QIDI Studio's own figures in PRINT_LOG.md.", "",
             "| colour | part | print | process preset | overrides beyond the common set | budget each | g each | note |", "|---|---|---|---|---|---|---|---|"]
    totals: dict[str, list[float]] = {}
    for colour in order:
        for r in rows:
            if r[0] != colour:
                continue
            c, part, qty, note, process, extra, h, g, err = r
            diff = ", ".join(f"{k} {v}" for k, v in extra.items())
            lines.append(f"| {colour} | {part} | {qty} | {process} | {diff or 'common'} | {hours(h)} | {g} | {note}{' **' + err + '**' if err else ''} |")
            tt = totals.setdefault(colour, [0.0, 0.0])
            tt[0] += h * qty
            tt[1] += g * qty
    lines += ["", "## Totals (all quantities)", "", "| colour | budget hours (upper bound) | grams |", "|---|---|---|"]
    for colour in order:
        if colour in totals:
            lines.append(f"| {colour} | {totals[colour][0]:.0f} | {totals[colour][1]:.0f} |")
    lines += ["", "## Presets", "",
              f"Printer `{MACHINE}` with the {NOZZLE.replace('_', ' ')} nozzle (nozzle temperatures +{NOZZLE_TEMP_ADD['pla']} C for the steel's poorer conduction), plate `{BED_TYPE}`. "
              f"Filament: PLA `{FILAMENT['pla']}` (preset 220 / 210 first layer plus the offset, bed 60, fan 100 %). "
              f"Process `{PROCESS}` (`{PROCESS_FINE}` for the dome).",
              "", "**common overrides**: " + ", ".join(f"{k} {v}" for k, v in COMMON.items()),
              "", "**PETG process overrides**: " + ", ".join(f"{k} {v}" for k, v in MATERIAL_PROCESS["petg"].items()),
              "", "Materials: PLA and PETG only for the prototype. The PAHT-CF and PC-CF spools and the hardened nozzle wait for the beta.",
              "", "Verify the first coupon's first layer before trusting the projects for anything larger. If a project opens with the wrong presets, set them from the part's `_settings.txt`."]
    (out / "MANIFEST.md").write_text("\n".join(lines) + "\n")

    # ---- log template
    (out / "PRINT_LOG.md").write_text("""# HelmKit print log

One entry per print. Copy the block. Every problem goes in exactly one bin; the bin says where the fix lives.

| bin | what it is | where the fix goes |
|---|---|---|
| slicer | adhesion, warping, stringing, support, temperature, a first layer that did not stick | the override tables in `make_usb.py` or the QIDI Studio filament preset; re-export the project, no geometry change |
| fit | a mating dimension off by a measured amount | the calibration table below, then one number in `canon.py`, then that part regenerated and re-exported |
| design | a feature that cannot print or does not do its job | the generator; then `print_check.py`, `print_matrix.py` and both assemblies re-run before the reprint |
| accept | a drill pass, a file, glue, a shim | the assembly step in the spec (section 6) |

## Calibration table (coupons A and B)

Everything prints in PLA now, so there is one set of offsets rather than one per material. Measure the hole with
calipers, then test the fit by hand. The delta is what canon has to move by before any large part is regenerated.

Hardware at the bench: calipers, a 12 ga nail (2.68), a 16 ga nail (1.59) and a second one bent into a U with its legs 3.9 mm apart, 12 mm webbing if to hand, an M3 thread-forming screw, an M3 nut, an M4 screw and nut.
The Ø8 peg and the bayonet stub print as part of coupon A. Coupon C needs no hardware at all: its base and dial are
both printed, so it can be tested the moment it comes off the plate.

| fit | coupon | modelled | how to test | measured | delta | canon knob | new value |
|---|---|---|---|---|---|---|---|
| 12 ga tenon nail, horizontal, round + teardrop | d1 v2 | 3.10 teardrop (2.68 shank) | the nail slides through the 3.1 teardrop under its own weight | first round to pass 3.1; teardrop passes at 2.9 (very snug) | 2026-09-25 | `PIN_DIA` 2.9 | stands |
| printed Ø3.2 plunger in printed 3.4 | d1 v2 | 3.40 | the loose printed pin slides in the vertical 3.4 and the horizontal 3.4s without force | does not fit 3.4 or 3.6 (3.8 untested) | 2026-09-25 | index plunger, Phase 3 | keeper 3.9 with a 3.0 shank |
| M3 thread-forming | d1 v2 | 3.00 | an M3 screw cuts its own thread without splitting the plate | 2.9 very tight but takes it; 3.4 smooth | 2026-09-25 | `M3_TAP_DIA` | 3.0 applied |
| 16 ga pin-lock, vertical | d1 v2 | 2.30 snug / 2.50 clear (1.59 shank) | the nail presses into the snug hole with light taps and drops through the clear one | 1.6 to 1.9 none; 2.2 hard press (coupon B); 2.5 perfect | 2026-09-25 | `NAPE_PINLOCK_PIN` | 2.3 / 2.5 applied |
| U-pin pair | d1 v2 | 1.8 and 1.9 pairs, legs 3.93 apart | a bent 16 ga nail drops in to its bridge and pulls out by it | not testable: both pairs under size (see the row above); retest on the pin-lock body at 2.5 | 2026-09-25 | `NAPE_PINLOCK_PIN` slot | Phase 2 |
| strap slot pair, 12 mm webbing | d1 v2 | 14 x 4, 12 apart, 1 mm chamfers | webbing threads down one slot and up the other and runs over the chamfers | skipped, no webbing | 2026-09-25 | `STRAP_SLOT`, `_PITCH`, `_CHAMFER` | test on the cradle |
| M4 clearance | d1 v2 | 4.60 | an M4 screw drops through | 4.4 snug; 4.6 and 4.8 drop | 2026-09-25 | `M4_CLEAR_DIA` | 4.6 applied |
| M3 clearance | d1 v2 | 3.80 | an M3 screw drops through | 3.4 threads smoothly; 3.6 shoves in; 3.8 by extrapolation | 2026-09-25 | `M3_CLEAR_DIA` | 3.8 applied |
| Ø8 peg in the socket, opens upward | d1 v2 | 8.50 | the printed peg slides in by hand with no rock | 8.3 snug / 8.5 smooth / 8.7 rattles | 2026-09-25 | `CYL_SOCKET_D` | 8.5 applied |
| socket cross-pin | A | 3.20 | a 3.2 nail passes through both walls and the peg | | | `PIN_DIA` | |
| bayonet drop and turn | H (after A, D2, E, F, G) | floor 3.8 under a lug at 4.0 | the stub drops in, turns ~107 deg up the ramp to the stop and seats snug-tight; the wrong way is blocked | snug-tight, both stubs, floor 3.8; 3.2 flat and 3.6 turn loose | 2026-09-20 | `BAYONET_CAM` (3.2, 3.8), `BAYONET_BOSS` 7.6 open, `BAYONET_BORE_CLEAR` 0.5, `BAYONET_NOTCH_CLEAR` 1.1 beyond the lug, `STALK_LUG` reach 2.6, `STALK_LUG_CHAMFER` 1.4, reverse block | applied to canon 2026-09-20; the knob-lock notch has no host until the lock post is designed |
| ratchet direction | C | one way | the dial clicks freely one way and locks solid the other | | | `NAPE_RATCHET_DIR` | |
| Ø8 peg, socket opening on the BED face | d1 v2 | 8.70 | turn the coupon over; the peg must enter without force | 8.3 no / 8.5 snug / 8.7 smooth / 8.9 rattles | 2026-09-25 | `CYL_SOCKET_BED_D` | 8.7 applied (the cradle's node tops) |
| horizontal hole, round vs teardrop | d1 v2 | 3.10 teardrop | the nail slips the teardrop; note whether the round one binds | 2.9 T very snug; 2.9 R no; 3.1 R + T pass; 3.4 R + T pass | 2026-09-25 | `PIN_DIA` 2.9 -> 3.1 teardrops | stands |
| M3 nut, sideways pocket | B | 5.70 | an M3 nut presses in and will not spin | | | `NEXUS_NUT_POCKET` | |
| ring on hub | B | 0.30 clearance | the ring turns freely on the hub without slop | | | `NEXUS_RING` | |
| Ø4 pin in 4.1 / 4.3 | B | 4.10 / 4.30 | a printed Ø4 pin is snug in 4.1 and free in 4.3 | | | `SENSOR_BAR pin_fit` | |
| 2 mm nail in 2.1 / 2.2 | B | 2.10 / 2.20 | snug in 2.1, clear in 2.2 | | | `NAPE_PINLOCK_PIN` | |

## Entries

### <date> <part> (<colour>, project <part>.3mf)
- printer state: X-Max 3, plate textured PEI, nozzle 0.4, chamber heater off, door <closed / ajar>, filament <brand/colour>, dried? y/n
- QIDI Studio: time <h:mm>, grams <g>, presets as in _settings.txt? y/n
- result: ok / failed at <layer or hour> / finished with defects
- measured: <fit, mm> ...
- problem bin: slicer / fit / design / accept
- action: <what changed, where (file + commit)>
- photo: <filename>
""")

    (out / "README.md").write_text(f"""# helmkit/ (USB print folder)

Printer: QIDI X-Max 3. Slicer: QIDI Studio. `<colour>/<part>/` holds `<part>.stl`, `<part>.3mf` (a QIDI Studio
project with the printer, filament and process presets and this part's overrides embedded), `<part>_settings.txt`
and `<part>_notes.txt`. `MANIFEST.md` lists every part with quantity, presets, budget and grams; `PRINT_LOG.md` is
the log to keep.

## Slicing a part

1. Open `<part>.3mf` in QIDI Studio (File > Open Project). If it asks whether to load the project's presets, load them.
2. The sidebar should show Printer `{MACHINE}`, Filament `{FILAMENT['petg']}` or `{FILAMENT['pla']}`, Process
   `{PROCESS}` (`{PROCESS_FINE}` for the dome), each marked modified, and the plate `{BED_TYPE}`. Compare with the
   part's `_settings.txt`; if anything differs, set it from that file.
3. Slice plate. Check the preview: a brim where the note asks for one, supports only on the dome and the gauge, the
   first layer on the plate. Write the time and grams in `PRINT_LOG.md`.
4. Export G-code as `<part>.gcode` next to the project (or Print over the network). One copy per project: for a
   second copy add an instance in the app once the first has printed well, or print the file again.
5. At the printer: the spool the folder is named for, textured PEI plate, chamber heater off, door ajar or the top
   vented (PLA softens in a closed warm chamber).

Colours: TWO, with ONE spool change. Print everything in `black-pla/` first (the structure, internals and housings), then
switch to grey once and print `grey-pla/` (the visible shells: domes, crown arch, apex, brow, pylons). Never switch back.

Order: coupons A, B, D2, E, F, G, H (printed 2026-09-15..20; the bayonet is in canon) -> d1 (the cradle gate) -> band gauge -> calipers, calibration table, regenerate ->
cradle -> rear halves + nape + pads + covers -> first wear -> sensor bar + carriers + small parts -> bench electronics ->
nexus, spools, disk backs, knobs -> one dome -> the rest.

Materials: PLA and PETG only for the prototype. The PAHT-CF and PC-CF spools and the hardened nozzle wait for the beta.

This folder is generated by tools/blender/vp0/make_usb.py from the generated set and is not tracked in git.
""")
    print(f"wrote {out}  ({len(rows)} parts, {errors} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
