# Main Makefile for Values Compass project
# Include the data processing targets
include Makefile.data

.PHONY: all setup clean test run lint lint-org lint-shell tangle-all download format deps org-pipeline org-tangle org-execute org-execute-block org-eval-file help validate presentation.pdf github_repo_qr.svg github_repo_qr.png setup-presentation

# Python command to use (using uv for better dependency isolation)
PYTHON = uv run python

# Variables for org-mode pipeline
ORG_FILES = $(wildcard *.org) $(wildcard docs/*.org) $(wildcard notebooks/*.org)
ORG_FILE = values-tree-analysis.org
EMACS = emacs
SCRIPTS_DIR = scripts
DATA_DIR = data
EXPORTS_DIR = exports
SHELL_SCRIPTS = $(wildcard $(SCRIPTS_DIR)/*.sh)

# Default target is help
.DEFAULT_GOAL := help

# Create virtual environment
.venv:
	python -m venv .venv

README.md:
	pandoc -i README.org -o README.md

README.txt:
	emacs --batch --eval "(require 'org)" --eval "(find-file \"README.org\")" --eval "(org-ascii-export-to-ascii)" --kill

# Install dependencies
deps: .venv README.md
	. .venv/bin/activate && pip install -U pip uv
	. .venv/bin/activate && uv pip install -e ".[dev]"
	@echo "UV installed successfully. You can now use 'uv run python' for isolated environments."

# Install data processing dependencies
deps-data: .venv
	. .venv/bin/activate && uv pip install -e ".[data]"
	@echo "Data processing dependencies installed."

# Install spaCy model for embedding analysis
deps-nlp: deps
	. .venv/bin/activate && uv pip install spacy
	. .venv/bin/activate && uv run python -m spacy download en_core_web_md
	@echo "spaCy and English medium model installed."

# Project setup (creates virtual environment and installs dependencies)
setup: .venv deps deps-nlp deps-data

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

# Extends the clean-all target from Makefile.data
clean-all-project: clean
	rm -rf .venv/
	rm -rf .direnv/
	rm -rf .cache/

# Run tests
test: .venv
	. .venv/bin/activate && $(PYTHON) -m pytest

# Run all linters
lint: lint-py lint-org lint-shell

# Run Python linters
lint-py: .venv
	. .venv/bin/activate && uv run ruff check .
	. .venv/bin/activate && uv run black --check .
	. .venv/bin/activate && uv run isort --check .
	. .venv/bin/activate && uv run mypy values_explorer/

# Run Org-mode lint
lint-org:
	@echo "Linting Org files..."
	@for file in $(ORG_FILES); do \
		echo "Linting $$file"; \
		$(EMACS) --batch --eval "(require 'org)" --eval "(require 'org-lint)" \
			--file=$$file --funcall org-lint --kill; \
	done

# Run ShellCheck on shell scripts
lint-shell:
	@command -v shellcheck >/dev/null 2>&1 || echo "Warning: shellcheck not installed. Skipping shell script linting."
	@command -v shellcheck >/dev/null 2>&1 && { \
		echo "Checking shell scripts with shellcheck..."; \
		for script in $(SHELL_SCRIPTS); do \
			echo "Checking $$script"; \
			shellcheck -x $$script || true; \
		done; \
	}

# Tangle all org files
tangle-all:
	@echo "Tangling all org files..."
	@for file in $(ORG_FILES); do \
		echo "Tangling $$file"; \
		$(EMACS) --batch --eval "(require 'org)" --file=$$file --funcall org-babel-tangle; \
	done

# Download all data files
download:
	@mkdir -p $(DATA_DIR)
	@echo "Downloading values tree CSV..."
	@curl -s -o $(DATA_DIR)/values_tree.csv https://huggingface.co/datasets/Anthropic/values-in-the-wild/raw/main/values_tree.csv
	@echo "Downloading values frequencies CSV..."
	@curl -s -o $(DATA_DIR)/values_frequencies.csv https://huggingface.co/datasets/Anthropic/values-in-the-wild/raw/main/values_frequencies.csv
	@echo "Download complete."

# Generate top values CSV from values_frequencies.csv
$(DATA_DIR)/top_values.csv: $(DATA_DIR)/values_frequencies.csv
	@echo "Generating top values CSV..."
	@uv run python $(SCRIPTS_DIR)/top_20.py
	@echo "✓ Generated $(DATA_DIR)/top_values.csv"

# Generate chart from top values CSV
$(DATA_DIR)/top_values_chart.png: $(DATA_DIR)/top_values.csv
	@echo "Generating top values chart..."
	@uv run python $(SCRIPTS_DIR)/plot_top_10.py
	@echo "✓ Generated $(DATA_DIR)/top_values_chart.png"

# Generate embedding clusters from top values CSV (complex version)
$(DATA_DIR)/values_clusters_visualization.html: $(DATA_DIR)/top_values.csv
	@echo "Generating embedding clusters..."
	@uv run python $(SCRIPTS_DIR)/embedding_clusters.py
	@echo "✓ Generated $(DATA_DIR)/values_clusters_visualization.html"

# Generate simple value similarity analysis (without spaCy dependency)
$(DATA_DIR)/value_similarities.txt: $(DATA_DIR)/top_values.csv
	@echo "Generating simple value similarities using pandas only..."
	@uv run python -c "import pandas as pd; df = pd.read_csv('$(DATA_DIR)/top_values.csv'); top100 = df.sort_values('pct_convos', ascending=False).head(100); with open('$(DATA_DIR)/value_similarities.txt', 'w') as f: f.write('Top 100 Values by Frequency\\n=====================\\n\\n'); [f.write(f\"{row['value']}: {row['pct_convos']:.3f}%\\n\") for i, row in top100.iterrows()]"
	@echo "✓ Generated value similarities analysis"


values-transit-map:
	cd docs/visualizations && pdflatex values_transit_map.tex

# Generate QR code for GitHub repository in SVG format
github_repo_qr.svg:
	qrencode -l H -s 8 -t SVG -o $@ "https://github.com/aygp-dr/values-compass"

# Generate QR code for GitHub repository in PNG format
github_repo_qr.png:
	qrencode -l H -s 8 -o $@ "https://github.com/aygp-dr/values-compass"

# Install dependencies for presentation generation and viewing
setup-presentation:
	@echo "Installing presentation dependencies..."
	@scripts/presentations/setup_presentation.sh

# Generate PDF from presentation.org using Emacs and org-mode export
presentation.pdf: presentation.org github_repo_qr.svg
	$(EMACS) --batch --eval "(require 'org)" --file=$< --eval "(org-latex-export-to-pdf)" --kill

# Format code
format: .venv
	. .venv/bin/activate && uv run ruff check --fix .
	. .venv/bin/activate && uv run black .
	. .venv/bin/activate && uv run isort .

# Run project
run: .venv
	. .venv/bin/activate && $(PYTHON) -m values_explorer.main

# Values Tree Analysis Pipeline
org-pipeline: org-tangle org-execute

# Tangle the org file to extract all code blocks
org-tangle:
	$(EMACS) --batch --eval "(require 'org)" --file=$(ORG_FILE) --funcall org-babel-tangle

# Execute the analysis pipeline scripts with virtual environment
org-execute: 
	@# Ensure data is available 
	curl -s -o $(DATA_DIR)/values_tree.csv https://huggingface.co/datasets/Anthropic/values-in-the-wild/raw/main/values_tree.csv 2>/dev/null || true
	@# Run the analysis steps in sequence
	bash $(SCRIPTS_DIR)/setup_db.sh
	. .venv/bin/activate && python $(SCRIPTS_DIR)/top_20.py
	. .venv/bin/activate && python $(SCRIPTS_DIR)/plot_top_10.py
	. .venv/bin/activate && python $(SCRIPTS_DIR)/db_analysis.py
	bash $(SCRIPTS_DIR)/export.sh

# Execute a specific code block by ID
org-execute-block:
	@[ -z "$(BLOCK_ID)" ] && echo "Error: Please specify BLOCK_ID" && exit 1 || \
		$(EMACS) --batch --eval "(require 'org)" --file=$(ORG_FILE) \
			--eval "(org-babel-goto-named-src-block \"$(BLOCK_ID)\")" \
			--eval "(org-babel-execute-src-block)" --kill

# Re-evaluate the entire org file
org-eval-file:
	$(EMACS) --batch --eval "(require 'org)" --file=$(ORG_FILE) \
		--eval "(org-babel-execute-buffer)" --kill

# Validate the entire project (run before commits)
validate: lint test

# All-in-one target that does everything
all: setup download tangle-all format lint test org-pipeline

# Help target
help:
	@echo "Values Compass - Exploring Anthropic's Values-in-the-Wild Dataset"
	@echo ""
	@echo "Main targets:"
	@echo "  all                 - Full project setup, download, tangle, lint, test, and analysis"
	@echo "  validate            - Run lint and tests (use before commits)"
	@echo ""
	@echo "Environment setup targets:"
	@echo "  setup               - Set up environment and install dependencies"
	@echo "  .venv               - Create Python virtual environment"
	@echo "  deps                - Install dependencies using uv"
	@echo "  deps-data           - Install data processing dependencies"
	@echo "  clean               - Clean up build artifacts"
	@echo "  clean-all           - Clean all data and build artifacts (from Makefile.data)"
	@echo "  clean-all-project   - Clean everything including virtual environments"
	@echo ""
	@echo "Development targets:"
	@echo "  shell               - Start a shell with the environment activated"
	@echo "  test                - Run tests"
	@echo "  lint                - Run all linters (Python, Org-mode, Shell)"
	@echo "  lint-py             - Run Python linters only"
	@echo "  lint-org            - Run Org-mode linter only"
	@echo "  lint-shell          - Run ShellCheck on shell scripts"
	@echo "  format              - Format code"
	@echo "  download            - Download all data files"
	@echo "  tangle-all          - Tangle all org files"
	@echo "  run                 - Run the main application"
	@echo ""
	@echo "Org-mode analysis:"
	@echo "  org-pipeline        - Run the complete analysis pipeline"
	@echo "  org-tangle          - Tangle code blocks from the org file"
	@echo "  org-execute         - Execute the tangled scripts"
	@echo "  org-execute-block   - Execute a specific code block by ID (BLOCK_ID=name)"
	@echo "  org-eval-file       - Evaluate all code blocks in the org file"
	@echo "  presentation.pdf   - Generate PDF from presentation.org"
	@echo "  github_repo_qr.svg - Generate QR code for GitHub repo (SVG format)"
	@echo "  github_repo_qr.png - Generate QR code for GitHub repo (PNG format)"
	@echo "  setup-presentation - Install presentation dependencies (LaTeX, pdfpc, etc.)"
	@echo ""
	@echo "See 'make data-help' for dataset-specific targets"
