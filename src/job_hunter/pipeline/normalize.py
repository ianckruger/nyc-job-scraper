from __future__ import annotations

from job_hunter.core.models import JobPosting
from job_hunter.taxonomy.titles import normalize_title
from job_hunter.utils.text import normalize_whitespace


def normalize_job(job: JobPosting) -> JobPosting:
    job.title = normalize_title(job.title)
    job.company = normalize_whitespace(job.company)
    job.location = normalize_whitespace(job.location) if job.location else None
    job.remote_policy = normalize_whitespace(job.remote_policy) if job.remote_policy else None
    job.description = normalize_whitespace(job.description)
    job.job_url = job.job_url.strip()
    if job.apply_url:
        job.apply_url = job.apply_url.strip()
    return job


def normalize_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    return [normalize_job(job) for job in jobs]
