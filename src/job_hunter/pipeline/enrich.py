from __future__ import annotations

from job_hunter.config.settings import Settings
from job_hunter.core.models import JobPosting
from job_hunter.filters.nyc import is_nyc_job, nyc_score
from job_hunter.filters.remote import remote_score
from job_hunter.filters.seniority import infer_seniority, seniority_score
from job_hunter.filters.swe import is_swe_role, swe_score
from job_hunter.taxonomy.skills import extract_skills


def enrich_job(job: JobPosting, settings: Settings) -> JobPosting:
    job.is_swe_relevant = is_swe_role(job.title, job.description)
    job.is_nyc_relevant = is_nyc_job(job.location, job.description)

    if not job.seniority:
        job.seniority = infer_seniority(job.title)

    skills = extract_skills(job.description)
    for skill in skills:
        if skill not in job.tags:
            job.tags.append(skill)

    score = 0.0
    score += swe_score(job.title, job.description)
    score += nyc_score(job.location, job.description)
    score += remote_score(job.remote_policy, job.location, job.description)
    score += seniority_score(job.seniority)
    score += min(len(skills) * 0.5, 5.0)
    job.score = round(score, 2)

    return job


def enrich_jobs(jobs: list[JobPosting], settings: Settings) -> list[JobPosting]:
    enriched = [enrich_job(job, settings) for job in jobs]

    if settings.swe_only:
        enriched = [job for job in enriched if job.is_swe_relevant]
    if settings.nyc_only:
        enriched = [job for job in enriched if job.is_nyc_relevant]

    return enriched
