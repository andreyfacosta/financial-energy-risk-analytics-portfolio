# Red-Team Audit — Prop Farmer Advantage Play Output

## Executive verdict

The NotebookLM output is strong as a mental model, but not safe as a deterministic decision system without correction.

Score:

```text
Mental model: 9/10
Data discipline: 7/10
Simulation readiness: 7/10
Production decision readiness: 5/10
```

The next step is to turn every claim into:

```text
claim -> evidence type -> variable -> simulation input -> falsification test
```

## Red flag 1 — N >= 20 is not universal

The output treats 20 attempts as a survival threshold. That only works if effective payout probability is high.

Examples:

```text
P_success = 15%   -> no-payout probability after 20 attempts = 3.9%
P_success = 4.5%  -> no-payout probability after 20 attempts = 39.8%
P_success = 3.36% -> no-payout probability after 20 attempts = 50.5%
```

Therefore 20 attempts is not a law. It is a parameterized hypothesis.

Correct formula:

```text
N_required = ln(target_no_payout_probability) / ln(1 - P_success)
```

## Red flag 2 — risk of ruin is mislabeled

`(1 - P_success)^N` is probability of no payout in N attempts. It is not complete bankroll ruin.

True bankroll ruin depends on:

- bankroll path,
- eval fees,
- resets,
- activation fees,
- denials,
- partial payouts,
- scaling,
- concurrent accounts,
- human error,
- regime shifts.

The skill must call it `no_payout_probability`, not full ruin.

## Red flag 3 — probabilities are not stationary

Historical `P_fund`, `P_withdrawal`, and `P_success` depend on:

- firm,
- market regime,
- account size,
- drawdown type,
- payout rules,
- strategy,
- number of simultaneous accounts,
- fatigue,
- rule changes.

The skill must store them as empirical priors that get updated.

## Red flag 4 — tactics are policies, not commands

Aggressive tactics may be rational under advantage-play logic, but only as state-dependent policies.

Each policy needs:

- what problem it solves,
- what payoff it targets,
- what bust path it creates,
- what data validates it,
- what data refutes it,
- what firm rules block it.

## Red flag 5 — multi-account is not automatic diversification

Multi-account only lowers variance if account outcomes are not highly correlated.

Correlation can come from:

- same setup,
- same session,
- same news event,
- same platform,
- same trader fatigue,
- same firm review process.

The simulator needs a correlation parameter in v1.

## Final red-team rule

Do not reject aggressive tactics by intuition.
Do not accept aggressive tactics by narrative.
Convert them into state-dependent policies and test them.
