# DAX Measures

Create a disconnected `Measures` table and add these measures. Column names match the generated CSV files.

## Format Recommendations

| Measure type | Suggested format |
|---|---|
| Portfolio value, flows, impact | Currency, CAD, 0 decimals |
| Returns, allocation, volatility, drawdown | Percentage, 1-2 decimals |
| Counts | Whole number |

## Portfolio Value and Returns

```DAX
Portfolio Value CAD =
SUM ( portfolio_daily_returns[portfolio_value_cad] )

Latest Portfolio Value CAD =
VAR LatestDate = MAXX ( ALL ( portfolio_daily_returns[date] ), portfolio_daily_returns[date] )
RETURN
    CALCULATE (
        SUM ( portfolio_daily_returns[portfolio_value_cad] ),
        portfolio_daily_returns[date] = LatestDate
    )

Daily Return =
AVERAGE ( portfolio_daily_returns[daily_return] )

Cumulative Return =
AVERAGE ( portfolio_daily_returns[cumulative_return] )

Benchmark Return =
AVERAGE ( portfolio_daily_returns[benchmark_return] )

Benchmark Cumulative Return =
AVERAGE ( portfolio_daily_returns[benchmark_cumulative_return] )

Active Return =
AVERAGE ( portfolio_daily_returns[active_return] )
```

## Allocation and Risk

```DAX
Market Value CAD =
SUM ( allocation_summary[market_value_cad] )

Selected Allocation % =
DIVIDE (
    [Market Value CAD],
    CALCULATE (
        [Market Value CAD],
        ALLSELECTED ( allocation_summary )
    )
)

Portfolio Allocation % =
DIVIDE (
    [Market Value CAD],
    CALCULATE (
        [Market Value CAD],
        ALLEXCEPT (
            allocation_summary,
            allocation_summary[portfolio_id],
            allocation_summary[portfolio_name]
        )
    )
)

Target Allocation % =
AVERAGE ( allocation_summary[target_allocation_pct] )

Weighted Target Allocation % =
DIVIDE (
    SUMX (
        allocation_summary,
        allocation_summary[target_allocation_pct] * allocation_summary[market_value_cad]
    ),
    [Market Value CAD]
)

Portfolio Allocation Drift % =
[Portfolio Allocation %] - [Weighted Target Allocation %]

Selected Allocation Drift % =
[Selected Allocation %] - [Weighted Target Allocation %]

Absolute Allocation Drift % =
SUMX (
    allocation_summary,
    ABS ( allocation_summary[allocation_drift_pct] )
)

Maximum Drawdown % =
MIN ( drawdown_summary[max_drawdown_pct] )

Current Drawdown % =
AVERAGE ( drawdown_summary[current_drawdown_pct] )

Annualized Volatility % =
AVERAGE ( volatility_summary[annualized_volatility_pct] )

Allocation Drift Flag Count =
CALCULATE (
    COUNTROWS ( allocation_summary ),
    allocation_summary[risk_flag] <> "Within range"
)
```

## FX, Flows, and Scenarios

```DAX
FX Exposure CAD =
SUM ( fx_exposure_summary[fx_exposure_cad] )

FX Exposure % =
SUM ( fx_exposure_summary[fx_exposure_pct] )

Contribution CAD =
SUM ( portfolio_daily_returns[contribution_cad] )

Withdrawal CAD =
SUM ( portfolio_daily_returns[withdrawal_cad] )

Net Flow CAD =
SUM ( portfolio_daily_returns[net_flow_cad] )

Projected Retirement Value CAD =
SUM ( contribution_projection[projected_retirement_value_cad] )

Stress Impact CAD =
SUM ( scenario_results[stress_impact_cad] )

Worst Scenario Impact CAD =
MINX (
    VALUES ( scenario_results[scenario] ),
    CALCULATE ( [Stress Impact CAD] )
)
```

## Validation Notes

- `Latest Portfolio Value CAD` should reconcile to `executive_investment_summary.csv`.
- `Allocation Drift Flag Count` should match non-within-range rows in `allocation_summary.csv`.
- Use `portfolio_daily_returns` for return trends and `allocation_summary` for latest allocation visuals.
- Do not use summed allocation percentages across multiple portfolios; percentages are only directly interpretable inside a single portfolio context.
- Use `Portfolio Allocation %` and `Portfolio Allocation Drift %` when a visual is filtered to one portfolio or has portfolio on the axis.
- Use `Selected Allocation %` for all-portfolio asset allocation views; it weights by market value over the selected portfolio universe.
- `Weighted Target Allocation %` is market-value weighted and safer than summing target percentages.
