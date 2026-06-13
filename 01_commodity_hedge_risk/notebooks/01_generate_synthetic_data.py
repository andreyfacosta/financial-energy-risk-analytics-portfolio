from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DB_PATH = DATA_DIR / "commodity_hedge_risk.sqlite"

RNG = np.random.default_rng(42)


def iso_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for column in columns:
        out[column] = pd.to_datetime(out[column]).dt.strftime("%Y-%m-%d")
    return out


def build_reference_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    commodities = pd.DataFrame(
        [
            ("WHEAT", "Spring Wheat", "MGEX Wheat", 136.08, "USD"),
            ("CANOLA", "Canola", "ICE Canola", 20.00, "CAD"),
            ("CORN", "Corn", "CBOT Corn", 127.01, "USD"),
            ("SOY", "Soybeans", "CBOT Soybeans", 136.08, "USD"),
            ("BARLEY", "Feed Barley", "Synthetic Barley", 100.00, "CAD"),
        ],
        columns=[
            "commodity_id",
            "commodity_name",
            "benchmark_contract",
            "contract_size_mt",
            "currency",
        ],
    )

    counterparties = pd.DataFrame(
        [
            ("CP001", "Prairie Elevators Ltd", "Producer Network", "Manitoba", "A", 4_500_000),
            ("CP002", "Northern Milling Co", "Processor", "Ontario", "BBB", 3_250_000),
            ("CP003", "Pacific Export Terminal", "Exporter", "British Columbia", "A", 6_000_000),
            ("CP004", "SaskAgri Trading", "Merchant", "Saskatchewan", "BBB", 3_800_000),
            ("CP005", "Lakehead Grain Buyers", "Processor", "Ontario", "BB", 2_200_000),
            ("CP006", "Red River Feed Group", "Feedlot", "Manitoba", "BBB", 2_800_000),
            ("CP007", "Alberta BioProducts", "Processor", "Alberta", "A", 5_200_000),
            ("CP008", "Great Lakes Exporters", "Exporter", "Ontario", "BBB", 4_100_000),
            ("CP009", "Vancouver Crush Partners", "Processor", "British Columbia", "A", 5_600_000),
            ("CP010", "Central Prairie Farms", "Producer Network", "Saskatchewan", "BB", 2_000_000),
        ],
        columns=[
            "counterparty_id",
            "counterparty_name",
            "counterparty_type",
            "region",
            "credit_rating",
            "credit_limit_cad",
        ],
    )

    return commodities, counterparties


def build_calendar() -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", "2025-06-30", freq="D")
    calendar = pd.DataFrame({"date": dates})
    calendar["year"] = calendar["date"].dt.year
    calendar["month"] = calendar["date"].dt.month
    calendar["quarter"] = calendar["date"].dt.quarter
    calendar["week"] = calendar["date"].dt.isocalendar().week.astype(int)
    calendar["is_month_end"] = calendar["date"].dt.is_month_end.astype(int)
    return iso_dates(calendar, ["date"])


def random_walk(start: float, n: int, daily_vol: float) -> np.ndarray:
    shocks = RNG.normal(0, daily_vol, n)
    values = start * np.exp(np.cumsum(shocks))
    return np.round(values, 2)


