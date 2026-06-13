# Power BI Build Guide

This guide explains how to manually build the Commodity Hedge Risk Dashboard in Power BI Desktop from the generated CSV files. It assumes the CSVs have already been created by running the two Python scripts from the repository root.

## 1. Generate Data Before Opening Power BI

From the repository root:

```powershell
python 01_commodity_hedge_risk/notebooks/01_generate_synthetic_data.py
python 01_commodity_hedge_risk/notebooks/02_analyze_hedge_risk.py
```

Confirm these files exist in `01_commodity_hedge_risk/data/`:

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

## 2. Import CSV Files

1. Open Power BI Desktop.
2. Select **Get data**.
3. Choose **Text/CSV**.
4. Navigate to `01_commodity_hedge_risk/data/`.
5. Import each CSV listed above.
6. Select **Transform Data** instead of loading directly if Power BI does not detect data types correctly.

## 3. Data Type Checks in Power Query

Set these types before loading:

| Table | Column | Type |
|---|---|---|
| calendar | date | Date |
| daily_risk_metrics | date | Date |
| daily_cash_prices | date | Date |
| daily_futures_prices | date | Date |
| fx_rates | date | Date |
| margin_requirements | date | Date |
| physical_transactions | trade_date, delivery_start, delivery_end | Date |
| futures_positions | trade_date | Date |
| stress_test_results | as_of_date | Date |
| all tables | ID/name/status/category fields | Text |
| all tables | exposure, price, quantity, margin, VaR, utilization fields | Decimal number |
| calendar | year, month, quarter, week, is_month_end | Whole number |

Click **Close & Apply**.

## 4. Date Table Instructions

Use the imported `calendar` table as the date table.

1. Go to **Table view**.
2. Select `calendar`.
3. Go to **Table tools**.
4. Select **Mark as date table**.
5. Choose `calendar[date]`.

Do not create a separate auto date table. The imported `calendar.csv` is already aligned with the synthetic market data period.

## 5. Relationship Model

Create these relationships in **Model view**:

| From table | Column | To table | Column | Cardinality | Cross-filter |
|---|---|---|---|---|---|
| calendar | date | daily_risk_metrics | date | One-to-many | Single |
| calendar | date | daily_cash_prices | date | One-to-many | Single |
| calendar | date | daily_futures_prices | date | One-to-many | Single |
| calendar | date | fx_rates | date | One-to-one or one-to-many | Single |
| calendar | date | margin_requirements | date | One-to-many | Single |
| calendar | date | risk_flags | date | One-to-many | Single |
| calendar | date | stress_test_results | as_of_date | One-to-many | Single |
| commodities | commodity_id | daily_risk_metrics | commodity_id | One-to-many | Single |
| commodities | commodity_id | physical_transactions | commodity_id | One-to-many | Single |
| commodities | commodity_id | futures_positions | commodity_id | One-to-many | Single |
| commodities | commodity_id | daily_cash_prices | commodity_id | One-to-many | Single |
| commodities | commodity_id | daily_futures_prices | commodity_id | One-to-many | Single |
| commodities | commodity_id | margin_requirements | commodity_id | One-to-many | Single |
| commodities | commodity_id | risk_flags | commodity_id | One-to-many | Single |
| commodities | commodity_id | stress_test_results | commodity_id | One-to-many | Single |
| counterparties | counterparty_id | physical_transactions | counterparty_id | One-to-many | Single |
| counterparties | counterparty_id | counterparty_exposure | counterparty_id | One-to-one or one-to-many | Single |

Recommended model layout:

- Put `calendar`, `commodities`, and `counterparties` at the top as dimensions.
- Put `daily_risk_metrics`, `risk_flags`, `stress_test_results`, and `counterparty_exposure` in the center as dashboard fact tables.
- Put raw transactional tables on the lower part of the model.

## 6. Measures Table

1. Go to **Home**.
2. Select **Enter data**.
3. Create a one-column table with one row:

| Measure Group |
|---|
| Commodity Hedge Risk |

4. Name the table `Measures`.
5. Hide the `Measure Group` column after creating measures.
6. Copy the measures from `powerbi/dax_measures.md`.

Minimum measures for the first build:

