from __future__ import annotations

from job_hunter.core.models import JobPosting
from job_hunter.storage.jobs_repo import build_fingerprint


def dedupe_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    seen_urls: set[str] = set()
    seen_fingerprints: set[str] = set()
    unique: list[JobPosting] = []

    for job in jobs:
        url_key = (job.job_url or "").strip().lower()
        fingerprint = build_fingerprint(job)

        if url_key and url_key in seen_urls:
            continue
        if fingerprint in seen_fingerprints:
            continue

        if url_key:
            seen_urls.add(url_key)
        seen_fingerprints.add(fingerprint)
        unique.append(job)

    return unique
