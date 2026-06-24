"""The convergence Streamlit app (M2-0n) actually loads and runs — the gate.

Per the KS-0501 lesson: run the REAL Streamlit script via `AppTest` (live AND replay
against the committed fixture), so an import/render error — or a replay that can't load
the saved run — FAILS the build. Ships with the screen.
"""

from __future__ import annotations

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from keystone.demo import recorded_run_path

_APP = str(
    Path(__file__).resolve().parents[1]
    / "src"
    / "keystone"
    / "ui"
    / "convergence_app.py"
)
_FIXTURE = recorded_run_path()


def _app() -> AppTest:
    return AppTest.from_file(_APP, default_timeout=120)


def test_app_loads_and_runs_without_exception() -> None:
    at = _app().run()
    assert not at.exception, at.exception
    assert at.sidebar.radio


def test_app_renders_from_the_saved_run_replay() -> None:
    at = _app().run()
    at.sidebar.radio[0].set_value("Replay saved run")
    at.run()
    at.sidebar.text_input[0].set_value(str(_FIXTURE))
    at.run()
    assert not at.exception, at.exception


def test_app_renders_live() -> None:
    at = _app().run()
    at.sidebar.radio[0].set_value("Live run")
    at.run()
    assert not at.exception, at.exception


def test_replay_of_an_incompatible_run_degrades_without_crashing(
    tmp_path: Path,
) -> None:
    # A schema-mismatched saved run must NOT crash the replay screen — it shows an error
    # and the honest empty state. Proves the gate catches a forced break (the real
    # fixture, used above, still renders — restore).
    data = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    data["schema_version"] = 1
    bad = tmp_path / "stale_v1_run.json"
    bad.write_text(json.dumps(data), encoding="utf-8")

    at = _app().run()
    at.sidebar.radio[0].set_value("Replay saved run")
    at.run()
    at.sidebar.text_input[0].set_value(str(bad))
    at.run()
    assert not at.exception, at.exception
    assert at.error or at.sidebar.error
