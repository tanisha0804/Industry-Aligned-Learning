import json
from pathlib import Path

def compute_skill_gap(resume_skills: list, job_skills_file: Path):
    with open(job_skills_file, "r", encoding="utf-8") as f:
        job_data = json.load(f)

    job_skills = set(job_data.get("skills", []))
    resume_skills = set(resume_skills)

    missing = sorted(job_skills - resume_skills)

    return {
        "total_missing_skills": len(missing),
        "missing_skills": missing
    }
