# Data Dictionary — Bluestock Mutual Fund Analytics
**Database:** `bluestock_mf.db` | **Last Updated:** June 2025

---

## Table: `dim_fund` (Dimension)
**Source:** `01_fund_master.csv`  
**Description:** Master reference for all 40 mutual fund schemes.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| amfi_code | INTEGER (PK) | Unique AMFI scheme code assigned by SEBI | 119551 |
| scheme_name | TEXT | Full official name of the scheme | SBI Bluechip Fund - Regular Plan |
| fund_house | TEXT | Name of the Asset Management Company | SBI Mutual Fund |
| category | TEXT | Broad SEBI category | Equity, Debt, Hybrid |
| sub_category | TEXT | SEBI sub-category | Large Cap, Mid Cap, Liquid |
| plan | TEXT | Direct or Regular plan | Direct, Regular |
| risk_category | TEXT | Risk grade per SEBI riskometer | Low, Moderate, High |
| benchmark_index | TEXT | Benchmark index for performance comparison | Nifty 100 TRI |
| launch_date | TEXT | Date the scheme was launched | 2013-01-01 |
| expense_ratio_pct | REAL | Annual expense ratio charged to investors (%) | 1.54 |
| aum_crore | REAL | Assets Under Management in ₹ Crore | 14288 |
| morningstar_rating | INTEGER | Morningstar star rating (1–5) | 4 |

---

## Table: `dim_date` (Dimension)
**Source:** Derived from `fact_nav` dates  
**Description:** Date dimension for time-series analysis.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| date | TEXT (PK) | Calendar date in YYYY-MM-DD format | 2024-01-15 |
| year | INTEGER | Calendar year | 2024 |
| month | INTEGER | Month number (1–12) | 1 |
| quarter | INTEGER | Quarter (1–4) | 1 |
| weekday | TEXT | Day of week name | Monday |

---

## Table: `fact_nav` (Fact)
**Source:** `02_nav_history.csv`  
**Description:** Daily NAV for all schemes. Forward-filled for holidays/weekends.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| nav_id | INTEGER (PK) | Auto-increment surrogate key | 1 |
| amfi_code | INTEGER (FK) | References dim_fund.amfi_code | 119551 |
| date | TEXT (FK) | References dim_date.date | 2024-01-15 |
| nav | REAL | Net Asset Value in ₹ per unit (must be > 0) | 78.43 |

---

## Table: `fact_transactions` (Fact)
**Source:** `08_investor_transactions.csv`  
**Description:** All investor buy/sell transactions. Cleaned and standardised.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| transaction_id | TEXT (PK) | Unique transaction identifier | TXN00001 |
| investor_id | TEXT | Unique investor identifier | INV001 |
| amfi_code | INTEGER (FK) | References dim_fund.amfi_code | 119551 |
| transaction_date | TEXT | Date of transaction (YYYY-MM-DD) | 2024-01-10 |
| transaction_type | TEXT | Standardised type: SIP / Lumpsum / Redemption | SIP |
| amount_inr | REAL | Transaction amount in ₹ (must be > 0) | 5000.00 |
| units | REAL | Units purchased or redeemed | 63.87 |
| nav_at_transaction | REAL | NAV at time of transaction | 78.28 |
| kyc_status | TEXT | KYC compliance status | KYC Verified |
| state | TEXT | Investor's state of residence | Maharashtra |

---

## Table: `fact_performance` (Fact)
**Source:** `07_scheme_performance.csv`  
**Description:** Risk-return metrics for all 40 schemes.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| amfi_code | INTEGER (PK/FK) | References dim_fund.amfi_code | 119551 |
| return_1yr_pct | REAL | 1-year trailing return (%) | 12.42 |
| return_3yr_pct | REAL | 3-year CAGR (%) | 12.36 |
| return_5yr_pct | REAL | 5-year CAGR (%) | 14.45 |
| benchmark_3yr_pct | REAL | Benchmark 3-year CAGR (%) | 11.49 |
| alpha | REAL | Excess return vs benchmark (Jensen's Alpha) | 0.87 |
| beta | REAL | Market sensitivity (1.0 = market-neutral) | 0.89 |
| sharpe_ratio | REAL | Risk-adjusted return (higher = better) | 0.88 |
| sortino_ratio | REAL | Downside risk-adjusted return | 1.29 |
| std_dev_ann_pct | REAL | Annualised standard deviation of returns (%) | 14.0 |
| max_drawdown_pct | REAL | Maximum peak-to-trough decline (%) | -21.70 |
| expense_ratio_pct | REAL | Annual fee (valid range: 0.1%–2.5%) | 1.54 |
| expense_flag | TEXT | OK or ANOMALY (outside valid range) | OK |
| risk_grade | TEXT | SEBI riskometer risk level | Moderate |

---

## Table: `fact_aum` (Fact)
**Source:** `03_aum_by_fund_house.csv`  
**Description:** Monthly AUM snapshots per fund house.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| aum_id | INTEGER (PK) | Auto-increment surrogate key | 1 |
| date | TEXT | Reporting date (end of month) | 2024-03-31 |
| fund_house | TEXT | Name of the AMC | SBI Mutual Fund |
| aum_lakh_crore | REAL | AUM in Lakh Crore ₹ | 6.05 |
| aum_crore | REAL | AUM in Crore ₹ | 605000 |
| num_schemes | INTEGER | Number of active schemes | 186 |

---

## Table: `fact_sip_inflows` (Fact)
**Source:** `04_monthly_sip_inflows.csv`  
**Description:** Industry-level monthly SIP flow statistics.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| month | TEXT (PK) | Month in YYYY-MM format | 2024-01 |
| sip_inflow_crore | REAL | Total SIP inflows in ₹ Crore | 18838 |
| active_sip_accounts_crore | REAL | Active SIP accounts (in Crore units) | 7.91 |
| new_sip_accounts_lakh | REAL | New SIP registrations (in Lakh units) | 49.6 |
| sip_aum_lakh_crore | REAL | SIP AUM in Lakh Crore ₹ | 10.26 |
| yoy_growth_pct | REAL | Year-on-year growth in SIP inflows (%) | 24.5 |

---

## Table: `fact_category_inflows` (Fact)
**Source:** `05_category_inflows.csv`  
**Description:** Monthly net inflows by fund category.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INTEGER (PK) | Auto-increment surrogate key | 1 |
| month | TEXT | Month in YYYY-MM format | 2024-04 |
| category | TEXT | Fund category name | Large Cap |
| net_inflow_crore | REAL | Net inflow (positive = buy, negative = redemption) | 2413.0 |

---

## Data Quality Rules
| Rule | Table | Column | Constraint |
|------|-------|--------|------------|
| NAV must be positive | fact_nav | nav | nav > 0 |
| Amount must be positive | fact_transactions | amount_inr | amount_inr > 0 |
| Valid transaction types only | fact_transactions | transaction_type | IN ('SIP','Lumpsum','Redemption') |
| Expense ratio in valid range | fact_performance | expense_ratio_pct | 0.1% – 2.5% |
| No duplicate NAV records | fact_nav | amfi_code + date | UNIQUE |
| KYC must be valid enum | fact_transactions | kyc_status | IN ('KYC Verified','KYC Pending','KYC Rejected') |
