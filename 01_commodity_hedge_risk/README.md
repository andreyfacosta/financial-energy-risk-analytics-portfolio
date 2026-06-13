# Commodity Hedge Risk Dashboard

## Business Context

A Canadian grain company buys and sells physical grain while using futures contracts to hedge price exposure. The risk team needs a clear view of physical exposure, futures exposure, net open exposure, hedge ratio, basis risk, P&L, margin calls, stress tests, and counterparty concentration.

This project creates a synthetic but realistic analytics workflow for that scenario. It is built to demonstrate employability for remote Financial Data Analyst, Risk Reporting Analyst, Commodity Risk Analyst, BI Analyst, Treasury/Risk Reporting, and FP&A roles.

## What This Project Shows

- Synthetic data generation for a realistic commodity risk environment.
- CSV outputs that can be loaded directly into Power BI.
- SQLite-compatible schema and SQL query examples.
- pandas analysis for risk metrics, P&L, VaR approximation, stress testing, and risk flags.
- Power BI model and DAX measure documentation.
- Executive dashboard design with recruiter-friendly business framing.

## Data Tables

Raw input tables:

- `physical_transactions`
- `futures_positions`
- `daily_cash_prices`
- `daily_futures_prices`
- `fx_rates`
- `margin_requirements`
- `counterparties`
- `commodities`
- `calendar`

Analytical output tables:

- `daily_risk_metrics.csv`
- `counterparty_exposure.csv`
- `risk_flags.csv`
- `stress_test_results.csv`
- `risk_summary.csv`

## Metrics

- Physical exposure
- Futures exposure
- Net open exposure
- Hedge ratio
- Daily P&L
- Cumulative P&L
- Basis
- Basis risk
- Margin requirement
- VaR 95/99 approximation
- Stress test impact
- Counterparty exposure
- Risk flags

## Run Locally

From the repository root:

```powershell
python 01_commodity_hedge_risk/notebooks/01_generate_synthetic_data.py
python 01_commodity_hedge_risk/notebooks/02_analyze_hedge_risk.py
```

Generated outputs are written to:

```text
01_commodity_hedge_risk/data/
```

## Power BI Pages

1. Executive Summary
2. Exposure & Hedge Ratio
3. P&L and Margin
4. Basis Risk
5. Stress Testing
6. Counterparty / Region View

## Data Notice

All data is synthetic. No confidential employer data is used.
