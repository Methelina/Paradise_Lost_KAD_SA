"""Logging configuration for AmuleD_v2.

Configures structured-ish console logging via the stdlib :mod:`logging`
module.  When :mod:`rich` is installed a :class:`rich.logging.RichHandler`
is used for coloured, structured output; otherwise a simple
:class:`logging.StreamHandler` with a plain formatter is used.  Rich is an
optional import — its absence never causes a crash.

src/amuled_v2/logging_setup.py
Version:     0.1.0
Author:      Soror L.'.L.'.
Updated:     2026-09-22

Patch Notes v0.1.0 (Soror L.'.L'.):
  [+] stdlib logging with optional rich handler.
  [+] No crash when rich is absent.
  [+] configure_logging(level) sets root logger level and handlers.
"""

from __future__ import annotations

import logging
import sys

# ------------------------------------------------------------------
# Optional rich import
# ------------------------------------------------------------------

try:
    from rich.logging import RichHandler  # type: ignore[import-untyped]
    _HAS_RICH = True
except ImportError:  # pragma: no cover - exercised when rich absent
    _HAS_RICH = False


class _PlainFormatter(logging.Formatter):
    """Minimal formatter used when rich is unavailable."""

    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        return f"[{ts}] {record.levelname:<7} {record.name}: {record.getMessage()}"


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure root logging and return the ``amuled_v2`` logger.

    Idempotent: calling multiple times replaces existing handlers to avoid
    duplicate output.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Remove existing handlers to stay idempotent.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    if _HAS_RICH:
        handler: logging.Handler = RichHandler(
            show_time=True,
            show_level=True,
            show_path=False,
            rich_tracebacks=True,
        )
        handler.setLevel(numeric_level)
        root.addHandler(handler)
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(numeric_level)
        handler.setFormatter(_PlainFormatter())
        root.addHandler(handler)

    logger = logging.getLogger("amuled_v2")
    logger.setLevel(numeric_level)
    return logger
