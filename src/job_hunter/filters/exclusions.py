from __future__ import annotations

EXCLUDED_TITLE_KEYWORDS = {
    "internship only",
    "unpaid",
}


def should_exclude(title: str, description: str = "") -> bool:
    text = f"{title} {description}".lower()
    return any(keyword in text for keyword in EXCLUDED_TITLE_KEYWORDS)
