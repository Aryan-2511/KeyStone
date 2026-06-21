"""The seam Streamlit app (KS-0501) actually loads and runs — the gate hole fix.

`make verify` previously passed while the app crashed on import (`seam_app.py`
imported a name `seam_screen.py` didn't export) because NOTHING in the suite ran the
app module. These tests run the real Streamlit script via `AppTest`, so an import
error or a render exception in the demo app now FAILS the build — both live (the arc
runs) and replay (a saved run is loaded). This guards the deliverable (a running
screen), not just the SVG-string helper.
"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

_APP = str(
    Path(__file__).resolve().parents[1] / "src" / "keystone" / "ui" / "seam_app.py"
)


def _app() -> AppTest:
    # Generous timeout: the live default runs the Layer-1 arc.
    return AppTest.from_file(_APP, default_timeout=120)


def test_app_loads_and_runs_live_without_exception() -> None:
    at = _app().run()
    # An import error in seam_app.py (or any render exception) surfaces here.
    assert not at.exception, at.exception
    # The script body actually executed: the data-source control is present.
    assert at.sidebar.radio


def test_app_renders_from_a_saved_run_replay() -> None:
    at = _app().run()
    assert not at.exception, at.exception
    at.sidebar.radio[0].set_value("Replay saved run")
    at.run()
    assert not at.exception, at.exception
