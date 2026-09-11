#!/usr/bin/env python3
"""
stabilizer_field_model.py — what a coil in the HelmKit ear disk can actually do to tissue,
under ordinary electromagnetism (the wiki framework's alpha = 0 sub-theory).

Design doc: docs/psionic_engineering/stabilizer_derivation.md

The Mk1 Psi Stabilizer coil sits in the disk pod, coaxial with the disk axis that passes
through the brain core. This tool models that coil as two interleaved flat Archimedean
spirals (a bifilar pancake) wound from ordinary insulated wire, in either connection:

  opposing — Tesla series-opposing (US 512,340): adjacent turns carry opposite current.
             Magnetic field largely cancels, inter-winding voltage is large. This is the
             topology the wiki's Bifilar Coil Engineering page mandates (it maximises E²).
  aiding   — series-aiding: adjacent turns carry the same current. A plain N-turn pancake
             with twice the turns. Maximises B and therefore dB/dt.

For each connection it computes, by direct filament summation (Biot–Savart for B, the
vector potential A for the induced electric field, Coulomb line charges for the
electrostatic field), the fields at three points on and near the disk axis inside the head:

  scalp   the temple skin under the disk
  cortex  ~8 mm under the scalp, evaluated OFF axis at r = cortex_r (the induced E of a
          coaxial coil is azimuthal and vanishes on the axis)
  core    the brain core on the axis, the point the disks are centred on

and then answers the only question that matters for an entrainment design:

  How large an electric field does this coil put INTO cortical tissue, at what frequency,
  for what drive, and how does that compare with (a) the ICNIRP basic restriction on the
  in-situ electric field and (b) the field strengths at which transcranial stimulation is
  known to change neural activity?

Two physical facts the report makes explicit, because the wiki designs skip them:

  1. An externally applied (electrostatic / capacitive) E-field is screened by the
     conductive scalp. The in-tissue field is smaller than the applied field by
     roughly omega*eps0 / |sigma + i*omega*eps0*eps_r|, which is ~1e-5 at 40 kHz and
     ~1e-3 at 5 MHz for grey matter. At 40 kHz the wiki's E²-maximising bifilar coil
     therefore deposits essentially no E-field in the brain by ordinary electromagnetism.
     At MHz the displacement current through the scalp is no longer negligible: the
     E_static_tissue column is the SURFACE value (it decays inward as the current
     spreads), and it oscillates at the carrier, a frequency neurons cannot follow.
  2. Amplitude-modulating a MHz carrier at a slow envelope does NOT produce a slow
     in-tissue field. dB/dt is dominated by the carrier; tissue is linear at these levels
     and does not demodulate. An induced field at 7.83 Hz or 0.1 Hz requires driving the
     coil AT that frequency, where E_induced scales with f and is tiny.

Tissue parameters are Gabriel-class approximations for grey matter and are marked as such;
replace them from the IT'IS database before quoting. Exposure limits are the ICNIRP 2010
(1 Hz – 100 kHz) and ICNIRP 2020 (100 kHz – 300 GHz) general-public values; the numbers
are transcribed in EXPOSURE_LIMITS with their table references and should be checked
against docs/safety.md §2, which already verified the 2020 values.

Stdlib only (same discipline as tools/verify_psi_equations.py and tools/analyze_g2.py).

Usage:
    python3 tools/stabilizer_field_model.py                       # default disk coil, full report
    python3 tools/stabilizer_field_model.py --id 20 --od 100 --wire 0.511 --pitch 1.9 \
        --current 0.5 --voltage 50 --f 7.83 10 1e6 5e6
    python3 tools/stabilizer_field_model.py --json                # machine-readable

Exit code 0 always (this is a calculator, not a gate).
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
import sys

MU0 = 4e-7 * math.pi
EPS0 = 8.854187817e-12
C0 = 299792458.0
RHO_CU = 1.68e-8            # ohm·m, copper at 20 °C

# ---------------------------------------------------------------------------
# tissue (grey matter), Gabriel-class order-of-magnitude values — VERIFY against IT'IS
# ---------------------------------------------------------------------------
TISSUE_GREY = [
    # (f_Hz, sigma_S_per_m, eps_r)
    (1.0, 0.020, 4.0e7),
    (10.0, 0.028, 4.0e7),
    (100.0, 0.09, 3.9e6),
    (1e3, 0.10, 1.6e5),
    (1e4, 0.11, 3.9e4),
    (4e4, 0.12, 1.4e4),
    (1e5, 0.13, 3.9e3),
    (1e6, 0.16, 9.9e2),
    (5e6, 0.23, 4.4e2),
    (1e7, 0.29, 3.2e2),
    (1e8, 0.56, 80.0),
]


def tissue(f):
    """Log-log interpolate (sigma, eps_r) for grey matter at frequency f."""
    if f <= TISSUE_GREY[0][0]:
        return TISSUE_GREY[0][1], TISSUE_GREY[0][2]
    if f >= TISSUE_GREY[-1][0]:
        return TISSUE_GREY[-1][1], TISSUE_GREY[-1][2]
    for (f0, s0, e0), (f1, s1, e1) in zip(TISSUE_GREY, TISSUE_GREY[1:]):
        if f0 <= f <= f1:
            t = (math.log(f) - math.log(f0)) / (math.log(f1) - math.log(f0))
            return math.exp(math.log(s0) + t * (math.log(s1) - math.log(s0))), math.exp(math.log(e0) + t * (math.log(e1) - math.log(e0)))
    return TISSUE_GREY[-1][1], TISSUE_GREY[-1][2]


def screening_factor(f):
    """|E_inside / E_applied| for a quasi-static E-field normal to a conductive tissue boundary:
    continuity of total normal current density, (sigma + i w eps0 eps_r) E_in = i w eps0 E_out."""
    if f <= 0:
        return 0.0
    sigma, eps_r = tissue(f)
    w = 2 * math.pi * f
    return (w * EPS0) / abs(complex(sigma, w * EPS0 * eps_r))


# ---------------------------------------------------------------------------
# exposure limits (general public). ICNIRP 2010 Table 2 basic restrictions on in-situ E
# for CNS tissue of the head; ICNIRP 2010 Table 4 reference levels for B; ICNIRP 2020
# Table 5/8 for 100 kHz+ (H converted to B with B = mu0 H). TRANSCRIBED — verify.
# ---------------------------------------------------------------------------
def icnirp_cns_E_limit(f):
    """ICNIRP 2010 general-public basic restriction, in-situ E in CNS tissue of the head (V/m rms)."""
    if f < 1.0:
        return None
    if f < 10.0:
        return 0.1 / f
    if f < 25.0:
        return 0.01
    if f < 1000.0:
        return 4e-4 * f
    if f < 3000.0:
        return 0.4
    if f <= 10e6:
        return 1.35e-4 * f
    return None


def icnirp_B_reference(f):
    """General-public reference level for magnetic flux density (tesla, rms); 2010 below 100 kHz, 2020 above."""
    if f < 1.0:
        return None
    if f < 8.0:
        return 4e-2 / f ** 2          # 4e4/f² µT
    if f < 25.0:
        return 5e-3 / f               # 5000/f µT
    if f < 400.0:
        return 2e-4                   # 200 µT
    if f < 3000.0:
        return 8e-2 / f               # 8e4/f µT
    if f < 1e5:
        return 2.7e-5                 # 27 µT
    if f <= 10e6:
        return MU0 * 2.2 / (f / 1e6)  # 2020 Table 5: H = 2.2/f_M A/m, 30-min average
    return None


# reference doses from the transcranial-stimulation literature (V/m in cortex). Fill from
# docs/psionic_engineering/stabilizer_derivation.md once the abstracts are checked.
NEURAL_EFFECT_FIELDS = {
    "tACS 1 mA scalp, measured intracranial (Huang 2017, order of magnitude)": 0.3,
    "weakest documented network entrainment in slices (Fröhlich & McCormick 2010)": 0.2,
    "spike-timing entrainment threshold in vivo (Vöröslakos 2018, ~1 V/m)": 1.0,
}


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------
def spiral_segments(r_in, r_out, n_turns, phase, segments_per_turn=180, z=0.0):
    """Archimedean spiral filament from r_in to r_out over n_turns, starting at angle `phase`.
    Returns a list of (p0, p1) segment endpoints as (x, y, z) tuples."""
    pts = []
    total = int(round(n_turns * segments_per_turn))
    for k in range(total + 1):
        t = k / total
        r = r_in + (r_out - r_in) * t
        a = phase + 2 * math.pi * n_turns * t
        pts.append((r * math.cos(a), r * math.sin(a), z))
    return list(zip(pts[:-1], pts[1:]))


def pancake_coil(d_in, d_out, pair_pitch, connection, z=0.0):
    """Two interleaved spirals. Each spiral advances `pair_pitch` per turn; they are offset half a
    pitch (interleaved). `connection` 'opposing' gives the second spiral -1 current, 'aiding' +1.
    Returns [(segments, current_sign)], n_turns per spiral, wire length per spiral (m)."""
    n = (d_out - d_in) / 2.0 / pair_pitch
    r_in, r_out = d_in / 2.0, d_out / 2.0
    s1 = spiral_segments(r_in, r_out, n, 0.0, z=z)
    s2 = spiral_segments(r_in + pair_pitch / 2.0, r_out + pair_pitch / 2.0, n, 0.0, z=z)
    sign2 = -1.0 if connection == "opposing" else 1.0
    length = sum(math.dist(a, b) for a, b in s1)
    return [(s1, 1.0), (s2, sign2)], n, length


# ---------------------------------------------------------------------------
# fields by filament summation
# ---------------------------------------------------------------------------
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def B_field(coil, I, p):
    """Biot–Savart, midpoint rule per segment. Tesla."""
    bx = by = bz = 0.0
    for segs, sgn in coil:
        for a, b in segs:
            dl = _sub(b, a)
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
            r = _sub(p, mid)
            rn = _norm(r)
            if rn < 1e-9:
                continue
            c = _cross(dl, r)
            k = sgn * I * MU0 / (4 * math.pi) / rn ** 3
            bx += k * c[0]; by += k * c[1]; bz += k * c[2]
    return (bx, by, bz)


def A_field(coil, I, p):
    """Magnetic vector potential (Coulomb gauge), midpoint rule. T·m. E_induced = -dA/dt."""
    ax = ay = az = 0.0
    for segs, sgn in coil:
        for a, b in segs:
            dl = _sub(b, a)
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
            rn = _norm(_sub(p, mid))
            if rn < 1e-9:
                continue
            k = sgn * I * MU0 / (4 * math.pi) / rn
            ax += k * dl[0]; ay += k * dl[1]; az += k * dl[2]
    return (ax, ay, az)


def E_static(coil, lam, p):
    """Electrostatic field of the windings carrying line charge +lam on spiral 1 and (sign2*lam)
    on spiral 2 (the inter-winding voltage of a series-opposing coil puts ±V/2 on the two wires).
    Free-space value, V/m; multiply by screening_factor(f) for the in-tissue value."""
    ex = ey = ez = 0.0
    for segs, sgn in coil:
        for a, b in segs:
            dl = _norm(_sub(b, a))
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
            r = _sub(p, mid)
            rn = _norm(r)
            if rn < 1e-9:
                continue
            k = sgn * lam * dl / (4 * math.pi * EPS0) / rn ** 3
            ex += k * r[0]; ey += k * r[1]; ez += k * r[2]
    return (ex, ey, ez)


# ---------------------------------------------------------------------------
# lumped parameters
# ---------------------------------------------------------------------------
def lumped(d_in, d_out, pair_pitch, wire_d, n_turns, length_per_wire, connection, f, eps_r_ins=1.8, k_couple=0.85):
    """Inductance (Mohan current-sheet, circular), inter-winding capacitance (two-wire line),
    resistance with skin effect, reactances and self-resonance."""
    d_avg = (d_in + d_out) / 2.0
    rho = (d_out - d_in) / (d_out + d_in)
    L1 = MU0 * n_turns ** 2 * d_avg / 2.0 * (math.log(2.46 / rho) + 0.20 * rho ** 2)
    if connection == "opposing":
        L = 2 * L1 * (1 - k_couple)
    else:
        L = 2 * L1 * (1 + k_couple)
    centre_spacing = pair_pitch / 2.0
    ratio = max(centre_spacing / wire_d, 1.0001)
    C_per_m = math.pi * EPS0 * eps_r_ins / math.acosh(ratio)
    C = C_per_m * length_per_wire
    area = math.pi * (wire_d / 2) ** 2
    R_dc = RHO_CU * 2 * length_per_wire / area
    delta = math.sqrt(RHO_CU / (math.pi * f * MU0)) if f > 0 else float("inf")
    R_ac = R_dc * max(1.0, (wire_d / 2) / (2 * delta)) if delta < wire_d / 4 else R_dc
    w = 2 * math.pi * f
    XL = w * L
    XC = 1 / (w * C) if (w > 0 and C > 0) else float("inf")
    f_srf = 1 / (2 * math.pi * math.sqrt(L * C)) if (L > 0 and C > 0) else float("inf")
    return dict(L_single_H=L1, L_H=L, C_F=C, R_dc_ohm=R_dc, R_ac_ohm=R_ac, X_L_ohm=XL, X_C_ohm=XC, f_srf_Hz=f_srf, skin_depth_m=delta)


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def analyse(args):
    d_in, d_out = args.id * 1e-3, args.od * 1e-3
    pitch = args.pitch * 1e-3
    wire = args.wire * 1e-3
    out = {"coil": dict(id_mm=args.id, od_mm=args.od, pair_pitch_mm=args.pitch, wire_mm=args.wire, current_A=args.current, voltage_V=args.voltage),
           "points": {}, "connections": {}}
    # points along the disk axis (coil at z = 0, head at negative z). Off-axis cortex point at r = cortex_r.
    pts = {
        "scalp": (0.0, 0.0, -args.scalp * 1e-3),
        "cortex": (args.cortex_r * 1e-3, 0.0, -args.cortex * 1e-3),
        "core": (0.0, 0.0, -args.core * 1e-3),
        "far_side": (0.0, 0.0, -(args.core * 2) * 1e-3),
    }
    out["points"] = {k: dict(x_mm=v[0] * 1e3, z_mm=v[2] * 1e3) for k, v in pts.items()}
    for conn in ("opposing", "aiding"):
        coil, n, length = pancake_coil(d_in, d_out, pitch, conn)
        rec = dict(turns_per_spiral=n, wire_length_per_spiral_m=length, frequencies={})
        for f in args.f:
            lp = lumped(d_in, d_out, pitch, wire, n, length, conn, f)
            w = 2 * math.pi * f
            fr = dict(lumped=lp, fields={})
            # electrostatic: series-opposing puts the drive voltage across the pair; aiding puts ~0 between adjacent turns
            V_pair = args.voltage if conn == "opposing" else args.voltage / max(n, 1.0)
            lam = (lp["C_F"] / length) * V_pair if length > 0 else 0.0
            for name, p in pts.items():
                B = B_field(coil, args.current, p)
                A = A_field(coil, args.current, p)
                Bn = _norm(B)
                E_ind = w * _norm(A)                        # |E| = w|A| for sinusoidal drive (peak of the induced field)
                E_stat_air = _norm(E_static(coil, lam, p))
                sf = screening_factor(f)
                E_stat_tissue = E_stat_air * sf
                lim_E = icnirp_cns_E_limit(f)
                lim_B = icnirp_B_reference(f)
                fields = dict(B_T=Bn, B_uT=Bn * 1e6, E_induced_V_per_m=E_ind, E_static_air_V_per_m=E_stat_air,
                              E_static_tissue_V_per_m=E_stat_tissue, screening=sf,
                              icnirp_cns_E_limit_V_per_m=lim_E, icnirp_B_reference_T=lim_B,
                              E_induced_over_limit=(E_ind / lim_E) if lim_E else None,
                              B_over_reference=(Bn / lim_B) if lim_B else None)
                if name == "cortex":
                    fields["current_for_cns_limit_A"] = (args.current * lim_E / E_ind) if (lim_E and E_ind > 0) else None
                    fields["current_for_tACS_0p3_Vpm_A"] = (args.current * 0.3 / E_ind) if E_ind > 0 else None
                fr["fields"][name] = fields
            rec["frequencies"][f"{f:g}"] = fr
        out["connections"][conn] = rec
    return out


def fmt(x, unit=""):
    if x is None:
        return "  n/a  "
    if x == 0:
        return "0" + unit
    mag = math.floor(math.log10(abs(x)))
    if -3 <= mag < 4:
        return f"{x:.3g}{unit}"
    return f"{x:.2e}{unit}"


def print_report(out):
    c = out["coil"]
    print(f"Stabilizer disk coil: bifilar pancake ID {c['id_mm']:.0f} OD {c['od_mm']:.0f} mm, pair pitch {c['pair_pitch_mm']} mm, wire {c['wire_mm']} mm; drive {c['current_A']} A / {c['voltage_V']} V")
    print("points (coil plane z=0, head toward -z): " + ", ".join(f"{k} ({v['x_mm']:.0f}, {v['z_mm']:.0f})" for k, v in out["points"].items()))
    for conn, rec in out["connections"].items():
        print(f"\n== {conn.upper()} connection: {rec['turns_per_spiral']:.1f} turns per spiral, {rec['wire_length_per_spiral_m']:.1f} m per wire")
        for fk, fr in rec["frequencies"].items():
            lp = fr["lumped"]
            print(f"  f = {fk} Hz: L {fmt(lp['L_H']*1e6)} uH, C {fmt(lp['C_F']*1e12)} pF, R {fmt(lp['R_ac_ohm'])} ohm, X_L {fmt(lp['X_L_ohm'])} ohm, X_C {fmt(lp['X_C_ohm'])} ohm, SRF {fmt(lp['f_srf_Hz']/1e6)} MHz")
            print(f"    {'point':9s} {'B (uT)':>10s} {'B/ref':>8s} {'E_ind (V/m)':>12s} {'E_ind/CNS lim':>14s} {'E_stat air':>11s} {'screen':>9s} {'E_stat tissue':>14s}")
            for name, fl in fr["fields"].items():
                print(f"    {name:9s} {fmt(fl['B_uT']):>10s} {fmt(fl['B_over_reference']):>8s} {fmt(fl['E_induced_V_per_m']):>12s} {fmt(fl['E_induced_over_limit']):>14s} {fmt(fl['E_static_air_V_per_m']):>11s} {fmt(fl['screening']):>9s} {fmt(fl['E_static_tissue_V_per_m']):>14s}")
            cx = fr["fields"]["cortex"]
            if cx.get("current_for_cns_limit_A") is not None:
                print(f"    -> current to reach the CNS in-situ limit at the cortex: {fmt(cx['current_for_cns_limit_A'])} A; to reach a tACS-class 0.3 V/m: {fmt(cx['current_for_tACS_0p3_Vpm_A'])} A")
    print("\nNotes: E_ind is the peak induced field for a sinusoidal drive AT that frequency (a modulated carrier induces at the carrier, not the envelope).")
    print("Tissue parameters are Gabriel-class approximations; exposure limits transcribed from ICNIRP 2010/2020 general-public tables — verify before quoting.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--id", type=float, default=20.0, help="inner diameter, mm")
    ap.add_argument("--od", type=float, default=100.0, help="outer diameter, mm")
    ap.add_argument("--pitch", type=float, default=1.9, help="radial advance per turn of each spiral (two wires wide), mm")
    ap.add_argument("--wire", type=float, default=0.511, help="conductor diameter, mm (24 AWG = 0.511)")
    ap.add_argument("--current", type=float, default=1.0, help="drive current amplitude, A")
    ap.add_argument("--voltage", type=float, default=50.0, help="drive voltage amplitude across the pair, V")
    ap.add_argument("--scalp", type=float, default=44.0, help="axial distance coil plane -> scalp, mm")
    ap.add_argument("--cortex", type=float, default=52.0, help="axial distance coil plane -> cortex, mm")
    ap.add_argument("--cortex-r", type=float, default=30.0, help="off-axis radius of the cortex evaluation point, mm")
    ap.add_argument("--core", type=float, default=121.0, help="axial distance coil plane -> brain core, mm")
    ap.add_argument("--f", type=float, nargs="+", default=[7.83, 10.0, 40e3, 1e6, 5e6], help="drive frequencies, Hz")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    out = analyse(args)
    if args.json:
        json.dump(out, sys.stdout, indent=1)
    else:
        print_report(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
