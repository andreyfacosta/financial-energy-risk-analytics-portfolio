# Commodity Hedge Risk Dashboard

Power BI-ready commodity risk analytics project for a synthetic Canadian grain company scenario. The project combines Python, pandas, SQL, SQLite, DAX planning, and executive dashboard design to show practical risk reporting skills for finance, commodity, BI, and operations analytics roles.

All data is synthetic. No confidential employer data is used.

## Dashboard Preview

Screenshots will be added after the dashboard is built in Power BI Desktop.

| Page | Screenshot file |
|---|---|
| Executive Summary | `docs/screenshots/executive_summary.png` |
| Exposure & Hedge Ratio | `docs/screenshots/exposure_hedge_ratio.png` |
| P&L and Margin | `docs/screenshots/pnl_margin.png` |
| Basis Risk | `docs/screenshots/basis_risk.png` |
| Stress Testing | `docs/screenshots/stress_testing.png` |
| Counterparty / Region View | `docs/screenshots/counterparty_region.png` |

See `docs/screenshots/README.md` for export instructions.

## Business Problem

A grain company buys and sells physical grain while using futures contracts to hedge commodity price risk. Leadership needs a dashboard that explains whether exposure is properly hedged, how P&L is moving, whether basis risk is increasing, how much margin is required, which stress scenarios matter, and whether any counterparties are approaching or exceeding credit limits.

## Executive Summary

The v1 synthetic dataset covers January 2025 through June 2025 and creates a complete analytics workflow:

- Raw business tables for physical transactions, futures positions, prices, FX, margins, commodities, counterparties, and calendar.
- Analytical outputs for daily risk metrics, counterparty exposure, risk flags, stress tests, and executive summary KPIs.
- SQLite database with raw tables, analytical tables, and SQL views.
- Power BI model and DAX documentation for a six-page dashboard.

Latest synthetic portfolio snapshot as of `2025-06-30`:

| Metric | Value |
|---|---:|
| Physical exposure CAD | 5,598,513 |
| Futures exposure CAD | -14,287,679 |
| Net open exposure CAD | -8,689,165 |
| Weighted hedge ratio | 3.03 |
| Daily P&L CAD | -52,623 |
| Cumulative P&L CAD | -1,472,393 |
| Margin requirement CAD | 5,373,329 |
| VaR 99 CAD | 760,926 |
| Open risk flags | 14 |
| Highest counterparty utilization | 159% |

## Key Risk Questions Answered

- What is the current physical exposure by commodity?
- How much of that exposure is hedged with futures?
- Is the portfolio under-hedged or over-hedged?
- What is the current net open exposure?
- Which commodities are driving daily and cumulative P&L?
- How much initial margin is required for open futures positions?
- Is basis risk increasing between cash and futures prices?
- What happens under commodity price, basis, and FX stress scenarios?
- Which counterparties are near or above credit limits?
- Which risk flags should be escalated to management?

## Key Metrics

- Physical exposure
- Futures exposure
- Net open exposure
- Hedge ratio
- Daily P&L
- Cumulative P&L
- Basis CAD/MT
- Basis risk
- Margin requirement
- VaR 95 and VaR 99 approximation
- Stress test impact
- Counterparty exposure
- Credit utilization
- Risk flags

## Data Model

Raw input tables:

- `physical_transactions.csv`
- `futures_positions.csv`
- `daily_cash_prices.csv`
- `daily_futures_prices.csv`
- `fx_rates.csv`
- `margin_requirements.csv`
- `counterparties.csv`
- `commodities.csv`
- `calendar.csv`

Analytical output tables:

- `daily_risk_metrics.csv`
- `counterparty_exposure.csv`
- `risk_flags.csv`
- `stress_test_results.csv`
- `risk_summary.csv`

SQLite database:

- `data/commodity_hedge_risk.sqlite`
- Includes raw tables, analytical tables, and views from `sql/analytics_queries.sql`.

## Analytical Workflow

1. `notebooks/01_generate_synthetic_data.py`
   - Creates realistic synthetic grain, futures, price, FX, margin, counterparty, and calendar data.
   - Writes raw CSV files.
   - Builds a SQLite database using `sql/schema.sql`.

