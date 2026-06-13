# Power BI Model Specification

## Data Import

Import CSV files from `01_commodity_hedge_risk/data/`.

Recommended import tables:

- `calendar.csv`
- `commodities.csv`
- `counterparties.csv`
- `physical_transactions.csv`
- `futures_positions.csv`
- `daily_cash_prices.csv`
- `daily_futures_prices.csv`
- `fx_rates.csv`
- `margin_requirements.csv`
- `daily_risk_metrics.csv`
- `counterparty_exposure.csv`
- `risk_flags.csv`
- `stress_test_results.csv`
- `risk_summary.csv`

## Relationships

Create these relationships:

| From table | Column | To table | Column | Cardinality |
|---|---|---|---|---|
| calendar | date | daily_risk_metrics | date | One-to-many |
| calendar | date | daily_cash_prices | date | One-to-many |
| calendar | date | daily_futures_prices | date | One-to-many |
| calendar | date | fx_rates | date | One-to-one or one-to-many |
| commodities | commodity_id | daily_risk_metrics | commodity_id | One-to-many |
| commodities | commodity_id | physical_transactions | commodity_id | One-to-many |
| commodities | commodity_id | futures_positions | commodity_id | One-to-many |
| commodities | commodity_id | daily_cash_prices | commodity_id | One-to-many |
| commodities | commodity_id | daily_futures_prices | commodity_id | One-to-many |
| counterparties | counterparty_id | physical_transactions | counterparty_id | One-to-many |
| counterparties | counterparty_id | counterparty_exposure | counterparty_id | One-to-one or one-to-many |

Set cross-filter direction to single unless a visual requires otherwise.

## Measures Table

Create a disconnected table named `Measures` and store DAX measures there.

## Recommended Pages

### 1. Executive Summary

Visuals:
- KPI cards: Net Open Exposure, Hedge Ratio, Daily P&L, Cumulative P&L, Margin Requirement, VaR 99, Open Risk Flags.
- Line chart: Cumulative P&L by date.
- Bar chart: Net open exposure by commodity.
- Table: Top risk flags.

### 2. Exposure & Hedge Ratio

Visuals:
- Combo chart: physical exposure, futures exposure, net exposure by date.
- Line chart: hedge ratio by commodity.
- Matrix: exposure by commodity and contract month.
- Conditional formatting for hedge ratio outside 0.75 to 1.25.

### 3. P&L and Margin

Visuals:
- Daily P&L waterfall or column chart.
- Cumulative P&L line chart.
- Margin requirement by commodity.
- Broker/position summary from futures data.

### 4. Basis Risk

Visuals:
- Basis line chart by commodity.
- Basis risk CAD by commodity.
- Cash vs futures price trend.
- Region slicer from cash prices.

### 5. Stress Testing

Visuals:
- Scenario impact by commodity.
- Total scenario impact.
- Sensitivity table with cash shock, futures shock, FX shock, and basis shift.

### 6. Counterparty / Region View

Visuals:
- Counterparty exposure table with credit limit utilization.
- Region exposure map or bar chart.
- Risk flag slicer.
- Credit rating distribution.

## Slicers

- Date
- Commodity
- Region
- Contract month
- Risk severity
- Counterparty
- Credit rating

## Design Guidance

Use an executive risk reporting style:

- Neutral background.
- Red/amber/green conditional formatting.
- KPI cards at the top.
- Trend visuals in the middle.
- Exception tables at the bottom.
