import json
from pathlib import Path
from collections import defaultdict

BASE_DATA = Path("backend/app/data")

def build_learner_profile(resume_file: Path):
    """
    Builds Bayesian prior belief vector for a learner = P(skill | learner)
    primary skill = 0.7
    secondary skill = 0.4
    skill not in resume = 0.1
    """

    with open(resume_file, "r", encoding="utf-8") as f:
        resume = json.load(f)

    primary_skills = set(resume["skills"]["primary_skills"])
    secondary_skills = set(resume["skills"]["secondary_skills"])

    belief = defaultdict(lambda: 0.1)
    for skill in primary_skills:
        belief[skill] = 0.7
    for skill in secondary_skills:
        belief[skill] = max(belief[skill], 0.4)

    return dict(belief)
