from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DB_PATH = DATA_DIR / "drilling_project_controls.sqlite"
RNG = np.random.default_rng(1202)


def iso_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for column in columns:
        out[column] = pd.to_datetime(out[column]).dt.strftime("%Y-%m-%d")
    return out


def build_calendar() -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", "2025-06-30", freq="D")
    calendar = pd.DataFrame({"date": dates})
    calendar["year"] = calendar["date"].dt.year
    calendar["month"] = calendar["date"].dt.month
    calendar["quarter"] = calendar["date"].dt.quarter
    calendar["week"] = calendar["date"].dt.isocalendar().week.astype(int)
    calendar["is_month_end"] = calendar["date"].dt.is_month_end.astype(int)
    return iso_dates(calendar, ["date"])


def build_reference_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    wells = pd.DataFrame(
        [
            ("WELL001", "Prairie Dawn 01", "Williston", "Saskatchewan", "Horizontal", 3450, "2025-01-05", "2025-02-15", "Complete"),
            ("WELL002", "Red River 02", "Williston", "Manitoba", "Horizontal", 3300, "2025-01-18", "2025-03-01", "Complete"),
            ("WELL003", "Foothills 03", "Deep Basin", "Alberta", "Directional", 4100, "2025-02-01", "2025-03-20", "Complete"),
            ("WELL004", "Clearwater 04", "Clearwater", "Alberta", "Horizontal", 2850, "2025-02-18", "2025-03-30", "Complete"),
            ("WELL005", "Prairie North 05", "Williston", "Saskatchewan", "Horizontal", 3600, "2025-03-10", "2025-04-25", "Complete"),
            ("WELL006", "Peace River 06", "Peace River", "Alberta", "Directional", 2950, "2025-04-01", "2025-05-10", "Complete"),
            ("WELL007", "Northern Lights 07", "Deep Basin", "Alberta", "Horizontal", 4300, "2025-04-20", "2025-06-05", "Complete"),
            ("WELL008", "Prairie West 08", "Williston", "Saskatchewan", "Horizontal", 3750, "2025-05-12", "2025-06-25", "Complete"),
        ],
        columns=["well_id", "well_name", "basin", "region", "well_type", "target_depth_m", "planned_start", "planned_end", "status"],
    )
    contractors = pd.DataFrame(
        [
            ("CON001", "Northstar Drilling Services", "Drilling", "Calgary", "A"),
            ("CON002", "Prairie Directional", "Directional", "Regina", "B"),
            ("CON003", "Redline Fluids", "Fluids", "Edmonton", "A"),
            ("CON004", "Summit Cementing", "Cementing", "Calgary", "B"),
            ("CON005", "FieldSafe Services", "HSE", "Winnipeg", "A"),
            ("CON006", "Ironhorse Rentals", "Equipment", "Estevan", "B"),
        ],
        columns=["contractor_id", "contractor_name", "service_line", "base_location", "safety_rating"],
    )
    rigs = pd.DataFrame(
        [
            ("RIG001", "Rig 12", "Triple", 1500, 54000),
            ("RIG002", "Rig 18", "Triple", 1600, 58000),
            ("RIG003", "Rig 23", "Double", 1200, 42000),
            ("RIG004", "Rig 31", "Triple", 1700, 61000),
            ("RIG005", "Rig 44", "Double", 1100, 39000),
        ],
        columns=["rig_id", "rig_name", "rig_type", "horsepower", "daily_rate_cad"],
    )
    return wells, contractors, rigs


