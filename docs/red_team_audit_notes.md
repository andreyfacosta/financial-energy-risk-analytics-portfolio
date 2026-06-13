# Red-Team Audit Notes

This file documents portfolio claims, limitations, and remaining manual work before creating Power BI screenshots or using the repository in applications.

## Safe to Claim

- The repository is Power BI-ready.
- Each project includes synthetic data, Python generation and analysis scripts, CSV outputs, SQLite database, SQL schema, SQL analytical queries, DAX documentation, Power BI build guide, README, demo script, and screenshot instructions.
- The data is synthetic and designed for portfolio demonstration.
- The projects demonstrate Python, pandas, SQL, SQLite, Power BI modeling preparation, DAX measure planning, executive reporting, and business-risk storytelling.
- Project 1 demonstrates commodity hedge risk reporting concepts.
- Project 2 demonstrates drilling project controls and energy operations reporting concepts.
- Project 3 demonstrates group insurance loss ratio and renewal risk reporting concepts.
- Project 4 demonstrates pension investment risk and retirement analytics concepts.

## Not Safe to Claim Yet

- Do not claim finished Power BI dashboards until `.pbix` files are manually built.
- Do not claim screenshots exist until PNGs are exported into each `docs/screenshots/` folder.
- Do not claim production-grade market risk, actuarial, project controls, or investment systems.
- Do not claim the metrics are validated against real employer data.
- Do not claim confidential employer experience, internal tools, real trading data, real claims data, or real pension data.
- Do not claim automated job applications or recruiter outreach.

## What Remains Manual

- Build each `.pbix` manually in Power BI Desktop using each project's build guide.
- Create DAX measures inside Power BI Desktop.
- Validate visuals against executive summary CSVs.
- Export screenshots with the required filenames.
- Add final screenshot links or embedded images after PNGs exist.
- Optionally add a short video walkthrough after dashboards are built.

## Known Limitations

- All data is synthetic.
- Metrics are demonstration-grade and simplified.
- VaR, stress testing, loss ratio, forecast final cost, allocation drift, and retirement projections are simplified examples.
- SQLite databases are included for portfolio review and validation; they are not production warehouses.
- DAX measures are documented in Markdown and still need manual creation/testing inside Power BI Desktop.
- `.pbix` files are intentionally not included yet.

## DAX Aggregation Warnings

- Avoid summing percentages unless the measure explicitly recalculates a ratio from numerator and denominator.
- Project 2 daily cumulative cost should be summed by latest value per well, not `MAX` across all wells.
- Project 3 premium mix should be calculated as selected product premium divided by selected total premium, not by summing stored mix percentages.
- Project 4 allocation should be weighted by market value; do not sum allocation percentages across multiple portfolios.
- Use summary tables for executive cards when the metric is a final snapshot.
- Use daily or monthly analytical tables for trend visuals.

## Recruiter-Facing Usage Guidance

- Lead with Project 1 and Project 2 for commodity risk and energy operations relevance.
- Use Project 3 for insurance/benefits finance roles.
- Use Project 4 for investment, pension, treasury, or risk reporting roles.
- Say "Power BI-ready portfolio" until dashboards and screenshots are created.
- Emphasize the business problem, metric design, reproducible workflow, and executive communication.
- Be clear that the data is synthetic and no confidential employer data is included.

## Screenshot Status

Screenshots are pending for all projects.

Required manual folders:

- `01_commodity_hedge_risk/docs/screenshots/`
- `02_drilling_project_controls/docs/screenshots/`
- `03_insurance_loss_ratio/docs/screenshots/`
- `04_pension_investment_risk/docs/screenshots/`

Each project has a screenshot README listing the required PNG filenames.
