"""The live-execution view (UI-02) — make the system VISIBLY RUN.

The app's entry point: press "Run the arc" and the FIVE REAL Layer-1 steps reveal
progressively as the run completes — ingest → detect → seam-bind → report → sign — the
hash-chained ledger growing entry by entry, ARRIVING at the four result heroes as the
run's destinations. The steps + the ledger ALREADY exist in the `RunResult.arc` (the
KS-0405 milestone arc); this view SURFACES them progressively — it does NOT recompute or
fake anything.

The live / recorded honesty rule (load-bearing):
- LIVE: the result is computed now (`build_run_result`) — real computation — then its five
  real steps reveal, paced for legibility.
- RECORDED: the SAME five steps reveal, paced, replaying the GENUINE saved run
  (`recorded_run.json`) — NOT instant, NOT a fake sleep-driven simulation. A real prior
  run, revealed progressively.
The reveal is IDENTICAL; the only difference is live computes now vs recorded plays back.

`arc_steps` is the pure, testable derivation (the five real steps from the RunResult);
`render_run` is the Streamlit progressive reveal. Colour/type from `keystone.ui.tokens`.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass

import streamlit as st

from keystone.demo import RunResult

from . import tokens as T

# The five milestone stages, in arc order, with a plain label + the token colour each
# step speaks in (L1 berry for the AML beats, amber for the seam, green for the sign-off).
_STAGE_META: tuple[tuple[str, str, str], ...] = (
    ("ingested", "INGEST", T.BERRY),
    ("detected", "DETECT", T.BERRY),
    ("seam_bound", "SEAM-BIND", T.AMBER),
    ("reported", "REPORT", T.BERRY),
    ("signed", "SIGN", T.NVIDIA_GREEN),
)

# The four result heroes the run ARRIVES at (name + its claim). The shell maps the index
# to its hero view; standalone, the cards are inert.
HERO_DESTINATIONS: tuple[tuple[str, str], ...] = (
    ("Seam", "one event, two failures"),
    ("Jurisdictions", "one risk, every rulebook"),
    ("Seam matrix", "five attacks, one law"),
    ("Convergence", "violated, then satisfied"),
)


@dataclass(frozen=True)
class ArcStep:
    """One revealed arc step — its real artifact + the ledger height after it."""

    stage: str
    label: str
    color: str
    title: str
    detail: str
    ledger_entries: int  # hash-chained entries committed after this step (1..5)


def _payload(result: RunResult, stage: str) -> dict[str, object]:
    for entry in result.arc.entries:
        if entry.payload.get("stage") == stage:
            return dict(entry.payload)
    return {}


def _money(amount: float, currency: str) -> str:
    return f"${amount:,.2f} {currency}"


def arc_steps(result: RunResult) -> tuple[ArcStep, ...]:
    """Derive the five REAL arc steps from the RunResult (no recompute, no fabrication).

    Each step's artifact is read from the real ledger entry payload + the typed views, so
    what the view reveals is exactly what the run produced.
    """
    fc = result.financial_crime
    b = result.binding
    rep = result.report
    n_tx = _payload(result, "ingested").get("transaction_count")
    narrative = (
        "narrative generated"
        if not rep.narrative_fell_back
        else "narrative fell back to the faithful template"
    )
    chain = "chain verified" if result.arc.chain_verified else "chain TAMPERED"
    titles_details: tuple[tuple[str, str], ...] = (
        (
            f"{n_tx} transactions ingested" if n_tx else "transactions ingested",
            f"the synthetic stream, including the seam transfer {b.transaction_id}",
        ),
        (
            f"{fc.typology} flagged on {b.transaction_id}",
            f"memo-blind FATF — {len(fc.transaction_ids)} transfers from {fc.account}, "
            "on amounts & timing alone",
        ),
        (
            f"{b.transaction_id} = {b.signature_name}",
            "the flagged transfer carries the exact L2 vulnerability Garak found and "
            "Guardrails patched",
        ),
        (
            f"{rep.report_format} + goAML drafted",
            f"STR over {rep.transaction_count} transfers · "
            f"{_money(rep.total_amount, rep.currency)} · {narrative}",
        ),
        (
            f"Signed · {chain} · {result.arc.entry_count} entries",
            f"human sign-off by {rep.signed_by} — the report moved draft → signed",
        ),
    )
    return tuple(
        ArcStep(
            stage=stage,
            label=label,
            color=color,
            title=title,
            detail=detail,
            ledger_entries=i + 1,
        )
        for i, ((stage, label, color), (title, detail)) in enumerate(
            zip(_STAGE_META, titles_details, strict=True)
        )
    )


# --- the Streamlit progressive reveal -----------------------------------------

_RAN_KEY = "_arc_ran"
_PACE_KEY = "_arc_pace"
#: Session key holding the current run-result (shared with the hero views, so the heroes
#: are the destinations of the SAME run). Defaulted to the recorded run by the shell.
RUN_RESULT_KEY = "run_result"


# Readable text tints for each accent (the deep border colours are too dark as 11px
# label text on the panel).
_LABEL_TINT: dict[str, str] = {
    T.BERRY: "#D17AAE",
    T.AMBER: "#E7B973",
    T.NVIDIA_GREEN: T.NVIDIA_GREEN,
}


def _step_block(step: ArcStep) -> str:
    """One completed step as a styled HTML card (token colours, mono forensic feel)."""
    label_color = _LABEL_TINT.get(step.color, step.color)
    return (
        f'<div style="display:flex;gap:14px;align-items:flex-start;margin:10px 0;'
        f"padding:14px 18px;background:{T.PANEL};border-radius:{T.RADIUS}px;"
        f'border-left:3px solid {step.color};">'
        f'<div style="font-family:{T.STACK_MONO};font-size:18px;color:{T.NVIDIA_GREEN};'
        f'font-weight:600;margin-top:2px;">✓</div>'
        f'<div style="flex:1;">'
        f'<div style="font-family:{T.STACK_MONO};font-size:11px;letter-spacing:1.6px;'
        f'color:{label_color};font-weight:600;">{step.label}</div>'
        f'<div style="font-family:{T.STACK_DISPLAY};font-size:18px;color:{T.TEXT};'
        f'font-weight:600;margin:2px 0;">{step.title}</div>'
        f'<div style="font-family:{T.STACK_BODY};font-size:13px;color:{T.TEXT_DIM};">'
        f"{step.detail}</div></div>"
        f'<div style="font-family:{T.STACK_MONO};font-size:11px;color:{T.TEXT_DIM};'
        f'text-align:right;white-space:nowrap;margin-top:2px;">ledger<br>'
        f'<span style="font-size:18px;color:{T.TEXT};">{step.ledger_entries}</span>'
        f" / 5</div></div>"
    )


def _header() -> str:
    return (
        f'<div style="font-family:{T.STACK_MONO};font-size:11px;letter-spacing:1.6px;'
        f'color:{T.NVIDIA_GREEN};font-weight:600;">KEYSTONE · LIVE EXECUTION</div>'
        f'<div style="font-family:{T.STACK_DISPLAY};font-size:34px;color:{T.TEXT};'
        f'font-weight:700;letter-spacing:-0.5px;margin:6px 0 2px;">Watch it run.</div>'
        f'<div style="font-family:{T.STACK_BODY};font-size:15px;color:{T.TEXT_DIM};">'
        "Five real steps — ingest, detect, seam-bind, report, sign — committed to a "
        "hash-chained ledger, arriving at the result heroes.</div>"
    )


def render_run(
    build: Callable[[], RunResult | None],
    mode_label: str,
    *,
    on_open: Callable[[int], None] | None = None,
    pace: float = 0.35,
) -> None:
    """Render the entry view: the primary Run-the-arc action + the progressive reveal.

    `build` produces the run-result when the button is pressed: `build_run_result()` in
    live mode (real computation now) or `load_recorded_run()` in recorded mode (a genuine
    saved run). EITHER way the same five real steps reveal, paced. The result is stored in
    `RUN_RESULT_KEY` so the hero views are the destinations of the SAME run.
    """
    st.markdown(_header(), unsafe_allow_html=True)
    st.caption(mode_label)

    if st.button("▶ Run the arc", type="primary", use_container_width=True):
        st.session_state[RUN_RESULT_KEY] = build()
        st.session_state[_RAN_KEY] = True
        st.session_state[_PACE_KEY] = True  # pace only the run that just triggered

    if not st.session_state.get(_RAN_KEY):
        st.caption(
            "Press **Run the arc** to execute the five-step Layer-1 arc and watch the "
            "evidence ledger build, entry by entry."
        )
        return

    result = st.session_state.get(RUN_RESULT_KEY)
    if result is None:
        st.error("No run to reveal — load a run or check the data source.")
        return

    steps = arc_steps(result)
    pace_now = bool(st.session_state.pop(_PACE_KEY, False))
    for step in steps:
        st.markdown(_step_block(step), unsafe_allow_html=True)
        if pace_now:
            time.sleep(pace)

    _render_destinations(on_open)


def _render_destinations(on_open: Callable[[int], None] | None) -> None:
    """The four heroes the run ARRIVED at — the destinations, not standalone pictures."""
    st.markdown(
        f'<div style="margin-top:18px;font-family:{T.STACK_MONO};font-size:11px;'
        f'letter-spacing:1.4px;color:{T.AMBER};font-weight:600;">'
        "THE RUN REACHED THESE DESTINATIONS</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(len(HERO_DESTINATIONS))
    for i, (col, (name, claim)) in enumerate(zip(cols, HERO_DESTINATIONS, strict=True)):
        with col:
            st.markdown(
                f'<div style="font-family:{T.STACK_DISPLAY};font-size:15px;'
                f'color:{T.TEXT};font-weight:600;">{name}</div>'
                f'<div style="font-family:{T.STACK_BODY};font-size:12px;'
                f'color:{T.TEXT_DIM};margin-bottom:6px;">{claim}</div>',
                unsafe_allow_html=True,
            )
            opened = st.button(
                f"Open {name} →", key=f"_dest_{i}", use_container_width=True
            )
            if opened and on_open is not None:
                on_open(i)


def step_titles(result: RunResult) -> Iterable[str]:
    """The five revealed step titles (for tests / a quick textual summary)."""
    return (step.title for step in arc_steps(result))
