# Bluestock Mutual Fund Analytics Platform

Capstone internship project — an end-to-end analytics platform covering 40 mutual fund schemes: ETL, a SQLite database, exploratory analysis, performance metrics, an interactive Power BI dashboard, and advanced risk analytics with a simple fund recommender.

## Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/           ← original downloaded files
│   ├── processed/     ← cleaned, merged CSVs
│   └── db/            ← bluestock_mf.db (SQLite)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/
│   ├── etl_pipeline.py
│   ├── live_nav_fetch.py
│   ├── compute_metrics.py
│   └── recommender.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── dashboard/
│   └── bluestock_mf.pbix
├── reports/
│   ├── Final_Report.pdf
│   └── Presentation.pptx
└── README.md
```

## Deliverables

| ID | Deliverable | Format | Weight |
|----|---|---|---|
| D1 | ETL pipeline script | `.py` | 15% |
| D2 | SQLite database | `.db` | 10% |
| D3 | EDA notebook | `.ipynb` | 15% |
| D4 | Performance metrics | `.ipynb` + CSVs | 15% |
| D5 | Interactive dashboard | `.pbix` | 20% |
| D6 | Advanced analytics | `.ipynb` | 10% |
| D7 | Final report + slides | `.pdf` + `.pptx` | 15% |

## Data Sources

- **fund_master** — 40 schemes: AMC, category, expense ratio, exit load, risk category
- **nav_history** — daily NAV records per scheme
- **scheme_performance** — trailing returns, alpha, beta, Sharpe, Sortino, risk grade
- **investor_transactions** — SIP / lumpsum / redemption transactions with demographics
- **portfolio_holdings** — stock-level sector weights per scheme
- **benchmark_indices** — NIFTY 50 and related index closes

## Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the ETL pipeline
```bash
python scripts/etl_pipeline.py
```
This loads raw CSVs from `data/raw/`, cleans and validates them, forward-fills NAV gaps on weekends/holidays, and writes cleaned output to `data/processed/`.

### 3. Build the database
The cleaned data is loaded into `data/db/bluestock_mf.db` following `sql/schema.sql`. Sample analytical queries are in `sql/queries.sql`.

### 4. Explore the notebooks
Run in order for the full analysis:
1. `01_data_ingestion.ipynb` — raw data loading and validation
2. `02_data_cleaning.ipynb` — cleaning, merging, DB load
3. `03_eda_analysis.ipynb` — 15-chart exploratory analysis
4. `04_performance_analytics.ipynb` — Sharpe, Beta, Alpha, drawdown
5. `05_advanced_analytics.ipynb` — VaR/CVaR, rolling Sharpe, cohorts, SIP continuity, recommender, sector HHI

### 5. Open the dashboard
Open `dashboard/bluestock_mf.pbix` in Power BI Desktop. Four pages: Industry Overview, Fund Performance (with NAV drill-through), Investor Analytics, SIP Trends.

### 6. Run the recommender
```bash
python scripts/recommender.py Moderate
```
Accepts `Low`, `Moderate`, or `High` as a risk appetite argument; returns the top 3 funds by Sharpe ratio in that risk band.

## Bonus Challenges Completed

| ID | Challenge | File(s) |
|----|---|---|
| B1 | Scheduled ETL — auto-fetch NAV every weekday at 8 PM | `scripts/schedule_nav_fetch.ps1`, `scripts/run_nav_fetch.bat` (Windows Task Scheduler) |
| B3 | Monte Carlo simulation — 5-year NAV projection with uncertainty bands | `notebooks/06_monte_carlo_simulation.ipynb`, `reports/monte_carlo_nav_projection.png`, `reports/monte_carlo_summary.csv` |
| B4 | Markowitz Efficient Frontier — portfolio optimization across 5 funds | `notebooks/07_efficient_frontier.ipynb`, `reports/efficient_frontier.png`, `reports/efficient_frontier_weights.csv` |
| B5 | Automated HTML email report — weekly performance summary | `scripts/email_report.py`, `reports/weekly_report.html` |

## Key Findings

- Small-cap funds carry the highest tail risk (VaR/CVaR); liquid funds the lowest — risk grades are empirically well-calibrated to realized volatility.
- ~98% of investors with 6+ SIP transactions show payment gaps beyond the 35-day continuity threshold, flagging a strong retention opportunity.
- Investor cohorts differ meaningfully in behavior: the 2024 cohort invests more per SIP and prefers equity; the 2025 cohort skews toward safer liquid funds.
- Several nominally "diversified" equity funds carry high sector concentration (HHI) — a hidden risk not visible from category labels alone.

## Notes on Methodology

- All annualization uses 252 trading days, not calendar days, to avoid overstating CAGR.
- NAV gaps on weekends/holidays are forward-filled after reindexing to the full trading calendar.
- The `.db` file is excluded from version control (see `.gitignore`); rebuild it locally via the ETL pipeline, or share `sql/schema.sql` to recreate the structure.
- AUM figures are labeled with explicit units (crore) in column names to avoid lakh/crore ambiguity.

## Author

Shagun — Capstone Internship Project
Repository: [github.com/Shagun0514/CapStone_Internship_Project](https://github.com/Shagun0514/CapStone_Internship_Project)
