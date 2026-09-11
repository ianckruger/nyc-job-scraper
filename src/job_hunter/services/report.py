from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


def generate_markdown_report(
    input_path: Path,
    output_path: Path,
    *,
    title: str = "NYC SWE Job Shortlist",
) -> int:
    """Render a saved job CSV as a company-grouped Markdown shortlist."""
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        jobs = list(csv.DictReader(handle))

    jobs.sort(key=lambda job: (-_score(job), job.get("company", ""), job.get("title", "")))
    by_company: dict[str, list[dict[str, str]]] = defaultdict(list)
    for job in jobs:
        by_company[job.get("company") or "Unknown company"].append(job)

    lines = [f"# {title}", ""]
    lines.append(f"**Jobs:** {len(jobs)}  ")
    lines.append(f"**Companies:** {len(by_company)}  ")
    lines.append(f"**Source CSV:** `{input_path.name}`")
    lines.append("")

    if not jobs:
        lines.append("No jobs matched the selected filters.")
    else:
        for company, company_jobs in sorted(by_company.items()):
            lines.extend([f"## {company} ({len(company_jobs)})", ""])
            for job in company_jobs:
                lines.extend(_render_job(job))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(jobs)


def _render_job(job: dict[str, str]) -> list[str]:
    title = job.get("title") or "Untitled role"
    job_url = job.get("job_url") or job.get("apply_url") or ""
    title_line = f"- [{title}]({job_url})" if job_url else f"- {title}"

    details = [
        f"**Score:** {_score(job):.1f}",
        f"**Location:** {job.get('location') or 'Not listed'}",
    ]
    if job.get("remote_policy"):
        details.append(f"**Work mode:** {job['remote_policy']}")
    if job.get("seniority"):
        details.append(f"**Level:** {job['seniority']}")
    if job.get("posted_at"):
        details.append(f"**Posted:** {job['posted_at'][:10]}")

    lines = [title_line, f"  - {' · '.join(details)}"]
    apply_url = job.get("apply_url")
    if apply_url and apply_url != job_url:
        lines.append(f"  - [Apply]({apply_url})")
    lines.append("")
    return lines


def _score(job: dict[str, Any]) -> float:
    try:
        return float(job.get("score") or 0)
    except (TypeError, ValueError):
        return 0.0
