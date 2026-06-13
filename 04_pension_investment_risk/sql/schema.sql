DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS asset_classes;
DROP TABLE IF EXISTS holdings;
DROP TABLE IF EXISTS daily_prices;
DROP TABLE IF EXISTS fx_rates;
DROP TABLE IF EXISTS contributions;
DROP TABLE IF EXISTS withdrawals;
DROP TABLE IF EXISTS benchmarks;
DROP TABLE IF EXISTS calendar;

CREATE TABLE portfolios (
    portfolio_id TEXT PRIMARY KEY,
    portfolio_name TEXT NOT NULL,
    risk_profile TEXT NOT NULL,
    target_return_pct REAL NOT NULL,
    base_currency TEXT NOT NULL
);

CREATE TABLE members (
    member_id TEXT PRIMARY KEY,
    portfolio_id TEXT NOT NULL,
    age INTEGER NOT NULL,
    retirement_age INTEGER NOT NULL,
    annual_salary_cad REAL NOT NULL,
    contribution_rate_pct REAL NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id)
);

CREATE TABLE asset_classes (
    asset_class_id TEXT PRIMARY KEY,
    asset_class_name TEXT NOT NULL,
    asset_category TEXT NOT NULL,
    currency TEXT NOT NULL,
    risk_bucket TEXT NOT NULL
);

CREATE TABLE holdings (
    holding_id TEXT PRIMARY KEY,
    portfolio_id TEXT NOT NULL,
    asset_class_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    units REAL NOT NULL,
    target_allocation_pct REAL NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id),
    FOREIGN KEY (asset_class_id) REFERENCES asset_classes(asset_class_id)
);

CREATE TABLE daily_prices (
    date TEXT NOT NULL,
    asset_class_id TEXT NOT NULL,
    price_local REAL NOT NULL,
    PRIMARY KEY (date, asset_class_id),
    FOREIGN KEY (asset_class_id) REFERENCES asset_classes(asset_class_id)
);

CREATE TABLE fx_rates (
    date TEXT PRIMARY KEY,
    usd_cad REAL NOT NULL,
    eur_cad REAL NOT NULL
);

CREATE TABLE contributions (
    contribution_id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    member_id TEXT NOT NULL,
    portfolio_id TEXT NOT NULL,
    contribution_cad REAL NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id)
);

CREATE TABLE withdrawals (
    withdrawal_id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    member_id TEXT NOT NULL,
    portfolio_id TEXT NOT NULL,
    withdrawal_cad REAL NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id)
);

CREATE TABLE benchmarks (
    date TEXT NOT NULL,
    portfolio_id TEXT NOT NULL,
    benchmark_name TEXT NOT NULL,
    benchmark_return REAL NOT NULL,
    PRIMARY KEY (date, portfolio_id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id)
);

CREATE TABLE calendar (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    week INTEGER NOT NULL,
    is_month_end INTEGER NOT NULL
);
