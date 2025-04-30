# Main Makefile for Values Compass project
# See Makefile.data for dataset-specific targets

# Include the data processing targets
include Makefile.data

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

# Install data processing dependencies
deps-data: .venv
	. .venv/bin/activate && uv pip install -e ".[data]"
	@echo "Data processing dependencies installed."

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

# Project help target
help:
	@echo "Values Compass - Exploring Anthropic's Values-in-the-Wild Dataset"
	@echo ""
	@echo "Environment setup targets:"
	@echo "  setup               - Set up environment and install dependencies"
	@echo "  .venv               - Create Python virtual environment"
	@echo "  deps                - Install dependencies using uv"
	@echo "  clean               - Clean up build artifacts"
	@echo "  clean-all           - Clean all artifacts including environment"
	@echo ""
	@echo "Development targets:"
	@echo "  shell               - Start a shell with the environment activated"
	@echo "  test                - Run tests"
	@echo "  lint                - Run linters"
	@echo "  format              - Format code"
	@echo "  run                 - Run the main application"
	@echo ""
	@echo "See 'make data-help' for dataset-specific targets"
