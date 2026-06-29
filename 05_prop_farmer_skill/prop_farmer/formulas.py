from __future__ import annotations

import math


def _check_probability(value: float, name: str) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be in [0, 1].")


def p_success(
    p_fund: float,
    p_withdrawal_given_funded: float,
    payout_denial_rate: float = 0.0,
    human_error_rate: float = 0.0,
) -> float:
    """Effective probability that one evaluation purchase ends in paid money.

    This is not a universal property of prop firms. It is an empirical estimate:
    strategy x firm rules x user execution x market regime.
    """
    _check_probability(p_fund, "p_fund")
    _check_probability(p_withdrawal_given_funded, "p_withdrawal_given_funded")
    _check_probability(payout_denial_rate, "payout_denial_rate")
    _check_probability(human_error_rate, "human_error_rate")
    return p_fund * p_withdrawal_given_funded * (1 - payout_denial_rate) * (1 - human_error_rate)


def ev_per_attempt(
    effective_p_success: float,
    avg_net_payout: float,
    eval_fee: float,
    p_fund: float = 0.0,
    activation_fee: float = 0.0,
    expected_reset_cost: float = 0.0,
    expected_commission_slippage: float = 0.0,
) -> float:
    """Expected value per evaluation attempt.

    Activation fee is an expected cost if it is only paid after passing evaluation.
    """
    _check_probability(effective_p_success, "effective_p_success")
    _check_probability(p_fund, "p_fund")
    if eval_fee < 0 or activation_fee < 0 or expected_reset_cost < 0 or expected_commission_slippage < 0:
        raise ValueError("costs must be non-negative.")
    if avg_net_payout < 0:
        raise ValueError("avg_net_payout must be non-negative.")
    expected_activation = p_fund * activation_fee
    return (
        effective_p_success * avg_net_payout
        - eval_fee
        - expected_activation
        - expected_reset_cost
        - expected_commission_slippage
    )


def no_payout_probability(effective_p_success: float, attempts: int) -> float:
    """Probability of zero payouts after N independent attempts.

    This is often mislabeled as risk of ruin. True bankroll ruin requires a
    bankroll path simulation. This closed-form metric is only the probability
    of no positive terminal event in N attempts.
    """
    _check_probability(effective_p_success, "effective_p_success")
    if attempts < 0:
        raise ValueError("attempts must be non-negative.")
    return (1 - effective_p_success) ** attempts


def required_attempts(effective_p_success: float, target_no_payout_probability: float) -> int | float:
    """Attempts required to push no-payout probability below a target."""
    _check_probability(effective_p_success, "effective_p_success")
    _check_probability(target_no_payout_probability, "target_no_payout_probability")
    if effective_p_success == 0 or target_no_payout_probability == 0:
        return math.inf
    return math.ceil(math.log(target_no_payout_probability) / math.log(1 - effective_p_success))


def breakeven_win_rate(risk_per_loss: float, reward_per_win: float) -> float:
    """Win rate required to break even before fees/slippage.

    Example: risk 4 to win 1 requires 80% before costs.
    """
    if risk_per_loss <= 0 or reward_per_win <= 0:
        raise ValueError("risk_per_loss and reward_per_win must be positive.")
    return risk_per_loss / (risk_per_loss + reward_per_win)


def bankroll_attempt_capacity(bankroll: float, eval_fee: float, reserve: float = 0.0) -> int:
    if bankroll < 0 or eval_fee <= 0 or reserve < 0:
        raise ValueError("invalid bankroll, eval_fee, or reserve.")
    available = max(0.0, bankroll - reserve)
    return int(available // eval_fee)
