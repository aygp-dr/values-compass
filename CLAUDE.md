# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands
- **Setup**: `gmake setup` (create virtual environment and install dependencies)
- **Environment**: `source scripts/activate.sh` (activate environment with helper aliases)
- **Run tests**: `gmake test` (all tests), `pytest tests/path/to/test.py::test_function -v` (single test)
- **Jupyter**: `jupyter notebook notebooks/` (start notebook server)
- **Lint**: `gmake lint` (run all linters)
- **Format**: `gmake format` (format code with black, isort, and ruff)
- **Data processing**: `gmake data-help` (see available data commands)
- **Dataset access**: Use `datasets` library: `load_dataset("Anthropic/values-in-the-wild", "values_frequencies")`

## Code Style Guidelines
- **Python**: PEP 8, docstrings (Google style), type annotations
- **Imports**: stdlib → third-party → local modules (blank line separation)
- **Formatting**: 4-space indentation, 88-char line length (Black style)
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Types**: Type hints for function parameters and return values
- **Error handling**: Specific exceptions with meaningful messages
- **Documentation**: Org-mode format in notebooks and README
- **Comments**: Explain "why" not "what" in comments

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