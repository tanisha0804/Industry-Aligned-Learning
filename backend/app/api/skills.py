from fastapi import APIRouter
from pathlib import Path
import json

from app.core.skill_extractor import extract_skills_from_file
from app.core.skill_aggregator import aggregate_resume_skills
import matplotlib.pyplot as plt


router = APIRouter()


@router.post("/extract-all")
def extract_all_resume_skills():
    base_dir = Path(__file__).resolve().parents[1] / "data"

    resumes_text = base_dir / "resumes_processed"
    resumes_skills = base_dir / "resumes_skills"
    viz_dir = base_dir / "visualization"

    resumes_skills.mkdir(exist_ok=True)
    viz_dir.mkdir(exist_ok=True)

    # --------- extract skills per resume ----------
    for txt_file in resumes_text.glob("*.txt"):
        skills = extract_skills_from_file(txt_file)

        output = {
            "source": "resume",
            "file": txt_file.name,
            "skills": skills
        }

        out_file = resumes_skills / f"{txt_file.stem}.json"
        out_file.write_text(json.dumps(output, indent=2))

    #  aggregate + visualize 
    skill_counts = aggregate_resume_skills(resumes_skills)
    top_skills = skill_counts.most_common(15)

    if top_skills:
        skills, counts = zip(*top_skills)

        plt.figure(figsize=(10, 6))
        plt.barh(skills, counts)
        plt.xlabel("Frequency")
        plt.title("Top Resume Skills (Debug View)")
        plt.gca().invert_yaxis()

        plt.tight_layout()
        plt.savefig(viz_dir / "resume_skill_frequency.png")
        plt.close()

    return {
        "status": "Resume skill extraction completed",
        "total_resumes": len(list(resumes_text.glob("*.txt"))),
        "unique_skills": len(skill_counts)
    }
