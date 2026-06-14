"""Structural tests that assert the harness's own gates stay wired up.

These make the Phase-0 done-criteria mechanical: if someone removes the
coverage floor or the CI secret-scan job, a test fails rather than the rule
silently rotting.
"""

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_coverage_floor_configured() -> None:
    """A blocking coverage floor must be configured (KS-0003)."""
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    addopts = data["tool"]["pytest"]["ini_options"]["addopts"]
    assert "--cov-fail-under=" in addopts


def test_ci_runs_pre_commit() -> None:
    """CI must run pre-commit as its own gate, not only locally (KS-0004)."""
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "pre-commit:" in ci
    assert "pre-commit run --all-files" in ci


def test_secrets_baseline_present() -> None:
    """detect-secrets must have a committed baseline (KS-0004)."""
    assert (REPO_ROOT / ".secrets.baseline").is_file()
