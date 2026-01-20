# backend/app/core/data_processor.py

import json
from pathlib import Path
from core.job_skill_extractor import extract_skills_from_job_text

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
