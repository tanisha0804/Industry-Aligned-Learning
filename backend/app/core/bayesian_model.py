from core.learner_profile import build_learner_profile
import json 
from pathlib import Path

BASE_DATA = Path("backend/app/data")

def process_learner_profiles():
    input_dir = BASE_DATA / "resumes_skills"
    output_dir = BASE_DATA / "learner_profiles"
    output_dir.mkdir(exist_ok=True)

    for resume_file in input_dir.glob("*.json"):
        belief = build_learner_profile(resume_file)

        out_file = output_dir / resume_file.name
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(belief, f, indent=2)

        print(f"Learner profile created: {resume_file.name}")