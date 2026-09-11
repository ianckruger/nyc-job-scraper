from __future__ import annotations

from dataclasses import asdict, dataclass

from job_hunter.config.settings import Settings
from job_hunter.core.models import JobPosting
from job_hunter.filters.nyc import is_nyc_job, mentions_nyc, nyc_rejection_reason, nyc_score
from job_hunter.filters.remote import remote_score
from job_hunter.filters.seniority import infer_seniority, seniority_score
from job_hunter.filters.swe import is_swe_role, swe_rejection_reason, swe_score
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


@dataclass(frozen=True)
class FilterAuditRecord:
    source: str
    source_job_id: str | None
    company: str
    title: str
    location: str | None
    remote_policy: str | None
    job_url: str
    score: float
    is_swe_relevant: bool
    is_nyc_relevant: bool
    rejection_reasons: list[str]
    description_excerpt: str

    @classmethod
    def from_job(cls, job: JobPosting, reasons: list[str]) -> "FilterAuditRecord":
        return cls(
            source=job.source,
            source_job_id=job.source_job_id,
            company=job.company,
            title=job.title,
            location=job.location,
            remote_policy=job.remote_policy,
            job_url=job.job_url,
            score=job.score,
            is_swe_relevant=job.is_swe_relevant,
            is_nyc_relevant=job.is_nyc_relevant,
            rejection_reasons=reasons,
            description_excerpt=job.description[:280],
        )

    def as_dict(self) -> dict[str, str | float | bool | None]:
        data = asdict(self)
        data["rejection_reasons"] = "; ".join(self.rejection_reasons)
        return data


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
    enriched, metrics, _ = enrich_filter_and_audit_jobs(jobs, settings, collect_audit=False)
    return enriched, metrics


def enrich_filter_and_audit_jobs(
    jobs: list[JobPosting], settings: Settings, *, collect_audit: bool
) -> tuple[list[JobPosting], FilterMetrics, list[FilterAuditRecord]]:
    enriched = [enrich_job(job, settings) for job in jobs]
    swe_matches = sum(job.is_swe_relevant for job in enriched)
    nyc_matches = sum(job.is_nyc_relevant for job in enriched)
    both_matches = sum(job.is_swe_relevant and job.is_nyc_relevant for job in enriched)

    filtered: list[JobPosting] = []
    audit_records: list[FilterAuditRecord] = []
    for job in enriched:
        reasons: list[str] = []
        if settings.swe_only and not job.is_swe_relevant:
            reasons.append(f"SWE: {swe_rejection_reason(job.title)}")
        if settings.nyc_only and not job.is_nyc_relevant:
            reasons.append(f"NYC: {nyc_rejection_reason(job.location)}")

        if reasons:
            if collect_audit:
                audit_records.append(FilterAuditRecord.from_job(job, reasons))
        else:
            filtered.append(job)

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
    return filtered, metrics, audit_records


def enrich_jobs(jobs: list[JobPosting], settings: Settings) -> list[JobPosting]:
    """Backward-compatible shortcut for callers that only need eligible jobs."""
    enriched, _ = enrich_and_filter_jobs(jobs, settings)
    return enriched
