from __future__ import annotations

import csv
from pathlib import Path

from job_hunter.pipeline.enrich import FilterAuditRecord


AUDIT_COLUMNS = [
    "source",
    "source_job_id",
    "company",
    "title",
    "location",
    "remote_policy",
    "job_url",
    "score",
    "is_swe_relevant",
    "is_nyc_relevant",
    "rejection_reasons",
    "description_excerpt",
]


def export_filter_audit(records: list[FilterAuditRecord], output_path: Path) -> int:
    """Write rejected jobs and their active-filter reasons to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record.as_dict())
    return len(records)
