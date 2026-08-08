from __future__ import annotations

from dataclasses import dataclass

from job_hunter.config.logging import get_logger
from job_hunter.config.settings import Settings
from job_hunter.core.models import JobPosting
from job_hunter.pipeline.dedupe import dedupe_jobs
from job_hunter.pipeline.discover import discover_jobs, fetch_raw, parse_jobs
from job_hunter.pipeline.enrich import enrich_jobs
from job_hunter.pipeline.normalize import normalize_jobs
from job_hunter.pipeline.rank import rank_jobs
from job_hunter.sources.base import BaseJobSource
from job_hunter.storage.jobs_repo import JobsRepository, utc_now_iso

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    source_name: str
    discovered: int
    parsed: int
    saved: int
    filtered_out: int


@dataclass
class RunSummary:
    results: list[PipelineResult]
    total_saved: int


def run_source_pipeline(
    source: BaseJobSource,
    repo: JobsRepository,
    settings: Settings,
) -> PipelineResult:
    source_label = f"{source.name}:{getattr(source, 'company', source.name)}"
    logger.info("Running source pipeline for %s", source_label)

    items = discover_jobs(source)
    payloads = fetch_raw(source, items)
    parsed_jobs = parse_jobs(source, payloads)
    normalized = normalize_jobs(parsed_jobs)
    deduped = dedupe_jobs(normalized)
    enriched = enrich_jobs(deduped, settings)
    ranked = rank_jobs(enriched)

    filtered_out = len(deduped) - len(enriched)
    saved = 0
    for job in ranked:
        repo.upsert_job(job)
        saved += 1

    return PipelineResult(
        source_name=source_label,
        discovered=len(items),
        parsed=len(parsed_jobs),
        saved=saved,
        filtered_out=filtered_out,
    )


def run_pipeline(
    sources: list[BaseJobSource],
    repo: JobsRepository,
    settings: Settings,
) -> RunSummary:
    results: list[PipelineResult] = []
    total_saved = 0

    for source in sources:
        try:
            result = run_source_pipeline(source, repo, settings)
            results.append(result)
            total_saved += result.saved
        except Exception as exc:
            logger.exception("Pipeline failed for source %s: %s", source.name, exc)
            results.append(
                PipelineResult(
                    source_name=source.name,
                    discovered=0,
                    parsed=0,
                    saved=0,
                    filtered_out=0,
                )
            )
        finally:
            close = getattr(source, "close", None)
            if callable(close):
                close()

    return RunSummary(results=results, total_saved=total_saved)


def record_source_run(
    repo: JobsRepository,
    source_name: str,
    *,
    jobs_found: int,
    jobs_saved: int,
    status: str = "completed",
    error_message: str | None = None,
) -> None:
    repo.conn.execute(
        """
        INSERT INTO source_runs (
            source_name, started_at, finished_at, status, jobs_found, jobs_saved, error_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_name,
            utc_now_iso(),
            utc_now_iso(),
            status,
            jobs_found,
            jobs_saved,
            error_message,
        ),
    )
    repo.conn.commit()
