"""The Keystone demo shell (KS-0503) — the frame around the two hero screens.

    uv run streamlit run src/keystone/ui/shell_app.py

A single navigable app that HOSTS the existing hero screens (seam, jurisdiction —
imported and rendered, never reimplemented) and adds three supporting views around
them: the evidence ledger, the cross-layer posture, and the assurance before/after.

Everything renders from the `keystone.demo` RunResult (v3) — live (`build_run_result`)
or replay (`load_run_result`, default = the committed fixture). Embedded via
`st.components.v1.html` (never `st.html`); a run that can't load shows a plain message
and the honest empty state.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from keystone.demo import RunResult, build_run_result, load_run_result
from keystone.ui import shell_screens as views
from keystone.ui.jurisdiction_screen import JURISDICTION_HEIGHT_PX, jurisdiction_html
from keystone.ui.seam_screen import SEAM_HEIGHT_PX, seam_html

_FIXTURE = (
    Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "seam_run_result.json"
)

# label -> (html builder from a RunResult, iframe height). The first two HOST the
# heroes verbatim; the rest are the supporting views.
_VIEWS: dict[str, tuple[Callable[[RunResult | None], str], int]] = {
    "① Seam — one event, two failures": (seam_html, SEAM_HEIGHT_PX),
    "② Jurisdictions — one risk, every rulebook": (
        jurisdiction_html,
        JURISDICTION_HEIGHT_PX,
    ),
    "③ Evidence ledger": (
        lambda r: views.view_html(views.ledger_svg(r)),
        views.LEDGER_HEIGHT_PX,
    ),
    "④ Cross-layer posture": (
        lambda r: views.view_html(views.posture_svg(r)),
        views.POSTURE_HEIGHT_PX,
    ),
    "⑤ Assurance before / after": (
        lambda r: views.view_html(views.before_after_svg(r)),
        views.BEFORE_AFTER_HEIGHT_PX,
    ),
}


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

    # Default to the committed fixture (deterministic replay); the loader is
    # version-aware, so any other path errors clearly instead of crashing.
    path = st.sidebar.text_input("Saved run path", value=str(_FIXTURE))
    try:
        return load_run_result(path), f"Replaying `{path}`."
    except (OSError, ValueError) as exc:
        st.sidebar.error(f"Couldn't load that run: {exc}")
        return None, f"No run loaded from `{path}`."


def render() -> None:
    st.set_page_config(page_title="Keystone — demo", page_icon="🔗", layout="wide")
    st.sidebar.title("Keystone")
    view = st.sidebar.radio("View", tuple(_VIEWS), label_visibility="visible")
    result, note = _load_run()
    st.sidebar.caption(note)

    build_html, height = _VIEWS[view]
    components.html(build_html(result), height=height, scrolling=False)


if __name__ == "__main__":
    render()
