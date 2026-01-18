from collections import Counter
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from app.utils.skill_seed import load_skill_seeds
from app.utils.pdf_parser import file_to_text


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\.\- ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_token_candidates(text: str):
    tokens = text.split()
    return [
        t for t in tokens
        if t not in ENGLISH_STOP_WORDS
        and len(t) > 2
        and not t.isdigit()
    ]


def extract_skills_from_file(file_path: str) -> dict:

    text = file_to_text(file_path)
    if not text or not text.strip():
        return {
            "seed_skills": {},
            "discovered_skills": {}
        }

    text = normalize_text(text)
    skill_seeds = load_skill_seeds()

    seed_hits = Counter()
    for seed in skill_seeds:
        if seed in text:
            seed_hits[seed] += text.count(seed)


    tokens = extract_token_candidates(text)
    token_freq = Counter(tokens)

    discovered = {
        token: count
        for token, count in token_freq.items()
        if count >= 3
        and token not in skill_seeds
        and len(token) <= 30
    }

    return {
        "seed_skills": dict(seed_hits),
        "discovered_skills": discovered
    }

def flatten_extracted_skills(extracted: dict) -> list:
    """
    Converts structured extraction output into a flat list of skill strings.
    Handles dicts, lists, and scalars safely.
    """

    flat_skills = []

    # Seed skills
    seed = extracted.get("seed_skills", {})
    if isinstance(seed, dict):
        flat_skills.extend(seed.keys())
    elif isinstance(seed, list):
        flat_skills.extend(seed)

    # Discovered skills
    discovered = extracted.get("discovered_skills", {})
    if isinstance(discovered, dict):
        for group in discovered.values():

            if isinstance(group, dict):
                flat_skills.extend(group.keys())
            elif isinstance(group, list):
                flat_skills.extend(group)
            elif isinstance(group, str):
                flat_skills.append(group)
    return flat_skills

