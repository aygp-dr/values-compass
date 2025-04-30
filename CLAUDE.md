# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands
- **Setup**: `pip install -e .` (install in development mode)
- **Run tests**: `pytest` (all tests), `pytest tests/path/to/test.py::test_function -v` (single test)
- **Jupyter**: `jupyter notebook notebooks/` (start notebook server)
- **Lint**: `flake8 values_explorer/` (lint Python code)
- **Type checking**: `mypy values_explorer/` (check types)
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
- **Co-authors**: Do not include co-author info in commit message body
- **Attribution**: 
  - Co-Authored-By: Claude <claude@anthropic.com>
  - Reviewed-By: Jason Walsh <j@wal.sh>