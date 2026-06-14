"""
live_nav_fetch.py  —  Fetch live NAV from mfapi.in for 6 key schemes
"""
import requests, pandas as pd, os, time

SCHEMES = {
    125497: "HDFC Top 100 Direct",
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip",
}

BASE = "https://api.mfapi.in/mf/{}"
OUT  = "data/raw"
os.makedirs(OUT, exist_ok=True)

all_records = []

for code, name in SCHEMES.items():
    try:
        r = requests.get(BASE.format(code), timeout=10)
        r.raise_for_status()
        j = r.json()
        meta = j.get("meta", {})
        rows = j.get("data", [])
        df = pd.DataFrame(rows)
        df["amfi_code"]   = code
        df["scheme_name"] = name
        df = df.rename(columns={"date": "nav_date", "nav": "nav_value"})
        df = df[["amfi_code", "scheme_name", "nav_date", "nav_value"]]
        all_records.append(df)
        latest = rows[0] if rows else {}
        print(f"[OK] {name:25s} | latest NAV: {latest.get('nav','?')} on {latest.get('date','?')} | {len(rows)} records")
        time.sleep(0.3)
    except Exception as e:
        print(f"[ERR] {name}: {e}")

if all_records:
    combined = pd.concat(all_records, ignore_index=True)
    out_path = os.path.join(OUT, "live_nav_all_schemes.csv")
    combined.to_csv(out_path, index=False)
    print(f"\nSaved {len(combined):,} rows → {out_path}")
