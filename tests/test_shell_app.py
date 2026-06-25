"""The Keystone shell app (KS-0503) actually loads and runs — the gate.

Per the KS-0501 lesson: run the REAL Streamlit script via `AppTest`. This loads the
shell, cycles ALL five views (the two hosted heroes + the three supporting views) in
BOTH live and replay, and asserts no exception — so a broken view, a broken hero
import, or a replay that can't load fails the build.
"""

from __future__ import annotations

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from keystone.demo import recorded_run_path

_APP = str(
    Path(__file__).resolve().parents[1] / "src" / "keystone" / "ui" / "shell_app.py"
)
_FIXTURE = recorded_run_path()


def _app() -> AppTest:
    return AppTest.from_file(_APP, default_timeout=180)


def _radio(at: AppTest, label: str):  # type: ignore[no-untyped-def]
    # Select by label, not index — robust to widget creation order.
    return next(r for r in at.sidebar.radio if r.label == label)


def test_shell_loads_and_runs_live_across_all_views() -> None:
    at = _app().run()
    assert not at.exception, at.exception
    assert len(at.sidebar.radio) >= 2  # View + Data source
    # Default is now the recorded run (safe default); select Live to test live mode.
    _radio(at, "Data source").set_value("Live run")
    at.run()
    for label in _radio(at, "View").options:
        _radio(at, "View").set_value(label)
        at.run()
        assert not at.exception, (label, at.exception)


def test_recorded_run_is_the_safe_default_data_source() -> None:
    # Demo insurance: on load (nothing flipped), the shell replays the recorded run.
    at = _app().run()
    assert not at.exception, at.exception
    assert _radio(at, "Data source").value == "Replay saved run"


def test_shell_renders_from_the_v2_saved_run_replay() -> None:
    at = _app().run()
    _radio(at, "Data source").set_value("Replay saved run")
    at.run()
    at.sidebar.text_input[0].set_value(str(_FIXTURE))
    at.run()
    assert not at.exception, at.exception
    # cycle every view (the run entry + hosted heroes + supporting) in replay
    for label in _radio(at, "View").options:
        _radio(at, "View").set_value(label)
        at.run()
        assert not at.exception, (label, at.exception)


def test_run_view_is_the_entry_and_reveals_the_five_steps() -> None:
    # The shell opens on the live-execution view; pressing Run the arc reveals the five
    # real steps and arrives at the destinations.
    at = _app().run()
    assert _radio(at, "View").value == "▶ Run the arc"  # the entry point
    next(b for b in at.button if "Run the arc" in b.label).click()
    at.run()
    assert not at.exception, at.exception
    md = " ".join(m.value for m in at.markdown)
    for step in ("INGEST", "DETECT", "SEAM-BIND", "REPORT", "SIGN"):
        assert step in md, step
    assert "STRUCTURING" in md  # the real artifact, not fabricated
    assert any("Open Seam" in b.label for b in at.button)  # the destinations


def test_run_view_degrades_on_an_incompatible_run(tmp_path: Path) -> None:
    # Forced break: a schema-mismatched saved run must NOT crash the run view — pressing
    # Run the arc degrades to the honest error (then the real fixture, above, reveals).
    data = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    data["schema_version"] = 1
    bad = tmp_path / "stale_v1_run.json"
    bad.write_text(json.dumps(data), encoding="utf-8")

    at = _app().run()
    at.sidebar.text_input[0].set_value(str(bad))
    at.run()
    next(b for b in at.button if "Run the arc" in b.label).click()
    at.run()
    assert not at.exception, at.exception  # degraded, not crashed
    assert at.error or at.sidebar.error
