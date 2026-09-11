from __future__ import annotations

from pathlib import Path

from job_hunter.config.settings import Settings
from job_hunter.core.models import JobPosting
from job_hunter.pipeline.enrich import enrich_filter_and_audit_jobs
from job_hunter.services.audit import export_filter_audit


def make_job(title: str, location: str) -> JobPosting:
    return JobPosting(
        source="test",
        source_job_id=f"{title}-{location}",
        company="Example",
        title=title,
        location=location,
        job_url=f"https://example.test/{title}-{location}",
        description="Role description.",
    )


def test_audit_records_active_filter_reasons(tmp_path: Path) -> None:
    jobs = [
        make_job("Software Engineer", "New York, NY"),
        make_job("Software Engineer", "Bellevue, WA"),
        make_job("Account Specialist", "New York, NY"),
        make_job("Senior Software Engineer", "Bellevue, WA"),
    ]

    eligible, metrics, audit_records = enrich_filter_and_audit_jobs(
        jobs,
        Settings.model_construct(swe_only=True, nyc_only=True),
        collect_audit=True,
    )

    assert len(eligible) == 1
    assert metrics.passed_active_filters == 1
    assert len(audit_records) == 3

    by_title = {record.title: record for record in audit_records}
    assert by_title["Software Engineer"].rejection_reasons == [
        "NYC: location has no NYC signal"
    ]
    assert by_title["Account Specialist"].rejection_reasons == [
        "SWE: title has no SWE keyword"
    ]
    assert by_title["Senior Software Engineer"].rejection_reasons == [
        "SWE: title contains excluded phrase: senior",
        "NYC: location has no NYC signal",
    ]

    output_path = tmp_path / "audit.csv"
    assert export_filter_audit(audit_records, output_path) == 3
    assert "rejection_reasons" in output_path.read_text(encoding="utf-8")
