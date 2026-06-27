"""The live-execution view (UI-02) — the five real arc steps, derived not fabricated.

Deterministic, fast — no Streamlit. `arc_steps` is the pure derivation the progressive
reveal renders; these assert it surfaces the FIVE REAL milestone stages with their REAL
artifacts (from the ledger + the typed views), and that RECORDED mode reveals the SAME
steps a fresh build does — proving recorded is a paced REAL replay, not a fabrication.
"""

from __future__ import annotations

from keystone.demo import build_run_result, load_recorded_run
from keystone.ui.run_view import (
    HERO_DESTINATIONS,
    arc_steps,
    red_team_moment,
    triage_moment,
)


def test_arc_steps_are_the_five_real_milestone_stages() -> None:
    r = load_recorded_run()
    steps = arc_steps(r)
    # The five revealed steps ARE the run's real arc stages, in order.
    assert tuple(s.stage for s in steps) == r.arc.stages
    assert tuple(s.stage for s in steps) == (
        "ingested",
        "detected",
        "seam_bound",
        "reported",
        "signed",
    )
    # The hash-chained ledger grows entry by entry to the run's real entry count.
    assert tuple(s.ledger_entries for s in steps) == (1, 2, 3, 4, 5)
    assert steps[-1].ledger_entries == r.arc.entry_count


def test_steps_reveal_real_artifacts_not_fabricated() -> None:
    r = load_recorded_run()
    by_stage = {s.stage: s for s in arc_steps(r)}
    # DETECT shows the real FATF finding implicating the real seam tx.
    assert r.financial_crime.typology in by_stage["detected"].title
    assert r.binding.transaction_id in by_stage["detected"].title
    # SEAM-BIND shows the real binding (the canonical signature).
    assert r.binding.signature_name in by_stage["seam_bound"].title
    # REPORT shows the real report format; SIGN the real signer + chain state.
    assert r.report.report_format in by_stage["reported"].title
    assert r.report.signed_by in by_stage["signed"].detail
    expected_chain = "verified" if r.arc.chain_verified else "TAMPERED"
    assert expected_chain in by_stage["signed"].title


def test_recorded_reveals_the_same_steps_as_a_fresh_build() -> None:
    # Recorded mode is a PACED REAL REPLAY: the steps it reveals are the genuine run's
    # steps — identical (the offline template narrative is deterministic) to a fresh
    # build's. NOT fabricated, NOT a different/instant thing.
    recorded = arc_steps(load_recorded_run())
    fresh = arc_steps(build_run_result())
    assert tuple(s.stage for s in recorded) == tuple(s.stage for s in fresh)
    assert tuple(s.title for s in recorded) == tuple(s.title for s in fresh)


def test_the_run_arrives_at_the_four_heroes() -> None:
    # The destinations the run reaches — the four result heroes (not standalone pictures).
    assert len(HERO_DESTINATIONS) == 4
    names = {name for name, _ in HERO_DESTINATIONS}
    assert names == {"Seam", "Jurisdictions", "Seam matrix", "Convergence"}


# --- the two AGENT moments (UI-03): framing reads the REAL blocks, not hardcoded ----


def test_red_team_moment_reads_the_real_red_team_block() -> None:
    # The Red-Team Agent beat is DERIVED from the real red_team block — its fields equal
    # the block's (no recompute, no fabrication, no hardcoded dramatization).
    r = load_recorded_run()
    m = red_team_moment(r)
    rt = r.red_team
    assert m.exploited_family == rt.exploited_family
    assert m.abandoned_families == rt.abandoned_families
    assert m.probes_run == rt.probes_run
    assert m.mechanism == rt.mechanism and "not an LLM" in m.mechanism
    # The landed exploit it surfaces is the strongest got-through failure_rate in the trace.
    expected = max(d.failure_rate for d in rt.decisions if d.got_through)
    assert m.landed_rate == expected
    # The real exploited family + its landed rate read into the displayed text.
    assert rt.exploited_family is not None
    assert rt.exploited_family in m.title and rt.exploited_family in m.detail


def test_triage_moment_reads_the_real_triage_block() -> None:
    # The Triage Agent beat is DERIVED from the real triage block — route/signals/rationale
    # equal the block's; the displayed route + rationale are the agent's genuine decision.
    r = load_recorded_run()
    m = triage_moment(r)
    tr = r.triage
    assert (m.route, m.failure_rate, m.seam_result, m.severity) == (
        tr.route,
        tr.failure_rate,
        tr.seam_result,
        tr.severity,
    )
    assert m.rationale == tr.rationale
    assert m.mechanism == tr.mechanism and "not an LLM" in m.mechanism
    assert tr.route.upper() in m.title  # e.g. "Routed → ESCALATE"


def test_triage_moment_links_route_to_the_red_team_landed_exploit() -> None:
    # The literal supervisor–worker topology: the failure_rate the Triage Agent routes on
    # IS the Red-Team Agent's strongest landed exploit (the worker's output, the supervisor's
    # input). The framing surfaces that link.
    r = load_recorded_run()
    m = triage_moment(r)
    assert m.reads_red_team_exploit is True
    assert m.failure_rate == red_team_moment(r).landed_rate
    assert "Red-Team Agent" in m.detail


def test_agent_moments_are_derived_not_hardcoded() -> None:
    # Recorded and a fresh build yield the SAME moments (the offline path is deterministic),
    # and each equals its block — proving the framing is a function of the run, not a
    # hardcoded script. (A different run's blocks would yield different moments.)
    rec, fresh = load_recorded_run(), build_run_result()
    assert red_team_moment(rec).title == red_team_moment(fresh).title
    assert triage_moment(rec).route == triage_moment(fresh).route == fresh.triage.route
