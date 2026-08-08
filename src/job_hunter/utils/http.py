from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from job_hunter.config.settings import Settings, get_settings


class HttpClient:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._client = httpx.Client(
            timeout=self.settings.request_timeout_s,
            headers={"User-Agent": self.settings.user_agent},
            follow_redirects=True,
        )

    def get_json(self, url: str, *, params: Optional[dict[str, Any]] = None) -> Any:
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_text(self, url: str, *, params: Optional[dict[str, Any]] = None) -> str:
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response.text

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def polite_sleep(seconds: float = 0.25) -> None:
    time.sleep(seconds)
