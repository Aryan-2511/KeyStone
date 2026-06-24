"""Sidebar polish (UI-02) — restyle the chrome to the shared design system.

Bounded to LOOKS (no new controls, no behaviour change): the sidebar currently reads as
default-Streamlit (tiny stock radios, stock green button) next to the polished canvas —
the disconnected thing. This injects token-driven CSS so the sidebar reads as ONE
product with the heroes (mono/forensic feel, token colours, clear hierarchy), and
elevates the `▶ Run the arc` primary action so it looks like THE action. One injector,
called once per page.
"""

from __future__ import annotations

import streamlit as st

from . import tokens as T

# Token-driven sidebar CSS. Scoped to the sidebar + the primary button; nothing here
# changes widget LABELS, so the AppTest (which selects radios by label) is unaffected.
_SIDEBAR_CSS = f"""<style>
@import url('{T.GOOGLE_FONTS_HREF}');
/* The sidebar as a designed panel, not stock chrome. */
[data-testid="stSidebar"] {{
  background: {T.PANEL};
  border-right: 1px solid {T.HAIRLINE};
}}
[data-testid="stSidebar"] * {{ font-family: {T.STACK_BODY}; }}
/* Control labels in the forensic mono face, letter-spaced — reads as evidence chrome. */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
  font-family: {T.STACK_MONO}; font-size: 11px; letter-spacing: 1.4px;
  text-transform: uppercase; color: {T.TEXT_DIM};
}}
/* Radio options: readable, token-coloured (the tiny stock radios were the disconnect). */
[data-testid="stSidebar"] [data-testid="stRadio"] label p {{
  font-family: {T.STACK_BODY}; font-size: 14px; color: {T.TEXT};
}}
[data-testid="stSidebar"] .ks-brand {{
  font-family: {T.STACK_DISPLAY}; font-weight: 700; font-size: 22px;
  color: {T.TEXT}; letter-spacing: -0.3px; margin: 4px 0 2px;
}}
[data-testid="stSidebar"] .ks-brand-sub {{
  font-family: {T.STACK_MONO}; font-size: 10px; letter-spacing: 1.6px;
  color: {T.NVIDIA_GREEN}; text-transform: uppercase; margin-bottom: 14px;
}}
/* The primary action — "Run the arc" — elevated + token-styled, not the stock green. */
.stApp button[kind="primary"] {{
  background: {T.AMBER}; color: {T.INK}; border: none;
  font-family: {T.STACK_DISPLAY}; font-weight: 700; letter-spacing: 0.3px;
  border-radius: {T.RADIUS}px;
}}
.stApp button[kind="primary"]:hover {{ background: {T.NVIDIA_GREEN}; color: {T.INK}; }}
</style>"""

_BRAND = (
    '<div class="ks-brand">Keystone</div>'
    '<div class="ks-brand-sub">assurance · compliance</div>'
)


def style_sidebar() -> None:
    """Inject the token-driven sidebar styling + the brand block (call once per page)."""
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)
    st.sidebar.markdown(_BRAND, unsafe_allow_html=True)
