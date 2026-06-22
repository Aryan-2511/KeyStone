"""The Keystone shell app (KS-0503) actually loads and runs — the gate.

Per the KS-0501 lesson: run the REAL Streamlit script via `AppTest`. This loads the
shell, cycles ALL five views (the two hosted heroes + the three supporting views) in
BOTH live and replay, and asserts no exception — so a broken view, a broken hero
import, or a replay that can't load fails the build.
"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

_APP = str(
    Path(__file__).resolve().parents[1] / "src" / "keystone" / "ui" / "shell_app.py"
)
_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "seam_run_result.json"


def _app() -> AppTest:
    return AppTest.from_file(_APP, default_timeout=180)


def _radio(at: AppTest, label: str):  # type: ignore[no-untyped-def]
    # Select by label, not index — robust to widget creation order.
    return next(r for r in at.sidebar.radio if r.label == label)


def test_shell_loads_and_runs_live_across_all_views() -> None:
    at = _app().run()
    assert not at.exception, at.exception
    assert len(at.sidebar.radio) >= 2  # View + Data source
    for label in _radio(at, "View").options:
        _radio(at, "View").set_value(label)
        at.run()
        assert not at.exception, (label, at.exception)


def test_shell_renders_from_the_v2_saved_run_replay() -> None:
    at = _app().run()
    _radio(at, "Data source").set_value("Replay saved run")
    at.run()
    at.sidebar.text_input[0].set_value(str(_FIXTURE))
    at.run()
    assert not at.exception, at.exception
    # cycle every view (hosted heroes + supporting) in replay
    for label in _radio(at, "View").options:
        _radio(at, "View").set_value(label)
        at.run()
        assert not at.exception, (label, at.exception)
