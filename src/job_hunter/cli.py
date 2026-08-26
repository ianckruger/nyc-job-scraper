from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.table import Table

from job_hunter.config.logging import configure_logging, get_logger
from job_hunter.config.settings import get_settings
from job_hunter.pipeline.runner import record_source_run, run_pipeline
from job_hunter.services.dashboard import dashboard_summary
from job_hunter.services.export import export_csv, export_json
from job_hunter.services.search import search_jobs
from job_hunter.sources import build_sources
from job_hunter.storage.db import connect, init_db
from job_hunter.storage.jobs_repo import JobsRepository

app = typer.Typer(help="NYC SWE job aggregation pipeline")
logger = get_logger(__name__)


@app.callback()
def main(
    ctx: typer.Context,
    log_level: Optional[str] = typer.Option(None, "--log-level", help="Override log level"),
) -> None:
    settings = get_settings()
    configure_logging(log_level or settings.log_level)
    ctx.obj = settings


@app.command()
def initdb() -> None:
    """Create or migrate the local database."""
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    print(f"[green]Initialized database[/green] at {settings.db_path}")


@app.command()
def config() -> None:
    """Show resolved runtime configuration."""
    settings = get_settings()
    print("[bold]Resolved settings[/bold]")
    print(f"app_name: {settings.app_name}")
    print(f"env: {settings.env}")
    print(f"db_path: {settings.db_path}")
    print(f"data_dir: {settings.data_dir}")
    print(f"source_list: {settings.source_list}")
    print(f"swe_only: {settings.swe_only}")
    print(f"nyc_only: {settings.nyc_only}")


@app.command()
def run(
    source: list[str] = typer.Option(
        [],
        "--source",
        "-s",
        help="Source to run. Repeat the flag to run multiple sources.",
    ),
) -> None:
    """
    Run the pipeline end-to-end:
    discover -> fetch -> parse -> normalize -> dedupe -> enrich -> rank -> store
    """
    settings = get_settings()
    selected_sources = source or settings.source_list

    logger.info("Starting pipeline", extra={"sources": selected_sources})

    conn = connect(settings.db_path)
    init_db(conn)
    repo = JobsRepository(conn)

    adapters = build_sources(selected_sources)
    if not adapters:
        print("[red]No source adapters configured. Check config/sources.yaml.[/red]")
        raise typer.Exit(code=1)

    summary = run_pipeline(adapters, repo, settings)

    table = Table(title="Pipeline Results")
    table.add_column("Source")
    table.add_column("Discovered", justify="right")
    table.add_column("Parsed", justify="right")
    table.add_column("Dedupe", justify="right")
    table.add_column("SWE", justify="right")
    table.add_column("NYC", justify="right")
    table.add_column("Both", justify="right")
    table.add_column("Saved", justify="right")
    table.add_column("Filtered Out", justify="right")
    table.add_column("Fetch", justify="right")
    table.add_column("Total", justify="right")

    for result in summary.results:
        table.add_row(
            result.source_name,
            str(result.discovered),
            str(result.parsed),
            str(result.deduped),
            str(result.filter_metrics.swe_matches),
            str(result.filter_metrics.nyc_matches),
            str(result.filter_metrics.both_matches),
            str(result.saved),
            str(result.filtered_out),
            f"{result.fetch_seconds:.1f}s",
            f"{result.total_seconds:.1f}s",
        )
        record_source_run(
            repo,
            result.source_name,
            jobs_found=result.parsed,
            jobs_saved=result.saved,
            metrics=result.metrics_dict(),
        )

    print(table)
    print(f"[green]Saved {summary.total_saved} jobs[/green] to {settings.db_path}")


@app.command("list")
def list_jobs(
    query: str = typer.Option("", "--query", "-q"),
    limit: int = typer.Option(20, "--limit", "-n"),
) -> None:
    """List stored jobs from the database."""
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)

    jobs = search_jobs(
        conn,
        query=query,
        swe_only=settings.swe_only,
        nyc_only=settings.nyc_only,
        limit=limit,
    )

    table = Table(title="Stored Jobs")
    table.add_column("Score", justify="right")
    table.add_column("Company")
    table.add_column("Title")
    table.add_column("Location")
    table.add_column("URL")

    for job in jobs:
        table.add_row(
            f"{job.get('score', 0):.1f}",
            job.get("company", ""),
            job.get("title", ""),
            job.get("location") or "",
            job.get("job_url", ""),
        )

    print(table)


@app.command()
def stats() -> None:
    """Show a quick dashboard summary."""
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    summary = dashboard_summary(conn)

    print("[bold]Dashboard[/bold]")
    print(f"total_jobs: {summary['total_jobs']}")
    print(f"swe_jobs: {summary['swe_jobs']}")
    print(f"nyc_jobs: {summary['nyc_jobs']}")
    print("top_companies:")
    for row in summary["top_companies"]:
        print(f"  - {row['company']}: {row['count']}")


@app.command()
def export(
    output: Path = typer.Option(Path("data/exports/jobs.csv"), "--output", "-o"),
    format: str = typer.Option("csv", "--format", "-f", help="csv or json"),
) -> None:
    """Export stored jobs to a file."""
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)

    if format.lower() == "json":
        count = export_json(
            conn,
            output,
            swe_only=settings.swe_only,
            nyc_only=settings.nyc_only,
        )
    else:
        count = export_csv(
            conn,
            output,
            swe_only=settings.swe_only,
            nyc_only=settings.nyc_only,
        )

    print(f"[green]Exported {count} jobs[/green] to {output}")
