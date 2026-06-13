# DAX Measures

Create a disconnected `Measures` table and add these measures. Column names match the generated CSV files.

## Format Recommendations

| Measure type | Suggested format |
|---|---|
| Premium, claims, profitability, severity | Currency, CAD, 0 decimals |
| Loss ratio and mix | Percentage, 1-2 decimals |
| Counts | Whole number |

## Premium and Claims

```DAX
Earned Premium CAD =
SUM ( monthly_loss_ratio[earned_premium_cad] )

Paid Claims CAD =
SUM ( monthly_loss_ratio[paid_claims_cad] )

Incurred Claims CAD =
SUM ( monthly_loss_ratio[incurred_claims_cad] )

Profitability CAD =
[Earned Premium CAD] - [Incurred Claims CAD]

Loss Ratio =
DIVIDE ( [Incurred Claims CAD], [Earned Premium CAD] )

Selected Loss Ratio =
DIVIDE (
    SUM ( monthly_loss_ratio[incurred_claims_cad] ),
    SUM ( monthly_loss_ratio[earned_premium_cad] )
)

Policy Profitability CAD =
SUM ( policy_profitability[profitability_cad] )

Employer Profitability CAD =
SUM ( employer_summary[profitability_cad] )

Claim Count =
SUM ( monthly_loss_ratio[claim_count] )
```

## Frequency and Severity

```DAX
Member Count =
SUM ( monthly_loss_ratio[member_count] )

Claims Frequency =
DIVIDE ( [Claim Count], [Member Count] )

Claims Severity CAD =
DIVIDE ( [Incurred Claims CAD], [Claim Count] )

Premium per Member CAD =
DIVIDE ( [Earned Premium CAD], [Member Count] )

Claims per Member CAD =
DIVIDE ( [Incurred Claims CAD], [Member Count] )
```

## Renewal Risk

```DAX
High Risk Employers =
CALCULATE (
    DISTINCTCOUNT ( renewal_risk_flags[employer_id] ),
    renewal_risk_flags[renewal_risk] = "High"
)

Medium Risk Employers =
CALCULATE (
    DISTINCTCOUNT ( renewal_risk_flags[employer_id] ),
    renewal_risk_flags[renewal_risk] = "Medium"
)

Unprofitable Employers =
CALCULATE (
    DISTINCTCOUNT ( employer_summary[employer_id] ),
    employer_summary[profitability_cad] < 0
)
```

## Product Mix

```DAX
Product Mix Earned Premium CAD =
SUM ( product_mix_summary[earned_premium_cad] )

Premium Mix % =
DIVIDE (
    [Product Mix Earned Premium CAD],
    CALCULATE (
        [Product Mix Earned Premium CAD],
        ALLSELECTED ( product_mix_summary )
    )
)

Product Loss Ratio =
DIVIDE (
    SUM ( product_mix_summary[incurred_claims_cad] ),
    SUM ( product_mix_summary[earned_premium_cad] )
)
```

## Validation Notes

- `Loss Ratio` should reconcile to `executive_insurance_summary.csv`.
- `High Risk Employers` should match high renewal risk rows in `renewal_risk_flags.csv`.
- Use `monthly_loss_ratio` for trend visuals and `policy_profitability` for policy-level profitability ranking.
- Avoid using `SUM ( product_mix_summary[premium_mix_pct] )` in dashboard visuals; summing pre-calculated percentages can produce misleading totals under slicers.
- `Premium Mix %` recalculates the share from earned premium over the currently selected product mix denominator.
- `Profitability CAD` is derived from premium minus incurred claims so it stays consistent with slicers and the displayed loss ratio.
