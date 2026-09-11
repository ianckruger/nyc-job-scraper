from __future__ import annotations

from typing import Any

from job_hunter.config.logging import get_logger
from job_hunter.config.sources import load_sources_config
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
        configured_entries = _resolve_configured_entries(source_name)
        if not configured_entries:
            logger.warning("No configured source or company matches: %s", source_name)
            continue

        for adapter_name, entry in configured_entries:
            adapter = _build_adapter(adapter_name, entry, shared_http)
            if adapter is not None:
                adapters.append(adapter)

    return adapters


def _resolve_configured_entries(source_name: str) -> list[tuple[str, dict[str, Any]]]:
    """Resolve an adapter name or a configured company/token alias."""
    config = load_sources_config()
    if source_name in config:
        return [(source_name, entry) for entry in config[source_name]]

    requested_name = source_name.casefold()
    matches: list[tuple[str, dict[str, Any]]] = []
    for adapter_name, entries in config.items():
        for entry in entries:
            aliases = (
                entry.get("token"),
                entry.get("board_token"),
                entry.get("company_token"),
                entry.get("company"),
                entry.get("name"),
            )
            if any(
                isinstance(alias, str) and alias.casefold() == requested_name
                for alias in aliases
            ):
                matches.append((adapter_name, entry))
    return matches


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
