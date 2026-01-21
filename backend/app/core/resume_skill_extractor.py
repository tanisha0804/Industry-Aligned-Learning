import re
from utils.skill_seed import load_primary_skills, load_secondary_skills

PRIMARY_SKILLS = load_primary_skills()
SECONDARY_SKILLS = load_secondary_skills()

RESUME_SECTIONS = [
    "technical skills",
    "skills",
    "tools",
    "technologies",
    "projects",
    "experience",
    "work experience",
    "internship",
    "professional experience"
]

def extract_relevant_sections(text: str) -> str:
    lines = text.splitlines()
    capture = False
    collected = []

    for line in lines:
        clean = line.lower().strip()

        if any(sec in clean for sec in RESUME_SECTIONS):
            capture = True
            continue

        if capture:
            if len(clean) == 0:
                break
            collected.append(line)

    return "\n".join(collected)


def extract_parenthetical_phrases(text: str):
    """
    Extracts content inside parentheses:
    Example:
    Project XYZ (Python, Flask, MySQL)
    """
    matches = re.findall(r"\(([^)]+)\)", text)
    phrases = set()

    for match in matches:
        parts = re.split(r",|/|;", match)
        for p in parts:
            phrase = p.strip().lower()
            if 2 <= len(phrase) <= 40:
                phrases.add(phrase)

    return phrases


def extract_phrases(text: str):
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9+/ ]", " ", text)

    tokens = text.lower().split()
    phrases = set()

    for i in range(len(tokens)):
        for j in range(i + 1, min(i + 4, len(tokens) + 1)):
            phrase = " ".join(tokens[i:j]).strip()
            if 2 <= len(phrase) <= 40:
                phrases.add(phrase)

    return phrases


def normalize_to_ontology(candidates):
    primary = set()
    secondary = set()

    for phrase in candidates:
        if phrase in PRIMARY_SKILLS:
            primary.add(PRIMARY_SKILLS[phrase])

        elif phrase in SECONDARY_SKILLS:
            secondary.add(SECONDARY_SKILLS[phrase])

    return primary, secondary


def extract_skills_from_resume(text: str):
    primary = set()
    secondary = set()

    gated_text = extract_relevant_sections(text)

    if not gated_text.strip():
        return {
            "primary_skills": [],
            "secondary_skills": []
        }

    parenthetical = extract_parenthetical_phrases(gated_text)
    p1, s1 = normalize_to_ontology(parenthetical)
    primary |= p1
    secondary |= s1

    phrases = extract_phrases(gated_text)
    p2, s2 = normalize_to_ontology(phrases)
    primary |= p2
    secondary |= s2

    return {
        "primary_skills": sorted(primary),
        "secondary_skills": sorted(secondary)
    }
