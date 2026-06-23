"""The seam-matrix hero (M1-06) — five attacks, one framework, one characterized law.

The third sibling of the seam (KS-0501) and jurisdiction (KS-0502) heroes, and the
demo's "it's a law" moment. A CONVERGENCE figure (echoing the seam screen, so it reads
as a sibling): five distinct attacks flow IN, through ONE central shared-framework
element, out to their results — four bind cleanly to a financial-crime typology, one is
the characterized BOUNDARY.

The hero of the figure is the central framework element: it carries, ONCE, the
independence property ("the crime detector never reads the attack channel") that every
pair inherits — the answer to "isn't this circular?" stated at the level of the whole
result, not five times. The axis grouping is visible (P1-P3 vary the typology holding
the attack class; P4-P5 vary the attack class) so a reviewer SEES the principled,
anti-cherry-pick sampling. P4 the boundary gets EQUAL visual weight and a distinct
"boundary" treatment (dashed, like jurisdiction's solid-vs-dashed), terminating in an
explicit proven result — never an empty/missing slot.

Every value is read from `RunResult.matrix` (derived from REGISTERED_PAIRS) — never
hardcoded. Caveats (P1's incidental rapid-movement overlap; P5's synthetic tool-call
channel) live as reachable detail in the shell, NOT on this hero, which stays clean.
Colour, type and spacing come from `keystone.ui.tokens`; pure string building (no
Streamlit import) so the SVG exports standalone for visual QA.
"""

from __future__ import annotations

from keystone.demo import MatrixPairView, RunResult

from . import tokens as T
from .svg import MISSING, TextStyle, document
from .svg import lines as _lines
from .svg import text as _text
from .svg import wrap as _wrap

_VIEWBOX_W = 1280
_VIEWBOX_H = 920

_HERO_MAX_WIDTH = 1180
MATRIX_HEIGHT_PX = round(_HERO_MAX_WIDTH * _VIEWBOX_H / _VIEWBOX_W) + 18

_LABEL = "The seam matrix: five attacks, one framework, one characterized law"

# The honest caveats — reachable inspectable detail (the shell surfaces these), kept
# OFF the hero so it stays clean and never overclaims by omission. So "is P5 as real as
# P1?" has an honest answer.
MATRIX_CAVEATS: tuple[str, ...] = (
    "P1 (structuring) — its dense cluster also incidentally trips rapid-movement. "
    "Real typologies overlap; the pairs are still detector-distinct (P2 fires "
    "rapid-movement and NOT structuring; P1 binds structuring).",
    "P5 (tool-misuse) — the crime side is fully real and independent (a standing "
    "flagged-destination screen, caught on the recipient alone). The attack side is "
    "more synthetic: the substrate has no real tool-call surface, so the tool-misuse "
    "is carried as a marker in the memo, not a live tool invocation.",
)

# --- geometry (five rows; attacks left, framework centre, results right) -------
_ROW0_CY = 256.0
_ROW_H = 126.0
_NODE_H = 92.0
_ATTACK_X, _ATTACK_W = 118.0, 250.0
_FW_X, _FW_W = 545.0, 190.0
_FW_CX = _FW_X + _FW_W / 2
_RESULT_X, _RESULT_W = 900.0, 300.0


def _row_cy(i: int) -> float:
    return _ROW0_CY + i * _ROW_H


def _svg_document(body: str) -> str:
    return document(body, width=_VIEWBOX_W, height=_VIEWBOX_H, label=_LABEL)


def _empty_state(message: str) -> str:
    cx, cy = _VIEWBOX_W / 2, _VIEWBOX_H / 2
    return _svg_document(
        _text(
            cx,
            cy - 16,
            "No matrix to show",
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 600, "middle"),
        )
        + _text(
            cx,
            cy + 16,
            message,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM, anchor="middle"),
        )
        + _text(
            cx,
            cy + 52,
            "▮▮▮▮▮  ▮▮▮▮▮  ▮▮▮▮▮  ▮▮▮▮▮  ▮▮▮▮▮",
            TextStyle(
                T.TYPE_SCALE["data"], T.MUTED, T.STACK_MONO, anchor="middle", spacing=4
            ),
        )
    )


