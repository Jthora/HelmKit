"""Tests for tools/stabilizer_field_model.py — analytic anchors and transcribed exposure tables."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import stabilizer_field_model as M  # noqa: E402


class LoopAnchor(unittest.TestCase):
    def test_single_loop_on_axis_matches_analytic(self):
        R, I, z = 0.05, 1.0, 0.03
        segs = M.spiral_segments(R, R, 1.0, 0.0, segments_per_turn=720)
        coil = [(segs, 1.0)]
        B = M.B_field(coil, I, (0.0, 0.0, z))
        analytic = M.MU0 * I * R ** 2 / (2 * (R ** 2 + z ** 2) ** 1.5)
        self.assertAlmostEqual(B[2], analytic, delta=analytic * 0.005)
        self.assertLess(abs(B[0]) + abs(B[1]), analytic * 1e-3)

    def test_vector_potential_matches_direct_integral(self):
        # A_phi of a loop of radius R at (rho, 0, 0): (mu0 I R / 4 pi) * integral cos(phi) / |r| dphi, integrated finely
        R, I, rho = 0.05, 1.0, 0.025
        segs = M.spiral_segments(R, R, 1.0, 0.0, segments_per_turn=720)
        A = M.A_field([(segs, 1.0)], I, (rho, 0.0, 0.0))
        n = 200000
        acc = 0.0
        for k in range(n):
            phi = 2 * math.pi * (k + 0.5) / n
            r = math.sqrt((rho - R * math.cos(phi)) ** 2 + (R * math.sin(phi)) ** 2)
            acc += math.cos(phi) / r
        A_ref = M.MU0 * I * R / (4 * math.pi) * acc * (2 * math.pi / n)
        self.assertAlmostEqual(A[1], A_ref, delta=abs(A_ref) * 0.01)     # azimuthal at (rho, 0, 0) is +y
        self.assertLess(abs(A[0]) + abs(A[2]), abs(A_ref) * 1e-3)


class Connections(unittest.TestCase):
    def test_opposing_cancels_far_field_relative_to_aiding(self):
        opp, n, _ = M.pancake_coil(0.02, 0.10, 0.0019, "opposing")
        aid, _, _ = M.pancake_coil(0.02, 0.10, 0.0019, "aiding")
        p = (0.0, 0.0, -0.121)
        b_opp = math.sqrt(sum(b * b for b in M.B_field(opp, 1.0, p)))
        b_aid = math.sqrt(sum(b * b for b in M.B_field(aid, 1.0, p)))
        self.assertLess(b_opp, b_aid / 10.0)
        self.assertGreater(n, 15)

    def test_pancake_turn_count(self):
        _, n, length = M.pancake_coil(0.02, 0.10, 0.0019, "aiding")
        self.assertAlmostEqual(n, 21.05, delta=0.1)
        self.assertAlmostEqual(length, n * math.pi * 0.06, delta=0.2)


class Screening(unittest.TestCase):
    def test_screening_is_tiny_at_elf_and_grows_with_frequency(self):
        s10, s40k, s5M = M.screening_factor(10.0), M.screening_factor(4e4), M.screening_factor(5e6)
        self.assertLess(s10, 1e-6)
        self.assertLess(s40k, 1e-4)
        self.assertGreater(s5M, 5e-4)
        self.assertLess(s5M, 5e-3)
        self.assertTrue(s10 < s40k < s5M)

    def test_screening_formula_at_5mhz(self):
        sigma, eps_r = M.tissue(5e6)
        w = 2 * math.pi * 5e6
        expected = w * M.EPS0 / abs(complex(sigma, w * M.EPS0 * eps_r))
        self.assertAlmostEqual(M.screening_factor(5e6), expected, places=12)


class ExposureTables(unittest.TestCase):
    """Spot values read from ICNIRP 2010 Table 2 / Table 4 and ICNIRP 2020 Table 5 (general public)."""

    def test_cns_basic_restriction_2010(self):
        self.assertAlmostEqual(M.icnirp_cns_E_limit(5.0), 0.02)
        self.assertAlmostEqual(M.icnirp_cns_E_limit(10.0), 0.01)
        self.assertAlmostEqual(M.icnirp_cns_E_limit(60.0), 0.024)
        self.assertAlmostEqual(M.icnirp_cns_E_limit(2000.0), 0.4)
        self.assertAlmostEqual(M.icnirp_cns_E_limit(5e6), 675.0)
        self.assertIsNone(M.icnirp_cns_E_limit(0.1))

    def test_b_reference_levels(self):
        self.assertAlmostEqual(M.icnirp_B_reference(2.0), 1e-2)          # 4e-2/f^2
        self.assertAlmostEqual(M.icnirp_B_reference(10.0), 5e-4)         # 5e-3/f
        self.assertAlmostEqual(M.icnirp_B_reference(60.0), 2e-4)         # 200 uT
        self.assertAlmostEqual(M.icnirp_B_reference(1000.0), 8e-5)       # 8e-2/f
        self.assertAlmostEqual(M.icnirp_B_reference(4e4), 2.7e-5)        # 27 uT
        self.assertAlmostEqual(M.icnirp_B_reference(1e6), M.MU0 * 2.2)   # 2020 Table 5: 2.2/f_M A/m


class Lumped(unittest.TestCase):
    def test_series_opposing_has_lower_inductance_and_higher_srf(self):
        d_in, d_out, pitch, wire = 0.02, 0.10, 0.0019, 0.000511
        _, n, length = M.pancake_coil(d_in, d_out, pitch, "aiding")
        lo = M.lumped(d_in, d_out, pitch, wire, n, length, "opposing", 1e6)
        la = M.lumped(d_in, d_out, pitch, wire, n, length, "aiding", 1e6)
        self.assertLess(lo["L_H"], la["L_H"] / 5)
        self.assertGreater(lo["f_srf_Hz"], la["f_srf_Hz"])
        self.assertAlmostEqual(lo["C_F"], la["C_F"])
        self.assertGreater(lo["R_ac_ohm"], lo["R_dc_ohm"])     # skin effect at 1 MHz on 0.5 mm wire


class Cli(unittest.TestCase):
    def test_json_run(self):
        import io, json, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.main(["--f", "10", "--json"])
        self.assertEqual(rc, 0)
        d = json.loads(buf.getvalue())
        self.assertIn("opposing", d["connections"])
        cx = d["connections"]["aiding"]["frequencies"]["10"]["fields"]["cortex"]
        self.assertGreater(cx["current_for_cns_limit_A"], 10.0)      # a disk coil cannot legally reach the CNS limit at ELF


if __name__ == "__main__":
    unittest.main()
