.PHONY: setup clean test run lint deps

# Python command to use (using uv for better dependency isolation)
PYTHON = uv run python

# Default target
all: setup

# Create virtual environment
.venv:
	python -m venv .venv

# Install dependencies
deps: .venv
	. .venv/bin/activate && pip install -U pip uv
	. .venv/bin/activate && uv pip install -e ".[dev]"
	@echo "UV installed successfully. You can now use 'uv run python' for isolated environments."

# Project setup (creates virtual environment and installs dependencies)
setup: .venv deps

# Create shell with environment loaded
shell:
	@echo "Activating virtual environment..."
	@bash -c "source scripts/activate.sh && exec bash"

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +

# Deep clean (includes virtual environment)
clean-all: clean
	rm -rf .venv/
	rm -rf .direnv/
	rm -rf .cache/

# Run tests
test: .venv
	. .venv/bin/activate && $(PYTHON) -m pytest

# Run linters
lint: .venv
	. .venv/bin/activate && uv run ruff check .
	. .venv/bin/activate && uv run black --check .
	. .venv/bin/activate && uv run isort --check .
	. .venv/bin/activate && uv run mypy values_explorer/

# Format code
format: .venv
	. .venv/bin/activate && uv run ruff check --fix .
	. .venv/bin/activate && uv run black .
	. .venv/bin/activate && uv run isort .

# Run project
run: .venv
	. .venv/bin/activate && $(PYTHON) -m values_explorer.main
