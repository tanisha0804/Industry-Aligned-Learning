from utils.skill_seed import load_primary_skills, load_secondary_skills
PRIMARY = load_primary_skills()
SECONDARY = load_secondary_skills()
CANONICAL_MAP = {}

for skill in PRIMARY:
    CANONICAL_MAP[skill.lower()] = skill.upper()

for alias, canonical in SECONDARY.items():
    CANONICAL_MAP[alias.lower()] = canonical.upper()

def normalize_skill(skill: str):
    if not skill:
        return None
    key = skill.strip().lower()
    result = CANONICAL_MAP.get(key)

    if result is None:
        print("ORMALIZER DROPPED:", skill)

    return result

def normalize_skill_set(skills):
    normalized = set()
    for s in skills:
        canon = normalize_skill(s)
        if canon:
            normalized.add(canon)
    return normalized
