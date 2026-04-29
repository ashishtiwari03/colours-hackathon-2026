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

SECTORS = {
    "manufacturing": {
        "company_name": "MetalWorks Latvia",
        "company_size": 100,
        "target_team": "Production",
        "teams_trajectory": {
            "Production":  (3.21, 2.72),
            "Engineering": (3.44, 3.20),
            "Sales":       (3.67, 3.80),
            "HR":          (3.93, 4.00),
            "Management":  (3.65, 3.70),
        },
        "projection": {
            "workload_manageability": (2.30, 3.40),
            "recognition":            (2.55, 3.35),
            "communication":          (2.55, 3.10),
            "manager_support":        (2.55, 3.50),
            "growth":                 (2.95, 3.20),
            "autonomy":               (2.53, 3.10),
            "social_connection":      (3.58, 3.80),
            "burnout_risk":           (4.25, 3.20),
        },
    },
    "it": {
        "company_name": "TechRiga",
        "company_size": 80,
        "target_team": "Engineering",
        "teams_trajectory": {
            "Engineering": (3.30, 2.80),
            "QA":          (3.40, 3.20),
            "Product":     (3.70, 3.80),
            "Sales":       (3.65, 3.70),
            "Operations":  (3.55, 3.65),
        },
        "projection": {
            "workload_manageability": (2.26, 3.30),
            "recognition":            (3.20, 3.50),
            "communication":          (2.70, 3.20),
            "manager_support":        (2.90, 3.40),
            "growth":                 (3.50, 3.70),
            "autonomy":               (2.40, 3.20),
            "social_connection":      (2.80, 3.30),
            "burnout_risk":           (4.46, 3.40),
        },
    },
}


def build_historical_trend(sector_key: str = "manufacturing") -> pd.DataFrame:
    rng = random.Random(42)
    rows = []
    for team, (start, end) in SECTORS[sector_key]["teams_trajectory"].items():
        for i, month in enumerate(_MONTHS):
            t = i / (HISTORICAL_MONTHS - 1)
            base = start + t * (end - start)
            score = round(base + rng.uniform(-0.05, 0.05), 2)
            rows.append({"month": month, "team": team, "wellbeing_score": score})
    return pd.DataFrame(rows)


def build_projection(sector_key: str = "manufacturing") -> pd.DataFrame:
    rows = [
        {"dimension": dim, "current_score": cur, "projected_score": proj}
        for dim, (cur, proj) in SECTORS[sector_key]["projection"].items()
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
    for key in SECTORS:
        print(f"\n=== {key.upper()} ===")
        print(f"Company: {SECTORS[key]['company_name']} ({SECTORS[key]['company_size']} employees)")
        hist = build_historical_trend(key)
        print(f"\nHistorical (last row per team):")
        for team in SECTORS[key]['teams_trajectory']:
            last = hist[hist['team'] == team].iloc[-1]
            print(f"  {team:12s} {last['wellbeing_score']:.2f}")
        proj = build_projection(key)
        print(f"\nProjection:")
        print(proj.to_string(index=False))
