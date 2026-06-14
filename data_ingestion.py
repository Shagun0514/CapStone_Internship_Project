"""
data_ingestion.py  —  Day 1: Load & inspect all datasets
"""
import pandas as pd
import os

RAW = "data/raw"

FILES = {
    "fund_master":    "01_fund_master.csv",
    "nav_history":    "02_nav_history.csv",
    "transactions":   "08_investor_transactions.csv",
    "holdings":       "09_portfolio_holdings.csv",
}

dfs = {}
anomalies = []

for name, fname in FILES.items():
    path = os.path.join(RAW, fname)
    df = pd.read_csv(path)
    dfs[name] = df
    print(f"\n{'='*55}")
    print(f"  {name}  |  shape: {df.shape}")
    print(f"{'='*55}")
    print(df.dtypes)
    print("\nHead:")
    print(df.head(3).to_string())
    nulls = df.isnull().sum()
    if nulls.any():
        anomalies.append(f"{name}: nulls in {nulls[nulls>0].to_dict()}")
    dups = df.duplicated().sum()
    if dups:
        anomalies.append(f"{name}: {dups} duplicate rows")

# AMFI code validation
fm_codes  = set(dfs["fund_master"]["amfi_code"])
nav_codes = set(dfs["nav_history"]["amfi_code"])
missing   = fm_codes - nav_codes
if missing:
    anomalies.append(f"AMFI codes in fund_master but missing in nav_history: {missing}")

print("\n\n=== DATA QUALITY SUMMARY ===")
if anomalies:
    for a in anomalies:
        print(" !", a)
else:
    print("  No anomalies detected. All datasets clean.")

print(f"\nFund houses  : {dfs['fund_master']['fund_house'].nunique()}")
print(f"Categories   : {dfs['fund_master']['category'].unique().tolist()}")
print(f"Sub-cats     : {dfs['fund_master']['sub_category'].nunique()}")
print(f"Risk grades  : {dfs['fund_master']['risk_category'].unique().tolist()}")
print(f"NAV rows     : {len(dfs['nav_history']):,}")
print(f"Txn rows     : {len(dfs['transactions']):,}")
print(f"Holdings rows: {len(dfs['holdings']):,}")