def build_market_data(commodities: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    business_dates = pd.bdate_range("2025-01-02", "2025-06-30")
    regions = ["Manitoba", "Saskatchewan", "Alberta", "Ontario", "British Columbia"]
    contract_months = ["2025-03", "2025-05", "2025-07", "2025-09"]
    base_prices = {
        "WHEAT": 220.0,
        "CANOLA": 475.0,
        "CORN": 185.0,
        "SOY": 390.0,
        "BARLEY": 205.0,
    }
    region_basis = {
        "Manitoba": 6.0,
        "Saskatchewan": 2.5,
        "Alberta": -1.5,
        "Ontario": 11.0,
        "British Columbia": 18.0,
    }

    fx = pd.DataFrame({"date": business_dates, "usd_cad": random_walk(1.36, len(business_dates), 0.002)})

    futures_rows = []
    cash_rows = []
    margin_rows = []
    for _, commodity in commodities.iterrows():
        commodity_id = commodity["commodity_id"]
        base = base_prices[commodity_id]
        curve = random_walk(base, len(business_dates), 0.009)

        for contract_index, contract_month in enumerate(contract_months):
            carry = 1 + contract_index * 0.012
            contract_noise = RNG.normal(0, base * 0.005, len(business_dates))
            contract_prices = np.maximum(curve * carry + contract_noise, 20)
            for date, price in zip(business_dates, contract_prices):
                futures_rows.append(
                    {
                        "date": date,
                        "commodity_id": commodity_id,
                        "contract_month": contract_month,
                        "futures_price_usd_mt": round(float(price), 2),
                    }
                )

        front_futures = curve
        fx_values = fx["usd_cad"].to_numpy()
        for region in regions:
            basis = region_basis[region] + RNG.normal(0, 4.0, len(business_dates))
            if commodity["currency"] == "USD":
                cash_prices = front_futures * fx_values + basis
            else:
                cash_prices = front_futures + basis
            for date, cash_price in zip(business_dates, cash_prices):
                cash_rows.append(
                    {
                        "date": date,
                        "commodity_id": commodity_id,
                        "region": region,
                        "cash_price_cad_mt": round(float(max(cash_price, 20)), 2),
                    }
                )

        exchange = "ICE" if commodity_id in {"CANOLA", "BARLEY"} else "CME"
        base_margin = {
            "WHEAT": 2_100,
            "CANOLA": 1_350,
            "CORN": 1_800,
            "SOY": 2_350,
            "BARLEY": 1_050,
        }[commodity_id]
        margin_noise = RNG.normal(0, base_margin * 0.04, len(business_dates))
        for date, noise in zip(business_dates, margin_noise):
            initial = max(base_margin + noise, base_margin * 0.7)
            margin_rows.append(
                {
                    "date": date,
                    "commodity_id": commodity_id,
                    "exchange": exchange,
                    "initial_margin_usd_per_contract": round(float(initial), 2),
                    "maintenance_margin_usd_per_contract": round(float(initial * 0.82), 2),
                }
            )

    futures_prices = iso_dates(pd.DataFrame(futures_rows), ["date"])
    cash_prices = iso_dates(pd.DataFrame(cash_rows), ["date"])
    margin_requirements = iso_dates(pd.DataFrame(margin_rows), ["date"])
    fx_rates = iso_dates(fx, ["date"])
    return cash_prices, futures_prices, fx_rates, margin_requirements


def build_physical_transactions(
    commodities: pd.DataFrame,
    counterparties: pd.DataFrame,
    cash_prices: pd.DataFrame,
) -> pd.DataFrame:
    dates = pd.bdate_range("2025-01-02", "2025-05-30")
    regions = counterparties["region"].unique()
    rows = []
    cash_lookup = cash_prices.set_index(["date", "commodity_id", "region"])["cash_price_cad_mt"]

    for i in range(180):
        trade_date = pd.Timestamp(RNG.choice(dates))
        delivery_start = trade_date + pd.Timedelta(days=int(RNG.integers(5, 30)))
        delivery_end = delivery_start + pd.Timedelta(days=int(RNG.integers(14, 50)))
        commodity_id = str(RNG.choice(commodities["commodity_id"].to_numpy()))
        counterparty = counterparties.sample(n=1, random_state=int(RNG.integers(1, 1_000_000))).iloc[0]
        region = str(counterparty["region"] if RNG.random() < 0.65 else RNG.choice(regions))
        buy_sell = str(RNG.choice(["Buy", "Sell"], p=[0.58, 0.42]))
        quantity = float(RNG.integers(250, 6_500))
        trade_date_key = trade_date.strftime("%Y-%m-%d")
        try:
            price = float(cash_lookup.loc[(trade_date_key, commodity_id, region)])
        except KeyError:
            price = float(cash_prices.loc[cash_prices["commodity_id"] == commodity_id, "cash_price_cad_mt"].median())
        fx_exposure_usd = quantity * price * float(RNG.choice([0.0, 0.15, 0.35], p=[0.45, 0.35, 0.20])) / 1.36

        rows.append(
            {
                "transaction_id": f"PHY{i + 1:04d}",
                "trade_date": trade_date,
                "delivery_start": delivery_start,
                "delivery_end": delivery_end,
                "commodity_id": commodity_id,
                "counterparty_id": counterparty["counterparty_id"],
                "region": region,
                "buy_sell": buy_sell,
                "quantity_mt": round(quantity, 2),
                "cash_price_cad_mt": round(price, 2),
                "fx_exposure_usd": round(float(fx_exposure_usd), 2),
                "status": "Open" if delivery_end >= pd.Timestamp("2025-06-30") else "Delivered",
            }
        )

    return iso_dates(pd.DataFrame(rows), ["trade_date", "delivery_start", "delivery_end"])


def build_futures_positions(
    commodities: pd.DataFrame,
    futures_prices: pd.DataFrame,
    margin_requirements: pd.DataFrame,
) -> pd.DataFrame:
    dates = pd.bdate_range("2025-01-02", "2025-05-30")
    contract_months = ["2025-03", "2025-05", "2025-07", "2025-09"]
    brokers = ["RBC Clearing", "TD Securities", "BMO Capital Markets", "CIBC World Markets"]
    rows = []

    futures_lookup = futures_prices.set_index(["date", "commodity_id", "contract_month"])["futures_price_usd_mt"]
    margin_lookup = margin_requirements.set_index(["date", "commodity_id"])["initial_margin_usd_per_contract"]
    commodity_size = commodities.set_index("commodity_id")["contract_size_mt"].to_dict()

    for i in range(120):
        trade_date = pd.Timestamp(RNG.choice(dates))
        commodity_id = str(RNG.choice(commodities["commodity_id"].to_numpy()))
        month_candidates = [m for m in contract_months if pd.Timestamp(m + "-01") >= trade_date.replace(day=1)]
        contract_month = str(RNG.choice(month_candidates or contract_months[-1:]))
        exchange = "ICE" if commodity_id in {"CANOLA", "BARLEY"} else "CME"
        buy_sell = str(RNG.choice(["Buy", "Sell"], p=[0.38, 0.62]))
        contracts = int(RNG.integers(2, 75))
        key = (trade_date.strftime("%Y-%m-%d"), commodity_id, contract_month)
        futures_price = float(futures_lookup.loc[key])
        margin = float(margin_lookup.loc[(trade_date.strftime("%Y-%m-%d"), commodity_id)])

        rows.append(
            {
                "position_id": f"FUT{i + 1:04d}",
                "trade_date": trade_date,
                "contract_month": contract_month,
                "commodity_id": commodity_id,
                "hedge_type": str(RNG.choice(["Inventory hedge", "Forward sale hedge", "Basis hedge"])),
                "exchange": exchange,
                "buy_sell": buy_sell,
                "contracts": contracts,
                "contract_size_mt": commodity_size[commodity_id],
                "futures_price_usd_mt": round(futures_price, 2),
                "broker": str(RNG.choice(brokers)),
                "initial_margin_usd_per_contract": round(margin, 2),
                "status": "Open" if contract_month in {"2025-07", "2025-09"} else "Closed",
            }
        )

    return iso_dates(pd.DataFrame(rows), ["trade_date"])


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

    commodities, counterparties = build_reference_tables()
    calendar = build_calendar()
    cash_prices, futures_prices, fx_rates, margin_requirements = build_market_data(commodities)
    physical_transactions = build_physical_transactions(commodities, counterparties, cash_prices)
    futures_positions = build_futures_positions(commodities, futures_prices, margin_requirements)

    tables = {
        "commodities": commodities,
        "counterparties": counterparties,
        "calendar": calendar,
        "fx_rates": fx_rates,
        "daily_cash_prices": cash_prices,
        "daily_futures_prices": futures_prices,
        "margin_requirements": margin_requirements,
        "physical_transactions": physical_transactions,
        "futures_positions": futures_positions,
    }

    for name, df in tables.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)

    write_sqlite(tables)

    print(f"Generated {len(tables)} raw tables in {DATA_DIR}")
    print(f"SQLite database created at {DB_PATH}")


if __name__ == "__main__":
    main()
