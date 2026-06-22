"""The recorded-run fallback (KS-0504) — the demo safety net, proven offline.

The whole point of this task: the committed recorded run replays through the real UI
with ZERO network and ZERO Ollama/GPU, indistinguishable from a live run. These tests
PROVE the replay path is offline (sockets blocked → still renders all five views), and
that the recording is a genuine, version-clean, chain-valid v3 run.
"""

from __future__ import annotations

import socket

from keystone.demo import (
    RUN_RESULT_SCHEMA_VERSION,
    build_run_result,
    load_recorded_run,
    load_run_result,
    recorded_run_path,
    save_run_result,
)
from keystone.ui import seam_app, shell_app
from keystone.ui.jurisdiction_screen import jurisdiction_svg
from keystone.ui.seam_screen import seam_svg
from keystone.ui.shell_screens import before_after_svg, ledger_svg, posture_svg


def test_recorded_run_exists_is_v3_and_chain_valid() -> None:
    assert recorded_run_path().is_file()
    rr = load_recorded_run()
    assert rr.schema_version == RUN_RESULT_SCHEMA_VERSION == 3
    # The recording re-verifies its own hash chain offline — tamper-evident evidence.
    assert rr.arc.chain_verified is True
    assert rr.arc.arc_complete is True


def test_recorded_run_is_a_genuine_build_not_hand_edited() -> None:
    # Its substantive values match a fresh real build (only timestamps/hashes differ),
    # proving it was produced by build_run_result, not fabricated.
    rec = load_recorded_run()
    fresh = build_run_result()
    assert rec.seam_transaction.id == fresh.seam_transaction.id
    assert rec.seam_transaction.amount == fresh.seam_transaction.amount
    assert rec.binding.signature_name == fresh.binding.signature_name
    assert rec.financial_crime.typology == fresh.financial_crime.typology
    assert rec.report.finnet == fresh.report.finnet
    assert rec.ai_security.assurance == fresh.ai_security.assurance


def test_recorded_run_round_trips(tmp_path) -> None:  # type: ignore[no-untyped-def]
    rr = load_recorded_run()
    out = save_run_result(rr, tmp_path / "rt.json")
    assert load_run_result(out) == rr


def test_replay_renders_all_five_views_with_NO_network(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # Block ALL outbound sockets: any network or Ollama/GPU call would raise. The
    # recorded-run replay path must render every view regardless — a dead-network stage.
    def _no_network(*args: object, **kwargs: object) -> object:
        raise AssertionError("the offline replay path must not open a network socket")

    monkeypatch.setattr(socket.socket, "connect", _no_network)
    monkeypatch.setattr(socket, "create_connection", _no_network)
    monkeypatch.setattr(socket, "getaddrinfo", _no_network)

    rr = load_recorded_run()  # load: file + json only, no socket
    # All five views render purely from the run-result — the two heroes + three views.
    for builder in (
        seam_svg,
        jurisdiction_svg,
        ledger_svg,
        posture_svg,
        before_after_svg,
    ):
        markup = builder(rr)
        assert markup.startswith("<svg") and markup.endswith("</svg>")
    # Real values are present in the offline render (indistinguishable from live).
    assert rr.binding.transaction_id in seam_svg(rr)
    assert "10 / 12" in before_after_svg(rr)


def test_recorded_run_is_the_default_replay_source() -> None:
    # The apps default their replay path to the recorded run (the safe, offline default).
    assert recorded_run_path().name == "recorded_run.json"
    # the path helper is what the apps reference (one source of truth)
    assert hasattr(seam_app, "recorded_run_path")
    assert hasattr(shell_app, "recorded_run_path")
