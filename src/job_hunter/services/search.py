from __future__ import annotations

import sqlite3
from typing import Any

from job_hunter.services.export import fetch_jobs


def search_jobs(
    conn: sqlite3.Connection,
    *,
    query: str = "",
    min_score: float = 0.0,
    swe_only: bool = False,
    nyc_only: bool = False,
    limit: int = 50,
) -> list[dict[str, Any]]:
    jobs = fetch_jobs(
        conn,
        min_score=min_score,
        swe_only=swe_only,
        nyc_only=nyc_only,
        limit=limit * 5,
    )
    if not query.strip():
        return jobs[:limit]

    needle = query.lower()
    filtered = [
        job
        for job in jobs
        if needle in f"{job.get('title', '')} {job.get('company', '')} {job.get('description', '')}".lower()
    ]
    return filtered[:limit]
