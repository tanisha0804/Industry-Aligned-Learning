import json
from pathlib import Path

BASE_DATA = Path("backend/app/data")

def compute_industry_demand(
    jd_skills: list,
    market_trends: dict,
    alpha=0.6,
    beta=0.4
):
    demand = {}

    for skill in jd_skills:
        jd_score = 1.0  # presence-based
        market_score = market_trends.get(skill, 0.3)
        demand[skill] = alpha * jd_score + beta * market_score

    total = sum(demand.values())
    for s in demand:
        demand[s] /= total
    return dict(sorted(demand.items(), key=lambda x: x[1], reverse=True))
