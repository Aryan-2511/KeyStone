"""End-to-end test of the installed `keystone` console script.

Per the verification policy, this exercises the *real* entry point as a
subprocess (the script `uv sync` installs into the environment), not
`import main`. It proves the packaged front door genuinely runs the assurance
arc offline. Fast in-process coverage of the same wiring (and the narration)
lives in `tests/test_cli_demo.py`; the real-arc subprocess run is marked `slow`
so the fast inner loop stays fast while `make verify` still proves the installed
script.
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


def test_console_version_subcommand() -> None:
    result = subprocess.run(
        [str(_console_script()), "version"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert keystone.__version__ in result.stdout


@pytest.mark.slow
def test_console_demo_runs_the_real_arc_offline() -> None:
    """`keystone demo` (the installed script) runs the genuine arc offline and
    narrates the real result — exit 0, real fields, no network. This is the
    "fresh clone -> it works" proof at the packaging boundary."""
    result = subprocess.run(
        [str(_console_script()), "demo"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    out = result.stdout
    # Real fields from the produced RunResult (not stub / not hardcoded prose):
    assert "TXN-000016" in out  # the seam transaction id
    assert "STRUCTURING" in out  # the FATF typology
    assert "Red-Team Agent" in out and "Triage Agent" in out  # both agents narrated
    assert "route:" in out  # the triage route was read
    assert "memo-instruction-injection" in out  # the bound signature
    assert "hash chain verified: yes" in out  # the ledger sealed + verified
