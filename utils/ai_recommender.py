import json
from pathlib import Path

try:
    from utils.mistral_client import ask
    from utils.insight_engine import load_survey, detect_risks
except ImportError:
    from mistral_client import ask
    from insight_engine import load_survey, detect_risks

RECOMMENDATIONS_CACHE = Path("data/recommendations_cache.json")

FALLBACK_RECOMMENDATION = {
    "headline": "This dimension requires leadership attention.",
    "why_it_matters": (
        "Low scores in this area are linked to reduced engagement and higher turnover. "
        "Employees may feel unsupported or undervalued. Early action prevents escalation."
    ),
    "actions": [
        {"action": "Conduct a focused team check-in to surface specific concerns.", "effort": "low", "impact": "medium", "timeline_weeks": 1},
        {"action": "Review workload distribution and adjust task assignments with the team lead.", "effort": "medium", "impact": "high", "timeline_weeks": 3},
        {"action": "Schedule a follow-up survey in 4 weeks to measure improvement.", "effort": "low", "impact": "medium", "timeline_weeks": 4},
    ],
}


def build_prompt(risk: dict, company_size: int) -> str:
    return (
        f"You are an HR consultant advising a Latvian manufacturing company with {company_size} employees.\n"
        f"Survey data shows a risk in team '{risk['team']}' on dimension '{risk['dimension']}'.\n"
        f"Mean score: {risk['mean_score']} out of 5 (severity delta from threshold: {risk['severity']}).\n"
        f"Team size: {risk['employee_count']} employees.\n\n"
        f"Generate 3 concrete, practical action recommendations tailored to a Latvian manufacturing context.\n"
        f"Respond ONLY with valid JSON, no markdown fences, no preamble.\n"
        f"Use this exact JSON structure:\n"
        f'{{\n'
        f'  "headline": "one short sentence describing the issue",\n'
        f'  "why_it_matters": "2-3 sentence explanation",\n'
        f'  "actions": [\n'
        f'    {{"action": "...", "effort": "low|medium|high", "impact": "low|medium|high", "timeline_weeks": <int>}},\n'
        f'    {{"action": "...", "effort": "low|medium|high", "impact": "low|medium|high", "timeline_weeks": <int>}},\n'
        f'    {{"action": "...", "effort": "low|medium|high", "impact": "low|medium|high", "timeline_weeks": <int>}}\n'
        f'  ]\n'
        f'}}'
    )


def get_recommendation(risk: dict, company_size: int = 100) -> dict:
    prompt = build_prompt(risk, company_size)
    raw = ask(prompt)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        print("[ai_recommender] JSON parse failed, using fallback")
        return FALLBACK_RECOMMENDATION.copy()


def generate_all_recommendations(risks: list[dict], company_size: int = 100) -> list[dict]:
    results = []
    for i, risk in enumerate(risks):
        print(f"[ai_recommender] {i+1}/{len(risks)}: {risk['team']}/{risk['dimension']}")
        rec = get_recommendation(risk, company_size)
        results.append({**risk, **rec})
    return results


if __name__ == "__main__":
    df = load_survey()
    risks = detect_risks(df, top_n=5)
    print(f"Detected {len(risks)} risks. Generating recommendations...\n")

    results = generate_all_recommendations(risks, company_size=80)

    for r in results:
        print(f"\n{'='*60}")
        print(f"Team: {r['team']} | Dimension: {r['dimension']} | Score: {r['mean_score']}")
        print(f"Headline: {r['headline']}")
        print(f"Why it matters: {r['why_it_matters']}")
        for j, a in enumerate(r["actions"], 1):
            print(f"  Action {j}: {a['action']}")
            print(f"    Effort: {a['effort']} | Impact: {a['impact']} | Timeline: {a['timeline_weeks']}w")

    RECOMMENDATIONS_CACHE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved to {RECOMMENDATIONS_CACHE}")
