from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional

DB_PATH = Path("data/job_hunter.db")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    jobs_found INTEGER NOT NULL DEFAULT 0,
    jobs_saved INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    source_job_id TEXT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    remote_policy TEXT,
    job_url TEXT NOT NULL,
    apply_url TEXT,
    description TEXT,
    posted_at TEXT,
    scraped_at TEXT NOT NULL,
    updated_at TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    currency TEXT,
    employment_type TEXT,
    seniority TEXT,
    score REAL NOT NULL DEFAULT 0.0,
    is_swe_relevant INTEGER NOT NULL DEFAULT 0,
    is_nyc_relevant INTEGER NOT NULL DEFAULT 0,
    raw_payload TEXT,
    metadata TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_source_source_job_id
ON jobs(source, source_job_id)
WHERE source_job_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_job_url
ON jobs(job_url);

CREATE INDEX IF NOT EXISTS idx_jobs_company
ON jobs(company);

CREATE INDEX IF NOT EXISTS idx_jobs_title
ON jobs(title);

CREATE INDEX IF NOT EXISTS idx_jobs_score
ON jobs(score);

CREATE INDEX IF NOT EXISTS idx_jobs_posted_at
ON jobs(posted_at);

CREATE TABLE IF NOT EXISTS job_tags (
    job_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (job_id, tag),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_fingerprints (
    fingerprint TEXT PRIMARY KEY,
    job_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);
"""

def connect(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()

def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]

def dumps_json(value: Any) -> Optional[str]:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, default=str)

def loads_json(value: Optional[str]) -> Any:
    if value is None:
        return None
    return json.loads(value)