from collections import Counter
from pathlib import Path
import json


def aggregate_resume_skills(resume_skills_dir: Path):
# Combine skills from all resumes and count frequencies.
    counter = Counter()

    for skill_file in resume_skills_dir.glob("*.json"):
        data = json.loads(skill_file.read_text(encoding="utf-8"))
        counter.update(data["skills"])

    return counter
