import json
from pathlib import Path

""" from core.job_skill_extractor import extract_skills_from_job_text
from core.course_skill_extractor import extract_skills_from_course
from core.resume_skill_extractor import extract_skills_from_resume

BASE_DATA = Path("backend/app/data")

def process_job_descriptions():
    input_dir = BASE_DATA / "jobs_processed"
    output_dir = BASE_DATA / "jobs_skills"
    output_dir.mkdir(exist_ok=True)

    for txt_file in input_dir.glob("*.txt"):
        text = txt_file.read_text(encoding="utf-8", errors="ignore")

        skills = extract_skills_from_job_text(text)

        out_file = output_dir / f"{txt_file.stem}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "source": txt_file.name,
                    "skills": skills
                },
                f,
                indent=2
            )

        print(f"Job skills extracted: {txt_file.name}")

def process_courses():
    input_dir = BASE_DATA / "courses_processed"
    output_dir = BASE_DATA / "courses_skills"
    output_dir.mkdir(exist_ok=True)

    for txt_file in input_dir.glob("*.txt"):
        text = txt_file.read_text(encoding="utf-8", errors="ignore")

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            continue

        course_title = lines[0]
        course_body = "\n".join(lines[1:])

        skills = extract_skills_from_course(course_title, course_body)

        out_file = output_dir / f"{txt_file.stem}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "course_title": course_title,
                    "skills": skills
                },
                f,
                indent=2
            )

        print(f"Course skills extracted: {txt_file.name}")

def process_resumes():
    input_dir = BASE_DATA / "resumes_processed"
    output_dir = BASE_DATA / "resumes_skills"
    output_dir.mkdir(exist_ok=True)

    for txt_file in input_dir.glob("*.txt"):
        text = txt_file.read_text(encoding="utf-8", errors="ignore")

        skills = extract_skills_from_resume(text)

        out_file = output_dir / f"{txt_file.stem}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "resume": txt_file.name,
                    "skills": skills
                },
                f,
                indent=2
            )

        print(f"Resume skills extracted: {txt_file.name}") """


# --------------------------------------------------
# SKILL GAP ANALYSIS (DAY 8)
# --------------------------------------------------


from core.skill_gap import compute_skill_gap
from core.industry_demand import compute_industry_demand
import json

BASE_DATA = Path("backend/app/data")

def process_skill_gaps():
    industry_demand_file = BASE_DATA / "market_trends.json"
    learner_dir = BASE_DATA / "learner_profiles"
    output_dir = BASE_DATA / "skill_gaps"
    output_dir.mkdir(exist_ok=True)

    with open(industry_demand_file, "r", encoding="utf-8") as f:
        industry_demand = json.load(f)

    for learner_file in learner_dir.glob("*.json"):
        with open(learner_file, "r", encoding="utf-8") as f:
            learner_belief = json.load(f)

        gap_scores = compute_skill_gap(industry_demand, learner_belief)

        out_file = output_dir / learner_file.name
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(gap_scores, f, indent=2)

        print(f"Skill gap computed for {learner_file.name}")



