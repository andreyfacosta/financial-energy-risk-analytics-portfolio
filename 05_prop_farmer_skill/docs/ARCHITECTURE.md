# Prop Farmer Multi-Agent Architecture

## Principle

All agents share the same cognitive base:

```text
prop-firm farming = advantage-play game
```

The system must search, test, falsify, and update policies. It must not turn a YouTube method into dogma.

## Agents

### 1. Source Extraction Agent

Extracts claims from videos, transcripts, docs, and firm pages.

### 2. Firm Rule Agent

Maintains current firm rules with date snapshots.

### 3. Policy Designer Agent

Turns tactics into testable policies.

### 4. Rules-Aware Backtest Agent

Tests a strategy under exact firm rules.

### 5. Monte Carlo Agent

Simulates bankroll and payout paths.

### 6. Falsification Agent

Searches for reasons a policy fails.

### 7. Hive Memory Agent

Stores outcomes and updates priors.

### 8. Decision Agent

Only recommends controlled experiments after all gates pass.

## Memory schema

Every event should be logged as:

```json
{
  "event_id": "",
  "timestamp": "",
  "firm": "",
  "account_id": "",
  "account_size": 0,
  "state_before": "",
  "policy": "",
  "cost": 0,
  "pnl": 0,
  "payout_requested": 0,
  "payout_received": 0,
  "payout_denied": false,
  "denial_reason": "",
  "account_dead": false,
  "rule_snapshot_id": "",
  "notes": ""
}
```

## Deterministic loop

```text
extract rules
extract claims
compile game state
generate policy
simulate
backtest
red-team
run small experiment
log outcome
update priors
repeat
```

## Critical distinction

The system is not built to preserve individual accounts. It is built to optimize the distribution of payouts over many tickets while controlling bankroll survival.
