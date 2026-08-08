from __future__ import annotations

SWE_KEYWORDS = {
    "software engineer",
    "software developer",
    "backend engineer",
    "frontend engineer",
    "full stack engineer",
    "mobile engineer",
    "ios engineer",
    "android engineer",
    "platform engineer",
    "product engineer",
    "machine learning engineer",
    "data engineer",
    "computer vision engineer",
    "site reliability engineer",
    "devops engineer",
}

EXCLUDE_KEYWORDS = {
    "recruiter",
    "sales",
    "marketing",
    "customer success",
    "hr",
    "finance",
    "legal",
}


def is_swe_role(title: str, description: str = "") -> bool:
    return swe_score(title, description) >= 5.0


def swe_score(title: str, description: str = "") -> float:
    text = f"{title} {description}".lower()
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return 0.0
    matches = sum(1 for word in SWE_KEYWORDS if word in text)
    if matches == 0:
        return 0.0
    return 5.0 + min(matches, 3)
