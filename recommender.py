"""
recommender.py  —  Simple fund recommender by risk appetite
Usage: python recommender.py --risk Low|Moderate|High
"""
import pandas as pd, numpy as np, argparse, os

RAW = "data/raw"

def compute_sharpe(nav_df, amfi_code):
    df = nav_df[nav_df["amfi_code"] == amfi_code].copy()
    df = df.sort_values("date")
    df["return"] = df["nav"].pct_change()
    df = df.dropna()
    if len(df) < 30:
        return np.nan
    mu  = df["return"].mean() * 252
    sig = df["return"].std()  * np.sqrt(252)
    return mu / sig if sig > 0 else np.nan

def recommend(risk: str):
    risk = risk.strip().capitalize()
    valid = {"Low", "Moderate", "High"}
    if risk not in valid:
        print(f"Invalid risk. Choose from: {valid}")
        return

    fm  = pd.read_csv(os.path.join(RAW, "01_fund_master.csv"))
    nav = pd.read_csv(os.path.join(RAW, "02_nav_history.csv"), parse_dates=["date"])

    subset = fm[fm["risk_category"] == risk].copy()
    if subset.empty:
        print(f"No funds found for risk_category='{risk}'")
        return

    subset["sharpe"] = subset["amfi_code"].apply(lambda c: compute_sharpe(nav, c))
    subset = subset.dropna(subset=["sharpe"])
    top3   = subset.nlargest(3, "sharpe")[
        ["amfi_code", "scheme_name", "fund_house", "sub_category", "expense_ratio_pct", "sharpe"]
    ].reset_index(drop=True)
    top3.index += 1

    print(f"\n{'='*60}")
    print(f"  Top 3 Funds for Risk Appetite: {risk}")
    print(f"{'='*60}")
    print(top3.to_string())
    print()
    return top3

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--risk", default="Moderate", help="Low | Moderate | High")
    args = parser.parse_args()
    recommend(args.risk)
