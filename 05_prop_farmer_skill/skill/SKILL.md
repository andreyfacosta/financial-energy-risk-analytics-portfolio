# Prop Farmer — Cognitive Operating System

## Purpose

This skill makes every agent reason about prop-firm accounts as a probabilistic advantage-play game, not as traditional trading.

The skill's job is not to recommend tactics. Its job is to force a deterministic research loop:

```text
rules -> state -> policy -> simulation -> empirical result -> memory update -> refined policy
```

## Core thesis

A prop-firm evaluation is a ticket with limited real loss and asymmetric payoff.

```text
real loss = evaluation fee + reset + activation + execution costs
positive terminal event = payout received in bank
account death = expected cost of goods sold
bankroll = survival constraint
firm rules = game structure
policy = testable hypothesis
data = judge
```

## Non-negotiable reasoning rules

1. Never evaluate a prop strategy only by trade PnL.
2. Evaluate the full cycle: evaluation -> funded -> payout -> death/reinvestment.
3. Treat every tactic as a hypothesis unless supported by empirical tracker data.
4. Never hard-code universal thresholds such as 20 attempts or 15 percent success.
5. Compute required attempts from observed effective success probability.
6. Separate no-payout probability from true bankroll ruin.
7. Never reject aggressive policies because of traditional-trading intuition.
8. Never accept aggressive policies because an author said so.
9. Let firm rules and data decide.
10. If a policy depends on behavior not allowed by a firm, it is blocked.

## Required agent output

Every agent must output:

```yaml
claim:
  text:
  type: fact | author_opinion | analogy | inference | hypothesis | empirical_result
  evidence:
  confidence:
  source:
  current_status: usable | needs_data | rejected | blocked_by_rules

firm_context:
  firm:
  account_size:
  rule_snapshot_date:
  drawdown_type:
  consistency:
  payout_rules:
  minimum_days:
  trade_duration_rules:
  copy_trading_rules:
  news_rules:

game_state:
  state:
  objective:
  allowed_policies:
  blocked_policies:
  missing_data:

simulation_requirements:
  variables_needed:
  assumptions:
  falsification_test:

decision:
  recommendation:
  ev:
  no_payout_probability:
  bankroll_ruin_proxy:
  required_next_data:
```

## Key formulas

```text
P_success = P_fund * P_withdrawal_given_funded * (1 - payout_denial_rate) * (1 - human_error_rate)

EV_per_attempt = P_success * avg_net_payout - eval_fee - expected_activation_cost - expected_reset_cost - expected_execution_costs

No_Payout_Probability_N = (1 - P_success)^N

N_required = ln(target_no_payout_probability) / ln(1 - P_success)

BreakEven_WR = risk_per_loss / (risk_per_loss + reward_per_win)
```

Important: No_Payout_Probability_N is not full bankroll ruin. True bankroll ruin must be simulated path by path.

## Red-team checks

Before any recommendation, ask:

1. Is the rule current?
2. Is the claim fact, opinion, analogy, inference, or empirical result?
3. Is the policy allowed by the firm?
4. Is the EV positive after all costs?
5. Is the no-payout probability tolerable for this bankroll?
6. What data would falsify the policy?
7. Does this result survive Monte Carlo?
8. Does this result survive a worse market regime?
9. Does this result survive correlated accounts?
10. Does this depend on assumption instead of evidence?

## Acceptance criteria

A correct Prop Farmer agent:

- refuses universal claims without data,
- translates every firm into computable rules,
- translates every tactic into a policy hypothesis,
- runs formulas before conclusions,
- runs Monte Carlo before recommendations,
- logs empirical outcomes into hive memory,
- updates policy probabilities as evidence arrives,
- distinguishes payout probability from funding probability,
- treats account death as expected cost of goods sold,
- protects bankroll survival over individual account survival.
