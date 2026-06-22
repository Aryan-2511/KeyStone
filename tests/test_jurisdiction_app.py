"""The jurisdiction Streamlit app (KS-0502) actually loads and runs — the gate.

Mandatory from the KS-0501 lesson: a green gate that never runs the app is worthless
(it passed twice on a broken app). This runs the real Streamlit script via `AppTest`
(live AND replay) and asserts no exception, so an import/render error fails the build.
"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

_APP = str(
    Path(__file__).resolve().parents[1]
    / "src"
    / "keystone"
    / "ui"
    / "jurisdiction_app.py"
)


def _app() -> AppTest:
    return AppTest.from_file(_APP, default_timeout=120)


def test_app_loads_and_runs_live_without_exception() -> None:
    at = _app().run()
    assert not at.exception, at.exception
    assert at.sidebar.radio  # the script body executed


def test_app_renders_from_a_saved_run_replay() -> None:
    at = _app().run()
    assert not at.exception, at.exception
    at.sidebar.radio[0].set_value("Replay saved run")
    at.run()
    assert not at.exception, at.exception
