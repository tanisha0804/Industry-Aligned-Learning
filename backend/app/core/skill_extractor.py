import re
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from pathlib import Path
from collections import Counter
from app.utils.skill_seed import load_skill_seeds

SKILL_SEED = load_skill_seeds()

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\+\# ]", " ", text)
    return text


def extract_skill_candidates(text: str, skill_seeds: set) -> Counter:
    """
    Seed-guided skill extraction.
    """
    text = normalize_text(text)
    tokens = text.split()

    # Remove stopwords and very short tokens
    filtered_tokens = [
        t for t in tokens
        if t not in ENGLISH_STOP_WORDS and len(t) > 2
    ]

    detected_skills = []

    # Match multi-word & single-word skills
    for seed in skill_seeds:
        pattern = r"\b" + re.escape(seed) + r"\b"
        if re.search(pattern, text):
            detected_skills.append(seed)


    return Counter(detected_skills)


def extract_skills_from_file(file_path: Path) -> Counter:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return extract_skill_candidates(text, SKILL_SEED)
