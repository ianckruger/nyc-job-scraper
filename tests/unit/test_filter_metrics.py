from __future__ import annotations

import pytest

from job_hunter.config.settings import Settings
from job_hunter.core.models import JobPosting
from job_hunter.pipeline.enrich import enrich_and_filter_jobs


def make_job(title: str, location: str) -> JobPosting:
    return JobPosting(
        source="test",
        source_job_id=f"{title}-{location}",
        company="Example",
        title=title,
        location=location,
        job_url=f"https://example.test/{title}-{location}",
    )


@pytest.mark.parametrize(
    ("swe_only", "nyc_only", "expected_passed"),
    [
        (False, False, 4),
        (True, False, 2),
        (False, True, 2),
        (True, True, 1),
    ],
)
def test_filter_metrics_explain_active_filter_results(
    swe_only: bool, nyc_only: bool, expected_passed: int
) -> None:
    jobs = [
        make_job("Software Engineer", "New York, NY"),
        make_job("Software Engineer", "Bellevue, WA"),
        make_job("Account Manager", "New York, NY"),
        make_job("Account Manager", "Bellevue, WA"),
    ]

    eligible, metrics = enrich_and_filter_jobs(
        jobs,
        Settings.model_construct(swe_only=swe_only, nyc_only=nyc_only),
    )

    assert len(eligible) == expected_passed
    assert metrics.input_jobs == 4
    assert metrics.swe_matches == 2
    assert metrics.nyc_matches == 2
    assert metrics.both_matches == 1
    assert metrics.rejected_not_swe == 2
    assert metrics.rejected_not_nyc == 2
    assert metrics.rejected_both == 1
    assert metrics.passed_active_filters == expected_passed
