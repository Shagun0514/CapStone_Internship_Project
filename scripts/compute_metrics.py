"""
day2_pipeline.py — Day 2: Clean all CSVs + load into SQLite
"""
import pandas as pd, numpy as np, sqlite3, os
from sqlalchemy import create_engine, text

RAW  = "data/raw"
PROC = "data/processed"
DB   = "bluestock_mf.db"
os.makedirs(PROC, exist_ok=True)

engine = create_engine(f"sqlite:///{DB}")

# ── 1. CLEAN nav_history ────────────────────────────────────────────────────
print("\n[1] Cleaning nav_history...")
nav = pd.read_csv(f"{RAW}/02_nav_history.csv")
nav["date"] = pd.to_datetime(nav["date"])
nav = nav.sort_values(["amfi_code","date"])
nav = nav.drop_duplicates(subset=["amfi_code","date"])
nav = nav[nav["nav"] > 0]
# forward-fill missing dates per fund
filled = []
for code, grp in nav.groupby("amfi_code"):
    grp = grp.set_index("date")["nav"]
    grp = grp.reindex(pd.date_range(grp.index.min(), grp.index.max(), freq="D")).ffill()
    tmp = grp.reset_index()
    tmp.columns = ["date", "nav"]
    tmp["amfi_code"] = code
    filled.append(tmp)
nav = pd.concat(filled, ignore_index=True)[["amfi_code","date","nav"]]
nav.to_csv(f"{PROC}/02_nav_history_clean.csv", index=False)
print(f"   nav_history: {len(nav):,} rows (after ffill)")

# ── 2. CLEAN investor_transactions ──────────────────────────────────────────
print("\n[2] Cleaning investor_transactions...")
txn = pd.read_csv(f"{RAW}/08_investor_transactions.csv")
txn["transaction_date"] = pd.to_datetime(txn["transaction_date"])
# standardise transaction_type
type_map = {
    "sip":"SIP","Sip":"SIP","SIP":"SIP",
    "lumpsum":"Lumpsum","Lumpsum":"Lumpsum","LUMPSUM":"Lumpsum",
    "redemption":"Redemption","Redemption":"Redemption","REDEMPTION":"Redemption",
}
txn["transaction_type"] = txn["transaction_type"].map(type_map).fillna(txn["transaction_type"])
txn = txn[txn["amount_inr"] > 0]
valid_kyc = {"KYC Verified","KYC Pending","KYC Rejected"}
kyc_anomalies = txn[~txn["kyc_status"].isin(valid_kyc)]
if len(kyc_anomalies): print(f"   KYC anomalies: {len(kyc_anomalies)} rows")
txn.to_csv(f"{PROC}/08_investor_transactions_clean.csv", index=False)
print(f"   transactions: {len(txn):,} rows")

# ── 3. CLEAN scheme_performance ─────────────────────────────────────────────
print("\n[3] Cleaning scheme_performance...")
perf = pd.read_csv(f"{RAW}/07_scheme_performance.csv")
return_cols = ["return_1yr_pct","return_3yr_pct","return_5yr_pct",
               "benchmark_3yr_pct","alpha","beta","sharpe_ratio","sortino_ratio"]
for c in return_cols:
    perf[c] = pd.to_numeric(perf[c], errors="coerce")
# flag expense ratio anomalies
perf["expense_flag"] = perf["expense_ratio_pct"].apply(
    lambda x: "ANOMALY" if not (0.1 <= x <= 2.5) else "OK")
anomalies = perf[perf["expense_flag"]=="ANOMALY"]
if len(anomalies): print(f"   Expense ratio anomalies:\n{anomalies[['scheme_name','expense_ratio_pct']]}")
else: print("   Expense ratios all within 0.1–2.5% ✓")
perf.to_csv(f"{PROC}/07_scheme_performance_clean.csv", index=False)
print(f"   scheme_performance: {len(perf)} rows")

# ── 4. CLEAN remaining CSVs ─────────────────────────────────────────────────
print("\n[4] Cleaning remaining CSVs...")

fm = pd.read_csv(f"{RAW}/01_fund_master.csv")
fm.to_csv(f"{PROC}/01_fund_master_clean.csv", index=False)

aum = pd.read_csv(f"{RAW}/03_aum_by_fund_house.csv")
aum["date"] = pd.to_datetime(aum["date"])
aum.to_csv(f"{PROC}/03_aum_by_fund_house_clean.csv", index=False)

sip = pd.read_csv(f"{RAW}/04_monthly_sip_inflows.csv")
sip["month"] = pd.to_datetime(sip["month"])
sip.to_csv(f"{PROC}/04_monthly_sip_inflows_clean.csv", index=False)

cat = pd.read_csv(f"{RAW}/05_category_inflows.csv")
cat["month"] = pd.to_datetime(cat["month"])
cat.to_csv(f"{PROC}/05_category_inflows_clean.csv", index=False)

hld = pd.read_csv(f"{RAW}/09_portfolio_holdings.csv")
hld.to_csv(f"{PROC}/09_portfolio_holdings_clean.csv", index=False)

print("   All remaining CSVs cleaned and saved.")

# ── 5. LOAD INTO SQLITE ─────────────────────────────────────────────────────
print("\n[5] Loading into SQLite...")

with engine.connect() as con:
    con.execute(text("PRAGMA foreign_keys = ON"))

fm.to_sql("dim_fund", engine, if_exists="replace", index=False)
print(f"   dim_fund: {len(fm)} rows")

# dim_date from nav dates
dates = nav[["date"]].drop_duplicates().copy()
dates["year"]    = dates["date"].dt.year
dates["month"]   = dates["date"].dt.month
dates["quarter"] = dates["date"].dt.quarter
dates["weekday"] = dates["date"].dt.day_name()
dates.to_sql("dim_date", engine, if_exists="replace", index=False)
print(f"   dim_date: {len(dates)} rows")

nav.to_sql("fact_nav", engine, if_exists="replace", index=False)
print(f"   fact_nav: {len(nav):,} rows")

txn.to_sql("fact_transactions", engine, if_exists="replace", index=False)
print(f"   fact_transactions: {len(txn):,} rows")

perf.to_sql("fact_performance", engine, if_exists="replace", index=False)
print(f"   fact_performance: {len(perf)} rows")

aum.to_sql("fact_aum", engine, if_exists="replace", index=False)
print(f"   fact_aum: {len(aum)} rows")

sip.to_sql("fact_sip_inflows", engine, if_exists="replace", index=False)
cat.to_sql("fact_category_inflows", engine, if_exists="replace", index=False)
hld.to_sql("fact_holdings", engine, if_exists="replace", index=False)

print("\n✅ All tables loaded into bluestock_mf.db")

# ── 6. VERIFY ROW COUNTS ────────────────────────────────────────────────────
print("\n[6] Row count verification:")
tables = ["dim_fund","dim_date","fact_nav","fact_transactions",
          "fact_performance","fact_aum","fact_sip_inflows",
          "fact_category_inflows","fact_holdings"]
with engine.connect() as con:
    for t in tables:
        n = con.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"   {t:30s}: {n:,}")
