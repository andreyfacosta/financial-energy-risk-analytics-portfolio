DROP VIEW IF EXISTS v_latest_portfolio_returns;
DROP VIEW IF EXISTS v_allocation_drift;
DROP VIEW IF EXISTS v_fx_exposure;
DROP VIEW IF EXISTS v_scenario_downside;

CREATE VIEW v_latest_portfolio_returns AS
SELECT r.*
FROM portfolio_daily_returns r
JOIN (
    SELECT portfolio_id, MAX(date) AS max_date
    FROM portfolio_daily_returns
    GROUP BY portfolio_id
) latest
    ON latest.portfolio_id = r.portfolio_id
    AND latest.max_date = r.date;

CREATE VIEW v_allocation_drift AS
SELECT *
FROM allocation_summary
ORDER BY ABS(allocation_drift_pct) DESC;

CREATE VIEW v_fx_exposure AS
SELECT
    portfolio_id,
    portfolio_name,
    currency,
    SUM(fx_exposure_cad) AS fx_exposure_cad,
    SUM(fx_exposure_pct) AS fx_exposure_pct
FROM fx_exposure_summary
GROUP BY portfolio_id, portfolio_name, currency;

CREATE VIEW v_scenario_downside AS
SELECT *
FROM scenario_results
WHERE stress_impact_cad < 0
ORDER BY stress_impact_cad ASC;
