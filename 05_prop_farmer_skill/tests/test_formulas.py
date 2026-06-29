import math
import unittest

from prop_farmer.formulas import bankroll_attempt_capacity, breakeven_win_rate, no_payout_probability, p_success, required_attempts


class FormulaTests(unittest.TestCase):
    def test_p_success(self):
        self.assertAlmostEqual(p_success(0.25, 0.15), 0.0375)

    def test_no_payout_probability(self):
        self.assertAlmostEqual(no_payout_probability(0.15, 20), 0.85 ** 20)

    def test_required_attempts(self):
        self.assertEqual(required_attempts(0.15, 0.05), math.ceil(math.log(0.05) / math.log(0.85)))

    def test_breakeven_wr(self):
        self.assertAlmostEqual(breakeven_win_rate(4, 1), 0.8)

    def test_bankroll_capacity(self):
        self.assertEqual(bankroll_attempt_capacity(2000, 50), 40)


if __name__ == "__main__":
    unittest.main()
