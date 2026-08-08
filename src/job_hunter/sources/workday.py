from __future__ import annotations

from typing import Any, Iterable, Optional

from job_hunter.config.logging import get_logger
from job_hunter.core.models import JobPosting
from job_hunter.sources.base import APISource

logger = get_logger(__name__)


class WorkdaySource(APISource):
    name = "workday"

    def __init__(self, *, company: str, board_url: str, enabled: bool = True) -> None:
        super().__init__(enabled=enabled)
        self.company = company
        self.board_url = board_url

    def discover(self) -> Iterable[str]:
        logger.warning("Workday source not implemented yet for %s", self.company)
        return []

    def fetch(self, item: str) -> Any:
        return {}

    def parse(self, raw: Any, *, item: Optional[str] = None) -> list[JobPosting]:
        return []
