from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_COMPANIES_PATH = Path(__file__).resolve().parent / "companies.yaml"


def load_company_registry(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the company-first registry of public ATS boards."""
    registry_path = path or DEFAULT_COMPANIES_PATH
    if not registry_path.exists():
        return []

    with registry_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    companies = data.get("companies", [])
    if not isinstance(companies, list):
        raise ValueError("Company registry must contain a 'companies' list.")
    return [entry for entry in companies if isinstance(entry, dict) and entry.get("enabled", True)]


def load_sources_config(path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    """Group company registry entries by ATS provider for source construction."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in load_company_registry(path):
        provider = entry.get("provider")
        if isinstance(provider, str) and provider:
            grouped.setdefault(provider, []).append(entry)
    return grouped


def get_source_entries(source_name: str, path: Path | None = None) -> list[dict[str, Any]]:
    return load_sources_config(path).get(source_name, [])
