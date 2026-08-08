from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Optional

from job_hunter.core.models import JobPosting
from job_hunter.sources.base import APISource
from job_hunter.utils.datetime import parse_datetime, utc_now
from job_hunter.utils.http import HttpClient, polite_sleep
from job_hunter.utils.text import strip_html


class GreenhouseSource(APISource):
    """
    Greenhouse public job board API:
    https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
    """

    name = "greenhouse"
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(
        self,
        *,
        board_token: str,
        company: str,
        http: Optional[HttpClient] = None,
        fetch_details: bool = True,
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.board_token = board_token.strip()
        self.company = company.strip()
        self.http = http or HttpClient()
        self.fetch_details = fetch_details
        self._owns_http = http is None

    def discover(self) -> Iterable[str]:
        return [self.board_token]

    def fetch(self, item: str) -> dict[str, Any]:
        board_token = item
        list_url = f"{self.BASE_URL}/{board_token}/jobs"
        payload = self.http.get_json(list_url, params={"content": "true"})
        jobs = payload.get("jobs", [])

        if not self.fetch_details:
            return {"board_token": board_token, "jobs": jobs}

        detailed_jobs: list[dict[str, Any]] = []
        for job in jobs:
            job_id = job.get("id")
            if job_id is None:
                detailed_jobs.append(job)
                continue
            detail_url = f"{self.BASE_URL}/{board_token}/jobs/{job_id}"
            try:
                detail = self.http.get_json(detail_url)
                detailed_jobs.append(detail)
            except Exception:
                detailed_jobs.append(job)
            polite_sleep(0.15)

        return {"board_token": board_token, "jobs": detailed_jobs}

    def parse(self, raw: Any, *, item: Optional[str] = None) -> list[JobPosting]:
        if not isinstance(raw, dict):
            return []
        return self.parse_json(raw, item=item)

    def parse_json(self, payload: dict[str, Any], *, item: Optional[str] = None) -> list[JobPosting]:
        jobs: list[JobPosting] = []
        for raw_job in payload.get("jobs", []):
            job = self._parse_job(raw_job)
            if job is not None:
                jobs.append(job)
        return jobs

    def _parse_job(self, raw_job: dict[str, Any]) -> Optional[JobPosting]:
        title = (raw_job.get("title") or "").strip()
        job_url = (raw_job.get("absolute_url") or "").strip()
        if not title or not job_url:
            return None

        location = self._extract_location(raw_job)
        description = self._extract_description(raw_job)
        remote_policy = self._extract_remote_policy(location, description)
        posted_at = parse_datetime(raw_job.get("updated_at") or raw_job.get("first_published"))

        return JobPosting(
            source=self.name,
            source_job_id=str(raw_job.get("id") or job_url),
            title=title,
            company=self.company,
            location=location,
            remote_policy=remote_policy,
            job_url=job_url,
            apply_url=job_url,
            description=description,
            posted_at=posted_at,
            scraped_at=utc_now(),
            metadata={"raw_payload": raw_job, "board_token": self.board_token},
        )

    def _extract_location(self, raw_job: dict[str, Any]) -> Optional[str]:
        location = raw_job.get("location")
        if isinstance(location, dict):
            return location.get("name")
        if isinstance(location, str):
            return location

        offices = raw_job.get("offices") or []
        if offices and isinstance(offices[0], dict):
            return offices[0].get("name")
        return None

    def _extract_description(self, raw_job: dict[str, Any]) -> str:
        content = raw_job.get("content")
        if isinstance(content, str) and content.strip():
            return strip_html(content)
        return ""

    def _extract_remote_policy(self, location: Optional[str], description: str) -> Optional[str]:
        text = f"{location or ''} {description}".lower()
        if "remote" in text and "hybrid" in text:
            return "hybrid"
        if "remote" in text:
            return "remote"
        if "hybrid" in text:
            return "hybrid"
        if location:
            return "on-site"
        return None

    def close(self) -> None:
        if self._owns_http:
            self.http.close()
