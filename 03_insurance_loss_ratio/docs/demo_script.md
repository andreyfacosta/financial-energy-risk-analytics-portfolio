# 2-3 Minute Interview Demo Script

This project is a group insurance loss ratio dashboard built with synthetic benefits finance data.

The business problem is that an insurance or benefits finance team needs to monitor whether premium revenue is covering claims experience, which employers are becoming unprofitable, which products and categories are driving claims, and which groups should be reviewed before renewal.

I built the pipeline in Python with pandas. The first script generates synthetic employers, group policies, members, monthly premiums, claims, claim categories, products, regions, and a calendar table. The second script calculates monthly loss ratio, policy profitability, claims frequency, claims severity, product mix, and renewal risk flags.

The key metrics are earned premium, paid claims, incurred claims, loss ratio, member count, premium per member, claims per member, claims frequency, claims severity, profitability, and renewal risk.

The Power BI dashboard is designed with six pages: Executive Summary, Loss Ratio Trend, Policy and Employer Profitability, Claims Frequency and Severity, Product and Category Mix, and Renewal Risk Watchlist.

The most important business distinction is whether a high loss ratio comes from high frequency, high severity, or both. That changes the recommendation: pricing review, benefit design review, claims management, or simple monitoring.

What I would improve next is adding credibility weighting, renewal pricing scenarios, and more detailed cohort analysis by age band and coverage tier.
