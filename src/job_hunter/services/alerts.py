from __future__ import annotations

import sqlite3
from typing import Any

from job_hunter.services.search import search_jobs


def new_job_alerts(
    conn: sqlite3.Connection,
    *,
    since_scraped_at: str | None = None,
    min_score: float = 5.0,
    limit: int = 20,
) -> list[dict[str, Any]]:
    clauses = ["score >= ?"]
    params: list[Any] = [min_score]

    if since_scraped_at:
        clauses.append("scraped_at >= ?")
        params.append(since_scraped_at)

    sql = f"""
        SELECT *
        FROM jobs
        WHERE {' AND '.join(clauses)}
        ORDER BY scraped_at DESC, score DESC
        LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]
