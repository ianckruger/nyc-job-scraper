from __future__ import annotations

from job_hunter.config.sources import load_company_registry, load_sources_config
from job_hunter.sources import build_sources
from job_hunter.sources.greenhouse import GreenhouseSource


def test_source_registry_accepts_configured_board_token_alias() -> None:
    sources = build_sources(["datadog"], http=object())

    assert len(sources) == 1
    assert isinstance(sources[0], GreenhouseSource)
    assert sources[0].company == "Datadog"
    assert sources[0].board_token == "datadog"


def test_source_registry_accepts_configured_company_alias_case_insensitively() -> None:
    sources = build_sources(["FIGMA"], http=object())

    assert len(sources) == 1
    assert isinstance(sources[0], GreenhouseSource)
    assert sources[0].company == "Figma"


def test_company_registry_groups_entries_by_provider() -> None:
    registry = load_company_registry()
    sources = load_sources_config()

    assert any(entry["company"] == "Datadog" for entry in registry)
    assert any(entry["company"] == "Datadog" for entry in sources["greenhouse"])
    assert any(entry["company"] == "Netflix" for entry in sources["lever"])
