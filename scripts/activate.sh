#!/bin/sh
# This file must be used with "source scripts/activate.sh" from bash/zsh
# You cannot run it directly

if [ "${BASH_SOURCE:-}" = "${0}" ]; then
    echo "Error: This script must be sourced. Run 'source scripts/activate.sh' instead" >&2
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate the virtual environment
. "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")/../.venv/bin/activate"

# Install dependencies if needed
if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    pip install -U pip uv
fi

# Check if project is installed
if ! python -c "import values_explorer" &>/dev/null; then
    echo "Installing project in development mode..."
    uv pip install -e ".[dev]"
fi

# Setup helpful aliases
alias py="uv run python"
alias pytest="uv run pytest"
alias ruff="uv run ruff"
alias black="uv run black"
alias isort="uv run isort"
alias mypy="uv run mypy"

echo "Values Compass environment activated with Python $(python --version)"
echo "Helper aliases created: py, pytest, ruff, black, isort, mypy"
echo "Use 'py' command to run Python with proper isolation"
echo "Run 'deactivate' to exit the virtual environment"