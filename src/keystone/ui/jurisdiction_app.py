"""The jurisdiction-contrast hero as a Streamlit page (KS-0502).

    streamlit run src/keystone/ui/jurisdiction_app.py

Renders `keystone.ui.jurisdiction_screen` from the `keystone.demo` RunResult — the
ONLY data source — embedded via `st.components.v1.html` (an iframe; NEVER `st.html`,
which sanitises inline SVG away — the KS-0501 bug). Live (`build_run_result`) or
replay (`load_run_result`, default = the committed fixture). A run that can't load
shows a plain message and the honest empty state — never a crash or fake data.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from keystone.demo import RunResult, build_run_result, load_run_result
from keystone.ui.jurisdiction_screen import JURISDICTION_HEIGHT_PX, jurisdiction_html

_FIXTURE = (
    Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "seam_run_result.json"
)


def _load_run() -> tuple[RunResult | None, str]:
    """Resolve the run-result for the chosen mode; return (result, status-note)."""
    mode = st.sidebar.radio(
        "Data source",
        ("Live run", "Replay saved run"),
        help="Live runs the Layer-1 arc now; replay reads a saved run-result.",
    )
    if mode == "Live run":
        if (
            st.sidebar.button("Run the arc", type="primary")
            or "live_run" not in st.session_state
        ):
            with st.spinner("Running the Layer-1 arc…"):
                st.session_state["live_run"] = build_run_result()
        result: RunResult = st.session_state["live_run"]
        return result, "Live run of the Layer-1 arc."

    # Default to the committed v2 fixture (deterministic replay); a stray
    # keystone-run.json in the cwd must NOT silently override it. Type any path to
    # replay a different run — the loader is version-aware and errors clearly.
    path = st.sidebar.text_input("Saved run path", value=str(_FIXTURE))
    try:
        return load_run_result(path), f"Replaying `{path}`."
    except (OSError, ValueError) as exc:
        st.sidebar.error(f"Couldn't load that run: {exc}")
        return None, f"No run loaded from `{path}`."


def render() -> None:
    st.set_page_config(
        page_title="Keystone — jurisdictions", page_icon="🌐", layout="wide"
    )
    result, note = _load_run()
    st.sidebar.caption(note)
    components.html(
        jurisdiction_html(result), height=JURISDICTION_HEIGHT_PX, scrolling=False
    )


if __name__ == "__main__":
    render()
