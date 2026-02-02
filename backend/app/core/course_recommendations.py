import json
from pathlib import Path

# ======================================================
# PATHS
# ======================================================

SKILL_GAP_DIR = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\resume_skill_gap"
)

COURSE_SKILLS_FILE = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\course_code_skill\course_skills_llm.json"
)

OUTPUT_DIR = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\course_recommendations"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


PRIMARY_SKILL_COURSES = {
    "Python": ["UE22CS151A"],
    "C": ["UE22CS151B"],
    "Java": ["UE22CS352B"],
    "Data Structures": ["UE22CS252A"],
    "Algorithms": ["UE22CS241B"],
    "SQL": ["UE22CS351A"],
    "MySQL": ["UE22CS351A"],
    "Operating Systems": ["UE22CS242B"],
    "Linux": ["UE22CS242B"],
    "Machine Learning": ["UE22CS352A"],
    "Cloud Computing": ["UE22CS351B"],
    "AWS": ["UE22CS351B"],
    "Docker": ["UE22CS351B"],
    "Kubernetes": ["UE22CS351B"],
    "Computer Networks": ["UE22CS252B"],
    "JavaScript": ["UE22CS242A"]
}

with open(COURSE_SKILLS_FILE, "r", encoding="utf-8") as f:
    courses = json.load(f)

course_by_code = {
    course["course_code"]: {
        "course_code": course["course_code"],
        "course_title": course["course_title"],
        "skills": course["skills"]
    }
    for course in courses
}

for gap_file in SKILL_GAP_DIR.glob("*_skill_gap.json"):
    with open(gap_file, "r", encoding="utf-8") as f:
        gap_data = json.load(f)

    resume_name = gap_data["name"]
    recommendations = []

    for item in gap_data["skills"]:
        missing_skill = item["skill"]
        importance_score = item["severity_score"]

        matched_courses = []

        if missing_skill in PRIMARY_SKILL_COURSES:
            for course_code in PRIMARY_SKILL_COURSES[missing_skill]:
                if course_code in course_by_code:
                    course = course_by_code[course_code]
                    matched_courses.append({
                        "course_code": course["course_code"],
                        "course_title": course["course_title"],
                        "covers_skills": course["skills"]
                    })
        else:
            for course in courses:
                if missing_skill in course["skills"]:
                    matched_courses.append({
                        "course_code": course["course_code"],
                        "course_title": course["course_title"],
                        "covers_skills": course["skills"]
                    })
        if matched_courses:
            recommendations.append({
                "missing_skill": missing_skill,
                "importance_score": importance_score,
                "recommended_courses": matched_courses
            })

    output = {
        "name": resume_name,
        "total_missing_skills": gap_data["total_missing_skills"],
        "recommendations": recommendations
    }

    output_path = OUTPUT_DIR / f"{resume_name}_course_recommendations.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"course recommendations generated for {resume_name}")

print("\n Course recommendation pipeline completed successfully")