def build_jobs_and_budgets(wells: pd.DataFrame, contractors: pd.DataFrame, rigs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    jobs = []
    budgets = []
    categories = ["Rig", "Directional", "Fluids", "Cementing", "Rentals", "HSE"]
    for i, well in wells.iterrows():
        planned_start = pd.Timestamp(well["planned_start"])
        planned_end = pd.Timestamp(well["planned_end"])
        planned_days = max((planned_end - planned_start).days + 1, 1)
        actual_start = planned_start + pd.Timedelta(days=int(RNG.integers(-1, 4)))
        actual_days = planned_days + int(RNG.integers(-3, 9))
        actual_end = actual_start + pd.Timedelta(days=actual_days - 1)
        rig = rigs.iloc[i % len(rigs)]
        contractor = contractors.iloc[i % len(contractors)]
        afe_id = f"AFE{i + 1:04d}"
        job_id = f"JOB{i + 1:04d}"
        jobs.append(
            {
                "job_id": job_id,
                "well_id": well["well_id"],
                "rig_id": rig["rig_id"],
                "contractor_id": contractor["contractor_id"],
                "afe_id": afe_id,
                "job_start": actual_start,
                "planned_spud_date": planned_start,
                "planned_total_depth_date": planned_end,
                "actual_spud_date": actual_start,
                "actual_total_depth_date": actual_end,
                "planned_depth_m": well["target_depth_m"],
            }
        )
        base_budget = well["target_depth_m"] * float(RNG.uniform(1050, 1550))
        weights = np.array([0.38, 0.16, 0.14, 0.10, 0.16, 0.06])
        weights = weights / weights.sum()
        for category, weight in zip(categories, weights):
            budgets.append(
                {
                    "afe_id": afe_id,
                    "well_id": well["well_id"],
                    "budget_category": category,
                    "budget_cad": round(base_budget * weight, 2),
                    "planned_days": planned_days,
                }
            )
    return iso_dates(pd.DataFrame(jobs), ["job_start", "planned_spud_date", "planned_total_depth_date", "actual_spud_date", "actual_total_depth_date"]), pd.DataFrame(budgets)


def build_operations_costs_events(
    wells: pd.DataFrame,
    jobs: pd.DataFrame,
    contractors: pd.DataFrame,
    rigs: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    operations = []
    costs = []
    npt_events = []
    hse_events = []
    cost_id = 1
    npt_id = 1
    hse_id = 1
    category_multipliers = {
        "Rig": 0.42,
        "Directional": 0.18,
        "Fluids": 0.14,
        "Cementing": 0.08,
        "Rentals": 0.12,
        "HSE": 0.06,
    }
    npt_categories = ["Mechanical", "Weather", "Logistics", "Directional", "Waiting on materials"]
    hse_types = ["First aid", "Near miss", "Spill", "Equipment damage", "Lost time incident"]

    well_lookup = wells.set_index("well_id")
    rig_lookup = rigs.set_index("rig_id")
    for _, job in jobs.iterrows():
        start = pd.Timestamp(job["actual_spud_date"])
        end = pd.Timestamp(job["actual_total_depth_date"])
        dates = pd.date_range(start, end, freq="D")
        target_depth = float(well_lookup.loc[job["well_id"], "target_depth_m"])
        daily_depth = RNG.gamma(shape=3.2, scale=target_depth / (len(dates) * 3.2), size=len(dates))
        daily_depth = daily_depth / daily_depth.sum() * target_depth
        cumulative = np.cumsum(daily_depth)
        rig_rate = float(rig_lookup.loc[job["rig_id"], "daily_rate_cad"])

        for day_index, (date, depth, cum_depth) in enumerate(zip(dates, daily_depth, cumulative), start=1):
            npt_hours = float(max(0, RNG.normal(2.2, 2.4)))
            if RNG.random() < 0.18:
                npt_hours += float(RNG.uniform(4, 10))
            maintenance_hours = float(max(0, RNG.normal(1.0, 0.8)))
            standby_hours = float(max(0, RNG.normal(0.8, 0.9)))
            productive_hours = max(0.0, 24.0 - npt_hours - maintenance_hours - standby_hours)
            phase = "Surface" if day_index <= 4 else "Intermediate" if cum_depth < target_depth * 0.72 else "Production"
            operations.append(
                {
                    "date": date,
                    "job_id": job["job_id"],
                    "well_id": job["well_id"],
                    "rig_id": job["rig_id"],
                    "operation_phase": phase,
                    "depth_drilled_m": round(float(depth), 2),
                    "cumulative_depth_m": round(float(cum_depth), 2),
                    "drilling_hours": round(productive_hours, 2),
                    "productive_hours": round(productive_hours, 2),
                    "standby_hours": round(standby_hours, 2),
                    "maintenance_hours": round(maintenance_hours, 2),
                    "rig_available_hours": 24.0,
                }
            )
            for category, multiplier in category_multipliers.items():
                contractor = contractors.sample(n=1, random_state=int(RNG.integers(1, 1_000_000))).iloc[0]
                base_cost = rig_rate * multiplier
                cost = base_cost * RNG.uniform(0.80, 1.35) + npt_hours * RNG.uniform(1500, 3500) * multiplier
                costs.append(
                    {
                        "cost_id": f"COST{cost_id:05d}",
                        "date": date,
                        "job_id": job["job_id"],
                        "contractor_id": contractor["contractor_id"],
                        "cost_category": category,
                        "actual_cost_cad": round(float(cost), 2),
                    }
                )
                cost_id += 1
            if npt_hours >= 3:
                contractor = contractors.sample(n=1, random_state=int(RNG.integers(1, 1_000_000))).iloc[0]
                npt_events.append(
                    {
                        "npt_event_id": f"NPT{npt_id:05d}",
                        "date": date,
                        "job_id": job["job_id"],
                        "contractor_id": contractor["contractor_id"],
                        "npt_category": str(RNG.choice(npt_categories)),
                        "npt_hours": round(npt_hours, 2),
                        "estimated_cost_impact_cad": round(float(npt_hours * RNG.uniform(5500, 9500)), 2),
                    }
                )
                npt_id += 1
            if RNG.random() < 0.055:
                contractor = contractors.sample(n=1, random_state=int(RNG.integers(1, 1_000_000))).iloc[0]
                event_type = str(RNG.choice(hse_types, p=[0.40, 0.30, 0.12, 0.12, 0.06]))
                severity = "High" if event_type == "Lost time incident" else str(RNG.choice(["Low", "Medium"], p=[0.65, 0.35]))
                hse_events.append(
                    {
                        "hse_event_id": f"HSE{hse_id:05d}",
                        "date": date,
                        "job_id": job["job_id"],
                        "contractor_id": contractor["contractor_id"],
                        "event_type": event_type,
                        "severity": severity,
                        "recordable": 1 if severity in {"Medium", "High"} else 0,
                        "lost_time": 1 if severity == "High" else 0,
                    }
                )
                hse_id += 1

    return (
        iso_dates(pd.DataFrame(operations), ["date"]),
        iso_dates(pd.DataFrame(costs), ["date"]),
        iso_dates(pd.DataFrame(npt_events), ["date"]),
        iso_dates(pd.DataFrame(hse_events), ["date"]),
    )


def write_sqlite(tables: dict[str, pd.DataFrame]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    schema_sql = (SQL_DIR / "schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema_sql)
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="append", index=False)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    wells, contractors, rigs = build_reference_tables()
    calendar = build_calendar()
    jobs, budgets = build_jobs_and_budgets(wells, contractors, rigs)
    operations, costs, npt_events, hse_events = build_operations_costs_events(wells, jobs, contractors, rigs)

    tables = {
        "wells": wells,
        "drilling_jobs": jobs,
        "daily_operations": operations,
        "cost_actuals": costs,
        "afe_budgets": budgets,
        "contractors": contractors,
        "rigs": rigs,
        "hse_events": hse_events,
        "npt_events": npt_events,
        "calendar": calendar,
    }
    for name, df in tables.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
    write_sqlite(tables)
    print(f"Generated {len(tables)} raw tables in {DATA_DIR}")
    print(f"SQLite database created at {DB_PATH}")


if __name__ == "__main__":
    main()
