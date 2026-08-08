from __future__ import annotations

from typing import Any, Iterable, Optional

from job_hunter.core.models import JobPosting
from job_hunter.sources.base import APISource
from job_hunter.utils.datetime import parse_datetime, utc_now
from job_hunter.utils.http import HttpClient, polite_sleep
from job_hunter.utils.text import strip_html


class LeverSource(APISource):
    """
    Lever public postings API:
    https://api.lever.co/v0/postings/{company}?mode=json
    """

    name = "lever"
    BASE_URL = "https://api.lever.co/v0/postings"

    def __init__(
        self,
        *,
        company_token: str,
        company: str,
        http: Optional[HttpClient] = None,
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.company_token = company_token.strip()
        self.company = company.strip()
        self.http = http or HttpClient()
        self._owns_http = http is None

    def discover(self) -> Iterable[str]:
        return [self.company_token]

    def fetch(self, item: str) -> list[dict[str, Any]]:
        url = f"{self.BASE_URL}/{item}"
        payload = self.http.get_json(url, params={"mode": "json"})
        polite_sleep(0.1)
        return payload if isinstance(payload, list) else []

    def parse(self, raw: Any, *, item: Optional[str] = None) -> list[JobPosting]:
        if not isinstance(raw, list):
            return []
        jobs: list[JobPosting] = []
        for raw_job in raw:
            job = self._parse_job(raw_job)
            if job is not None:
                jobs.append(job)
        return jobs

    def _parse_job(self, raw_job: dict[str, Any]) -> Optional[JobPosting]:
        title = (raw_job.get("text") or "").strip()
        job_url = (raw_job.get("hostedUrl") or raw_job.get("applyUrl") or "").strip()
        if not title or not job_url:
            return None

        categories = raw_job.get("categories") or {}
        location = categories.get("location")
        commitment = categories.get("commitment")
        description = strip_html(
            "\n".join(
                part
                for part in [
                    raw_job.get("descriptionPlain") or "",
                    raw_job.get("description") or "",
                ]
                if part
            )
        )

        return JobPosting(
            source=self.name,
            source_job_id=str(raw_job.get("id") or job_url),
            title=title,
            company=self.company,
            location=location,
            remote_policy=self._extract_remote_policy(location, description),
            job_url=job_url,
            apply_url=raw_job.get("applyUrl") or job_url,
            description=description,
            posted_at=parse_datetime(
                str(raw_job.get("createdAt") or raw_job.get("updatedAt") or "")
            ),
            scraped_at=utc_now(),
            employment_type=commitment,
            metadata={"raw_payload": raw_job, "company_token": self.company_token},
        )

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
