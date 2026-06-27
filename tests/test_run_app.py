"""The live-execution Streamlit app (UI-02) actually loads and reveals — the gate.

Per the KS-0501 lesson: run the REAL Streamlit script via `AppTest`. Loads the page,
presses "Run the arc", and asserts the five real steps reveal and the run arrives at the
destinations — in BOTH live and recorded — with no exception.
"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

_APP = str(
    Path(__file__).resolve().parents[1] / "src" / "keystone" / "ui" / "run_app.py"
)
_STEP_LABELS = ("INGEST", "DETECT", "SEAM-BIND", "REPORT", "SIGN")


def _app() -> AppTest:
    return AppTest.from_file(_APP, default_timeout=120)


def _markdown(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown)


def _run_button(at: AppTest):  # type: ignore[no-untyped-def]
    return next(b for b in at.button if "Run the arc" in b.label)


def test_app_loads_without_exception() -> None:
    at = _app().run()
    assert not at.exception, at.exception
    assert at.sidebar.radio  # the data-source control is present


def test_run_the_arc_reveals_the_five_real_steps_recorded() -> None:
    at = _app().run()  # default = recorded
    _run_button(at).click()
    at.run()
    assert not at.exception, at.exception
    md = _markdown(at)
    for label in _STEP_LABELS:
        assert label in md, label
    # The reveal carries the REAL artifact (the FATF finding), not a fabrication.
    assert "STRUCTURING" in md
    # The TWO agent moments are foregrounded (UI-03), distinct from the stages, and
    # honestly framed (adaptive policies, not LLMs).
    assert "RED-TEAM AGENT" in md and "TRIAGE AGENT" in md
    assert "not an LLM" in md
    # The Triage Agent surfaces its real route (escalate) over the recorded signals.
    assert "ESCALATE" in md
    # The run arrived at the destinations (the four heroes).
    assert any("Open Seam" in b.label for b in at.button)


def test_run_the_arc_reveals_live() -> None:
    at = _app().run()
    next(r for r in at.sidebar.radio if r.label == "Data source").set_value("Live run")
    at.run()
    _run_button(at).click()
    at.run()
    assert not at.exception, at.exception
    md = _markdown(at)
    for label in _STEP_LABELS:
        assert label in md, label
