"""End-to-end test of the installed `keystone` console script.

Per the verification policy, this exercises the *real* entry point as a
subprocess (the script `uv sync` installs into the environment), not
`import main`. Breadth is intentionally deferred — this is the seed e2e that
proves the packaging/console-script surface actually works.
"""

import subprocess
import sys
from pathlib import Path

import pytest

import keystone

pytestmark = pytest.mark.e2e


def _console_script() -> Path:
    """Locate the installed `keystone` executable next to the venv python."""
    bindir = Path(sys.executable).parent
    candidates = [bindir / "keystone.exe", bindir / "keystone"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise AssertionError(
        f"keystone console script not found in {bindir} — is the project synced?"
    )


def test_console_script_prints_version() -> None:
    result = subprocess.run(
        [str(_console_script())],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert keystone.__version__ in result.stdout
