from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml
from job_hunter.config.settings import get_settings
DEFAULT_SOURCES_PATH = Path(__file__).resolve().parent / "sources.yaml"
def load_sources_config(path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    config_path = path or DEFAULT_SOURCES_PATH
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return {key: value or [] for key, value in data.items()}
def get_source_entries(source_name: str, path: Path | None = None) -> list[dict[str, Any]]:
    config = load_sources_config(path)
    return config.get(source_name, [])