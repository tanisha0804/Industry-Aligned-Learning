import requests
import json
import time
import math
import re
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv()

import os
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

JOB_SKILLS_FILE = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\jobs_skills\Job Description + SkillSet.json"
)

OUTPUT_DIR = Path(
    r"D:\project Industry-Academia\Industry-Aligned-Learning\backend\app\data\industry_skill_demand"
)

OUTPUT_JSON = OUTPUT_DIR / "core_skill_demands.json"
OUTPUT_PNG = OUTPUT_DIR / "core_skill_demands_top50.png"


BUFFER_TERMS = {
    "awesome", "list", "lists", "resources", "resource",
    "interview", "questions", "practice", "free", "public",
    "example", "examples", "demo", "sample", "samples",
    "tutorial", "guide", "book", "books",
    "collection", "dataset", "repo", "repository",
    "app", "apps", "application", "project",
    "framework", "frameworks", "library", "libraries",
    "tool", "tools", "system", "systems", "platform",
    "api", "apis", "service", "services"
}

ALIASES = {
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
    "data structure": "Data Structures & Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "dl": "Deep Learning",
    "nodejs": "Node.js",
    "reactjs": "React",
    "scikit learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
}

SKILL_ONTOLOGY = {
    # Languages
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "c++": "C++",
    "go": "Go",
    "rust": "Rust",

    # Web / Backend
    "react": "React",
    "angular": "Angular",
    "vue": "Vue.js",
    "node": "Node.js",
    "express": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring Boot",

    # Cloud / DevOps
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "jenkins": "Jenkins",

    # AI / Data
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "artificial intelligence": "Artificial Intelligence",
    "natural language processing": "Natural Language Processing",
    "computer vision": "Computer Vision",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "huggingface": "HuggingFace",

    # Data Engineering
    "spark": "Apache Spark",
    "hadoop": "Hadoop",
    "databricks": "Databricks",

    # Databases
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",

    # Systems
    "linux": "Linux"
}

def normalize_skill(raw: str):
    raw = raw.lower().strip()
    raw = re.sub(r"[_\-]", " ", raw)

    if raw in BUFFER_TERMS or len(raw) < 3:
        return None

    if raw in ALIASES:
        return ALIASES[raw]

    for key, canonical in SKILL_ONTOLOGY.items():
        if key in raw:
            return canonical

    return None

def load_core_skills(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    skills = set()
    for s in data.get("skills", []):
        ns = normalize_skill(s)
        if ns:
            skills.add(ns)

    return skills

DISCOVERY_QUERIES = [
    "language:python", "language:java", "language:javascript",
    "language:go", "language:c++",
    "topic:machine-learning", "topic:cloud",
    "topic:kubernetes", "topic:data-science"
]

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"

def discover_skills_from_github():
    scores = defaultdict(int)

    for query in DISCOVERY_QUERIES:
        print(f" GitHub discovery: {query}")

        r = requests.get(
            GITHUB_SEARCH_URL,
            headers=HEADERS,
            params={"q": query, "sort": "stars", "order": "desc", "per_page": 30},
            timeout=10
        )

        if r.status_code != 200:
            continue

        for repo in r.json().get("items", []):
            if repo.get("language"):
                s = normalize_skill(repo["language"])
                if s:
                    scores[s] += repo["stargazers_count"]

            for t in repo.get("topics", []):
                s = normalize_skill(t)
                if s:
                    scores[s] += repo["stargazers_count"]

        time.sleep(2)

    return scores

STACKOVERFLOW_TAG_URL = "https://api.stackexchange.com/2.3/tags"

def stackoverflow_score(skill):
    r = requests.get(
        STACKOVERFLOW_TAG_URL,
        params={"inname": skill, "site": "stackoverflow", "pagesize": 1},
        timeout=8
    )
    if r.status_code != 200:
        return 0

    items = r.json().get("items", [])
    return items[0]["count"] if items else 0

def normalize(scores):
    if not scores:
        return {}

    max_val = max(scores.values())
    if max_val == 0:
        return {k: 0.0 for k in scores}

    return {
        k: math.log1p(v) / math.log1p(max_val)
        for k, v in scores.items()
    }

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    jd_skills = load_core_skills(JOB_SKILLS_FILE)
    github_raw = discover_skills_from_github()

    # Ensure JD skills are never dropped
    for s in jd_skills:
        github_raw.setdefault(s, 1)

    so_raw = {}
    for s in github_raw:
        print(f"StackOverflow lookup: {s}")
        so_raw[s] = stackoverflow_score(s)
        time.sleep(1)

    gh_norm = normalize(github_raw)
    so_norm = normalize(so_raw)

    market = {
        s: round(0.6 * gh_norm.get(s, 0) + 0.4 * so_norm.get(s, 0), 4)
        for s in github_raw
    }

    market = dict(sorted(market.items(), key=lambda x: x[1], reverse=True))

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(dict(list(market.items())[:100]), f, indent=2)

    top50 = dict(list(market.items())[:50])
    plt.figure(figsize=(12, 9))
    plt.barh(top50.keys(), top50.values())
    plt.gca().invert_yaxis()
    plt.title("Core Technology Skill Demand (Industry + Global)")
    plt.xlabel("Market Demand Score (Log-Scaled)")
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG)
    plt.close()

    print("Combined JD + Global skill demand generated")

if __name__ == "__main__":
    main()
