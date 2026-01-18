from pathlib import Path
from app.utils.pdf_parser import pdf_to_text
from app.utils.skill_seed import load_skill_seeds

SKILL_SEED = load_skill_seeds()
from app.core.skill_extractor import extract_skill_candidates

def process_pdf_folder(raw_dir: Path, processed_dir: Path):
    processed_dir.mkdir(parents=True, exist_ok=True)

    for pdf_file in raw_dir.glob("*.pdf"):
        text = pdf_to_text(pdf_file)

        output_file = processed_dir / f"{pdf_file.stem}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Processed: {pdf_file.name}")

def run_all_processing(base_data_dir: Path):
    resumes_raw = base_data_dir / "resumes_raw"
    jobs_raw = base_data_dir / "jobs_raw"
    courses_raw = base_data_dir / "courses_raw"

    resumes_processed = base_data_dir / "resumes_processed"
    jobs_processed = base_data_dir / "jobs_processed"
    courses_processed = base_data_dir / "courses_processed"

    print(">>> Processing PDFs")
    print("Resumes exist:", resumes_raw.exists())
    print("Jobs exist:", jobs_raw.exists())
    print("Courses exist:", courses_raw.exists())

    process_pdf_folder(resumes_raw, resumes_processed)
    process_pdf_folder(jobs_raw, jobs_processed)
    process_pdf_folder(courses_raw, courses_processed)
