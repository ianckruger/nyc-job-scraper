from __future__ import annotations

from typing import Any, Iterable, Optional

from job_hunter.config.logging import get_logger
from job_hunter.core.models import JobPosting
from job_hunter.sources.base import HTMLSource

logger = get_logger(__name__)


class GenericPageScraper(HTMLSource):
    name = "webscrape"

    def __init__(self, *, url: str, company: str, enabled: bool = True) -> None:
        super().__init__(enabled=enabled)
        self.url = url
        self.company = company

    def discover(self) -> Iterable[str]:
        logger.warning("Generic web scraper not implemented yet for %s", self.company)
        return []

    def fetch(self, item: str) -> Any:
        return ""

    def parse(self, raw: Any, *, item: Optional[str] = None) -> list[JobPosting]:
        return []
