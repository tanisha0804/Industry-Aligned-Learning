# backend/app/core/course_skill_extractor.py

import re
from rapidfuzz import fuzz
from utils.skill_seed import load_primary_skills, load_secondary_skills

PRIMARY_SKILLS = load_primary_skills()
SECONDARY_SKILLS = load_secondary_skills()

COURSE_SKILL_SECTIONS = [
    "tools",
    "software",
    "languages",
    "lab",
    "laboratory",
    "prerequisite",
    "elective"
]

# 1. COURSE TITLE → SKILL MAPPIN
def extract_from_course_title(title: str):
    title = title.lower()
    skills = set()

    for seed, canonical in PRIMARY_SKILLS.items():
        if seed in title:
            skills.add(canonical)

    for seed, canonical in SECONDARY_SKILLS.items():
        if seed in title:
            skills.add(canonical)

    return skills

# 2. SECTION GATING

def extract_relevant_sections(text: str) -> str:
    lines = text.splitlines()
    capture = False
    collected = []

    for line in lines:
        clean = line.lower().strip()

        if any(sec in clean for sec in COURSE_SKILL_SECTIONS):
            capture = True
            continue

        if capture:
            if len(clean) == 0:
                break
            collected.append(line)

    return " ".join(collected)

# 3. NOUN / PHRASE EXTRACTION (1–3 GRAMS)

def extract_candidates(text: str):
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9+/ ]", " ", text)

    tokens = text.lower().split()
    candidates = set()

    for i in range(len(tokens)):
        for j in range(i + 1, min(i + 4, len(tokens) + 1)):
            phrase = " ".join(tokens[i:j]).strip()
            if 2 <= len(phrase) <= 40:
                candidates.add(phrase)

    return candidates

# 4. EXACT + FUZZY MATCHING 

def match_to_ontology(candidates):
    primary = set()
    secondary = set()

    for phrase in candidates:
        # Exact match first
        if phrase in PRIMARY_SKILLS:
            primary.add(PRIMARY_SKILLS[phrase])
            continue

        if phrase in SECONDARY_SKILLS:
            secondary.add(SECONDARY_SKILLS[phrase])
            continue

        # Fuzzy fallback
        for seed, canonical in PRIMARY_SKILLS.items():
            if fuzz.partial_ratio(phrase, seed) >= 90:
                primary.add(canonical)

        for seed, canonical in SECONDARY_SKILLS.items():
            if fuzz.partial_ratio(phrase, seed) >= 90:
                secondary.add(canonical)

    return primary, secondary

# MAIN AP
def extract_skills_from_course(course_title: str, course_text: str):
    primary = set()
    secondary = set()

    # Title-based extraction 
    title_skills = extract_from_course_title(course_title)
    for s in title_skills:
        if s in PRIMARY_SKILLS.values():
            primary.add(s)
        else:
            secondary.add(s)

    # Section-gated extraction
    gated_text = extract_relevant_sections(course_text)

    if gated_text.strip():
        candidates = extract_candidates(gated_text)
        p, s = match_to_ontology(candidates)
        primary |= p
        secondary |= s

    return {
        "primary_skills": sorted(primary),
        "secondary_skills": sorted(secondary)
    }
