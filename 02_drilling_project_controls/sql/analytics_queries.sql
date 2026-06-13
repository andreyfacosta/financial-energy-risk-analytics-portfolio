DROP VIEW IF EXISTS v_well_latest_status;
DROP VIEW IF EXISTS v_contractor_scorecard;
DROP VIEW IF EXISTS v_budget_variance_by_well;
DROP VIEW IF EXISTS v_npt_by_category;
DROP VIEW IF EXISTS v_hse_by_severity;

CREATE VIEW v_well_latest_status AS
SELECT d.*
FROM daily_project_metrics d
JOIN (
    SELECT well_id, MAX(date) AS max_date
    FROM daily_project_metrics
    GROUP BY well_id
) latest
    ON latest.well_id = d.well_id
    AND latest.max_date = d.date;

CREATE VIEW v_contractor_scorecard AS
SELECT
    contractor_id,
    contractor_name,
    COUNT(DISTINCT well_id) AS wells_supported,
    SUM(actual_cost_cad) AS actual_cost_cad,
    AVG(rig_utilization_pct) AS avg_rig_utilization_pct,
    SUM(npt_hours) AS npt_hours,
    SUM(hse_incident_count) AS hse_incident_count
FROM daily_project_metrics
GROUP BY contractor_id, contractor_name;

CREATE VIEW v_budget_variance_by_well AS
SELECT
    well_id,
    well_name,
    afe_budget_cad,
    actual_cost_cad,
    forecast_final_cost_cad,
    cost_variance_cad,
    cost_variance_pct,
    forecast_variance_cad,
    risk_flag
FROM well_performance_summary;

CREATE VIEW v_npt_by_category AS
SELECT
    npt_category,
    SUM(npt_hours) AS npt_hours,
    SUM(estimated_cost_impact_cad) AS estimated_cost_impact_cad
FROM npt_events
GROUP BY npt_category;

CREATE VIEW v_hse_by_severity AS
SELECT
    severity,
    COUNT(*) AS hse_incident_count,
    SUM(recordable) AS recordable_count,
    SUM(lost_time) AS lost_time_count
FROM hse_events
GROUP BY severity;
