"""
Demo of SmartFormatter.

Run in terminal (TTY) -> colored output:
    python demo.py

Pipe to file (non-TTY) -> JSON output:
    python demo.py 2> /tmp/logs.json && cat /tmp/logs.json

Force colored even when piped:
    FORCE_COLORED_LOGS=true python demo.py 2>&1 | cat

Force JSON even in terminal:
    FORCE_COLORED_LOGS=false python demo.py
"""

import logging
import logging.config

logging.config.fileConfig("logging_conf.ini")
logger = logging.getLogger("myapp")

logger.debug("This is a debug message")
logger.info("Service started on port 8000")
logger.warning("Memory usage above 80%s", "%")
logger.error("Failed to connect to database")
logger.critical("Unrecoverable error — shutting down")