def _header(r: RunResult) -> str:
    m = r.matrix
    dist = f"{m.clean_count} bind cleanly · {m.boundary_count} characterized boundary"
    return (
        f'<circle cx="52" cy="52" r="4" fill="{T.NVIDIA_GREEN}"/>'
        + _text(
            68,
            56,
            "KEYSTONE · THE SEAM MATRIX",
            TextStyle(
                T.TYPE_SCALE["eyebrow"], T.NVIDIA_GREEN, T.STACK_MONO, 600, spacing=1.6
            ),
        )
        + _text(
            48,
            104,
            "Not one event. A pattern — and its edge.",
            TextStyle(T.TYPE_SCALE["hero"], T.TEXT, T.STACK_DISPLAY, 700, spacing=-0.5),
        )
        + _text(
            48,
            134,
            "The same binding holds across five distinct attacks — and we characterize "
            "the one place it does not.",
            TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT_DIM),
        )
        + _text(
            _VIEWBOX_W - 48,
            104,
            dist,
            TextStyle(T.TYPE_SCALE["small"], T.AMBER, T.STACK_MONO, 600, "end", 0.5),
        )
    )


def _axis_bracket(label: str, top: float, bottom: float) -> str:
    """A left-edge bracket + vertical label grouping one axis's rows (the sampling)."""
    x = 78.0
    mid = (top + bottom) / 2
    lx = 44.0
    return (
        f'<path d="M{x + 10} {top} H{x} V{bottom} H{x + 10}" fill="none" '
        f'stroke="{T.HAIRLINE}" stroke-width="1.5"/>'
        + f'<text transform="rotate(-90 {lx} {mid})" x="{lx}" y="{mid}" '
        f'font-family="{T.STACK_MONO}" font-size="11" font-weight="600" '
        f'fill="{T.TEXT_DIM}" text-anchor="middle" letter-spacing="1.5">{label}</text>'
    )


def _column_header(x: float, label: str, color: str) -> str:
    return _text(
        x,
        198,
        label,
        TextStyle(T.TYPE_SCALE["eyebrow"], color, T.STACK_MONO, 600, spacing=1.6),
    )


def _attack_node(p: MatrixPairView, cy: float) -> str:
    """One attack (left): the OWASP id + plain name. All attacks are AI-security (L2)."""
    top = cy - _NODE_H / 2
    inner = _ATTACK_X + 18
    owasp, owasp_missing = (p.attack_owasp_id, not p.attack_owasp_id)
    return (
        f'<rect x="{_ATTACK_X}" y="{top}" width="{_ATTACK_W}" height="{_NODE_H}" '
        f'rx="{T.RADIUS}" fill="{T.PURPLE_WASH}" stroke="{T.PURPLE}" stroke-opacity="0.55"/>'
        f'<rect x="{_ATTACK_X}" y="{top}" width="3" height="{_NODE_H}" rx="1.5" fill="{T.PURPLE}"/>'
        + _text(
            inner,
            top + 26,
            f"{p.pair_id} · {owasp if not owasp_missing else MISSING}",
            TextStyle(
                T.TYPE_SCALE["eyebrow"], "#B98BD6", T.STACK_MONO, 600, spacing=1.2
            ),
        )
        + _lines(
            inner,
            top + 52,
            _wrap(p.attack_name or MISSING, 26),
            20,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT, T.STACK_DISPLAY, 600),
        )
    )


