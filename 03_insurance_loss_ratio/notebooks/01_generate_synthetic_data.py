from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DB_PATH = DATA_DIR / "insurance_loss_ratio.sqlite"
RNG = np.random.default_rng(1303)


def iso_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for column in columns:
        out[column] = pd.to_datetime(out[column]).dt.strftime("%Y-%m-%d")
    return out


def build_calendar() -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    calendar = pd.DataFrame({"date": dates})
    calendar["year"] = calendar["date"].dt.year
    calendar["month"] = calendar["date"].dt.month
    calendar["quarter"] = calendar["date"].dt.quarter
    calendar["week"] = calendar["date"].dt.isocalendar().week.astype(int)
    calendar["is_month_end"] = calendar["date"].dt.is_month_end.astype(int)
    return iso_dates(calendar, ["date"])


def build_reference_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    regions = pd.DataFrame(
        [
            ("REG001", "Prairies", "Manitoba"),
            ("REG002", "Ontario", "Ontario"),
            ("REG003", "Alberta", "Alberta"),
            ("REG004", "British Columbia", "British Columbia"),
            ("REG005", "Atlantic", "Nova Scotia"),
        ],
        columns=["region_id", "region_name", "province"],
    )
    employers = pd.DataFrame(
        [
            ("EMP001", "Prairie Manufacturing", "Manufacturing", "REG001", "250-499"),
            ("EMP002", "Northern Retail Group", "Retail", "REG002", "500-999"),
            ("EMP003", "West Energy Services", "Energy", "REG003", "100-249"),
            ("EMP004", "Pacific Logistics", "Transportation", "REG004", "250-499"),
            ("EMP005", "Lakeview Schools", "Education", "REG002", "1000+"),
            ("EMP006", "Central Ag Foods", "Food processing", "REG001", "500-999"),
            ("EMP007", "Atlantic Care Homes", "Healthcare", "REG005", "250-499"),
            ("EMP008", "Metro Software Co", "Technology", "REG002", "100-249"),
            ("EMP009", "Foothills Construction", "Construction", "REG003", "100-249"),
            ("EMP010", "Harbour Hospitality", "Hospitality", "REG004", "250-499"),
            ("EMP011", "Winnipeg Services", "Professional services", "REG001", "100-249"),
            ("EMP012", "Capital Distribution", "Wholesale", "REG002", "500-999"),
        ],
        columns=["employer_id", "employer_name", "industry", "region_id", "employer_size_band"],
    )
    products = pd.DataFrame(
        [
            ("PRD001", "Core Health", "Health", "Core"),
            ("PRD002", "Enhanced Health", "Health", "Enhanced"),
            ("PRD003", "Dental Plus", "Dental", "Enhanced"),
            ("PRD004", "Disability Protect", "Disability", "Core"),
            ("PRD005", "Life Basic", "Life", "Core"),
        ],
        columns=["product_id", "product_name", "product_category", "coverage_level"],
    )
    categories = pd.DataFrame(
        [
            ("CAT001", "Prescription Drugs", "Health"),
            ("CAT002", "Paramedical", "Health"),
            ("CAT003", "Dental Basic", "Dental"),
            ("CAT004", "Dental Major", "Dental"),
            ("CAT005", "Short Term Disability", "Disability"),
            ("CAT006", "Life Claim", "Life"),
        ],
        columns=["category_id", "category_name", "category_group"],
    )
    return regions, employers, products, categories


