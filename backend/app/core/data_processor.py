from pathlib import Path
from app.utils.pdf_parser import file_to_text
from app.utils.skill_seed import load_skill_seeds
import json
from app.core.skill_extractor import extract_skills_from_file
from app.core.skill_extractor import flatten_extracted_skills
from app.core.skill_aggregator import aggregate_resume_skills

BASE_DATA = Path("app/data")

SKILL_SEED = load_skill_seeds()



def process_pdf_folder(raw_dir: Path, processed_dir: Path):
    processed_dir.mkdir(parents=True, exist_ok=True)

    for pdf_file in raw_dir.glob("*.pdf"):
        text = file_to_text(pdf_file)

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

# addition to extract skills from job descriptions and courses
def process_all_job_descriptions():
    input_dir = BASE_DATA / "jobs_processed"
    output_dir = BASE_DATA / "jobs_skills"
    output_dir.mkdir(exist_ok=True)

    for txt_file in input_dir.glob("*.txt"):
        extracted = extract_skills_from_file(txt_file)
        raw_skill_list = flatten_extracted_skills(extracted)
        final_skills = aggregate_resume_skills(raw_skill_list)

        out_file = output_dir / f"{txt_file.stem}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "source": txt_file.name,
                    "skills": final_skills
                },
                f,
                indent=2
            )


def process_all_courses():
    input_dir = BASE_DATA / "courses_processed"
    output_dir = BASE_DATA / "courses_skills"
    output_dir.mkdir(exist_ok=True)

    for txt_file in input_dir.glob("*.txt"):
        skills = extract_skills_from_file(txt_file)

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
