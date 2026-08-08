from __future__ import annotations
from pathlib import Path
from job_hunter.config.settings import get_settings
from job_hunter.services.export import export_csv
from job_hunter.storage.db import connect, init_db
def main() -> None:
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    output = Path("data/exports/jobs.csv")
    count = export_csv(
        conn,
        output,
        swe_only=settings.swe_only,
        nyc_only=settings.nyc_only,
    )
    print(f"Exported {count} jobs to {output}")
if __name__ == "__main__":
    main()