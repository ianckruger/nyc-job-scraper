from __future__ import annotations

import sqlite3
from typing import Any


def dashboard_summary(conn: sqlite3.Connection) -> dict[str, Any]:
    total = conn.execute("SELECT COUNT(*) AS count FROM jobs").fetchone()["count"]
    swe = conn.execute(
        "SELECT COUNT(*) AS count FROM jobs WHERE is_swe_relevant = 1"
    ).fetchone()["count"]
    nyc = conn.execute(
        "SELECT COUNT(*) AS count FROM jobs WHERE is_nyc_relevant = 1"
    ).fetchone()["count"]
    top_companies = conn.execute(
        """
        SELECT company, COUNT(*) AS count
        FROM jobs
        GROUP BY company
        ORDER BY count DESC, company ASC
        LIMIT 10
        """
    ).fetchall()

    return {
        "total_jobs": total,
        "swe_jobs": swe,
        "nyc_jobs": nyc,
        "top_companies": [dict(row) for row in top_companies],
    }
