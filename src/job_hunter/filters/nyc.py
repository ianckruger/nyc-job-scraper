from __future__ import annotations
import re
import unicodedata


NYC_LOCATION_PATTERN = re.compile(
    r"\b(?:"
    r"new york(?: city)?"
    r"|nyc"
    r"|ny\s*,\s*ny"
    r"|manhattan"
    r"|brooklyn"
    r"|queens"
    r"|bronx"
    r"|staten island"
    r")\b",
    re.IGNORECASE,
)

def normalize_location(location: str | None) -> str:
    """ returns a comparable display that's independating of the location string"""
    if not location:
        return ""

    normalized = unicodedata.normalize("NFKC", location).casefold()
    normalized = normalized.replace("\N{BULLET}", ";").replace("|", ";")
    return re.sub(r"\s+", " ", normalized).strip()
    

def is_nyc_job(location:str | None) -> bool:
    return bool(NYC_LOCATION_PATTERN.search(normalize_location(location)))

def nyc_score(location: str | None) -> float:
    return 3.0 if is_nyc_job(location) else 0.0

def mentions_nyc(text: str)-> bool:
    """context  but not proof of location"""
    return bool(NYC_LOCATION_PATTERN.search(text or ""))
