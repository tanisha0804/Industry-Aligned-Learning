import re
from rapidfuzz import fuzz
from utils.skill_seed import load_primary_skills, load_secondary_skills

PRIMARY_SKILLS = load_primary_skills()
SECONDARY_SKILLS = load_secondary_skills()

# 1. SECTION GATING 
SKILL_SECTIONS = [
    "skills",
    "technical skills",
    "requirements",
    "skill set",
    "tools",
    "technologies"
]

def extract_skill_sections(text: str) -> str:
    lines = text.splitlines()
    capture = False
    collected = []

    for line in lines:
        clean = line.strip().lower()

        if any(sec in clean for sec in SKILL_SECTIONS):
            capture = True
            continue

        if capture:
            if len(clean) == 0:
                break
            collected.append(line)

    return " ".join(collected)


# 2. NOUN-PHRASE CANDIDATES
def extract_candidates(text: str):
    text = re.sub(r"http\S+|www\S+", "", text)   # remove URLs
    text = re.sub(r"[^a-zA-Z0-9+/ ]", " ", text)

    tokens = text.split()
    phrases = []

    for i in range(len(tokens)):
        for j in range(i + 1, min(i + 4, len(tokens))):
            phrase = " ".join(tokens[i:j]).lower()
            if 2 <= len(phrase) <= 35:
                phrases.append(phrase)

    return set(phrases)


# 3. FUZZY + ONTOLOGY MATCHING
def match_to_seed(candidates):
    primary = set()
    secondary = set()

    for phrase in candidates:
        phrase_l = phrase.lower()

        # ---------- PRIMARY SKILLS ----------
        for seed, canonical in PRIMARY_SKILLS.items():
            score = fuzz.partial_ratio(phrase_l, seed)

            if score >= 85:
                primary.add(canonical)

        # ---------- SECONDARY SKILLS ----------
        for seed, canonical in SECONDARY_SKILLS.items():
            score = fuzz.partial_ratio(phrase_l, seed)

            if score >= 85:
                secondary.add(canonical)

    return {
        "primary_skills": sorted(primary),
        "secondary_skills": sorted(secondary)
    }


# MAIN API
def extract_skills_from_job_text(text: str):
    gated = extract_skill_sections(text)

    if not gated.strip():
        return []

    candidates = extract_candidates(gated)
    skills = match_to_seed(candidates)

    return skills
