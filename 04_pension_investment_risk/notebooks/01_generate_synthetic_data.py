from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DB_PATH = DATA_DIR / "pension_investment_risk.sqlite"
RNG = np.random.default_rng(1404)


def iso_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for column in columns:
        out[column] = pd.to_datetime(out[column]).dt.strftime("%Y-%m-%d")
    return out


def build_calendar() -> pd.DataFrame:
    dates = pd.bdate_range("2025-01-02", "2025-12-31")
    calendar = pd.DataFrame({"date": dates})
    calendar["year"] = calendar["date"].dt.year
    calendar["month"] = calendar["date"].dt.month
    calendar["quarter"] = calendar["date"].dt.quarter
    calendar["week"] = calendar["date"].dt.isocalendar().week.astype(int)
    calendar["is_month_end"] = calendar["date"].dt.is_month_end.astype(int)
    return iso_dates(calendar, ["date"])


def random_walk(start: float, n: int, daily_vol: float, drift: float = 0.0002) -> np.ndarray:
    shocks = RNG.normal(drift, daily_vol, n)
    return np.round(start * np.exp(np.cumsum(shocks)), 4)


def build_reference_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    portfolios = pd.DataFrame(
        [
            ("PF001", "Conservative Income", "Conservative", 0.035, "CAD"),
            ("PF002", "Balanced Growth", "Balanced", 0.055, "CAD"),
            ("PF003", "Growth Plus", "Growth", 0.070, "CAD"),
            ("PF004", "Retirement 2045", "Target Date", 0.060, "CAD"),
        ],
        columns=["portfolio_id", "portfolio_name", "risk_profile", "target_return_pct", "base_currency"],
    )
    assets = pd.DataFrame(
        [
            ("AC001", "Canadian Equity", "Equity", "CAD", "High"),
            ("AC002", "US Equity", "Equity", "USD", "High"),
            ("AC003", "Global Equity", "Equity", "USD", "High"),
            ("AC004", "Canadian Bonds", "Fixed Income", "CAD", "Low"),
            ("AC005", "Global Bonds", "Fixed Income", "USD", "Medium"),
            ("AC006", "Real Assets", "Alternatives", "CAD", "Medium"),
            ("AC007", "Cash", "Cash", "CAD", "Low"),
            ("AC008", "European Equity", "Equity", "EUR", "High"),
        ],
        columns=["asset_class_id", "asset_class_name", "asset_category", "currency", "risk_bucket"],
    )
    return portfolios, assets


def build_members(portfolios: pd.DataFrame) -> pd.DataFrame:
    rows = []
    member_id = 1
    for _, portfolio in portfolios.iterrows():
        for _ in range(30):
            age = int(RNG.integers(28, 62))
            rows.append(
                {
                    "member_id": f"MEM{member_id:05d}",
                    "portfolio_id": portfolio["portfolio_id"],
                    "age": age,
                    "retirement_age": int(RNG.choice([60, 65, 67], p=[0.18, 0.70, 0.12])),
                    "annual_salary_cad": round(float(np.clip(RNG.normal(78000, 22000), 42000, 165000)), 2),
                    "contribution_rate_pct": round(float(RNG.uniform(0.04, 0.11)), 4),
                }
            )
            member_id += 1
    return pd.DataFrame(rows)


