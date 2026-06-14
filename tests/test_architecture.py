"""The architecture import contract must hold.

Runs import-linter's contracts (defined in [tool.importlinter]) so a forbidden
import — e.g. the deterministic core reaching into the LLM/agent edge — fails
the test gate, not just the CLI. We invoke the real `lint-imports` console
script as a subprocess: it is the canonical interface (identical to what CI and
pre-commit run) and avoids relying on import-linter's internal init order.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _lint_imports() -> Path:
    """Locate the installed `lint-imports` executable next to the venv python."""
    bindir = Path(sys.executable).parent
    for candidate in (bindir / "lint-imports.exe", bindir / "lint-imports"):
        if candidate.is_file():
            return candidate
    raise AssertionError(
        f"lint-imports not found in {bindir} — is the dev group synced?"
    )


def test_import_contract_passes() -> None:
    result = subprocess.run(
        [str(_lint_imports())],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, (
        "import-linter contract violated — see [tool.importlinter] in "
        "pyproject.toml and docs/design/architecture-boundaries.md\n"
        f"{result.stdout}\n{result.stderr}"
    )
