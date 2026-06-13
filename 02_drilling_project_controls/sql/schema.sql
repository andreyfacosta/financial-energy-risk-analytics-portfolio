DROP TABLE IF EXISTS wells;
DROP TABLE IF EXISTS drilling_jobs;
DROP TABLE IF EXISTS daily_operations;
DROP TABLE IF EXISTS cost_actuals;
DROP TABLE IF EXISTS afe_budgets;
DROP TABLE IF EXISTS contractors;
DROP TABLE IF EXISTS rigs;
DROP TABLE IF EXISTS hse_events;
DROP TABLE IF EXISTS npt_events;
DROP TABLE IF EXISTS calendar;

CREATE TABLE wells (
    well_id TEXT PRIMARY KEY,
    well_name TEXT NOT NULL,
    basin TEXT NOT NULL,
    region TEXT NOT NULL,
    well_type TEXT NOT NULL,
    target_depth_m REAL NOT NULL,
    planned_start TEXT NOT NULL,
    planned_end TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE contractors (
    contractor_id TEXT PRIMARY KEY,
    contractor_name TEXT NOT NULL,
    service_line TEXT NOT NULL,
    base_location TEXT NOT NULL,
    safety_rating TEXT NOT NULL
);

CREATE TABLE rigs (
    rig_id TEXT PRIMARY KEY,
    rig_name TEXT NOT NULL,
    rig_type TEXT NOT NULL,
    horsepower INTEGER NOT NULL,
    daily_rate_cad REAL NOT NULL
);

CREATE TABLE drilling_jobs (
    job_id TEXT PRIMARY KEY,
    well_id TEXT NOT NULL,
    rig_id TEXT NOT NULL,
    contractor_id TEXT NOT NULL,
    afe_id TEXT NOT NULL,
    job_start TEXT NOT NULL,
    planned_spud_date TEXT NOT NULL,
    planned_total_depth_date TEXT NOT NULL,
    actual_spud_date TEXT NOT NULL,
    actual_total_depth_date TEXT NOT NULL,
    planned_depth_m REAL NOT NULL,
    FOREIGN KEY (well_id) REFERENCES wells(well_id),
    FOREIGN KEY (rig_id) REFERENCES rigs(rig_id),
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id)
);

CREATE TABLE afe_budgets (
    afe_id TEXT NOT NULL,
    well_id TEXT NOT NULL,
    budget_category TEXT NOT NULL,
    budget_cad REAL NOT NULL,
    planned_days REAL NOT NULL,
    PRIMARY KEY (afe_id, budget_category),
    FOREIGN KEY (well_id) REFERENCES wells(well_id)
);

CREATE TABLE daily_operations (
    date TEXT NOT NULL,
    job_id TEXT NOT NULL,
    well_id TEXT NOT NULL,
    rig_id TEXT NOT NULL,
    operation_phase TEXT NOT NULL,
    depth_drilled_m REAL NOT NULL,
    cumulative_depth_m REAL NOT NULL,
    drilling_hours REAL NOT NULL,
    productive_hours REAL NOT NULL,
    standby_hours REAL NOT NULL,
    maintenance_hours REAL NOT NULL,
    rig_available_hours REAL NOT NULL,
    PRIMARY KEY (date, job_id),
    FOREIGN KEY (job_id) REFERENCES drilling_jobs(job_id),
    FOREIGN KEY (well_id) REFERENCES wells(well_id),
    FOREIGN KEY (rig_id) REFERENCES rigs(rig_id)
);

CREATE TABLE cost_actuals (
    cost_id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    job_id TEXT NOT NULL,
    contractor_id TEXT NOT NULL,
    cost_category TEXT NOT NULL,
    actual_cost_cad REAL NOT NULL,
    FOREIGN KEY (job_id) REFERENCES drilling_jobs(job_id),
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id)
);

CREATE TABLE hse_events (
    hse_event_id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    job_id TEXT NOT NULL,
    contractor_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    recordable INTEGER NOT NULL,
    lost_time INTEGER NOT NULL,
    FOREIGN KEY (job_id) REFERENCES drilling_jobs(job_id),
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id)
);

CREATE TABLE npt_events (
    npt_event_id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    job_id TEXT NOT NULL,
    contractor_id TEXT NOT NULL,
    npt_category TEXT NOT NULL,
    npt_hours REAL NOT NULL,
    estimated_cost_impact_cad REAL NOT NULL,
    FOREIGN KEY (job_id) REFERENCES drilling_jobs(job_id),
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id)
);

CREATE TABLE calendar (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    week INTEGER NOT NULL,
    is_month_end INTEGER NOT NULL
);
