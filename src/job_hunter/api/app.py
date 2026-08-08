from __future__ import annotations
from fastapi import FastAPI, Query
from job_hunter.config.settings import get_settings
from job_hunter.services.dashboard import dashboard_summary
from job_hunter.services.search import search_jobs
from job_hunter.storage.db import connect, init_db
app = FastAPI(title="Job Hunter API")
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
@app.get("/jobs")
def jobs(
    q: str = Query("", alias="query"),
    limit: int = Query(20, ge=1, le=200),
) -> list[dict]:
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    return search_jobs(
        conn,
        query=q,
        swe_only=settings.swe_only,
        nyc_only=settings.nyc_only,
        limit=limit,
    )
@app.get("/stats")
def stats() -> dict:
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    return dashboard_summary(conn)