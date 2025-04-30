.PHONY: setup clean test run lint deps

# Default target
all: setup

# Create virtual environment
.venv:
	python -m venv .venv

# Install dependencies
deps: .venv
	. .venv/bin/activate && pip install -U pip uv
	. .venv/bin/activate && uv pip install -e ".[dev]"

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
	. .venv/bin/activate && python -m pytest

# Run linters
lint: .venv
	. .venv/bin/activate && ruff check .
	. .venv/bin/activate && black --check .
	. .venv/bin/activate && isort --check .
	. .venv/bin/activate && mypy values_explorer/

# Format code
format: .venv
	. .venv/bin/activate && ruff check --fix .
	. .venv/bin/activate && black .
	. .venv/bin/activate && isort .

# Run project
run: .venv
	. .venv/bin/activate && python -m values_explorer.main
