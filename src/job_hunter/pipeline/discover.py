from __future__ import annotations

from typing import Iterable

from job_hunter.config.logging import get_logger
from job_hunter.core.models import JobPosting
from job_hunter.sources.base import BaseJobSource

logger = get_logger(__name__)


def discover_jobs(source: BaseJobSource) -> list[str]:
    return list(source.discover())


def fetch_raw(source: BaseJobSource, items: Iterable[str]) -> list[tuple[str, object]]:
    payloads: list[tuple[str, object]] = []
    for item in items:
        try:
            payloads.append((item, source.fetch(item)))
        except Exception as exc:
            logger.warning("Fetch failed for %s item=%s: %s", source.name, item, exc)
    return payloads


def parse_jobs(source: BaseJobSource, payloads: Iterable[tuple[str, object]]) -> list[JobPosting]:
    jobs: list[JobPosting] = []
    for item, raw in payloads:
        jobs.extend(source.safe_parse(raw, item=item))
    return jobs
