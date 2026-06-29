import unittest

from prop_farmer.models import DrawdownType, FirmRules, SimulationConfig, StrategyEdge
from prop_farmer.simulator import run_monte_carlo, summarize_trials


class SimulatorTests(unittest.TestCase):
    def test_simulator_runs(self):
        firm = FirmRules(
            firm="TestFirm",
            account_size=50000,
            eval_fee=50,
            activation_fee=100,
            payout_cap=2000,
            payout_split=1.0,
            drawdown_type=DrawdownType.STATIC,
        )
        edge = StrategyEdge(
            name="test_edge",
            p_fund=0.3,
            p_withdrawal_given_funded=0.2,
            avg_net_payout=1000,
        )
        config = SimulationConfig(starting_bankroll=1000, max_attempts=20, max_trials=100, random_seed=1)
        trials = run_monte_carlo(firm, edge, config)
        summary = summarize_trials(trials)
        self.assertEqual(summary["trials"], 100)
        self.assertIn("ruin_rate", summary)


if __name__ == "__main__":
    unittest.main()
