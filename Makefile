# Keystone developer task runner.
# Recipe lines use real tabs (required by make). `check` mirrors CI exactly.

.DEFAULT_GOAL := check
.PHONY: setup format lint typecheck arch test test-all audit check verify phase-check demo clean

setup:  ## Pin Python, sync all groups, install garak as an isolated tool
	uv python pin 3.12
	uv sync --all-groups
	uv tool install garak

format:  ## Auto-format the codebase
	uv run ruff format src tests scripts

lint:  ## Check formatting + lint rules (no writes)
	uv run ruff format --check src tests scripts
	uv run ruff check src tests scripts

typecheck:  ## Strict static type check
	uv run mypy

arch:  ## Enforce architecture import boundaries (import-linter)
	uv run lint-imports

test:  ## Fast test suite (excludes slow-marked tests)
	uv run pytest -m "not slow"

test-all:  ## Full test suite including slow tests
	uv run pytest

audit:  ## Audit dependencies for known vulnerabilities
	uv run pip-audit

check: lint typecheck arch test audit  ## Fast inner-loop gate: lint + typecheck + arch + fast tests + audit

# verify is the skeptical, independent acceptance gate (generator/evaluator
# separation). It runs the FULL test suite (incl. slow/milestone/e2e) and the
# standalone scope validator — see docs/QUALITY.md. It must fail loudly.
verify: lint typecheck arch  ## Acceptance gate: scope validation + full test suite
	uv run python scripts/validate_feature_list.py
	uv run python scripts/validate_obligations.py
	uv run python scripts/validate_controls.py
	uv run pytest
	uv run pip-audit
	@echo "verify: acceptance gate passed"

phase-check:  ## Run milestone tests that prove a phase is complete
	uv run pytest -m milestone

demo:  ## Run the Streamlit chassis shell
	uv run streamlit run src/keystone/ui/app.py

clean:  ## Remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
