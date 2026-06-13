# DAX Measures

Create a disconnected table named `Measures` in Power BI Desktop and store these measures there. The column names below match the generated CSV files in `01_commodity_hedge_risk/data/`.

## Format Recommendations

| Measure type | Suggested format |
|---|---|
| CAD exposure, P&L, margin, VaR, stress impact | Currency, CAD, 0 decimals |
| Quantities | Whole number or decimal, MT suffix in visual title |
| Hedge ratio | Decimal number, 2 decimals |
| Basis | Decimal number, 2 decimals |
| Percentages | Percentage, 1-2 decimals |
| Counts | Whole number |

## Core Exposure Measures

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

Net Open Quantity MT =
SUM ( daily_risk_metrics[net_open_quantity_mt] )

Hedge Ratio =
DIVIDE (
    [Absolute Futures Quantity MT],
    [Absolute Physical Quantity MT]
)
```

## Latest Snapshot Measures

Use these for KPI cards on the Executive Summary page. They return the latest available date in the imported dataset while preserving filters such as commodity.

```DAX
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

Latest Absolute Net Open Exposure CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Absolute Net Open Exposure CAD],
        daily_risk_metrics[date] = LatestDate
    )

Latest Physical Quantity MT =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Physical Quantity MT],
        daily_risk_metrics[date] = LatestDate
    )

Latest Futures Quantity MT =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Futures Quantity MT],
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

Latest Daily P&L CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Daily P&L CAD],
        daily_risk_metrics[date] = LatestDate
    )

Latest Cumulative P&L CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Cumulative P&L CAD],
        daily_risk_metrics[date] = LatestDate
    )

Latest Margin Requirement CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Margin Requirement CAD],
        daily_risk_metrics[date] = LatestDate
    )

Latest VaR 99 CAD =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [VaR 99 CAD],
        daily_risk_metrics[date] = LatestDate
    )
```

## P&L and Risk Measures

```DAX
Daily P&L CAD =
SUM ( daily_risk_metrics[daily_pnl_cad] )

Cumulative P&L CAD =
VAR LatestVisibleDate = MAX ( calendar[date] )
RETURN
    CALCULATE (
        SUM ( daily_risk_metrics[cumulative_pnl_cad] ),
        daily_risk_metrics[date] = LatestVisibleDate
    )

Running P&L CAD =
CALCULATE (
    [Daily P&L CAD],
    FILTER (
        ALLSELECTED ( calendar[date] ),
        calendar[date] <= MAX ( calendar[date] )
    )
)

YTD P&L CAD =
TOTALYTD (
    [Daily P&L CAD],
    calendar[date]
)

Average Basis CAD/MT =
AVERAGE ( daily_risk_metrics[basis_cad_mt] )

Basis Risk CAD =
SUM ( daily_risk_metrics[basis_risk_cad] )

Margin Requirement CAD =
SUM ( daily_risk_metrics[margin_requirement_cad] )

VaR 95 CAD =
SUM ( daily_risk_metrics[var_95_cad] )

VaR 99 CAD =
SUM ( daily_risk_metrics[var_99_cad] )
```

## Stress Testing Measures

```DAX
Stress Down 5pct CAD =
SUM ( daily_risk_metrics[stress_down_5pct_cad] )

Stress Up 5pct CAD =
SUM ( daily_risk_metrics[stress_up_5pct_cad] )

Stress Impact CAD =
SUM ( stress_test_results[stress_impact_cad] )

Worst Stress Scenario Impact CAD =
MINX (
    VALUES ( stress_test_results[scenario] ),
    CALCULATE ( [Stress Impact CAD] )
)

Best Stress Scenario Impact CAD =
MAXX (
    VALUES ( stress_test_results[scenario] ),
    CALCULATE ( [Stress Impact CAD] )
)
```

## Risk Flag Measures

```DAX
Open Risk Flags =
COUNTROWS ( risk_flags )

High Risk Flag Count =
CALCULATE (
    COUNTROWS ( risk_flags ),
    risk_flags[severity] = "High"
)

Medium Risk Flag Count =
CALCULATE (
    COUNTROWS ( risk_flags ),
    risk_flags[severity] = "Medium"
)

Latest Open Risk Flags =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [Open Risk Flags],
        risk_flags[date] = LatestDate
    )

Latest High Risk Flag Count =
VAR LatestDate = [Latest Reporting Date]
RETURN
    CALCULATE (
        [High Risk Flag Count],
        risk_flags[date] = LatestDate
    )
```

## Counterparty Measures

```DAX
Counterparty Exposure CAD =
SUM ( counterparty_exposure[exposure_cad] )

Average Credit Utilization % =
AVERAGE ( counterparty_exposure[credit_utilization_pct] )

Max Credit Utilization % =
MAX ( counterparty_exposure[credit_utilization_pct] )

Counterparties Over Limit =
CALCULATE (
    DISTINCTCOUNT ( counterparty_exposure[counterparty_id] ),
    counterparty_exposure[credit_utilization_pct] >= 1
)
```

## Validation Notes

- `Latest Hedge Ratio` should be close to the `Weighted hedge ratio` row in `risk_summary.csv` for the full portfolio.
- `Latest Net Open Exposure CAD` should match the `Net open exposure CAD` row in `risk_summary.csv` when no slicers are applied.
- `Latest VaR 99 CAD` should match the `VaR 99 CAD` row in `risk_summary.csv` when no slicers are applied.
- `High Risk Flag Count` should equal the number of high-severity rows in `risk_flags.csv` for the selected filter context.
- `Max Credit Utilization %` should match the maximum value in `counterparty_exposure[credit_utilization_pct]`.

## Conditional Formatting Rules

- Hedge Ratio below 0.75: amber.
- Hedge Ratio above 1.25: amber or red.
- Absolute Net Open Exposure above CAD 1.5M: red.
- Credit Utilization % above 70 percent: amber.
- Credit Utilization % above 90 percent: red.
- VaR 99 CAD above CAD 750K: red.
- High Risk Flag Count above 0: red.