def build_market_data(assets: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = pd.bdate_range("2025-01-02", "2025-12-31")
    starts = {
        "AC001": 100, "AC002": 115, "AC003": 108, "AC004": 98,
        "AC005": 101, "AC006": 95, "AC007": 100, "AC008": 104,
    }
    vols = {
        "AC001": 0.010, "AC002": 0.012, "AC003": 0.011, "AC004": 0.003,
        "AC005": 0.004, "AC006": 0.007, "AC007": 0.0001, "AC008": 0.012,
    }
    rows = []
    for asset_id in assets["asset_class_id"]:
        prices = random_walk(starts[asset_id], len(dates), vols[asset_id])
        for date, price in zip(dates, prices):
            rows.append({"date": date, "asset_class_id": asset_id, "price_local": price})
    fx = pd.DataFrame(
        {
            "date": dates,
            "usd_cad": random_walk(1.35, len(dates), 0.002, 0.00002),
            "eur_cad": random_walk(1.47, len(dates), 0.0022, 0.00001),
        }
    )
    return iso_dates(pd.DataFrame(rows), ["date"]), iso_dates(fx, ["date"])


def build_holdings_flows_benchmarks(
    portfolios: pd.DataFrame,
    assets: pd.DataFrame,
    members: pd.DataFrame,
    daily_prices: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    target_weights = {
        "Conservative": {"AC001": 0.15, "AC002": 0.10, "AC003": 0.08, "AC004": 0.42, "AC005": 0.15, "AC006": 0.05, "AC007": 0.05, "AC008": 0.00},
        "Balanced": {"AC001": 0.22, "AC002": 0.20, "AC003": 0.15, "AC004": 0.23, "AC005": 0.10, "AC006": 0.06, "AC007": 0.02, "AC008": 0.02},
        "Growth": {"AC001": 0.25, "AC002": 0.27, "AC003": 0.22, "AC004": 0.08, "AC005": 0.05, "AC006": 0.06, "AC007": 0.02, "AC008": 0.05},
        "Target Date": {"AC001": 0.22, "AC002": 0.22, "AC003": 0.18, "AC004": 0.18, "AC005": 0.08, "AC006": 0.06, "AC007": 0.03, "AC008": 0.03},
    }
    first_prices = daily_prices[daily_prices["date"] == daily_prices["date"].min()].set_index("asset_class_id")["price_local"].to_dict()
    holdings = []
    for _, portfolio in portfolios.iterrows():
        total_value = float(RNG.uniform(18_000_000, 42_000_000))
        weights = target_weights[portfolio["risk_profile"]]
        for asset_id, target in weights.items():
            if target == 0:
                continue
            drifted_weight = max(0.01, target + float(RNG.normal(0, 0.015)))
            value = total_value * drifted_weight
            units = value / first_prices[asset_id]
            holdings.append(
                {
                    "holding_id": f"HLD{len(holdings) + 1:05d}",
                    "portfolio_id": portfolio["portfolio_id"],
                    "asset_class_id": asset_id,
                    "as_of_date": "2025-01-02",
                    "units": round(float(units), 4),
                    "target_allocation_pct": target,
                }
            )

    months = pd.date_range("2025-01-31", "2025-12-31", freq="ME")
    contributions = []
    withdrawals = []
    for _, member in members.iterrows():
        monthly_contribution = member["annual_salary_cad"] * member["contribution_rate_pct"] / 12
        for month in months:
            contributions.append(
                {
                    "contribution_id": f"CONTR{len(contributions) + 1:06d}",
                    "date": month,
                    "member_id": member["member_id"],
                    "portfolio_id": member["portfolio_id"],
                    "contribution_cad": round(float(monthly_contribution * RNG.uniform(0.92, 1.08)), 2),
                }
            )
            if member["age"] >= 58 and RNG.random() < 0.18:
                withdrawals.append(
                    {
                        "withdrawal_id": f"WDR{len(withdrawals) + 1:06d}",
                        "date": month,
                        "member_id": member["member_id"],
                        "portfolio_id": member["portfolio_id"],
                        "withdrawal_cad": round(float(RNG.uniform(800, 3500)), 2),
                    }
                )

    dates = pd.bdate_range("2025-01-02", "2025-12-31")
    benchmarks = []
    for _, portfolio in portfolios.iterrows():
        vol = {"Conservative": 0.003, "Balanced": 0.006, "Growth": 0.009, "Target Date": 0.007}[portfolio["risk_profile"]]
        bench = RNG.normal(portfolio["target_return_pct"] / 252, vol, len(dates))
        for date, ret in zip(dates, bench):
            benchmarks.append(
                {
                    "date": date,
                    "portfolio_id": portfolio["portfolio_id"],
                    "benchmark_name": f"{portfolio['portfolio_name']} Benchmark",
                    "benchmark_return": round(float(ret), 6),
                }
            )
    return (
        pd.DataFrame(holdings),
        iso_dates(pd.DataFrame(contributions), ["date"]),
        iso_dates(pd.DataFrame(withdrawals), ["date"]),
        iso_dates(pd.DataFrame(benchmarks), ["date"]),
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
    portfolios, assets = build_reference_tables()
    members = build_members(portfolios)
    daily_prices, fx_rates = build_market_data(assets)
    holdings, contributions, withdrawals, benchmarks = build_holdings_flows_benchmarks(portfolios, assets, members, daily_prices)
    calendar = build_calendar()
    tables = {
        "portfolios": portfolios,
        "members": members,
        "asset_classes": assets,
        "holdings": holdings,
        "daily_prices": daily_prices,
        "fx_rates": fx_rates,
        "contributions": contributions,
        "withdrawals": withdrawals,
        "benchmarks": benchmarks,
        "calendar": calendar,
    }
    for name, df in tables.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
    write_sqlite(tables)
    print(f"Generated {len(tables)} raw tables in {DATA_DIR}")
    print(f"SQLite database created at {DB_PATH}")


if __name__ == "__main__":
    main()
