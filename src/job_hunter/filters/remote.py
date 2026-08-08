from __future__ import annotations


def remote_score(
    remote_policy: str | None,
    location: str | None = None,
    description: str = "",
) -> float:
    text = f"{remote_policy or ''} {location or ''} {description}".lower()
    if "remote" in text:
        return 2.0
    if "hybrid" in text:
        return 1.0
    if remote_policy == "on-site":
        return 0.5
    return 0.0
