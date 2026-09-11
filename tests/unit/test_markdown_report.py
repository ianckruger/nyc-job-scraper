from __future__ import annotations

from pathlib import Path

from job_hunter.services.report import generate_markdown_report


def test_generate_markdown_report_groups_jobs_and_sorts_by_score(tmp_path: Path) -> None:
    input_path = tmp_path / "jobs.csv"
    input_path.write_text(
        "company,title,location,remote_policy,job_url,apply_url,posted_at,seniority,score\n"
        "Figma,Software Engineer,New York NY,remote,https://example.test/figma,,2026-09-01,mid,12.5\n"
        "Stripe,Backend Engineer,New York NY,hybrid,https://example.test/stripe,,2026-09-02,junior,10\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "shortlist.md"

    assert generate_markdown_report(input_path, output_path) == 2

    report = output_path.read_text(encoding="utf-8")
    assert "# NYC SWE Job Shortlist" in report
    assert "## Figma (1)" in report
    assert "## Stripe (1)" in report
    assert "[Software Engineer](https://example.test/figma)" in report
    assert report.index("## Figma") < report.index("## Stripe")