def build_policies_members_premiums_claims(
    employers: pd.DataFrame,
    products: pd.DataFrame,
    categories: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    policy_rows = []
    member_rows = []
    premium_rows = []
    claim_rows = []
    months = pd.date_range("2025-01-01", "2025-12-01", freq="MS")
    member_id = 1
    claim_id = 1
    policy_id_num = 1
    product_rate = {"PRD001": 145, "PRD002": 215, "PRD003": 85, "PRD004": 62, "PRD005": 28}
    category_mean = {"CAT001": 135, "CAT002": 95, "CAT003": 180, "CAT004": 850, "CAT005": 2400, "CAT006": 8000}

    for _, employer in employers.iterrows():
        chosen_products = products.sample(n=3, random_state=int(RNG.integers(1, 1_000_000)))
        base_members = int(RNG.integers(80, 620))
        for _, product in chosen_products.iterrows():
            policy_id = f"POL{policy_id_num:04d}"
            policy_id_num += 1
            effective = pd.Timestamp("2025-01-01") - pd.Timedelta(days=int(RNG.integers(0, 365)))
            renewal = pd.Timestamp("2026-01-01") + pd.Timedelta(days=int(RNG.integers(0, 90)))
            policy_rows.append(
                {
                    "policy_id": policy_id,
                    "employer_id": employer["employer_id"],
                    "product_id": product["product_id"],
                    "effective_date": effective,
                    "renewal_date": renewal,
                    "status": "Active",
                    "pricing_tier": str(RNG.choice(["Standard", "Preferred", "Watch"], p=[0.62, 0.25, 0.13])),
                }
            )
            member_count = int(max(25, base_members * RNG.uniform(0.75, 1.05)))
            members_for_policy = []
            for _ in range(member_count):
                member = {
                    "member_id": f"MBR{member_id:05d}",
                    "policy_id": policy_id,
                    "employer_id": employer["employer_id"],
                    "age_band": str(RNG.choice(["18-29", "30-39", "40-49", "50-59", "60+"], p=[0.18, 0.28, 0.25, 0.20, 0.09])),
                    "coverage_tier": str(RNG.choice(["Single", "Couple", "Family"], p=[0.48, 0.22, 0.30])),
                    "enrollment_date": effective + pd.Timedelta(days=int(RNG.integers(0, 120))),
                    "status": "Active",
                }
                members_for_policy.append(member)
                member_rows.append(member)
                member_id += 1
            rate = product_rate[product["product_id"]] * RNG.uniform(0.90, 1.18)
            for month in months:
                active_members = int(member_count * RNG.uniform(0.96, 1.03))
                premium_rows.append(
                    {
                        "premium_id": f"PREM{len(premium_rows) + 1:05d}",
                        "month_start": month,
                        "policy_id": policy_id,
                        "employer_id": employer["employer_id"],
                        "product_id": product["product_id"],
                        "member_count": active_members,
                        "earned_premium_cad": round(float(active_members * rate), 2),
                    }
                )
                claim_frequency = {"Health": 0.10, "Dental": 0.075, "Disability": 0.010, "Life": 0.002}[product["product_category"]]
                expected_claims = max(0, int(active_members * claim_frequency * RNG.uniform(0.65, 1.45)))
                product_categories = categories[categories["category_group"] == product["product_category"]]
                if product_categories.empty:
                    product_categories = categories
                for _ in range(expected_claims):
                    member = members_for_policy[int(RNG.integers(0, len(members_for_policy)))]
                    cat = product_categories.sample(n=1, random_state=int(RNG.integers(1, 1_000_000))).iloc[0]
                    paid = float(RNG.gamma(shape=2.2, scale=category_mean[cat["category_id"]] / 2.2))
                    incurred = paid * float(RNG.uniform(1.00, 1.22))
                    service = month + pd.Timedelta(days=int(RNG.integers(0, 27)))
                    paid_date = service + pd.Timedelta(days=int(RNG.integers(7, 45)))
                    claim_rows.append(
                        {
                            "claim_id": f"CLM{claim_id:06d}",
                            "service_date": service,
                            "paid_date": paid_date,
                            "policy_id": policy_id,
                            "employer_id": employer["employer_id"],
                            "member_id": member["member_id"],
                            "category_id": cat["category_id"],
                            "paid_claim_cad": round(paid, 2),
                            "incurred_claim_cad": round(incurred, 2),
                            "claim_status": "Paid" if RNG.random() > 0.08 else "Pending",
                        }
                    )
                    claim_id += 1

    return (
        iso_dates(pd.DataFrame(policy_rows), ["effective_date", "renewal_date"]),
        iso_dates(pd.DataFrame(member_rows), ["enrollment_date"]),
        iso_dates(pd.DataFrame(premium_rows), ["month_start"]),
        iso_dates(pd.DataFrame(claim_rows), ["service_date", "paid_date"]),
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
    regions, employers, products, categories = build_reference_tables()
    policies, members, premiums, claims = build_policies_members_premiums_claims(employers, products, categories)
    calendar = build_calendar()
    tables = {
        "group_policies": policies,
        "employers": employers,
        "members": members,
        "premiums": premiums,
        "claims": claims,
        "claim_categories": categories,
        "policy_products": products,
        "regions": regions,
        "calendar": calendar,
    }
    for name, df in tables.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
    write_sqlite(tables)
    print(f"Generated {len(tables)} raw tables in {DATA_DIR}")
    print(f"SQLite database created at {DB_PATH}")


if __name__ == "__main__":
    main()