```DAX
Physical Exposure CAD =
SUM ( daily_risk_metrics[physical_exposure_cad] )

Futures Exposure CAD =
SUM ( daily_risk_metrics[futures_exposure_cad] )

Net Open Exposure CAD =
SUM ( daily_risk_metrics[net_open_exposure_cad] )

Absolute Net Open Exposure CAD =
SUMX (
    daily_risk_metrics,
    ABS ( daily_risk_metrics[net_open_exposure_cad] )
)

Physical Quantity MT =
SUM ( daily_risk_metrics[physical_quantity_mt] )

Futures Quantity MT =
SUM ( daily_risk_metrics[futures_quantity_mt] )

Absolute Physical Quantity MT =
SUMX (
    daily_risk_metrics,
    ABS ( daily_risk_metrics[physical_quantity_mt] )
)

Absolute Futures Quantity MT =
SUMX (
    daily_risk_metrics,
    ABS ( daily_risk_metrics[futures_quantity_mt] )
)

Hedge Ratio =
DIVIDE (
    [Absolute Futures Quantity MT],
    [Absolute Physical Quantity MT]
)

Latest Reporting Date =
MAXX (
    ALL ( daily_risk_metrics[date] ),
    daily_risk_metrics[date]
)

Latest Net Open Exposure CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Net Open Exposure CAD],
        daily_risk_metrics[date] = LatestDate
    )

Latest Hedge Ratio =
VAR LatestDate = [Latest Reporting Date]
VAR LatestFutures =
    CALCULATE (
        [Absolute Futures Quantity MT],
        daily_risk_metrics[date] = LatestDate
    )
VAR LatestPhysical =
    CALCULATE (
        [Absolute Physical Quantity MT],
        daily_risk_metrics[date] = LatestDate
    )
RETURN
    DIVIDE ( LatestFutures, LatestPhysical )

Daily P&L CAD =
SUM ( daily_risk_metrics[daily_pnl_cad] )

Latest Daily P&L CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Daily P&L CAD],
        daily_risk_metrics[date] = LatestDate
    )

Running P&L CAD =
CALCULATE (
    [Daily P&L CAD],
    FILTER (
        ALLSELECTED ( calendar[date] ),
        calendar[date] <= MAX ( calendar[date] )
    )
)

Margin Requirement CAD =
SUM ( daily_risk_metrics[margin_requirement_cad] )

Latest Margin Requirement CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Margin Requirement CAD],
        daily_risk_metrics[date] = LatestDate
    )

VaR 99 CAD =
SUM ( daily_risk_metrics[var_99_cad] )

Latest VaR 99 CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [VaR 99 CAD],
        daily_risk_metrics[date] = LatestDate
    )

Average Basis CAD/MT =
AVERAGE ( daily_risk_metrics[basis_cad_mt] )

Open Risk Flags =
COUNTROWS ( risk_flags )

High Risk Flag Count =
CALCULATE (
    COUNTROWS ( risk_flags ),
    risk_flags[severity] = "High"
)

Latest High Risk Flag Count =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [High Risk Flag Count],
        risk_flags[date] = LatestDate
    )

Counterparty Exposure CAD =
SUM ( counterparty_exposure[exposure_cad] )

Max Credit Utilization % =
MAX ( counterparty_exposure[credit_utilization_pct] )

Stress Impact CAD =
SUM ( stress_test_results[stress_impact_cad] )

Worst Stress Scenario Impact CAD =
MINX (
    VALUES ( stress_test_results[scenario] ),
    CALCULATE ( [Stress Impact CAD] )
)
```

## 7. Report Theme and Page Setup

Recommended report setup:

- Canvas: 16:9.
- Page background: white or very light gray.
- Visual background: white.
- Main accent: dark blue or charcoal.
- Risk colors: red for high, amber for medium, green for within tolerance.
- Use concise titles with business language.

Suggested slicers on all pages:

- `calendar[date]`
- `commodities[commodity_name]`
- `daily_risk_metrics[contract_month]`

## 8. Page 1 - Executive Summary

Purpose: show the current risk position and exceptions.

Visuals:

1. KPI card: `Latest Net Open Exposure CAD`
2. KPI card: `Latest Hedge Ratio`
3. KPI card: `Latest Daily P&L CAD`
4. KPI card: `Running P&L CAD`
5. KPI card: `Latest Margin Requirement CAD`
6. KPI card: `Latest VaR 99 CAD`
7. KPI card: `Latest High Risk Flag Count`
8. Line chart:
   - X-axis: `calendar[date]`
   - Y-axis: `Running P&L CAD`
   - Legend: `commodities[commodity_name]`
9. Bar chart:
   - Axis: `commodities[commodity_name]`
   - Values: `Net Open Exposure CAD`
10. Table:
   - `risk_flags[date]`
   - `risk_flags[commodity_name]`
   - `risk_flags[metric]`
   - `risk_flags[severity]`
   - `risk_flags[value]`
   - `risk_flags[threshold]`

Conditional formatting:

- Apply red background to `risk_flags[severity] = High`.
- Apply amber background to `risk_flags[severity] = Medium`.
- Use red data labels for negative P&L.

Validation:

- With no slicers applied, latest net open exposure should match `risk_summary.csv`.
- Latest hedge ratio should be near the weighted hedge ratio in `risk_summary.csv`.

## 9. Page 2 - Exposure & Hedge Ratio

Purpose: explain whether physical exposure is properly hedged.

Visuals:

1. Line and clustered column chart:
   - X-axis: `calendar[date]`
   - Column values: `Physical Exposure CAD`, `Futures Exposure CAD`
   - Line values: `Net Open Exposure CAD`
   - Legend: `commodities[commodity_name]`
2. Line chart:
   - X-axis: `calendar[date]`
   - Y-axis: `Hedge Ratio`
   - Legend: `commodities[commodity_name]`
3. Matrix:
   - Rows: `commodities[commodity_name]`
   - Columns: `daily_risk_metrics[contract_month]`
   - Values: `Physical Quantity MT`, `Futures Quantity MT`, `Net Open Quantity MT`
