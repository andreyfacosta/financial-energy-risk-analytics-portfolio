from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DB_PATH = DATA_DIR / "insurance_loss_ratio.sqlite"


def read_csv(name: str, date_cols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{name}.csv", parse_dates=date_cols or [])


def build_monthly_loss_ratio() -> pd.DataFrame:
    premiums = read_csv("premiums", ["month_start"])
    claims = read_csv("claims", ["service_date", "paid_date"])
    policies = read_csv("group_policies", ["effective_date", "renewal_date"])
    employers = read_csv("employers")
    products = read_csv("policy_products")
    regions = read_csv("regions")

    claims["month_start"] = claims["service_date"].values.astype("datetime64[M]")
    claims_monthly = (
        claims.groupby(["month_start", "policy_id", "employer_id"], as_index=False)
        .agg(
            paid_claims_cad=("paid_claim_cad", "sum"),
            incurred_claims_cad=("incurred_claim_cad", "sum"),
            claim_count=("claim_id", "count"),
        )
    )
    df = premiums.merge(claims_monthly, on=["month_start", "policy_id", "employer_id"], how="left")
    for col in ["paid_claims_cad", "incurred_claims_cad", "claim_count"]:
        df[col] = df[col].fillna(0)
    df = (
        df.merge(policies[["policy_id", "renewal_date", "pricing_tier"]], on="policy_id", how="left")
        .merge(employers, on="employer_id", how="left")
        .merge(regions, on="region_id", how="left")
        .merge(products, on="product_id", how="left")
    )
    df["loss_ratio"] = np.where(df["earned_premium_cad"] > 0, df["incurred_claims_cad"] / df["earned_premium_cad"], 0)
    df["claims_frequency"] = np.where(df["member_count"] > 0, df["claim_count"] / df["member_count"], 0)
    df["claims_severity_cad"] = np.where(df["claim_count"] > 0, df["incurred_claims_cad"] / df["claim_count"], 0)
    df["premium_per_member_cad"] = np.where(df["member_count"] > 0, df["earned_premium_cad"] / df["member_count"], 0)
    df["claims_per_member_cad"] = np.where(df["member_count"] > 0, df["incurred_claims_cad"] / df["member_count"], 0)
    df["profitability_cad"] = df["earned_premium_cad"] - df["incurred_claims_cad"]
    cols = [
        "month_start", "policy_id", "employer_id", "employer_name", "industry", "region_id", "region_name",
        "province", "product_id", "product_name", "product_category", "coverage_level", "pricing_tier",
        "member_count", "earned_premium_cad", "paid_claims_cad", "incurred_claims_cad", "claim_count",
        "loss_ratio", "claims_frequency", "claims_severity_cad", "premium_per_member_cad",
        "claims_per_member_cad", "profitability_cad",
    ]
    return df[cols].round(4)


def build_outputs(monthly: pd.DataFrame) -> dict[str, pd.DataFrame]:
    claims = read_csv("claims", ["service_date", "paid_date"])
    categories = read_csv("claim_categories")
    products = read_csv("policy_products")

    policy_profitability = (
        monthly.groupby(["policy_id", "employer_id", "employer_name", "product_id", "product_name", "region_name"], as_index=False)
        .agg(
            earned_premium_cad=("earned_premium_cad", "sum"),
            paid_claims_cad=("paid_claims_cad", "sum"),
            incurred_claims_cad=("incurred_claims_cad", "sum"),
            claim_count=("claim_count", "sum"),
            avg_member_count=("member_count", "mean"),
            profitability_cad=("profitability_cad", "sum"),
        )
    )
    policy_profitability["loss_ratio"] = np.where(policy_profitability["earned_premium_cad"] > 0, policy_profitability["incurred_claims_cad"] / policy_profitability["earned_premium_cad"], 0)
    policy_profitability["claims_frequency"] = np.where(policy_profitability["avg_member_count"] > 0, policy_profitability["claim_count"] / policy_profitability["avg_member_count"], 0)
    policy_profitability["claims_severity_cad"] = np.where(policy_profitability["claim_count"] > 0, policy_profitability["incurred_claims_cad"] / policy_profitability["claim_count"], 0)

    claim_detail = claims.merge(categories, on="category_id", how="left")
    severity_frequency = (
        claim_detail.groupby(["category_id", "category_name", "category_group"], as_index=False)
        .agg(
            claim_count=("claim_id", "count"),
            paid_claims_cad=("paid_claim_cad", "sum"),
            incurred_claims_cad=("incurred_claim_cad", "sum"),
            claims_severity_cad=("incurred_claim_cad", "mean"),
        )
    )

    employer_summary = (
        monthly.groupby(["employer_id", "employer_name", "industry", "region_name"], as_index=False)
        .agg(
            earned_premium_cad=("earned_premium_cad", "sum"),
            incurred_claims_cad=("incurred_claims_cad", "sum"),
            claim_count=("claim_count", "sum"),
            avg_member_count=("member_count", "mean"),
            profitability_cad=("profitability_cad", "sum"),
        )
    )
    employer_summary["loss_ratio"] = np.where(employer_summary["earned_premium_cad"] > 0, employer_summary["incurred_claims_cad"] / employer_summary["earned_premium_cad"], 0)
    employer_summary["claims_per_member_cad"] = np.where(employer_summary["avg_member_count"] > 0, employer_summary["incurred_claims_cad"] / employer_summary["avg_member_count"], 0)
    conditions = [
        (employer_summary["loss_ratio"] > 0.95) | (employer_summary["profitability_cad"] < 0),
        (employer_summary["loss_ratio"] > 0.80) | (employer_summary["claims_per_member_cad"] > employer_summary["claims_per_member_cad"].quantile(0.75)),
    ]
    employer_summary["renewal_risk"] = np.select(conditions, ["High", "Medium"], default="Low")

    renewal = employer_summary[[
        "employer_id", "employer_name", "industry", "region_name", "earned_premium_cad", "incurred_claims_cad",
        "loss_ratio", "profitability_cad", "claim_count", "claims_per_member_cad", "renewal_risk",
    ]].copy()
    renewal["recommended_action"] = np.select(
        [renewal["renewal_risk"] == "High", renewal["renewal_risk"] == "Medium"],
        ["Renewal pricing review", "Monitor experience trend"],
        default="Standard renewal"
    )

    product_mix = (
        monthly.groupby(["product_id", "product_name", "product_category", "coverage_level"], as_index=False)
        .agg(
            earned_premium_cad=("earned_premium_cad", "sum"),
            incurred_claims_cad=("incurred_claims_cad", "sum"),
            member_count=("member_count", "sum"),
            claim_count=("claim_count", "sum"),
        )
        .merge(products, on=["product_id", "product_name", "product_category", "coverage_level"], how="left")
    )
    product_mix["loss_ratio"] = np.where(product_mix["earned_premium_cad"] > 0, product_mix["incurred_claims_cad"] / product_mix["earned_premium_cad"], 0)
    product_mix["premium_mix_pct"] = product_mix["earned_premium_cad"] / product_mix["earned_premium_cad"].sum()

    executive = pd.DataFrame(
        [
            ("Earned premium CAD", round(float(monthly["earned_premium_cad"].sum()), 2), "Total earned premium"),
            ("Incurred claims CAD", round(float(monthly["incurred_claims_cad"].sum()), 2), "Total incurred claims"),
            ("Paid claims CAD", round(float(monthly["paid_claims_cad"].sum()), 2), "Total paid claims"),
            ("Portfolio loss ratio", round(float(monthly["incurred_claims_cad"].sum() / monthly["earned_premium_cad"].sum()), 4), "Incurred claims divided by earned premium"),
            ("Profitability CAD", round(float(monthly["profitability_cad"].sum()), 2), "Earned premium minus incurred claims"),
            ("Claim count", int(monthly["claim_count"].sum()), "Total claim count"),
            ("Average claims severity CAD", round(float(severity_frequency["claims_severity_cad"].mean()), 2), "Average incurred claim severity by category"),
            ("High renewal risk employers", int((renewal["renewal_risk"] == "High").sum()), "Employers with high renewal risk"),
        ],
        columns=["metric", "value", "notes"],
    )
    return {
        "policy_profitability": policy_profitability.round(4),
        "claims_severity_frequency": severity_frequency.round(4),
        "renewal_risk_flags": renewal.round(4),
        "employer_summary": employer_summary.round(4),
        "product_mix_summary": product_mix.round(4),
        "executive_insurance_summary": executive,
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
    monthly = build_monthly_loss_ratio()
    outputs = {"monthly_loss_ratio": monthly}
    outputs.update(build_outputs(monthly))
    for name, df in outputs.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
    write_outputs_to_sqlite(outputs)
    print("Generated analytical outputs:")
    for name, df in outputs.items():
        print(f"- {name}.csv: {len(df)} rows")


if __name__ == "__main__":
    main()
