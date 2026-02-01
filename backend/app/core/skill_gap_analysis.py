import json
from pathlib import Path

RESUME_SKILLS_DIR = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\resumes_skills"
)

JOB_SKILLS_FILE = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\jobs_skills\Job Description + SkillSet.json"
)

GLOBAL_DEMAND_FILE = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\industry_skill_demand\core_skill_demands.json"
)

OUTPUT_DIR = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\resume_skill_gap"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(JOB_SKILLS_FILE, "r", encoding="utf-8") as f:
    job_data = json.load(f)

job_skills = set(job_data.get("skills", []))

with open(GLOBAL_DEMAND_FILE, "r", encoding="utf-8") as f:
    global_demand = json.load(f)

for resume_file in RESUME_SKILLS_DIR.glob("*.json"):
    with open(resume_file, "r", encoding="utf-8") as f:
        resume_data = json.load(f)

    resume_name = resume_file.stem
    resume_skills = set(resume_data.get("skills", []))

    missing_skills = job_skills - resume_skills #core logic to find the missing skills from each resume
    skills_with_scores = []
    for skill in missing_skills:
        skills_with_scores.append({
            "skill": skill,
            "severity_score": round(global_demand.get(skill, 0.3), 4)
        })
    skills_with_scores.sort(
        key=lambda x: x["severity_score"],
        reverse=True
    )

    output = {
        "name": resume_name,
        "total_missing_skills": len(skills_with_scores),
        "skills": skills_with_scores
    }

    output_path = OUTPUT_DIR / f"{resume_name}_skill_gap.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Generated skill gap file for {resume_name}")

print("\nSkill gap analysis completed for all resumes")
