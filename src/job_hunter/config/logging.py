from __future__ import annotations

import logging
import sys

from rich.logging import RichHandler


def configure_logging(level: str = "INFO") -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False, markup=True)],
    )

    # Quiet noisy libraries a bit
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("bs4").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)