"""
Simple Fund Recommender
------------------------
Usage:
    python recommender.py Low
    python recommender.py Moderate
    python recommender.py High

Input : risk appetite (Low / Moderate / High)
Output: top 3 funds by Sharpe ratio within the matching risk_grade
"""
import sys
import pandas as pd

DATA_DIR = "../data/raw"

RISK_MAP = {
    "Low": ["Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High": ["High", "Very High"],
}


def load_scheme_performance(data_dir: str = DATA_DIR) -> pd.DataFrame:
    return pd.read_csv(f"{data_dir}/07_scheme_performance.csv")


def recommend_funds(risk_appetite: str, scheme_perf: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    if risk_appetite not in RISK_MAP:
        raise ValueError(f"risk_appetite must be one of {list(RISK_MAP)}, got {risk_appetite!r}")

    grades = RISK_MAP[risk_appetite]
    matched = scheme_perf[scheme_perf["risk_grade"].isin(grades)]
    top = matched.sort_values("sharpe_ratio", ascending=False).head(top_n)

    return top[[
        "scheme_name", "fund_house", "risk_grade",
        "sharpe_ratio", "return_3yr_pct", "std_dev_ann_pct"
    ]].reset_index(drop=True)


def print_recommendation_table(risk_appetite: str, data_dir: str = DATA_DIR) -> None:
    scheme_perf = load_scheme_performance(data_dir)
    result = recommend_funds(risk_appetite, scheme_perf)

    print(f"\nTop {len(result)} fund recommendations for '{risk_appetite}' risk appetite:\n")
    print(result.to_string(index=False))


if __name__ == "__main__":
    risk_appetite = sys.argv[1] if len(sys.argv) > 1 else "Moderate"
    print_recommendation_table(risk_appetite)
