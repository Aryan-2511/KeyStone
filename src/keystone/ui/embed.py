"""Seamless hero embedding (UI-01) — one place that strips the iframe seam.

Every hero is embedded the SAME way through `embed_hero`: a single CSS reset removes the
`components.v1.html` iframe's default chrome (border / inset rectangle), so the hero —
whose SVG fills with the SAME `tokens.INK` the Streamlit page background uses — sits
FLUSH on the page with no "pasted picture" edge. The KS-0501 embedding is kept intact
(`components.v1.html` + the height-from-viewBox sizing); only its visible frame is
neutralised. One function, so the four heroes + the shell can't drift apart.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from . import tokens as T

# Strip the embedded-component iframe's default frame so the hero meets the page with no
# visible edge. INK keeps the iframe surface identical to the page background.
SEAMLESS_CSS = (
    "<style>"
    ".stApp iframe{border:none !important;}"
    f".stApp [data-testid='stCustomComponentV1']{{background:{T.INK} !important;}}"
    "</style>"
)


def embed_hero(html: str, height: int) -> None:
    """Embed a hero HTML doc flush on the page (no iframe seam); KS-0501 sizing intact."""
    st.markdown(SEAMLESS_CSS, unsafe_allow_html=True)
    components.html(html, height=height, scrolling=False)
