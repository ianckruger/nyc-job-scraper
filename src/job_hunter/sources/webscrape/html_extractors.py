from __future__ import annotations

from bs4 import BeautifulSoup


def extract_title(soup: BeautifulSoup) -> str:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    heading = soup.find(["h1", "h2"])
    return heading.get_text(strip=True) if heading else ""


def extract_links(soup: BeautifulSoup) -> list[str]:
    return [anchor.get("href", "") for anchor in soup.find_all("a", href=True)]
