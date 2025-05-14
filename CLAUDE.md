# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands
- **Setup**: `make setup` (create virtual environment and install dependencies)
- **Environment**: `source scripts/activate.sh` (activate environment with helper aliases)
- **Run tests**: `make test` (all tests), `pytest tests/path/to/test.py::test_function -v` (single test)
- **Lint**: `make lint` (run all linters: ruff, black, isort, mypy)
- **Format**: `make format` (format code with black, isort, and ruff)
- **Run application**: `make run` (run the main module)
- **Data processing**: `make data-help` (see available data commands)

## Data File Targets
- **Download data**: `make download` or `make download-csv` (downloads all required CSV files)
- **Check data**: `make check-files` (verify data files are available)  
- **Base files**: `data/values_tree.csv`, `data/values_frequencies.csv` (auto-downloaded via targets)
- **Custom data files**: Create via Python module - `uv run python -m values_explorer.data.loader <args>`
- **Filtered data**: For files like `data/filtered_values.csv`, create a custom script that includes appropriate dependencies (example: `uv run make data/filtered_values.csv`)

## Code Style Guidelines
- **Python**: PEP 8, type annotations for all function parameters and returns
- **Formatting**: Black with 88-char line length, sorted imports (isort)
- **Imports**: Group as stdlib → third-party → local with blank line separation
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error handling**: Use specific exceptions with clear error messages
- **Documentation**: Google-style docstrings for all public functions/classes
- **Types**: Use typing module annotations (List, Dict, Optional, etc.)
- **Linting**: Uses ruff for linting with rules E, F, I, N, W, B, A enabled

## Git Commit Guidelines
- **Conventional Commits**: Use format `<type>(<scope>): <description>` 
- **Types**: feat, fix, docs, style, refactor, perf, test, chore
- **Example**: `feat(visualization): add scatter plot for value frequency`
- **Commit Trailers**: Use `--trailer` for attribution, not in message body