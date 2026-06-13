# Drilling Project Controls Dashboard

Power BI-ready project controls dashboard for a synthetic petroleum drilling and oilfield operations scenario. The project monitors AFE budget, actual cost, schedule variance, drilling progress, non-productive time, rig utilization, contractor performance, HSE incidents, forecast final cost, and operational risk flags.

All data is synthetic. No confidential employer data is used.

## Dashboard Preview

Screenshots will be added after the dashboard is built in Power BI Desktop.

| Page | Screenshot file |
|---|---|
| Executive Summary | `docs/screenshots/executive_summary.png` |
| Budget vs Actual | `docs/screenshots/budget_vs_actual.png` |
| Schedule & NPT | `docs/screenshots/schedule_npt.png` |
| Rig / Contractor Performance | `docs/screenshots/rig_contractor_performance.png` |
| HSE & Operational Risk | `docs/screenshots/hse_operational_risk.png` |
| Well Detail | `docs/screenshots/well_detail.png` |

## Business Problem

A drilling operations team needs a management dashboard that combines AFE budgets, daily actual costs, operational progress, NPT events, rig utilization, contractor performance, HSE indicators, and forecast final cost. The goal is to identify wells at risk before cost and schedule overruns become surprises.

## Executive Summary

The synthetic dataset creates an end-to-end project controls workflow for multiple wells, rigs, and contractors. It includes raw operational tables, analytical output tables, a SQLite database, SQL views, DAX measures, and a six-page Power BI build guide.

Use this project to demonstrate energy operations analytics, project controls reporting, cost variance analysis, schedule analysis, and executive dashboard storytelling.

## Key Metrics

- AFE budget
- Actual cost
- Cost variance CAD
- Cost variance %
- Planned days
- Actual days
- Schedule variance
- Drilling days
- Non-productive time hours
- NPT %
- Rig utilization %
- Cost per meter
- Contractor performance
- HSE incident count
- Forecast final cost
- Forecast variance
- Risk flags

## Data Model

Raw input tables:

- `wells.csv`
- `drilling_jobs.csv`
- `daily_operations.csv`
- `cost_actuals.csv`
- `afe_budgets.csv`
- `contractors.csv`
- `rigs.csv`
- `hse_events.csv`
- `npt_events.csv`
- `calendar.csv`

Analytical output tables:

- `daily_project_metrics.csv`
- `well_performance_summary.csv`
- `contractor_performance.csv`
- `cost_variance_summary.csv`
- `npt_summary.csv`
- `hse_summary.csv`
- `executive_project_controls_summary.csv`

SQLite database:

- `data/drilling_project_controls.sqlite`

## Analytical Workflow

1. `notebooks/01_generate_synthetic_data.py`
   - Generates synthetic wells, jobs, rigs, contractors, AFE budgets, daily operations, actual costs, NPT events, HSE events, and calendar data.
   - Writes raw CSVs and a SQLite database.

2. `notebooks/02_analyze_project_controls.py`
   - Calculates daily project controls KPIs and summary outputs.
   - Writes analytical CSVs and analytical SQLite tables/views.

3. Power BI Desktop
   - Imports CSV files.
   - Builds relationships around calendar, wells, jobs, rigs, and contractors.
   - Creates DAX measures from `powerbi/dax_measures.md`.
   - Builds report pages using `powerbi/powerbi_build_guide.md`.

## Power BI Pages

1. Executive Summary
2. Budget vs Actual
3. Schedule & NPT
4. Rig / Contractor Performance
5. HSE & Operational Risk
6. Well Detail

## Synthetic Insights

The synthetic data is designed to surface realistic project controls patterns:

- Some wells run above AFE due to higher daily service costs and NPT.
- Contractor performance varies by cost variance, utilization, and HSE count.
- Forecast final cost changes as drilling progress increases.
- NPT and rig utilization explain a meaningful part of schedule variance.
- HSE indicators provide operational risk context next to cost and schedule KPIs.

## Business Recommendations

- Review wells with high forecast variance before total depth.
- Separate cost overruns caused by drilling progress from overruns caused by NPT.
- Use contractor scorecards to support service quality and commercial discussions.
- Escalate high-severity HSE events even if cost performance is acceptable.
- Monitor rig utilization and NPT daily, not only at well closeout.

## Skills Demonstrated

- Python synthetic data generation.
- pandas project controls analysis.
- SQLite schema and SQL query design.
- Cost and schedule variance reporting.
- NPT, rig utilization, contractor, and HSE analytics.
- Power BI model planning and DAX measure design.
- Executive dashboard communication for energy operations.

## How to Reproduce

From the repository root:

```powershell
python 02_drilling_project_controls/notebooks/01_generate_synthetic_data.py
python 02_drilling_project_controls/notebooks/02_analyze_project_controls.py
```

Then build the report manually using:

```text
02_drilling_project_controls/powerbi/powerbi_build_guide.md
```

## Limitations

- The data is synthetic and designed for portfolio demonstration.
- Forecast final cost is a simplified progress-based estimate.
- NPT categories and HSE severity are simplified.
- The Power BI `.pbix` must be built manually from the guide.

## Interview Talking Points

- I converted a drilling project controls problem into a complete analytics workflow.
- I modeled AFE budgets, actual costs, schedule progress, rig utilization, NPT, contractors, and HSE events.
- I calculated cost variance, schedule variance, forecast final cost, cost per meter, utilization, and operational risk flags.
- I prepared Power BI-ready outputs, DAX measures, and a dashboard build guide for executive reporting.
