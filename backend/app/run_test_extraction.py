"""
Test extraction on 1 resume, 1 JD, 1 course handbook
"""
import json
from pathlib import Path
from core.pdf_skill_extractor import PDFSkillExtractor


def test_single_extraction():
    """Test extraction on one file from each source"""
    
    extractor = PDFSkillExtractor()
    base_path = Path(".")
    
    # Test files - one from each source
    test_cases = [
        {
            "type": "Resume",
            "path": "data/resumes_raw/NAVEEN D_profile - NAVEEN D 2022 Batch PES University EC.pdf"
        },
        {
            "type": "Job Description",
            "path": "data/jobs_raw/Job Description + SkillSet.pdf"
        },
        {
            "type": "Course Handbook",
            "path": "data/courses_raw/Handbook 2022-2026.pdf"
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        file_path = base_path / test_case["path"]
        
        print(f"\n{'='*60}")
        print(f"Testing: {test_case['type']}")
        print(f"File: {file_path.name}")
        print('='*60)
        
        if not file_path.exists():
            print(f"ERROR: File not found at {file_path}")
            continue
        
        result = extractor.extract_from_file(str(file_path))
        results[test_case["type"]] = result
        
        # Display results
        if result.get('error'):
            print(f"Error: {result['error']}")
        else:
            print(f"✓ Skills extracted: {result['count']}")
            print(f"\nSkills found ({result['count']} total):")
            
            if result['skills']:
                # Group by first letter for readability
                skills_by_letter = {}
                for skill in result['skills']:
                    first_letter = skill[0].upper()
                    if first_letter not in skills_by_letter:
                        skills_by_letter[first_letter] = []
                    skills_by_letter[first_letter].append(skill)
                
                for letter in sorted(skills_by_letter.keys()):
                    skills = skills_by_letter[letter]
                    print(f"  {letter}: {', '.join(sorted(skills))}")
            else:
                print("  (No skills matched)")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    for source_type, result in results.items():
        count = result.get('count', 0)
        print(f"{source_type}: {count} skills extracted")
    
    # Save detailed results
    output_file = "test_extraction_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    test_single_extraction()
