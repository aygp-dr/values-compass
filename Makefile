.PHONY: setup clean test run lint venv deps

# Default target
all: setup

# Create virtual environment
venv:
	python -m venv .venv

# Install dependencies
deps:
	pip install -U pip uv
	uv pip install -e ".[dev]"

# Project setup (creates virtual environment and installs dependencies)
setup: venv deps

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
test:
	python -m pytest

# Run linters
lint:
	ruff check .
	black --check .
	isort --check .
	mypy values_explorer/

# Format code
format:
	ruff check --fix .
	black .
	isort .

# Run project
run:
	python -m values_explorer.main
