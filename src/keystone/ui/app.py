"""Streamlit shell for the Keystone chassis (UI layer).

A minimal operator view: a button to run the workflow once, a table of ledger
entries, and a chain-integrity indicator. No layer UI yet. Run via `make demo`
(`streamlit run src/keystone/ui/app.py`).
"""

from __future__ import annotations

import asyncio

import streamlit as st

from keystone.agents.run import run_once
from keystone.core.ledger import ledger_db_path, open_ledger


def render() -> None:
    st.set_page_config(page_title="Keystone chassis", page_icon="🔗")
    st.title("Keystone — chassis")
    st.caption(f"Evidence ledger: `{ledger_db_path()}`")

    if st.button("Run chassis", type="primary"):
        with st.spinner("Running NAT workflow…"):
            result = asyncio.run(run_once())
        st.success(f"Workflow result: {result}")

    ledger = open_ledger()
    entries = ledger.all()

    if ledger.verify_chain():
        st.markdown("**Chain integrity:** :green[● verified]")
    else:
        st.markdown("**Chain integrity:** :red[● TAMPERED]")

    st.subheader("Evidence ledger")
    if entries:
        st.dataframe(
            [e.model_dump() for e in entries],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No entries yet — click **Run chassis**.")


if __name__ == "__main__":
    render()
