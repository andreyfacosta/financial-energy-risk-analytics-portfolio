# PRD — Prop Farmer Skill

## Product

Prop Farmer is a cognitive operating system and simulation framework for researching prop-firm farming as an advantage-play game.

## Primary objective

Maximize validated knowledge about which policies convert prop-firm evaluation costs into real payouts under controlled bankroll survival constraints.

## Non-objectives

- Do not provide trading signals.
- Do not recommend violating prop-firm rules.
- Do not assume traditional risk rules.
- Do not hard-code influencer claims as truth.
- Do not use raw PnL as the main metric.

## System modules

1. Knowledge Base: stores extracted claims with evidence type and confidence.
2. Firm Rule Compiler: transforms current prop-firm rules into computable JSON.
3. Game State Machine: tracks each account state.
4. Policy Library: stores tactics as hypotheses.
5. Formulas Engine: computes EV, no-payout probability, required attempts, break-even WR.
6. Monte Carlo Engine: simulates bankroll paths and account cycles.
7. Rules-Aware Backtest Adapter: tests systems against prop constraints.
8. Hive Memory: stores all empirical outcomes.
9. Thesis Generator: creates new testable policies.
10. Falsification Agent: actively tries to disprove policies.
11. Decision Engine: allows recommendations only after rules, simulation, and empirical memory.

## Minimum viable script

The first script must:

1. load firm rules,
2. load a strategy edge estimate,
3. compute effective P_success,
4. compute EV per attempt,
5. compute attempts required for target no-payout probability,
6. run Monte Carlo,
7. produce a red-team warning list.

## Acceptance criteria

A run is valid if it outputs:

- effective P_success,
- EV per attempt,
- no-payout probability at current bankroll,
- required attempts for target,
- Monte Carlo ruin proxy,
- average ending bankroll,
- probability of at least one payout,
- red-team flags,
- missing data list.

## Future acceptance criteria

The full system must add:

- live firm-rule snapshots,
- versioned rules by date,
- per-firm evidence,
- per-policy posterior probabilities,
- rules-aware strategy backtests,
- account-level tracker,
- payout verification,
- denial tracking,
- policy comparison dashboard.
