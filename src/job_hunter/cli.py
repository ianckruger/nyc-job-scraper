from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from job_hunter.config.logging import configure_logging, get_logger
from job_hunter.config.settings import get_settings
from job_hunter.storage.db import connect, init_db

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
    discover -> fetch -> parse -> normalize -> dedupe -> store
    """
    settings = get_settings()
    selected_sources = source or settings.source_list

    logger.info("Starting pipeline", extra={"sources": selected_sources})

    conn = connect(settings.db_path)
    init_db(conn)

    # Placeholder: wire in a source registry next.
    print(f"[yellow]Would run sources:[/yellow] {selected_sources}")
    print("[yellow]Pipeline runner comes next: source registry -> adapters -> repository[/yellow]")


@app.command()
def export(
    output: Path = typer.Option(Path("data/exports/jobs.csv"), "--output", "-o"),
) -> None:
    """Export stored jobs to a file."""
    print(f"[yellow]Export destination:[/yellow] {output}")
    print("[yellow]This will read from the DB and write CSV/JSON later in the pipeline.[/yellow]")