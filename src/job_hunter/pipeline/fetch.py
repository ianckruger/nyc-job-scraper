from __future__ import annotations

from job_hunter.pipeline.discover import fetch_raw
from job_hunter.sources.base import BaseJobSource

__all__ = ["fetch_raw", "fetch_source_payloads"]


def fetch_source_payloads(source: BaseJobSource) -> list[tuple[str, object]]:
    items = list(source.discover())
    return fetch_raw(source, items)
