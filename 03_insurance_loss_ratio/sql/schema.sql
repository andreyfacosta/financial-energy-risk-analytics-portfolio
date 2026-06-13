DROP TABLE IF EXISTS group_policies;
DROP TABLE IF EXISTS employers;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS premiums;
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS claim_categories;
DROP TABLE IF EXISTS policy_products;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS calendar;

CREATE TABLE regions (
    region_id TEXT PRIMARY KEY,
    region_name TEXT NOT NULL,
    province TEXT NOT NULL
);

CREATE TABLE employers (
    employer_id TEXT PRIMARY KEY,
    employer_name TEXT NOT NULL,
    industry TEXT NOT NULL,
    region_id TEXT NOT NULL,
    employer_size_band TEXT NOT NULL,
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

CREATE TABLE policy_products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    coverage_level TEXT NOT NULL
);

CREATE TABLE group_policies (
    policy_id TEXT PRIMARY KEY,
    employer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    renewal_date TEXT NOT NULL,
    status TEXT NOT NULL,
    pricing_tier TEXT NOT NULL,
    FOREIGN KEY (employer_id) REFERENCES employers(employer_id),
    FOREIGN KEY (product_id) REFERENCES policy_products(product_id)
);

CREATE TABLE members (
    member_id TEXT PRIMARY KEY,
    policy_id TEXT NOT NULL,
    employer_id TEXT NOT NULL,
    age_band TEXT NOT NULL,
    coverage_tier TEXT NOT NULL,
    enrollment_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (policy_id) REFERENCES group_policies(policy_id),
    FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
);

CREATE TABLE premiums (
    premium_id TEXT PRIMARY KEY,
    month_start TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    employer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    member_count INTEGER NOT NULL,
    earned_premium_cad REAL NOT NULL,
    FOREIGN KEY (policy_id) REFERENCES group_policies(policy_id)
);

CREATE TABLE claim_categories (
    category_id TEXT PRIMARY KEY,
    category_name TEXT NOT NULL,
    category_group TEXT NOT NULL
);

CREATE TABLE claims (
    claim_id TEXT PRIMARY KEY,
    service_date TEXT NOT NULL,
    paid_date TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    employer_id TEXT NOT NULL,
    member_id TEXT NOT NULL,
    category_id TEXT NOT NULL,
    paid_claim_cad REAL NOT NULL,
    incurred_claim_cad REAL NOT NULL,
    claim_status TEXT NOT NULL,
    FOREIGN KEY (policy_id) REFERENCES group_policies(policy_id),
    FOREIGN KEY (employer_id) REFERENCES employers(employer_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (category_id) REFERENCES claim_categories(category_id)
);

CREATE TABLE calendar (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    week INTEGER NOT NULL,
    is_month_end INTEGER NOT NULL
);
