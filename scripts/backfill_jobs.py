from __future__ import annotations
from job_hunter.config.settings import get_settings
from job_hunter.pipeline.runner import run_pipeline
from job_hunter.sources import build_sources
from job_hunter.storage.db import connect, init_db
from job_hunter.storage.jobs_repo import JobsRepository
def main() -> None:
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    repo = JobsRepository(conn)
    adapters = build_sources(settings.source_list)
    summary = run_pipeline(adapters, repo, settings)
    print(f"Saved {summary.total_saved} jobs")
if __name__ == "__main__":
    main()