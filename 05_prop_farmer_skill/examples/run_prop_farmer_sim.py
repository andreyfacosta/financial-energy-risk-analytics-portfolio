from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prop_farmer.models import ClaimType, DrawdownType, FirmRules, SimulationConfig, StrategyEdge
from prop_farmer.simulator import run_monte_carlo, summarize_trials
from prop_farmer.formulas import p_success, ev_per_attempt, required_attempts, no_payout_probability
from prop_farmer.decision_engine import evaluate_purchase_gate


def main() -> None:
    firm = FirmRules(
        firm="SampleFuturesProp",
        account_size=50000,
        eval_fee=55,
        activation_fee=120,
        payout_cap=2000,
        payout_split=0.90,
        drawdown_type=DrawdownType.INTRADAY_TRAILING,
        minimum_trade_duration_seconds=10,
    )
    edge = StrategyEdge(
        name="sample_policy_prior",
        p_fund=0.25,
        p_withdrawal_given_funded=0.15,
        avg_net_payout=1500,
        payout_std=300,
        payout_denial_rate=0.02,
        expected_commission_slippage=15,
        human_error_rate=0.03,
        evidence_type=ClaimType.HYPOTHESIS,
        evidence_notes="Replace with tracker and rules-aware backtest evidence.",
    )
    config = SimulationConfig(starting_bankroll=2000, max_attempts=100, max_trials=5000, random_seed=7)

    ps = p_success(edge.p_fund, edge.p_withdrawal_given_funded, edge.payout_denial_rate, edge.human_error_rate)
    snapshot = {
        "effective_p_success": ps,
        "ev_per_attempt": ev_per_attempt(ps, edge.avg_net_payout * firm.payout_split, firm.eval_fee, edge.p_fund, firm.activation_fee, edge.expected_reset_cost, edge.expected_commission_slippage),
        "attempts_required_for_5pct_no_payout": required_attempts(ps, 0.05),
        "no_payout_probability_after_20_attempts": no_payout_probability(ps, 20),
    }
    decision = evaluate_purchase_gate(config.starting_bankroll, firm, edge)
    trials = run_monte_carlo(firm, edge, config)

    print("=== Closed-form snapshot ===")
    print(json.dumps(snapshot, indent=2))
    print("\n=== Decision gate ===")
    print(json.dumps({"status": decision.status.value, "reason": decision.reason, "metrics": decision.metrics}, indent=2))
    print("\n=== Monte Carlo summary ===")
    print(json.dumps(summarize_trials(trials), indent=2))


if __name__ == "__main__":
    main()
