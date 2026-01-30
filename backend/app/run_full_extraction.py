"""
Full extraction on ALL resumes, JDs, and course handbooks
Save results to JSON files for analysis
"""
import json
from pathlib import Path
import re
from core.pdf_skill_extractor import PDFSkillExtractor


def extract_from_directory(extractor, directory: str, source_type: str):
    """Extract skills from all PDFs in a directory"""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"ERROR: Directory not found: {directory}")
        return []
    
    pdf_files = sorted(list(dir_path.glob("*.pdf")))
    print(f"\n{'='*60}")
    print(f"{source_type.upper()}: {len(pdf_files)} files found")
    print('='*60)
    
    results = []
    for idx, pdf_file in enumerate(pdf_files, 1):
        result = extractor.extract_from_file(str(pdf_file))
        results.append(result)
        
        # Progress indicator
        if idx % 10 == 0:
            print(f"  Progress: {idx}/{len(pdf_files)}")
    
    return results


def save_individual_files(all_results):
    """Save individual skill JSON files for each resume, JD, and course"""
    
    print(f"\n{'='*60}")
    print("SAVING INDIVIDUAL SKILL FILES")
    print('='*60)
    
    # Create directories
    Path("data/resumes_skills").mkdir(parents=True, exist_ok=True)
    Path("data/jobs_skills").mkdir(parents=True, exist_ok=True)
    Path("data/courses_skills").mkdir(parents=True, exist_ok=True)
    
    # Save resumes
    print("\nSaving resume skills...")
    for item in all_results.get("resumes", []):
        filename = item["file"].replace(".pdf", ".json")
        filepath = Path("data/resumes_skills") / filename
        skill_data = {
            "source_file": item["file"],
            "skills": item["skills"],
            "total_skills": item["count"]
        }
        with open(filepath, "w") as f:
            json.dump(skill_data, f, indent=2)
    print(f"  ✓ {len(all_results.get('resumes', []))} files saved")
    
    # Save job descriptions
    print("Saving job description skills...")
    for item in all_results.get("job_descriptions", []):
        filename = item["file"].replace(".pdf", ".json")
        filepath = Path("data/jobs_skills") / filename
        skill_data = {
            "source_file": item["file"],
            "skills": item["skills"],
            "total_skills": item["count"]
        }
        with open(filepath, "w") as f:
            json.dump(skill_data, f, indent=2)
    print(f"  ✓ {len(all_results.get('job_descriptions', []))} files saved")
    
    # Save courses
    print("Saving course skills...")
    for item in all_results.get("courses", []):
        filename = item["file"].replace(".pdf", ".json")
        filepath = Path("data/courses_skills") / filename
        skill_data = {
            "source_file": item["file"],
            "skills": item["skills"],
            "total_skills": item["count"]
        }
        with open(filepath, "w") as f:
            json.dump(skill_data, f, indent=2)
    print(f"  ✓ {len(all_results.get('courses', []))} files saved")

