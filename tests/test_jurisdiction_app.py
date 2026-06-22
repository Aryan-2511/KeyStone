"""The jurisdiction Streamlit app (KS-0502) actually loads and runs — the gate.

Mandatory from the KS-0501 lesson: a green gate that never runs the app is worthless.
This runs the real Streamlit script via `AppTest` (live AND replay against the
committed v2 fixture) and asserts no exception, and that a schema-mismatched saved
run degrades gracefully rather than crashing replay.
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
    / "jurisdiction_app.py"
)
_FIXTURE = recorded_run_path()


def _app() -> AppTest:
    return AppTest.from_file(_APP, default_timeout=120)


def test_app_loads_and_runs_live_without_exception() -> None:
    at = _app().run()
    assert not at.exception, at.exception
    assert at.sidebar.radio  # the script body executed


def test_app_renders_from_the_v2_saved_run_replay() -> None:
    at = _app().run()
    at.sidebar.radio[0].set_value("Replay saved run")
    at.run()
    at.sidebar.text_input[0].set_value(str(_FIXTURE))
    at.run()
    assert not at.exception, at.exception


def test_replay_of_an_incompatible_run_degrades_without_crashing(
    tmp_path: Path,
) -> None:
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
