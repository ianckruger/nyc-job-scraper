from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional

from job_hunter.storage.db import loads_json, rows_to_dicts


EXPORT_COLUMNS = [
    "id",
    "source",
    "source_job_id",
    "company",
    "title",
    "location",
    "remote_policy",
    "job_url",
    "apply_url",
    "posted_at",
    "scraped_at",
    "salary_min",
    "salary_max",
    "currency",
    "employment_type",
    "seniority",
    "score",
    "is_swe_relevant",
    "is_nyc_relevant",
]


def fetch_jobs(
    conn: sqlite3.Connection,
    *,
    min_score: float = 0.0,
    swe_only: bool = False,
    nyc_only: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    clauses = ["score >= ?"]
    params: list[Any] = [min_score]

    if swe_only:
        clauses.append("is_swe_relevant = 1")
    if nyc_only:
        clauses.append("is_nyc_relevant = 1")

    sql = f"""
        SELECT *
        FROM jobs
        WHERE {' AND '.join(clauses)}
        ORDER BY score DESC, posted_at DESC, company ASC, title ASC
    """
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    return rows_to_dicts(rows)


def export_csv(
    conn: sqlite3.Connection,
    output_path: Path,
    *,
    min_score: float = 0.0,
    swe_only: bool = False,
    nyc_only: bool = False,
    limit: int | None = None,
) -> int:
    jobs = fetch_jobs(
        conn,
        min_score=min_score,
        swe_only=swe_only,
        nyc_only=nyc_only,
        limit=limit,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for job in jobs:
            writer.writerow({column: job.get(column) for column in EXPORT_COLUMNS})

    return len(jobs)


def export_json(
    conn: sqlite3.Connection,
    output_path: Path,
    *,
    min_score: float = 0.0,
    swe_only: bool = False,
    nyc_only: bool = False,
    limit: int | None = None,
) -> int:
    jobs = fetch_jobs(
        conn,
        min_score=min_score,
        swe_only=swe_only,
        nyc_only=nyc_only,
        limit=limit,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(jobs, handle, ensure_ascii=False, indent=2, default=str)
    return len(jobs)
