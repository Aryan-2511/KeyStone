"""The Keystone demo shell — the live-execution entry point + the result heroes.

    uv run streamlit run src/keystone/ui/shell_app.py

The ENTRY POINT is the live-execution view (UI-02): press "Run the arc" and the five
real Layer-1 steps reveal progressively, arriving at the four result heroes (seam,
jurisdiction, matrix, convergence — hosted via `embed_hero`, never reimplemented) plus
three supporting views (ledger / posture / before-after).

Everything renders from the `keystone.demo` RunResult — live (`build_run_result`) or a
genuine saved run (`load_run_result`, default = the committed recorded run). Embedded
flush via `embed_hero` (UI-01); a run that can't load shows the honest empty state.
"""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from keystone.demo import (
    RunResult,
    build_run_result,
    load_run_result,
    recorded_run_path,
)
from keystone.ui import shell_screens as views
from keystone.ui.convergence_screen import CONVERGENCE_HEIGHT_PX, convergence_html
from keystone.ui.embed import embed_hero
from keystone.ui.jurisdiction_screen import JURISDICTION_HEIGHT_PX, jurisdiction_html
from keystone.ui.matrix_screen import MATRIX_CAVEATS, MATRIX_HEIGHT_PX, matrix_html
from keystone.ui.run_view import RUN_RESULT_KEY, render_run
from keystone.ui.seam_screen import SEAM_HEIGHT_PX, seam_html
from keystone.ui.sidebar import style_sidebar

# The live-execution entry view + the matrix view (whose caveats surface as detail).
_RUN_VIEW = "▶ Run the arc"
_MATRIX_VIEW = "③ The seam matrix — five attacks, one law"

# label -> (html builder from a RunResult, iframe height). The first four HOST the heroes
# verbatim (and are the run's destinations); the rest are the supporting views.
_VIEWS: dict[str, tuple[Callable[[RunResult | None], str], int]] = {
    "① Seam — one event, two failures": (seam_html, SEAM_HEIGHT_PX),
    "② Jurisdictions — one risk, every rulebook": (
        jurisdiction_html,
        JURISDICTION_HEIGHT_PX,
    ),
    _MATRIX_VIEW: (matrix_html, MATRIX_HEIGHT_PX),
    "④ Convergence — violated, then satisfied": (
        convergence_html,
        CONVERGENCE_HEIGHT_PX,
    ),
    "⑤ Evidence ledger": (
        lambda r: views.view_html(views.ledger_svg(r)),
        views.LEDGER_HEIGHT_PX,
    ),
    "⑥ Cross-layer posture": (
        lambda r: views.view_html(views.posture_svg(r)),
        views.POSTURE_HEIGHT_PX,
    ),
    "⑦ Assurance before / after": (
        lambda r: views.view_html(views.before_after_svg(r)),
        views.BEFORE_AFTER_HEIGHT_PX,
    ),
}
_OPTIONS = (_RUN_VIEW, *_VIEWS)
# The four heroes are the first four views — the run's destinations (index → view label).
_HERO_LABELS = tuple(_VIEWS)[:4]
_VIEW_KEY = "shell_view"


def _safe_load(path: str) -> RunResult | None:
    """Load a saved run, degrading to the honest empty state instead of crashing."""
    try:
        return load_run_result(path)
    except (OSError, ValueError) as exc:
        st.sidebar.error(f"Couldn't load that run: {exc}")
        return None


def _navigate(index: int) -> None:
    """Jump to a hero view (the run's destination) — applied before the View radio."""
    st.session_state["_pending_view"] = _HERO_LABELS[index]
    st.rerun()


def render() -> None:
    st.set_page_config(page_title="Keystone — demo", page_icon="🔗", layout="wide")
    style_sidebar()

    # A destination button set a pending view last run — apply it before the radio.
    if "_pending_view" in st.session_state:
        st.session_state[_VIEW_KEY] = st.session_state.pop("_pending_view")

    mode = st.sidebar.radio(
        "Data source",
        ("Replay saved run", "Live run"),
        help="Recorded replays a genuine saved run (offline); live builds the arc now.",
    )
    view = st.sidebar.radio("View", _OPTIONS, key=_VIEW_KEY)

    if mode == "Live run":
        path = ""
        mode_label = "Live run — the real Layer-1 arc, computed now."

        def build() -> RunResult | None:
            result = build_run_result()
            st.session_state[RUN_RESULT_KEY] = result
            return result

    else:
        path = st.sidebar.text_input("Saved run path", value=str(recorded_run_path()))
        mode_label = "Recorded run — a genuine saved run, replayed step by step."

        def build() -> RunResult | None:
            result = _safe_load(path)
            st.session_state[RUN_RESULT_KEY] = result
            return result

    # A safe default so the heroes work the moment the app opens (the recorded fallback),
    # before any run is pressed.
    if RUN_RESULT_KEY not in st.session_state:
        st.session_state[RUN_RESULT_KEY] = _safe_load(str(recorded_run_path()))

    if view == _RUN_VIEW:
        render_run(build, mode_label, on_open=_navigate)
        return

    result = st.session_state.get(RUN_RESULT_KEY)
    build_html, height = _VIEWS[view]
    embed_hero(build_html(result), height)

    # The matrix hero stays clean; its honest caveats live here as reachable detail.
    if view == _MATRIX_VIEW:
        with st.expander("Honest caveats — the matrix's fine print"):
            for caveat in MATRIX_CAVEATS:
                st.markdown(f"- {caveat}")


if __name__ == "__main__":
    render()
