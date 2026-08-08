from __future__ import annotations

from urllib.parse import urljoin, urlparse


def normalize_url(url: str, base: str | None = None) -> str:
    if base and not url.startswith(("http://", "https://")):
        return urljoin(base, url)
    return url.strip()


def domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()
