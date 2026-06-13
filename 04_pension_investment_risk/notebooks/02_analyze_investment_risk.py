from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DB_PATH = DATA_DIR / "pension_investment_risk.sqlite"


def read_csv(name: str, date_cols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{name}.csv", parse_dates=date_cols or [])


def build_position_values() -> pd.DataFrame:
    portfolios = read_csv("portfolios")
    assets = read_csv("asset_classes")
    holdings = read_csv("holdings", ["as_of_date"])
    prices = read_csv("daily_prices", ["date"])
    fx = read_csv("fx_rates", ["date"])
    df = holdings.merge(prices, on="asset_class_id", how="left").merge(assets, on="asset_class_id", how="left").merge(portfolios, on="portfolio_id", how="left").merge(fx, on="date", how="left")
    df["fx_to_cad"] = np.select(
        [df["currency"] == "USD", df["currency"] == "EUR"],
        [df["usd_cad"], df["eur_cad"]],
        default=1.0,
    )
    df["market_value_cad"] = df["units"] * df["price_local"] * df["fx_to_cad"]
    return df


def build_daily_returns(values: pd.DataFrame) -> pd.DataFrame:
    contributions = read_csv("contributions", ["date"]).groupby(["date", "portfolio_id"], as_index=False).agg(contribution_cad=("contribution_cad", "sum"))
    withdrawals = read_csv("withdrawals", ["date"]).groupby(["date", "portfolio_id"], as_index=False).agg(withdrawal_cad=("withdrawal_cad", "sum"))
    benchmarks = read_csv("benchmarks", ["date"])
    daily = (
        values.groupby(["date", "portfolio_id", "portfolio_name", "risk_profile"], as_index=False)
        .agg(portfolio_value_cad=("market_value_cad", "sum"))
        .sort_values(["portfolio_id", "date"])
        .merge(contributions, on=["date", "portfolio_id"], how="left")
        .merge(withdrawals, on=["date", "portfolio_id"], how="left")
        .merge(benchmarks, on=["date", "portfolio_id"], how="left")
    )
    daily[["contribution_cad", "withdrawal_cad"]] = daily[["contribution_cad", "withdrawal_cad"]].fillna(0)
    daily["net_flow_cad"] = daily["contribution_cad"] - daily["withdrawal_cad"]
    daily["prior_value_cad"] = daily.groupby("portfolio_id")["portfolio_value_cad"].shift(1)
    daily["daily_return"] = np.where(daily["prior_value_cad"] > 0, (daily["portfolio_value_cad"] - daily["prior_value_cad"] - daily["net_flow_cad"]) / daily["prior_value_cad"], 0)
    daily["cumulative_return"] = daily.groupby("portfolio_id")["daily_return"].transform(lambda s: (1 + s).cumprod() - 1)
    daily["benchmark_cumulative_return"] = daily.groupby("portfolio_id")["benchmark_return"].transform(lambda s: (1 + s).cumprod() - 1)
    daily["active_return"] = daily["daily_return"] - daily["benchmark_return"]
    return daily[[
        "date", "portfolio_id", "portfolio_name", "risk_profile", "portfolio_value_cad", "daily_return",
        "cumulative_return", "benchmark_return", "benchmark_cumulative_return", "active_return",
        "contribution_cad", "withdrawal_cad", "net_flow_cad",
    ]].round(6)


def build_outputs(values: pd.DataFrame, returns: pd.DataFrame) -> dict[str, pd.DataFrame]:
    latest_date = values["date"].max()
    latest_values = values[values["date"] == latest_date].copy()
    total_by_portfolio = latest_values.groupby("portfolio_id")["market_value_cad"].transform("sum")
    latest_values["allocation_pct"] = latest_values["market_value_cad"] / total_by_portfolio
    latest_values["allocation_drift_pct"] = latest_values["allocation_pct"] - latest_values["target_allocation_pct"]
    latest_values["fx_exposure_cad"] = np.where(latest_values["currency"] == "CAD", 0, latest_values["market_value_cad"])
    latest_values["risk_flag"] = np.select(
        [latest_values["allocation_drift_pct"].abs() > 0.05, latest_values["allocation_drift_pct"].abs() > 0.03],
        ["High drift", "Watch"],
        default="Within range",
    )
    allocation = latest_values[[
        "date", "portfolio_id", "portfolio_name", "risk_profile", "asset_class_id", "asset_class_name",
        "asset_category", "currency", "market_value_cad", "allocation_pct", "target_allocation_pct",
        "allocation_drift_pct", "fx_exposure_cad", "risk_flag",
    ]].rename(columns={"date": "as_of_date"})

    drawdowns = []
    volatility_rows = []
    for portfolio_id, group in returns.groupby("portfolio_id"):
        group = group.sort_values("date")
        peak = group["portfolio_value_cad"].cummax()
        drawdown = group["portfolio_value_cad"] / peak - 1
        latest = group.iloc[-1]
        drawdowns.append(
            {
                "portfolio_id": portfolio_id,
                "portfolio_name": latest["portfolio_name"],
                "risk_profile": latest["risk_profile"],
                "max_drawdown_pct": round(float(drawdown.min()), 6),
                "current_drawdown_pct": round(float(drawdown.iloc[-1]), 6),
                "peak_value_cad": round(float(peak.max()), 2),
                "trough_value_cad": round(float(group.loc[drawdown.idxmin(), "portfolio_value_cad"]), 2),
                "latest_value_cad": round(float(latest["portfolio_value_cad"]), 2),
            }
        )
        vol_30d = group["daily_return"].tail(30).std()
        ann_vol = group["daily_return"].std() * np.sqrt(252)
        volatility_rows.append(
            {
                "portfolio_id": portfolio_id,
                "portfolio_name": latest["portfolio_name"],
                "risk_profile": latest["risk_profile"],
                "volatility_30d_pct": round(float(vol_30d), 6),
                "annualized_volatility_pct": round(float(ann_vol), 6),
                "risk_flag": "High volatility" if ann_vol > 0.16 else "Watch" if ann_vol > 0.10 else "Normal",
            }
        )

    fx = (
        latest_values.groupby(["portfolio_id", "portfolio_name", "currency"], as_index=False)
        .agg(fx_exposure_cad=("fx_exposure_cad", "sum"), portfolio_value_cad=("market_value_cad", "sum"))
    )
    total_portfolio = latest_values.groupby("portfolio_id")["market_value_cad"].sum().to_dict()
    fx["fx_exposure_pct"] = fx.apply(lambda r: r["fx_exposure_cad"] / total_portfolio[r["portfolio_id"]], axis=1)

    contributions = read_csv("contributions", ["date"])
    members = read_csv("members")
    annual_contrib = contributions.groupby("portfolio_id", as_index=False).agg(annual_contribution_cad=("contribution_cad", "sum"))
    latest_portfolio = returns.sort_values("date").groupby("portfolio_id").tail(1)
    member_age = members.groupby("portfolio_id", as_index=False).agg(avg_age=("age", "mean"), avg_retirement_age=("retirement_age", "mean"))
    projection = latest_portfolio.merge(annual_contrib, on="portfolio_id", how="left").merge(member_age, on="portfolio_id", how="left")
    projection["years_to_retirement"] = (projection["avg_retirement_age"] - projection["avg_age"]).clip(lower=1)
    projection["assumed_return_pct"] = np.select(
        [projection["risk_profile"] == "Conservative", projection["risk_profile"] == "Balanced", projection["risk_profile"] == "Growth"],
        [0.035, 0.055, 0.070],
        default=0.060,
    )
    projection["projected_retirement_value_cad"] = projection["portfolio_value_cad"] * (1 + projection["assumed_return_pct"]) ** projection["years_to_retirement"] + projection["annual_contribution_cad"] * (((1 + projection["assumed_return_pct"]) ** projection["years_to_retirement"] - 1) / projection["assumed_return_pct"])
    contribution_projection = projection[[
        "portfolio_id", "portfolio_name", "risk_profile", "portfolio_value_cad", "annual_contribution_cad",
        "avg_age", "avg_retirement_age", "years_to_retirement", "assumed_return_pct",
        "projected_retirement_value_cad",
    ]]

    scenarios = []
    scenario_defs = [
        ("Equity drawdown 15pct", {"Equity": -0.15, "Fixed Income": 0.02, "Alternatives": -0.05, "Cash": 0.00}),
        ("Rates up 100 bps", {"Equity": -0.03, "Fixed Income": -0.06, "Alternatives": -0.02, "Cash": 0.00}),
        ("CAD strengthens 5pct", {"USD": -0.05, "EUR": -0.05, "CAD": 0.00}),
        ("Balanced recovery 8pct", {"Equity": 0.08, "Fixed Income": 0.03, "Alternatives": 0.04, "Cash": 0.00}),
    ]
    for scenario, shocks in scenario_defs:
        for _, row in latest_values.iterrows():
            if "USD" in shocks:
                shock = shocks[row["currency"]]
            else:
                shock = shocks[row["asset_category"]]
            scenarios.append(
                {
                    "as_of_date": latest_date,
                    "scenario": scenario,
                    "portfolio_id": row["portfolio_id"],
                    "portfolio_name": row["portfolio_name"],
                    "asset_class_id": row["asset_class_id"],
                    "asset_class_name": row["asset_class_name"],
                    "shock_pct": shock,
                    "stress_impact_cad": round(float(row["market_value_cad"] * shock), 2),
                }
            )

    executive = pd.DataFrame(
        [
            ("Portfolio value CAD", round(float(returns.groupby("portfolio_id").tail(1)["portfolio_value_cad"].sum()), 2), "Latest total portfolio value"),
            ("Average cumulative return", round(float(returns.groupby("portfolio_id").tail(1)["cumulative_return"].mean()), 6), "Average latest cumulative return"),
            ("Average active return", round(float(returns.groupby("portfolio_id").tail(1)["active_return"].mean()), 6), "Average latest daily active return"),
            ("Max drawdown", round(float(pd.DataFrame(drawdowns)["max_drawdown_pct"].min()), 6), "Worst max drawdown across portfolios"),
            ("Average annualized volatility", round(float(pd.DataFrame(volatility_rows)["annualized_volatility_pct"].mean()), 6), "Average annualized volatility"),
            ("FX exposure CAD", round(float(fx["fx_exposure_cad"].sum()), 2), "Non-CAD exposure"),
            ("Annual contribution CAD", round(float(annual_contrib["annual_contribution_cad"].sum()), 2), "Synthetic annual contribution flow"),
            ("Allocation drift flags", int((allocation["risk_flag"] != "Within range").sum()), "Asset classes outside drift tolerance"),
        ],
        columns=["metric", "value", "notes"],
    )
    return {
        "allocation_summary": allocation.round(6),
        "drawdown_summary": pd.DataFrame(drawdowns),
        "volatility_summary": pd.DataFrame(volatility_rows),
        "fx_exposure_summary": fx.round(6),
        "contribution_projection": contribution_projection.round(4),
        "scenario_results": pd.DataFrame(scenarios),
        "executive_investment_summary": executive,
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
    values = build_position_values()
    returns = build_daily_returns(values)
    outputs = {"portfolio_daily_returns": returns}
    outputs.update(build_outputs(values, returns))
    for name, df in outputs.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
    write_outputs_to_sqlite(outputs)
    print("Generated analytical outputs:")
    for name, df in outputs.items():
        print(f"- {name}.csv: {len(df)} rows")


if __name__ == "__main__":
    main()
