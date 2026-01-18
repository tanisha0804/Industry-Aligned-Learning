from collections import Counter
from app.core.skill_ontology import normalize_skills

def aggregate_resume_skills(skill_list: list) -> dict:
    raw_counts = Counter(skill_list)
    return normalize_skills(raw_counts)