2. `notebooks/02_analyze_hedge_risk.py`
   - Calculates physical exposure, futures exposure, hedge ratio, net open exposure, basis, P&L, margin, VaR approximation, stress scenarios, counterparty utilization, and risk flags.
   - Writes Power BI-ready analytical CSVs.
   - Writes analytical tables and views back into SQLite.

3. Power BI Desktop
   - Imports CSV files.
   - Builds relationships using calendar, commodity, and counterparty dimensions.
   - Creates DAX measures from `powerbi/dax_measures.md`.
   - Builds six dashboard pages using `powerbi/powerbi_build_guide.md`.

## Power BI Dashboard Pages

1. Executive Summary
   - KPI cards, cumulative P&L, net open exposure, risk flags, and counterparty exceptions.

2. Exposure & Hedge Ratio
   - Physical exposure, futures exposure, net open exposure, hedge ratio, and contract month view.

3. P&L and Margin
   - Daily P&L, running P&L, margin requirement, and futures position summary.

4. Basis Risk
   - Cash vs futures prices, basis CAD/MT, regional price view, and basis risk.

5. Stress Testing
   - Scenario impacts for commodity price, basis, and FX shocks.

6. Counterparty / Region View
   - Counterparty exposure, credit utilization, region exposure, and watch list flags.

## Key Insights from the Synthetic Dataset

- The latest synthetic portfolio is materially over-hedged, with a weighted hedge ratio of about `3.03`.
- Net open exposure is negative at about `CAD -8.69M`, indicating futures exposure is larger than the physical exposure in this snapshot.
- The latest daily P&L is negative at about `CAD -52.6K`, while cumulative project-period P&L is about `CAD -1.47M`.
- Initial margin requirement is about `CAD 5.37M`, which would be a management focus for treasury and liquidity planning.
- VaR 99 approximation is about `CAD 760.9K`, above the synthetic dashboard tolerance used in the risk flags.
- Counterparty utilization shows one limit-pressure case at `159%`, plus additional watch list counterparties above `70%`.
- The worst individual stress impacts in the current snapshot are tied to CAD weakening and bearish commodity shocks.

## Business Recommendations

- Review over-hedged commodities and determine whether futures positions should be reduced, rolled, or matched against upcoming physical transactions.
- Prioritize counterparty review for limit-pressure and watch list counterparties.
- Monitor margin requirement trend and coordinate with treasury on collateral planning.
- Add risk appetite thresholds by commodity to make escalation rules more precise.
- Review basis risk by region before relying on futures hedges as a full offset for cash market exposure.

## Skills Demonstrated

- Python data generation and reproducible analytics workflow.
- pandas transformation and risk metric calculation.
- SQLite-compatible schema design and SQL views.
- Financial and commodity risk reporting.
- Hedge exposure analysis and P&L approximation.
- VaR and stress testing approximation.
- Counterparty exposure and credit utilization analysis.
- Power BI model design and DAX measure planning.
- Executive dashboard storytelling.
- Recruiter-ready project documentation.

## How to Reproduce

From the repository root:

```powershell
python -m pip install -r requirements.txt
python 01_commodity_hedge_risk/notebooks/01_generate_synthetic_data.py
python 01_commodity_hedge_risk/notebooks/02_analyze_hedge_risk.py
```

Then open Power BI Desktop and follow:

```text
01_commodity_hedge_risk/powerbi/powerbi_build_guide.md
```

## Limitations

- The dataset is synthetic and designed for portfolio demonstration.
- VaR is an approximation based on rolling P&L volatility, not a full production-grade market risk model.
- Stress scenarios are simplified and deterministic.
- The Power BI `.pbix` must be built manually from the provided guide.
- The model does not include real broker statements, settlement logic, liquidity curves, or production trading controls.

## Interview Talking Points

- I translated a commodity hedge risk business problem into a full analytics workflow.
- I created synthetic data to avoid confidential information while preserving realistic business structure.
- I modeled both physical grain exposure and futures hedge exposure.
- I calculated hedge ratio, net open exposure, P&L, basis risk, margin, VaR approximation, stress impacts, and counterparty utilization.
- I prepared the data for Power BI and documented the model, DAX measures, and dashboard build steps.
- The dashboard is designed for executive risk review, not just technical analysis.
