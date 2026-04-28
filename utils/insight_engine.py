from pathlib import Path
import pandas as pd

SURVEY_PATH = Path("data/survey_responses.csv")
RISK_THRESHOLD = 3.0

DIMENSIONS = [
    "workload_manageability", "recognition", "communication",
    "manager_support", "growth", "autonomy", "social_connection", "burnout_risk",
]


def load_survey() -> pd.DataFrame:
    return pd.read_csv(SURVEY_PATH)


def team_dimension_means(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for team, grp in df.groupby("team"):
        count = len(grp)
        for dim in DIMENSIONS:
            rows.append({
                "team": team,
                "dimension": dim,
                "mean_score": round(grp[dim].mean(), 3),
                "employee_count": count,
            })
    return pd.DataFrame(rows)


def detect_risks(df: pd.DataFrame, top_n: int = 5) -> list[dict]:
    means = team_dimension_means(df)
    risks = []
    for _, row in means.iterrows():
        dim, score = row["dimension"], row["mean_score"]
        at_risk = (
            (dim != "burnout_risk" and score < RISK_THRESHOLD) or
            (dim == "burnout_risk" and score > 3.5)
        )
        if at_risk:
            threshold = 3.5 if dim == "burnout_risk" else RISK_THRESHOLD
            risks.append({
                "team": row["team"],
                "dimension": dim,
                "mean_score": score,
                "employee_count": row["employee_count"],
                "severity": round(abs(score - threshold), 3),
            })
    risks.sort(key=lambda r: r["severity"], reverse=True)
    return risks[:top_n]


def company_summary(df: pd.DataFrame) -> dict:
    non_burnout = [d for d in DIMENSIONS if d != "burnout_risk"]
    return {
        "total_employees": len(df),
        "num_teams": df["team"].nunique(),
        "overall_mean_excluding_burnout": round(df[non_burnout].values.mean(), 3),
        "overall_burnout_mean": round(df["burnout_risk"].mean(), 3),
    }


if __name__ == "__main__":
    df = load_survey()
    summary = company_summary(df)
    print("=== Company Summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    means = team_dimension_means(df)
    print(f"\n=== Team × Dimension Means ({len(means)} rows) ===")
    print(means.to_string(index=False))

    risks = detect_risks(df, top_n=5)
    print("\n=== Top 5 Risks ===")
    for r in risks:
        print(f"  [{r['severity']:+.2f}] {r['team']} / {r['dimension']} = {r['mean_score']} (n={r['employee_count']})")
