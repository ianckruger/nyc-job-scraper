from __future__ import annotations
import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import Iterable, Optional

from job_hunter.core.models import JobPosting
from job_hunter.storage.db import dumps_json


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_fingerprint(job: JobPosting) -> str:
    base = "|".join(
        [
            (job.company or "").strip().lower(),
            (job.title or "").strip().lower(),
            (job.location or "").strip().lower(),
            (job.job_url or "").strip().lower(),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


class JobsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert_job(self, job: JobPosting) -> int:
        """
        Insert or update a job using source+source_job_id if available,
        otherwise fall back to job_url uniqueness.
        """
        now = utc_now_iso()
        raw_payload = dumps_json(job.metadata.get("raw_payload")) if job.metadata else None
        metadata = dumps_json(job.metadata)

        existing_id = self._find_existing_job_id(job)
        if existing_id is not None:
            self.conn.execute(
                """
                UPDATE jobs
                SET company = ?,
                    title = ?,
                    location = ?,
                    remote_policy = ?,
                    job_url = ?,
                    apply_url = ?,
                    description = ?,
                    posted_at = ?,
                    scraped_at = ?,
                    updated_at = ?,
                    salary_min = ?,
                    salary_max = ?,
                    currency = ?,
                    employment_type = ?,
                    seniority = ?,
                    score = ?,
                    is_swe_relevant = ?,
                    is_nyc_relevant = ?,
                    raw_payload = ?,
                    metadata = ?
                WHERE id = ?
                """,
                (
                    job.company,
                    job.title,
                    job.location,
                    job.remote_policy,
                    job.job_url,
                    job.apply_url,
                    job.description,
                    job.posted_at.isoformat() if job.posted_at else None,
                    job.scraped_at.isoformat() if job.scraped_at else now,
                    now,
                    job.salary_min,
                    job.salary_max,
                    job.currency,
                    job.employment_type,
                    job.seniority,
                    job.score,
                    int(job.is_swe_relevant),
                    int(job.is_nyc_relevant),
                    raw_payload,
                    metadata,
                    existing_id,
                ),
            )
            self.conn.commit()
            return existing_id

        cursor = self.conn.execute(
            """
            INSERT INTO jobs (
                source, source_job_id, company, title, location, remote_policy,
                job_url, apply_url, description, posted_at, scraped_at, updated_at,
                salary_min, salary_max, currency, employment_type, seniority,
                score, is_swe_relevant, is_nyc_relevant, raw_payload, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.source,
                job.source_job_id,
                job.company,
                job.title,
                job.location,
                job.remote_policy,
                job.job_url,
                job.apply_url,
                job.description,
                job.posted_at.isoformat() if job.posted_at else None,
                job.scraped_at.isoformat() if job.scraped_at else now,
                None,
                job.salary_min,
                job.salary_max,
                job.currency,
                job.employment_type,
                job.seniority,
                job.score,
                int(job.is_swe_relevant),
                int(job.is_nyc_relevant),
                raw_payload,
                metadata,
            ),
        )
        job_id = int(cursor.lastrowid)
        self.conn.commit()
        self._save_fingerprint(job_id, build_fingerprint(job))
        self._save_tags(job_id, job.tags)
        return job_id

    def _find_existing_job_id(self, job: JobPosting) -> Optional[int]:
        if job.source_job_id:
            row = self.conn.execute(
                "SELECT id FROM jobs WHERE source = ? AND source_job_id = ?",
                (job.source, job.source_job_id),
            ).fetchone()
            if row:
                return int(row["id"])

        row = self.conn.execute(
            "SELECT id FROM jobs WHERE job_url = ?",
            (job.job_url,),
        ).fetchone()
        if row:
            return int(row["id"])

        return None

    def _save_tags(self, job_id: int, tags: Iterable[str]) -> None:
        for tag in tags:
            self.conn.execute(
                "INSERT OR IGNORE INTO job_tags (job_id, tag) VALUES (?, ?)",
                (job_id, tag),
            )
        self.conn.commit()

    def _save_fingerprint(self, job_id: int, fingerprint: str) -> None:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO job_fingerprints (fingerprint, job_id, created_at)
            VALUES (?, ?, ?)
            """,
            (fingerprint, job_id, utc_now_iso()),
        )
        self.conn.commit()