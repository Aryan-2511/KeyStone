"""The recorded-run fallback (KS-0504) — the demo safety net, proven offline.

The whole point of this task: the committed recorded run replays through the real UI
with ZERO network and ZERO Ollama/GPU, indistinguishable from a live run. These tests
PROVE the replay path is offline (sockets blocked → still renders all five views), and
that the recording is a genuine, version-clean, chain-valid run at the current schema.
"""

from __future__ import annotations

import socket

from keystone.demo import (
    RUN_RESULT_SCHEMA_VERSION,
    RunResult,
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


def test_recorded_run_exists_is_current_version_and_chain_valid() -> None:
    assert recorded_run_path().is_file()
    rr = load_recorded_run()
    assert rr.schema_version == RUN_RESULT_SCHEMA_VERSION == 7
    # The recording re-verifies its own hash chain offline — tamper-evident evidence.
    assert rr.arc.chain_verified is True
    assert rr.arc.arc_complete is True


# The COMPLETE set of fields that legitimately vary run-to-run — the paper's
# "reproducibility caveat" disclosure list, and the ONLY fields the exhaustive
# equality test below is allowed to mask. Confirmed empirically: diffing two fresh
# build_run_result() outputs (and the recorded run against a fresh build) yields
# EXACTLY these leaf paths and no others.
#
#   * ``generated_at`` — wall-clock stamp of the build (runner.py:227,
#     ``datetime.now(UTC)``).
#   * each ledger entry's ``ts`` — wall-clock stamp of the append
#     (core/ledger/ledger.py:75, ``datetime.now(UTC)``).
#   * each ledger entry's ``entry_hash`` — a SHA-256 over content that INCLUDES ``ts``
#     (core/ledger/models.py:32-52), so it necessarily varies whenever ``ts`` does.
#   * each ledger entry's ``prev_hash`` — the previous entry's ``entry_hash`` chained
#     forward, hence equally ts-derived (entry[0]'s ``prev_hash`` is the constant
#     GENESIS_HASH and does not vary; masking it uniformly is a safe no-op).
#
# Every OTHER field is substantive and MUST match between the recorded artifact and a
# fresh build — if one differs, the artifact is not fully reproducible and the test
# fails loudly (a real finding, not something to mask away).
_MASK = "<normalized>"


def _normalize(rr: RunResult) -> RunResult:
    """Return a copy of `rr` with EXACTLY the legitimately-varying fields masked.

    Masks only `generated_at` and, per ledger entry, `ts` + the ts-derived chain
    hashes (`entry_hash`, `prev_hash`) to a canonical constant. Nothing else is
    touched, so two genuine builds of the same arc compare fully equal while any
    substantive divergence still fails the comparison.
    """
    data = rr.model_dump()
    data["generated_at"] = _MASK
    for entry in data["arc"]["entries"]:
        entry["ts"] = _MASK
        entry["entry_hash"] = _MASK
        entry["prev_hash"] = _MASK
    return RunResult.model_validate(data)


def test_recorded_run_equals_fresh_build_exhaustively() -> None:
    # The reproducibility claim, formalized: with ONLY the disclosed run-varying fields
    # masked (generated_at + each ledger ts + the ts-derived entry_hash/prev_hash), the
    # committed recorded run equals a fresh build_run_result() as a WHOLE object — every
    # substantive number regenerates deterministically from the code. This is exhaustive
    # (full-object equality), not a field subset: any other difference would fail here.
    rec = load_recorded_run()
    fresh = build_run_result()
    assert _normalize(rec) == _normalize(fresh)


def test_recorded_run_is_a_genuine_build_not_hand_edited() -> None:
    # A fast, human-readable smoke check on a handful of headline fields. Now fully
    # SUBSUMED by test_recorded_run_equals_fresh_build_exhaustively (which asserts these
    # and every other substantive field); kept as a quick, readable sanity spot-check.
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
