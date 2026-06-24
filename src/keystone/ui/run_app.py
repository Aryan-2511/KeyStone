"""The live-execution view as a standalone Streamlit page (UI-02).

    streamlit run src/keystone/ui/run_view? -> use the shell; this is the isolated page.

Renders `keystone.ui.run_view` — press "Run the arc" and the five real Layer-1 steps
reveal progressively (the shell hosts the same view as its entry point, with the heroes
as navigable destinations; here the destination cards are inert). Live builds the arc
now; recorded replays the genuine saved run, paced — never instant, never faked.
"""

from __future__ import annotations

import streamlit as st

from keystone.demo import RunResult, build_run_result, load_recorded_run
from keystone.ui.run_view import RUN_RESULT_KEY, render_run
from keystone.ui.sidebar import style_sidebar


def render() -> None:
    st.set_page_config(
        page_title="Keystone — run the arc", page_icon="🔗", layout="wide"
    )
    style_sidebar()
    mode = st.sidebar.radio(
        "Data source",
        ("Replay saved run", "Live run"),
        help="Recorded replays a genuine saved run (offline); live builds the arc now.",
    )

    if mode == "Live run":
        mode_label = "Live run — the real Layer-1 arc, computed now."

        def build() -> RunResult | None:
            result = build_run_result()
            st.session_state[RUN_RESULT_KEY] = result
            return result

    else:
        mode_label = "Recorded run — a genuine saved run, replayed step by step."

        def build() -> RunResult | None:
            result = load_recorded_run()
            st.session_state[RUN_RESULT_KEY] = result
            return result

    render_run(build, mode_label)


if __name__ == "__main__":
    render()