def _result_node(p: MatrixPairView, cy: float) -> str:
    """One result (right): the bound FATF typology (CLEAN) or the boundary (P4)."""
    top = cy - _NODE_H / 2
    inner = _RESULT_X + 20
    if p.result == "BOUNDARY":
        # Distinct boundary treatment: dashed outline, an explicit proven result — NOT
        # an empty slot. The negative is deliberate ("by nature, not by gap").
        return (
            f'<rect x="{_RESULT_X}" y="{top}" width="{_RESULT_W}" height="{_NODE_H}" '
            f'rx="{T.RADIUS}" fill="{T.AMBER_WASH}" stroke="{T.AMBER}" stroke-width="1.5" '
            f'stroke-dasharray="7 5"/>'
            + _text(
                inner,
                top + 26,
                "BOUNDARY · the seam does NOT bind",
                TextStyle(
                    T.TYPE_SCALE["eyebrow"], T.AMBER, T.STACK_MONO, 600, spacing=1.2
                ),
            )
            + _lines(
                inner,
                top + 50,
                _wrap("No money moves → no typology fires. By nature, not by gap.", 38),
                18,
                TextStyle(T.TYPE_SCALE["body"], "#E7B973", T.STACK_BODY, 500),
            )
        )
    typ_text = p.typology if p.typology else MISSING
    return (
        f'<rect x="{_RESULT_X}" y="{top}" width="{_RESULT_W}" height="{_NODE_H}" '
        f'rx="{T.RADIUS}" fill="{T.BERRY_WASH}" stroke="{T.BERRY}" stroke-opacity="0.55"/>'
        f'<rect x="{_RESULT_X + _RESULT_W - 3}" y="{top}" width="3" height="{_NODE_H}" '
        f'rx="1.5" fill="{T.BERRY}"/>'
        + _text(
            inner,
            top + 26,
            typ_text,
            TextStyle(
                T.TYPE_SCALE["eyebrow"], "#D17AAE", T.STACK_MONO, 600, spacing=1.2
            ),
        )
        + _lines(
            inner,
            top + 50,
            _wrap(p.typology_label or MISSING, 34),
            18,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT, T.STACK_DISPLAY, 600),
        )
        + f'<circle cx="{_RESULT_X + _RESULT_W - 78}" cy="{top + 22}" r="4" fill="{T.NVIDIA_GREEN}"/>'
        + _text(
            _RESULT_X + _RESULT_W - 66,
            top + 26,
            "CLEAN",
            TextStyle(
                T.TYPE_SCALE["eyebrow"], T.NVIDIA_GREEN, T.STACK_MONO, 600, spacing=1.5
            ),
        )
    )


def _connector(cy: float, *, boundary: bool) -> str:
    """Attack → framework → result, for one row. Dashed for the boundary pair."""
    dash = ' stroke-dasharray="7 5"' if boundary else ""
    in_color = T.PURPLE
    out_color = T.AMBER if boundary else T.BERRY
    ax = _ATTACK_X + _ATTACK_W
    rx = _RESULT_X
    return (
        f'<line x1="{ax}" y1="{cy}" x2="{_FW_X}" y2="{cy}" stroke="{in_color}" '
        f'stroke-width="2.25" stroke-opacity="0.85"{dash}/>'
        f'<line x1="{_FW_X + _FW_W}" y1="{cy}" x2="{rx}" y2="{cy}" stroke="{out_color}" '
        f'stroke-width="2.25" stroke-opacity="0.85"{dash}/>'
        f'<circle cx="{ax}" cy="{cy}" r="3.5" fill="{in_color}"/>'
        f'<circle cx="{rx}" cy="{cy}" r="3.5" fill="{out_color}"/>'
    )


def _framework(r: RunResult) -> str:
    """The central element — the hero. ONE framework, carrying the independence ONCE."""
    top = _row_cy(0) - _NODE_H / 2 - 8
    bottom = _row_cy(4) + _NODE_H / 2 + 8
    h = bottom - top
    cy_mid = (top + bottom) / 2
    indep = r.matrix.independence_property or MISSING
    s = 13
    return (
        f'<rect x="{_FW_X}" y="{top}" width="{_FW_W}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.AMBER_PANEL}" stroke="{T.AMBER}" stroke-width="1.75"/>'
        f'<rect x="{_FW_X}" y="{top}" width="{_FW_W}" height="3" rx="1.5" fill="{T.AMBER}"/>'
        + _text(
            _FW_CX,
            top + 32,
            "ONE FRAMEWORK",
            TextStyle(T.TYPE_SCALE["eyebrow"], T.AMBER, T.STACK_MONO, 600, "middle", 2),
        )
        + _text(
            _FW_CX,
            top + 56,
            "binds all five",
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_MONO, 500, "middle"),
        )
        # the convergence node (echo of the seam screen's amber diamond)
        + f'<circle cx="{_FW_CX}" cy="{cy_mid}" r="22" fill="none" stroke="{T.AMBER}" stroke-opacity="0.35"/>'
        + f'<path d="M{_FW_CX} {cy_mid - s} L{_FW_CX + s} {cy_mid} L{_FW_CX} {cy_mid + s} '
        f'L{_FW_CX - s} {cy_mid} Z" fill="{T.AMBER}"/>'
        + _lines(
            _FW_CX,
            cy_mid + 56,
            _wrap(indep, 24),
            17,
            TextStyle(T.TYPE_SCALE["small"], T.TEXT, T.STACK_BODY, 500, "middle"),
        )
        + _text(
            _FW_CX,
            bottom - 22,
            "independence — a property, not a per-pair test",
            TextStyle(10, T.AMBER, T.STACK_MONO, 500, "middle", 0.5),
        )
    )


