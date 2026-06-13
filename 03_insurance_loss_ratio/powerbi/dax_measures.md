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
SUM ( monthly_loss_ratio[profitability_cad] )

Loss Ratio =
DIVIDE ( [Incurred Claims CAD], [Earned Premium CAD] )

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
Premium Mix % =
SUM ( product_mix_summary[premium_mix_pct] )

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
