import random
import pandas as pd

TEAMS = ["Production", "Engineering", "Sales", "HR", "Management"]
DIMENSIONS = [
    "workload_manageability", "recognition", "communication", "manager_support",
    "growth", "autonomy", "social_connection", "burnout_risk",
]
HISTORICAL_MONTHS = 6
PROJECTION_WEEKS = 12

_MONTHS = ["Oct 2025", "Nov 2025", "Dec 2025", "Jan 2026", "Feb 2026", "Mar 2026"]

# (start, end) wellbeing scores per team
_TRAJECTORIES = {
    "Production":  (3.2, 2.7),
    "Engineering": (3.4, 3.2),
    "Sales":       (3.7, 3.8),
    "HR":          (3.9, 4.0),
    "Management":  (3.6, 3.7),
}

_PROJECTION_DATA = {
    "workload_manageability": (2.30, 3.40),
    "recognition":            (2.55, 3.35),
    "communication":          (2.55, 3.10),
    "manager_support":        (2.55, 3.50),
    "growth":                 (2.95, 3.20),
    "autonomy":               (2.53, 3.10),
    "social_connection":      (3.58, 3.80),
    "burnout_risk":           (4.25, 3.20),
}


def build_historical_trend() -> pd.DataFrame:
    rng = random.Random(42)
    rows = []
    for team, (start, end) in _TRAJECTORIES.items():
        for i, month in enumerate(_MONTHS):
            t = i / (HISTORICAL_MONTHS - 1)
            base = start + t * (end - start)
            score = round(base + rng.uniform(-0.05, 0.05), 2)
            rows.append({"month": month, "team": team, "wellbeing_score": score})
    return pd.DataFrame(rows)


def build_projection() -> pd.DataFrame:
    rows = [
        {"dimension": dim, "current_score": cur, "projected_score": proj}
        for dim, (cur, proj) in _PROJECTION_DATA.items()
    ]
    return pd.DataFrame(rows)


def roi_calculation(company_size: int = 100) -> dict:
    annual_inaction_cost = int(1.5 * 12_000 * company_size / 100)
    pulseact_annual_cost = 6_000
    net_savings = annual_inaction_cost - pulseact_annual_cost
    payback_months = round(pulseact_annual_cost / (annual_inaction_cost / 12))
    return {
        "annual_inaction_cost": annual_inaction_cost,
        "pulseact_annual_cost": pulseact_annual_cost,
        "net_savings": net_savings,
        "payback_months": payback_months,
    }


if __name__ == "__main__":
    print("--- Historical trend (first 10 rows) ---")
    print(build_historical_trend().head(10).to_string(index=False))
    print("\n--- Projection ---")
    print(build_projection().to_string(index=False))
    print("\n--- ROI (80 employees) ---")
    print(roi_calculation(80))
