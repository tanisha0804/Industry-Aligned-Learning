import json
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException

from backend.app.core.pdf_skill_extractor import PDFSkillExtractor

app = FastAPI(title="Resume Skill Extraction API")

UPLOAD_DIR = Path("backend/app/data/tmp_uploads")
OUTPUT_DIR = Path("backend/app/data/live_resumes")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_id = uuid.uuid4().hex
    temp_pdf_path = UPLOAD_DIR / f"{file_id}.pdf"

    # Save PDF
    with open(temp_pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extractor = PDFSkillExtractor()
        text = extractor.extract_text_from_pdf(str(temp_pdf_path))
        skills = sorted(set(extractor.extract_skills(text)))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF parsing failed: {str(e)}")

    finally:
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()

    output = {
        "resume_name": file.filename,
        "total_skills": len(skills),
        "skills": skills
    }

    # Save result
    output_path = OUTPUT_DIR / f"{file_id}_skills.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return output
