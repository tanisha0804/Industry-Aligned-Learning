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
import json
from pathlib import Path
from .skill_gap import compute_missing_skills

BASE_DATA = Path(__file__).parent.parent / "data"

def extract_skill_set_from_job(job_json):
    skills = set()
    skill_block = job_json.get("skills", {})
    skills.update(skill_block.get("primary_skills", []))
    skills.update(skill_block.get("secondary_skills", []))
    return skills

def extract_skill_set_from_learner(learner_json):
    """Extract all skills from learner profile (flat dict: skill -> proficiency)."""
    skills = set()
    # Learner profiles are flat dicts: {skill_name: proficiency_score, ...}
    skills.update(learner_json.keys())
    return skills

def process_skill_gaps():
    jobs_dir = BASE_DATA / "jobs_skills"
    learner_dir = BASE_DATA / "learner_profiles"
    output_dir = BASE_DATA / "skill_gaps"
    output_dir.mkdir(exist_ok=True)

    with open(str(BASE_DATA / "market_trends.json"), "r") as f:
        market_trends = json.load(f)

    job_file = jobs_dir / "Job Description + SkillSet.json"
    base_resolved = Path(__file__).resolve().parents[1] / "data"
    jobs_dir = base_resolved / "jobs_skills"
    learner_dir = base_resolved / "learner_profiles"
    output_dir = base_resolved / "skill_gaps"

    print(f"DEBUG → base_resolved={base_resolved}")
    print(f"DEBUG → jobs_dir={jobs_dir}")
    try:
        print(f"DEBUG → jobs_dir.exists={jobs_dir.exists()}")
        print(f"DEBUG → jobs_dir listing: {[p.name for p in jobs_dir.iterdir()]}")
    except Exception as e:
        print(f"DEBUG → jobs_dir listing failed: {e}")

    print(f"DEBUG → attempting job_file={job_file}")

    if not job_file.exists():
        available = list(jobs_dir.glob("*.json"))
        if not available:
            raise FileNotFoundError(f"No job skill files found in {jobs_dir}")
        job_file = available[0]
        print(f"DEBUG → falling back to first job_file={job_file}")

    with open(str(job_file), "r", encoding="utf-8") as jf:
        job_json = json.load(jf)

    job_skill_set = extract_skill_set_from_job(job_json)

    print("DEBUG → Job skills:", len(job_skill_set))  # sanity check

    for learner_file in learner_dir.glob("*.json"):
        with open(str(learner_file), "r", encoding="utf-8") as lf:
            learner_json = json.load(lf)

        learner_skill_set = extract_skill_set_from_learner(learner_json)

        missing = compute_missing_skills(
            job_skill_set,
            learner_skill_set,
            market_trends
        )

        with open(str(output_dir / learner_file.name), "w") as out:
            json.dump(
                {
                    "learner_id": learner_file.stem,
                    "missing_skills": missing,
                    "total_missing": len(missing),
                    "critical_skills": [m for m in missing if m.get("priority") == "CRITICAL"],
                    "high_priority_skills": [m for m in missing if m.get("priority") == "HIGH"]
                },
                out,
                indent=2
            )

        print(
            f" {learner_file.stem} → "
            f"{len(missing)} missing skills"
        )






