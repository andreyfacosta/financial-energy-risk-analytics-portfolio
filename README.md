# Financial & Energy Risk Analytics Portfolio

Power BI-ready portfolio of financial, commodity, energy, insurance, pension, and operations risk analytics projects using Python, SQL, pandas, SQLite, and DAX documentation. The `.pbix` reports and screenshots are still manual next steps.

Built for remote Canada/global roles where financial risk, BI reporting, commodity exposure, energy operations, insurance analytics, and investment risk overlap.

## Portfolio Status

| Project | Status | Best target roles |
|---|---|---|
| [01 Commodity Hedge Risk Dashboard](01_commodity_hedge_risk/README.md) | Power BI-ready, screenshots pending | Commodity Risk Analyst, Risk Reporting Analyst, Financial Data Analyst |
| [02 Drilling Project Controls Dashboard](02_drilling_project_controls/README.md) | Power BI-ready, screenshots pending | Energy Data Analyst, Project Controls Analyst, Operations Data Analyst |
| [03 Insurance Loss Ratio Dashboard](03_insurance_loss_ratio/README.md) | Power BI-ready, screenshots pending | Insurance Data Analyst, Financial Data Analyst, BI Analyst - Finance |
| [04 Pension Investment Risk Dashboard](04_pension_investment_risk/README.md) | Power BI-ready, screenshots pending | Investment Risk Analyst, Pension Analyst, Treasury/Risk Reporting Analyst |

## Suggested Recruiter Path

Start with Project 1, then Project 2:

1. [Commodity Hedge Risk Dashboard](01_commodity_hedge_risk/README.md) shows financial and commodity risk reporting.
2. [Drilling Project Controls Dashboard](02_drilling_project_controls/README.md) connects energy operations, cost control, schedule risk, and executive BI.
3. [Insurance Loss Ratio Dashboard](03_insurance_loss_ratio/README.md) adds Canadian finance/insurance relevance.
4. [Pension Investment Risk Dashboard](04_pension_investment_risk/README.md) adds investment and retirement risk analytics.

Recruiter note: this is a Power BI-ready portfolio. The data, scripts, SQL, DAX documentation, and build guides are complete, but the Power BI Desktop reports and screenshots still need to be created manually.

## Power BI Build Guides

- [Project 1 Power BI Build Guide](01_commodity_hedge_risk/powerbi/powerbi_build_guide.md)
- [Project 2 Power BI Build Guide](02_drilling_project_controls/powerbi/powerbi_build_guide.md)
- [Project 3 Power BI Build Guide](03_insurance_loss_ratio/powerbi/powerbi_build_guide.md)
- [Project 4 Power BI Build Guide](04_pension_investment_risk/powerbi/powerbi_build_guide.md)

## Demo Scripts

- [Commodity Hedge Risk Demo](01_commodity_hedge_risk/docs/demo_script.md)
- [Drilling Project Controls Demo](02_drilling_project_controls/docs/demo_script.md)
- [Insurance Loss Ratio Demo](03_insurance_loss_ratio/docs/demo_script.md)
- [Pension Investment Risk Demo](04_pension_investment_risk/docs/demo_script.md)

## Target Roles

- Remote Financial Data Analyst
- Risk Reporting Analyst
- BI Analyst - Finance / Operations
- Energy Data Analyst
- Operations Data Analyst
- Commodity Risk Analyst
- Project Controls Data Analyst
- Insurance Data Analyst
- Treasury / Risk Reporting Analyst
- FP&A Analyst with Power BI
- Data Analyst SQL / Power BI / Python

## Tools and Skills Demonstrated

- Python 3, pandas, numpy, pathlib
- SQL and SQLite data modeling
- CSV-based analytics workflows for Power BI
- DAX measure planning
- Financial risk metrics, exposure reporting, P&L, VaR approximation, stress testing
- Project controls metrics, AFE budget, cost variance, schedule variance, NPT, HSE
- Insurance metrics, loss ratio, claims frequency, severity, profitability, renewal risk
- Investment metrics, allocation, returns, benchmark comparison, volatility, drawdown, FX exposure
- Executive dashboard storytelling and recruiter-facing documentation

## How to Reproduce All Projects

```powershell
python -m pip install -r requirements.txt

python 01_commodity_hedge_risk/notebooks/01_generate_synthetic_data.py
python 01_commodity_hedge_risk/notebooks/02_analyze_hedge_risk.py

python 02_drilling_project_controls/notebooks/01_generate_synthetic_data.py
python 02_drilling_project_controls/notebooks/02_analyze_project_controls.py

python 03_insurance_loss_ratio/notebooks/01_generate_synthetic_data.py
python 03_insurance_loss_ratio/notebooks/02_analyze_loss_ratio.py

python 04_pension_investment_risk/notebooks/01_generate_synthetic_data.py
python 04_pension_investment_risk/notebooks/02_analyze_investment_risk.py
```

After running the scripts, open each Power BI build guide and manually create the `.pbix` dashboards from the generated CSV files.

## Career Assets

- [LinkedIn drafts](career_assets/linkedin/)
- [Resume bullets](career_assets/resumes/)
- [Recruiter messages](career_assets/recruiter_messages/)
- [Interview prep](career_assets/interview_prep/)
- [Application tracker template](application_tracker_template.csv)
- [Target roles](target_roles.md)
- [Keywords](keywords.md)

## Data Notice

All datasets are synthetic and realistic by design. No confidential employer data, credentials, paid APIs, or private information are used. Metrics are demonstration-grade portfolio examples, not production risk, actuarial, project controls, or investment systems.
