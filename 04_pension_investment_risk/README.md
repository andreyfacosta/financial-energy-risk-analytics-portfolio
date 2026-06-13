# Pension Investment Risk Dashboard

Power BI-ready pension and retirement investment analytics project using synthetic portfolio data. The project monitors asset allocation, portfolio value, returns, benchmark performance, active return, volatility, drawdown, FX exposure, contribution flows, retirement projections, stress scenarios, risk profile, and risk flags.

All data is synthetic. No confidential employer data is used.

## Dashboard Preview

Screenshots will be added after the dashboard is built in Power BI Desktop.

| Page | Screenshot file |
|---|---|
| Executive Summary | `docs/screenshots/executive_summary.png` |
| Asset Allocation | `docs/screenshots/asset_allocation.png` |
| Returns vs Benchmark | `docs/screenshots/returns_vs_benchmark.png` |
| Volatility & Drawdown | `docs/screenshots/volatility_drawdown.png` |
| FX Exposure & Scenarios | `docs/screenshots/fx_exposure_scenarios.png` |
| Retirement Projection | `docs/screenshots/retirement_projection.png` |

## Business Problem

A pension or retirement investment analytics team needs to monitor whether portfolios remain aligned with target allocation, whether returns are tracking benchmarks, whether drawdown and volatility are acceptable, how much FX exposure exists, and how contribution behavior affects long-term retirement projections.

## Executive Summary

This project creates synthetic portfolios, members, asset classes, holdings, daily prices, FX rates, contributions, withdrawals, benchmarks, and calendar data. The analysis layer calculates daily returns, allocation drift, drawdown, volatility, FX exposure, contribution projections, stress scenarios, and executive summary KPIs.

## Key Metrics

- Asset allocation %
- Portfolio value
- Daily/monthly return
- Cumulative return
- Benchmark return
- Active return
- Volatility
- Maximum drawdown
- FX exposure
- Contribution flow
- Withdrawal flow
- Retirement projection
- Stress scenario impact
- Risk profile
- Risk flags

## Data Model

Raw input tables:

- `portfolios.csv`
- `members.csv`
- `asset_classes.csv`
- `holdings.csv`
- `daily_prices.csv`
- `fx_rates.csv`
- `contributions.csv`
- `withdrawals.csv`
- `benchmarks.csv`
- `calendar.csv`

Analytical output tables:

- `portfolio_daily_returns.csv`
- `allocation_summary.csv`
- `drawdown_summary.csv`
- `volatility_summary.csv`
- `fx_exposure_summary.csv`
- `contribution_projection.csv`
- `scenario_results.csv`
- `executive_investment_summary.csv`

SQLite database:

- `data/pension_investment_risk.sqlite`

## Analytical Workflow

1. `notebooks/01_generate_synthetic_data.py`
   - Generates synthetic portfolios, members, holdings, daily prices, FX, contributions, withdrawals, benchmarks, and calendar.
   - Writes raw CSV files and a SQLite database.

2. `notebooks/02_analyze_investment_risk.py`
   - Calculates daily returns, cumulative return, benchmark comparison, allocation, drawdown, volatility, FX exposure, projections, scenario impacts, and risk flags.
   - Writes analytical CSV files and analytical SQLite tables/views.

3. Power BI Desktop
   - Imports CSV files.
   - Builds relationships around calendar, portfolios, members, and asset classes.
   - Creates DAX measures and six dashboard pages.

## Power BI Pages

1. Executive Summary
2. Asset Allocation
3. Returns vs Benchmark
4. Volatility & Drawdown
5. FX Exposure & Scenarios
6. Retirement Projection

## Synthetic Insights

- Allocation drift can emerge when asset class returns diverge from target weights.
- Active return shows whether portfolios are outperforming or lagging synthetic benchmarks.
- Drawdown and volatility help distinguish growth portfolios from conservative portfolios.
- FX exposure is concentrated in USD and global equity/fixed income holdings.
- Retirement projections show how contribution rates and current balances influence long-term outcomes.

## Business Recommendations

- Review allocation drift above tolerance before month-end reporting.
- Monitor drawdown and volatility by risk profile rather than using one threshold for all portfolios.
- Explain active return against benchmark instead of showing portfolio return alone.
- Separate investment performance from contribution and withdrawal flows.
- Use stress scenarios to support member-facing risk conversations.

## Skills Demonstrated

- Python and pandas investment analytics workflow.
- SQL and SQLite data modeling.
- Return, benchmark, drawdown, volatility, allocation, FX, and scenario analysis.
- Power BI model planning and DAX measure design.
- Pension and retirement dashboard storytelling.

## How to Reproduce

From the repository root:

```powershell
python 04_pension_investment_risk/notebooks/01_generate_synthetic_data.py
python 04_pension_investment_risk/notebooks/02_analyze_investment_risk.py
```

Then build the report manually using:

```text
04_pension_investment_risk/powerbi/powerbi_build_guide.md
```

## Limitations

- The data is synthetic and intended for portfolio demonstration.
- Return calculations are simplified and not intended as production performance attribution.
- Retirement projections use simple assumptions and do not represent financial advice.
- The Power BI `.pbix` must be built manually from the guide.

## Interview Talking Points

- I modeled pension investment data from holdings, prices, FX, flows, and benchmarks.
- I calculated portfolio value, returns, active return, volatility, drawdown, allocation drift, FX exposure, scenario impact, and retirement projections.
- I prepared Power BI-ready outputs, SQL views, DAX measures, and a report build guide.
- The project shows how I connect investment risk, member outcomes, and executive reporting.
