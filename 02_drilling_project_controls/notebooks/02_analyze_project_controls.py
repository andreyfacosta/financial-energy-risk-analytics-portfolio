from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DB_PATH = DATA_DIR / "drilling_project_controls.sqlite"


def read_csv(name: str, date_cols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{name}.csv", parse_dates=date_cols or [])


def build_daily_metrics() -> pd.DataFrame:
    wells = read_csv("wells", ["planned_start", "planned_end"])
    jobs = read_csv("drilling_jobs", ["job_start", "planned_spud_date", "planned_total_depth_date", "actual_spud_date", "actual_total_depth_date"])
    operations = read_csv("daily_operations", ["date"])
    costs = read_csv("cost_actuals", ["date"])
    budgets = read_csv("afe_budgets")
    contractors = read_csv("contractors")
    rigs = read_csv("rigs")
    npt = read_csv("npt_events", ["date"])
    hse = read_csv("hse_events", ["date"])

    daily_cost = costs.groupby(["date", "job_id"], as_index=False).agg(actual_cost_cad=("actual_cost_cad", "sum"))
    daily_npt = npt.groupby(["date", "job_id"], as_index=False).agg(npt_hours=("npt_hours", "sum"), npt_cost_impact_cad=("estimated_cost_impact_cad", "sum"))
    daily_hse = hse.groupby(["date", "job_id"], as_index=False).agg(hse_incident_count=("hse_event_id", "count"), recordable_count=("recordable", "sum"), lost_time_count=("lost_time", "sum"))
    budget = budgets.groupby(["afe_id", "well_id"], as_index=False).agg(afe_budget_cad=("budget_cad", "sum"), planned_days=("planned_days", "max"))

    df = (
        operations.merge(daily_cost, on=["date", "job_id"], how="left")
        .merge(daily_npt, on=["date", "job_id"], how="left")
        .merge(daily_hse, on=["date", "job_id"], how="left")
        .merge(jobs, on=["job_id", "well_id", "rig_id"], how="left")
        .merge(wells[["well_id", "well_name", "basin", "region", "well_type", "target_depth_m"]], on="well_id", how="left")
        .merge(rigs[["rig_id", "rig_name", "rig_type", "daily_rate_cad"]], on="rig_id", how="left")
        .merge(contractors[["contractor_id", "contractor_name", "service_line", "safety_rating"]], on="contractor_id", how="left")
        .merge(budget, on=["afe_id", "well_id"], how="left")
    )
    for col in ["actual_cost_cad", "npt_hours", "npt_cost_impact_cad", "hse_incident_count", "recordable_count", "lost_time_count"]:
        df[col] = df[col].fillna(0)

    df = df.sort_values(["job_id", "date"])
    df["elapsed_days"] = df.groupby("job_id").cumcount() + 1
    df["cumulative_actual_cost_cad"] = df.groupby("job_id")["actual_cost_cad"].cumsum()
    df["cumulative_depth_m"] = df.groupby("job_id")["depth_drilled_m"].cumsum()
    df["progress_pct"] = np.minimum(df["cumulative_depth_m"] / df["target_depth_m"], 1.0)
    df["forecast_final_cost_cad"] = np.where(
        df["progress_pct"] >= 0.10,
        df["cumulative_actual_cost_cad"] / df["progress_pct"],
        df["afe_budget_cad"],
    )
    df["forecast_variance_cad"] = df["forecast_final_cost_cad"] - df["afe_budget_cad"]
    df["cost_variance_cad"] = df["cumulative_actual_cost_cad"] - (df["afe_budget_cad"] * df["progress_pct"])
    df["cost_variance_pct"] = np.where(df["afe_budget_cad"] > 0, df["forecast_variance_cad"] / df["afe_budget_cad"], 0)
    df["schedule_variance_days"] = df["elapsed_days"] - (df["planned_days"] * df["progress_pct"])
    df["rig_utilization_pct"] = np.where(df["rig_available_hours"] > 0, df["productive_hours"] / df["rig_available_hours"], 0)
    df["npt_pct"] = np.where(df["rig_available_hours"] > 0, df["npt_hours"] / df["rig_available_hours"], 0)
    df["cost_per_meter_cad"] = np.where(df["cumulative_depth_m"] > 0, df["cumulative_actual_cost_cad"] / df["cumulative_depth_m"], 0)
    df["drilling_days"] = df["elapsed_days"]
    conditions = [
        (df["cost_variance_pct"] > 0.15) | (df["schedule_variance_days"] > 5) | (df["lost_time_count"] > 0),
        (df["cost_variance_pct"] > 0.08) | (df["schedule_variance_days"] > 2) | (df["npt_pct"] > 0.25) | (df["recordable_count"] > 0),
    ]
    df["risk_flag"] = np.select(conditions, ["High", "Medium"], default="Normal")

    cols = [
        "date", "job_id", "well_id", "well_name", "basin", "region", "well_type", "rig_id", "rig_name",
        "contractor_id", "contractor_name", "operation_phase", "afe_budget_cad", "actual_cost_cad",
        "cumulative_actual_cost_cad", "cost_variance_cad", "cost_variance_pct", "planned_days",
        "elapsed_days", "schedule_variance_days", "drilling_days", "depth_drilled_m", "cumulative_depth_m",
        "target_depth_m", "progress_pct", "productive_hours", "rig_available_hours", "rig_utilization_pct",
        "npt_hours", "npt_pct", "npt_cost_impact_cad", "hse_incident_count", "recordable_count",
        "lost_time_count", "cost_per_meter_cad", "forecast_final_cost_cad", "forecast_variance_cad",
        "risk_flag",
    ]
    return df[cols].round(4)


def build_summaries(metrics: pd.DataFrame) -> dict[str, pd.DataFrame]:
    latest = metrics.sort_values(["well_id", "date"]).groupby("well_id").tail(1)
    well_summary = latest[[
        "well_id", "well_name", "basin", "region", "well_type", "contractor_id", "contractor_name", "rig_id",
        "rig_name", "afe_budget_cad", "cumulative_actual_cost_cad", "forecast_final_cost_cad",
        "forecast_variance_cad", "cost_variance_pct", "planned_days", "elapsed_days", "schedule_variance_days",
        "cumulative_depth_m", "target_depth_m", "cost_per_meter_cad", "risk_flag",
    ]].rename(columns={"cumulative_actual_cost_cad": "actual_cost_cad", "elapsed_days": "actual_days"})

    contractor = (
        metrics.groupby(["contractor_id", "contractor_name"], as_index=False)
        .agg(
            wells_supported=("well_id", "nunique"),
            actual_cost_cad=("actual_cost_cad", "sum"),
            npt_hours=("npt_hours", "sum"),
            avg_rig_utilization_pct=("rig_utilization_pct", "mean"),
            hse_incident_count=("hse_incident_count", "sum"),
            recordable_count=("recordable_count", "sum"),
            high_risk_days=("risk_flag", lambda s: int((s == "High").sum())),
        )
    )
    contractor["contractor_performance_score"] = (
        contractor["avg_rig_utilization_pct"] * 70
        - contractor["npt_hours"] / contractor["wells_supported"].clip(lower=1)
        - contractor["recordable_count"] * 5
    ).round(2)

    cost_variance = well_summary[[
        "well_id", "well_name", "afe_budget_cad", "actual_cost_cad", "forecast_final_cost_cad",
        "forecast_variance_cad", "cost_variance_pct", "risk_flag",
    ]].copy()
    npt_summary = (
        metrics.groupby(["well_id", "well_name"], as_index=False)
        .agg(npt_hours=("npt_hours", "sum"), npt_cost_impact_cad=("npt_cost_impact_cad", "sum"), drilling_days=("drilling_days", "max"))
    )
    npt_summary["npt_pct"] = np.where(npt_summary["drilling_days"] > 0, npt_summary["npt_hours"] / (npt_summary["drilling_days"] * 24), 0)
    hse_summary = (
        metrics.groupby(["well_id", "well_name"], as_index=False)
        .agg(hse_incident_count=("hse_incident_count", "sum"), recordable_count=("recordable_count", "sum"), lost_time_count=("lost_time_count", "sum"))
    )
    executive = pd.DataFrame(
        [
            ("AFE budget CAD", round(float(well_summary["afe_budget_cad"].sum()), 2), "Total approved budget"),
            ("Actual cost CAD", round(float(well_summary["actual_cost_cad"].sum()), 2), "Total actual cost to latest date"),
            ("Forecast final cost CAD", round(float(well_summary["forecast_final_cost_cad"].sum()), 2), "Progress-based forecast"),
            ("Forecast variance CAD", round(float(well_summary["forecast_variance_cad"].sum()), 2), "Forecast final cost minus AFE"),
            ("Average cost variance %", round(float(well_summary["cost_variance_pct"].mean()), 4), "Average well forecast variance percent"),
            ("Total NPT hours", round(float(npt_summary["npt_hours"].sum()), 2), "Non-productive time hours"),
            ("Average rig utilization %", round(float(metrics["rig_utilization_pct"].mean()), 4), "Productive hours divided by available hours"),
            ("HSE incident count", int(hse_summary["hse_incident_count"].sum()), "Total HSE events"),
            ("High risk wells", int((well_summary["risk_flag"] == "High").sum()), "Wells with high project control risk"),
        ],
        columns=["metric", "value", "notes"],
    )
    return {
        "well_performance_summary": well_summary.round(4),
        "contractor_performance": contractor.round(4),
        "cost_variance_summary": cost_variance.round(4),
        "npt_summary": npt_summary.round(4),
        "hse_summary": hse_summary.round(4),
        "executive_project_controls_summary": executive,
    }


def write_outputs_to_sqlite(tables: dict[str, pd.DataFrame]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        for name, df in tables.items():
            sqlite_df = df.copy()
            for column in sqlite_df.columns:
                if pd.api.types.is_datetime64_any_dtype(sqlite_df[column]):
                    sqlite_df[column] = sqlite_df[column].dt.strftime("%Y-%m-%d")
            sqlite_df.to_sql(name, conn, if_exists="replace", index=False)
        conn.executescript((SQL_DIR / "analytics_queries.sql").read_text(encoding="utf-8"))


def main() -> None:
    metrics = build_daily_metrics()
    outputs = {"daily_project_metrics": metrics}
    outputs.update(build_summaries(metrics))
    for name, df in outputs.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
    write_outputs_to_sqlite(outputs)
    print("Generated analytical outputs:")
    for name, df in outputs.items():
        print(f"- {name}.csv: {len(df)} rows")


if __name__ == "__main__":
    main()
