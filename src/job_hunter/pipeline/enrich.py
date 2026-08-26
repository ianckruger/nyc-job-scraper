from __future__ import annotations

from dataclasses import asdict, dataclass

from job_hunter.config.settings import Settings
from job_hunter.core.models import JobPosting
from job_hunter.filters.nyc import is_nyc_job, nyc_score, mentions_nyc
from job_hunter.filters.remote import remote_score
from job_hunter.filters.seniority import infer_seniority, seniority_score
from job_hunter.filters.swe import is_swe_role, swe_score
from job_hunter.taxonomy.skills import extract_skills


@dataclass(frozen=True)
class FilterMetrics:
    """Counts produced while evaluating one source's deduplicated jobs."""

    input_jobs: int
    swe_matches: int
    nyc_matches: int
    both_matches: int
    rejected_not_swe: int
    rejected_not_nyc: int
    rejected_both: int
    passed_active_filters: int

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


def enrich_job(job: JobPosting, settings: Settings) -> JobPosting:
    job.is_swe_relevant = is_swe_role(job.title, job.description)
    # job.is_nyc_relevant = is_nyc_job(job.location, job.description)
    job.is_nyc_relevant = is_nyc_job(job.location)
    job.metadata["mentions_nyc"] = mentions_nyc(job.description)


    if not job.seniority:
        job.seniority = infer_seniority(job.title)

    skills = extract_skills(job.description)
    for skill in skills:
        if skill not in job.tags:
            job.tags.append(skill)

    score = 0.0
    score += swe_score(job.title, job.description)
    # score += nyc_score(job.location, job.description)
    score += nyc_score(job.location)
    score += remote_score(job.remote_policy, job.location, job.description)
    score += seniority_score(job.seniority)
    score += min(len(skills) * 0.5, 5.0)
    job.score = round(score, 2)

    return job


def enrich_and_filter_jobs(
    jobs: list[JobPosting], settings: Settings
) -> tuple[list[JobPosting], FilterMetrics]:
    enriched = [enrich_job(job, settings) for job in jobs]
    swe_matches = sum(job.is_swe_relevant for job in enriched)
    nyc_matches = sum(job.is_nyc_relevant for job in enriched)
    both_matches = sum(job.is_swe_relevant and job.is_nyc_relevant for job in enriched)

    filtered = enriched
    if settings.swe_only:
        filtered = [job for job in filtered if job.is_swe_relevant]
    if settings.nyc_only:
        filtered = [job for job in filtered if job.is_nyc_relevant]

    metrics = FilterMetrics(
        input_jobs=len(enriched),
        swe_matches=swe_matches,
        nyc_matches=nyc_matches,
        both_matches=both_matches,
        rejected_not_swe=len(enriched) - swe_matches,
        rejected_not_nyc=len(enriched) - nyc_matches,
        rejected_both=sum(
            not job.is_swe_relevant and not job.is_nyc_relevant for job in enriched
        ),
        passed_active_filters=len(filtered),
    )
    return filtered, metrics


def enrich_jobs(jobs: list[JobPosting], settings: Settings) -> list[JobPosting]:
    """Backward-compatible shortcut for callers that only need eligible jobs."""
    enriched, _ = enrich_and_filter_jobs(jobs, settings)
    return enriched
