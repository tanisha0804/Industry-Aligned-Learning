import json
from pathlib import Path
from typing import Dict, Set, List

def compute_missing_skills(job_skill_set: set,
                        learner_skill_set: set,
                        market_trends: dict) -> List[Dict]:
    """
    Identifies skills required by industry (job) but missing from learner profile.
    Scores them by market demand from market_trends.json
    """
    missing = []
    for skill in job_skill_set:
        if skill not in learner_skill_set:
            market_demand = market_trends.get(skill, 0.3)
            missing.append({
                "skill": skill,
                "market_demand": round(market_demand, 3),
            })
    return sorted(
        missing,
        key=lambda x: x["market_demand"],
        reverse=True
    )

def aggregate_missing_skills_across_jobs(learner_skill_set: set,
                                         jobs_dir: Path,
                                         market_trends: dict) -> Dict:
    all_missing_by_skill = {}
    job_count = 0
    
    for job_file in jobs_dir.glob("*.json"):
        job_count += 1
        with open(job_file, "r", encoding="utf-8") as f:
            job_json = json.load(f)
        
        job_skill_set = _extract_skill_set_from_job(job_json)
        missing_in_this_job = compute_missing_skills(
            job_skill_set,
            learner_skill_set,
            market_trends
        )
        
        for skill_info in missing_in_this_job:
            skill = skill_info["skill"]
            if skill not in all_missing_by_skill:
                all_missing_by_skill[skill] = {
                    "skill": skill,
                    "market_demand": skill_info["market_demand"]
                }
            all_missing_by_skill[skill]["frequency"] += 1
    
    # Calculate frequency percentages
    for skill in all_missing_by_skill:
        all_missing_by_skill[skill]["frequency_pct"] = round(
            all_missing_by_skill[skill]["frequency"] / job_count * 100, 2
        ) if job_count > 0 else 0

    sorted_missing = sorted(
        all_missing_by_skill.values(),
        key=lambda x: (x["frequency_pct"] * x["market_demand"]),
        reverse=True
    )
    
    return {
        "total_jobs_analyzed": job_count,
        "missing_skills_count": len(all_missing_by_skill),
        "missing_skills": sorted_missing
    }

def _extract_skill_set_from_job(job_json: Dict) -> Set:
    """Helper to extract skill set from job JSON."""
    skills = set()
    skill_block = job_json.get("skills", {})
    skills.update(skill_block.get("primary_skills", []))
    skills.update(skill_block.get("secondary_skills", []))
    return skills
