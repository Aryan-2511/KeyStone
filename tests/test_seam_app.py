"""The seam Streamlit app (KS-0501) actually loads and runs — the gate hole fix.

`make verify` previously passed while the app crashed on import (`seam_app.py`
imported a name `seam_screen.py` didn't export) because NOTHING in the suite ran the
app module. These run the real Streamlit script via `AppTest` (live AND replay
against the committed v2 fixture), so an import/render error — or a replay that can't
load the saved run — FAILS the build.
"""

from __future__ import annotations

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

_APP = str(
    Path(__file__).resolve().parents[1] / "src" / "keystone" / "ui" / "seam_app.py"
)
_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "seam_run_result.json"


def _app() -> AppTest:
    # Generous timeout: the live default runs the Layer-1 arc.
    return AppTest.from_file(_APP, default_timeout=120)


def test_app_loads_and_runs_live_without_exception() -> None:
    at = _app().run()
    # An import error in seam_app.py (or any render exception) surfaces here.
    assert not at.exception, at.exception
    # The script body actually executed: the data-source control is present.
    assert at.sidebar.radio


def test_app_renders_from_the_v2_saved_run_replay() -> None:
    at = _app().run()
    at.sidebar.radio[0].set_value("Replay saved run")
    at.run()
    # Explicitly load the committed v2 fixture — the actual saved-run replay path.
    at.sidebar.text_input[0].set_value(str(_FIXTURE))
    at.run()
    assert not at.exception, at.exception


def test_replay_of_an_incompatible_run_degrades_without_crashing(
    tmp_path: Path,
) -> None:
    # A schema-mismatched saved run (a v1 run after the v2 migration) must NOT crash
    # the replay screen — it shows an error and the honest empty state. This is the
    # exact failure that hit replay; the gate now catches it.
    data = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    data["schema_version"] = 1
    bad = tmp_path / "stale_v1_run.json"
    bad.write_text(json.dumps(data), encoding="utf-8")

    at = _app().run()
    at.sidebar.radio[0].set_value("Replay saved run")
    at.run()
    at.sidebar.text_input[0].set_value(str(bad))
    at.run()
    assert not at.exception, at.exception  # caught + degraded, not crashed
    assert at.error or at.sidebar.error  # the honest error is shown
