from collections import defaultdict
import re

CANONICAL_SKILLS = {
    "Machine Learning": {
        "variants": [
            "ml", "machine learning", "deep learning", "dl",
            "neural networks", "cnn", "rnn"
        ],
        "domain": "AI",
        "type": "technical"
    },
    "Data Science": {
        "variants": [
            "data science", "data analysis", "data analytics",
            "statistics", "statistical analysis"
        ],
        "domain": "Data",
        "type": "technical"
    },
    "Python": {
        "variants": ["python"],
        "domain": "Programming",
        "type": "language"
    },
    "Java": {
        "variants": ["java"],
        "domain": "Programming",
        "type": "language"
    },
    "C/C++": {
        "variants": ["c", "c++"],
        "domain": "Programming",
        "type": "language"
    },
    "SQL": {
        "variants": ["sql", "mysql", "postgresql"],
        "domain": "Database",
        "type": "language"
    },
    "DevOps": {
        "variants": ["docker", "kubernetes", "ci/cd", "jenkins"],
        "domain": "DevOps",
        "type": "tool"
    },
    "Cloud": {
        "variants": ["aws", "azure", "gcp", "cloud computing"],
        "domain": "Cloud",
        "type": "platform"
    }
}

def normalize_token(token: str) -> str:
    token = token.lower()
    token = re.sub(r"[^a-z0-9\+\# ]", "", token)
    return token.strip()


def normalize_skills(raw_skills: dict) -> dict:

    normalized = defaultdict(lambda: {
        "count": 0,
        "type": None,
        "domain": None
    })

    # Reverse index: variant → canonical
    variant_map = {}
    for canonical, meta in CANONICAL_SKILLS.items():
        for v in meta["variants"]:
            variant_map[normalize_token(v)] = canonical

    for skill, count in raw_skills.items():
        norm_skill = normalize_token(skill)

        # Rule 1: Ignore junk
        if len(norm_skill) <= 2 and norm_skill not in {"c", "r"}:
            continue

        # Rule 2: Canonical mapping
        if norm_skill in variant_map:
            canonical = variant_map[norm_skill]
            normalized[canonical]["count"] += count
            normalized[canonical]["type"] = CANONICAL_SKILLS[canonical]["type"]
            normalized[canonical]["domain"] = CANONICAL_SKILLS[canonical]["domain"]

        # Rule 3: Keep discovered but meaningful skills
        else:
            if count >= 2 and len(norm_skill) > 3:
                normalized[skill]["count"] += count
                normalized[skill]["type"] = "discovered"
                normalized[skill]["domain"] = "unknown"

    return dict(normalized)
