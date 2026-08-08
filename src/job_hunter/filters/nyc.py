from __future__ import annotations

NYC_SIGNALS = [
    "new york",
    "new york city",
    "nyc",
    "manhattan",
    "brooklyn",
    "queens",
    "remote - ny",
    "hybrid in new york",
]


def is_nyc_job(location: str | None, description: str = "") -> bool:
    return nyc_score(location, description) >= 3.0


def nyc_score(location: str | None, description: str = "") -> float:
    text = f"{location or ''} {description}".lower()
    matches = sum(1 for signal in NYC_SIGNALS if signal in text)
    if matches == 0:
        return 0.0
    return 3.0 + min(matches, 4)
