# Power BI Build Guide

Use this guide to build the Pension Investment Risk Dashboard manually in Power BI Desktop.

## 1. Generate Data

From the repository root:

```powershell
python 04_pension_investment_risk/notebooks/01_generate_synthetic_data.py
python 04_pension_investment_risk/notebooks/02_analyze_investment_risk.py
```

## 2. Import Tables

Import these CSV files from `04_pension_investment_risk/data/`:

- `calendar.csv`
- `portfolios.csv`
- `members.csv`
- `asset_classes.csv`
- `holdings.csv`
- `daily_prices.csv`
- `fx_rates.csv`
- `contributions.csv`
- `withdrawals.csv`
- `benchmarks.csv`
- `portfolio_daily_returns.csv`
- `allocation_summary.csv`
- `drawdown_summary.csv`
- `volatility_summary.csv`
- `fx_exposure_summary.csv`
- `contribution_projection.csv`
- `scenario_results.csv`
- `executive_investment_summary.csv`

## 3. Data Types and Date Table

- Mark `calendar[date]` as the date table.
- Date fields: `portfolio_daily_returns[date]`, `daily_prices[date]`, `fx_rates[date]`, `contributions[date]`, `withdrawals[date]`, `benchmarks[date]`.
- Currency/decimal fields: portfolio value, market value, flows, stress impact, projection, FX exposure.
- Percentage fields: return, allocation, drawdown, volatility, risk profile metrics.

## 4. Relationships

| From | To | Cardinality |
|---|---|---|
| `calendar[date]` | `portfolio_daily_returns[date]` | One-to-many |
| `calendar[date]` | `daily_prices[date]` | One-to-many |
| `calendar[date]` | `fx_rates[date]` | One-to-one or one-to-many |
| `portfolios[portfolio_id]` | `portfolio_daily_returns[portfolio_id]` | One-to-many |
| `portfolios[portfolio_id]` | `allocation_summary[portfolio_id]` | One-to-many |
| `portfolios[portfolio_id]` | `drawdown_summary[portfolio_id]` | One-to-one or one-to-many |
| `portfolios[portfolio_id]` | `volatility_summary[portfolio_id]` | One-to-one or one-to-many |
| `portfolios[portfolio_id]` | `contribution_projection[portfolio_id]` | One-to-one or one-to-many |
| `asset_classes[asset_class_id]` | `allocation_summary[asset_class_id]` | One-to-many |
| `asset_classes[asset_class_id]` | `daily_prices[asset_class_id]` | One-to-many |
| `members[member_id]` | `contributions[member_id]` | One-to-many |
| `members[member_id]` | `withdrawals[member_id]` | One-to-many |

Use single-direction filtering.

## 5. Measures

Create a `Measures` table and copy measures from `powerbi/dax_measures.md`.

## 6. Page Build

### Executive Summary

- KPI cards: `Latest Portfolio Value CAD`, `Cumulative Return`, `Active Return`, `Annualized Volatility %`, `Maximum Drawdown %`, `FX Exposure CAD`, `Worst Scenario Impact CAD`.
- Line chart: cumulative return vs benchmark cumulative return by date.
- Bar chart: latest portfolio value by portfolio.
- Table: portfolio, risk profile, volatility, drawdown, drift flag count.

### Asset Allocation

- Stacked bar: allocation % by asset class and portfolio.
- Matrix: asset class, market value, allocation %, target allocation %, drift %.
- Conditional formatting: drift above 3 percent amber, above 5 percent red.

### Returns vs Benchmark

- Line chart: cumulative return and benchmark cumulative return by date.
- Bar chart: active return by portfolio.
- Slicers: portfolio and risk profile.

### Volatility & Drawdown

- Bar chart: annualized volatility by portfolio.
- Bar chart: maximum drawdown by portfolio.
- Table: volatility risk flag and drawdown metrics.

### FX Exposure & Scenarios

- Bar chart: FX exposure CAD by currency.
- Matrix: scenario impact by portfolio and asset class.
- KPI card: worst scenario impact.

### Retirement Projection

- Bar chart: projected retirement value by portfolio.
- Table: average age, retirement age, annual contribution, assumed return, projected value.
- Slicers: risk profile and portfolio.

## 7. Conditional Formatting

- Negative active return: red.
- Maximum drawdown below -10 percent: amber.
- Maximum drawdown below -15 percent: red.
- Allocation drift above 3 percent: amber.
- Allocation drift above 5 percent: red.
- Negative stress impact: red.

## 8. Final Validation

- Latest portfolio value reconciles to `executive_investment_summary.csv`.
- Allocation percentages sum close to 100 percent by portfolio.
- Scenario page shows both downside and recovery scenarios.
- Projection page has no blank projected values.
