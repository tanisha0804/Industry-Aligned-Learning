import json
from pathlib import Path

BASE_DATA = Path("backend/app/data")
def smooth_market_trends(trends: dict, min_value: float = 0.25):
    for skill in trends:
        if trends[skill] < min_value:
            trends[skill] = min_value
    return trends


def compute_industry_demand(
    jd_skills: list,
    market_trends: dict,
    alpha: float = 0.6,
    beta: float = 0.4
):

    demand = {}
    for skill in jd_skills:
        jd_score = 1.0
        market_score = market_trends.get(skill, 0.25)

        demand[skill] = alpha * jd_score + beta * market_score

    total = sum(demand.values())
    for skill in demand:
        demand[skill] /= total

    return dict(sorted(demand.items(), key=lambda x: x[1], reverse=True))



