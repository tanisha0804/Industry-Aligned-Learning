import json
from pathlib import Path

from core.job_skill_extractor import extract_skills_from_job_text
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

        print(f"Resume skills extracted: {txt_file.name}")
