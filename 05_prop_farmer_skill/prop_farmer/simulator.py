from __future__ import annotations

from dataclasses import dataclass
import random
from statistics import mean, median

from .models import FirmRules, StrategyEdge, SimulationConfig


@dataclass
class TrialResult:
    ending_bankroll: float
    ruined: bool
    attempts: int
    evaluations_passed: int
    payouts_received: int
    payouts_denied: int
    total_costs: float
    total_payouts: float
    max_bankroll_drawdown: float


def _payout(rng: random.Random, edge: StrategyEdge, firm: FirmRules) -> float:
    amount = max(0.0, rng.gauss(edge.avg_net_payout, edge.payout_std)) if edge.payout_std else edge.avg_net_payout
    if firm.payout_cap is not None:
        amount = min(amount, firm.payout_cap)
    return amount * firm.payout_split


def run_single_trial(firm: FirmRules, edge: StrategyEdge, config: SimulationConfig, rng: random.Random) -> TrialResult:
    firm.validate()
    edge.validate()
    bankroll = config.starting_bankroll
    peak = bankroll
    max_dd = 0.0
    attempts = passed = payouts = denied = 0
    costs = paid = 0.0

    while attempts < config.max_attempts and bankroll - firm.eval_fee >= config.ruin_floor:
        attempts += 1
        bankroll -= firm.eval_fee
        costs += firm.eval_fee
        max_dd = max(max_dd, peak - bankroll)

        if rng.random() > edge.p_fund:
            continue

        passed += 1
        if firm.activation_fee:
            if bankroll - firm.activation_fee < config.ruin_floor:
                break
            bankroll -= firm.activation_fee
            costs += firm.activation_fee
            max_dd = max(max_dd, peak - bankroll)

        if rng.random() > edge.p_withdrawal_given_funded:
            continue

        if rng.random() < edge.payout_denial_rate:
            denied += 1
            continue

        amount = _payout(rng, edge, firm)
        bankroll += amount
        paid += amount
        payouts += 1
        peak = max(peak, bankroll)

        if config.stop_after_first_payout:
            break

    return TrialResult(
        ending_bankroll=bankroll,
        ruined=bankroll - firm.eval_fee < config.ruin_floor,
        attempts=attempts,
        evaluations_passed=passed,
        payouts_received=payouts,
        payouts_denied=denied,
        total_costs=costs,
        total_payouts=paid,
        max_bankroll_drawdown=max_dd,
    )


def run_monte_carlo(firm: FirmRules, edge: StrategyEdge, config: SimulationConfig) -> list[TrialResult]:
    rng = random.Random(config.random_seed)
    return [run_single_trial(firm, edge, config, rng) for _ in range(config.max_trials)]


def summarize_trials(trials: list[TrialResult]) -> dict[str, float]:
    if not trials:
        raise ValueError("trials must not be empty")
    ending = [t.ending_bankroll for t in trials]
    payouts = [t.payouts_received for t in trials]
    ending_sorted = sorted(ending)
    return {
        "trials": len(trials),
        "avg_ending_bankroll": mean(ending),
        "median_ending_bankroll": median(ending),
        "p5_ending_bankroll": ending_sorted[max(0, int(0.05 * len(ending_sorted)) - 1)],
        "ruin_rate": mean([1 if t.ruined else 0 for t in trials]),
        "probability_at_least_one_payout": mean([1 if p > 0 else 0 for p in payouts]),
        "avg_payouts_received": mean(payouts),
        "avg_total_payouts": mean([t.total_payouts for t in trials]),
        "avg_total_costs": mean([t.total_costs for t in trials]),
        "avg_max_bankroll_drawdown": mean([t.max_bankroll_drawdown for t in trials]),
    }
