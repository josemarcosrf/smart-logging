"""
SmartFormatter: auto-switches between colored terminal logs and structured JSON logs.

- TTY detected (terminal)  -> colored, human-friendly output via colorlog
- Non-TTY (Docker, CI, etc) -> structured JSON output via python-json-logger

Override with env var FORCE_COLORED_LOGS=true|false.
"""

import logging
import os
import sys
from typing import Any

import colorlog
from pythonjsonlogger import jsonlogger


class SmartFormatter(logging.Formatter):
    """Formatter that picks colored or JSON output based on TTY detection."""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
        **kwargs: Any,
    ) -> None:
        super().__init__(fmt, datefmt, style)
        self.fmt = fmt or (
            "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
        )
        self.datefmt = datefmt

        # Lazy-init formatters
        self._colored_formatter: colorlog.ColoredFormatter | None = None
        self._json_formatter: jsonlogger.JsonFormatter | None = None

    @staticmethod
    def _is_tty(stream: Any) -> bool:
        return hasattr(stream, "isatty") and stream.isatty()

    def _should_use_colored(self, record: logging.LogRecord) -> bool:
        # Env var override
        force = os.getenv("FORCE_COLORED_LOGS", "").lower()
        if force == "true":
            return True
        if force == "false":
            return False

        # Check the logger's handlers for a TTY stream
        for logger in (logging.getLogger(record.name), logging.getLogger()):
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and hasattr(handler, "stream"):
                    if self._is_tty(handler.stream):
                        return True

        # Fallback: check stderr/stdout directly
        return self._is_tty(sys.stderr) or self._is_tty(sys.stdout)

    def _get_colored_formatter(self) -> colorlog.ColoredFormatter:
        if self._colored_formatter is None:
            self._colored_formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(asctime)s [%(name)s] "
                "[%(filename)s:%(lineno)d] - %(message)s",
                datefmt=self.datefmt,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
                reset=True,
                style="%",
            )
        return self._colored_formatter

    def _get_json_formatter(self) -> jsonlogger.JsonFormatter:
        if self._json_formatter is None:
            self._json_formatter = jsonlogger.JsonFormatter(
                self.fmt,
                datefmt=self.datefmt,
            )
        return self._json_formatter

    def format(self, record: logging.LogRecord) -> str:
        if self._should_use_colored(record):
            return self._get_colored_formatter().format(record)
        return self._get_json_formatter().format(record)
