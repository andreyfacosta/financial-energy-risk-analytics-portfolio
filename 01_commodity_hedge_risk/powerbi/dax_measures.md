# DAX Measures

Create these measures in a `Measures` table after importing the CSV files.

```DAX
Physical Exposure CAD =
SUM ( daily_risk_metrics[physical_exposure_cad] )

Futures Exposure CAD =
SUM ( daily_risk_metrics[futures_exposure_cad] )

Net Open Exposure CAD =
SUM ( daily_risk_metrics[net_open_exposure_cad] )

Physical Quantity MT =
SUM ( daily_risk_metrics[physical_quantity_mt] )

Futures Quantity MT =
SUM ( daily_risk_metrics[futures_quantity_mt] )

Hedge Ratio =
DIVIDE (
    ABS ( [Futures Quantity MT] ),
    ABS ( [Physical Quantity MT] )
)

Daily P&L CAD =
SUM ( daily_risk_metrics[daily_pnl_cad] )

Cumulative P&L CAD =
SUM ( daily_risk_metrics[cumulative_pnl_cad] )

Basis CAD/MT =
AVERAGE ( daily_risk_metrics[basis_cad_mt] )

Basis Risk CAD =
SUM ( daily_risk_metrics[basis_risk_cad] )

Margin Requirement CAD =
SUM ( daily_risk_metrics[margin_requirement_cad] )

VaR 95 CAD =
SUM ( daily_risk_metrics[var_95_cad] )

VaR 99 CAD =
SUM ( daily_risk_metrics[var_99_cad] )

Stress Down 5pct CAD =
SUM ( daily_risk_metrics[stress_down_5pct_cad] )

Stress Up 5pct CAD =
SUM ( daily_risk_metrics[stress_up_5pct_cad] )

Open Risk Flags =
COUNTROWS ( risk_flags )

High Severity Flags =
CALCULATE (
    COUNTROWS ( risk_flags ),
    risk_flags[severity] = "High"
)

Counterparty Exposure CAD =
SUM ( counterparty_exposure[exposure_cad] )

Credit Utilization % =
AVERAGE ( counterparty_exposure[credit_utilization_pct] )

Stress Impact CAD =
SUM ( stress_test_results[stress_impact_cad] )
```

## Conditional Formatting Rules

Recommended visual rules:

- Hedge Ratio below 0.75: amber or red.
- Hedge Ratio above 1.25: amber or red.
- Net Open Exposure absolute value above CAD 1.5M: red.
- Credit Utilization % above 0.70: amber.
- Credit Utilization % above 0.90: red.
- VaR 99 CAD above CAD 750K: red.
