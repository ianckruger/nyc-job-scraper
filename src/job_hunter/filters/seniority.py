from __future__ import annotations

SENIORITY_KEYWORDS = {
    "intern": "intern",
    "entry level": "entry",
    "junior": "junior",
    "mid level": "mid",
    "mid-level": "mid",
    "senior": "senior",
    "staff": "staff",
    "principal": "principal",
    "lead": "lead",
}


def infer_seniority(title: str) -> str | None:
    text = title.lower()
    for keyword, label in SENIORITY_KEYWORDS.items():
        if keyword in text:
            return label
    return None


def seniority_score(seniority: str | None) -> float:
    if seniority in {"mid", "senior", "staff", "principal", "lead"}:
        return 1.5
    if seniority in {"junior", "entry"}:
        return 1.0
    return 0.0
