from __future__ import annotations

import re
from html import unescape

from bs4 import BeautifulSoup


def strip_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    return unescape(re.sub(r"\s+", " ", text))


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()