4. KPI card:
   - `Absolute Net Open Exposure CAD`

Slicers:

- Commodity
- Contract month
- Date

Conditional formatting:

- Hedge ratio below 0.75: amber.
- Hedge ratio above 1.25: red.
- Absolute net open exposure above CAD 1.5M: red.

## 10. Page 3 - P&L and Margin

Purpose: show mark-to-market movement and collateral pressure.

Visuals:

1. Column chart:
   - X-axis: `calendar[date]`
   - Y-axis: `Daily P&L CAD`
   - Legend: `commodities[commodity_name]`
2. Line chart:
   - X-axis: `calendar[date]`
   - Y-axis: `Running P&L CAD`
3. Bar chart:
   - Axis: `commodities[commodity_name]`
   - Values: `Margin Requirement CAD`
4. Table:
   - `futures_positions[broker]`
   - `futures_positions[exchange]`
   - `futures_positions[contract_month]`
   - `futures_positions[buy_sell]`
   - `futures_positions[contracts]`
   - `futures_positions[initial_margin_usd_per_contract]`

Conditional formatting:

- Negative P&L: red.
- Positive P&L: green.
- High margin requirement: red or amber.

## 11. Page 4 - Basis Risk

Purpose: show local cash price divergence from futures prices.

Visuals:

1. Line chart:
   - X-axis: `calendar[date]`
   - Y-axis: `Average Basis CAD/MT`
   - Legend: `commodities[commodity_name]`
2. Line chart:
   - X-axis: `calendar[date]`
   - Y-axis: `daily_risk_metrics[avg_cash_price_cad_mt]` and `daily_risk_metrics[futures_price_cad_mt]`
   - Legend: `commodities[commodity_name]`
3. Bar chart:
   - Axis: `commodities[commodity_name]`
   - Values: `Basis Risk CAD`
4. Table:
   - `daily_cash_prices[region]`
   - `daily_cash_prices[commodity_id]`
   - `daily_cash_prices[cash_price_cad_mt]`

Slicers:

- Region from `daily_cash_prices[region]`
- Commodity
- Date

## 12. Page 5 - Stress Testing

Purpose: estimate downside and upside under price, basis, and FX shocks.

Visuals:

1. KPI card:
   - `Worst Stress Scenario Impact CAD`
2. Clustered bar chart:
   - Axis: `stress_test_results[scenario]`
   - Values: `Stress Impact CAD`
   - Legend: `commodities[commodity_name]`
3. Matrix:
   - Rows: `stress_test_results[scenario]`
   - Columns: `commodities[commodity_name]`
   - Values: `Stress Impact CAD`
4. Table:
   - `stress_test_results[scenario]`
   - `stress_test_results[cash_shock_pct]`
   - `stress_test_results[futures_shock_pct]`
   - `stress_test_results[basis_shift_cad_mt]`
   - `stress_test_results[fx_shock_pct]`
   - `stress_test_results[stress_impact_cad]`

Conditional formatting:

- Most negative stress impacts: red.
- Positive or offsetting impacts: green.

## 13. Page 6 - Counterparty / Region View

Purpose: identify credit concentration and counterparty watch list items.

Visuals:

1. KPI card:
   - `Max Credit Utilization %`
2. KPI card:
   - `Counterparties Over Limit`
3. Bar chart:
   - Axis: `counterparty_exposure[counterparty_name]`
   - Values: `Counterparty Exposure CAD`
4. Table:
   - `counterparty_exposure[counterparty_name]`
   - `counterparty_exposure[counterparty_type]`
   - `counterparty_exposure[region]`
   - `counterparty_exposure[credit_rating]`
   - `counterparty_exposure[credit_limit_cad]`
   - `counterparty_exposure[exposure_cad]`
   - `counterparty_exposure[credit_utilization_pct]`
   - `counterparty_exposure[risk_flag]`
5. Bar chart:
   - Axis: `counterparty_exposure[region]`
   - Values: `Counterparty Exposure CAD`

Conditional formatting:

- `risk_flag = Limit pressure`: red.
- `risk_flag = Watch list`: amber.
- `risk_flag = Within limit`: green.
- Credit utilization above 1: red.

## 14. Final Validation Checks

Before exporting screenshots:

- All six pages have titles and slicers.
- KPI cards respond to commodity slicers.
- `calendar` is marked as the date table.
- Relationships are active and single-direction unless intentionally changed.
- Measures compile with no DAX errors.
- Latest executive KPIs reconcile to `risk_summary.csv` when no slicers are applied.
- Counterparty table shows at least one `Limit pressure` row in the synthetic dataset.
- Stress testing page shows negative and positive scenario impacts.
- No visuals show unexpected blank values.

## 15. Export Screenshots

After finishing the `.pbix`, export page screenshots and save them in:

```text
01_commodity_hedge_risk/docs/screenshots/
```

Use these exact filenames:

- `executive_summary.png`
- `exposure_hedge_ratio.png`
- `pnl_margin.png`
- `basis_risk.png`
- `stress_testing.png`
- `counterparty_region.png`

These screenshots can then be referenced in the project README and LinkedIn Featured section.
