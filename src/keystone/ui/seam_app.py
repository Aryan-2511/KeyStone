"""The seam hero as a Streamlit page (KS-0501).

    streamlit run src/keystone/ui/seam_app.py

Renders `keystone.ui.seam_screen` from the `keystone.demo` RunResult contract — the
ONLY data source. Two modes:

- **Live** — `build_run_result()` runs the Layer-1 arc now (offline by default).
- **Replay** — `load_run_result(path)` reads a saved run (the KS-0504 fallback);
  defaults to the committed fixture so the page works with no prior run.

If a saved run can't be loaded, the page says so plainly and renders the honest
empty state — never a crash or fabricated data.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from keystone.demo import RunResult, build_run_result, load_run_result, run_json_path
from keystone.ui.seam_screen import SEAM_HEIGHT_PX, seam_html

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

    default = run_json_path() if Path(run_json_path()).is_file() else str(_FIXTURE)
    path = st.sidebar.text_input("Saved run path", value=default)
    try:
        return load_run_result(path), f"Replaying `{path}`."
    except (OSError, ValueError) as exc:
        st.sidebar.error(f"Couldn't load that run: {exc}")
        return None, f"No run loaded from `{path}`."


def render() -> None:
    st.set_page_config(page_title="Keystone — the seam", page_icon="🔗", layout="wide")

    result, note = _load_run()
    st.sidebar.caption(note)
    # An iframe (components.html), NOT st.html: st.html sanitises the inline SVG away,
    # leaving an empty main panel. The iframe renders the self-contained hero document.
    components.html(seam_html(result), height=SEAM_HEIGHT_PX, scrolling=False)


if __name__ == "__main__":
    render()