def parse_courses_from_processed_text(extractor, processed_txt_dir="data/courses_processed"):
    """Parse processed handbook .txt files and map each course code to nearby skills.

    Strategy: find course code occurrences in the processed text, take a window
    around each occurrence and run the skill extractor on that window to capture
    Tools / Languages mentioned in the table or description.
    """
    txt_dir = Path(processed_txt_dir)
    courses = []

    code_pattern = re.compile(r"\b[A-Z]{2}\d{2}[A-Z]{2}\d{3}[A-Z]?\b")

    for txt_file in sorted(txt_dir.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8", errors="ignore")

        for m in code_pattern.finditer(text):
            code = m.group(0)

            # Attempt to extract a reasonable title near the code
            title = None
            # Look for pattern 'CODE: Title'
            post = text[m.end(): m.end()+200]
            title_match = re.match(r"[:\-\s]+([^\n\r]+)", post)
            if title_match:
                title = title_match.group(1).strip()

            # If title still None, try to capture line containing code
            if not title:
                line_start = text.rfind('\n', 0, m.start())
                line_end = text.find('\n', m.end())
                line = text[line_start+1: line_end] if line_end!=-1 else text[line_start+1: m.end()+120]
                # Remove numeric columns
                title = re.sub(r"\b\d+\b", "", line).replace(code, "").strip()

            # Extract nearby window and get skills
            start = max(0, m.start()-500)
            end = min(len(text), m.end()+500)
            window = text[start:end]
            skills = sorted(list(extractor.extract_skills(window)))

            courses.append({
                "course_code": code,
                "course_title": title,
                "skills": skills,
                "skills_count": len(skills),
                "source_file": txt_file.name
            })

    # Deduplicate by course_code keeping first occurrence
    seen = set()
    unique_courses = []
    for c in courses:
        if c["course_code"] in seen:
            continue
        seen.add(c["course_code"])
        unique_courses.append(c)

    # Save minimal per-course skill lists and a separate full mapping
    skills_dir = Path("data/courses_skills")
    skills_dir.mkdir(parents=True, exist_ok=True)

    mapping_dir = Path("data/course_skill_matching")
    mapping_dir.mkdir(parents=True, exist_ok=True)

    combined_mapping = []

    for c in unique_courses:
        # Save minimal skills list (array) in data/courses_skills/<code>.json
        skills_only = c.get("skills", [])
        skills_file = skills_dir / f"{c['course_code']}.json"
        with open(skills_file, "w", encoding="utf-8") as f:
            json.dump(skills_only, f, indent=2)

        # Save full mapping in data/course_skill_matching/<code>.json
        mapping = {
            "course_code": c["course_code"],
            "course_title": c.get("course_title"),
            "skills": skills_only,
            "skills_count": c.get("skills_count", len(skills_only)),
            "source_file": c.get("source_file")
        }
        map_file = mapping_dir / f"{c['course_code']}.json"
        with open(map_file, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2)

        combined_mapping.append(mapping)

    # Save combined mapping file
    combined_file = mapping_dir / "courses_by_code_full.json"
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(combined_mapping, f, indent=2)

    return combined_file, len(unique_courses)


def main():
    print("Starting full PDF skill extraction...\n")
    
    extractor = PDFSkillExtractor()
    base_path = Path(".")
    
    # Extract from all three sources
    all_results = {}
    
    # 1. Resumes
    resume_results = extract_from_directory(
        extractor,
        "data/resumes_raw",
        "Resumes"
    )
    all_results["resumes"] = resume_results
    
    # 2. Job Descriptions
    jd_results = extract_from_directory(
        extractor,
        "data/jobs_raw",
        "Job Descriptions"
    )
    all_results["job_descriptions"] = jd_results
    
    # 3. Course Handbooks
    course_results = extract_from_directory(
        extractor,
        "data/courses_raw",
        "Course Handbooks"
    )
    all_results["courses"] = course_results
    
    # Summary statistics
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print('='*60)
    
    for source_type, results in all_results.items():
        total_files = len(results)
        total_skills = sum(r.get('count', 0) for r in results)
        avg_skills = total_skills // total_files if total_files > 0 else 0
        
        print(f"\n{source_type.upper()}:")
        print(f"  Files: {total_files}")
        print(f"  Total skills: {total_skills}")
        print(f"  Average per file: {avg_skills}")
    
    # Save combined results
    output_file = "data/ocr_extraction_full_results.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✓ Combined results saved to: {output_file}")
    
    # Save individual files
    save_individual_files(all_results)
    
    print(f"\n✓ All individual skill files saved successfully!")

    # Parse processed handbook text and create per-course skill mappings
    try:
        combined_file, count = parse_courses_from_processed_text(extractor)
        print(f"\n✓ Course-level mapping saved to: {combined_file} ({count} courses)")
    except Exception as e:
        print(f"\n⚠️ Course parsing failed: {e}")


if __name__ == "__main__":
    main()
