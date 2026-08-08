from __future__ import annotations

from typing import Any

from job_hunter.config.logging import get_logger
from job_hunter.config.sources import get_source_entries
from job_hunter.sources.base import BaseJobSource
from job_hunter.sources.greenhouse import GreenhouseSource
from job_hunter.sources.lever import LeverSource
from job_hunter.utils.http import HttpClient

logger = get_logger(__name__)


def build_sources(
    source_names: list[str],
    *,
    http: HttpClient | None = None,
) -> list[BaseJobSource]:
    shared_http = http or HttpClient()
    adapters: list[BaseJobSource] = []

    for source_name in source_names:
        entries = get_source_entries(source_name)
        if not entries:
            logger.warning("No configured entries for source: %s", source_name)
            continue

        for entry in entries:
            adapter = _build_adapter(source_name, entry, shared_http)
            if adapter is not None:
                adapters.append(adapter)

    return adapters


def _build_adapter(
    source_name: str,
    entry: dict[str, Any],
    http: HttpClient,
) -> BaseJobSource | None:
    company = entry.get("company") or entry.get("name") or entry.get("token") or "Unknown"
    token = entry.get("token") or entry.get("board_token") or entry.get("company_token")

    if source_name == "greenhouse":
        if not token:
            return None
        return GreenhouseSource(board_token=str(token), company=str(company), http=http)

    if source_name == "lever":
        if not token:
            return None
        return LeverSource(company_token=str(token), company=str(company), http=http)

    logger.warning("Source adapter not implemented yet: %s", source_name)
    return None
