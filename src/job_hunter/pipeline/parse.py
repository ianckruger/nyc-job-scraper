from __future__ import annotations

from job_hunter.pipeline.discover import parse_jobs
from job_hunter.sources.base import BaseJobSource

__all__ = ["parse_jobs", "parse_source_payloads"]


def parse_source_payloads(
    source: BaseJobSource, payloads: list[tuple[str, object]]
) -> list:
    return parse_jobs(source, payloads)
