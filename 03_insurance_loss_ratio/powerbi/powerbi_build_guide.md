# Power BI Build Guide

Use this guide to build the Insurance Loss Ratio Dashboard manually in Power BI Desktop.

## 1. Generate Data

From the repository root:

```powershell
python 03_insurance_loss_ratio/notebooks/01_generate_synthetic_data.py
python 03_insurance_loss_ratio/notebooks/02_analyze_loss_ratio.py
```

## 2. Import Tables

Import these CSV files from `03_insurance_loss_ratio/data/`:

- `calendar.csv`
- `group_policies.csv`
- `employers.csv`
- `members.csv`
- `premiums.csv`
- `claims.csv`
- `claim_categories.csv`
- `policy_products.csv`
- `regions.csv`
- `monthly_loss_ratio.csv`
- `policy_profitability.csv`
- `claims_severity_frequency.csv`
- `renewal_risk_flags.csv`
- `employer_summary.csv`
- `product_mix_summary.csv`
- `executive_insurance_summary.csv`

## 3. Data Types and Date Table

- Mark `calendar[date]` as the date table.
- Date fields: `calendar[date]`, `monthly_loss_ratio[month_start]`, `premiums[month_start]`, `claims[service_date]`, `claims[paid_date]`.
- Currency/decimal fields: premium, claims, profitability, severity, loss ratio, frequency.
- Text fields: employer, product, category, region, renewal risk.

## 4. Relationships

| From | To | Cardinality |
|---|---|---|
| `calendar[date]` | `monthly_loss_ratio[month_start]` | One-to-many |
| `employers[employer_id]` | `monthly_loss_ratio[employer_id]` | One-to-many |
| `employers[employer_id]` | `group_policies[employer_id]` | One-to-many |
| `employers[employer_id]` | `employer_summary[employer_id]` | One-to-one or one-to-many |
| `policy_products[product_id]` | `monthly_loss_ratio[product_id]` | One-to-many |
| `policy_products[product_id]` | `group_policies[product_id]` | One-to-many |
| `regions[region_id]` | `employers[region_id]` | One-to-many |
| `group_policies[policy_id]` | `monthly_loss_ratio[policy_id]` | One-to-many |
| `claim_categories[category_id]` | `claims[category_id]` | One-to-many |

Use single-direction filtering.

## 5. Measures

Create a `Measures` table and copy measures from `powerbi/dax_measures.md`.

## 6. Page Build

### Executive Summary

- KPI cards: `Earned Premium CAD`, `Incurred Claims CAD`, `Loss Ratio`, `Profitability CAD`, `Claim Count`, `High Risk Employers`.
- Line chart: `Loss Ratio` by `calendar[date]`.
- Bar chart: `Profitability CAD` by `employer_summary[employer_name]`.
- Table: employer, loss ratio, profitability, renewal risk.

### Loss Ratio Trend

- Line chart: loss ratio by month and product.
- Column chart: earned premium and incurred claims by month.
- Slicers: product category, region, employer.

### Policy / Employer Profitability

- Bar chart: profitability by employer.
- Table: policy, employer, product, premium, claims, loss ratio, profitability.
- Conditional formatting: loss ratio above 85 percent amber, above 95 percent red.

### Claims Frequency & Severity

- Scatter: claims frequency vs claims severity by employer.
- Bar chart: claim count by category.
- Card: claims per member.

### Product / Category Mix

- Donut or bar chart: premium mix by product category.
- Bar chart: incurred claims by claim category.
- Matrix: product category by region, showing premium, claims, and loss ratio.

### Renewal Risk Watchlist

- Table: employer, region, loss ratio, profitability, claims per member, renewal risk, recommended action.
- KPI cards: high risk employers, medium risk employers, unprofitable employers.

## 7. Conditional Formatting

- Loss ratio above 0.85: amber.
- Loss ratio above 0.95: red.
- Negative profitability: red.
- Renewal risk High: red.
- Renewal risk Medium: amber.

## 8. Final Validation

- Portfolio loss ratio reconciles to `executive_insurance_summary.csv`.
- Renewal watchlist contains high/medium/low categories.
- Trend pages respond to month, product, employer, and region filters.
