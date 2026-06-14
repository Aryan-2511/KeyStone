# Keystone developer task runner.
# Recipe lines use real tabs (required by make). `check` mirrors CI exactly.

.DEFAULT_GOAL := check
.PHONY: setup format lint typecheck test test-all audit check phase-check demo clean

setup:  ## Pin Python, sync all groups, install garak as an isolated tool
	uv python pin 3.12
	uv sync --all-groups
	uv tool install garak

format:  ## Auto-format the codebase
	uv run ruff format src tests

lint:  ## Check formatting + lint rules (no writes)
	uv run ruff format --check src tests
	uv run ruff check src tests

typecheck:  ## Strict static type check
	uv run mypy

test:  ## Fast test suite (excludes slow-marked tests)
	uv run pytest -m "not slow"

test-all:  ## Full test suite including slow tests
	uv run pytest

audit:  ## Audit dependencies for known vulnerabilities
	uv run pip-audit

check: lint typecheck test audit  ## The gate: lint + typecheck + fast tests + audit

phase-check:  ## Run milestone tests that prove a phase is complete
	uv run pytest -m milestone

demo:  ## Run the Keystone demo (placeholder until a later phase)
	@echo "demo target is a Phase 0 placeholder — wired up in a later phase"

clean:  ## Remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
