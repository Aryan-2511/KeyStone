"""The seam-matrix hero as a Streamlit page (M1-06).

    streamlit run src/keystone/ui/matrix_app.py

Renders `keystone.ui.matrix_screen` from the `keystone.demo` RunResult contract (the
matrix block, derived from REGISTERED_PAIRS) — the ONLY data source. Two modes:

- **Replay** — `load_run_result(path)` reads a saved run (default = the committed
  recorded run; the safe, offline default).
- **Live** — `build_run_result()` runs the Layer-1 arc now (offline by default).

If a saved run can't be loaded, the page says so plainly and renders the honest empty
state — never a crash or fabricated data. Embedded via `components.v1.html` (an iframe),
NEVER `st.html` (which sanitises the inline SVG away).
"""

from __future__ import annotations

import streamlit as st

from keystone.demo import (
    RunResult,
    build_run_result,
    load_run_result,
    recorded_run_path,
)
from keystone.ui.embed import embed_hero
from keystone.ui.matrix_screen import MATRIX_HEIGHT_PX, matrix_html


def _load_run() -> tuple[RunResult | None, str]:
    """Resolve the run-result for the chosen mode; return (result, status-note)."""
    mode = st.sidebar.radio(
        "Data source",
        ("Replay saved run", "Live run"),
        help="Replay reads the committed recorded run (offline); live builds the arc now.",
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

    path = st.sidebar.text_input("Saved run path", value=str(recorded_run_path()))
    try:
        return load_run_result(path), f"Replaying `{path}`."
    except (OSError, ValueError) as exc:
        st.sidebar.error(f"Couldn't load that run: {exc}")
        return None, f"No run loaded from `{path}`."


def render() -> None:
    st.set_page_config(
        page_title="Keystone — the seam matrix", page_icon="🔗", layout="wide"
    )
    result, note = _load_run()
    st.sidebar.caption(note)
    embed_hero(matrix_html(result), MATRIX_HEIGHT_PX)


if __name__ == "__main__":
    render()
