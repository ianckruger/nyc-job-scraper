from __future__ import annotations

from job_hunter.core.models import JobPosting


def rank_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    return sorted(
        jobs,
        key=lambda job: (
            -job.score,
            job.posted_at.isoformat() if job.posted_at else "",
            job.company.lower(),
            job.title.lower(),
        ),
    )
