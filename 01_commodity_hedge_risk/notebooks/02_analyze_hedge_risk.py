from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DB_PATH = DATA_DIR / "commodity_hedge_risk.sqlite"


def read_csv(name: str, date_cols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{name}.csv", parse_dates=date_cols or [])


def front_month_futures(futures_prices: pd.DataFrame, fx_rates: pd.DataFrame) -> pd.DataFrame:
    futures = futures_prices.copy()
    futures["contract_month_end"] = pd.to_datetime(futures["contract_month"] + "-01") + pd.offsets.MonthEnd(0)
    futures = futures[futures["contract_month_end"] >= futures["date"]]
    futures = futures.sort_values(["date", "commodity_id", "contract_month_end"])
    front = futures.drop_duplicates(["date", "commodity_id"], keep="first")
    front = front.merge(fx_rates, on="date", how="left")
    front["futures_price_cad_mt"] = front["futures_price_usd_mt"] * front["usd_cad"]
    return front[["date", "commodity_id", "contract_month", "futures_price_usd_mt", "usd_cad", "futures_price_cad_mt"]]


def active_physical_by_day(physical: pd.DataFrame, dates: pd.Series) -> pd.DataFrame:
    rows = []
    for date in dates:
        active = physical[(physical["trade_date"] <= date) & (physical["delivery_end"] >= date)].copy()
        if active.empty:
            continue
        active["signed_quantity_mt"] = np.where(active["buy_sell"] == "Buy", active["quantity_mt"], -active["quantity_mt"])
        grouped = (
            active.groupby(["commodity_id", "region"], as_index=False)
            .agg(
                physical_quantity_mt=("signed_quantity_mt", "sum"),
                physical_abs_quantity_mt=("quantity_mt", "sum"),
                physical_transaction_count=("transaction_id", "count"),
            )
        )
        grouped["date"] = date
        rows.append(grouped)
    if not rows:
        return pd.DataFrame(columns=["date", "commodity_id", "region", "physical_quantity_mt", "physical_abs_quantity_mt", "physical_transaction_count"])
    return pd.concat(rows, ignore_index=True)


def active_futures_by_day(futures: pd.DataFrame, dates: pd.Series) -> pd.DataFrame:
    rows = []
    futures = futures.copy()
    futures["contract_month_end"] = pd.to_datetime(futures["contract_month"] + "-01") + pd.offsets.MonthEnd(0)
    futures["signed_quantity_mt"] = np.where(
        futures["buy_sell"] == "Buy",
        futures["contracts"] * futures["contract_size_mt"],
        -futures["contracts"] * futures["contract_size_mt"],
    )
    futures["abs_contracts"] = futures["contracts"].abs()

    for date in dates:
        active = futures[(futures["trade_date"] <= date) & (futures["contract_month_end"] >= date)].copy()
        if active.empty:
            continue
        grouped = (
            active.groupby(["commodity_id"], as_index=False)
            .agg(
                futures_quantity_mt=("signed_quantity_mt", "sum"),
                active_contracts=("abs_contracts", "sum"),
                futures_position_count=("position_id", "count"),
            )
        )
        grouped["date"] = date
        rows.append(grouped)
    if not rows:
        return pd.DataFrame(columns=["date", "commodity_id", "futures_quantity_mt", "active_contracts", "futures_position_count"])
    return pd.concat(rows, ignore_index=True)


def build_daily_metrics() -> pd.DataFrame:
    commodities = read_csv("commodities")
    physical = read_csv("physical_transactions", ["trade_date", "delivery_start", "delivery_end"])
    futures = read_csv("futures_positions", ["trade_date"])
    cash = read_csv("daily_cash_prices", ["date"])
    futures_prices = read_csv("daily_futures_prices", ["date"])
    fx_rates = read_csv("fx_rates", ["date"])
    margin = read_csv("margin_requirements", ["date"])

    dates = fx_rates["date"].sort_values().drop_duplicates()
    front = front_month_futures(futures_prices, fx_rates)
    cash_avg = (
        cash.groupby(["date", "commodity_id"], as_index=False)
        .agg(avg_cash_price_cad_mt=("cash_price_cad_mt", "mean"))
    )

    physical_daily = active_physical_by_day(physical, dates)
    physical_by_commodity = (
        physical_daily.groupby(["date", "commodity_id"], as_index=False)
        .agg(
            physical_quantity_mt=("physical_quantity_mt", "sum"),
            physical_abs_quantity_mt=("physical_abs_quantity_mt", "sum"),
            physical_transaction_count=("physical_transaction_count", "sum"),
        )
    )
    futures_daily = active_futures_by_day(futures, dates)

    base = (
        front.merge(cash_avg, on=["date", "commodity_id"], how="left")
        .merge(physical_by_commodity, on=["date", "commodity_id"], how="left")
        .merge(futures_daily, on=["date", "commodity_id"], how="left")
        .merge(commodities[["commodity_id", "commodity_name"]], on="commodity_id", how="left")
    )

    fill_cols = [
        "physical_quantity_mt",
        "physical_abs_quantity_mt",
        "physical_transaction_count",
        "futures_quantity_mt",
        "active_contracts",
        "futures_position_count",
    ]
    base[fill_cols] = base[fill_cols].fillna(0)

    margin_latest = margin.groupby(["date", "commodity_id"], as_index=False).agg(
        initial_margin_usd_per_contract=("initial_margin_usd_per_contract", "mean")
    )
    base = base.merge(margin_latest, on=["date", "commodity_id"], how="left")

    base["physical_exposure_cad"] = base["physical_quantity_mt"] * base["avg_cash_price_cad_mt"]
    base["futures_exposure_cad"] = base["futures_quantity_mt"] * base["futures_price_cad_mt"]
    base["net_open_quantity_mt"] = base["physical_quantity_mt"] + base["futures_quantity_mt"]
    base["net_open_exposure_cad"] = base["physical_exposure_cad"] + base["futures_exposure_cad"]
    base["hedge_ratio"] = np.where(
        base["physical_quantity_mt"].abs() > 0,
        base["futures_quantity_mt"].abs() / base["physical_quantity_mt"].abs(),
        0,
    )
    base["basis_cad_mt"] = base["avg_cash_price_cad_mt"] - base["futures_price_cad_mt"]
    base["margin_requirement_cad"] = base["active_contracts"] * base["initial_margin_usd_per_contract"] * base["usd_cad"]

    base = base.sort_values(["commodity_id", "date"])
    base["cash_change_cad_mt"] = base.groupby("commodity_id")["avg_cash_price_cad_mt"].diff().fillna(0)
    base["futures_change_cad_mt"] = base.groupby("commodity_id")["futures_price_cad_mt"].diff().fillna(0)
    base["prior_physical_quantity_mt"] = base.groupby("commodity_id")["physical_quantity_mt"].shift(1).fillna(0)
    base["prior_futures_quantity_mt"] = base.groupby("commodity_id")["futures_quantity_mt"].shift(1).fillna(0)
    base["physical_pnl_cad"] = base["prior_physical_quantity_mt"] * base["cash_change_cad_mt"]
    base["futures_pnl_cad"] = base["prior_futures_quantity_mt"] * base["futures_change_cad_mt"]
    base["daily_pnl_cad"] = base["physical_pnl_cad"] + base["futures_pnl_cad"]
    base["cumulative_pnl_cad"] = base.groupby("commodity_id")["daily_pnl_cad"].cumsum()

    base["basis_risk_cad"] = (
        base.groupby("commodity_id")["basis_cad_mt"]
        .rolling(20, min_periods=5)
        .std()
        .reset_index(level=0, drop=True)
        .fillna(0)
        * base["physical_quantity_mt"].abs()
    )
    pnl_vol = (
        base.groupby("commodity_id")["daily_pnl_cad"]
        .rolling(20, min_periods=5)
        .std()
        .reset_index(level=0, drop=True)
        .fillna(0)
    )
    base["var_95_cad"] = 1.65 * pnl_vol
    base["var_99_cad"] = 2.33 * pnl_vol
    base["stress_down_5pct_cad"] = base["physical_exposure_cad"] * -0.04 + base["futures_exposure_cad"] * -0.05
    base["stress_up_5pct_cad"] = base["physical_exposure_cad"] * 0.04 + base["futures_exposure_cad"] * 0.05

    output_cols = [
        "date",
        "commodity_id",
        "commodity_name",
        "contract_month",
        "avg_cash_price_cad_mt",
        "futures_price_cad_mt",
        "usd_cad",
        "basis_cad_mt",
        "physical_quantity_mt",
        "futures_quantity_mt",
        "net_open_quantity_mt",
        "physical_exposure_cad",
        "futures_exposure_cad",
        "net_open_exposure_cad",
        "hedge_ratio",
        "daily_pnl_cad",
        "cumulative_pnl_cad",
        "basis_risk_cad",
        "margin_requirement_cad",
        "var_95_cad",
        "var_99_cad",
        "stress_down_5pct_cad",
        "stress_up_5pct_cad",
        "physical_transaction_count",
        "futures_position_count",
    ]
    return base[output_cols].round(2)


def build_risk_flags(metrics: pd.DataFrame) -> pd.DataFrame:
    flags = []
    for row in metrics.itertuples(index=False):
        checks = [
            (
                row.hedge_ratio < 0.75 and abs(row.physical_quantity_mt) > 0,
                "Hedge ratio below target",
                row.hedge_ratio,
                ">= 0.75",
                "Medium",
                "Open physical exposure is under-hedged.",
            ),
            (
                row.hedge_ratio > 1.25 and abs(row.physical_quantity_mt) > 0,
                "Hedge ratio above target",
                row.hedge_ratio,
                "<= 1.25",
                "Medium",
                "Futures quantity is high relative to physical exposure.",
            ),
            (
                abs(row.net_open_exposure_cad) > 1_500_000,
                "Large net open exposure",
                row.net_open_exposure_cad,
                "abs <= 1,500,000",
                "High",
                "Residual price exposure needs review.",
            ),
            (
                row.basis_risk_cad > 500_000,
                "High basis risk",
                row.basis_risk_cad,
                "<= 500,000",
                "High",
                "Basis volatility is material against open physical quantity.",
            ),
            (
                row.margin_requirement_cad > 1_000_000,
                "High margin requirement",
                row.margin_requirement_cad,
                "<= 1,000,000",
                "Medium",
                "Collateral requirement is elevated.",
            ),
            (
                row.daily_pnl_cad < -500_000,
                "Large daily loss",
                row.daily_pnl_cad,
                ">= -500,000",
                "High",
                "Daily mark-to-market loss exceeded tolerance.",
            ),
            (
                row.var_99_cad > 750_000,
                "High VaR approximation",
                row.var_99_cad,
                "<= 750,000",
                "High",
                "Recent P&L volatility suggests higher downside risk.",
            ),
        ]
        for triggered, metric, value, threshold, severity, explanation in checks:
            if triggered:
                flags.append(
                    {
                        "date": row.date,
                        "commodity_id": row.commodity_id,
                        "commodity_name": row.commodity_name,
                        "metric": metric,
                        "value": round(float(value), 2),
                        "threshold": threshold,
                        "severity": severity,
                        "explanation": explanation,
                    }
                )
    return pd.DataFrame(flags)


def build_counterparty_exposure(metrics: pd.DataFrame) -> pd.DataFrame:
    physical = read_csv("physical_transactions", ["trade_date", "delivery_start", "delivery_end"])
    counterparties = read_csv("counterparties")
    cash = read_csv("daily_cash_prices", ["date"])

    latest_date = metrics["date"].max()
    active = physical[(physical["trade_date"] <= latest_date) & (physical["delivery_end"] >= latest_date)].copy()
    active["signed_quantity_mt"] = np.where(active["buy_sell"] == "Buy", active["quantity_mt"], -active["quantity_mt"])

    latest_cash = cash[cash["date"] == latest_date][["commodity_id", "region", "cash_price_cad_mt"]].rename(
        columns={"cash_price_cad_mt": "latest_cash_price_cad_mt"}
    )
    active = active.merge(latest_cash, on=["commodity_id", "region"], how="left")
    active["latest_cash_price_cad_mt"] = active["latest_cash_price_cad_mt"].fillna(active["cash_price_cad_mt"])
    active["exposure_cad"] = active["signed_quantity_mt"] * active["latest_cash_price_cad_mt"]

    exposure = (
        active.groupby(["counterparty_id"], as_index=False)
        .agg(
            exposure_cad=("exposure_cad", "sum"),
            gross_quantity_mt=("quantity_mt", "sum"),
            open_transactions=("transaction_id", "count"),
        )
        .merge(counterparties, on="counterparty_id", how="left")
    )
    exposure["exposure_cad"] = exposure["exposure_cad"].abs()
    exposure["credit_utilization_pct"] = np.where(
        exposure["credit_limit_cad"] > 0,
        exposure["exposure_cad"] / exposure["credit_limit_cad"],
        0,
    )
    exposure["risk_flag"] = np.select(
        [
            exposure["credit_utilization_pct"] >= 0.90,
            exposure["credit_utilization_pct"] >= 0.70,
        ],
        ["Limit pressure", "Watch list"],
        default="Within limit",
    )
    cols = [
        "counterparty_id",
        "counterparty_name",
        "counterparty_type",
        "region",
        "credit_rating",
        "credit_limit_cad",
        "exposure_cad",
        "credit_utilization_pct",
        "gross_quantity_mt",
        "open_transactions",
        "risk_flag",
    ]
    return exposure[cols].sort_values("exposure_cad", ascending=False).round(2)


def build_stress_tests(metrics: pd.DataFrame) -> pd.DataFrame:
    latest = metrics[metrics["date"] == metrics["date"].max()].copy()
    scenarios = [
        ("Bearish commodity shock", -0.04, -0.05, 0.00, 0.00),
        ("Bullish commodity shock", 0.04, 0.05, 0.00, 0.00),
        ("Basis widens CAD 15/mt", 0.00, 0.00, 15.00, 0.00),
        ("Basis narrows CAD 15/mt", 0.00, 0.00, -15.00, 0.00),
        ("CAD weakens 5pct", 0.00, 0.05, 0.00, 0.05),
    ]
    rows = []
    for scenario, cash_shock, futures_shock, basis_shift, fx_shock in scenarios:
        stressed = latest.copy()
        cash_impact = stressed["physical_quantity_mt"] * stressed["avg_cash_price_cad_mt"] * cash_shock
        futures_impact = stressed["futures_quantity_mt"] * stressed["futures_price_cad_mt"] * (futures_shock + fx_shock)
        basis_impact = stressed["physical_quantity_mt"] * basis_shift
        stressed["stress_impact_cad"] = cash_impact + futures_impact + basis_impact
        for row in stressed.itertuples(index=False):
            rows.append(
                {
                    "as_of_date": row.date,
                    "scenario": scenario,
                    "commodity_id": row.commodity_id,
                    "commodity_name": row.commodity_name,
                    "cash_shock_pct": cash_shock,
                    "futures_shock_pct": futures_shock,
                    "basis_shift_cad_mt": basis_shift,
                    "fx_shock_pct": fx_shock,
                    "stress_impact_cad": round(float(row.stress_impact_cad), 2),
                }
            )
    return pd.DataFrame(rows)


def build_summary(metrics: pd.DataFrame, flags: pd.DataFrame, counterparty: pd.DataFrame) -> pd.DataFrame:
    latest = metrics[metrics["date"] == metrics["date"].max()]
    summary = [
        ("As of date", str(latest["date"].max().date()), "Latest available market date"),
        ("Physical exposure CAD", round(float(latest["physical_exposure_cad"].sum()), 2), "Signed physical exposure"),
        ("Futures exposure CAD", round(float(latest["futures_exposure_cad"].sum()), 2), "Signed hedge exposure"),
        ("Net open exposure CAD", round(float(latest["net_open_exposure_cad"].sum()), 2), "Physical plus futures exposure"),
        ("Weighted hedge ratio", round(float(latest["futures_quantity_mt"].abs().sum() / max(latest["physical_quantity_mt"].abs().sum(), 1)), 4), "Abs futures quantity / abs physical quantity"),
        ("Daily P&L CAD", round(float(latest["daily_pnl_cad"].sum()), 2), "Latest daily mark-to-market approximation"),
        ("Cumulative P&L CAD", round(float(latest["cumulative_pnl_cad"].sum()), 2), "Cumulative project-period P&L approximation"),
        ("Margin requirement CAD", round(float(latest["margin_requirement_cad"].sum()), 2), "Estimated active futures initial margin"),
        ("VaR 95 CAD", round(float(latest["var_95_cad"].sum()), 2), "Approximate 95pct VaR from rolling P&L volatility"),
        ("VaR 99 CAD", round(float(latest["var_99_cad"].sum()), 2), "Approximate 99pct VaR from rolling P&L volatility"),
        ("Open risk flags", int(len(flags[flags["date"] == latest["date"].max()])), "Risk flags on latest date"),
        ("Highest counterparty utilization", round(float(counterparty["credit_utilization_pct"].max()), 4), "Max exposure / credit limit"),
    ]
    return pd.DataFrame(summary, columns=["metric", "value", "notes"])


def write_outputs_to_sqlite(tables: dict[str, pd.DataFrame]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        for name, df in tables.items():
            sqlite_df = df.copy()
            for column in sqlite_df.columns:
                if pd.api.types.is_datetime64_any_dtype(sqlite_df[column]):
                    sqlite_df[column] = sqlite_df[column].dt.strftime("%Y-%m-%d")
            sqlite_df.to_sql(name, conn, if_exists="replace", index=False)

        analytics_sql = (SQL_DIR / "analytics_queries.sql").read_text(encoding="utf-8")
        conn.executescript(analytics_sql)


def main() -> None:
    metrics = build_daily_metrics()
    flags = build_risk_flags(metrics)
    counterparty = build_counterparty_exposure(metrics)
    stress_tests = build_stress_tests(metrics)
    summary = build_summary(metrics, flags, counterparty)

    metrics.to_csv(DATA_DIR / "daily_risk_metrics.csv", index=False)
    flags.to_csv(DATA_DIR / "risk_flags.csv", index=False)
    counterparty.to_csv(DATA_DIR / "counterparty_exposure.csv", index=False)
    stress_tests.to_csv(DATA_DIR / "stress_test_results.csv", index=False)
    summary.to_csv(DATA_DIR / "risk_summary.csv", index=False)
    write_outputs_to_sqlite(
        {
            "daily_risk_metrics": metrics,
            "risk_flags": flags,
            "counterparty_exposure": counterparty,
            "stress_test_results": stress_tests,
            "risk_summary": summary,
        }
    )

    print("Generated analytical outputs:")
    for file_name in [
        "daily_risk_metrics.csv",
        "risk_flags.csv",
        "counterparty_exposure.csv",
        "stress_test_results.csv",
        "risk_summary.csv",
    ]:
        path = DATA_DIR / file_name
        print(f"- {path.name}: {pd.read_csv(path).shape[0]} rows")


if __name__ == "__main__":
    main()
