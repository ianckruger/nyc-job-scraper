from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "job_hunter"
    env: str = "dev"
    debug: bool = False
    log_level: str = "INFO"

    data_dir: Path = Path("data")
    db_path: Path = Path("data/job_hunter.db")

    default_sources: str = "greenhouse,lever,ashby,workday"
    swe_only: bool = True
    nyc_only: bool = True

    request_timeout_s: float = 20.0
    user_agent: str = "job-hunter/0.1 (+local project)"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / "exports"

    @property
    def source_list(self) -> list[str]:
        return [s.strip() for s in self.default_sources.split(",") if s.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    return settings