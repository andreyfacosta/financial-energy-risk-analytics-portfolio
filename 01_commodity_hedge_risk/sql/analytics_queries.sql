-- SQLite-compatible query examples for the Commodity Hedge Risk Dashboard.
-- These queries support Power BI import validation and analyst review.

DROP VIEW IF EXISTS v_latest_cash_prices;
DROP VIEW IF EXISTS v_latest_futures_prices;
DROP VIEW IF EXISTS v_physical_exposure_by_counterparty;
DROP VIEW IF EXISTS v_open_futures_positions;
DROP VIEW IF EXISTS v_margin_requirement_by_commodity;

CREATE VIEW v_latest_cash_prices AS
SELECT
    cp.date,
    cp.commodity_id,
    c.commodity_name,
    cp.region,
    cp.cash_price_cad_mt
FROM daily_cash_prices cp
JOIN commodities c ON c.commodity_id = cp.commodity_id
WHERE cp.date = (SELECT MAX(date) FROM daily_cash_prices);

CREATE VIEW v_latest_futures_prices AS
SELECT
    fp.date,
    fp.commodity_id,
    c.commodity_name,
    fp.contract_month,
    fp.futures_price_usd_mt,
    fx.usd_cad,
    fp.futures_price_usd_mt * fx.usd_cad AS futures_price_cad_mt
FROM daily_futures_prices fp
JOIN commodities c ON c.commodity_id = fp.commodity_id
JOIN fx_rates fx ON fx.date = fp.date
WHERE fp.date = (SELECT MAX(date) FROM daily_futures_prices);

CREATE VIEW v_physical_exposure_by_counterparty AS
SELECT
    p.counterparty_id,
    cp.counterparty_name,
    cp.region,
    cp.credit_rating,
    cp.credit_limit_cad,
    p.commodity_id,
    SUM(CASE WHEN p.buy_sell = 'Buy' THEN p.quantity_mt ELSE -p.quantity_mt END) AS signed_quantity_mt,
    SUM(CASE WHEN p.buy_sell = 'Buy' THEN 1 ELSE -1 END * p.quantity_mt * p.cash_price_cad_mt) AS exposure_cad
FROM physical_transactions p
JOIN counterparties cp ON cp.counterparty_id = p.counterparty_id
GROUP BY
    p.counterparty_id,
    cp.counterparty_name,
    cp.region,
    cp.credit_rating,
    cp.credit_limit_cad,
    p.commodity_id;

CREATE VIEW v_open_futures_positions AS
SELECT
    f.commodity_id,
    c.commodity_name,
    f.contract_month,
    f.exchange,
    f.broker,
    SUM(CASE WHEN f.buy_sell = 'Buy' THEN f.contracts ELSE -f.contracts END) AS signed_contracts,
    SUM(CASE WHEN f.buy_sell = 'Buy' THEN 1 ELSE -1 END * f.contracts * f.contract_size_mt) AS signed_quantity_mt,
    SUM(ABS(f.contracts) * f.initial_margin_usd_per_contract) AS initial_margin_usd
FROM futures_positions f
JOIN commodities c ON c.commodity_id = f.commodity_id
WHERE f.status = 'Open'
GROUP BY f.commodity_id, c.commodity_name, f.contract_month, f.exchange, f.broker;

CREATE VIEW v_margin_requirement_by_commodity AS
SELECT
    f.commodity_id,
    c.commodity_name,
    f.exchange,
    SUM(ABS(f.contracts) * mr.initial_margin_usd_per_contract * fx.usd_cad) AS initial_margin_cad
FROM futures_positions f
JOIN commodities c ON c.commodity_id = f.commodity_id
JOIN margin_requirements mr
    ON mr.commodity_id = f.commodity_id
    AND mr.exchange = f.exchange
    AND mr.date = (SELECT MAX(date) FROM margin_requirements)
JOIN fx_rates fx ON fx.date = mr.date
WHERE f.status = 'Open'
GROUP BY f.commodity_id, c.commodity_name, f.exchange;

-- Latest executive KPIs from generated analytical output.
SELECT
    metric,
    value,
    notes
FROM risk_summary
ORDER BY metric;

-- Highest open counterparty exposure.
SELECT
    counterparty_name,
    region,
    credit_rating,
    exposure_cad,
    credit_limit_cad,
    credit_utilization_pct,
    risk_flag
FROM counterparty_exposure
ORDER BY exposure_cad DESC
LIMIT 10;

-- Largest daily net open exposures.
SELECT
    date,
    commodity_name,
    net_open_exposure_cad,
    hedge_ratio,
    basis_cad_mt,
    var_99_cad
FROM daily_risk_metrics
ORDER BY ABS(net_open_exposure_cad) DESC
LIMIT 20;
