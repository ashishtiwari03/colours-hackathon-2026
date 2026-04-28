"""Generate MetalWorks Latvia wellbeing survey CSV with realistic patterns."""
import csv
import random
from pathlib import Path

random.seed(42)  # reproducible

# Team profiles: (team_name, count, dimension_means)
# Means are intentionally crafted to tell the demo story
TEAMS = {
    "Production": {
        "count": 40,
        "means": {
            "workload_manageability": 2.1,
            "recognition": 2.4,
            "communication": 2.6,
            "manager_support": 2.3,
            "growth": 2.8,
            "autonomy": 2.7,
            "social_connection": 3.5,  # they bond with each other, that's why they stay
            "burnout_risk": 4.2,        # high risk
        },
    },
    "Engineering": {
        "count": 25,
        "means": {
            "workload_manageability": 3.0,
            "recognition": 2.6,
            "communication": 3.2,
            "manager_support": 3.4,
            "growth": 3.8,
            "autonomy": 4.0,
            "social_connection": 3.3,
            "burnout_risk": 3.4,
        },
    },
    "Sales": {
        "count": 15,
        "means": {
            "workload_manageability": 3.6,
            "recognition": 4.0,
            "communication": 3.8,
            "manager_support": 3.9,
            "growth": 3.7,
            "autonomy": 3.8,
            "social_connection": 4.1,
            "burnout_risk": 2.6,
        },
    },
    "HR": {
        "count": 10,
        "means": {
            "workload_manageability": 3.8,
            "recognition": 3.7,
            "communication": 4.0,
            "manager_support": 4.1,
            "growth": 3.5,
            "autonomy": 3.9,
            "social_connection": 4.0,
            "burnout_risk": 2.4,
        },
    },
    "Management": {
        "count": 10,
        "means": {
            "workload_manageability": 3.5,
            "recognition": 3.8,
            "communication": 3.6,
            "manager_support": 3.7,
            "growth": 4.0,
            "autonomy": 4.3,
            "social_connection": 3.6,
            "burnout_risk": 2.9,
        },
    },
}

DIMENSIONS = [
    "workload_manageability",
    "recognition",
    "communication",
    "manager_support",
    "growth",
    "autonomy",
    "social_connection",
    "burnout_risk",
]


def likert_around(mean: float, spread: float = 0.7) -> int:
    """Return an integer 1-5 normally distributed around mean."""
    value = random.gauss(mean, spread)
    return max(1, min(5, round(value)))


def generate_rows() -> list[dict]:
    rows = []
    employee_id = 1
    for team_name, profile in TEAMS.items():
        for _ in range(profile["count"]):
            row = {
                "employee_id": f"E{employee_id:03d}",
                "team": team_name,
                "tenure_years": random.choice([1, 1, 2, 2, 3, 3, 4, 5, 7, 10]),
                "remote_share": random.choice([0, 0, 25, 50, 50, 75, 100]),
            }
            for dim in DIMENSIONS:
                row[dim] = likert_around(profile["means"][dim])
            rows.append(row)
            employee_id += 1
    return rows


def main():
    rows = generate_rows()
    output_path = Path("data") / "survey_responses.csv"
    output_path.parent.mkdir(exist_ok=True)
    fieldnames = ["employee_id", "team", "tenure_years", "remote_share"] + DIMENSIONS
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} rows → {output_path}")
    print("\nQuick sanity check (means by team):")
    for team_name in TEAMS:
        team_rows = [r for r in rows if r["team"] == team_name]
        workload = sum(r["workload_manageability"] for r in team_rows) / len(team_rows)
        burnout = sum(r["burnout_risk"] for r in team_rows) / len(team_rows)
        print(f"  {team_name:12s} workload={workload:.2f}  burnout_risk={burnout:.2f}")


if __name__ == "__main__":
    main()