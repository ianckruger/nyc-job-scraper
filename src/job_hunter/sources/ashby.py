from __future__ import annotations

from typing import Any, Iterable, Optional

from job_hunter.config.logging import get_logger
from job_hunter.core.models import JobPosting
from job_hunter.sources.base import APISource

logger = get_logger(__name__)


class AshbySource(APISource):
    name = "ashby"

    def __init__(self, *, org_slug: str, company: str, enabled: bool = True) -> None:
        super().__init__(enabled=enabled)
        self.org_slug = org_slug
        self.company = company

    def discover(self) -> Iterable[str]:
        logger.warning("Ashby source not implemented yet for %s", self.company)
        return []

    def fetch(self, item: str) -> Any:
        return {}

    def parse(self, raw: Any, *, item: Optional[str] = None) -> list[JobPosting]:
        return []
