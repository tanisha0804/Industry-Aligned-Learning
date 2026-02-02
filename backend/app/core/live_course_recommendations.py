import json
from pathlib import Path
from typing import List, Dict

def load_course_skills(course_skills_file: Path) -> List[Dict]:
    with open(course_skills_file, "r", encoding="utf-8") as f:
        return json.load(f)

def recommend_courses(
    missing_skills: List[str],
    course_skills_file: Path
) -> List[Dict]:

    courses = load_course_skills(course_skills_file)
    recommendations = []

    for skill in missing_skills:
        matched_course = None

        for course in courses:
            course_skills = course.get("skills", [])

            if skill in course_skills:
                matched_course = {
                    "missing_skill": skill,
                    "recommended_course": {
                        "course_code": course.get("course_code"),
                        "course_title": course.get("course_title"),
                        "covers_skills": course_skills
                    }
                }
                break 

        if matched_course:
            recommendations.append(matched_course)

    return recommendations
