"""Fast, in-process coverage of the console front door and its narration.

These run the arc in-process (offline, deterministic — no network) so the fast
gate catches any regression of `keystone demo` back to a stub, and cover the
narration renderer directly. The installed-script subprocess proof lives in
`tests/e2e/test_cli.py` (marked slow).
"""

from __future__ import annotations

import pytest

from keystone import __version__
from keystone.__main__ import main
from keystone.demo import load_recorded_run
from keystone.demo.narrate import narrate_run


def test_narrate_reads_real_fields() -> None:
    """`narrate_run` renders the actual RunResult fields — never fabricated text."""
    result = load_recorded_run()  # a committed, genuinely-produced offline run
    text = narrate_run(result)

    # Each assertion pins a real field read off the RunResult:
    assert result.seam_transaction.id in text
    assert result.financial_crime.typology in text  # e.g. STRUCTURING
    assert result.binding.signature_name in text  # e.g. memo-instruction-injection
    assert result.triage.route.upper() in text  # the triage route
    exploited_family = result.red_team.exploited_family
    assert exploited_family is not None  # this run landed an exploit
    assert exploited_family in text  # the landed-exploit family
    assert result.report.report_format in text  # e.g. FINNET
    # Both agents narrated, and honestly framed as policies (not LLMs):
    assert "Red-Team Agent" in text and "Triage Agent" in text
    assert "not an LLM" in text
    # The ledger sealing is surfaced:
    assert "hash chain verified" in text


def test_main_version_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_main_demo_default_runs_arc_offline(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Bare `keystone` (no subcommand) defaults to `demo`, runs the real arc
    offline, narrates real fields, and exits 0."""
    assert main([]) == 0  # [] -> default "demo"
    out = capsys.readouterr().out
    assert "end-to-end assurance arc" in out
    assert "TXN-000016" in out  # a real field, proving the arc actually ran
    assert "hash chain verified: yes" in out