def _footer(r: RunResult) -> str:
    """The boundary statement (attached to P4) + the derived-from note."""
    y = _VIEWBOX_H - 70
    stmt = r.matrix.boundary_statement or MISSING
    derived = (
        f"Rendered from REGISTERED_PAIRS · {len(r.matrix.pairs)} pairs · "
        "nothing hardcoded"
    )
    return (
        f'<line x1="48" y1="{y - 18}" x2="{_VIEWBOX_W - 48}" y2="{y - 18}" stroke="{T.HAIRLINE}"/>'
        + f'<rect x="48" y="{y - 6}" width="3" height="40" rx="1.5" fill="{T.AMBER}"/>'
        + _text(
            66,
            y + 8,
            "THE BOUNDARY (P4)",
            TextStyle(T.TYPE_SCALE["eyebrow"], T.AMBER, T.STACK_MONO, 600, spacing=1.5),
        )
        + _lines(
            66,
            y + 28,
            _wrap(stmt, 96),
            17,
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_BODY),
        )
        + _text(
            _VIEWBOX_W - 48,
            _VIEWBOX_H - 22,
            derived,
            TextStyle(T.TYPE_SCALE["small"], T.MUTED, T.STACK_MONO, anchor="end"),
        )
    )


def matrix_svg(result: RunResult | None) -> str:
    """The seam-matrix hero as a self-contained SVG string, from a `RunResult`."""
    if result is None or not result.matrix.pairs:
        return _empty_state("Run the demo or load a saved run to render the matrix.")

    pairs = result.matrix.pairs
    rows: list[str] = []
    for i, p in enumerate(pairs):
        cy = _row_cy(i)
        boundary = p.result == "BOUNDARY"
        rows.append(_connector(cy, boundary=boundary))
        rows.append(_attack_node(p, cy))
        rows.append(_result_node(p, cy))

    # Axis brackets, derived from the pairs' axis grouping (the principled sampling).
    brackets = ""
    axis_a = [i for i, p in enumerate(pairs) if p.axis == "A"]
    axis_b = [i for i, p in enumerate(pairs) if p.axis == "B"]
    if axis_a:
        brackets += _axis_bracket(
            "AXIS A — ONE ATTACK CLASS, THREE TYPOLOGIES",
            _row_cy(axis_a[0]) - _NODE_H / 2,
            _row_cy(axis_a[-1]) + _NODE_H / 2,
        )
    if axis_b:
        brackets += _axis_bracket(
            "AXIS B — BEYOND INJECTION",
            _row_cy(axis_b[0]) - _NODE_H / 2,
            _row_cy(axis_b[-1]) + _NODE_H / 2,
        )

    headers = _column_header(
        _ATTACK_X, "THE ATTACK · OWASP LLM", "#B98BD6"
    ) + _column_header(_RESULT_X, "CAUGHT AS · FATF TYPOLOGY", "#D17AAE")

    body = (
        _header(result)
        + headers
        + brackets
        + "".join(rows)
        + _framework(result)
        + _footer(result)
    )
    return _svg_document(body)


def matrix_html(result: RunResult | None) -> str:
    """A self-contained HTML doc for `components.v1.html` (an iframe), centred on ink."""
    return (
        f"<style>{T.fonts_css()}"
        f"html,body{{margin:0;background:{T.INK};}}"
        f".ks-matrix{{max-width:{_HERO_MAX_WIDTH}px;margin:0 auto;}}</style>"
        f'<div class="ks-matrix">{matrix_svg(result)}</div>'
    )
