from __future__ import annotations

import re

# These phrases decide whether a title is an engineering role worth keeping.
SWE_TITLE_KEYWORDS = frozenset(
    {
        "software engineer",
        "software developer",
        "backend engineer",
        "backend developer",
        "frontend engineer",
        "frontend developer",
        "front-end engineer",
        "front-end developer",
        "full stack engineer",
        "full stack developer",
        "full-stack engineer",
        "full-stack developer",
        "mobile engineer",
        "mobile developer",
        "ios engineer",
        "ios developer",
        "android engineer",
        "android developer",
        "platform engineer",
        "platform developer",
        "product engineer",
        "data engineer",
        "machine learning engineer",
        "computer vision engineer",
        "site reliability engineer",
        "devops engineer",
        "devops developer",
        "sre",
    }
)

# The current search targets early-career individual-contributor roles.
TITLE_EXCLUSION_KEYWORDS = frozenset(
    {
        "senior",
        "staff",
        "principal",
        "lead",
        "manager",
        "director",
        "vice president",
        "vp",
        "recruiter",
        "sales engineer",
        "solutions engineer",
        "support engineer",
        "technical program manager",
        "product manager",
        "customer success",
    }
)

# These terms make an already-qualified engineering job rank higher. They never
# make a non-engineering title pass the SWE filter.
DESCRIPTION_RANK_KEYWORDS = {
    "coding": 1.0,
    "python": 0.5,
    "typescript": 0.5,
    "javascript": 0.5,
    "java": 0.5,
    "go": 0.5,
    "rust": 0.5,
    "aws": 0.5,
    "kubernetes": 0.5,
    "distributed systems": 1.0,
}


def _contains_phrase(text: str, phrase: str) -> bool:
    return bool(re.search(rf"\b{re.escape(phrase)}\b", text))


def swe_title_check(title: str) -> bool:
    """Return whether a title is an eligible early-career SWE role."""
    normalized_title = title.casefold().strip()
    if not normalized_title:
        return False

    if any(_contains_phrase(normalized_title, phrase) for phrase in TITLE_EXCLUSION_KEYWORDS):
        return False

    return any(_contains_phrase(normalized_title, phrase) for phrase in SWE_TITLE_KEYWORDS)


def is_swe_role(title: str, description: str = "") -> bool:
    """Classify by title only; descriptions are ranking evidence, not eligibility."""
    return swe_title_check(title)


def swe_score(title: str, description: str = "") -> float:
    """Return a relevance score for an eligible SWE title."""
    if not swe_title_check(title):
        return 0.0

    normalized_description = description.casefold()
    description_bonus = sum(
        weight
        for phrase, weight in DESCRIPTION_RANK_KEYWORDS.items()
        if _contains_phrase(normalized_description, phrase)
    )
    return 5.0 + min(description_bonus, 3.0)
