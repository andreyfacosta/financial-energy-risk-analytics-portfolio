DROP TABLE IF EXISTS physical_transactions;
DROP TABLE IF EXISTS futures_positions;
DROP TABLE IF EXISTS daily_cash_prices;
DROP TABLE IF EXISTS daily_futures_prices;
DROP TABLE IF EXISTS fx_rates;
DROP TABLE IF EXISTS margin_requirements;
DROP TABLE IF EXISTS counterparties;
DROP TABLE IF EXISTS commodities;
DROP TABLE IF EXISTS calendar;

CREATE TABLE commodities (
    commodity_id TEXT PRIMARY KEY,
    commodity_name TEXT NOT NULL,
    benchmark_contract TEXT NOT NULL,
    contract_size_mt REAL NOT NULL,
    currency TEXT NOT NULL
);

CREATE TABLE counterparties (
    counterparty_id TEXT PRIMARY KEY,
    counterparty_name TEXT NOT NULL,
    counterparty_type TEXT NOT NULL,
    region TEXT NOT NULL,
    credit_rating TEXT NOT NULL,
    credit_limit_cad REAL NOT NULL
);

CREATE TABLE calendar (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    week INTEGER NOT NULL,
    is_month_end INTEGER NOT NULL
);

CREATE TABLE fx_rates (
    date TEXT PRIMARY KEY,
    usd_cad REAL NOT NULL
);

CREATE TABLE daily_cash_prices (
    date TEXT NOT NULL,
    commodity_id TEXT NOT NULL,
    region TEXT NOT NULL,
    cash_price_cad_mt REAL NOT NULL,
    PRIMARY KEY (date, commodity_id, region),
    FOREIGN KEY (commodity_id) REFERENCES commodities(commodity_id)
);

CREATE TABLE daily_futures_prices (
    date TEXT NOT NULL,
    commodity_id TEXT NOT NULL,
    contract_month TEXT NOT NULL,
    futures_price_usd_mt REAL NOT NULL,
    PRIMARY KEY (date, commodity_id, contract_month),
    FOREIGN KEY (commodity_id) REFERENCES commodities(commodity_id)
);

CREATE TABLE margin_requirements (
    date TEXT NOT NULL,
    commodity_id TEXT NOT NULL,
    exchange TEXT NOT NULL,
    initial_margin_usd_per_contract REAL NOT NULL,
    maintenance_margin_usd_per_contract REAL NOT NULL,
    PRIMARY KEY (date, commodity_id, exchange),
    FOREIGN KEY (commodity_id) REFERENCES commodities(commodity_id)
);

CREATE TABLE physical_transactions (
    transaction_id TEXT PRIMARY KEY,
    trade_date TEXT NOT NULL,
    delivery_start TEXT NOT NULL,
    delivery_end TEXT NOT NULL,
    commodity_id TEXT NOT NULL,
    counterparty_id TEXT NOT NULL,
    region TEXT NOT NULL,
    buy_sell TEXT NOT NULL,
    quantity_mt REAL NOT NULL,
    cash_price_cad_mt REAL NOT NULL,
    fx_exposure_usd REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (commodity_id) REFERENCES commodities(commodity_id),
    FOREIGN KEY (counterparty_id) REFERENCES counterparties(counterparty_id)
);

CREATE TABLE futures_positions (
    position_id TEXT PRIMARY KEY,
    trade_date TEXT NOT NULL,
    contract_month TEXT NOT NULL,
    commodity_id TEXT NOT NULL,
    hedge_type TEXT NOT NULL,
    exchange TEXT NOT NULL,
    buy_sell TEXT NOT NULL,
    contracts INTEGER NOT NULL,
    contract_size_mt REAL NOT NULL,
    futures_price_usd_mt REAL NOT NULL,
    broker TEXT NOT NULL,
    initial_margin_usd_per_contract REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (commodity_id) REFERENCES commodities(commodity_id)
);
