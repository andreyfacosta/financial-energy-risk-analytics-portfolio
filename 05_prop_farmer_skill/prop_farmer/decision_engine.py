from __future__ import annotations

from dataclasses import dataclass

from .formulas import bankroll_attempt_capacity, ev_per_attempt, no_payout_probability, p_success, required_attempts
from .models import DecisionStatus, FirmRules, PolicyHypothesis, StrategyEdge


@dataclass(frozen=True)
class Decision:
    status: DecisionStatus
    reason: str
    metrics: dict[str, float | int | str]


def evaluate_purchase_gate(
    bankroll: float,
    firm: FirmRules,
    edge: StrategyEdge,
    target_no_payout_probability: float = 0.05,
) -> Decision:
    """Classify whether this configuration is ready for experiment.

    This is not a buy/sell/trade recommendation. It is a research gate.
    """
    firm.validate()
    edge.validate()
    ps = p_success(edge.p_fund, edge.p_withdrawal_given_funded, edge.payout_denial_rate, edge.human_error_rate)
    capacity = bankroll_attempt_capacity(bankroll, firm.eval_fee)
    req = required_attempts(ps, target_no_payout_probability)
    ev = ev_per_attempt(
        effective_p_success=ps,
        avg_net_payout=edge.avg_net_payout * firm.payout_split,
        eval_fee=firm.eval_fee,
        p_fund=edge.p_fund,
        activation_fee=firm.activation_fee,
        expected_reset_cost=edge.expected_reset_cost,
        expected_commission_slippage=edge.expected_commission_slippage,
    )
    metrics = {
        "bankroll_attempt_capacity": capacity,
        "required_attempts_for_target_no_payout": req if req != float("inf") else "infinite",
        "effective_p_success": ps,
        "no_payout_probability_at_capacity": no_payout_probability(ps, capacity),
        "ev_per_attempt": ev,
    }
    if capacity <= 0:
        return Decision(DecisionStatus.BANKROLL_BLOCKED, "Bankroll cannot buy one evaluation ticket.", metrics)
    if ev < 0:
        return Decision(DecisionStatus.REJECTED_NEGATIVE_EV, "Current inputs imply negative EV per attempt.", metrics)
    if req != float("inf") and capacity < req:
        return Decision(DecisionStatus.NEEDS_MORE_DATA, "Positive EV possible, but current bankroll does not meet the target no-payout probability.", metrics)
    return Decision(DecisionStatus.APPROVED_FOR_SIMULATION, "Closed-form gate passed. Run Monte Carlo and empirical tests before use.", metrics)


def evaluate_policy_gate(policy: PolicyHypothesis, firm: FirmRules) -> Decision:
    """Rule-aware policy gate.

    It blocks only explicit conflicts. It does not impose traditional-trading prudence.
    """
    firm.validate()
    prohibited = {p.lower() for p in firm.prohibited_practices}
    for blocker in policy.prohibited_if:
        if blocker.lower() in prohibited:
            return Decision(
                DecisionStatus.CONTRACTUALLY_BLOCKED,
                f"Policy is blocked by firm rule: {blocker}",
                {"policy": policy.name, "firm": firm.firm},
            )
    if "micro" in policy.name.lower() and firm.minimum_trade_duration_seconds is None:
        return Decision(DecisionStatus.NEEDS_CURRENT_FIRM_RULES, "Minimum trade duration is unknown.", {"policy": policy.name})
    if "copy" in policy.name.lower() and firm.copy_trading_allowed is not True:
        return Decision(DecisionStatus.NEEDS_CURRENT_FIRM_RULES, "Copy-trading permission is missing or false.", {"policy": policy.name})
    return Decision(DecisionStatus.APPROVED_FOR_EXPERIMENT, "No explicit rule conflict detected. Still requires simulation and tracker validation.", {"policy": policy.name})
