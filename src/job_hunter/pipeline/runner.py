from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from job_hunter.config.logging import get_logger
from job_hunter.config.settings import Settings
from job_hunter.core.models import JobPosting
from job_hunter.pipeline.dedupe import dedupe_jobs
from job_hunter.pipeline.discover import discover_jobs, fetch_raw, parse_jobs
from job_hunter.pipeline.enrich import (
    FilterAuditRecord,
    FilterMetrics,
    enrich_filter_and_audit_jobs,
)
from job_hunter.pipeline.normalize import normalize_jobs
from job_hunter.pipeline.rank import rank_jobs
from job_hunter.sources.base import BaseJobSource
from job_hunter.storage.db import dumps_json
from job_hunter.storage.jobs_repo import JobsRepository, utc_now_iso

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    source_name: str
    discovered: int
    parsed: int
    deduped: int
    filter_metrics: FilterMetrics
    saved: int
    filtered_out: int
    fetch_seconds: float
    parse_seconds: float
    normalize_dedupe_seconds: float
    enrich_filter_seconds: float
    store_seconds: float
    total_seconds: float
    audit_records: list[FilterAuditRecord]

    def metrics_dict(self) -> dict[str, Any]:
        return {
            "discovered": self.discovered,
            "parsed": self.parsed,
            "deduped": self.deduped,
            "saved": self.saved,
            "filtered_out": self.filtered_out,
            "filters": self.filter_metrics.as_dict(),
            "timings_seconds": {
                "fetch": round(self.fetch_seconds, 3),
                "parse": round(self.parse_seconds, 3),
                "normalize_dedupe": round(self.normalize_dedupe_seconds, 3),
                "enrich_filter": round(self.enrich_filter_seconds, 3),
                "store": round(self.store_seconds, 3),
                "total": round(self.total_seconds, 3),
            },
        }


@dataclass
class RunSummary:
    results: list[PipelineResult]
    total_saved: int
    audit_records: list[FilterAuditRecord]


def run_source_pipeline(
    source: BaseJobSource,
    repo: JobsRepository,
    settings: Settings,
    *,
    collect_audit: bool = False,
) -> PipelineResult:
    total_started = perf_counter()
    source_label = f"{source.name}:{getattr(source, 'company', source.name)}"
    logger.info("Running source pipeline for %s", source_label)

    items = discover_jobs(source)
    fetch_started = perf_counter()
    payloads = fetch_raw(source, items)
    fetch_seconds = perf_counter() - fetch_started

    parse_started = perf_counter()
    parsed_jobs = parse_jobs(source, payloads)
    parse_seconds = perf_counter() - parse_started

    normalize_dedupe_started = perf_counter()
    normalized = normalize_jobs(parsed_jobs)
    deduped = dedupe_jobs(normalized)
    normalize_dedupe_seconds = perf_counter() - normalize_dedupe_started

    enrich_filter_started = perf_counter()
    enriched, filter_metrics, audit_records = enrich_filter_and_audit_jobs(
        deduped,
        settings,
        collect_audit=collect_audit,
    )
    ranked = rank_jobs(enriched)
    enrich_filter_seconds = perf_counter() - enrich_filter_started

    filtered_out = len(deduped) - len(enriched)
    store_started = perf_counter()
    saved = 0
    for job in ranked:
        repo.upsert_job(job)
        saved += 1
    store_seconds = perf_counter() - store_started

    return PipelineResult(
        source_name=source_label,
        discovered=len(items),
        parsed=len(parsed_jobs),
        deduped=len(deduped),
        filter_metrics=filter_metrics,
        saved=saved,
        filtered_out=filtered_out,
        fetch_seconds=fetch_seconds,
        parse_seconds=parse_seconds,
        normalize_dedupe_seconds=normalize_dedupe_seconds,
        enrich_filter_seconds=enrich_filter_seconds,
        store_seconds=store_seconds,
        total_seconds=perf_counter() - total_started,
        audit_records=audit_records,
    )


def run_pipeline(
    sources: list[BaseJobSource],
    repo: JobsRepository,
    settings: Settings,
    *,
    collect_audit: bool = False,
) -> RunSummary:
    results: list[PipelineResult] = []
    total_saved = 0
    audit_records: list[FilterAuditRecord] = []

    for source in sources:
        try:
            result = run_source_pipeline(source, repo, settings, collect_audit=collect_audit)
            results.append(result)
            total_saved += result.saved
            audit_records.extend(result.audit_records)
        except Exception as exc:
            logger.exception("Pipeline failed for source %s: %s", source.name, exc)
            results.append(
                PipelineResult(
                    source_name=source.name,
                    discovered=0,
                    parsed=0,
                    deduped=0,
                    filter_metrics=FilterMetrics(0, 0, 0, 0, 0, 0, 0, 0),
                    saved=0,
                    filtered_out=0,
                    fetch_seconds=0.0,
                    parse_seconds=0.0,
                    normalize_dedupe_seconds=0.0,
                    enrich_filter_seconds=0.0,
                    store_seconds=0.0,
                    total_seconds=0.0,
                    audit_records=[],
                )
            )
        finally:
            close = getattr(source, "close", None)
            if callable(close):
                close()

    return RunSummary(
        results=results,
        total_saved=total_saved,
        audit_records=audit_records,
    )


def record_source_run(
    repo: JobsRepository,
    source_name: str,
    *,
    jobs_found: int,
    jobs_saved: int,
    metrics: dict[str, Any] | None = None,
    status: str = "completed",
    error_message: str | None = None,
) -> None:
    repo.conn.execute(
        """
        INSERT INTO source_runs (
            source_name, started_at, finished_at, status, jobs_found, jobs_saved, error_message, metrics_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_name,
            utc_now_iso(),
            utc_now_iso(),
            status,
            jobs_found,
            jobs_saved,
            error_message,
            dumps_json(metrics),
        ),
    )
    repo.conn.commit()
