from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AccountState(str, Enum):
    NOT_STARTED = "not_started"
    INSUFFICIENT_BANKROLL = "insufficient_bankroll"
    BANKROLL_OPERATIONAL = "bankroll_operational"
    EVALUATION_DAY_1 = "evaluation_day_1"
    EVALUATION_BUFFER_BUILDING = "evaluation_buffer_building"
    EVALUATION_BUFFER_PROTECTED = "evaluation_buffer_protected"
    EVALUATION_MINIMUM_DAYS = "evaluation_minimum_days"
    PASSED_EVALUATION = "passed_evaluation"
    FUNDED_PRE_PAYOUT = "funded_pre_payout"
    FUNDED_PAYOUT_READY = "funded_payout_ready"
    POST_PAYOUT = "post_payout"
    RISK_FREE = "risk_free"
    CRITICAL_DRAWDOWN = "critical_drawdown"
    DEAD = "dead"
    ABANDONED = "abandoned"
    RECYCLED = "recycled"


class DrawdownType(str, Enum):
    STATIC = "static"
    EOD_TRAILING = "eod_trailing"
    INTRADAY_TRAILING = "intraday_trailing"
    UNKNOWN = "unknown"


class ClaimType(str, Enum):
    FACT = "fact"
    AUTHOR_OPINION = "author_opinion"
    ANALOGY = "analogy"
    MATHEMATICAL_INFERENCE = "mathematical_inference"
    HYPOTHESIS = "hypothesis"
    EMPIRICAL_RESULT = "empirical_result"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    PARAMETERIZED_RULE = "parameterized_rule"


class DecisionStatus(str, Enum):
    APPROVED_FOR_SIMULATION = "approved_for_simulation"
    APPROVED_FOR_EXPERIMENT = "approved_for_experiment"
    NEEDS_MORE_DATA = "needs_more_data"
    NEEDS_CURRENT_FIRM_RULES = "needs_current_firm_rules"
    CONTRACTUALLY_BLOCKED = "contractually_blocked"
    BANKROLL_BLOCKED = "bankroll_blocked"
    REJECTED_NEGATIVE_EV = "rejected_negative_ev"


@dataclass(frozen=True)
class FirmRules:
    """Computable representation of a prop-firm account.

    Values must be updated from current firm rules before real use.
    """

    firm: str
    account_size: float
    eval_fee: float
    reset_fee: float = 0.0
    activation_fee: float = 0.0
    profit_target: float = 0.0
    daily_loss_limit: float = 0.0
    max_drawdown: float = 0.0
    drawdown_type: DrawdownType = DrawdownType.UNKNOWN
    consistency_cap_pct: Optional[float] = None
    minimum_trading_days: int = 0
    minimum_trade_duration_seconds: Optional[int] = None
    max_contracts: Optional[int] = None
    payout_minimum: float = 0.0
    payout_cap: Optional[float] = None
    payout_frequency_days: Optional[int] = None
    payout_split: float = 1.0
    withdrawal_resets_drawdown: Optional[bool] = None
    copy_trading_allowed: Optional[bool] = None
    news_trading_allowed: Optional[bool] = None
    prohibited_practices: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if self.eval_fee <= 0:
            raise ValueError("eval_fee must be positive.")
        if self.account_size <= 0:
            raise ValueError("account_size must be positive.")
        if not 0 < self.payout_split <= 1:
            raise ValueError("payout_split must be in (0, 1].")
        if self.consistency_cap_pct is not None and not 0 < self.consistency_cap_pct <= 1:
            raise ValueError("consistency_cap_pct must be in (0, 1].")


@dataclass(frozen=True)
class StrategyEdge:
    """Empirical edge estimate for one policy under one firm/rules context.

    These are not universal constants. They must come from tracker data, rules-aware
    backtests, or controlled experiments.
    """

    name: str
    p_fund: float
    p_withdrawal_given_funded: float
    avg_net_payout: float
    payout_std: float = 0.0
    payout_denial_rate: float = 0.0
    expected_reset_cost: float = 0.0
    expected_commission_slippage: float = 0.0
    human_error_rate: float = 0.0
    evidence_type: ClaimType = ClaimType.HYPOTHESIS
    evidence_notes: str = ""

    def validate(self) -> None:
        for field_name in ("p_fund", "p_withdrawal_given_funded", "payout_denial_rate", "human_error_rate"):
            value = getattr(self, field_name)
            if not 0 <= value <= 1:
                raise ValueError(f"{field_name} must be in [0, 1].")
        if self.avg_net_payout < 0:
            raise ValueError("avg_net_payout must be non-negative.")
        if self.payout_std < 0:
            raise ValueError("payout_std must be non-negative.")


@dataclass(frozen=True)
class PolicyHypothesis:
    """A tactic/policy treated as a hypothesis, not truth."""

    name: str
    state: AccountState
    objective: str
    solves_problem: str
    expected_payoff_logic: str
    bust_risk_logic: str
    positive_ev_conditions: tuple[str, ...]
    negative_ev_conditions: tuple[str, ...]
    required_data: tuple[str, ...]
    prohibited_if: tuple[str, ...] = field(default_factory=tuple)
    claim_type: ClaimType = ClaimType.HYPOTHESIS


@dataclass(frozen=True)
class SimulationConfig:
    starting_bankroll: float
    max_attempts: int = 250
    max_trials: int = 10_000
    ruin_floor: float = 0.0
    random_seed: Optional[int] = 42
    allow_reinvestment: bool = True
    stop_after_first_payout: bool = False
