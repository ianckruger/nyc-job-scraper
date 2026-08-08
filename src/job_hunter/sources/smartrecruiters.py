from __future__ import annotations

from typing import Any, Iterable, Optional

from job_hunter.config.logging import get_logger
from job_hunter.core.models import JobPosting
from job_hunter.sources.base import APISource

logger = get_logger(__name__)


class SmartRecruitersSource(APISource):
    name = "smartrecruiters"

    def __init__(self, *, company_id: str, company: str, enabled: bool = True) -> None:
        super().__init__(enabled=enabled)
        self.company_id = company_id
        self.company = company

    def discover(self) -> Iterable[str]:
        logger.warning("SmartRecruiters source not implemented yet for %s", self.company)
        return []

    def fetch(self, item: str) -> Any:
        return {}

    def parse(self, raw: Any, *, item: Optional[str] = None) -> list[JobPosting]:
        return []
