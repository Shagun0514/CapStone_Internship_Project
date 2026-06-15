-- ============================================================
-- queries.sql  —  10 Analytical SQL Queries
-- Database: bluestock_mf.db
-- ============================================================

-- Q1: Top 5 Fund Houses by Latest AUM
SELECT fund_house,
       ROUND(SUM(aum_crore), 2)        AS total_aum_crore,
       ROUND(SUM(aum_lakh_crore), 4)   AS total_aum_lakh_crore
FROM   fact_aum
WHERE  date = (SELECT MAX(date) FROM fact_aum)
GROUP  BY fund_house
ORDER  BY total_aum_crore DESC
LIMIT  5;

-- Q2: Average NAV Per Month (across all funds)
SELECT  STRFTIME('%Y-%m', date)     AS month,
        ROUND(AVG(nav), 4)          AS avg_nav,
        COUNT(DISTINCT amfi_code)   AS num_funds
FROM    fact_nav
GROUP   BY month
ORDER   BY month;

-- Q3: SIP Inflow Year-on-Year Growth
SELECT  STRFTIME('%Y', month)       AS year,
        ROUND(SUM(sip_inflow_crore),2)  AS total_sip_crore,
        ROUND(AVG(yoy_growth_pct),2)    AS avg_yoy_growth_pct
FROM    fact_sip_inflows
GROUP   BY year
ORDER   BY year;

-- Q4: Transaction Volume by State
SELECT  state,
        COUNT(*)                    AS total_transactions,
        ROUND(SUM(amount_inr),2)    AS total_amount_inr,
        COUNT(DISTINCT investor_id) AS unique_investors
FROM    fact_transactions
GROUP   BY state
ORDER   BY total_transactions DESC;

-- Q5: Funds with Expense Ratio < 1% (cheapest funds)
SELECT  f.scheme_name,
        f.fund_house,
        f.category,
        p.expense_ratio_pct,
        p.sharpe_ratio,
        p.return_3yr_pct
FROM    dim_fund f
JOIN    fact_performance p ON f.amfi_code = p.amfi_code
WHERE   p.expense_ratio_pct < 1.0
ORDER   BY p.expense_ratio_pct ASC;

-- Q6: Top 5 Funds by 3-Year Return vs Benchmark (Alpha generators)
SELECT  f.scheme_name,
        f.fund_house,
        p.return_3yr_pct,
        p.benchmark_3yr_pct,
        ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS excess_return,
        p.alpha
FROM    dim_fund f
JOIN    fact_performance p ON f.amfi_code = p.amfi_code
ORDER   BY excess_return DESC
LIMIT   5;

-- Q7: Monthly SIP Transaction Count and Avg Ticket Size
SELECT  STRFTIME('%Y-%m', transaction_date)  AS month,
        COUNT(*)                              AS sip_count,
        ROUND(AVG(amount_inr), 2)            AS avg_ticket_inr,
        ROUND(SUM(amount_inr), 2)            AS total_inr
FROM    fact_transactions
WHERE   transaction_type = 'SIP'
GROUP   BY month
ORDER   BY month;

-- Q8: Risk-Return Matrix — Avg Sharpe by Risk Grade
SELECT  risk_grade,
        COUNT(*)                        AS num_funds,
        ROUND(AVG(sharpe_ratio),3)      AS avg_sharpe,
        ROUND(AVG(return_3yr_pct),2)    AS avg_3yr_return,
        ROUND(AVG(std_dev_ann_pct),2)   AS avg_volatility,
        ROUND(AVG(max_drawdown_pct),2)  AS avg_max_drawdown
FROM    fact_performance
GROUP   BY risk_grade
ORDER   BY avg_sharpe DESC;

-- Q9: Category Net Inflow Trend (last 6 months)
SELECT  month,
        category,
        ROUND(net_inflow_crore, 2)  AS net_inflow_crore
FROM    fact_category_inflows
WHERE   month >= (SELECT DATE(MAX(month), '-6 months') FROM fact_category_inflows)
ORDER   BY month DESC, net_inflow_crore DESC;

-- Q10: Investor Cohort Summary — Transactions per KYC Status
SELECT  kyc_status,
        transaction_type,
        COUNT(*)                    AS num_transactions,
        ROUND(AVG(amount_inr),2)    AS avg_amount,
        ROUND(SUM(amount_inr),2)    AS total_amount
FROM    fact_transactions
GROUP   BY kyc_status, transaction_type
ORDER   BY kyc_status, num_transactions DESC;
