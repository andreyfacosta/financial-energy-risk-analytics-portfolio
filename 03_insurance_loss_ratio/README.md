# Insurance Loss Ratio Dashboard

Power BI-ready group insurance analytics project for a synthetic benefits finance scenario. The project monitors earned premium, paid and incurred claims, loss ratio, claims frequency, severity, profitability, renewal risk, product mix, cohort trends, and high-risk employer groups.

All data is synthetic. No confidential employer data is used.

## Dashboard Preview

Screenshots will be added after the dashboard is built in Power BI Desktop.

| Page | Screenshot file |
|---|---|
| Executive Summary | `docs/screenshots/executive_summary.png` |
| Loss Ratio Trend | `docs/screenshots/loss_ratio_trend.png` |
| Policy / Employer Profitability | `docs/screenshots/policy_employer_profitability.png` |
| Claims Frequency & Severity | `docs/screenshots/claims_frequency_severity.png` |
| Product / Category Mix | `docs/screenshots/product_category_mix.png` |
| Renewal Risk Watchlist | `docs/screenshots/renewal_risk_watchlist.png` |

## Business Problem

A group insurance and benefits finance team needs to monitor whether premium revenue is sufficient to cover claims experience, which employers are becoming unprofitable, which products and claim categories drive loss ratio, and which groups need renewal action.

## Executive Summary

This project creates a synthetic group insurance portfolio with employers, members, products, policies, monthly premiums, claims, categories, and regions. The analysis layer creates monthly loss ratio, profitability, frequency, severity, product mix, renewal risk, and executive summary outputs for Power BI.

## Key Metrics

- Earned premium
- Paid claims
- Incurred claims
- Loss ratio
- Claims frequency
- Claims severity
- Member count
- Premium per member
- Claims per member
- Profitability
- Renewal risk
- High-risk employers
- Product/category mix
- Trend by month

## Data Model

Raw input tables:

- `group_policies.csv`
- `employers.csv`
- `members.csv`
- `premiums.csv`
- `claims.csv`
- `claim_categories.csv`
- `policy_products.csv`
- `regions.csv`
- `calendar.csv`

Analytical output tables:

- `monthly_loss_ratio.csv`
- `policy_profitability.csv`
- `claims_severity_frequency.csv`
- `renewal_risk_flags.csv`
- `employer_summary.csv`
- `product_mix_summary.csv`
- `executive_insurance_summary.csv`

SQLite database:

- `data/insurance_loss_ratio.sqlite`

## Analytical Workflow

1. `notebooks/01_generate_synthetic_data.py`
   - Generates employers, products, policies, members, premiums, claims, claim categories, regions, and calendar.
   - Writes raw CSV files and a SQLite database.

2. `notebooks/02_analyze_loss_ratio.py`
   - Calculates monthly loss ratio, claims frequency, claims severity, profitability, renewal risk, and product mix outputs.
   - Writes analytical CSV files and analytical SQLite tables/views.

3. Power BI Desktop
   - Imports CSV files.
   - Builds relationships around calendar, policies, employers, products, regions, and claim categories.
   - Creates DAX measures and six dashboard pages.

## Power BI Pages

1. Executive Summary
2. Loss Ratio Trend
3. Policy / Employer Profitability
4. Claims Frequency & Severity
5. Product / Category Mix
6. Renewal Risk Watchlist

## Synthetic Insights

- Some employers are profitable while others show elevated loss ratios and renewal risk.
- Claims severity and claims frequency explain different types of loss ratio pressure.
- Product mix matters: richer products tend to have higher premium and higher claim activity.
- Renewal watchlist flags are driven by loss ratio, negative profitability, and claims per member.

## Business Recommendations

- Prioritize renewal review for employers with high loss ratio and negative profitability.
- Separate high-frequency groups from high-severity groups before recommending rate actions.
- Review product/category mix where specific claim categories drive incurred claims.
- Use member-normalized metrics to avoid overreacting to employer size.
- Track loss ratio monthly instead of only at renewal.

## Skills Demonstrated

- Python and pandas insurance analytics workflow.
- SQL and SQLite data modeling.
- Loss ratio, frequency, severity, profitability, and renewal risk analysis.
- Power BI model planning and DAX measure design.
- Finance/insurance dashboard storytelling.

## How to Reproduce

From the repository root:

```powershell
python 03_insurance_loss_ratio/notebooks/01_generate_synthetic_data.py
python 03_insurance_loss_ratio/notebooks/02_analyze_loss_ratio.py
```

Then build the report manually using:

```text
03_insurance_loss_ratio/powerbi/powerbi_build_guide.md
```

## Limitations

- The data is synthetic and intended for portfolio demonstration.
- Incurred claims are simplified as paid claims plus an estimated reserve factor.
- Renewal risk rules are simplified and should not be treated as actuarial pricing.
- The Power BI `.pbix` must be built manually from the guide.

## Interview Talking Points

- I modeled a group insurance portfolio from raw policy, member, premium, and claim data.
- I calculated loss ratio, claims frequency, severity, profitability, and renewal risk.
- I prepared Power BI-ready analytical outputs, SQL views, DAX measures, and a dashboard build guide.
- The project shows how I connect finance, insurance operations, and BI reporting.
