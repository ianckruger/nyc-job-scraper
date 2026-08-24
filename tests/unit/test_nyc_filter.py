from __future__ import annotations

import pytest

from job_hunter.config.settings import Settings
from job_hunter.core.models import JobPosting
from job_hunter.filters.nyc import is_nyc_job, normalize_location
from job_hunter.pipeline.enrich import enrich_job


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        ("New York, NY", True),
        ("New York City, NY", True),
        ("Austin; New York City; San Francisco", True),
        ("San Francisco, CA • New York, NY", True),
        ("Bellevue, WA", False),
        ("United States", False),
        ("US Remote", False),
        (None, False),
    ],
)
def test_is_nyc_job_uses_location_signals(location: str | None, expected: bool) -> None:
    assert is_nyc_job(location) is expected


def test_normalize_location_handles_display_separators() -> None:
    assert normalize_location("  San Francisco  •  New York, NY | United States  ") == (
        "san francisco ; new york, ny ; united states"
    )


def test_enrichment_does_not_use_description_as_nyc_location_evidence() -> None:
    job = JobPosting(
        source="test",
        source_job_id="1",
        company="Example",
        title="Software Engineer",
        location="Bellevue, WA",
        job_url="https://example.test/jobs/1",
        description="Our company has a large New York office.",
    )

    enrich_job(job, Settings())

    assert job.is_nyc_relevant is False
    assert job.metadata["mentions_nyc"] is True
