-- ============================================================
-- bluestock_mf.db  —  Star Schema DDL
-- Day 2: Mutual Fund Analytics
-- ============================================================

PRAGMA foreign_keys = ON;

-- DIMENSION: Fund Master
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    scheme_name         TEXT    NOT NULL,
    fund_house          TEXT    NOT NULL,
    category            TEXT    NOT NULL,
    sub_category        TEXT,
    plan                TEXT,
    risk_category       TEXT,
    benchmark_index     TEXT,
    launch_date         TEXT,
    expense_ratio_pct   REAL,
    aum_crore           REAL,
    morningstar_rating  INTEGER
);

-- DIMENSION: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date        TEXT    PRIMARY KEY,
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    quarter     INTEGER NOT NULL,
    weekday     TEXT    NOT NULL
);

-- FACT: Daily NAV
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   INTEGER NOT NULL,
    date        TEXT    NOT NULL,
    nav         REAL    NOT NULL CHECK (nav > 0),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date)      REFERENCES dim_date(date)
);

-- FACT: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id      TEXT    PRIMARY KEY,
    investor_id         TEXT    NOT NULL,
    amfi_code           INTEGER NOT NULL,
    transaction_date    TEXT    NOT NULL,
    transaction_type    TEXT    NOT NULL CHECK (transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount_inr          REAL    NOT NULL CHECK (amount_inr > 0),
    units               REAL,
    nav_at_transaction  REAL,
    kyc_status          TEXT,
    state               TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: Scheme Performance
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code           INTEGER PRIMARY KEY,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    expense_ratio_pct   REAL CHECK (expense_ratio_pct BETWEEN 0.1 AND 2.5),
    expense_flag        TEXT,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: AUM by Fund House
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date                TEXT    NOT NULL,
    fund_house          TEXT    NOT NULL,
    aum_lakh_crore      REAL,
    aum_crore           REAL,
    num_schemes         INTEGER
);

-- FACT: Monthly SIP Inflows
CREATE TABLE IF NOT EXISTS fact_sip_inflows (
    month                       TEXT    PRIMARY KEY,
    sip_inflow_crore            REAL,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);

-- FACT: Category Inflows
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    month           TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    net_inflow_crore REAL
);
