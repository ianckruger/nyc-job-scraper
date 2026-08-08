from job_hunter.sources.greenhouse import GreenhouseSource
from job_hunter.storage.db import connect, init_db
from job_hunter.storage.jobs_repo import JobsRepository

def main() -> None:
    conn = connect()
    init_db(conn)
    repo = JobsRepository(conn)

    source = GreenhouseSource()
    jobs = source.scrape()

    for job in jobs:
        repo.upsert_job(job)

if __name__ == "__main__":
    main()