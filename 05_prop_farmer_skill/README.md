# Prop Farmer Skill — Advantage Play Framework

This module is a research-grade cognitive operating system for prop-firm farming.

It deliberately does **not** treat prop-firm work as normal trading. The unit of analysis is:

```text
firm -> account -> state -> policy -> outcome -> payout/death -> learning
```

Core thesis:

```text
evaluation fee = ticket premium
prop-firm rules = game structure
funded account = intermediate state
payout = positive terminal event
dead account = expected COGS
bankroll = survival constraint
policy = testable hypothesis
data = final judge
```

## Contents

```text
prop_farmer/
  models.py          Domain model: firms, states, policies, evidence.
  formulas.py        EV, no-payout probability, required attempts, break-even WR.
  simulator.py       Monte Carlo engine for ticket -> funded -> payout cycles.
  decision_engine.py Deterministic gates and red-team checks.

skill/
  SKILL.md           Cognitive operating system for agents.

docs/
  PRD.md             Product requirements for the full multi-agent system.
  RED_TEAM_AUDIT.md  Aggressive conceptual audit.
  ARCHITECTURE.md    Agent architecture and hive-memory loop.

configs/
  sample_firm_rules.json
  sample_strategy_edge.json

examples/
  run_prop_farmer_sim.py

tests/
  test_formulas.py
  test_simulator.py
```

## Quick start

```bash
cd 05_prop_farmer_skill
python examples/run_prop_farmer_sim.py
python -m unittest discover -s tests
```

## Rule of the system

Nothing is hard-coded as truth. Every tactic is one of:

- `EMPIRICAL_RESULT`
- `PARAMETERIZED_RULE`
- `HYPOTHESIS`
- `UNSUPPORTED_CLAIM`
- `CONTRACTUALLY_BLOCKED`

A policy is actionable only after it passes:

1. current firm rules,
2. bankroll constraints,
3. state-machine context,
4. simulation,
5. empirical memory,
6. red-team audit.

## Not financial advice

This is for research, simulation, documentation, and internal system design. It is not a recommendation to buy evaluations, trade futures, violate firm rules, or use any specific prop firm.
