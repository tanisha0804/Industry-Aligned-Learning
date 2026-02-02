import json
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException

from backend.app.core.pdf_skill_extractor import PDFSkillExtractor
from backend.app.core.live_skill_gap import compute_skill_gap
from backend.app.core.live_course_recommendations import recommend_courses

app = FastAPI(title="Industry-Aligned Resume Analyzer")


TMP_UPLOAD_DIR = Path("backend/app/data/tmp_uploads")
LIVE_RESUME_DIR = Path("backend/app/data/live_resumes")

JOB_SKILLS_FILE = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\jobs_skills\Job Description + SkillSet.json"
)

COURSE_SKILLS_FILE = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\course_code_skill\course_skills_llm.json"
)

TMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LIVE_RESUME_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    1. Upload resume PDF
    2. Extract skills
    3. Compute skill gap
    4. Recommend ONE course per missing skill
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_id = uuid.uuid4().hex
    temp_pdf_path = TMP_UPLOAD_DIR / f"{file_id}.pdf"

    with open(temp_pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extractor = PDFSkillExtractor()
        text = extractor.extract_text_from_pdf(str(temp_pdf_path))
        extracted_skills = sorted(set(extractor.extract_skills(text)))

        skill_gap = compute_skill_gap(
            resume_skills=extracted_skills,
            job_skills_file=JOB_SKILLS_FILE
        )

        course_recommendations = recommend_courses(
            missing_skills=skill_gap["missing_skills"],
            course_skills_file=COURSE_SKILLS_FILE
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {str(e)}"
        )

    finally:
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()

    response = {
        "resume_name": file.filename,
        "total_extracted_skills": len(extracted_skills),
        "extracted_skills": extracted_skills,

        "total_missing_skills": skill_gap["total_missing_skills"],
        "missing_skills": skill_gap["missing_skills"],

        "course_recommendations": course_recommendations
    }
    output_path = LIVE_RESUME_DIR / f"{file_id}_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2)

    return response
