# smart-logging

Smart logging utilities that automatically switch between human-friendly colored terminal logs and structured JSON logs suitable for machines (Docker, CI, log aggregators).

This project provides a single, focused component: `SmartFormatter` — a `logging.Formatter` that chooses a colored output (via `colorlog`) when writing to a TTY and a structured JSON output (via `python-json-logger`) when writing to a non-TTY. You can override the auto-detection using an environment variable.

I wrote this to make it easy for you to get readable logs when developing locally, and structured logs when running in containers or CI without changing your application code.

---

## Features

- Terminal-friendly colored logs when writing to stdout/stderr on a TTY.
- Structured JSON logs when output is redirected (files, Docker, systemd, etc).
- Environment variable override: `FORCE_COLORED_LOGS=true|false`.
- Plug-and-play: works with `logging.config.fileConfig` or programmatic `logging` setup.
- Small and dependency-light: only `colorlog` and `python-json-logger`.

---

## Contents

- `smart_formatter.py` — main implementation (provides `SmartFormatter`).
- `logging_conf.ini` — an example `fileConfig`-based configuration.
- `demo.py` — demo script showing both modes.
- `requirements.txt` — runtime dependencies.
- `.gitignore` — common ignores for development.

---

## Installation

1. Create and activate a Python virtual environment (recommended):

   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate      # Windows (PowerShell/CMD)

2. Install requirements:

   pip install -r requirements.txt

---

## Quick start

- To see colored output in your terminal:

   python demo.py

- To get JSON output (simulate non-TTY, e.g. capturing logs to a file):

   python demo.py 2> logs.json && cat logs.json

- Force colored logs even when piped:

   FORCE_COLORED_LOGS=true python demo.py 2>&1 | cat

- Force JSON logs even in a terminal:

   FORCE_COLORED_LOGS=false python demo.py

---

## Example configuration

Use the provided `logging_conf.ini` (a minimal example for `logging.config.fileConfig`):

    [loggers]
    keys=root

    [handlers]
    keys=console

    [formatters]
    keys=smart

    [logger_root]
    level=DEBUG
    handlers=console

    [handler_console]
    class=logging.StreamHandler
    formatter=smart
    stream=ext://sys.stderr

    [formatter_smart]
    class=smart_formatter.SmartFormatter
    format=%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s

Notes:
- The formatter class path is `smart_formatter.SmartFormatter` (importable from the current working directory).
- `stream=ext://sys.stderr` ensures messages go to stderr (common for logs). The formatter checks handler streams to detect TTY.
- You can adapt the `format=` string to include additional fields (request id, host, etc) as required.

---

## Programmatic usage

If you prefer `dictConfig` or manual setup, you can attach the formatter programmatically:

1. Import and instantiate:

   from smart_formatter import SmartFormatter
   import logging

   handler = logging.StreamHandler()
   handler.setFormatter(SmartFormatter())
   root = logging.getLogger()
   root.setLevel(logging.DEBUG)
   root.addHandler(handler)

2. From there, use logging as usual.

---

## API: SmartFormatter

- Class: `SmartFormatter(logging.Formatter)`
  - Behavior: decides at `format(record)` time whether to use a colored formatter or JSON formatter.
  - Detection:
    - Read `FORCE_COLORED_LOGS` environment variable. If `true` -> colored, if `false` -> JSON.
    - Otherwise, inspects handler streams attached to the relevant loggers for `isatty()`.
    - Falls back to checking `sys.stderr` and `sys.stdout`.

This design ensures the correct output format even if different handlers are attached at runtime.

---

## Environment variables

- `FORCE_COLORED_LOGS`
  - `true`  — always produce colored logs
  - `false` — always produce JSON logs
  - unset   — auto-detect based on TTY

---

## Troubleshooting & tips

- If your logs are still JSON in the terminal:
  - Check whether your terminal emulator or the way you run the app makes the Python stdout/stderr report as non-TTY (for example, IDE run panels sometimes behave like non-TTY).
  - You can force colored logs with `FORCE_COLORED_LOGS=true`.
- If you get import errors for `smart_formatter` when using `logging_conf.ini`, ensure the working directory includes `smart_formatter.py` or that it is on `PYTHONPATH`.
- When running inside Docker, logs typically go to stdout/stderr and are non-TTY — JSON is often the desired format for downstream aggregators.

---

## Development & testing

- Tests: There are no formal tests included in the repo presently. To test manually:
  - Run `python demo.py` locally and verify colored output.
  - Run `python demo.py 2> logs.json` and verify JSON lines in `logs.json`.
- Linting: Feel free to add `ruff`, `mypy`, or `flake8` to the project to enforce style and typing.
- Packaging: This is a small utility; if you plan to publish, add `setup.py` / `pyproject.toml` and appropriate metadata.

---

## Dependencies

- `colorlog` — colored log formatter for terminal output.
- `python-json-logger` — produces JSON-formatted logs compatible with standard logging.

See `requirements.txt` for pinned versions.

---

## Contributing

If you'd like me to extend this:
- Add structured fields (trace id, request id) automatically.
- Add a context manager or wrapper to inject request/context info.
- Provide unit tests and CI setup.
Tell me which direction you prefer and I will help implement it.

---

## License

This repository does not currently include an explicit license file. If you want to publish or share this code, add a `LICENSE` file (for example MIT or Apache-2.0) and I can help draft one.

---

If you want, I can:
- Add example `pyproject.toml` and packaging metadata.
- Add unit tests that exercise the TTY and non-TTY paths (using monkeypatching).
- Provide a small Dockerfile showing JSON logging behavior.

Which of those would you like me to do next?
