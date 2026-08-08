from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any, Iterable, Iterator, Optional

from job_hunter.core.models import JobPosting


class BaseJobSource(ABC):
    """
    Base contract for any job source adapter.

    Every source should:
    - discover raw job identifiers or URLs
    - fetch raw payloads
    - parse raw payloads into JobPosting objects
    """

    name: str = "base"

    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = enabled

    @abstractmethod
    def discover(self) -> Iterable[str]:
        """
        Return source-specific identifiers or URLs for postings.
        Example values:
        - Greenhouse job board URLs
        - Lever posting URLs
        - Workday requisition IDs
        """

    @abstractmethod
    def fetch(self, item: str) -> Any:
        """
        Fetch raw data for a discovered item.

        This can return:
        - str for HTML
        - dict for JSON
        - bytes for binary payloads
        """

    @abstractmethod
    def parse(self, raw: Any, *, item: Optional[str] = None) -> list[JobPosting]:
        """
        Convert raw source data into canonical JobPosting objects.
        A single raw page may produce one or more postings.
        """

    def scrape(self) -> list[JobPosting]:
        """
        Full end-to-end extraction for one source.
        """
        if not self.enabled:
            return []

        results: list[JobPosting] = []
        for item in self.discover():
            raw = self.fetch(item)
            results.extend(self.parse(raw, item=item))
        return results

    def iter_jobs(self) -> Iterator[JobPosting]:
        """
        Streaming version of scrape() for pipelines that want to process
        jobs one at a time.
        """
        for job in self.scrape():
            yield job

    def make_source_job_id(self, item: str, raw: Any | None = None) -> str:
        """
        Build a stable source-level identifier when the source does not
        provide a clean requisition ID.
        """
        return item.strip()

    def enrich_metadata(self, job: JobPosting, raw: Any | None = None) -> JobPosting:
        """
        Hook for source-specific metadata enrichment before storage.
        Override in subclasses only when needed.
        """
        return job

    def postprocess(self, job: JobPosting, raw: Any | None = None) -> JobPosting:
        """
        Final per-source adjustment point.
        Useful for filling source name, source_job_id, or metadata.
        """
        if not job.source:
            job.source = self.name
        return self.enrich_metadata(job, raw)

    def safe_parse(self, raw: Any, *, item: Optional[str] = None) -> list[JobPosting]:
        """
        Optional helper for wrappers or runners that want parsing failures
        to be isolated per item.
        """
        try:
            jobs = self.parse(raw, item=item)
            return [self.postprocess(job, raw) for job in jobs]
        except Exception:
            return []


class APISource(BaseJobSource):
    """
    Convenience base for sources that primarily fetch JSON.
    """

    def parse_json(self, payload: dict[str, Any], *, item: Optional[str] = None) -> list[JobPosting]:
        raise NotImplementedError


class HTMLSource(BaseJobSource):
    """
    Convenience base for sources that primarily fetch HTML.
    """

    def parse_html(self, html: str, *, item: Optional[str] = None) -> list[JobPosting]:
        raise NotImplementedError