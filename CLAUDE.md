# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands
- **Setup**: `gmake setup` (create virtual environment and install dependencies)
- **Environment**: `source scripts/activate.sh` (activate environment with helper aliases)
- **Run tests**: `gmake test` (all tests), `pytest tests/path/to/test.py::test_function -v` (single test)
- **Lint**: `gmake lint` (run all linters: ruff, black, isort, mypy)
- **Format**: `gmake format` (format code with black, isort, and ruff)
- **Run application**: `gmake run` (run the main module)
- **Data processing**: `gmake data-help` (see available data commands)

## Code Style Guidelines
- **Python**: PEP 8, type annotations for all function parameters and returns
- **Formatting**: Black with 88-char line length, sorted imports (isort)
- **Imports**: Group as stdlib → third-party → local with blank line separation
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error handling**: Use specific exceptions with clear error messages
- **Documentation**: Google-style docstrings for all public functions/classes
- **Types**: Use typing module annotations (List, Dict, Optional, etc.)

## Git Commit Guidelines
- **Conventional Commits**: Use format `<type>(<scope>): <description>` 
- **Types**: feat, fix, docs, style, refactor, perf, test, chore
- **Example**: `feat(visualization): add scatter plot for value frequency`
- **Commit Trailers**: Use `--trailer` for attribution, not in message body
  ```bash
  git commit -m "feat(scope): description" \
    --trailer "Co-Authored-By: Claude <claude@anthropic.com>" \
    --trailer "Reviewed-By: Jason Walsh <j@wal.sh>"
  ```