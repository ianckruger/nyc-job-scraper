from __future__ import annotations

TITLE_ALIASES = {
    "swe": "software engineer",
    "sr.": "senior",
    "sr ": "senior ",
}


def normalize_title(title: str) -> str:
    normalized = title.strip()
    lower = normalized.lower()
    for alias, replacement in TITLE_ALIASES.items():
        if alias in lower:
            normalized = normalized.replace(alias, replacement)
            normalized = normalized.replace(alias.title(), replacement.title())
    return " ".join(normalized.split())
