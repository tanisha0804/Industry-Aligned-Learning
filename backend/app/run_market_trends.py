import json
from core.google_trends import fetch_trend_scores
from utils.skill_seed import load_primary_skills

skills = list(set(load_primary_skills().values()))

trend_scores = fetch_trend_scores(skills)

with open("backend/app/data/market_trends.json", "w") as f:
    json.dump(trend_scores, f, indent=2)

print("Market trend scores cached")
