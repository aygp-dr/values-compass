#+TITLE: CLAUDE Configuration
#+AUTHOR: aygp-dr
#+DATE: 2025-05-17
#+PROPERTY: header-args :mkdirp yes

* Project Configuration for Claude Code

** Build & Test Commands
- Setup: ~make setup~ (create virtual environment and install dependencies)
- Environment: ~source scripts/activate.sh~ (activate environment)
- Run tests: ~make test~ (all tests), ~pytest tests/path/to/test.py::test_function -v~ (single test)
- Lint: ~make lint~ (run all linters: ruff, black, isort, mypy)
- Format: ~make format~ (run black, isort, and ruff --fix)
- Run application: ~make run~ (run main module)
- Data processing: ~make data-help~ (see available data commands)

** Code Style Guidelines
- Python: PEP 8, with type annotations for all function parameters and returns
- Formatting: Black with 88-char line length, sorted imports (isort)
- Imports: Group as stdlib → third-party → local with blank line separation
- Naming: snake_case for variables/functions, PascalCase for classes
- Error handling: Use specific exceptions with clear error messages
- Documentation: Google-style docstrings for all public functions/classes
- Types: Use typing module annotations (List, Dict, Optional, etc.)
- Linting: Uses ruff for linting with rules E, F, I, N, W, B, A enabled

** Org Mode Usage
- Use Babel for code execution with ~:mkdirp yes~ for directory creation
- Org files can be executed using ~make org-execute~ or ~make org-execute-block BLOCK_ID=name~
- For visualizations, use Mermaid diagrams or LaTeX for complex graphics

** Git Commit Guidelines
- Conventional Commits: Use format ~<type>(<scope>): <description>~ 
- Types: feat, fix, docs, style, refactor, perf, test, chore
- Example: ~feat(visualization): add scatter plot for value frequency~
- Use --trailer for Co-Authored-By and don't use "Generated with" in the body

** Project Structure
- ~scripts/~ :: Python and shell scripts for data processing and visualization
- ~data/~ :: Raw data files (CSV, JSON) and processed datasets
- ~docs/~ :: Documentation including visualizations and analysis reports
- ~docs/visualizations/~ :: Generated visualizations and diagrams
- ~docs/hierarchy/~ :: Hierarchical structure of the values taxonomy
- ~values_explorer/~ :: Main Python package