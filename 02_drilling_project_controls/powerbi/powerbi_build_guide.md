# Power BI Build Guide

Use this guide to build the Drilling Project Controls Dashboard manually in Power BI Desktop.

## 1. Generate Data

From the repository root:

```powershell
python 02_drilling_project_controls/notebooks/01_generate_synthetic_data.py
python 02_drilling_project_controls/notebooks/02_analyze_project_controls.py
```

## 2. Import Tables

Import these CSV files from `02_drilling_project_controls/data/`:

- `calendar.csv`
- `wells.csv`
- `drilling_jobs.csv`
- `daily_operations.csv`
- `cost_actuals.csv`
- `afe_budgets.csv`
- `contractors.csv`
- `rigs.csv`
- `hse_events.csv`
- `npt_events.csv`
- `daily_project_metrics.csv`
- `well_performance_summary.csv`
- `contractor_performance.csv`
- `cost_variance_summary.csv`
- `npt_summary.csv`
- `hse_summary.csv`
- `executive_project_controls_summary.csv`

## 3. Data Types

- Date: `calendar[date]`, `daily_project_metrics[date]`, event dates, cost dates, job start/end dates.
- Whole number: counts, planned days, elapsed days where appropriate.
- Decimal: costs, percentages, depth, hours, utilization, forecast values.
- Text: well, rig, contractor, region, phase, risk flag, category fields.

Mark `calendar[date]` as the date table.

## 4. Relationships

Create these relationships:

| From | To | Cardinality |
|---|---|---|
| `calendar[date]` | `daily_project_metrics[date]` | One-to-many |
| `calendar[date]` | `daily_operations[date]` | One-to-many |
| `calendar[date]` | `cost_actuals[date]` | One-to-many |
| `calendar[date]` | `hse_events[date]` | One-to-many |
| `calendar[date]` | `npt_events[date]` | One-to-many |
| `wells[well_id]` | `daily_project_metrics[well_id]` | One-to-many |
| `wells[well_id]` | `drilling_jobs[well_id]` | One-to-many |
| `wells[well_id]` | `well_performance_summary[well_id]` | One-to-one or one-to-many |
| `drilling_jobs[job_id]` | `daily_project_metrics[job_id]` | One-to-many |
| `contractors[contractor_id]` | `daily_project_metrics[contractor_id]` | One-to-many |
| `contractors[contractor_id]` | `contractor_performance[contractor_id]` | One-to-one or one-to-many |
| `rigs[rig_id]` | `daily_project_metrics[rig_id]` | One-to-many |

Use single-direction filtering.

## 5. Measures

Create a `Measures` table and copy the measures from `powerbi/dax_measures.md`.

## 6. Page Build

### Executive Summary

Visuals:

- KPI cards: `Forecast Final Cost CAD`, `Forecast Variance CAD`, `Cost Variance %`, `NPT Hours`, `Rig Utilization %`, `HSE Incident Count`, `High Risk Wells`.
- Bar chart: `Forecast Variance CAD` by `well_performance_summary[well_name]`.
- Line chart: `Daily Actual Cost CAD` by `calendar[date]`.
- Table: well name, risk flag, forecast variance, schedule variance, NPT hours.

### Budget vs Actual

Visuals:

- Clustered bar: AFE budget vs actual cost by well.
- Waterfall: forecast variance by well.
- Matrix: cost category from `cost_actuals[cost_category]` and actual cost.
- Slicers: basin, region, well type.

### Schedule & NPT

Visuals:

- Line chart: progress percent over time by well.
- Bar chart: NPT hours by well.
- Bar chart: schedule variance days by well.
- Table: NPT category, NPT hours, estimated cost impact.

### Rig / Contractor Performance

Visuals:

- Bar chart: rig utilization by rig.
- Table: contractor name, performance score, NPT hours, HSE incident count.
- Scatter: average rig utilization vs actual cost by contractor.
- Slicer: service line.

### HSE & Operational Risk

Visuals:

- KPI cards: HSE incident count, recordable count, lost time count.
- Bar chart: HSE incidents by severity.
- Table: HSE event type, severity, contractor, date.
- Matrix: risk flag by well and operation phase.

### Well Detail

Visuals:

- Slicer: well name.
- KPI cards: AFE budget, actual cost, forecast variance, progress percent, cost per meter, schedule variance.
- Line chart: cumulative actual cost and cumulative depth by date.
- Table: daily operation phase, depth drilled, NPT hours, cost, risk flag.

## 7. Conditional Formatting

- Cost variance % above 10 percent: amber.
- Cost variance % above 15 percent: red.
- Schedule variance above 3 days: amber.
- Schedule variance above 5 days: red.
- Risk flag High: red.
- Risk flag Medium: amber.
- Lost time count above 0: red.

## 8. Final Validation

- KPI totals reconcile to `executive_project_controls_summary.csv`.
- All six pages respond to well and date slicers.
- No visuals show unexpected blanks.
- High risk wells are visible in the Executive Summary and Well Detail pages.
