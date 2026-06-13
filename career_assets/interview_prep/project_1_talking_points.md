# Interview Talking Points - Commodity Hedge Risk Dashboard

## 60-Second Project Summary

I built a synthetic commodity hedge risk dashboard for a Canadian grain company scenario. The model combines physical grain transactions, futures positions, daily cash and futures prices, FX rates, counterparties, margin requirements, and calendar data. The output is a Power BI-ready dataset and model design for monitoring exposure, hedge ratio, basis risk, P&L, margin requirements, VaR approximation, stress test impact, and counterparty exposure.

## Business Problem

A grain company can be exposed to commodity price moves when it buys or sells physical grain. Futures contracts can reduce that risk, but the risk team needs visibility into whether the hedge is appropriately sized, whether basis is moving against the company, and whether margin or counterparty pressure is increasing.

## Technical Approach

- Generated realistic synthetic datasets in Python using pandas and numpy.
- Stored raw tables as CSV files for Power BI ingestion.
- Created a SQLite schema and SQL query layer to show database modeling ability.
- Produced analytical outputs for daily risk metrics, risk flags, stress tests, counterparty exposure, and executive KPI summaries.
- Documented Power BI pages and DAX measures so the dashboard can be built visually.

## Metrics I Can Explain

- Physical exposure
- Futures exposure
- Net open exposure
- Hedge ratio
- Basis and basis risk
- Daily and cumulative P&L
- Margin requirement
- VaR 95/99 approximation
- Stress test impact
- Counterparty exposure
- Risk flags

## Why It Matters for Employers

This project shows I can combine finance/risk thinking with practical data analytics. It also connects directly to commodity, treasury, FP&A, insurance, and operational risk reporting roles because the structure is similar: clean data, define KPIs, flag risk, explain movement, and prepare a dashboard for decision-makers.
