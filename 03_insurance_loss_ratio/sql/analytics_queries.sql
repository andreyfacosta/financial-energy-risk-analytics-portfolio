DROP VIEW IF EXISTS v_latest_policy_profitability;
DROP VIEW IF EXISTS v_high_risk_employers;
DROP VIEW IF EXISTS v_loss_ratio_by_product;
DROP VIEW IF EXISTS v_claims_by_category;

CREATE VIEW v_latest_policy_profitability AS
SELECT *
FROM policy_profitability
ORDER BY loss_ratio DESC;

CREATE VIEW v_high_risk_employers AS
SELECT *
FROM renewal_risk_flags
WHERE renewal_risk IN ('High', 'Medium')
ORDER BY loss_ratio DESC;

CREATE VIEW v_loss_ratio_by_product AS
SELECT
    product_id,
    product_name,
    SUM(earned_premium_cad) AS earned_premium_cad,
    SUM(incurred_claims_cad) AS incurred_claims_cad,
    SUM(incurred_claims_cad) / NULLIF(SUM(earned_premium_cad), 0) AS loss_ratio
FROM monthly_loss_ratio
GROUP BY product_id, product_name;

CREATE VIEW v_claims_by_category AS
SELECT
    category_id,
    category_name,
    SUM(claim_count) AS claim_count,
    SUM(paid_claims_cad) AS paid_claims_cad,
    AVG(claims_severity_cad) AS avg_claims_severity_cad
FROM claims_severity_frequency
GROUP BY category_id, category_name;
